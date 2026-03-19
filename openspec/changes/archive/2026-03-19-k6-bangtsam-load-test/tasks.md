## 1. 測試資料

- [x] 1.1 建立 `k6/data/taiwanese-names.json`，收錄 38 位台灣歷史人物 ê 漢字名、台語羅馬字（多數唸法 + 其他唸法）、人物類別，至少 60 筆

## 2. k6 Script

- [x] 2.1 建立 `k6/bangtsam-load-test.js`，設定 constant-arrival-rate scenario（rate=1, timeUnit='1s', duration='1m', maxVUs=10）
- [x] 2.2 用 SharedArray 讀入 taiwanese-names.json，每個 iteration 用無仝 ê taibun 參數送 GET request 到 `http://localhost:8000/bangtsam`
- [x] 2.3 設定 thresholds：http_req_failed < 10%

## 3. 驗證

- [x] 3.1 確認 JSON 資料有效（72 筆、38 位人物），k6 script 語法正確

## 4. 手動驗證（Docker k6）

佇專案 root 目錄執行：

```bash
# Dry run（無需 server，驗證 script 語法）
docker run --rm \
  --mount type=bind,src=$(pwd)/k6,dst=/scripts \
  grafana/k6:latest run --dry-run /scripts/bangtsam-load-test.js

# 正式執行（需要先起 TTS server 佇 localhost:8000）
docker run --rm \
  --network host \
  --mount type=bind,src=$(pwd)/k6,dst=/scripts \
  grafana/k6:latest run /scripts/bangtsam-load-test.js
```

**注意事項：**
- `--network host` 才有法度連到 localhost:8000
- `--dry-run` 會驗證 script 語法 kah JSON 讀取，毋過無真正送 request
- TTS 合成較慢，`timeout` 設做 120 秒，`maxVUs` 設做 10 容許並行等待
