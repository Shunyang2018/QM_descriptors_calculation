import os
import sys

import pandas as pd

from lib import read_log, _summarize_descriptors
from tqdm import tqdm


def grab_from_mol_group(mols_group):
    logs = [x for x in os.listdir(os.path.join(mols_group, 'neutral')) if '.log' in x]

    QM_descs = []
    for log_f in tqdm(logs):
        try:
            QM = read_log(os.path.join(mols_group, 'neutral', log_f))
        except:
            continue

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


mols_group = sys.argv[1]
QM_descs = grab_from_mol_group(mols_group)

QM_descs.to_pickle('collected.pickle')

