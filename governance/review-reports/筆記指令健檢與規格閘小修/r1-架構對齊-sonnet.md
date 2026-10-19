severity: major

先講結論:這份設計大半是借既有零件,對得很整齊。最明顯的不齊是 B3 的治理帳讀法,它另寫了一支讀取,而 `_gov_vc_gate_events` 已經在做同樣的事。

## 1. 分層與依賴方向

大致對齊。
- `cmd_summary_add` 放在 `cmd_summary_line` 旁邊,用同一把 `_vault_write_lock`,寫入走 `atomic_write_verify`。對照 file: `scripts/lumos:22475`、`scripts/lumos:22530`。
- `_set_keys_text()` 讓 argparse 說明和擋下訊息共用同一份,跟 `_cmd_set_locked` 的 `SCALAR_KEYS`/`COND_KEYS` 同層,方向對。
- W10 用模組層集合只印一次警告,跟現成的 `_BT_PARALLEL_WARNED` / `_bt_parallel_warn` 同一種做法。對照 file: `scripts/lumos:54569`。
- 新的 `_summary_line_rebuild` 只會換行或刪行,沒有插入。summary-add 要新寫一支插入用的小函式,這是結構一樣的新增,不算不齊。

finding 1(B3 的讀法,major)
severity: major
blocking: 是
引句:「推送閘有候選計劃在審查帳找不到留痕時,才讀一次治理帳」
設計要自己再寫一段「讀治理帳、用字串篩行、解 JSON、去重」。但 `_gov_vc_gate_events(root, gate)` 已經做了這件事:先擋路徑(`_retro_gov_path_err`),用 `_retro_read_bytes`、`_ledger_lines` 切行,用 bytes needle 篩行,再解 JSON,帳壞時回「帳壞原因」讓呼叫端 fail-closed。`_retro_gov_events` 也是照這支抽出來的。
- 另寫一套會漏掉路徑守衛和 fail-closed 語意,並且多出第二種讀法。
- 「第一次走到才讀、存進 ctx 給多份計劃共用」的接法,`_nogo_ctx_gov` 已有先例,應照那個做。
- file: `scripts/lumos:15481`、`scripts/lumos:15467`、`scripts/lumos:9421`(`_nogo_ctx_gov`)

## 2. 命名與錯誤處理

finding 2(B3 的寫法,minor)
severity: minor
blocking: 否
引句:「同一筆再寫一筆治理帳事件」
- 設計沒寫用哪支寫入器。既有有三支:`_gate_event`、`_append_governance_log`、`_codeloop_gov_log`。
- `_gate_event` 會回傳寫入成敗,`docs/` 不存在時回 None;事件形狀是平的,帶 `gate`、`kind`、`hard`、`detail`。
- 設計的事件把整筆審查帳塞進巢狀的 `record`,跟既有事件形狀不同。
- 建議點名用 `_gate_event`,並確認 `hard` 缺欄時 `_gov_routes_local` 會判進版控帳。後者看程式是成立的:缺欄回 False,也就是進版控帳。
- file: `scripts/lumos:1488`、`scripts/lumos:1494`、`scripts/lumos:54089`

其餘錯誤處理對齊。summary-add 在非 git 專案時 rc2,跟 `drift fix` 同一個擋法;去重印「已經有」、rc0,跟 append 同一種寫法。

## 3. 第二種做法

finding 3(F14 手寫正規化,minor,⚠)
severity: minor
blocking: 否
引句:「統一規則:寫入端跑讀取端同一支判斷。」
設計把「去外層 `[[ ]]`、去結尾 `.md`、去頭尾空白」寫成新的正規化步驟。`link_target(s)` 已經做了這三件事(它還多去別名和標題),`_cmd_append_locked` 自己也用它做去重。建議直接用 `link_target` 再交給 `_lands_in_bad`。設計沒寫死用不用,我拿不準是它要自刻還是只是描述行為,所以標 ⚠ 交編排者。
- file: `scripts/lumos:502`、`scripts/lumos:28159`、`scripts/lumos:22763`

finding 4(F29 的 git 讀法與 W5 的 check-ignore 呼叫,minor)
severity: minor
blocking: 否
引句:「讀上一個提交的版本(一次,只這一篇),同樣抽一次;」
- 設計沒說用哪支函式讀 `HEAD:<這篇>`。既有做法是 `_lens_git`(逾時與吞錯統一)或 `_nodehome_reader(root, 某個 sha)`。
- 不要新開 `subprocess` 直呼 git。W5 的 `git check-ignore --stdin -z` 也一樣,`_lens_git` 在 `scripts/lumos:1477` 已有 check-ignore 的先例。
- 要確認 `_lens_git` 收不收 stdin 輸入,不收就得補一個參數,而不是另開 subprocess。
- 引句對應 F29;W5 那句是「不存在的路徑先整批問一次 `git check-ignore --stdin -z`」。
- file: `scripts/lumos:44935`、`scripts/lumos:32822`、`scripts/lumos:1477`

## 4. 落點

finding 5(lands_in 對應,minor,⚠)
severity: minor
blocking: 否
引句:「各提交互不依賴,可以分開推;⑦ 碰推送閘,代碼審會判 high,其他多半 standard。」
- ⑤ 的落點列了 `Systems/lumos-cli-read` 和 `Systems/lumos-refcheck`,但 doctor P 段(§7、§8 改它)和 `_node_code_ref_tokens` 的 `cmdline` 參數,我沒能從提供的資料確認它們的家是哪一篇。
- ⑦ 的 B3 新增「治理帳多一種 spec-gate-record 事件」,`lumos gov` 這類既有讀者要確認不受影響。這部分的家(治理帳分流那篇)不在 lands_in 裡。
- 其餘落點合理:
  - `Systems/筆記內容閘` 已經是 `neg_revisit_measure.py` 的家,對。
  - 規格閘、每支檔有家、test-profile-multiplatform 對應清楚。
  - summary-add 寫進 `lumos-cli-write`,跟 summary-line 同一個家。
- 這些都屬已存在的 Systems 節點,不需要另開新節點。

不對齊共 5 條,其中 major 1 條
