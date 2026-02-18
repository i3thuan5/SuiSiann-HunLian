## Context

hokbu-khuanking 是 SuiSiann TTS 的 inference server，使用 Tacotron（text→mel）+ WaveRNN（mel→waveform）在 T4 GPU 上合成台語語音。

現狀：
- Gunicorn prefork 6 workers，每個 worker 各自載入模型到 GPU
- 6 個 CUDA context + 6 份模型 → GPU memory 爆滿
- 錯誤：`CUDNN_STATUS_EXECUTION_FAILED`、WaveRNN 輸出 NaN
- 依賴 autoheal 持續重啟維持服務

架構：`nginx-cache → hokbu-nginx → Flask(hapsing)` 三層，其中 hokbu-nginx 僅做 X-Accel-Redirect 送 /kiatko/ 檔案。

## Goals / Non-Goals

**Goals:**
- GPU 記憶體穩定：模型只載入一次，inference 後記憶體回收
- Concurrency 可控：可設定同時 GPU inference 數量
- 保持 API 相容：`/taiuanue.mp3`, `/bangtsam`, `/hapsing` 端點不變
- 簡化架構：移除 hokbu-nginx，減少一層服務

**Non-Goals:**
- 不更換模型架構（不換 VITS、HiFi-GAN 等）
- 不做 multi-GPU / autoscaling
- 不更換 Nginx cache 層（nginx-cache 維持不變）
- 不改變訓練流程

## Decisions

### D1: FastAPI + Uvicorn 取代 Flask + Gunicorn

**選擇**: FastAPI + Gunicorn(1 worker, UvicornWorker)

**原因**:
- WaveRNN 是 autoregressive，無法跨 request batch，所以 Triton/TorchServe 的 dynamic batching 無優勢
- 單 process = 單一 CUDA context + 單一模型副本，根本解決 memory 問題
- Flask → FastAPI 遷移成本低，route 語法幾乎相同
- asyncio event loop 天然支援 request 排隊

**替代方案考慮**:
- Ray Serve：功能強但引入額外基礎設施，單 GPU 場景過度複雜
- Triton：autoregressive 模型無法利用其 batching，Python backend 等同 FastAPI 但更複雜
- TorchServe：已於 2025/08 被 archive，且 worker 模型同樣會載入多份

### D2: asyncio.Semaphore 控制 GPU concurrency

**選擇**: 透過環境變數 `GPU_CONCURRENCY` 設定 Semaphore 值，預設為 1

**原因**:
- Semaphore(1)：嚴格序列化 GPU 存取，最安全
- Semaphore(2)：允許 CPU 前處理與 GPU 推論重疊，稍快
- 可透過環境變數調整，不需改 code

**機制**:
```
request 進來 → async handler → 等 semaphore
  → 取得 semaphore → run_in_executor(inference)
  → inference 完成 → 釋放 semaphore → 回應
```

### D3: ThreadPoolExecutor 處理 blocking inference

**選擇**: `ThreadPoolExecutor(max_workers=N)` 搭配 `loop.run_in_executor()`

**原因**:
- PyTorch GPU 操作會釋放 GIL，所以 thread 可以有效重疊
- CPU 前處理（拆文分析器、text_to_sequence）也在 thread 中執行
- executor 的 max_workers 與 semaphore 值一致

### D4: GPU 記憶體管理策略

**選擇**:
- 所有 inference 包在 `torch.no_grad()` 中
- 模型啟動時設為 `.eval()` mode
- 每次 inference 後呼叫 `torch.cuda.empty_cache()`

**原因**:
- `no_grad()` 防止建立 gradient graph（現在的 code 完全沒有）
- `empty_cache()` 將 PyTorch cache 歸還給 CUDA，避免 fragmentation 累積
- `.eval()` 關閉 dropout 等 training-only 行為

### D5: 移除 hokbu-nginx，FastAPI 直接送檔

**選擇**: 用 FastAPI `FileResponse` 取代 Nginx X-Accel-Redirect

**原因**:
- hokbu-nginx 唯一功能是 X-Accel-Redirect 送 /kiatko/ 的檔案
- FastAPI `FileResponse` 使用 sendfile syscall，效能接近 Nginx
- 少一個 container = 少一個維護點、少一個網路跳轉
- nginx-cache 仍在前面，大部分 request 根本不會到 FastAPI

**架構變更**:
```
現在: nginx-cache → hokbu-nginx → Flask(hapsing)
之後: nginx-cache → FastAPI(hapsing)
```

### D6: /kiatko/ 快取清理時間

**選擇**: 從 15 分鐘改為 24 小時（透過環境變數可調）

**原因**:
- 15 分鐘太短，同樣文字重複合成浪費 GPU
- nginx-cache 已有 1 年快取，/kiatko/ 只是避免 disk 無限增長
- disk 成本遠低於 GPU 運算成本

## Risks / Trade-offs

- **[單點故障]** 只有 1 個 worker，process crash = 服務中斷 → Mitigation: Docker restart policy + autoheal 維持不變
- **[序列化延遲]** Semaphore(1) 時，6 個同時 request 的第 6 個等待時間 = 6× 合成時間 → Mitigation: nginx-cache 命中率高的話，實際同時打到 FastAPI 的 request 少；可調高 semaphore 值
- **[FileResponse vs Nginx]** Python 送檔效能略低於 Nginx → Mitigation: nginx-cache 層已 cache 大部分 response；未來可選擇性加回 Nginx
- **[Base Image 升級]** 升級到 pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime（Python 3.10），可用最新 FastAPI/Uvicorn。PyTorch 2.x 向下相容載入 1.x 的 checkpoints
