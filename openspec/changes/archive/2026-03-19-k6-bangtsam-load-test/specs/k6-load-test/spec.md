## ADDED Requirements

### Requirement: k6 script 執行 constant rate 負載試驗
系統 SHALL 提供 k6 JavaScript script，以 constant-arrival-rate 1 req/sec 送 GET request 到 `{BASE_URL}/bangtsam`，持續 1 分鐘（共 60 requests）。`BASE_URL` 透過環境變數 `BASE_URL` 傳入，預設 `http://localhost:8000`。

#### Scenario: 正常執行負載試驗
- **WHEN** 使用者執行 k6 script
- **THEN** k6 以 1 req/sec ê 速度送 60 個 GET request 到 `{BASE_URL}/bangtsam`，每個 request 帶無仝 ê `taibun` query 參數

#### Scenario: 指定自訂 BASE_URL
- **WHEN** 使用者透過環境變數傳入 `BASE_URL=http://my-server:8000`
- **THEN** k6 SHALL 用該 URL 做為 base，送 request 到 `http://my-server:8000/bangtsam`

#### Scenario: 無傳 BASE_URL
- **WHEN** 使用者無設定 `BASE_URL` 環境變數
- **THEN** k6 SHALL 用預設值 `http://localhost:8000`

#### Scenario: Server 回應慢時維持送 request 速度
- **WHEN** server 回應時間超過 1 秒
- **THEN** k6 SHALL 開新 VU 繼續送 request，維持 1 req/sec ê constant rate（maxVUs 上限 10）

### Requirement: 測試資料用台灣歷史人物台羅名
系統 SHALL 提供 JSON 測試資料檔，包含 38 位台灣歷史人物 ê 漢字名、台語羅馬字（含多數唸法 kah 其他唸法），至少 60 筆唸法。

#### Scenario: 每個 request 用無仝 ê 名
- **WHEN** k6 送出 60 個 request
- **THEN** 每個 request ê `taibun` 參數 SHALL 用無仝 ê 台羅名，照順序 iterate 測試資料

#### Scenario: 測試資料包含漢字對應
- **WHEN** 使用者開啟 `k6/data/taiwanese-names.json`
- **THEN** 每筆資料 SHALL 包含 `hanji`（漢字名）、`tailo`（台語羅馬字）、`category`（人物類別）欄位

### Requirement: 試驗結果報告
k6 script SHALL 設定 thresholds 來判斷試驗結果。

#### Scenario: 定義成功標準
- **WHEN** 試驗完成
- **THEN** k6 SHALL 檢查 http_req_failed rate < 10%（容許少量失敗）kah p(95) 回應時間有記錄（無設硬性上限，因為 TTS 合成時間變化大）
