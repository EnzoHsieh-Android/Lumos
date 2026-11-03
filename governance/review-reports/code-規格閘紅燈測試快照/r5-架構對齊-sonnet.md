severity: clean

**1. 分層與依賴方向:對齊**
- `_tg_rb_bad` 在修補後仍只呼叫同層的 `_tg_cand`,沒有新增呼叫對象,也沒有跨層直呼。對照:`scripts/lumos:49655`(定義)、`scripts/lumos:49658`(呼叫 `_tg_cand`)、`scripts/lumos:49334`(`_tg_cand` 簽名)。
- 參數改名後語意同義。`_tg_cand` 的第四個參數叫 `ident`,候選字典裡也有 `ident` 欄位(`scripts/lumos:49334` 起的 `_tg_cand`)。修補前叫 `key`,會跟候選字典裡「指紋」的 `key` 欄位撞名,現在不撞了。
- 全 repo 的 `_tg_rb_bad` 呼叫點(`scripts/lumos:49679`、`49741`、`49749`、`49751`、`49764`、`49795`、`49800`)只有 `gone_bad` 一處傳這個參數。它已同步改成 `ident="deleted"`(`scripts/lumos:49742`),沒有遺漏的 `key=` 呼叫。
- 提醒措辭與同區其他候選一致:
  - 兩條都用「請…」開頭的指令句,跟 `_tg_rb_doc` 的「還沒提交,請 git add 那支檔並提交」同寫法(`scripts/lumos:49813`、`49814`)。
  - 兩條也都用括號補充「(…時另列一條原因)」。
  - `gone_bad`(`scripts/lumos:49741` 到 `49742`)和孤兒檔那條(`scripts/lumos:49764` 到 `49765`)的新句型「改拿…來比(…有問題時另列一條原因)」彼此對稱。
- 看的段落:r5-repair-review.patch 裡「`def _tg_rb_bad(tok, file, reason, ident=None):`」那段,以及兩處「改拿它刪掉前那一版來比」「改拿它的內容來比」。

**2. 命名與錯誤處理:對齊**
- 沒有新增函式或常數,只有參數改名和訊息改字。
- 錯誤回傳形狀不變:仍是 `_tg_cand("tq/redbase-unreadable", …, extra=f"規格閘紅燈版 {tok}:{reason}")`,標頭「規格閘紅燈版 {tok}:」跟修補前一致(`scripts/lumos:49658`)。
- 「原因」是否真的是候選顯示的原因字串:`_TG_WHY["tq/redbase-unreadable"]` 的說明文字(`scripts/lumos:49331` 附近)已涵蓋「被刪、被改過或沒有留痕指到」,新措辭沒有跟它矛盾。
- 測試側沿用 `check(...)`、`_rb_repo`、`_rb_snap`、`_rb_push`、`_rb_only`、`toks`、`real`、`_RB_OTHER`、`_rb_fn`、`_tqg_kt` 這些既有輔助(`scripts/test_lumos.py:122525` 到 `122572`、`122747`),命名也是同一套「S4 r4 …」格式。
- 修補把舊斷言改成同時認「來比」,避免兩種措辭出現其一就漏抓。

**3. 第二種做法:沒有引入**
- 修補沒有另一套讀 git 狀態、路徑安全檢查、快取或找分岔點的寫法。
- 測試仍走既有的 `_rb_repo`/`_rb_push`/`_tqg_cands`。
- 讀 git 仍透過 `_lens_git_dl`(`scripts/lumos:49694` 附近的 `_tg_rb_deleted`)。
- 看的段落:patch 裡 `scripts/lumos` 的兩個 hunk 只動 docstring、參數名和訊息字串,沒有新增 `import`、子程序呼叫或模組級狀態。

**修補鏡頭中跟架構相關的部分:** 相鄰呼叫路徑仍沿用既有做法。`_tg_rb_metas` → `_tg_rb_bad` → `_tg_cand` 這條鏈,以及 `_tg_rb_load`/`_tg_rb_doc` 產生原因字串的路徑,都沒有改變形狀。

審材外佐證:`scripts/lumos:49334`(`_tg_cand`)、`scripts/lumos:49655`(`_tg_rb_bad`)、`scripts/lumos:49741`(`gone_bad`)、`scripts/lumos:49813`(`_tg_rb_doc` 的「請」句型)。

我是照 841e0f4bb 的內容查的,工作樹 HEAD 是 2b3ddb02c(只加審查材料),行號一致。

不對齊共 0 條,其中 major 0 條
