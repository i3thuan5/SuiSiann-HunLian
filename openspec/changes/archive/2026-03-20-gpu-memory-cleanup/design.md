## Context

`tsau()` 是 TTS inference ê進入點，由 Flask route 經 `hapsing()` 呼叫。目前 inference 無用 `torch.no_grad()`，PyTorch 預設會建立 computational graph 記錄每一步運算，為了 backpropagation。Inference 時完全無需要 gradient，這是純浪費。

目前架構：Gunicorn 開 7 個 worker，每個 worker 各載入一份 model 到 GPU。每次 request 做 inference 時，額外ê gradient graph 加上無釋放ê暫存 tensor 疊加，頻繁 OOM。

## Goals / Non-Goals

**Goals:**
- 用 `torch.no_grad()` 消除 inference 時不必要ê gradient computation，減少 GPU 記憶體用量
- 用 `torch.cuda.empty_cache()` 在每次 inference 後釋放 PyTorch cache ê GPU 記憶體

**Non-Goals:**
- 毋改 Gunicorn worker 數量或 concurrency 設定（做法 2）
- 毋改 worker 類型（做法 4 gthread）
- 毋改整體架構（做法 6 queue + worker）
- 毋改 model loading 邏輯

## Decisions

### 1. `torch.no_grad()` 包覆整個 inference 區塊

將 `tsau()` 內 `for` loop ê inference 邏輯用 `with torch.no_grad():` 包起來。

**替代方案：** 用 `@torch.no_grad()` decorator 在 `tsau()` 上。毋過 `tsau()` 前段有非 tensor 操作（text_to_sequence、simple_table），用 context manager 較精確，只包覆真正需要ê部分。

### 2. `torch.cuda.empty_cache()` 放 tī inference loop 結束後

Tī `for` loop 結束了後 call 一次，毋是每個 iteration 內底 call。因為目前 `inputs` 通常只有一個元素（單一 request），多次 call 無意義。

**替代方案：** 每個 iteration 內 call。毋過額外ê overhead 無必要，一次 request 通常只有一個 input。

### 3. 只改 `tsau()` 函數，毋動 model 定義

Model 層ê `generate()` 方法（`tts_model.generate()`、`voc_model.generate()`）毋改。`no_grad()` tī caller 層設定就有效，會 propagate 到所有內部運算。

## Risks / Trade-offs

- **[風險] `empty_cache()` 效果有限** → `empty_cache()` 只是將 PyTorch allocator cache 還予 CUDA，毋是減少 peak memory。真正減少記憶體ê是 `no_grad()`。`empty_cache()` 是附帶ê清理，有做無壞處。
- **[風險] 多 worker OOM 問題未完全解決** → 7 個 worker 各載入一份 model ê根本問題猶在。這是後續做法 2/4 ê範圍。
- **[Trade-off] 無法 tī `no_grad()` 內做 gradient 相關操作** → Inference 本來就無需要，無影響。
