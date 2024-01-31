import datetime
import os

class EventInfo(object):
    def __init__(self, i, event, picks, type):
        self.event_index = i
        self.event = {}; self.picks = []
        if type == "real":
            # read
            ## event
            event = event.split()

            self.event["index"] = int(event[0])

            self.event["year"] = event[1]
            self.event["month"] = event[2]
            self.event["day"] = event[3]
            self.event["time"] = event[4]

            event_timestamp_str = self.event["year"] + self.event["month"] + self.event["day"] + " " + self.event["time"]
            event_timestamp_dt = datetime.datetime.strptime(event_timestamp_str, '%Y%m%d %H:%M:%S.%f')
            self.event["timestamp"] = event_timestamp_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

            self.event["otime"] = float(event[5])
            self.event["residual"] = float(event[6])

            self.event["lat"] = float(event[7])
            self.event["lon"] = float(event[8])
            self.event["dep"] = float(event[9])

            self.event["mag"] = float(event[10])
            self.event["mag_var"] = float(event[11])

            self.event["nP"] = int(event[12])
            self.event["nS"] = int(event[13])
            self.event["nPorS"] = int(event[14])
            # self.event["nPandS"] = int(event[15])

            self.event["station_gap"] = float(event[15])

            ## picks
            picks = [pick.split() for pick in picks]
            
            for rawpick in picks:
                pick = {}

                pick["net"] = rawpick[0]
                pick["id"] = rawpick[1]
                pick["type"] = rawpick[2].lower()

                pick["absolute_time"] = float(rawpick[3])
                pick["time"] = float(rawpick[4])

                pick_timestamp_dt = event_timestamp_dt + datetime.timedelta(seconds=pick["time"])
                pick["timestamp"] = pick_timestamp_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

                pick["amp"] = float(rawpick[5])
                pick["residual"] = float(rawpick[6])
                pick["prob"] = float(rawpick[7]) # weight for REAL
                pick["azimuth"] = float(rawpick[8])

                self.picks.append(pick)

        elif type == "json":
            self.event = event; self.picks = picks

        else:
            print("[EventInfo.__init__] Error: Unsupported format", type)
            exit(1)

    def toJson(self):
        return {"index": self.event_index, "eventInfo": self.event, "picksInfo": self.picks}
    
    def toWinpick(self, outdir, stntbl):
        # func
        def p3_value(id, picks, ev, chtbl):
            # id
            chid_UD = chtbl[(chtbl[3] == id) & (chtbl[4].isin(['UD', 'U', 'Z', 'VZ']))].values[0][0] # vertical compornent for P phase and maxamp
            chid_EW = chtbl[(chtbl[3] == id) & (chtbl[4].isin(['EW', 'E', 'X', 'VX']))].values[0][0] # horizontal compornent for S phase

            # pick
            values = []; amps = {}
            for pick in picks:
                type = pick["type"]
                time = pick["time"]
                pol = '+0'

                amp = str(pick["amp"])
                
                ## P phase
                if type == "p":
                    tp = str(time).split('.')
                    tp1 = tp[0].zfill(2)
                    tp2 = tp[1][0:3]

                    value = " ".join([chid_UD, '0', tp1, tp2, tp1, tp2, pol])
                
                ## S phase
                elif type == "s":
                    ts = str(time).split('.')
                    ts1 = ts[0].zfill(2)
                    ts2 = ts[1][0:3]

                    value = " ".join([chid_EW, '1', ts1, ts2, ts1, ts2, pol])

                values.append(value)
                amps[type] = amp
                
            # maxamp
            maxamp_type = max(amps, key=amps.get)
            maxamp = amps[maxamp_type]
            pol = '-1'

            if maxamp_type == "p":
                value = " ".join([chid_EW, '3', tp1, tp2, tp1, tp2, pol, maxamp])

            elif maxamp_type == "s":
                value = " ".join([chid_EW, '3', ts1, ts2, ts1, ts2, pol, maxamp])
            
            values.append(value)

            return values

        # main
        idx = self.event_index
        ev = self.event
        picks = self.picks
        stations = set([pick["id"] for pick in picks])

        chtbl = stntbl.chtbl_df

        # file name
        t1 = datetime.datetime.strptime(ev["timestamp"], "%Y-%m-%dT%H:%M:%S.%f").strftime("%y%m%d.%H%M%S") + "-000" # win default is first P pick
        i = 0
        while True:
            fname = os.path.join(outdir, t1)
            if os.path.exists(fname):
                t1 = "-".join(["-".join(t1.split("-")[:-1]), str(i+1).zfill(3)])
                i += 1
            else:
                break

        # first line
        p1 = ' '.join(['#p', t1, str(idx), 'auto']) + '\n'

        # second line
        t2 = datetime.datetime.strptime(ev["timestamp"], "%Y-%m-%dT%H:%M:%S.%f").strftime("%y %m %d %H %M %S")
        p2 = ' '.join(['#p', t2]) + '\n'

        # third line and beyond
        p3_values = []
        for id in stations:
            picks_id = [pick for pick in picks if pick["id"] == id]
            p3_values += p3_value(id, picks_id, ev, chtbl)
        p3_list = [' '.join(['#p', p3_value]) + '\n' for p3_value in p3_values]

        # write
        with open(fname, 'w') as f:
            f.write(p1)
            f.write(p2)
            f.writelines(p3_list)