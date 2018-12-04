#!/usr/bin/python
# coding: utf8

import requests
import datetime
import calendar
from dateutil import parser

from telegram.ext import Updater
import logging

TGRMBOT_TOKEN = "YOUR TELEGRAM BOT TOKEN"

TEAMUP_APIKEY = "YOUR TEAMUP API KEY"
TEAMUP_APIURL = "https://api.teamup.com"
TEAMUP_APICALENDAR = "YOUR CALENDAR ID"

TEAMUP_APISUBCALENDAR = {
            'YOUR SUBCALENDARID1': 'Raum Klein',
            'YOUR SUBCALENDARID2': 'Raum Gross (Vorne)',
            'YOUR SUBCALENDARID3': 'Raum Gross (Hinten)'
        }

INTERVAL_MINUTES = 5 

def tu_getchanges(bot, job):
    tu_headers = {'Teamup-Token': TEAMUP_APIKEY}
    tu_url = TEAMUP_APIURL + '/' + TEAMUP_APICALENDAR + '/events'
    dt_lastcall = datetime.datetime.utcnow() + datetime.timedelta(minutes=-INTERVAL_MINUTES)
    tu_lastcall = calendar.timegm(dt_lastcall.timetuple())
    tu_payload = {'modifiedSince': tu_lastcall}
    tu_response = requests.get(tu_url, headers=tu_headers, params=tu_payload)
    
    tu_changedevents = tu_response.json()
    data_posttg = []
    for tu_event in tu_changedevents['events']:
        tu_startdate = parser.parse(tu_event['start_dt'])
        tu_enddate = parser.parse(tu_event['end_dt'])
        txt_post = tu_event['title'] + " - " + TEAMUP_APISUBCALENDAR[str(tu_event['subcalendar_id'])] + " - " + tu_startdate.strftime('%d.%m.%Y %H') + "-" + tu_enddate.strftime('%H h')
        if (tu_event['delete_dt'] is not None):
            txt_post += " geloescht"
        data_posttg.append(txt_post)      
    msg = "Kalenderupdate:\n"
    if len(data_posttg) < 20 and len(data_posttg) > 0:
        for ev in data_posttg:
            msg += ev + "\n"
        msg += "\n"
        msg += "https://teamup.com/"+TEAMUP_APICALENDAR+"\n"
        for chat in Chats:
            print(chat)
            bot.send_message(chat_id=chat, 
                text=msg)
    elif len(data_posttg) > 0 :
        msg += "Zuviele Änderungen..."
        msg += "\n"
        msg += "https://teamup.com/"+TEAMUP_APICALENDAR+"\n"
        for chat in Chats:
            bot.send_message(chat_id=chat, 
                text=msg)

    #bot.send_message(chat_id='94397642', 
    #    text=msg)

def tu_gettoday(bot, update):
    tu_headers = {'Teamup-Token': TEAMUP_APIKEY}
    tu_url = TEAMUP_APIURL + '/' + TEAMUP_APICALENDAR + '/events'
    dt_start = datetime.date.today()
    #dt_end = dt_start + datetime.timedelta(hours=24)
    tu_start = datetime.date.isoformat(dt_start)
    #tu_end = datetime.date.isoformat(dt_end)
    tu_payload = {'startDate': tu_start, 'endDate': tu_start}
    #tu_payload = {}
    tu_response = requests.get(tu_url, headers=tu_headers, params=tu_payload)
    tu_todayevents = tu_response.json()
    data_posttg = []
    for tu_event in tu_todayevents['events']:
        tu_startdate = parser.parse(tu_event['start_dt'])
        tu_enddate = parser.parse(tu_event['end_dt'])
        txt_post = tu_event['title'] + " - " + TEAMUP_APISUBCALENDAR[str(tu_event['subcalendar_id'])] + " - " + tu_startdate.strftime('%d.%m.%Y %H') + "-" + tu_enddate.strftime('%H h')
        data_posttg.append(txt_post)      
    msg = "Heute:\n"
    if len(data_posttg) < 20 and len(data_posttg) > 0:
        for ev in data_posttg:
            msg += ev + "\n"
        msg += "\n"
        msg += "https://teamup.com/"+TEAMUP_APICALENDAR+"\n"
        bot.send_message(chat_id=update.message.chat_id, text=msg)
    elif len(data_posttg) > 0 :
        msg += "Zuviele Termine\n"
        msg += "\n"
        msg += "https://teamup.com/"+TEAMUP_APICALENDAR+"\n"
        bot.send_message(chat_id=update.message.chat_id, text=msg)
    else:
        msg += "Scheint frei zu sein...\n"
        msg += "\n"
        msg += "https://teamup.com/"+TEAMUP_APICALENDAR+"\n"
        bot.send_message(chat_id=update.message.chat_id, text=msg)
    #bot.send_message(chat_id='94397642', 
    #    text=msg)


Chats = []
updater = Updater(token=TGRMBOT_TOKEN)
dispatcher = updater.dispatcher
j = updater.job_queue

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                             level=logging.INFO)
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Kalenderupdate-Bot")
    Chats.append(update.message.chat_id)

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

today_handler = CommandHandler('today', tu_gettoday)
dispatcher.add_handler(today_handler)

def callback_minute(bot, job):
    bot.send_message(chat_id=bot.get_updates()[-1].message.chat_id, 
    text='One message every minute')

#enable for broadcasting calendar changes to all connected channels   
#job_minute = j.run_repeating(tu_getchanges, interval=60*INTERVAL_MINUTES, first=0)    

updater.start_polling()
updater.idle()
