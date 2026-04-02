## Context

專案 ê TTS API 是 FastAPI 應用程式（`fatchord-WaveRNN/hokbu-khuanking/suisiann.py`），提供 `/bangtsam` endpoint。接收 `taibun`（台語羅馬字）參數，合成語音回傳 mp3。Server 有 hash-based cache：仝款 ê 輸入文字會直接回傳舊 ê mp3，無重新合成。GPU concurrency 由 `GPU_CONCURRENCY` 環境變數控制（預設 1）。

## Goals / Non-Goals

**Goals:**
- 提供可重複執行 ê k6 負載試驗 script
- 用 60 個無仝 ê 台灣人物台羅名做測試資料，逐個 request 用無仝 ê 名避免 cache
- 整理人名漢字 kah 台羅 ê 對應表佇文件內底
- Constant rate 1 req/sec，1 分鐘，驗證基本穩定性

**Non-Goals:**
- Ramp up / stress test（後續若需要才加）
- 自動化 CI/CD 整合
- Server 端 ê 效能調校

## Decisions

### 1. 檔案位置：`k6/` 目錄佇專案 root

放佇專案 root 下 ê `k6/` 目錄，kah application code 分開。

- `k6/bangtsam-load-test.js` — k6 test script
- `k6/data/taiwanese-names.json` — 測試資料（含漢字 kah 台羅對應）

**理由：** k6 script 是獨立 ê 工具，無需要 kah Python code 混做伙。`k6/` 命名清楚表示用途。

### 2. 測試資料格式：JSON array with metadata

```json
[
  {
    "hanji": "蔣渭水",
    "tailo": "Tsiúnn Uī-tsuí",
    "category": "抗日/民主運動"
  }
]
```

**理由：** k6 ê `SharedArray` 會當直接讀 JSON。加 `hanji` kah `category` 欄位方便人讀嘛方便後續擴充。

### 3. Request 策略：Sequential iteration，無 random

用 k6 ê `SharedArray` 配合 `exec.vu.iterationInScenario` index 照順序送，確保 60 個 request 用 60 個無仝 ê 名。

**理由：** 比 random 較好控制，保證每個名攏會用著，無重複。

### 4. k6 scenario：`constant-arrival-rate`

用 k6 ê `constant-arrival-rate` scenario，設 rate=1, timeUnit='1s', duration='1m'。

**理由：** 這是 k6 內建 ê open model，保證穩定 1 req/sec 無論 server 回應速度。

### 5. BASE_URL 透過環境變數設定

用 k6 ê `__ENV.BASE_URL` 讀取環境變數，Docker 用 `-e BASE_URL=...` 傳入。無設定就 fallback 到 `http://localhost:8000`。

**理由：** 方便佇無仝環境（local、staging、production）測試，免改 script。

## Risks / Trade-offs

- **TTS 合成時間長** → 1 req/sec 若 server 回應超過 1 秒，k6 會排隊。設 `maxVUs` 較大（例 10）來容許並行等待。
- **GPU memory** → 多個並行 request 可能 OOM。靠 server 端 ê `gpu_semaphore` 控制，k6 端無需處理。
- **外國人名（馬偕、甘為霖等）** → 辭典有收錄，台羅查詢結果有效。
