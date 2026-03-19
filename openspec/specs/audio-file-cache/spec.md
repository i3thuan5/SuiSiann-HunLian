## ADDED Requirements

### Requirement: SHA256-based file cache
系統 SHALL 以口語調文字的 SHA256 hash 作為快取 key，將合成結果存為檔案。

#### Scenario: 相同文字命中快取
- **WHEN** request 的口語調文字（經 `台灣話口語講法` 轉換後）與先前 request 相同
- **THEN** 直接回傳已存在的 MP3 檔案，不重新 GPU 合成

#### Scenario: 新文字合成並快取
- **WHEN** request 的口語調文字沒有對應的快取檔案
- **THEN** 執行 GPU 合成，產生 WAV 檔，用 ffmpeg 轉為 MP3，存入 `/kiatko/` 目錄

#### Scenario: 快取檔名格式
- **WHEN** 口語調文字經 SHA256 hash
- **THEN** WAV 存為 `/kiatko/<sha256>.wav`，MP3 存為 `/kiatko/<sha256>.mp3`

### Requirement: FastAPI FileResponse for cached files
系統 SHALL 使用 FastAPI FileResponse 直接回傳快取的 MP3 檔案。

#### Scenario: 回傳快取檔案
- **WHEN** 快取的 MP3 檔案存在
- **THEN** 使用 FileResponse 回傳，Content-Type 為 `application/octet-stream`

### Requirement: Cache cleanup policy
快取檔案 SHALL 由 cron job 定期清理，清理間隔可透過設定調整。

#### Scenario: 定期清理舊快取
- **WHEN** cron job 執行
- **THEN** 刪除 `/kiatko/` 中超過設定時間（預設 24 小時）的檔案

### Requirement: Nginx proxy cache layer
nginx-cache SHALL 作為前端快取層，cache FastAPI 的回應。

#### Scenario: Nginx cache hit
- **WHEN** 相同 URL 的 request 再次到達
- **THEN** nginx-cache 直接回傳快取的回應，不轉發到 FastAPI

#### Scenario: Nginx cache miss
- **WHEN** URL 不在 nginx-cache 中
- **THEN** 轉發 request 到 FastAPI，並快取回應（200 狀態碼快取 1 年）
