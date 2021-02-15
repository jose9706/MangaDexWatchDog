import MangaDexAPI as md
import csv
import pandas
class MangaWatchDog():
    """Class takes in a manga id and then implements all the required functions to be able to log that manga
    with the intention of knowing when a new chapter is out. Can be modified to only find new chapters of a desired
    language"""

    def __init__(self, manga_id, language='English', createFromLog=False, debug=False):
        """Constructor for Logger"""
        if createFromLog:
            print('creating from log')
            df = pandas.read_csv('DexLogger.csv')
            print(df)
            # not implemented yet
        else:
            self.id = manga_id
            self.manga = md.Manga(manga_id)
            self.updateTime = self.manga.last_updated
            self.language = language
            self.debug = debug
            self.createFromLog = False
            # The first chapter is always in index 0 of the list returned of all the chapters. The list contains
            # chapters and each chapter has a property called chapter_no
            self.latestChapterNumber = self.manga.get_chapters(lambda chapter: chapter.lang_name == language)[
                0].chapter_no

    def comapareTimes(self) -> int:
        '''Function returns a value depending if the manga has been updated recently compared to the last time checked.

        Also updates the required values for the next check'''
        self.manga = md.Manga(self.id)
        newUpdateTime = self.manga.last_updated
        flag = 1 if newUpdateTime > self.updateTime else 0
        self.updateTime = newUpdateTime
        return flag

    def checkLanguage(self) -> int:
        '''This Functions returns a value of 1 if theres a chapter with a higher number than the previous recorded one
        1 for new chapter and 0 for no new chapter.

        Algo updates values for the new iteration of the function'''
        newLatestChapter = self.manga.get_chapters(lambda chapter: chapter.lang_name == self.language)[0].chapter_no
        flag = 1 if self.latestChapterNumber < newLatestChapter else 0
        self.latestChapterNumber = newLatestChapter
        return flag


    def logData(self):
        if self.createFromLog:
            #Do something since i created from a log
            print('updating from log based on createFromLog')
        else:
            titles = ["Manga ID", 'LastUpdateTime', 'LatestChapterNumber', 'Language']
            with open('DexLogger.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(titles)
                values = [self.id, self.updateTime, self.latestChapterNumber, self.language]
                writer.writerow(values)

