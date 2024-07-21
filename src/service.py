import os
import datetime
import json
import subprocess as sp
import pandas as pd

from model import Picks
from model_event import EventInfo

class PickConverter(object):
    def __init__(self, config):
        self.config = config
    
    def convertFromJson(self, config, realExecutor):
        # set config
        ## itr
        self.n = config.n

        ## input
        self.infile = self.config.infile
        self.picks = Picks(self.infile)

        ## output
        self.file_day = self.picks.day
        self.datatmp_dir_header = os.path.join(self.config.tmpdir, 'data-%s' % self.n)
        self.outtmp_dir_header = os.path.join(self.config.tmpdir, 'out-%s' % self.n)
        self.datatmp_dir = os.path.join(self.datatmp_dir_header, self.file_day)
        self.outtmp_dir = os.path.join(self.outtmp_dir_header, self.file_day)
        os.makedirs(self.datatmp_dir, exist_ok=True)
        os.makedirs(self.outtmp_dir, exist_ok=True)

        # read input
        if self.n-1 >= 0:
            originalPicks = pd.DataFrame(self.picks.meta)
            preAssociatedPicks = pd.DataFrame(realExecutor.picklist())
                  
            originalKeys = self.picks.meta[0].keys()
            merged_df = pd.merge(originalPicks, preAssociatedPicks, on=["id", "type", "timestamp"], how="left", suffixes=('', '_pre'), indicator=True)
            # merged_df.to_csv("tmp%s.csv" % self.n)
            unique_elements_df = merged_df[merged_df["_merge"] == "left_only"][originalKeys]
            picks = unique_elements_df.to_dict(orient='records')
        else:
            picks = self.picks.meta

        # read picks
        picks_dict = {}
        for pick in picks:
            id = pick['id']
            amp = pick['amp']
            type = pick['type']
            
            if id not in picks_dict.keys():
                picks_dict[id] = {}
            if type not in picks_dict[id].keys():
                picks_dict[id][type] = []
            picks_dict[id][type].append(pick)

        # write picks
        for id, picks_id in picks_dict.items():
            for type, picks in picks_id.items():
                for pick in picks:
                    # read
                    timestamp = pick['timestamp']
                    prob = pick['prob']
                    amp = pick['amp']
                    
                    # file name
                    net = "net"
                    type = type.upper()
                    outtxt = ".".join([net, id, type]) + ".txt"

                    # value
                    timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
                    base_time = datetime.datetime.strptime(self.file_day, '%Y%m%d') #REALは0時基準の相対時刻を必要とする
                    pick = (timestamp - base_time).total_seconds()
                    pick = str(pick)

                    prob = str(prob)
                    amp = str(amp)
                    line = ' '.join([pick, prob, amp]) + '\n'
                    
                    # write
                    with open(os.path.join(self.datatmp_dir, outtxt), 'a') as f:
                        f.write(line)

class RealExecutor(object):
    def __init__(self, config):
        self.config = config

        self.meta = []

    def real(self, config, pickConverter):
        self.in_dir = pickConverter.datatmp_dir
        self.rawout_dir = pickConverter.outtmp_dir
        self.outdir = self.config.outdir

        self.file_day = pickConverter.file_day

        datestr = os.path.basename(self.file_day)

        # D yyyy/mm/dd
        l = [datestr[0:4], datestr[4:6], datestr[6:8]]
        day_value = '/'.join(str(x) for x in l)

        # R rx/rh/tdx/tdh/tint[/gap/GCarc0/latref0/lonref0] (degree/km/degree/km/sec[degree/degree/degree/degree])
        l = [self.config.ho, self.config.dep, self.config.dho, self.config.ddep, self.config.tint]
        range_value = '/'.join(str(x) for x in l)

        # V vp0/vs0/[s_vp0/s_vs0/ielev] (km/s|km/s|[km/s|km/s|int])
        l = [6.2, 3.3, 5.5, 2.7, 2]
        vel_value = '/'.join(str(x) for x in l)

        # S np0/ns0/nps0/nppp/std0/dtps/nrt[/rsel/ires] (int/int/int/int/double/double/double/[double/int])
        l = [config.nps[0], config.nps[1], config.nps[2], 1, self.config.std, 0.5, self.config.nrt, self.config.rsel, self.config.ires]
        sup_value = '/'.join(str(x) for x in l)

        # G trx/trh/tdx/tdh (degree/km/degree/km) info of ttime
        l = [self.config.ho_tt, self.config.dep_tt, self.config.dho_tt, self.config.ddep_tt]
        grid_value = '/'.join(str(x) for x in l)

        # REAL
        com = "REAL" \
            + ' -D%s' % day_value \
            + ' -R%s' % range_value \
            + ' -V%s' % vel_value \
            + ' -S%s' % sup_value \
            + ' -G%s' % grid_value \
            + ' %s' % self.config.real_stntbl \
            + ' %s' % self.in_dir \
            + ' %s' % self.config.ttime_tbl \
            + ' %s' % self.rawout_dir
        print("[RealExecutor.real]:", com)

        ## needs REAL ##
        proc = sp.run(com, shell=True, stdout = sp.PIPE, stderr = sp.STDOUT) #be careful for shell injection!!
        out = proc.stdout.decode("utf8")
        print("[RealExecutor.real]: REAL", out)
    
    def convert2json(self, config, mkEachJson=False):
        # read txt
        events_rawfile = os.path.join(self.rawout_dir, "catalog_sel.txt")
        picks_rawfile = os.path.join(self.rawout_dir, "phase_sel.txt")
        
        with open(events_rawfile) as f:
            events_meta = [line.rstrip().lstrip() for line in f.readlines()]

        i = 1; picks_meta = []; picks_onemeta = []
        with open(picks_rawfile) as f:
            for pick_meta in f:
                pick_meta = pick_meta.rstrip().lstrip()
                if pick_meta in events_meta:
                    # if line is event info
                    if len(picks_onemeta) != 0:
                        # if previous event has one or more picks
                        picks_meta.append(picks_onemeta)
                        i += 1
                    picks_onemeta = []
                else:
                    # if line is pick info
                    picks_onemeta.append(pick_meta)
            else:
                # if line is end
                if len(picks_onemeta) != 0:
                    # if last event has one or more picks
                    picks_meta.append(picks_onemeta)                

        # print(len(events_meta), len(picks_meta)); exit()

        # make EventInfo instance
        eventInfoList = [EventInfo(i+1, event, picks, "real") for i, (event, picks) in enumerate(zip(events_meta, picks_meta))]

        # write json
        ## add to meta
        metaone = [eventInfo.toJson() for eventInfo in eventInfoList]
        self.meta.append(metaone)

        ## write output
        if mkEachJson:
            self.writeJson(config.n)

        self.writeJson()

    def picklist(self, n=-1):
        l = []

        if n >= 0:
            metaone = self.meta[n]
            for item in metaone:
                l += item['picksInfo']

        elif n == -1:
            for metaone in self.meta:
                for item in metaone:
                    l += item['picksInfo']

        return l
    
    def eventlist(self, n=-1):
        l = []

        if n >= 0:
            metaone = self.meta[n]
            for item in metaone:
                l.append(item['eventInfo'])

        elif n == -1:
            for metaone in self.meta:
                for item in metaone:
                    l.append(item['eventInfo'])

        return l
    
    def writeJson(self, n=-1):
        # write only one
        if n >= 0:
            outfile = os.path.join(self.outdir, "picks_associated-%s.json" % n)
            outmeta = self.meta[n]

        # write all
        elif n == -1:
            outfile = os.path.join(self.outdir, "picks_associated.json")

            ## 
            outmeta0 = []
            for i in range(len(self.meta)):
                ### add itr index
                outmetaone0 = self.meta[i]
                for item in outmetaone0:
                    item['itr'] = i + 1 # start from 1

                ### sort and concat meta
                outmeta0 += sorted(outmetaone0, key=lambda x: x['index'])

            ## rename index for one iteration
            outmeta = []
            key_mapping = {
                "index": "indexOneItr"
            }
            for item in outmeta0:
                outmeta.append({key_mapping.get(key, key): value for key, value in item.items()})

            ## add index for whole process
            for i, item in enumerate(outmeta):
                item['index'] = i + 1 # start from 1

        ## make output json
        with open(outfile, 'w') as f:
            json.dump(outmeta, f, indent=2)