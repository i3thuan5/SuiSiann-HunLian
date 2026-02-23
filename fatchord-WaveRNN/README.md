# WaveRNN

自 https://github.com/fatchord/WaveRNN 來訓練。

## 架構

```
Client
  │
  ▼
nginx-cache (20GB proxy cache, 1年有效)
  │  cache HIT → 直接回
  │  cache MISS ↓
  ▼
FastAPI / Uvicorn (hapsing container)
  │  單一 process, 單一 GPU model instance
  │  asyncio.Semaphore 控制 GPU concurrency
  │  Tacotron (text→mel) + WaveRNN (mel→waveform)
  │  SHA256 檔案快取 (/kiatko/)
  ▼
MP3 output
```

### Docker Compose Services

| Service | 說明 |
|---------|------|
| `nginx-cache` | 前端快取層，cache 回應 1 年 |
| `hapsing` | FastAPI inference server（Gunicorn 1 worker + UvicornWorker） |
| `autoheal` | 監控 container 健康狀態，自動重啟 |
| `thai-imtong` | Cron job，每 15 分鐘清理 /kiatko/ 超過 24 小時的快取檔案 |

### GPU 記憶體管理

- 模型只載入一次（`.eval()` mode），所有 request 共用
- 所有 inference 包在 `torch.no_grad()` 中
- 每次 inference 後呼叫 `torch.cuda.empty_cache()`
- `GPU_CONCURRENCY` 環境變數控制同時 GPU inference 數量（預設 1）

### 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `DEVICE` | `gpu` | `gpu` 或 `cpu` |
| `CUDA_VISIBLE_DEVICES` | `0` | GPU 裝置 |
| `GPU_CONCURRENCY` | `1` | 同時 GPU inference 數量 |
| `GUNICORN_TIMEOUT` | `60` | Request timeout（秒） |
| `VOCODER` | `wavernn` | `wavernn` 或 `griffinlim` |
| `BATCHED` | `batched` | WaveRNN batched 模式 |
| `TARGET` | `2000` | Batched 模式 target samples |
| `OVERLAP` | `400` | Batched 模式 overlap samples |
| `SENTRY_DSN` | （空） | Sentry error tracking |

## 安裝

- [dobi](https://github.com/dnephin/dobi)
- [docker](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
- [docker-compose](https://docs.docker.com/compose/install/)
- 設定docker權限`sudo usermod -aG docker $USER`

## 訓練步驟

1. 先用`time dobi liah-giliau`，會掠 [SuiSiann-Dataset](https://suisiann-dataset.ithuan.tw/)，掠好會生做按呢

```text
.
├── 0.2
│   ├── ImTong
│   │   ├── SuiSiann_0001.wav
│   │   ├── SuiSiann_0002.wav
│   │   ├── SuiSiann_0003.wav
│   │   ├── SuiSiann_0004.wav
│   │   ├── SuiSiann_0005.wav
│   │    ...
│   └── SuiSiann.csv
├── dobi.yaml
├── Dockerfile
...
```

2. `time dobi tsuan-pianma`，wave downsample 閣降做 16bits，上尾合成較緊
3. `time dobi preprocess-tacotron`，準備tactorn格式。
4. `time dobi tacotron`，訓練Tacotron模型。若是tī tactorn訓練中，欲產生gta檔案，走`dobi tacotron-gta`。
5. `time dobi preprocess-wavernn`，照gta檔案，產生wavernn需要ê`dataset.pkl`
6. `time dobi wavernn`，訓練WaveRNN模型
7. `time dobi huatsiann`，合成語句

## API

### 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/taiuanue.mp3` | GET/POST | 回傳 MP3 音檔 |
| `/bangtsam` | GET/POST | 同 `/taiuanue.mp3` |
| `/` | GET/POST | 同 `/taiuanue.mp3` |
| `/hapsing` | GET/POST | 回傳 JSON（MP3 URL + 時間長度） |

### 參數

- `taibun`：台語羅馬字（例：`Ta̍k-ke tsò-hué lâi tshit-thô !`）
- `hunsu`：漢字（若無 `taibun` 時使用）

### Tshi

#### Curl

Get:

```bash
time curl \
  'localhost:8000/taiuanue.mp3?taibun=Ta%CC%8Dk-ke%20ts%C3%B2-hu%C3%A9%20l%C3%A2i%20tshit-th%C3%B4%20!'
```

Post:

```bash
time curl -i -X POST \
  -H "Content-type: application/x-www-form-urlencoded" \
  -H "Accept: text/plain" \
  -d 'taibun=Ta̍k-ke tsò-hué lâi tshit-thô !' \
  localhost:8000/taiuanue.mp3
```

#### Python3

```python
from http.client import HTTPConnection
from urllib.parse import urlencode

taiBun = 'Ta̍k-ke tsò-hué lâi tshit-thô !'
參數 = urlencode({
    'taibun': taiBun,
})
headers = {
    "Content-type": "application/x-www-form-urlencoded",
    "Accept": "text/plain"
}
it_conn = HTTPConnection('localhost', port=8000)
it_conn.request("POST", '/', 參數, headers)
it_conn.getresponse().read()
```

## 產生 requirements.txt

```bash
cd hokbu-khuanking
docker run --rm -v "$(pwd)":/work -w /work \
  pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime \
  bash -c "pip install pip-tools && pip-compile requirements.in -o requirements.txt"
```
