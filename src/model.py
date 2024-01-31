import json
import datetime

class Picks(object):
    def __init__(self, in_file):
        with open(in_file) as f:
            meta = json.load(f)
        self.meta = meta

        days = []
        for pick in self.meta:
            day = datetime.datetime.strptime(pick['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
            if day.date() not in days:
                days.append(day.date())
        days = sorted(days)
        first_day = days[0]

        if len(days) != 1:
            print("[WARN]: Only the 1st day of data within the file is processed. Please divide the data into daily data.")
            self.meta = [pick for pick in self.meta if datetime.datetime.strptime(pick['timestamp'], "%Y-%m-%dT%H:%M:%S.%f").date() == first_day]

        self.day = first_day.strftime('%Y%m%d')