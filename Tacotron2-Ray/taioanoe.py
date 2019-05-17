import argparse
import os
from multiprocessing import cpu_count

from datasets import preprocessor
from hparams import hparams
from tqdm import tqdm
from os.path import isdir


def norm_data(args):

    merge_books = (args.merge_books == 'True')

    print('Selecting data folders..')
    supported_datasets = ['LJSpeech-1.0', 'LJSpeech-1.1', 'M-AILABS']
    if args.dataset not in supported_datasets:
        raise ValueError('dataset value entered {} does not belong to supported datasets: {}'.format(
            args.dataset, supported_datasets))

    if args.dataset.startswith('LJSpeech'):
        return [os.path.join(args.base_dir, args.dataset)]

    if args.dataset == 'M-AILABS':
        supported_languages = ['en_US', 'en_UK', 'fr_FR', 'it_IT', 'de_DE', 'es_ES', 'ru_RU',
                               'uk_UK', 'pl_PL', 'nl_NL', 'pt_PT', 'fi_FI', 'se_SE', 'tr_TR', 'ar_SA']
        if args.language not in supported_languages:
            raise ValueError('Please enter a supported language to use from M-AILABS dataset! \n{}'.format(
                supported_languages))

        supported_voices = ['female', 'male', 'mix']
        if args.voice not in supported_voices:
            raise ValueError('Please enter a supported voice option to use from M-AILABS dataset! \n{}'.format(
                supported_voices))

        path = os.path.join(args.base_dir, args.language,
                            'by_book', args.voice)
        supported_readers = [e for e in os.listdir(
            path) if os.path.isdir(os.path.join(path, e))]
        if args.reader not in supported_readers:
            raise ValueError('Please enter a valid reader for your language and voice settings! \n{}'.format(
                supported_readers))

        path = os.path.join(path, args.reader)
        supported_books = [e for e in os.listdir(
            path) if os.path.isdir(os.path.join(path, e))]
        if merge_books:
            return [os.path.join(path, book) for book in supported_books]

        else:
            if args.book not in supported_books:
                raise ValueError('Please enter a valid book for your reader settings! \n{}'.format(
                    supported_books))

            return [os.path.join(path, args.book)]


def run_preprocess(args, hparams):
    input_folders = [os.path.join(args.base_dir, args.dataset)]
    if not isdir(input_folders[0]):
        raise ValueError('Dataset  {} 有問題'.format(args.dataset))

    output_folder = os.path.join(args.base_dir, args.output)

    preprocess(args, input_folders, output_folder, hparams)


def main():
    print('initializing preprocessing..')
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default='')
    parser.add_argument('--hparams', default='',
                        help='Hyperparameter overrides as a comma-separated list of name=value pairs')
    parser.add_argument('--dataset', default='Taioanoe')
    parser.add_argument('--language', default='tg_TW')
    parser.add_argument('--output', default='training_data')
    parser.add_argument('--n_jobs', type=int, default=cpu_count())
    args = parser.parse_args()

    modified_hp = hparams.parse(args.hparams)

    run_preprocess(args, modified_hp)


if __name__ == '__main__':
    main()
