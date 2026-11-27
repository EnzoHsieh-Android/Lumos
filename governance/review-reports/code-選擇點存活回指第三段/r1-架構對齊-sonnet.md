severity: minor

我只讀了 `r1-pack-code.patch` 和 `scripts/lumos` 的鄰居寫法,沒有跑任何程式,也沒建暫存目錄。

**問 1:分層與依賴方向**
- 新增的 choice-layer 沒有跨層直呼。判讀檔寫入走 `_note_audit_write_verdict`,只加 `name`、`sort_keys` 兩個選用參數(`scripts/lumos:57596`)。
- 工作目錄走 `_note_audit_work_dir` 加 `_note_audit_safe_dir`(`scripts/lumos:57578`、`57618`),符號連結守衛是沿用的。
- 記帳走 `_choice_gate_event`,子命令派發放進 `_main_choice_cmds`(`scripts/lumos:82713`),跟 choice-kill、situation-rule 同處。
- 推送閘用 `aux` 參數把判讀傳進 `_choice_push_judge`,用的是既有的 `_choice_ledger_aux` 管道。
- gov 三行照既有 `_gov_choice_count_*` 一種事件一支計數函式的寫法,掛進 `_gov_choice_count_one` 的分派表。
- `_kill_target`、`_kill_revert` 抽成共用,逐支流程(`scripts/lumos:28655`、`28698`)與合批編譯(`29455`、`29620`)都改走它們,依賴方向沒問題。
- 下面 finding 1 是這次抽取沒收乾淨的地方。

severity: minor
blocking: 否
引句:「if rv is None:   # checkout 失敗或改成直接寫回原文:修改時間由這裡重讀(同 _kill_revert 的後半)」

這條出在 `_KillCompile.restore`(patch 第 536 行起)。`_kill_revert` 把「讀回修改時間、加入或移出 `unsure`」收進共用函式,但 `restore` 在 `rv is None` 的分支又手寫了一份同樣的 `_kill_after_write` / `discard` / `add`。結構是對的,只是抽取不徹底,同一段邏輯還剩兩處。

**問 2:命名與錯誤處理**
- 新函式命名跟鄰居一致:`_choice_layer_*`、`_gov_choice_count_*`、`_kill_*`。
- 錯誤出口大多走 `_situation_rule_say`,輸出 `擋下:` 前綴,跟既有 choice-kill 那批(`scripts/lumos:80129`、`80132`)一致。
- 「整份驗證、不合就整份拒收、什麼都不寫、rc 2」跟盲判一致。

severity: minor
blocking: 否
引句:「print("choice-layer:整份拒收,什麼都沒寫" + ("" if res else "(結果是空的)"), file=sys.stderr)」

這是整份拒收那條路徑跟盲判的差異,下面三點都在這一帶:
- **前綴不同**:盲判印 `擋下:盲判結果有 N 處不合,整份沒寫:`(`scripts/lumos:77795` 附近),這裡的前綴是 `choice-layer:`,沒有 `擋下:`。
- **逐筆錯誤沒有上限**:盲判逐筆印最多 10 條,再印「另有 N 處」,這裡的 `for e in bad` 全部印出。
- **BOM 處理不同**:盲判讀結果檔用 `utf-8-sig`(`scripts/lumos:77774` 附近),`_choice_layer_load_result` 用 `utf-8`,帶 BOM 的結果檔會被當成讀不到。

三點都只是輸出和邊界行為對不齊,結構一致,所以合成一條。

**問 3:第二種做法**
- **材料分份與份清單**:跟盲判不同。盲判每次重算、不留狀態(`scripts/lumos:77690` 附近,`--part` 重新挑段)。choice-layer 另外寫份清單與每份的雜湊,`--part` 從清單取。這跟 reread-prepare 在工作目錄寫清單檔的做法同一路,也有既有的 `_choice_cov_prune` 先例,我不判為另立一套。份的大小另有位元組上限,超過就改附段名清單、正文另存,這是盲判沒有的需求。
- **引句比對**:直接用 `_kt_sit_quote_norm`(`scripts/lumos:76246`),`_choice_layer_quote_in` 只是薄包裝,沒另寫正規化。
- **判讀檔寫法**:用 `_note_audit_write_verdict`,沒另寫原子寫入。
- **子命令註冊與說明表**:`HELP_WHEN` 一筆、argparse `add_parser` 緊跟 choice-kill、派發進 `_main_choice_cmds`,跟 choice-kill、choice-points 一致。
- **推送閘子原因**:`_CHOICE_PUSH_REASONS` 把「存活」拆成 `_CHOICE_PUSH_SURV`,`_CHOICE_PUSH_FIX` 每個子原因一句,沿用既有的 `by[原因]` 分桶,沒有另立判定路徑。

⚠ 判讀工作目錄的 14 天清檔(`_choice_layer_prune`)跟 `_note_audit_work_dir` 內建的 14 天清檔是兩份實作,只是範圍不同(後者只清上層的 `*.md`)。choice-kill 那邊的 `_choice_cov_prune` 已經是這種「各清各的子資料夾」的先例,所以我沒列成 finding,交編排者決定要不要統一成一支。

不對齊共 2 條,其中 major 0 條
