#!/usr/bin/env python3.4
# -*- coding: utf8 -*-

import telegram
import logging
import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, request

# Telegram Bot Authorization Token (Get from @BotFather)
TOKEN = 'TOKEN'

welcome = '''
Greetings. I am OpenBibleBot.

I will send you Bible Verses if you ask nicely.
You can do so by placing references after a /bible or /성경 command.

Example:
/bible Jn 1:1-5
/성경 요 1:1-5
'''

syntaxhelp = '''
I can send you text from the Bible if you learn how to ask nicely.

English syntax:
/bible Jn 1
/bible Jn 1:1-5
/bible Gn 1:1, Jn 1:1-5, Jn 15:3

Korean syntax:
/성경 요 1
/성경 요 1:1-5
/성경 창 1:1, 요 1:1-5, 요 15:3

Give me a try and see what I can do.
'''

refdict = {u'~':u'-',u'창':u'Gn',u'창세기':u'Genesis',u'출':u'Ex',u'출애굽기':u'Exodus',u'레':u'Lv',u'레위기':u'Leviticus',u'민':u'Nm',u'민수기':u'Numbers',u'신':u'Dt',u'신명기':u'Deuteronomy',u'수':u'Jo',u'여호수아':u'Joshua',u'삿':u'Jgs',u'사사기':u'Judges',u'룻':u'Ru',u'룻기':u'Ruth',u'삼상':u'1 Sm',u'사무엘상':u'1 Samuel',u'삼하':u'2 Sm',u'사무엘하':u'2 Samuel',u'왕상':u'1 Kgs',u'열왕기상':u'1 Kings',u'왕하':u'2 Kgs',u'열왕기하':u'2 Kings',u'대상':u'1 Chr',u'역대상':u'1 Chronicles',u'대하':u'2 Chr',u'역대하':u'2 Chronicles',u'스':u'Ezr',u'에스라':u'Ezra',u'느':u'Neh',u'느헤미야':u'Nehemiah',u'에':u'Est',u'에스더':u'Esther',u'욥':u'Jb',u'욥기':u'Job',u'시':u'Ps',u'시편':u'Psalms',u'잠':u'Prv',u'잠언':u'Proverbs',u'전':u'Eccl',u'전도서':u'Ecclesiastes',u'아':u'Sg',u'아가':u'Song of Songs',u'사':u'Is',u'이사야':u'Isaiah',u'렘':u'Jer',u'예레미야':u'Jeremiah',u'애':u'Lam',u'예레미야애가':u'Lamentations',u'겔':u'Ez',u'에스겔':u'Ezekiel',u'단':u'Dn',u'다니엘':u'Daniel',u'호':u'Hos',u'호세아':u'Hosea',u'욜':u'Jl',u'요엘':u'Joel',u'암':u'Am',u'아모스':u'Amos',u'옵':u'Ob',u'오바댜':u'Obadiah',u'욘':u'Jon',u'요나':u'Jonah',u'미':u'Mi',u'미가':u'Micah',u'나':u'Na',u'나훔':u'Nahum',u'합':u'Hb',u'하박국':u'Habakkuk',u'습':u'Zep',u'스바냐':u'Zephaniah',u'학':u'Hg',u'학개':u'Haggai',u'슥':u'Zec',u'스가랴':u'Zechariah',u'말':u'Mal',u'말라기':u'Malachi',u'마':u'Mt',u'마태복음':u'Matthew',u'막':u'Mk',u'마가복음':u'Mark',u'눅':u'Lk',u'누가복음':u'Luke',u'요':u'Jn',u'요한복음':u'John',u'행':u'Acts',u'사도행전':u'Acts',u'롬':u'Rom',u'로마서':u'Romans',u'고전':u'1 Cor',u'고린도전서':u'1 Corinthians',u'고후':u'2 Cor',u'고린도후서':u'2 Corinthians',u'갈':u'Gal',u'갈라디아서':u'Galatians',u'엡':u'Eph',u'에베소서':u'Ephesians',u'빌':u'Phil',u'빌립보서':u'Philippians',u'골':u'Col',u'골로새서':u'Colossians',u'살전':u'1 Thes',u'데살로니가전서':u'1 Thessalonians',u'살후':u'2 Thes',u'데살로니가후서':u'2 Thessalonians',u'딤전':u'1 Tm',u'디모데전서':u'1 Timothy',u'딤후':u'2 Tm',u'디모데후서':u'2 Timothy',u'딛':u'Ti',u'디도서':u'Titus',u'몬':u'Phlm',u'빌레몬서':u'Philemon',u'히':u'Heb',u'히브리서':u'Hebrews',u'약':u'Jas',u'야고보서':u'James',u'벧전':u'1 Pt',u'베드로전서':u'1 Peter',u'벧후':u'2 Pt',u'베드로후서':u'2 Peter',u'요일':u'1 Jn',u'요한1서':u'1 John',u'요이':u'2 Jn',u'요한2서':u'2 John',u'요삼':u'3 Jn',u'요한3서':u'3 John',u'유':u'Jude',u'유다서':u'Jude',u'계':u'Rv',u'요한계시록':u'Revelation',u'Gn':u'창',u'Genesis':u'창세기',u'Ex':u'출',u'Exodus':u'출애굽기',u'Lv':u'레',u'Leviticus':u'레위기',u'Nm':u'민',u'Numbers':u'민수기',u'Dt':u'신',u'Deuteronomy':u'신명기',u'Jo':u'수',u'Joshua':u'여호수아',u'Jgs':u'삿',u'Judges':u'사사기',u'Ru':u'룻',u'Ruth':u'룻기',u'1 Sm':u'삼상',u'1 Samuel':u'사무엘상',u'2 Sm':u'삼하',u'2 Samuel':u'사무엘하',u'1 Kgs':u'왕상',u'1 Kings':u'열왕기상',u'2 Kgs':u'왕하',u'2 Kings':u'열왕기하',u'1 Chr':u'대상',u'1 Chronicles':u'역대상',u'2 Chr':u'대하',u'2 Chronicles':u'역대하',u'Ezr':u'스',u'Ezra':u'에스라',u'Neh':u'느',u'Nehemiah':u'느헤미야',u'Est':u'에',u'Esther':u'에스더',u'Jb':u'욥',u'Job':u'욥기',u'Ps':u'시',u'Psalms':u'시편',u'Prv':u'잠',u'Proverbs':u'잠언',u'Eccl':u'전',u'Ecclesiastes':u'전도서',u'Sg':u'아',u'Song of Songs':u'아가',u'Is':u'사',u'Isaiah':u'이사야',u'Jer':u'렘',u'Jeremiah':u'예레미야',u'Lam':u'애',u'Lamentations':u'예레미야애가',u'Ez':u'겔',u'Ezekiel':u'에스겔',u'Dn':u'단',u'Daniel':u'다니엘',u'Hos':u'호',u'Hosea':u'호세아',u'Jl':u'욜',u'Joel':u'요엘',u'Am':u'암',u'Amos':u'아모스',u'Ob':u'옵',u'Obadiah':u'오바댜',u'Jon':u'욘',u'Jonah':u'요나',u'Mi':u'미',u'Micah':u'미가',u'Na':u'나',u'Nahum':u'나훔',u'Hb':u'합',u'Habakkuk':u'하박국',u'Zep':u'습',u'Zephaniah':u'스바냐',u'Hg':u'학',u'Haggai':u'학개',u'Zec':u'슥',u'Zechariah':u'스가랴',u'Mal':u'말',u'Malachi':u'말라기',u'Mt':u'마',u'Matthew':u'마태복음',u'Mk':u'막',u'Mark':u'마가복음',u'Lk':u'눅',u'Luke':u'누가복음',u'Jn':u'요',u'John':u'요한복음',u'Acts':u'행',u'Acts':u'사도행전',u'Rom':u'롬',u'Romans':u'로마서',u'1 Cor':u'고전',u'1 Corinthians':u'고린도전서',u'2 Cor':u'고후',u'2 Corinthians':u'고린도후서',u'Gal':u'갈',u'Galatians':u'갈라디아서',u'Eph':u'엡',u'Ephesians':u'에베소서',u'Phil':u'빌',u'Philippians':u'빌립보서',u'Col':u'골',u'Colossians':u'골로새서',u'1 Thes':u'살전',u'1 Thessalonians':u'데살로니가전서',u'2 Thes':u'살후',u'2 Thessalonians':u'데살로니가후서',u'1 Tm':u'딤전',u'1 Timothy':u'디모데전서',u'2 Tm':u'딤후',u'2 Timothy':u'디모데후서',u'Ti':u'딛',u'Titus':u'디도서',u'Phlm':u'몬',u'Philemon':u'빌레몬서',u'Heb':u'히',u'Hebrews':u'히브리서',u'Jas':u'약',u'James':u'야고보서',u'1 Pt':u'벧전',u'1 Peter':u'베드로전서',u'2 Pt':u'벧후',u'2 Peter':u'베드로후서',u'1 Jn':u'요일',u'1 John':u'요한1서',u'2 Jn':u'요이',u'2 John':u'요한2서',u'3 Jn':u'요삼',u'3 John':u'요한3서',u'Jude':u'유',u'Jude':u'유다서',u'Rv':u'계',u'Revelation':u'요한계시록'}

app = Flask(__name__)

global bot
logging.basicConfig(level=logging.DEBUG)

bot = telegram.Bot(TOKEN)  # Initialize the bot

@app.route('/' + TOKEN + '/HOOK', methods=['POST'])
def webhook_handler():
    try:
        if request.method == 'POST':
            # retrieve the message in JSON and then transform it to Telegram object
            update = telegram.Update.de_json(request.get_json(force=True))
            chat_id = update.message.chat.id
            text = update.message.text

            if '/start' in text:
                bot.sendMessage(chat_id=chat_id, text=welcome)
                return 'ok'
            elif '/help' in text:
                bot.sendMessage(chat_id=chat_id, text=syntaxhelp)
                return 'ok'
            elif text.startswith("/bible "):
                retrieve_english(text[7:], chat_id)
                return 'ok'
            elif text.startswith("/성경 "):
                print(text[3:])
                retrieve_korean(text[3:], chat_id)
                return 'ok'
            else:
                return 'ok'
        else:
            return 'ok'
    except:
        return 'ok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('https://bot.openbible.me/' + TOKEN + '/HOOK')
    # s = bot.setWebhook('')
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


def multiple_replace(dict, text):

    ''' Replace in 'text' all occurences of any key in the given
    dictionary by its corresponding value and returns a new string.'''

    # Create a regular expression from all the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)


def retrieve_english(reflist, chat_id):

    # Set a baseline response in case the requested reference is not understood.
    final = "I cannot understand that reference. Maybe you want to switch languages?"

    payload = {'passage': reflist, 'version': 'nasb'}
    xml = requests.get("http://api.preachingcentral.com/bible.php", params=payload)
    soup = BeautifulSoup(xml.text, 'xml')

    finaltext = []
    for ref in soup('range'):
        reference = ref.result.text
        reference = ' (' + reference + ')'
        reftext = []
        for item in ref('text'):
            reftext.append(item.text)
        reftext = ' '.join(reftext)
        reftext += reference
        finaltext.append(reftext)
        final = '\n\n'.join(finaltext)

    # Send out the final message
    bot.sendMessage(chat_id=chat_id, text=final)
    return 'ok'


def retrieve_korean(reflist, chat_id):

    # Set a baseline response in case the requested reference is not understood.
    final = "I cannot understand that reference. Maybe you want to switch languages?"

    reflist = multiple_replace(refdict, reflist)
    payload = {'passage': reflist, 'version': 'korean'}
    xml = requests.get("http://api.preachingcentral.com/bible.php", params=payload)
    soup = BeautifulSoup(xml.text, 'xml')

    finaltext = []
    for ref in soup('range'):
        reference = ref.result.text
        reference = ref.result.text
        reference = multiple_replace(refdict, reference)
        reference = ' (' + reference + ')'
        reftext = []
        for item in ref('text'):
            reftext.append(item.text)
        reftext = ' '.join(reftext)
        reftext = reftext.encode('latin1').decode('utf8')
        reftext += reference
        finaltext.append(reftext)
        final = '\n\n'.join(finaltext)

    # Send out the final message
    bot.sendMessage(chat_id=chat_id, text=final.encode('utf-8'))
    return 'ok'

@app.route('/')
def hello():
    return 'Hello, world!'

@app.errorhandler(404)
def page_not_found(e):
    return 'Sorry, nothing at this URL.', 404
