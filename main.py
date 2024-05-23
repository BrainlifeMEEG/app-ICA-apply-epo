# this app is used to read in an ICA object, exclude identified components
# and reconstruct the epo data before saving it.

import os
import mne
import json
import helper
from mne.preprocessing import ICA
import re

#workaround for -- _tkinter.TclError: invalid command name ".!canvas"
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


with open('config.json') as config_json:
    config = helper.convert_parameters_to_None(json.load(config_json))

# if config['exclude'] is not empty
if config['exclude']:
    # turn config['exclude'] into a list of integers, parsing the separated string to a list
    config['exclude'] = [int(x) for x in re.split("\\W+",config['exclude'])]

data_file = config['epo']
epo = mne.read_epochs(data_file, preload=True)

fname = config['ica']
ica = mne.preprocessing.read_ica(fname)
ica.exclude = config['exclude']


report = mne.Report(title='ICA')
report.add_ica(ica, 'ICA', inst = epo)
report.save('out_report/report_ica.html', overwrite=True)

ica.apply(epo)
epo.save(os.path.join('out_dir','meg.fif'),overwrite=True)

