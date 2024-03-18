# REALAssociator
Detailed usage for REALAssociator

## What is the output?
* association result file: `data/associated_picks.json`

  | Key | Description |
  | --- | --- |
  | `index` | event index within a single json file |
  | `eventInfo` | the event information from "Event line" in the "phase_sel.txt" (raw REAL output) |
  | `picksInfo[]` | list of the pick information from "Phase line" in the "phase_sel.txt" |

* See [here](../org/REAL_userguide_July2021.pdf) for the detailed information about "phase_sel.txt".

## How to use
### 1. Input file preparation
* output file of PhaseNet (picks.json)
  * format: json format <br>
    For the detailed information, see https://github.com/AI4EPS/PhaseNet
  * You can pick phase from WIN waveform files with [WIN2PhaseNet](https://github.com/rintr-suzuki/WIN2PhaseNet) and PhaseNet.
  * **Only the 1st day of data within the file is processed.** Please divide the data into daily data. <br>
    D option of original REAL configration is automatically set to the 1st day.
  * Make directry named `REALAssociator/data` and put the files there. <br>
    You can change the path with `--infile` option.

* channel table: correspondence Table of stations and their code
  * format: txt format <br>
    For the detailed information, see https://wwweic.eri.u-tokyo.ac.jp/WIN/man.ja/win.html (only in Japanese).
  * **Only support <=1,500 stations**
  * **Only support the following "component code (column [5])"**. <br>
    -Vertical compornent: EW,E,X,VX <br>
    -Horizontal compornent 1: NS,N,Y,VY <br>
    -Horizontal compornent 2: UD,U,Z,VZ
  * NIED provides channel table at the same time when downloading WIN waveform files. <br>
    For the detailed information, see https://hinetwww11.bosai.go.jp/auth/download/cont/?LANG=en
  * Put the file as `REALAssociator/etc/stn.tbl`. <br>
    You can change the path with `--chtbl` option.

* travel time table
  * format: txt format <br>
    For the detailed information, see "traveltime table" in [here](../org/REAL_userguide_July2021.pdf).
  * You can use `REALAssociator/etc/ttdb.txt` created from the velocity structure by Hasegawa et al. (1978) as a default.
  * G option of original REAL configration is automatically calculated to use the entire file from travel time table.
  * You can change the path with `--ttime` option.

### 2. Configuration of REALAssociator
* Set the following options at least.

  | Option | Description |
  | --- | --- |
  | `[--dep DEP]` | - search range in depth (unit: km, default: `250`) <br> - same as "rh" of original REAL configration |
  | `[--ho HO]` | - search range in horizontal (unit: degree, default: `0.7`) <br> - same as "rx" |
  | `[--ddep DDEP]` | - search grid size for depth (unit: km, default: `10`) <br> - same as "tdh" | 
  | `[--dho DHO]` | - search grid size for horizontal (unit: degree, default: `0.1`) <br> - same as "tdx" |

* Other settings of original REAL configration are as follows:
  * R option
    * tint: 5
    * gap: 360
    * GCarc0: 180
    * latref0: Null
    * lonref0: Null
  * V option
    * vp0: 6.2
    * vs0: 3.3
    * s_vp0: 5.5
    * s_vs0: 2.7
    * ielev: 0
  * S option
    * np0: 4
    * ns0: 0
    * nps0: 6
    * npsboth0: Not support
    * std0: 1.73
    * dtps: 0.5
    * nrt: 1.3
    * drt: Not support
    * nxd: Not support
    * rsel: 5.0

* See [here](../org/REAL_userguide_July2021.pdf) for the detailed information about the original REAL configration.

* Use `-h` option for the detailed information of all other options.

### 3. Execute REALAssociator
```
# Pull docker image (only once), run the 'real' container and then execute REALAssociator on the container environment. *1
# Stop and delete the container environment after execution is complete.
$ ./REALAssociator.bash --infile INFILE [--dep DEP] [--ho HO] [--ddep DDEP] [--dho DHO]
# e.g. 
# $ ./REALAssociator.bash --infile data/picks.json

# You can find the output of REALAssociator in '<dirname of infile>' directory.
```

## Notes
* *1 docker image is built from the following Dockerfile.
    * dockerfiles/Dockerfile