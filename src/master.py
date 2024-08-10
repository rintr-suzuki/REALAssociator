import os
import glob
import pandas as pd

from model_stn import StationTable

class MasterConfig(object):
    def __init__(self, args):
        ## set args
        for key, value in args.items():
            setattr(self, key, value)

        ## set tmpdir and outdir
        self.tmpdir = ".tmp"
        os.makedirs(self.tmpdir, exist_ok=True)

        self.outdir = os.path.dirname(self.infile)

        ## set locating program
        self.associator = "REAL"
            
        ## set stntbl
        if self.associator == "REAL":
            ## set chlst
            stntbl = StationTable(self.chtbl, None)
            stntbl.screeningTbl(self.tmpdir)

            ## make station table for REAL
            stntbl.tbl2realtbl(self.tmpdir)
            self.real_stntbl = stntbl.stnrealtbl

            ## set velocity structure table
            self.ttime_tbl = "etc/ttdb.txt" 

            ## set grid value 
            df = pd.read_csv(self.ttime_tbl, header=None, delimiter=' ')
            self.ho_tt = max(df[0])
            self.dep_tt = max(df[1])
            self.dho_tt = self.ho_tt / len(set(df[0].values))
            self.ddep_tt = self.dep_tt / (len(set(df[1].values))-1)

class Config(object):
    def __init__(self, masterConfig, n):
        self.master = masterConfig
        self.n = n

        # if set several th
        if type(self.master.nps[0]) == list:
            if len(self.master.nps) == self.master.itr_real:
                self.nps = self.master.nps[self.n]
            else:
                print("[Error]: --nps format is not proper. \
                      For example, 2 sets of thresholds are required for a 2 iteration process, like '30-10-40,0-2-5'. \
                      Alternatively, common set of thresholds can be set like '30-10-40'.")
        elif type(self.master.nps[0]) == int:
            if len(self.master.nps) == 3:
                self.nps = self.master.nps
            else:
                print("[Error]: --nps format is not proper. Required 3 values, like '30-10-40', but given %s. \
                      Alternatively, individual sets of thresholds can be set like '30-10-40,0-2-5'." % len(self.master.nps))
        else:
            print("[Error]: --nps format is not proper. Must be like '30-10-40,0-2-5' or '30-10-40'.")

class MasterProcess(object):
    def __init__(self, config):
        self.config = config

    def rm_tmp(self):
        ext = ["lst", "tbl", "txt", "dat"]

        l = []
        for s in ext:
            l += glob.glob(self.config.tmpdir + "/**/*.%s" % s, recursive=True)
        for file in l:
            os.remove(file)
            # print(file)