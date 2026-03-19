## Why

專案有 FastAPI TTS API（`/bangtsam`），需要了解佇負載之下 ê 效能表現。目前無任何負載試驗工具，無法度知影 API 佇持續 request 之下會 ê 回應時間、錯誤率。用 Grafana k6 做 constant rate 負載試驗，確認 API 佇 1 req/sec ê 條件下會當穩定運作。

## What Changes

- 新增 k6 負載試驗 JavaScript script，對 `http://localhost:8000/bangtsam` 送 GET request
- 新增台灣歷史人物台語羅馬字名單（38 位人物，60+ 個唸法），做為測試資料
- 每個 request 用無仝 ê 人名做 `taibun` 參數，避免 hit server 端 ê cache
- Constant rate: 1 req/sec，持續 1 分鐘，共 60 requests
- 人名 kah 羅馬字 ê 對應整理佇負載試驗文件內底

## Capabilities

### New Capabilities
- `k6-load-test`: k6 負載試驗 script kah 台灣人物台羅測試資料

### Modified Capabilities

## Impact

- 新增檔案佇專案（k6 script + 測試資料），無影響現有程式碼
- 執行時需要 k6 CLI 工具（`brew install k6` 或 `apt install k6`）
- 需要 TTS API server 先 tī localhost:8000 起行
