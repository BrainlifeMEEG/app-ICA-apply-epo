

import os
import mne
import json
from mne.preprocessing import ICA

with open('config.json') as config_json:
    config = json.load(config_json)

data_file = config['fif']
raw = mne.io.read_raw_fif(data_file, verbose=False)
raw.load_data()

fname = config['fifi']
ica=mne.preprocessing.read_ica(fname, verbose=None)

ica.apply(raw)