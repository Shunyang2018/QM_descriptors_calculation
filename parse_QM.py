import os

import pandas as pd

from joblib import Parallel, delayed

from lib import read_log, _summarize_descriptors

mols_groups = [os.path.join(x, 'DFT') for x in os.listdir('.') if os.path.isdir(x)]

df = []
for mols_group in mols_groups:

def grab_from_mol_group(mols_group):
    neutral_logs = [os.path.join(mols_group, 'neutral', x) for x in
                    os.listdir(os.path.join(mols_group, 'neutral')) if '.log' in x]

    QM_descs = []
    for log_f in neutral_logs:
        QM = read_log(log_f)

        if QM:
            desc_temp = {'neutral': QM}

            if os.path.isfile(os.path.join(mols_group, 'plus1', log_f)) and \
                    os.path.isfile(os.path.join(mols_group, 'minus1', log_f)):

                QM_plus1 = read_log(os.path.join(mols_group, 'plus1', log_f))
                QM_minus1 = read_log(os.path.join(mols_group, 'minus1', log_f))

                if QM_plus1 and QM_minus1:
                    desc_temp['plus1'] = QM_plus1
                    desc_temp['minus1'] = QM_minus1

                    QM_desc = _summarize_descriptors(desc_temp)
                    QM_desc['compound_id'] = log_f.split('_')[0]

                    QM_descs.append(QM_desc)
    QM_descs = pd.DataFrame(QM_descs)
    return QM_descs

QM_descs_all = Parallel(n_jobs=-1, verbose=10)(delayed(grab_from_mol_group)(x) for x in mols_groups)
QM_descs_all = pd.concat(QM_descs_all, ignore_index=True)

QM_descs_all.to_pickle('collected.pickle')
