import pandas
import MangaWatchDog
import csv
class logger():
    """"""

    def __init__(self, Mangas, createFromLog = False, LogPath = None):
        """Constructor for logger"""
        self.numberOfMangasWatched = Mangas

    def updateLog(self, Mangas):
        df = pandas.read_csv('DexLogger.csv')
        counter = 0
        for Mang in Mangas:
            df.iloc[counter] = [Mang.id, Mang.updateTime, Mang.latestChapterNumber, Mang.language]
            counter += 1
        df.to_csv('DexLogger.csv', index=False)


    def createLog(self, Mangas):
        titles = ["Manga ID", 'LastUpdateTime', 'LatestChapterNumber', 'Language']
        with open('DexLogger.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(titles)
            values = [Mangas.id, Mangas.updateTime, Mangas.latestChapterNumber, Mangas.language]
            writer.writerow(values)