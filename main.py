

import os
import mne
import json
from mne.preprocessing import ICA

#workaround for -- _tkinter.TclError: invalid command name ".!canvas"
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


with open('config.json') as config_json:
    config = json.load(config_json)

data_file = config['fif']
raw = mne.io.read_raw_fif(data_file, verbose=False)
raw.load_data()

fname = config['ica']
ica=mne.preprocessing.read_ica(fname, verbose=None)

#ica.apply(raw)



# heartbeats
plt.figure(1)
ica.plot_overlay(raw, exclude=[3], picks='mag')
plt.savefig(os.path.join('out_figs','plot_overlay_hb.png'))


# blinks
plt.figure(2)
ica.plot_overlay(raw, exclude=[1], picks='eeg')
plt.savefig(os.path.join('out_figs','plot_overlay_blinks.png'))
