import torch
from models.fatchord_version import WaveRNN
from utils import hparams as hp
from utils.text.symbols import symbols
from utils.paths import Paths
from models.tacotron import Tacotron
import argparse
from utils.text import text_to_sequence
from utils.display import save_attention, simple_table
from utils.dsp import reconstruct_waveform, save_wav
import numpy as np
import os


from flask import Flask, request, Response, jsonify
from os.path import join
from urllib.parse import quote

from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.語音合成 import 台灣話口語講法
import hashlib
from os.path import isfile
from librosa.core.audio import get_duration
import subprocess
from urllib.parse import urlencode
import sentry_sdk
from sys import stderr


def thak():
    class Tshamsoo():
        device = os.getenv('DEVICE', 'gpu')
        hp_file = 'hparams.py'
        vocoder = os.getenv('VOCODER', 'wavernn')
        batched = os.getenv('BATCHED', 'batched') == 'batched'
        target = os.getenv('TARGET', None)
        overlap = os.getenv('OVERLAP', None)
        tts_weights = None
        save_attn = os.getenv('SAVE_ATTN', False)
        voc_weights = None
        iters = os.getenv('GL_ITERS', 32)

    args = Tshamsoo()
    if args.vocoder in ['griffinlim', 'gl']:
        args.vocoder = 'griffinlim'
    elif args.vocoder in ['wavernn', 'wr']:
        args.vocoder = 'wavernn'
    else:
        raise argparse.ArgumentError('Must provide a valid vocoder type!')

    hp.configure(args.hp_file)  # Load hparams from file

    tts_weights = args.tts_weights
    save_attn = args.save_attn

    paths = Paths(hp.data_path, hp.voc_model_id, hp.tts_model_id)

    if args.device == 'gpu' and torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')
    print('Using device:', device, file=stderr)

    if args.vocoder == 'wavernn':
        # set defaults for any arguments that depend on hparams
        if args.target is None:
            args.target = hp.voc_target
        if args.overlap is None:
            args.overlap = hp.voc_overlap
        if args.batched is None:
            args.batched = hp.voc_gen_batched

        batched = args.batched
        target = int(args.target)
        overlap = int(args.overlap)

        print('\nInitialising WaveRNN Model...\n', file=stderr)
        # Instantiate WaveRNN Model
        voc_model = WaveRNN(rnn_dims=hp.voc_rnn_dims,
                            fc_dims=hp.voc_fc_dims,
                            bits=hp.bits,
                            pad=hp.voc_pad,
                            upsample_factors=hp.voc_upsample_factors,
                            feat_dims=hp.num_mels,
                            compute_dims=hp.voc_compute_dims,
                            res_out_dims=hp.voc_res_out_dims,
                            res_blocks=hp.voc_res_blocks,
                            hop_length=hp.hop_length,
                            sample_rate=hp.sample_rate,
                            mode=hp.voc_mode).to(device)

        voc_load_path = args.voc_weights if args.voc_weights else paths.voc_latest_weights
        voc_model.load(voc_load_path)
    else:
        voc_model = None
        batched = None
        target = None
        overlap = None

    print('\nInitialising Tacotron Model...\n', file=stderr)

    # Instantiate Tacotron Model
    tts_model = Tacotron(embed_dims=hp.tts_embed_dims,
                         num_chars=len(symbols),
                         encoder_dims=hp.tts_encoder_dims,
                         decoder_dims=hp.tts_decoder_dims,
                         n_mels=hp.num_mels,
                         fft_bins=hp.num_mels,
                         postnet_dims=hp.tts_postnet_dims,
                         encoder_K=hp.tts_encoder_K,
                         lstm_dims=hp.tts_lstm_dims,
                         postnet_K=hp.tts_postnet_K,
                         num_highways=hp.tts_num_highways,
                         dropout=hp.tts_dropout,
                         stop_threshold=hp.tts_stop_threshold).to(device)

    tts_load_path = tts_weights if tts_weights else paths.tts_latest_weights
    tts_model.load(tts_load_path)
    return args, voc_model, tts_model, batched, target, overlap, save_attn


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    enable_tracing=True,

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0.1,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=False,
)
app = Flask(__name__)
args, voc_model, tts_model, batched, target, overlap, save_attn = thak()


@app.route("/", methods=['POST', 'GET'])
@app.route("/taiuanue.mp3", methods=['POST', 'GET'])
@app.route("/bangtsam", methods=['POST', 'GET'])
def bangtsam_tts():
    if request.method == 'POST':
        _tongan_ti_hethong_toh, bangtsi = hapsing(request.form)
    else:
        _tongan_ti_hethong_toh, bangtsi = hapsing(request.args)

    huein = Response()
    huein.headers["Content-Type"] = "application/octet-stream"
    huein.headers["Content-Disposition"] = "attachment; filename=taiuanue.mp3"
    huein.headers['X-Accel-Redirect'] = bangtsi
    return huein


@app.route("/hapsing", methods=['POST', 'GET'])
def line_tts():
    if request.method == 'POST':
        tshamsoo = request.form
    else:
        tshamsoo = request.args
    tongan_ti_hethong_toh, _bangtsi = hapsing(tshamsoo)
    sikan = get_duration(filename=tongan_ti_hethong_toh)
    return jsonify({
        'bangtsi': 'https://{}/taiuanue.mp3?{}'.format(
            request.host, urlencode(tshamsoo, quote_via=quote)),
        'sikan': sikan,
    })


def hapsing(tshamsoo):
    try:
        taibun = tshamsoo['taibun']
        句物件 = 拆文分析器.對齊句物件(taibun, taibun)
    except KeyError:
        hunsu = tshamsoo['hunsu']
        句物件 = 拆文分析器.分詞句物件(hunsu)
    khaugitiau = 台灣話口語講法(句物件) + ' .'
    sootsai_wav = hashlib.sha256(khaugitiau.encode()).hexdigest() + '.wav'
    sootsai_mp3 = hashlib.sha256(khaugitiau.encode()).hexdigest() + '.mp3'
    imtong_sootsai_wav = join('/kiatko', sootsai_wav)
    imtong_sootsai_mp3 = join('/kiatko', sootsai_mp3)
    if not isfile(imtong_sootsai_mp3):
        tsau(khaugitiau, imtong_sootsai_wav)
        subprocess.run([
            'ffmpeg', '-y', '-i', imtong_sootsai_wav, imtong_sootsai_mp3
        ], check=True)

    bangtsi = '/kiatko/{}'.format(
        quote(sootsai_mp3),
    )
    return imtong_sootsai_mp3, bangtsi


def tsau(input_text, save_path):
    if input_text:
        inputs = [text_to_sequence(input_text.strip(), hp.tts_cleaner_names)]
    else:
        with open('sentences.txt') as f:
            inputs = [text_to_sequence(line.strip(), hp.tts_cleaner_names) for line in f]

    if args.vocoder == 'wavernn':
        voc_k = voc_model.get_step() // 1000
        tts_k = tts_model.get_step() // 1000

        simple_table([
            ('Tacotron', str(tts_k) + 'k'),
            ('r', tts_model.r),
            ('Vocoder Type', 'WaveRNN'),
            ('WaveRNN', str(voc_k) + 'k'),
            ('Generation Mode', 'Batched' if batched else 'Unbatched'),
            ('Target Samples', target if batched else 'N/A'),
            ('Overlap Samples', overlap if batched else 'N/A'),
        ])

    elif args.vocoder == 'griffinlim':
        tts_k = tts_model.get_step() // 1000
        simple_table([
            ('Tacotron', str(tts_k) + 'k'),
            ('r', tts_model.r),
            ('Vocoder Type', 'Griffin-Lim'),
            ('GL Iters', args.iters),
        ])

    for i, x in enumerate(inputs, 1):

        print(f'\n| Generating {i}/{len(inputs)}', file=stderr)
        _, m, attention = tts_model.generate(x)
        # Fix mel spectrogram scaling to be from 0 to 1
        m = (m + 4) / 8
        np.clip(m, 0, 1, out=m)

        if save_attn:
            save_attention(attention, save_path)

        if args.vocoder == 'wavernn':
            m = torch.tensor(m).unsqueeze(0)
            voc_model.generate(m, save_path, batched, target, overlap, hp.mu_law)
        elif args.vocoder == 'griffinlim':
            wav = reconstruct_waveform(m, n_iter=args.iters)
            save_wav(wav, save_path)

    print('\n\nDone.\n', file=stderr)
