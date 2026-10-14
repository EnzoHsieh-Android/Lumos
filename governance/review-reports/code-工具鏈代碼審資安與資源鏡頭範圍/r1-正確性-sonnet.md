severity: clean

我讀完 patch 裡 `scripts/lumos`、`scripts/test_lumos.py`、`templates.md` 與筆記,並在 `/tmp` 的乾淨 clone(HEAD 47781636)實跑。沒有 finding。

**`loop next` 的鏡頭範圍行**
- 條件:`str(loop_id).startswith("code-")` 才判。
  - 設計審編號不印。
  - 無連字號的 `codelens9` 這類舊編號也不印。
  - 兩者 JSON 的 `lens_scope` 都是 `default`。
- root 取法:`Path(repo).resolve() if repo else _vault_repo_root(env)`,與同一函式內 `reviewed_spec` 和 `_fix_check_status` 的算式一致。
- 判別:`_is_toolchain_repo` 看根下有沒有 `skills/lumos-project-notes/SKILL.md`。這個鍵沿用既有慣例。我查了 `_VENDORED_TOOLKIT` 與相關註解,沒看到安裝流程把這支檔複製進消費專案。
- try 包法:算 root 與判別在同一個 `try`,例外一律落到 `default`,不改退出碼。
- 位置:放在 `emit()` 內的共用路徑,在 `roster` 與 `roster_note` 兩個分支之後、`reviewed_spec` 之前。
  - 所有 phase 都經過這裡。
  - 提早 `return 2` 的擋下路徑不會印。
- 實跑:在工具鏈 clone 內跑 `lumos loop next code-foo --tier high`,最後一席之後緊接印出該行。加 `--repo /tmp` 則不印。

**8 支新測試**
- 在 clone 跑 `python3.14 scripts/test_lumos.py -k lens`:1072 passed、0 failed、2 skipped(來源 repo 專用)。
- 對照計劃條款 S1 到 S6、S9、S10 逐條讀過,沒有照綠卻沒守到的。
  - S1(`code-` 編號、`--repo` 指到工具鏈目錄):預期行逐字取自計劃,比對「緊接最後一席」與「消費專案拿掉那一行後逐字相同」。
  - S2:前置先證明夾具真是工具鏈 repo,再比設計審編號與 `codelens9`。
  - S3:把 `_vault_repo_root` 換成丟例外的版本,文字與 JSON 兩種輸出都與消費專案相同。
  - S9:規則原文獨立寫在測試裡,不從範本抽;有「找得到 6 份加 §5、§6」的前置,兩個變異(整句拿掉、少一個禁用寫法)都會點名到對的那一份。
  - S4:`_SEC_SIX_CLASSES_ORIG` 與改動前 `templates.md` 的原文一致。

**範本搬動**
- 我用 `git show` 取出 base 版 `templates.md` 的 §7.8 圍欄,抽出原六類,與新 `### 消費專案六類` 內文比對,結果一致,包含結尾的「另看這次新加的依賴」那行。
- 既有的 `t_templates_security_seat_section`(查 `攻擊路徑`、`不報`、`真能用的憑證`、`資安-<模型>`、`推論`)與 `t_role_cards_marker_absent_from_arch_and_security` 仍有鑑別力,而且都綠。
- §5、§6 為了讓規則落在「第二行」,把原本折成兩行的第一句併成一行,語意不變。
- 全 repo 除 `templates.md` 外沒有別處產生 `LUMOS-SEAT:` 派工詞。
- §3 圍欄原句 `_IDEMP_ORIG` 一字不少,替換句寫在圍欄前的須知,符合 d3。

**資料狀態五問**
- `lens_scope` 是現算的輸出欄位,不寫帳。
  - 新舊互讀:舊帳照讀,舊版 lumos 讀不到該欄位只是缺欄。
  - 寫一半、衍生資料、時間、不可逆:都不適用。
- JSON 多一個欄位屬純新增。現有 `loop next` 相關測試都綠,沒有被欄位數卡住的斷言。

**弱點備註,都不達 finding 門檻**
- S10 的 ② 用 `split("### §3 編排者派工前須知")[-1]`。標題改名時它會退成搜整段 `pre`,仍可能綠,但那行本身的內容還是會被比對。
- S4 ⑥、⑦ 是子字串存在檢查,只守「有寫」,不守語意。

最高等級 clean,blocking 0 條。

主要檔案(都在 `/Users/enzo/orca/workspaces/lumos-toolchain/lens-scope-rule/`):
- `scripts/lumos`:`_LENS_SCOPE_TOOLCHAIN_LINE` 在約 16154 行,`emit()` 內的接線在約 16427 到 16449 行。
- `scripts/test_lumos.py`:新增的 8 支測試在約 96305 行之後。
- `skills/lumos-design-loop/templates.md`:§0、§3 須知、§7.7、§7.8。

我實跑用的臨時 clone 在 `/tmp/lumos-seat-work/code-工具鏈代碼審資安與資源鏡頭範圍/正確性-sonnet/`,尚未刪除。
