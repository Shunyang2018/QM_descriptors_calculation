#!/bin/bash
#SBATCH -J qm_descriptors
#SBATCH -p medium
#SBATCH --time=20:00:00
#SBATCH --ntasks=40
#SBATCH --mem-per-cpu=2G
#SBATCH -N 1

source activate QM_descriptors

PATH=/home/ranasd01/.conda/envs/QM_descriptors/bin/python:$PATH:/home/ranasd01/Software/nbo6/bin
PYTHONPATH=/home/ranasd01/.conda/envs/QM_descriptors/lib/python3.7/site-packages/:$PYTHONPATH

g16root=/gpfs/apps/medsci/stacks/noOS/software/gaussian/g16.c01.avx2
GAUSS_SCRDIR=/gpfs/scratch/jobs/ranasd01/QM_dis
mkdir $GAUSS_SCRDIR
export g16root GAUSS_SCRDIR
. $g16root/g16/bsd/g16.profile

python main.py
