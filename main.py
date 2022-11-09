

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


reconst_raw = raw.copy()
ica.apply(reconst_raw)

#pick some channels that clearly show heartbeats and blinks
regexp = r'(MEG [12][45][123]1|EEG 00.)'
artifact_picks = mne.pick_channels_regexp(raw.ch_names, regexp=regexp)
plt.figure(3)
raw.plot(order=artifact_picks, n_channels=len(artifact_picks),
        show_scrollbars=False)
plt.savefig(os.path.join('out_figs','s1.png'))
plt.figure(4)
reconst_raw.plot(order=artifact_picks, n_channels=len(artifact_picks),
                 show_scrollbars=False)
plt.savefig(os.path.join('out_figs','s2.png'))

reconst_raw.save(os.path.join('out_dir','meg.fif'))
