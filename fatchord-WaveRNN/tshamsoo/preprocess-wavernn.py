import argparse
from csv import DictReader
import glob
from multiprocessing import Pool, cpu_count
from os.path import splitext, basename
from pathlib import Path
import pickle
from typing import Union

from utils import hparams as hp
from utils.display import *
from utils.dsp import *
from utils.files import get_files
from utils.paths import Paths


parser = argparse.ArgumentParser(
    description='Preprocessing for WaveRNN and Tacotron')
parser.add_argument(
    '--path', '-p',
    help='directly point to dataset path (overrides hparams.wav_path'
)
parser.add_argument(
    '--extension', '-e', metavar='EXT', default='.npy',
    help='file extension to search for in dataset folder'
)
parser.add_argument(
    '--hp_file', metavar='FILE', default='hparams.py',
    help='The file to use for the hyperparameters'
)
args = parser.parse_args()

hp.configure(args.hp_file)  # Load hparams from file
if args.path is None:
    args.path = hp.wav_path

extension = args.extension
path = args.path


wav_files = get_files(path, extension)
paths = Paths(hp.data_path, hp.voc_model_id, hp.tts_model_id)

print(f'\n{len(wav_files)} {extension[1:]} files found in "{path}"\n')

if len(wav_files) == 0:

    print('Please point wav_path in hparams.py to your dataset,')
    print('or use the --path option.\n')

else:

    if not hp.ignore_tts:
        u_tihleh = set()
        for sootsai in wav_files:
            u_tihleh.add(splitext(basename(sootsai))[0])

        dataset_wavernn = []
        with open(paths.data / 'dataset.pkl', 'rb') as f:
            for item_id, length in pickle.load(f):
                if item_id in u_tihleh:
                    dataset_wavernn.append((item_id, length))

        with open(paths.data / 'dataset_wavernn.pkl', 'wb') as f:
            pickle.dump(dataset_wavernn, f)
