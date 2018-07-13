"""
notes:
- use pyemu.os_utils.run() for all system calls - it will deal with the "./" and ".exe"
"""

import os
import platform
import shutil
import numpy as np
import pandas as pd
import flopy
import pyemu

# GLOBALS - ALL CAPS! 
EXT = ''
BIN_PATH = os.path.join("..", "bin")  # path to bins from where freyberg.py lives
if "linux" in platform.platform().lower():
    BIN_PATH = os.path.join(BIN_PATH, "linux")
elif "darwin" in platform.platform().lower():
    BIN_PATH = os.path.join(BIN_PATH, "mac")
else:
    BIN_PATH = os.path.join(BIN_PATH, "win")
    EXT = '.exe'

# MF = os.path.join(BIN_PATH,"mfnwt")
# PPP = os.path.join(BIN_PATH, "pestpp")
# IES = os.path.join(BIN_PATH, "pestpp-ies")
MF = "mfnwt"
PPP = "pestpp"
IES = "pestpp-ies"

BINS = [MF, PPP, IES]  # keep this list current
for b in BINS:
    assert os.path.exists(os.path.join(BIN_PATH, b))


def prep_notebook(wd):
    if os.path.exists(wd):
        shutil.rmtree(wd)
    os.mkdir(wd)
    for b in BINS:
        shutil.copy2(os.path.join(BIN_PATH, b), os.path.join(wd, b))



def build_model(model_ws="test"):
    if os.path.exists(model_ws):
        shutil.rmtree(model_ws)
    m = flopy.modflow.Modflow("freyberg",version="mfnwt",exe_name=MF,model_ws=model_ws,external_path='.')

    botm = np.loadtxt(os.path.join("..","_data","botm.ref")).flatten().reshape((40,20))
    print(botm)
    flopy.modflow.ModflowDis(m,nrow=40,ncol=20,nlay=1,nper=3,delr=250,delc=250,top=35.0,botm=[botm],
                             perlen=[1.0,1825.0,1.0],steady=[True,False,True])

    ibound = np.loadtxt(os.path.join("..","_data","ibound.ref"))
    flopy.modflow.ModflowBas(m,ibound=ibound,strt=20.0,hnoflo=-1.0e+10)

    hk = np.loadtxt(os.path.join("..","_data","hk.truth.ref"))
    flopy.modflow.ModflowUpw(m,hk=hk,laytyp=0,ipakcb=50)

    wel_data = pd.read_csv(os.path.join("..","_data","well_data.csv"),skipinitialspace=True)
    wel_data.loc[:,"k"] = wel_data.pop('l') - 1
    wel_data.loc[:,"i"] = wel_data.pop("r") - 1
    wel_data.loc[:,"j"] = wel_data.pop("c") - 1
    wel_data.loc[:,"flux"] = wel_data.pop("flux").astype(np.float32)
    wel_data = wel_data.loc[:,["k","i","j","flux"]].to_records(index=False)
    flopy.modflow.ModflowWel(m,stress_period_data=wel_data,ipakcb=50)

    chd_data = []
    for k in range(m.ncol):
        if ibound[m.nrow-1,k] == 0:
            continue
        chd_data.append([0,m.nrow-1,k,15.0,15.0])
    flopy.modflow.ModflowChd(m,stress_period_data=chd_data,ipakcb=50)

    flopy.modflow.ModflowRch(m,rech=1.0e-4,ipakcb=50)

    reach_data = []
    seg_data = []
    start = 25  # upgradient bottom
    end = 15  # downgradient bottom
    elevup = np.linspace(start, end, m.nrow+1)
    elevdn = elevup[1:]
    elevup = elevup[:-1]
    for i in range(m.nrow):
        reach_data.append([0,i,15,i+1,1,250.0])
        seg_data.append([i+1,1,i+2,elevup[i],elevdn[i],0.1,0.1,0.1,1.0,1.0,10.0,10.0])


    cols = ["nseg","icalc","outseg","elevup","elevdn","hcond1","hcond2","roughch","thickm1","thickm2","width1","width2"]
    reach_data = pd.DataFrame(data=reach_data,columns = ["k","i","j","iseg","ireach","rchlen"]).to_records(index=False)
    seg_data = pd.DataFrame(data=seg_data,columns=cols).to_records(index=False)
    seg_data["outseg"][39] = 0
    #print(seg_data)
    flopy.modflow.ModflowSfr2(m,nstrm=40,reach_data=reach_data,segment_data=seg_data)

    flopy.modflow.ModflowOc(m,stress_period_data={(0,0):["save head","save budget"]})
    flopy.modflow.ModflowNwt(m)
    m.write_input()
    pyemu.os_utils.run("{0} {1}".format(MF,m.namefile),cwd=model_ws)


def test():
    wd = "test"
    prep_notebook(wd)
    for b in BINS:
        assert os.path.exists(os.path.join(wd, b))




if __name__ == "__main__":
    #test()
    build_model()
