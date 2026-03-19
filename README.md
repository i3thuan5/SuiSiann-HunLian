# Hun-lian

現此時huānn`fachord-WaveRNN`專案

## k6 負載試驗

用 Grafana k6 對 TTS API（`/bangtsam`）做負載試驗。
測試資料：38 位台灣歷史人物 ê 台語羅馬字名（72 筆唸法），來源：[教育部臺灣閩南語常用詞辭典](https://sutian.moe.edu.tw/zh-hant/huliok/miasenn/)。

```bash
# Dry run（驗證 script 語法，免起 server）
docker run --rm \
  --mount type=bind,src=$(pwd)/k6,dst=/scripts \
  grafana/k6:latest run --dry-run /scripts/bangtsam-load-test.js

# 正式執行（預設 localhost:8000）
docker run --rm \
  --network host \
  --mount type=bind,src=$(pwd)/k6,dst=/scripts \
  grafana/k6:latest run /scripts/bangtsam-load-test.js

# 指定其他 URL
docker run --rm \
  --network host \
  --mount type=bind,src=$(pwd)/k6,dst=/scripts \
  -e BASE_URL=http://your-server:8000 \
  grafana/k6:latest run /scripts/bangtsam-load-test.js
```
