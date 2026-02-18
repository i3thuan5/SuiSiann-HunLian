## 1. Dependencies & Dockerfile

- [x] 1.1 建立新的 requirements.in，將 flask/gunicorn 替換為 fastapi/uvicorn[standard]，保留其他依賴
- [x] 1.2 Dockerfile 改用 requirements.in 安裝（升級 base image 後舊 requirements.txt 無效，pip-compile 可後續在 Docker 內執行）
- [x] 1.3 更新 hokbu-khuanking/Dockerfile：CMD 改用 gunicorn -w 1 -k uvicorn.workers.UvicornWorker，移除 GUNICORN_WORKERS 環境變數，新增 GPU_CONCURRENCY 環境變數

## 2. Core FastAPI Application

- [x] 2.1 改寫 hokbu-khuanking/suisiann.py 為 FastAPI app：lifespan 載入模型（eval mode）、asyncio.Semaphore(GPU_CONCURRENCY)、ThreadPoolExecutor
- [x] 2.2 實作 inference function：包在 torch.no_grad() + try/finally torch.cuda.empty_cache()
- [x] 2.3 實作 /taiuanue.mp3 和 /bangtsam 端點（GET/POST），使用 FileResponse 回傳 MP3
- [x] 2.4 實作 / 根路徑端點，行為同 /taiuanue.mp3
- [x] 2.5 實作 /hapsing 端點（GET/POST），回傳 JSON（bangtsi URL + sikan duration）
- [x] 2.6 維持 Sentry SDK 整合（使用 FastAPI 的 sentry-sdk[fastapi]）

## 3. Cache & File Serving

- [x] 3.1 保留 SHA256-based 檔案快取邏輯（口語調 → hash → /kiatko/）
- [x] 3.2 使用 FastAPI FileResponse 直接送 MP3 檔（取代 X-Accel-Redirect）

## 4. Docker Compose & Nginx

- [x] 4.1 從 docker-compose.yaml 移除 hokbu-nginx service
- [x] 4.2 移除 hokbu-bridge network，hapsing 直接接到 default network
- [x] 4.3 更新 nginx-cache/default.conf：upstream 從 hokbu-nginx 改為 hapsing:8000
- [x] 4.4 更新 hapsing service 的環境變數（移除 GUNICORN_WORKERS，新增 GPU_CONCURRENCY）
- [x] 4.5 更新 thai-khuanking/15min/hinnsak.sh：清理時間從 15 分鐘改為 24 小時（-mmin +1440）

## 5. CI/CD

- [x] 5.1 更新 .travis.yml integration test：移除 GUNICORN_WORKERS、hokbu-nginx nginx -t、deploy 舊變數
- [x] 5.2 更新 deploy.yaml 及 .env.template：移除 hokbu-nginx reload、舊 Gunicorn 變數，新增 GPU_CONCURRENCY

## 6. Cleanup

- [x] 6.1 移除 hokbu-nginx/ 目錄（default.conf 不再需要）
- [x] 6.2 從 docker-compose.yaml 移除 hokbu-bridge network 定義
