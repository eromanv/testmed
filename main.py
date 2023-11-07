from fastapi import FastAPI
from datetime import datetime, timedelta

import arrow
app = FastAPI()

busy = [
    {'start': '10:30', 'stop': '10:50'},
    {'start': '18:40', 'stop': '18:50'},
    {'start': '14:40', 'stop': '15:50'},
    {'start': '16:40', 'stop': '17:20'},
    {'start': '20:05', 'stop': '20:20'},
]

busy = sorted(busy, key=lambda x: x['start'])
window_size = 30

def generate_free_windows():
    working_start = '09:00'
    working_end = '21:00'

    busy_times = [(arrow.get(slot['start'], 'HH:mm'), arrow.get(slot['stop'], 'HH:mm')) for slot in busy]
    slots = []

    current_time = arrow.get(working_start, 'HH:mm')
    while current_time < arrow.get(working_end, 'HH:mm'):
        slot_stop = min(current_time.shift(minutes=window_size), arrow.get(working_end, 'HH:mm'))
        slots.append({'start': current_time.format('HH:mm'), 'stop': slot_stop.format('HH:mm')})
        current_time = slot_stop

    free_windows = [slot for slot in slots if not any(is_intersecting(slot['start'], slot['stop'], busy_start.format('HH:mm'), busy_stop.format('HH:mm')) for busy_start, busy_stop in busy_times)]

    return {"free_slots": free_windows}

def is_intersecting(start1, stop1, start2, stop2):
    return arrow.get(start1, 'HH:mm') < arrow.get(stop2, 'HH:mm') and arrow.get(start2, 'HH:mm') < arrow.get(stop1, 'HH:mm')

def add_time(current_time, minutes):
    time_format = '%H:%M'
    current_datetime = datetime.strptime(current_time, time_format)
    new_datetime = current_datetime + timedelta(minutes=minutes)
    return new_datetime.strftime(time_format)

@app.get("/")
def get_free_windows():
    result = generate_free_windows()
    return result

