from os.path import dirname, join
from sys import argv
from csv import DictReader


def main(csv_sootsai, boklok_sootsai):
    tsitma = dirname(csv_sootsai)
    tsuan = []
    with open(csv_sootsai, encoding='utf-8') as f:
        for tsua in DictReader(f):
            imtong = join(tsitma, tsua['音檔'])
            lmj = tsua['羅馬字']
            tsuan.append('|'.join([imtong, lmj]))
    with open(
        join(boklok_sootsai, 'suisiann_audio_text_train_filelist.txt'),
        'wt', encoding='utf-8'
    ) as tong:
        print('\n'.join(tsuan[:-600]), file=tong)
    with open(
        join(boklok_sootsai, 'suisiann_audio_text_vat_filelist.txt'),
        'wt', encoding='utf-8'
    ) as tong:
        print('\n'.join(tsuan[-600:-500]), file=tong)
    with open(
        join(boklok_sootsai, 'suisiann_audio_text_test_filelist.txt'),
        'wt', encoding='utf-8'
    ) as tong:
        print('\n'.join(tsuan[-500:]), file=tong)


if __name__ == '__main__':
    main(argv[1], argv[2])
