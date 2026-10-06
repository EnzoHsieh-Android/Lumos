severity: major

席名:資安-r2-sonnet(攻擊者視角;材料 /tmp/code-capretro-r2.patch 全讀,真代碼查證)

逐類結論:
1. 不可信輸入流到危險操作:見 F1(寫檔跳出 repo)、F2(終端跳脫漏一處)。讀回顧檔(`_retro_read_bytes`)中間目錄是符號連結時會讀到 repo 外同名檔 cap-retro.json,但只讀固定檔名且內容仍要過驗證與指紋,拿不到別的檔內容,已看,無獨立攻擊路徑。`_retro_id_bad` 擋 `/`、`\`、控制字元、`..`,編號組路徑本身跳不出 `review-reports/`,跳出靠的是目錄本身是捷徑(F1)。
2. 繞過擋點:治理帳與審查帳本來就是未驗證的版控明文(誰能提交就能偽造 recorded/skipped 與 sha),這輪沒有新增繞過面;`_retro_has_dossier` 用 is_file 會跟隨捷徑,攻擊者本就能不放卷證來讓回顧「不適用」,已看,無新增。
3. 密鑰與個資:已看,無(新增程式不讀環境變數、不印路徑以外的本機資料)。
4. 雜湊:sha256 綁同一份已驗位元組(`--record` 與判定共用 raw),已看,無。
5. 執行邊界:新增程式與測試無 shell=True、eval、網路呼叫;無新依賴(hashlib、stat、shlex 皆標準庫)。已看,無。

### F1 --template --write 只擋最後一段捷徑,卷證資料夾本身是捷徑時在 repo 外建檔
severity: major
blocking: 是 — 跳出 repo 寫檔(新建、不覆蓋,檔名固定 cap-retro.json,內容含帳上 report_path/auditor 字串)
- 攻擊路徑:誰=提交 PR 的外部貢獻者;從哪=PR 內容(git 保留符號連結)——把 governance/review-reports/<編號> 提成指向 repo 外某目錄的符號連結,該目錄需有一個檔,帳上 report_path 寫 `governance/review-reports/<編號>/<該檔名>`,並在 docs/.canary-log.jsonl、docs/.governance-log.jsonl 附上到上限的多席列與 cap-decision 事件(帳本本來就隨 PR 提交);送什麼=上述 PR;維護者照 lumos 自己印的提示執行 `lumos loop retro <編號> --template --write`;拿到什麼=在符號連結指到的任意既有目錄(例如維護者家目錄下某個有檔的目錄)新建 cap-retro.json(0644,內容有攻擊者控的字串)。
- 走到哪一段:`_retro_has_dossier` 用 `d.is_dir()` 與 `(Path(root)/n).is_file()`,兩者都跟隨捷徑,判為「有卷證」;`cmd_loop_retro` 的 `os.open(... O_EXCL | O_NOFOLLOW ...)` 的 O_NOFOLLOW 只管最後一段檔名,中間的 `<編號>` 目錄是捷徑照樣解析。
- 壞在哪:O_EXCL 不覆蓋既有檔,所以只能「新建」,影響受限,但確實在 repo 外寫了檔;沒有任何一步檢查解析後的路徑仍在 repo 內。
引句:「fd = os.open(str(p), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o644)」
- 佐證行:file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:13005`(_retro_has_dossier);file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:12998`(_retro_dir 只做字串拼接,無 realpath 檢查)
- 重現(已實跑):/tmp/sec_r2_repro.py(在 scripts/ 下執行 `python3 /tmp/sec_r2_repro.py`,用測試的 `_cr_repo/_cr_loop/_cr_decide` 造帳,把卷證資料夾換成指向 tempdir 的符號連結)輸出 `0 ✓ 已建回顧檔骨架:governance/review-reports/crx/cap-retro.json`,且 `os.listdir(<repo 外 tempdir>)` 含 `cap-retro.json`。
- 修法方向:寫檔前要求 `os.path.realpath(dir)` 仍在 realpath(root) 之下,或用 dir_fd + O_NOFOLLOW 逐段開(O_DIRECTORY|O_NOFOLLOW)。

### F2 cap-decision 成功訊息把帳上輪次 id 原樣印到終端(終端跳脫漏一處)
severity: minor
blocking: 否 — 只能對終端注入控制序列,不寫檔不改判定;需維護者在含惡意帳的 checkout 上跑 cap-decision
- 攻擊路徑:誰=PR 貢獻者;從哪=docs/.canary-log.jsonl 某列的 round 欄位(字串即可通過 `_retro_ledger_rounds`);送什麼=`"r1\u001b]0;PWNED\u0007\u009b2J"` 這種含 OSC/CSI(含 8 位元 C1)的輪次 id;拿到什麼=維護者跑 `lumos loop cap-decision` 成功後,終端收到原樣的 ESC/OSC/C1 序列(改標題、清屏、部分終端的 OSC 52 寫剪貼簿)。
- 壞在哪:同一支函式其他訊息都過 `_esc_clean`,唯獨這行 `', '.join(rounds)` 沒過;同輪修補宣稱涵蓋所有印帳上內容處,這處漏了。`--template`(不加 --write)印到標準輸出的 JSON 用 ensure_ascii=False,C0 會被 json 跳脫,但 U+0080–U+009F 的 C1 不會,ctx 內 report_path/auditor 同理原樣出現(同根因,縱深防禦)。
引句:「print(f"✓ 已記人裁:{_esc_clean(loop_id, 60)} {decision}(帳上輪次 {', '.join(rounds)})")」
- 佐證行:file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:13545`
- 重現(已實跑):/tmp/sec_r2_b.py 輸出 stdout 為 `'✓ 已記人裁:crx extra-round(帳上輪次 r1\x1b]0;PWNED\x07\x9b2J, r2, r3)...'`(repr,含原始 ESC 與 0x9b)。
- 修法方向:該行輪次清單過 `_esc_clean`;template 的 stdout 輸出也過一次 C1 清除或改 ensure_ascii=True。

總結:最嚴重 major,blocking 1 條
