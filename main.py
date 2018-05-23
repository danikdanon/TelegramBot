#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from parser import get_page
from BuildingDictionaries import dictCurrNext, dictCurrPrev, wordCntDict
from operator import itemgetter
import numpy
import matplotlib.pyplot as mpl


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    msg = '''/ParsePage url - просканировать страницу и создать все необходимые словарики
             /describe  word - проанализировать слово
              /WordsEmissions - получить слова-выбросы
             /TopNwords (count) (rare,frequency) - топ (count) самых редких(частых) слов
             /DescribeFrequency - построить график распределения частот слов
             /DescribeLength - построить график распределения длин слов
             '''
    update.message.reply_text(msg)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def describe(bot, update):
    word = update.message.text.split()[1]
    cnt =  WordsCnt[word]

    MostFrequentAfter = sorted(dictCurNext[word].items(), key=itemgetter(1))
    MostFrequentBefore = sorted(dictCurPrev[word].items(), key=itemgetter(1))

    if len(MostFrequentBefore) < 3 or len(MostFrequentAfter) < 3:
        update.message.reply_text('There is not enough info about this word')
        return

    reply = 'Count - {}  MostFrequentAfter: {}, {}, {}.  MostFrequentBefore: {}, {}, {}.'.format(cnt,MostFrequentAfter[0][0], MostFrequentAfter[1][0], MostFrequentAfter[1][0], MostFrequentBefore[0][0], MostFrequentBefore[1][0], MostFrequentBefore[2][0])
    update.message.reply_text(reply)

def parse(bot, update):
    txt = update.message.text
    l = txt.split(' ')
    url = l[1]
    page = get_page(url)
    update.message.reply_text('parse пошел')
    global dictCurPrev
    global dictCurNext
    global WordsCnt
    dictCurPrev = dictCurrPrev(page)
    dictCurNext = dictCurrNext(page)
    WordsCnt = wordCntDict(page)

def WordsEmissions(bot, update):
    update.message.reply_text('wordEmissions пошел')
    FrequencyOfWords = []
    for word in WordsCnt:
        FrequencyOfWords.append(WordsCnt[word])
    std_variation= numpy.std(FrequencyOfWords)
    avg_variation = numpy.mean(FrequencyOfWords)
    left_bound = avg_variation - 3*std_variation
    right_bound = avg_variation + 3*std_variation

    for word in WordsCnt:
        if WordsCnt[word] < left_bound or WordsCnt[word] > right_bound:
            update.message.reply_text(word)

def PrintDicts():
    print(WordsCnt)


def TopN(bot, update):

    input = update.message.text.split()
    cnt = input[1]
    type = input[2]

    cnt = 100

    WOemissions = DeleteEmissions()
    WordsCntList = sorted(WOemissions.items(), key=itemgetter(1)) ## отсортили слова по частоте


    if type == 'frequent':
        update.message.reply_text('{} caмых частых слов '.format(cnt))
        count = 0
        for word in reversed(WordsCntList):
            update.message.reply_text(word[0], 'первое слово пошло блять')
            count += 1
            if count >= cnt:
                update.message.reply_text(word[0], 'вышел из цикла нахуй')
                break

    if type == 'rare':
        update.message.reply_text('{} caмых редких слов '.format(cnt))
        count = 0
        for word in WordsCntList:
            update.message.reply_text(word[0], 'первое слово пошло блять')
            count += 1
            if count >= cnt:
                update.message.reply_text(word[0], 'вышел из цикла нахуй')
                break




def DeleteEmissions():
    NewDict = {}
    FrequencyOfWords = []
    for word in WordsCnt:
        FrequencyOfWords.append(WordsCnt[word])
    std_variation = numpy.std(FrequencyOfWords)
    avg_variation = numpy.mean(FrequencyOfWords)
    left_bound = avg_variation - 3 * std_variation
    right_bound = avg_variation + 3 * std_variation

    for word in WordsCnt:
        if not (WordsCnt[word] < left_bound or WordsCnt[word] > right_bound):
            NewDict[word] = WordsCnt[word]

    return NewDict


def describe_frequency(bot, update):

    WOemissions = DeleteEmissions() # словарь без выбросов

    xAxis = []
    yAxis = []

    dict = {}  # словарик - частотность слова - количество слов с такой частотностью

    for word in WOemissions:
        cnt = WOemissions[word]
        if cnt in dict:
            dict[cnt] += 1
        else:
            dict[cnt] = 1

    for cnt in dict:
        xAxis.append(cnt)
        yAxis.append(dict[cnt])

    line_frequency = mpl.plot(xAxis, yAxis, 'go:')
    mpl.axis([0.0, 15.0, 0.0, 500.0])
    mpl.xlabel(u'Частота слова')
    mpl.ylabel(u'Кол-во слов с такой частотой')
    mpl.grid()

    mpl.savefig('/img.png', format='png')
    bot.send_photo(chat_id=update.message.chat_id, photo=open('img.png', 'rb'))
    mpl.clf()


def describe_length(bot, update, hist):
    WOemissions = DeleteEmissions()  # словарь без выбросов

    xAxis = []
    yAxis = []

    dict = {}  # словарик - длина слова - количество слов с такой длиной

    for word in WOemissions:
        length = len(word)
        if length in dict:
            dict[length] += 1
        else:
            dict[length] = 1

    for cnt in dict:
        xAxis.append(cnt)
        yAxis.append(dict[cnt])

    line_frequency = mpl.plot(xAxis, yAxis, 'go:')
    mpl.axis([0.0, 15.0, 0.0, 500.0])
    mpl.xlabel(u'Частота слова')
    mpl.ylabel(u'Кол-во слов с такой частотой')
    mpl.grid()

    mpl.savefig('/img.png', format='png')
    bot.send_photo(chat_id=update.message.chat_id, photo=open('img.png', 'rb'))
    mpl.clf()





TOKEN = '594769948:AAE6M4sgh-SkhlUIorlN0r6kXGD7_Xh-UHQ'
REQUEST_KWARGS={
    'proxy_url': 'socks5://whrpm.teletype.live:1080',
    # Optional, if you need authentication:
    'urllib3_proxy_kwargs': {
        'username': 'telegram',
        'password': 'telegram',
    }
}


WordsCnt = {}
dictCurPrev = {}
dictCurNext = {}


def main():
    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    dp.add_handler(CommandHandler('describe', describe))
    dp.add_handler(CommandHandler('ParsePage', parse))
    dp.add_handler(CommandHandler('WordsEmissions', WordsEmissions))
    dp.add_handler(CommandHandler('print', PrintDicts))
    dp.add_handler(CommandHandler('TopNwords', TopN))
    dp.add_handler(CommandHandler('DescribeFrequency', describe_frequency))
    dp.add_handler(CommandHandler('DescribeLength', describe_length))


    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()