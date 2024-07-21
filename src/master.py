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
            self.nps = self.master.nps[self.n]
        elif type(self.master.nps[0]) == int:
            self.nps = self.master.nps
        else:
            print("[Error]: --nps is not proper")

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