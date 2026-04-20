"""
Apply ICA components to epoched MEG/EEG data.

This app reads an ICA object, excludes identified bad components (automatically
detected for EOG/ECG artifacts or manually specified), and reconstructs the epoched
data before saving it.

Inputs:
    - epo: Path to MNE epochs .fif file
    - ica: Path to ICA decomposition file
    - exclude: Optional comma-separated list of component indices to exclude
    - reject_EOG: Boolean to automatically detect and exclude EOG artifacts
    - reject_ECG: Boolean to automatically detect and exclude ECG artifacts
    - EOG_chan: Optional EOG channel name or index
    - ECG_chan: Optional ECG channel name or index

Outputs:
    - out_dir/meg-epo.fif: Epoched data with ICA components applied
    - out_figs/plot_overlay.png: Visualization of ICA overlay before application
    - out_report/report_ica.html: QC report with ICA information
    - product.json: Metadata about applied ICA
"""

# Copyright (c) 2026 brainlife.io
#
# This app applies ICA decomposition to MNE epoched data
#
# Authors:
# - Maximilien Chaumon (https://github.com/dnacombo)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'brainlife_utils'))

# Standard imports
import re
import mne
import matplotlib.pyplot as plt

# Import shared utilities
from brainlife_utils import (
    load_config,
    setup_matplotlib_backend,
    ensure_output_dirs,
    create_product_json,
    add_info_to_product,
    add_image_to_product,
    save_figure_with_base64
)

# Set up matplotlib for headless execution
setup_matplotlib_backend()

# Ensure output directories exist
ensure_output_dirs('out_dir', 'out_figs', 'out_report')

# Load configuration
config = load_config()

# == PARSE EXCLUDE COMPONENTS ==
# Turn config['exclude'] into a list of integers, parsing the separated string to a list
exclude_components = []
if config.get('exclude') and config['exclude'] != 'None':
    exclude_components = [int(x) for x in re.split("\\W+", config['exclude'])]

# == LOAD DATA ==
data_file = config['epo']
epo = mne.read_epochs(data_file, preload=True)

# Load ICA object
fname = config['ica']
ica = mne.preprocessing.read_ica(fname)

# Set initial exclude list
ica.exclude = exclude_components.copy()

# == PARSE EOG/ECG CHANNELS ==
eog_ch = None
if config.get('EOG_chan') and config['EOG_chan'] != 'None':
    eog_ch = config['EOG_chan']
    try:
        # Try to convert to int if it's a number
        eog_ch = int(eog_ch)
    except (ValueError, TypeError):
        # Keep as string (channel name)
        pass

ecg_ch = None
if config.get('ECG_chan') and config['ECG_chan'] != 'None':
    ecg_ch = config['ECG_chan']
    try:
        # Try to convert to int if it's a number
        ecg_ch = int(ecg_ch)
    except (ValueError, TypeError):
        # Keep as string (channel name)
        pass

# == DETECT BAD COMPONENTS ==
product_items = []
if config.get('reject_EOG', False):
    try:
        eog_epochs = mne.preprocessing.create_eog_epochs(epo, ch_name=eog_ch)
        eog_idx, eog_scores = ica.find_bads_eog(epo, ch_name=eog_ch, threshold=3.0,
                                                start=None, stop=None, l_freq=1, h_freq=10, reject_by_annotation=False,  # Epochs don't support this
                                                measure='zscore', verbose=None)
        if eog_idx:
            exclude_components = list(set(exclude_components + eog_idx))
            ica.exclude.extend(eog_idx)
            add_info_to_product(product_items, f'Excluded {len(eog_idx)} EOG artifact components', 'success')
    except Exception as e:
        add_info_to_product(product_items, f'Could not detect EOG artifacts: {str(e)}', 'warning')

if config.get('reject_ECG', False):
    try:
        ecg_epochs = mne.preprocessing.create_ecg_epochs(epo, ch_name=ecg_ch)
        ecg_idx, ecg_scores = ica.find_bads_ecg(epo, ch_name=ecg_ch, threshold='auto',
                                                start=None, stop=None, l_freq=8, h_freq=16,
                                                method='ctps',reject_by_annotation=False,  # Epochs don't support this
                                                measure='zscore', verbose=None)
        if ecg_idx:
            exclude_components = list(set(exclude_components + ecg_idx))
            ica.exclude.extend(ecg_idx)
            add_info_to_product(product_items, f'Excluded {len(ecg_idx)} ECG artifact components', 'success')
    except Exception as e:
        add_info_to_product(product_items, f'Could not detect ECG artifacts: {str(e)}', 'warning')

# Update to unique exclude list
ica.exclude = list(set(ica.exclude))

# == CREATE OVERLAY VISUALIZATION ==
overlay_fig = ica.plot_overlay(epo.average(), show=False)
overlay_fig_path = os.path.join('out_figs', 'plot_overlay.png')
overlay_base64 = save_figure_with_base64(
    overlay_fig,
    overlay_fig_path,
    dpi_file=150,
    dpi_base64=80,
)
plt.close(overlay_fig)

# == CREATE REPORT ==
report = mne.Report(title='ICA Application Report (Epochs)')
report.add_ica(ica, 'ICA Components', inst=epo,
               ecg_evoked=ecg_epochs.average() if 'ecg_epochs' in locals() else None, 
               ecg_scores=ecg_scores if 'ecg_scores' in locals() else None,
               eog_evoked=eog_epochs.average() if 'eog_epochs' in locals() else None,
               eog_scores=eog_scores if 'eog_scores' in locals() else None,
               n_jobs=10)

# Add overlay information
report_text = f'<p><b>Total Components:</b> {ica.n_components}</p>'
report_text += f'<p><b>Excluded Components:</b> {len(ica.exclude)}</p>'
if ica.exclude:
    report_text += f'<p><b>Excluded Indices:</b> {sorted(ica.exclude)}</p>'

report.save(os.path.join('out_report', 'report_ica.html'), overwrite=True)

# == APPLY ICA ==
ica.apply(epo)
print(f'Applied ICA to {len(epo)} epochs')

# == SAVE PROCESSED EPOCHS ==
epo.save(os.path.join('out_dir', 'meg-epo.fif'), overwrite=True)
print('Epochs saved to out_dir/meg-epo.fif')

# == CREATE PRODUCT.JSON ==
add_image_to_product(product_items, 'ICA Overlay', base64_data=overlay_base64)
add_info_to_product(product_items, f'Applied ICA to {len(epo)} epochs with {len(ica.exclude)} excluded components', 'success')
create_product_json(product_items)

