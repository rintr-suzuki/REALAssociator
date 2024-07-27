# -*- coding: utf-8 -*-
import argparse

from master import MasterConfig, Config, MasterProcess
from service import PickConverter, RealExecutor

def tp1(arg):
    parts = arg.split(',')
    result = []
    for part in parts:
        values = list(map(int, part.split('-')))
        result.append(values)

    if len(result) <= 1:
        result = result[0]
    return result

def read_args():
    #tp1 = lambda x:list(map(str, x.split(','))map(str, x.split('/')))
    parser = argparse.ArgumentParser()

    parser.add_argument('--infile', help='path of input phase file created by PhaseNet (picks.json)')

    # channel table of station code
    parser.add_argument('--chtbl', default='etc/stn.tbl', help='path of channel table file (default: etc/stn.tbl)')

    #
    parser.add_argument('--ttime', default='etc/ttdb.txt', help='default travel time table for REAL (default: etc/ttdb.txt)')
    # parser.add_argument('--velfile', default='etc/itvel.nd', help='velocity file(1-D)') # need for make tt
    # parser.add_argument('--make_tt', action='store_true', help='in case you want to make new tt to renew grid size and so on')
    # parser.add_argument('--corfile', default='etc/PS-P_coef_final.dat', help='sedimentary correction file')
    # parser.add_argument('--weigfile', default='etc/weight.txt', help='weighting for relocation according to prob')

    # params for REAL
    parser.add_argument('--dep', type=int, default=250, help='depth[km]') # Zhang et al.(2019): 20
    parser.add_argument('--ho', type=float, default=0.7, help='horizontal length[deg]') # Zhang et al.(2019): 0.5
    parser.add_argument('--ddep', type=int, default=10, help='grid of depth[km]') # Zhang et al.(2019): 2
    parser.add_argument('--dho', type=float, default=0.1, help='grid of horizontal length[deg]') # Zhang et al.(2019): 0.02

    # parser.add_argument('--ielev', type=int, default=2, \
    #     help='station elevation & sedimentary correction 0: no correction, 1: elevation correction only, 2: sedimentary correction only')
    parser.add_argument('--nps', type=tp1, default=[[30, 10, 40], [0, 2, 5]], help='Threshold for number of P,S,P+S on association connected by hyphens. \
                        It can be set for each iteration by separating them with commas. (default: 30-10-40,0-2-5)')
    parser.add_argument('--std', type=float, default=1.73, help='standard deviation threshold within 1 event')
    parser.add_argument('--nrt', type=float, default=1.3, help='nrt*default time window(travel time for 1 grid)')
    parser.add_argument('--ires', type=int, default=1, help='resolution_or_not')
    parser.add_argument('--tint', type=int, default=5, help='two events cannot appear within tint sec')
    parser.add_argument('--rsel', type=float, default=5.0, help='remove picks with large residuals less than rsel*STD')

    # step of REAL
    parser.add_argument('--itr_real', type=int, default=2, help='Number of REAL process iterations. After 2nd association, remaining picks are used, excluding the picks associated before the (n-1)th association. (default: 2)')

    args = parser.parse_args()
    return args

def main(params):
    # initial settings
    ## master setting
    masterConfig = MasterConfig(params)
    masterProcess = MasterProcess(masterConfig)

    # init
    # masterConfig.itr_real = 1 # todo
    pickConverter = PickConverter(masterConfig)
    realExecutor = RealExecutor(masterConfig)

    for n in range(masterConfig.itr_real):
        config = Config(masterConfig, n)

        # json->txt
        pickConverter.convertFromJson(config, realExecutor)

        # txt->REAL->txt
        realExecutor.real(config, pickConverter)

        # txt->json
        realExecutor.convert2json(config)

    # remove tmp file
    masterProcess.rm_tmp()

if __name__ == '__main__':
   params = vars(read_args()) # convert to dict
   main(params)