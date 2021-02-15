# MangaDex API v1.0
#
# Requires python3.7 with the following packages installed
# - aiofiles 0.5.0
# - aiohttp 3.6.2
# - Pillow 7.2.0
# - requests 2.24.0

import aiofiles
import aiohttp
import asyncio
import io
import os
import requests

from datetime import datetime
from PIL import Image

class Chapter:
    __slots__ = ('id', 'title', 'chapter_no', 'page_count',
                 'group_name', 'group_id', 'lang_name',
                 'hash', 'server', 'page_array', 'timestamp',
                 'fetched_data')

    def __init__(self, id, **kwargs):
        self.id = id
        self.fetched_data = False
        for attr in kwargs.keys():
            setattr(self, attr, kwargs[attr])

    def download(self, interval=None, pdf_file=None):
        if not self.fetched_data:
            self._fetch()
            self.fetched_data = True
        if not interval:
            interval = (0, self.page_count - 1)
        starting_page = interval[0]
        ending_page = interval[1]
        if starting_page < 0 or starting_page > ending_page or starting_page >= self.page_count:
            raise Exception('invalid starting page')
        if ending_page >= self.page_count:
            raise Exception('invalid ending page')
        front = self._retrieve_img(starting_page)
        pages = []
        for pageno in range(starting_page + 1, ending_page + 1):
            pages.append(self._retrieve_img(pageno))
            print(f'Page {pageno} downloaded ({self.id})')
        if not pdf_file:
            pdf_file = f'Chapter {self.chapter_no} - {self.title}.pdf'
        front.save(pdf_file, save_all=True, append_images=pages)
        print(f'Downloaded chapter {self.chapter_no} ({self.id})')

    async def download_async(self, semaphore, interval=None, pdf_file=None):
        if not self.fetched_data:
            self._fetch()
            self.fetched_data = True
        if not interval:
            interval = (0, self.page_count - 1)
        starting_page = interval[0]
        ending_page = interval[1]
        if starting_page < 0 or starting_page > ending_page or starting_page >= self.page_count:
            raise Exception('invalid starting page')
        if ending_page >= self.page_count:
            raise Exception('invalid ending page')
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                front = await self._retrieve_img_async(starting_page, session)
                pages = []
                for pageno in range(starting_page + 1, ending_page + 1):
                    pages.append(await self._retrieve_img_async(pageno, session))
                    print(f'Page {pageno} downloaded ({self.id})')
                if not pdf_file:
                    pdf_file = f'Chapter {self.chapter_no} - {self.title}.pdf'
                f = await aiofiles.open(pdf_file, 'wb')
                front.save(f._file, format='pdf', save_all=True, append_images=pages)
                await f.close()
        print(f'Downloaded chapter {self.chapter_no} ({self.id})')

    def __getattr__(self, attr):
        self._fetch()
        self.fetched_data = True
        return super(Chapter, self).__getattribute__(attr)

    def __str__(self):
        if not self.fetched_data:
            self._fetch()
            self.fetched_data = True
        s = ''
        s += f'Title: {self.title}\n'
        s += f'Chapter number: {self.chapter_no}\n'
        s += f'Page count: {self.page_count}\n'
        s += f'Group: {self.group_name}\n'
        s += f'Language: {self.lang_name}\n'
        s += f'Published: {datetime.fromtimestamp(self.timestamp).strftime("%m/%d/%Y:%H:%M:%S")}\n'
        return s

    def _retrieve_img(self, pageno):
        r = requests.get(f'{self.server}{self.hash}/{self.page_array[pageno]}', stream=True)
        if r.status_code != 200:
            raise Exception(f'Bad status code ({r.status_code})')
        im = Image.open(r.raw).convert('RGB')
        width, height = im.size
        new_width  = 800
        new_height = new_width * height // width
        return im.resize((new_width, new_height), Image.ANTIALIAS)

    async def _retrieve_img_async(self, pageno, session):
        async with session.get(f'{self.server}{self.hash}/{self.page_array[pageno]}', timeout=None) as resp:
            if resp.status != 200:
                raise Exception(f'HTTP {resp.status}')
            im = Image.open(io.BytesIO(await resp.read())).convert('RGB')
            width, height = im.size
            new_width  = 800
            new_height = new_width * height // width
            return im.resize((new_width, new_height), Image.ANTIALIAS)

    def _fetch(self):
        json_obj = requests.get(f'https://mangadex.org/api/chapter/{self.id}').json()
        if json_obj['status'] != 'OK':
            raise Exception(f'Bad status ({json_obj["status"]})')
        self.title = json_obj['title']
        self.chapter_no = int(json_obj['chapter'])
        self.group_name = json_obj['group_name']
        self.group_id = json_obj['group_id']
        self.lang_name = json_obj['lang_name']
        self.hash = json_obj['hash']
        self.server = json_obj['server']
        self.page_array = json_obj['page_array']
        self.page_count = len(self.page_array)
        self.timestamp = json_obj['timestamp']

class Manga:
    __slots__ = ('id', 'title', 'description',
                 'last_updated', 'author', 'artist',
                 'chapters', 'cover_url')

    def __init__(self, id):
        self.id = id
        self._fetch()

    def download(self, predicate, folder_name=None):
        if not folder_name:
            folder_name = self.title
        asyncio.run(self._download_all(predicate, folder_name))

    def get_chapters(self, predicate):
        return [chapter for chapter in self.chapters if predicate(chapter)]

    def __str__(self):
        s = ''
        s += f'Title: {self.title}\n'
        s += f'Description: {self.description}\n'
        s += f'Last updated: {datetime.fromtimestamp(self.last_updated).strftime("%m/%d/%Y:%H:%M:%S")}\n'
        s += f'Author: {self.author}\n'
        s += f'Artist: {self.artist}\n'
        s += f'Entries: {len(self.chapters)}\n'
        return s

    async def _download_all(self, predicate, folder_name):
        semaphore = asyncio.Semaphore(10)
        chapters = self.get_chapters(predicate)
        directory = os.path.join(os.getcwd(), folder_name)
        if not os.path.exists(directory):
            os.mkdir(directory)
        await asyncio.gather(*[chapter.download_async(semaphore, pdf_file=os.path.join(directory, f'chapter{chapter.chapter_no}.pdf')) \
                                                      for chapter in chapters])
        print(f'Downloaded {self.title} ({self.id})')

    def _fetch(self):
        json_obj = requests.get(f'https://mangadex.org/api/manga/{self.id}').json()
        if json_obj['status'] != 'OK':
            raise Exception(f'Bad status ({json_obj["status"]})')
        self.title = json_obj['manga']['title']
        self.description = json_obj['manga']['description']
        self.last_updated = json_obj['manga']['last_updated']
        self.author = json_obj['manga']['author']
        self.artist = json_obj['manga']['artist']
        self.chapters = []
        chapter_dict = json_obj['chapter']
        for chapter_id, v in chapter_dict.items():
            self.chapters.append(Chapter(int(chapter_id), title=v['title'], \
                                                     chapter_no=float(v['chapter']), \
                                                     group_name=v['group_name'], \
                                                     group_id=v['group_id'], \
                                                     lang_name=v['lang_name'], \
                                                     timestamp=v['timestamp']))
        self.cover_url = json_obj['manga']['cover_url']
