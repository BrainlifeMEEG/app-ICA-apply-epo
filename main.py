# this app is used to read in an ICA object, exclude identified components
# and reconstruct the raw data before saving it.

import os
import mne
import json
import helper
from mne.preprocessing import ICA

#workaround for -- _tkinter.TclError: invalid command name ".!canvas"
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


with open('config.json') as config_json:
    config = helper.convert_parameters_to_None(json.load(config_json))

data_file = config['mne']
raw = mne.io.read_raw_fif(data_file, preload=True)

fname = config['ica']
ica = mne.preprocessing.read_ica(fname)
ica.exclude = config['exclude']

plt.figure(1)
ica.plot_overlay(raw)
plt.savefig(os.path.join('out_figs','plot_overlay.png'))


report = mne.Report(title='ICA')
report.add_ica(ica, 'ICA', inst = raw)
report.save('out_report/report_ica.html', overwrite=True)

ica.apply(raw)
raw.save(os.path.join('out_dir','meg.fif'),overwrite=True)


# # heartbeats
# plt.figure(1)
# ica.plot_overlay(raw, exclude=[3], picks='mag')
# plt.savefig(os.path.join('out_figs','plot_overlay_hb.png'))


# # blinks
# plt.figure(2)
# ica.plot_overlay(raw, exclude=[1], picks='eeg')
# plt.savefig(os.path.join('out_figs','plot_overlay_blinks.png'))


# reconst_raw = raw.copy()
# ica.apply(reconst_raw)

# ica.exclude = [0, 3]
# indices= ica.exclude

# # build product.json dictionary for brainlife message
# product = {}
# product['brainlife'] = []
# product['brainlife'].append({'type': 'info', "msg": "here are the excluded nodes: "+', '.join([ str(f) for f in indices ])})

# # save product.json
# with open('product1.json','w') as prod_f:
#     json.dump(product,prod_f)

#pick some channels that clearly show heartbeats and blinks
#regexp = r'(MEG [12][45][123]1|EEG 00.)'
#artifact_picks = mne.pick_channels_regexp(raw.ch_names, regexp=regexp)
#plt.figure(3)
#raw.plot(order=artifact_picks, n_channels=len(artifact_picks),
#        show_scrollbars=False)
#plt.savefig(os.path.join('out_figs','s1.png'))
#plt.figure(4)
#reconst_raw.plot(order=artifact_picks, n_channels=len(artifact_picks),
#                 show_scrollbars=False)
#plt.savefig(os.path.join('out_figs','s2.png'))

