## ADDED Requirements

### Requirement: Inference 時禁用 gradient computation
`tsau()` 函數ê inference 運算 MUST 在 `torch.no_grad()` context 內執行，避免建立不必要ê computational graph。

#### Scenario: Inference 後回收 GPU 記憶體
- **WHEN** `tsau()` 執行 `tts_model.generate()` kah `voc_model.generate()`
- **THEN** 所有 inference 運算 SHALL 在 `torch.no_grad()` context 內執行，PyTorch 不建立 gradient graph

#### Scenario: 正常產生音檔
- **WHEN** 用戶送一個 TTS request 到 `/hapsing` 或 `/taiuanue.mp3`
- **THEN** 音檔 SHALL 正常產生，結果 kah 無加 `no_grad()` 時完全相同

### Requirement: Inference 完成後釋放 GPU 暫存記憶體
`tsau()` 函數 MUST 在 inference 完成後 call `torch.cuda.empty_cache()` 釋放 PyTorch allocator cache ê GPU 記憶體。

#### Scenario: 環境變數設定 concurrency
- **WHEN** `tsau()` ê inference loop 執行完畢
- **THEN** SHALL call `torch.cuda.empty_cache()` 釋放暫存ê GPU 記憶體

#### Scenario: CPU 模式下無副作用
- **WHEN** `DEVICE=cpu` 且 `tsau()` 執行完畢
- **THEN** `torch.cuda.empty_cache()` SHALL 無任何副作用（PyTorch 內建行為，CPU 模式下是 no-op）
