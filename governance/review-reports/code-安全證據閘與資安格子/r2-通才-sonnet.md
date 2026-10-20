severity: major

審查範圍:修補差異 `r2-repair-tests.patch`,以 detached worktree 在 7655a12d 跑測試並做翻紅檢查。`-k secev_r1` 134 條全綠,`secev_s2`、`secev_s5` 共 106 條全綠,另有 `secev_s01`、`secq_s08`、`secev_s59`(後兩者以 `-k` 前綴跑,各 12 條)全綠。全套沒跑。

## 1. S13 數值測試:改壞「入口 open 格數」的算法照綠
severity: major
blocking: 是

引句:「check("S13 數值 護欄數 1、入口 open 格數與全庫 open 數等於格子清單數出來的值",」

壞在哪:測試用的 vault 裡,入口 open 格數(`want_mine`)和全庫 open 數(`want_all`)都是 18,兩個值分不開。`_spec_gate_security_line` 計算入口 open 格數時,只有「護欄引用到的入口」該算進去。測試的資料讓每個入口都落進去,所以這個限制根本沒被驗到。

重現(在 detached worktree 裡):
- 把 `scripts/lumos:14571` 的 `c["surface"] in surf and` 拿掉,清 `__pycache__` 後跑 `python3.14 scripts/test_lumos.py -k secq_r1_s13`,結果 `2 passed, 0 failed`,仍全綠。
- 另外在測試裡加印,得到 `DBG13 18 18`。
- 這條測試只釘「兩個數字等於格子清單數出來的值」,抓不到入口過濾被改壞。
- 修法:加一個不被護欄引用的入口(它的格子是 open),讓入口 open 格數小於全庫 open 數。

歸因:未判定。這條測試是這輪新加的,修前版本沒有對應測試。

## 2. 人機區分測試:只留 stdin 檢查,測試照綠
severity: major
blocking: 是

引句:「check("人機區分 非互動 → 擋下、說要本人在終端機跑、給可複製指令、不寫入」

壞在哪:合約和 docstring 寫「stdin 與 stdout 都要是互動終端」。測試只跑了兩種組合:
- 兩者都不是終端(`stdin=DEVNULL`,stdout 用 pipe 擷取)
- 兩者都是終端(pty)

「stdin 是終端、stdout 被導向 pipe」這個相鄰組合沒測。

重現:把 `scripts/lumos:11406` 改成 `if not (sys.stdin.isatty()):`,清 `__pycache__` 後跑 `python3.14 scripts/test_lumos.py -k secev_r1_approval_add`,4 條全綠。守衛被弱化一半,測試抓不到。

歸因:未判定。這條測試是這輪新加的。

## 3. `_sg_pty_run` 不守自己的 timeout,child 不會被收掉
severity: minor
blocking: 否

引句:「def _sg_pty_run(argv, answer, cwd=None, timeout=60):」

壞在哪:迴圈因為 timeout 結束後,程式直接 `waitpid(pid, 0)`,沒有 kill child。如果提示字串改了、沒出現「確認碼:」,child 會一直等輸入。測試要等整支測試的 180 秒上限才失敗,還會留下孤兒程序,而不是快速紅燈。

重現:`_sg_pty_run(["/bin/sleep","12"], lambda c:c, timeout=2)` 實際跑了 12.0 秒才回來,回傳 `(0, '')`。

附帶:`execv` 失敗時,child 沒有 `os._exit` 保護,會往上跑進測試 runner,有重複執行測試的風險。這點沒有實際重現,標 ⚠。

## 4. 「主線候選」測試的前置斷言太鬆
severity: minor
blocking: 否

引句:「check("主線候選 前置:分支不刪 → 放行、主線是本機 main", not rep["blocked"] and "main" in rep["mainline"]["how"]」

壞在哪:`"main" in how` 對 `refs/remotes/origin/main` 也成立,所以前置斷言證明不了「主線選到的是本機 main」。

後半段的翻紅斷言沒有問題:我把 `_secev_mainline_pick` 改成固定取第一個候選,「分支刪掉護欄 → 照擋」那條就紅了。

建議:前置改成比對主線 sha 等於本機 `main` 的 `rev-parse`。

## 5. 效率與重用
severity: minor
blocking: 否

引句:「def t_secev_r1_s55_mainline_row_really_judges():」

兩個問題:
- `t_secev_r1_s55_mainline_row_really_judges` 與 `t_secev_r1_tool_rename_is_weakening` 重複搭同一組 fixture,可以抽成共用 helper:
  - 「10 個請求的 k6 報告」(`low`)
  - 控制項 C2
  - `_SG_K6_TOOL`
  - 提交後分支調低下限
- 慢的測試:`t_secev_r1_type_gate_fence_and_reports` 要 37.6 秒,`t_secev_r1_s18_revision_real_push` 要 33.0 秒,離 180 秒上限約 5 倍餘裕。前者在同一支裡建了十幾個 repo,拆開或共用 repo 可以降低風險。

## 6. golden 的重產程式沒有任何測試守,README 描述與檔案結構對不上
severity: minor
blocking: 否

引句:「重產:把那一版的 `scripts/lumos`、`scripts/test_quality*.py` 抄到一個暫存目錄」

壞在哪:
- `_sg_golden_capture` 與 `_sg_golden_capture_s8` 只存在於測試檔裡,沒有被任何測試呼叫。我手動對 d42840cf 版跑,S1、S59 的輸出與 golden 逐字相同;S8 我沒跑完。所以目前是正確的,但之後沒人守它。
- README 說 `plan_text` 是「另加」的頂層鍵,實際上它在 `s8.plan_text` 底下。
- golden 把 `pitfalls` 的整段 stdout 與每個階段的 JSON 逐字凍結。之後任何合法的改動都會讓它紅,卻沒寫退場條件。
- 專案 CLAUDE.md 規定:「承認風險要附回頭看的條件」,可以補一行 `RETIRE-IF` 或 `REVISIT`。

## 三問的答案
- ① 原問題的修復效果有哪些行為證據:
  - 型別閘、tree_too_large、主線設定不從被推提交讀取、主線候選全參與、`approval_backdated`、`rename_is_weakening` 等都有前置加翻紅的結構,134 條全綠。
  - 其中我只對「主線候選挑第一個」實際翻紅過:該測試翻紅,但它的前置斷言太鬆(見第 4 條)。
  - 對共用檔額度只算一次的 S41:單獨去掉兩層去重中的任一層,測試仍綠;兩層同時去掉才會紅。測試真有咬到,但單層回歸抓不到。
  - 其餘修補我沒有逐一翻紅,範圍內未驗。
- ② 修補處的正常、錯誤與相鄰路徑是否仍成立:
  - `use_relative_dates` 與 `add_entry` 預設日期的改動,舊的 S2x、S5x 共 106 條仍綠。
  - S1、S8、S59 的 golden 保住了「跟改動前逐字相同」,但 S1 與 S8 都只驗到 `merge-base == HEAD` 的早退路徑,S8 也失去了原本在真實圖譜 repo 裡跑的涵蓋。
  - 相鄰路徑沒被測到的:第 1、2 條。
- ③ 新發現的同一案例在修前、修後各是什麼結果:都是這輪新加的測試,沒有修前版本可比,歸因都標「未判定」。

最嚴重 severity:major,blocking 共 2 條。

relevant 路徑:
- `/Users/enzo/orca/workspaces/lumos-toolchain/security-gate/governance/review-reports/code-安全證據閘與資安格子/r2-repair-tests.patch`
- `/Users/enzo/orca/workspaces/lumos-toolchain/security-gate/scripts/lumos`(`_secapr_confirm_human`、`_spec_gate_security_line`、`_secev_mainline_pick`)
- `/Users/enzo/orca/workspaces/lumos-toolchain/security-gate/scripts/test_lumos.py`

我用的 detached worktree 和暫存的舊版目錄已刪,`/tmp` 底下沒留下 gctl 暫存。
