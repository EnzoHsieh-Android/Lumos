# AGENTS.md（Codex 等外部 agent 的入口指路檔）

本 repo 的規矩與現況**單一來源**如下，本檔只指路、不複製內容（防漂移）：

1. **專案規矩**：讀 `CLAUDE.md`（圖譜先行、零依賴家規、合約鏈、寫入規範）。
2. **系統現況**：讀 `docs/lumos-toolchain-knowledge/MOC/index.md`（知識圖譜索引），再按需讀 `Systems/`（機制）、`Projects/`（計劃與決策）、`Verification/`（驗證紀錄）。圖譜是唯一真相來源，與 code 衝突以圖譜的合約（★INVARIANT★）為準。
3. **CLI**：`python3 scripts/lumos --help`（66 個頂層命令；讀圖譜用 `context`/`search`/`contracts`/`query`）。
4. **看你被派來做什麼**:被派成唯讀審計員/辯方(`codex exec --sandbox read-only`)時,**不要**改 `docs/*-knowledge/` 下的檔,發現問題用報告回覆;被當協作者開在這個 repo 裡時,照 `CLAUDE.md`(與下方紀律區塊)的規矩走——改了會影響行為/決策/驗證的 code,當次就把脈絡寫回圖譜。
