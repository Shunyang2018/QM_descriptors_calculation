from rdkit import Chem
import os
import subprocess
from .file_parser import mol2xyz, xyz2com
from .grab_QM_descriptors import read_log


def _summarize_descriptors(QM_descriptors):
    QM_descriptor_return = QM_descriptors['neutral']

    # charges and fukui indices
    for charge in ['mulliken_charge', 'hirshfeld_charges', 'NPA_Charge']:
        QM_descriptor_return['{}_plus1'.format(charge)] = QM_descriptors['plus1'][charge]
        QM_descriptor_return['{}_minus1'.format(charge)] = QM_descriptors['minus1'][charge]

        QM_descriptor_return['{}_fukui_elec'.format(charge)] = QM_descriptors['neutral'][charge] - \
                                                               QM_descriptors['minus1'][charge]
        QM_descriptor_return['{}_fukui_neu'.format(charge)] = QM_descriptors['plus1'][charge] - \
                                                              QM_descriptors['neutral'][charge]

    # spin density
    for spin in ['mulliken_spin_density', 'hirshfeld_spin_density']:
        QM_descriptor_return['{}_plus1'.format(spin)] = QM_descriptors['plus1'][spin]
        QM_descriptor_return['{}_minus1'.format(charge)] = QM_descriptors['minus1'][spin]

    # SCF
    QM_descriptor_return['SCF_plus1'] = QM_descriptors['plus1']['SCF']
    QM_descriptor_return['SCF_minus1'] = QM_descriptors['minus1']['SCF']

    return QM_descriptor_return


def dft_scf(folder, sdf, g16_path, level_of_theory, n_procs, logger, timeout=600):
    basename = os.path.basename(sdf)
    file_name = os.path.splitext(basename)[0]

    if os.path.isfile(os.path.join(folder, 'neutral', file_name + '.log')) and \
            os.path.isfile(os.path.join(folder, 'minus1', file_name + '.log')) and \
            os.path.isfile(os.path.join(folder, 'plus1', file_name + '.log')):
        QM_descriptors = {}
        for jobtype in ['neutral', 'plus1', 'minus1']:
            QM_descriptors[jobtype] = read_log(os.path.join(folder, jobtype, file_name + '.log'))

        try:
            QM_descriptor_return = _summarize_descriptors(QM_descriptors)
        except:
            pass
        else:
            os.remove(os.path.join(folder, file_name + '.sdf'))
            return QM_descriptor_return

    parent_folder = os.getcwd()
    os.chdir(folder)

    QM_descriptor_return = None
    try:

        xyz = mol2xyz(Chem.SDMolSupplier(sdf, removeHs=False, sanitize=False)[0])

        pwd = os.getcwd()

        g16_command = os.path.join(g16_path, 'g16')
        QM_descriptors = {}
        for jobtype in ['neutral', 'plus1', 'minus1']:
            if not os.path.isdir(jobtype):
                os.mkdir(jobtype)

            if jobtype == 'neutral':
                charge = 0
                mult = 1
                head = '%nprocshared={}\n%mem=64GB\n# b3lyp/def2svp nmr=GIAO scf=(maxcycle=512, xqc) ' \
                       'pop=(full,mbs,hirshfeld,nbo6read)\n'.format(n_procs)
            elif jobtype == 'plus1':
                charge = 1
                mult = 2
                head = '%nprocshared={}\n%mem=64GB\n# b3lyp/def2svp scf=(maxcycle=512, xqc) ' \
                       'pop=(full,mbs,hirshfeld,nbo6read)\n'.format(n_procs)
            elif jobtype == 'minus1':
                charge = -1
                mult = 2
                head = '%nprocshared={}\n%mem=64GB\n# b3lyp/def2svp scf=(maxcycle=512, xqc) ' \
                       'pop=(full,mbs,hirshfeld,nbo6read)\n'.format(n_procs)

            os.chdir(jobtype)
            comfile = file_name + '.gjf'
            xyz2com(xyz, head=head, comfile=comfile, charge=charge, mult=mult, footer='$NBO BNDIDX $END\n')

            logfile = file_name + '.log'
            outfile = file_name + '.out'
            with open(outfile, 'w') as out:
                subprocess.run('{} < {} >> {}'.format(g16_command, comfile, logfile), shell=True, stdout=out,
                               stderr=out, timeout=timeout)
                QM_descriptors[jobtype] = read_log(logfile)

            if os.path.isfile('{}.chk'.format(file_name)):
                os.remove('{}.chk'.format(file_name))

            os.chdir(pwd)

        # charges and fukui indices
        QM_descriptor_return = _summarize_descriptors(QM_descriptors)

        os.remove(sdf)
    except:
        pass

    os.chdir(parent_folder)

    return QM_descriptor_return
