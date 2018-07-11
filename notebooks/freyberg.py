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
BIN_PATH = os.path.join("..","bin") #path to bins from where freyberg.py lives
if "linux" in platform.platform().lower():
    BIN_PATH = os.path.join(BIN_PATH,"linux")
elif "darwin" in platform.platform().lower():
    BIN_PATH = os.path.join(BIN_PATH,"mac")
else:
    BIN_PATH = os.path.join(BIN_PATH,"win")
    EXT = '.exe'
    
# MF = os.path.join(BIN_PATH,"mfnwt")
# PPP = os.path.join(BIN_PATH, "pestpp")
# IES = os.path.join(BIN_PATH, "pestpp-ies")
MF = "mfnwt"
PPP = "pestpp"
IES = "pestpp-ies"

BINS = [MF,PPP,IES] #keep this list current
for b in BINS:
	assert os.path.exists(os.path.join(BIN_PATH,b))

def prep_notebook(wd):
	if os.path.exists(wd):
		shutil.rmtree(wd)
	os.mkdir(wd)
	for b in BINS:
		shutil.copy2(os.path.join(BIN_PATH,b),os.path.join(wd,b))

def test():
	wd = "test"
	prep_notebook(wd)
	for b in BINS:
		assert os.path.exists(os.path.join(wd,b))

if __name__ == "__main__":
	test()
