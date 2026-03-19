## Why

hokbu-khuanking inference server 使用 Gunicorn 6 workers（multiprocess）部署，每個 worker 各自載入一份 Tacotron + WaveRNN 到 GPU，導致：
- GPU memory 爆滿，出現 `CUDNN_STATUS_EXECUTION_FAILED` 錯誤
- 多 process 踩到彼此的 GPU 記憶體，WaveRNN 輸出全部變 NaN（`Categorical distribution` ValueError）
- 服務不穩定，需要 autoheal 持續重啟

根本原因：Gunicorn prefork 模型不適合 GPU inference，需要改為單 process async 架構。

## What Changes

- **BREAKING** 將 Flask/Gunicorn 替換為 FastAPI/Uvicorn（單 worker, async event loop）
- 模型只載入一次，所有 request 共用同一個 model instance
- 加入 `torch.no_grad()` 包裹所有 inference 呼叫，防止 gradient graph 累積
- 加入 `torch.cuda.empty_cache()` 定期回收 GPU 記憶體
- 使用 `asyncio.Semaphore` 控制同時 GPU inference 數量（可設定）
- 移除 hokbu-nginx container，由 FastAPI `FileResponse` 直接送檔
- 簡化 Docker Compose 架構（3層→2層）

## Capabilities

### New Capabilities
- `gpu-inference-serving`: GPU inference 服務架構 — 單 process async 模型、GPU 記憶體管理、concurrency 控制
- `audio-file-cache`: 音檔快取機制 — SHA256-based 檔案快取、清理策略

### Modified Capabilities

（無既有 spec）

## Impact

- **程式碼**: `hokbu-khuanking/suisiann.py` 全面改寫為 FastAPI async
- **Dockerfile**: `hokbu-khuanking/Dockerfile` 更新依賴（flask→fastapi, gunicorn→uvicorn）
- **Docker Compose**: 移除 `hokbu-nginx` service，`hapsing` 直接對 `nginx-cache`
- **Nginx**: `nginx-cache/default.conf` upstream 改指向 FastAPI；移除 `hokbu-nginx/`
- **API**: 端點路徑不變（`/taiuanue.mp3`, `/bangtsam`, `/hapsing`）
- **依賴**: 新增 fastapi, uvicorn；移除 flask, gunicorn
- **CI/CD**: `.travis.yml` integration test 需配合調整
