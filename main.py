import MangaWatchDog as L
import Logger
import time as t
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def main():
    Mangas = [L.MangaWatchDog(44394, 'English'), L.MangaWatchDog(32386, 'English')]
    print(Mangas[0].comapareTimes())
    print(Mangas[0].checkLanguage())
    #sendEmail('Hola')
    # Log.logData()
    actualLog = Logger.logger(1)
    actualLog.createLog(Mangas[0])
    while True:
        loopWatch(MangaList=Mangas)
        t.sleep(5)
    # manga = MD.Manga(44394)
    # # manga.download(lambda chapter: chapter.group_id == 4896)
    # list_of_chapters = manga.get_chapters(lambda chapter: chapter.lang_name == 'English')
    # print(manga.get_chapters(lambda chapter: chapter.group_id == 4896))
    # new_list_chapters = manga.get_chapters(lambda chapter: chapter.lang_name == 'English')


def loopWatch(MangaList):
    '''Function takes in a list of mangas and generates an alarm if there is an update found

    in progress----------'''
    for Manga in MangaList:
        if Manga.comapareTimes() == 1:
            print('New update found for manga '.join(Manga.manga.title))
            if Manga.checkLanguage() == 1:
                alarm(Manga)
        else:
            print('No update found for manga ', Manga.manga.title, ' at ', datetime.now())


def alarm(Manga):
    print('New update found for manga ', Manga.manga.title, ' at', datetime.now())
    message = '''A new update has been found for the manga ' + {} +'\n 
    The new chapter is number ' + {} +'\n'''.format(Manga.manga.title, Manga.latestChapterNumber)
    sendEmail(message)


def sendEmail(mail_content):
    # The mail addresses and password
    sender_address = 'flow.error.apame@gmail.com'
    sender_pass = 'Shippuden1991'
    receiver_address = 'joseal9706@gmail.com'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Python Manga Updates'  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')


if __name__ == '__main__':
    main()
