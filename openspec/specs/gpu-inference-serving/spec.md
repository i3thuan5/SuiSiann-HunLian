## ADDED Requirements

### Requirement: Single-process model loading
系統 SHALL 在單一 process 中載入 Tacotron 和 WaveRNN 模型各一份到 GPU，所有 request 共用同一個 model instance。

#### Scenario: 服務啟動時載入模型
- **WHEN** FastAPI application 啟動（lifespan startup）
- **THEN** Tacotron 和 WaveRNN 模型各載入一份到 GPU，設為 `.eval()` mode

#### Scenario: 多個 request 共用模型
- **WHEN** 多個 request 同時到達
- **THEN** 所有 request 使用同一個 Tacotron 和 WaveRNN model instance，不會額外載入模型

### Requirement: GPU memory management
系統 SHALL 在每次 inference 時使用 `torch.no_grad()` 並在完成後回收 GPU 記憶體。

#### Scenario: Inference 不建立 gradient graph
- **WHEN** 執行 Tacotron 或 WaveRNN inference
- **THEN** 所有 inference 操作在 `torch.no_grad()` context 中執行，不建立 gradient graph

#### Scenario: Inference 後回收 GPU 記憶體
- **WHEN** 一次 inference 完成（成功或失敗）
- **THEN** 系統呼叫 `torch.cuda.empty_cache()` 歸還未使用的 GPU 記憶體

### Requirement: Concurrency control via semaphore
系統 SHALL 使用 asyncio.Semaphore 控制同時進行 GPU inference 的數量，可透過環境變數設定。

#### Scenario: 環境變數設定 concurrency
- **WHEN** 環境變數 `GPU_CONCURRENCY` 設為 N（預設 1）
- **THEN** 系統建立 `asyncio.Semaphore(N)`，最多同時有 N 個 request 在做 GPU inference

#### Scenario: 超過 concurrency 限制的 request 排隊
- **WHEN** 已有 N 個 request 正在做 GPU inference，第 N+1 個 request 到達
- **THEN** 第 N+1 個 request 在 asyncio event loop 中等待（非阻塞），直到有 semaphore 釋出

#### Scenario: Inference 失敗時釋放 semaphore
- **WHEN** GPU inference 過程中發生錯誤
- **THEN** semaphore 仍然被正確釋放（使用 `async with` 保證）

### Requirement: Async request handling
系統 SHALL 使用 async handler + ThreadPoolExecutor 處理 blocking 的 GPU inference。

#### Scenario: GPU inference 不阻塞 event loop
- **WHEN** request 需要 GPU inference
- **THEN** inference 在 ThreadPoolExecutor 中執行，asyncio event loop 保持回應其他 request

### Requirement: API endpoint compatibility
系統 SHALL 保持與現有 API 端點完全相容。

#### Scenario: /taiuanue.mp3 端點
- **WHEN** GET 或 POST request 到 `/taiuanue.mp3`，帶 `taibun` 參數
- **THEN** 回傳 MP3 音檔，Content-Type 為 `application/octet-stream`，Content-Disposition 為 `attachment; filename=taiuanue.mp3`

#### Scenario: /bangtsam 端點
- **WHEN** GET 或 POST request 到 `/bangtsam`，帶 `taibun` 參數
- **THEN** 行為與 `/taiuanue.mp3` 完全相同

#### Scenario: / 根路徑端點
- **WHEN** GET 或 POST request 到 `/`，帶 `taibun` 參數
- **THEN** 行為與 `/taiuanue.mp3` 完全相同

#### Scenario: /hapsing 端點
- **WHEN** GET 或 POST request 到 `/hapsing`，帶 `taibun` 或 `hunsu` 參數
- **THEN** 回傳 JSON `{"bangtsi": "<mp3_url>", "sikan": <duration_seconds>}`

#### Scenario: taibun 參數輸入
- **WHEN** request 帶 `taibun` 參數（台語羅馬字）
- **THEN** 使用 `拆文分析器.對齊句物件(taibun, taibun)` 解析

#### Scenario: hunsu 參數輸入
- **WHEN** request 帶 `hunsu` 參數（漢字）而無 `taibun`
- **THEN** 使用 `拆文分析器.分詞句物件(hunsu)` 解析

### Requirement: Health check
系統 SHALL 提供健康檢查端點供 Docker healthcheck 使用。

#### Scenario: 健康檢查
- **WHEN** Docker healthcheck 執行
- **THEN** 可透過 `nvidia-smi` 或 HTTP health endpoint 確認 GPU 和服務狀態

### Requirement: Sentry error tracking
系統 SHALL 維持 Sentry error tracking 整合。

#### Scenario: Sentry 初始化
- **WHEN** 環境變數 `SENTRY_DSN` 有設定
- **THEN** Sentry SDK 初始化並追蹤錯誤和效能
