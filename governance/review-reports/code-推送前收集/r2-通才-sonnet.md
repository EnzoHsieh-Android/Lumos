severity: minor

通才回歸席報告。我沒找到會弄壞既有功能的問題,只有一條 minor。

**已讀,無 finding 的部分**
- **不帶 `--keep-going` 的 `code-loop check` 輸出**:我在共用 clone 裡用改動前(`e0da694b`)和改動後的 `scripts/lumos` 各跑一次,比對輸出與離開碼。四段範圍、文字與 `--json` 兩種輸出,結果逐行一致。這四段全判成 tier=light,所以沒走到「擋下」的路徑。擋下路徑靠既有測試補:`-k code_loop` 94 個全過、`-k keep_going` 42 個全過。
- **`_CodeloopKg` 抽出後 `_codeloop_guard_verdict` 的行為**:
  - 我逐道對照舊程式和新程式:合約測試(含 `bound_advisory` 重跑)、表態、新增告警、pitfalls 失敗時新增告警閘照跑、`kg.tier` 的設定時機。語意都等價。
  - 函式裡沒有殘留的 `blocks` 或 `seen` 引用。
  - `_sys`、`graphctl`、`_json`、`_sp` 在後面的表態那段仍有使用,不會變成沒用到的變數或匯入。
- **兩條 C901 的 lint-waive 理由成立**(用 `ruff --select C901 --config 'lint.mccabe.max-complexity = 10'` 量):
  - `_codeloop_guard_verdict`:改動前 35、改動後 32。
  - `cmd_code_loop`:改動前 53、改動後 26。
  - `.lumos/lint.json` 用的規則集(`F,B,ASYNC,RUF,DTZ,E7,E9,C901`)掃改動前後,新增的告警只有這兩條。它們的身分是定義那一行的片段,兩支定義行確實都多了 `keep_going` 參數。
  - 注意:`.lumos/lint-waivers.json` 就在 repo 裡,但你指的 `governance/lint-waivers.jsonl` 不存在,我讀的是前者。
- **`lumos enforcement` 與上線標記**:
  - `lumos enforcement` 對掛鉤只檢查回頭重讀有沒帶 `--gate`,這次沒動到;`-k enforcement` 68 個全過。
  - `scripts/lumos` 裡的上線標記字串有 `note-audit check`、`note-audit reread-check`、`drift check`、`home check --staged`,掛鉤修補都沒動到這幾串。
  - 拿掉 `code-loop check --help` 探測後,「中斷就停」清單同步刪了那一列,`pre-push` 的 bash 3.2 語法檢查通過。
- **既有掛鉤測試**:`-k prepush` 270 個全過,另有 `-k cl_reason` 3 個、`-k push_summary` 11 個全過。
- **掛鉤各項修補**:
  - `tee … >&2 2>/dev/null` 的重導向順序正確;留底檔寫不進去時,輸出仍會印出來(我用 `/bin/bash` 實測)。
  - `run_group` 在 `( … ) &` 子殼裡執行,新加的 `trap … TERM` 不會蓋掉主殼的陷阱。
  - `elif` 接在 `if` 的註解之後,語法沒問題。
  - log 檔搬進 `$_PP_TMP`、紅時用 `pp_keep_log` 搬出來,這條路沒有漏洞。
- **`push-summary`**:`_note_audit_root` 取代 `Path.cwd()` 之後,不在 git 專案又沒帶 `--repo` 時改回 2。掛鉤一律帶 `--repo`,而且回非零會落到簡版彙總,所以掛鉤不受影響。

severity: minor
blocking: 否 — 純粹是多餘的欄位,不影響擋不擋,也不影響輸出。
引句:「"summary": _CODELOOP_BLOCK_KIND_REASONS.get(b.get("reason_kind"), _CODELOOP_BLOCK_KIND_FALLBACK)」
問題:`--keep-going` 的 JSON 現在每筆 `blocks` 都帶 `summary`,並新增 `_CODELOOP_BLOCK_KIND_REASONS` 這張表。但掛鉤只讀 `LUMOS-BLOCKS:` 那一行,理由用它自己寫死的 `pp_cl_reason`,整個 repo 沒有任何程式讀 `summary`(`scripts/lumos` 裡其餘的 `"summary"` 都是筆記欄位)。
具體失敗情境:兩份表現在靠測試 `t_prepush_cl_reason_table_matches_lumos` 逐字綁在一起,是為了一個沒人讀的欄位,以後改文案要同步改兩處。這不會出錯,只是多維護一份。要麼讓掛鉤真的用它,要麼拿掉。
佐證:`scripts/lumos:51244`(表)、`scripts/hooks/pre-push:136`(`pp_cl_reason`)

最高等級是 minor,blocking 共 0 條。

我的實驗目錄已刪。`pp_keep_log` 在測試紅時會在 `$TMPDIR` 留一份 log,這是設計如此,不算 finding。
