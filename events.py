import datetime
import os
import requests
from icalendar import Calendar

import mongo


ICALENDAR_URL = os.environ.get('ICALENDAR_URL')

def parsedt(comp):
    if comp and hasattr(comp, 'dt'):
        dt = comp.dt
        if isinstance(dt, datetime.date):
            dt = datetime.datetime.combine(dt, datetime.time(0, 0, 0, 0))
        return dt

def refresh():

    resp = requests.get(ICALENDAR_URL)
    cal = Calendar.from_ical(resp.content)

    for event in cal.subcomponents:

        uid = event['UID']
        title = event['SUMMARY']
        url = event['DESCRIPTION']

        location = event['LOCATION']

        start = parsedt(event['DTSTART'])
        end = parsedt(event['DTEND'])

        spec = {'uid': uid}
        doc = {
            'uid': uid,
            'title': title,
            'url': url,
            'location': location,
            'start': start,
            'end': end,
        }

        db = mongo.connect()
        db.events.update(spec, {'$set': doc}, upsert=True)

def upcoming_events():
    db = mongo.connect()
    c = db.events.find({}).sort('start', 0)
    return list(c)

def previous_events():
    pass


if __name__ == '__main__':
    refresh()
