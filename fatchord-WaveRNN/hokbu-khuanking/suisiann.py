import asyncio
import hashlib
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from os.path import isfile, join
from sys import stderr
from urllib.parse import quote, urlencode

import numpy as np
import sentry_sdk
import torch
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from librosa.core.audio import get_duration
from models.fatchord_version import WaveRNN
from models.tacotron import Tacotron
from utils import hparams as hp
from utils.display import save_attention
from utils.dsp import reconstruct_waveform, save_wav
from utils.paths import Paths
from utils.text import text_to_sequence
from utils.text.symbols import symbols
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.語音合成 import 台灣話口語講法

models = {}
gpu_semaphore = None
executor = None


def thak():
    vocoder = os.getenv('VOCODER', 'wavernn')
    device_env = os.getenv('DEVICE', 'gpu')
    batched = os.getenv('BATCHED', 'batched') == 'batched'
    target_env = os.getenv('TARGET', None)
    overlap_env = os.getenv('OVERLAP', None)
    save_attn = os.getenv('SAVE_ATTN', False)
    iters = os.getenv('GL_ITERS', 32)

    if vocoder in ['griffinlim', 'gl']:
        vocoder = 'griffinlim'
    elif vocoder in ['wavernn', 'wr']:
        vocoder = 'wavernn'
    else:
        raise ValueError('Must provide a valid vocoder type!')

    hp.configure('hparams.py')
    paths = Paths(hp.data_path, hp.voc_model_id, hp.tts_model_id)

    if device_env == 'gpu' and torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')
    print('Using device:', device, file=stderr)

    voc_model = None
    target = None
    overlap = None

    if vocoder == 'wavernn':
        if target_env is None:
            target_env = hp.voc_target
        if overlap_env is None:
            overlap_env = hp.voc_overlap
        if batched is None:
            batched = hp.voc_gen_batched

        target = int(target_env)
        overlap = int(overlap_env)

        print('\nInitialising WaveRNN Model...\n', file=stderr)
        voc_model = WaveRNN(
            rnn_dims=hp.voc_rnn_dims,
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
            mode=hp.voc_mode,
        ).to(device)
        voc_load_path = paths.voc_latest_weights
        voc_model.load(voc_load_path)
        voc_model.eval()

    print('\nInitialising Tacotron Model...\n', file=stderr)
    tts_model = Tacotron(
        embed_dims=hp.tts_embed_dims,
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
        stop_threshold=hp.tts_stop_threshold,
    ).to(device)
    tts_load_path = paths.tts_latest_weights
    tts_model.load(tts_load_path)
    tts_model.eval()

    return {
        'vocoder': vocoder,
        'voc_model': voc_model,
        'tts_model': tts_model,
        'batched': batched,
        'target': target,
        'overlap': overlap,
        'save_attn': save_attn,
        'iters': iters,
    }


@asynccontextmanager
async def lifespan(app):
    global models, gpu_semaphore, executor

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        enable_tracing=True,
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

    models = thak()

    concurrency = int(os.getenv('GPU_CONCURRENCY', '1'))
    gpu_semaphore = asyncio.Semaphore(concurrency)
    executor = ThreadPoolExecutor(max_workers=concurrency)
    print(f'GPU concurrency: {concurrency}', file=stderr)

    yield

    executor.shutdown(wait=False)


app = FastAPI(lifespan=lifespan)


def _get_tshamsoo(request: Request):
    if request.method == 'POST':
        return request._form
    return request.query_params


def _hapsing(tshamsoo):
    try:
        taibun = tshamsoo['taibun']
        句物件 = 拆文分析器.對齊句物件(taibun, taibun)
    except KeyError:
        hunsu = tshamsoo['hunsu']
        句物件 = 拆文分析器.分詞句物件(hunsu)
    khaugitiau = 台灣話口語講法(句物件) + ' .'
    sootsai_hash = hashlib.sha256(khaugitiau.encode()).hexdigest()
    imtong_sootsai_wav = join('/kiatko', sootsai_hash + '.wav')
    imtong_sootsai_mp3 = join('/kiatko', sootsai_hash + '.mp3')
    if not isfile(imtong_sootsai_mp3):
        _tsau(khaugitiau, imtong_sootsai_wav)
        subprocess.run(
            ['ffmpeg', '-y', '-i', imtong_sootsai_wav, imtong_sootsai_mp3],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    return imtong_sootsai_mp3


def _tsau(input_text, save_path):
    inputs = [text_to_sequence(input_text.strip(), hp.tts_cleaner_names)]

    tts_model = models['tts_model']
    voc_model = models['voc_model']

    with torch.no_grad():
        for i, x in enumerate(inputs, 1):
            print(f'\n| Generating {i}/{len(inputs)}', file=stderr)
            _, m, attention = tts_model.generate(x)
            m = (m + 4) / 8
            np.clip(m, 0, 1, out=m)

            if models['save_attn']:
                save_attention(attention, save_path)

            if models['vocoder'] == 'wavernn':
                m = torch.tensor(m).unsqueeze(0)
                voc_model.generate(
                    m, save_path,
                    models['batched'], models['target'],
                    models['overlap'], hp.mu_law,
                )
            elif models['vocoder'] == 'griffinlim':
                wav = reconstruct_waveform(m, n_iter=models['iters'])
                save_wav(wav, save_path)

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    print('\n\nDone.\n', file=stderr)


async def _async_hapsing(request: Request):
    if request.method == 'POST':
        await request.form()
    tshamsoo = _get_tshamsoo(request)
    async with gpu_semaphore:
        loop = asyncio.get_event_loop()
        imtong_sootsai_mp3 = await loop.run_in_executor(
            executor, _hapsing, tshamsoo
        )
    return imtong_sootsai_mp3, tshamsoo


@app.api_route("/", methods=['GET', 'POST'])
@app.api_route("/taiuanue.mp3", methods=['GET', 'POST'])
@app.api_route("/bangtsam", methods=['GET', 'POST'])
async def bangtsam_tts(request: Request):
    imtong_sootsai_mp3, _tshamsoo = await _async_hapsing(request)
    return FileResponse(
        imtong_sootsai_mp3,
        media_type='application/octet-stream',
        filename='taiuanue.mp3',
    )


@app.api_route("/hapsing", methods=['GET', 'POST'])
async def line_tts(request: Request):
    imtong_sootsai_mp3, tshamsoo = await _async_hapsing(request)
    sikan = get_duration(filename=imtong_sootsai_mp3)
    return JSONResponse({
        'bangtsi': 'https://{}/taiuanue.mp3?{}'.format(
            request.headers.get('host', ''),
            urlencode(dict(tshamsoo), quote_via=quote),
        ),
        'sikan': sikan,
    })
