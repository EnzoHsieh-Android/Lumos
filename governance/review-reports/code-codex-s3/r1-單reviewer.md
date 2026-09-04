# code-codex-s3 r1 單 reviewer 報告

審的是 `governance/review-reports/code-codex-s3/r1-snapshot.patch`(commit `761ddf8`)。所有 finding 都用該 diff 對應的原始版本(不是本機工作樹——工作樹已有另一輪未 commit 的修正,見文末〈附註〉)直接跑 `scan_codex_file`/`classify_bash`/`run_one_codex` 重現,不是憑讀碼猜測。

---

## Finding 1 — 同輪兩次 developer 注入會共用同一個 apply_patch 錨點(跨注入誤配)

severity: major
blocking: 否
file: `governance/eval/lens-utilization/recount.py:283`(對應 diff 內 `scan_codex_file` 的錨定迴圈)

引句:「anchor, target, fallback = None, "", None」

具體失敗場景:同一輪(兩個 user 邊界之間)如果連續發生兩次 hook 注入(例如兩次 Edit 各自觸發一次 PreToolUse,但第二次注入之後 session 提前結束、沒有再呼叫 apply_patch),第一次注入正確錨到它自己後面的 apply_patch;第二次注入往後找不到任何 apply_patch,退而往回找,抓到的卻是「已經被第一次注入認領走」的同一個 apply_patch。我用兩則注入(dev1 釘 `Systems/a.md`,dev2 釘 `Systems/b.md`)+ 中間只放一個 `apply_patch` 呼叫(目標 `src/A.py`)重現:兩列 row 的 `file` 都印成 `src/A.py`——dev2 那列本來跟 `src/A.py` 完全無關,卻被算成「注入後有沒有讀 `Systems/b.md`」是以 `src/A.py` 那個編輯點的前後文去判定,錯置了因果。這個問題不是「先往後找/先往前找」順序造成的(工作樹另一輪已把順序改成取最近距離,但同一場景重跑仍然錯置,因為兩次注入本來就只剩一個 apply_patch 可搶)。目前兩支新測試都只放單一 developer 注入,沒有任何 fixture 覆蓋這個情境。

---

## Finding 2 — 節點名稱只取 basename 比對 stem,產生跨目錄假陽性

severity: major
blocking: 否
file: `governance/eval/lens-utilization/recount.py:220`(diff 行:`for t2 in terms:` 起的三行)

引句:「base = t2.rsplit("/", 1)[-1]」

具體失敗場景:`classify_bash` 把 `lumos show <路徑>` 的路徑一律砍到只剩檔名去比 stem。若某輪釘住的節點是 `Systems/bar.md`,而模型當時其實跑的是 `lumos show 別的資料夾/bar.md`(不同檔案,只是恰好同名,或甚至是打錯路徑、根本不存在的節點),`classify_bash` 仍會回傳 stem `"bar"`,`scan_codex_file`/`scan_file` 用 `stems` 字典(同樣只用 basename 去掉副檔名當 key)一比對,就把這一列判定成「讀到了 `Systems/bar.md`」。我用 `classify_bash('python3 scripts/lumos show Elsewhere/bar.md', slug)` 直接重現:回傳的 `lumos_terms` 含 `"bar"`,對到 pins `["Systems/bar.md","Other/qux.md"]` 建出的 `stems` 後,`hit_read` 直接判給 `Systems/bar.md`——即使命令列上的路徑寫的是 `Elsewhere/bar.md`。這是本次 diff 新加的行為(舊版只把原始 term 塞進 `lumos_terms`,不會做 basename 拆解,所以不會誤配);PR 說明自己承認「這會改 Claude 側既有報表數字」但只驗證了「原本漏算的變有算」,沒有針對「同名不同檔」做假陽性檢查。本機圖譜目前檔名不重複(用 `os.walk` 逐檔核對過),所以現有報表數字這次可能沒中獎,但這條路徑本身沒有任何防護,往後圖譜長大、出現同名筆記(不同資料夾)時會悄悄灌水。

---

## Finding 3 — 同輪內找不到 apply_patch 時仍會把任意 exec 呼叫當成已錨定,灌大分母

severity: major
blocking: 否
file: `governance/eval/lens-utilization/recount.py:298`

引句:「if anchor is None and fallback is not None:」

具體失敗場景:一次 hook 注入之後,如果同輪只有普通 `exec_command`(例如模型只是先查了一下,沒有真的呼叫 `apply_patch`),`_patch_target` 對每個 `custom_tool_call` 都回傳空字串,於是進 `fallback` 分支;搜完兩個方向都沒有合法 patch 目標,最後仍把 `fallback`(第一個非 patch 的 exec 呼叫)硬套成 `anchor`,`anchored` 印成 `True`、`file` 是空字串、`ftype` 判成 `"unknown"`。我用「dev 注入 + 一個只跑 `echo hi` 的 exec、同輪內完全沒有 apply_patch」重現:這一列仍然 `anchored=True`,而 `main()` 算 `denom`(分母)用的過濾條件是 `n_pinned>0 and ftype!="scratch" and anchored`——`"unknown"!="scratch"` 為真、`anchored` 為真,這一列就會被算進「有錨點、可信任」的分母,實際上它跟任何一次真正的程式碼編輯都沒有關聯。這會系統性地灌大分母,稀釋真正有意義的「注入後有沒有讀」統計。工作樹另一輪已經把這個 fallback 整段拿掉(改成同輪沒有 apply_patch 就 `anchored=False`),說明這條路的確被判定要修。

---

## Finding 4 — Codex runner 不檢查退出碼,timeout 只看「部分輸出裡有沒有出現期望指令」,可能把失敗場次判成通過

severity: major
blocking: 否
file: `scripts/scenario_probe.py:251`

引句:「except subprocess.TimeoutExpired as e:」

具體失敗場景:`run_one_codex` 呼叫完 `subprocess.run` 之後完全沒有看 `r.returncode`;`TimeoutExpired` 分支也只是把逾時前已經寫出的部分 stdout 拿去餵 `judge()`。我直接把 `subprocess.run` mock 成回傳 `returncode=2`(視同 codex 崩潰/被中斷)但 `stdout` 裡已經印出一行符合 `expect` 的 `lumos query` 指令,結果 `run_one_codex(...)["passed"]` 是 `True`;同樣把它 mock 成 `TimeoutExpired`(帶著同一行部分輸出)再跑一次,結果也是 `passed=True`。也就是說:只要 codex 在真正跑完前已經先印出了期望的那句指令,不管它後面是崩潰還是逾時,這一場都會被記成「通過」。這條探針的整個目的就是量測「Codex 會不會自己敲 lumos」,把儀器本身的失敗(逾時/非零退出)吃成成功結果,會系統性地美化 pass rate。

---

## Finding 5(minor)— `python/python3` 前綴辨識用 `endswith("lumos")`,會誤認其他腳本

severity: minor
blocking: 否
file: `governance/eval/lens-utilization/recount.py:200`

引句:「os.path.basename(args[0]).endswith("lumos")」

具體失敗場景:任何以 `python3 <路徑>` 開頭、且該路徑的 basename 剛好以 `lumos` 結尾但不是真正的 lumos CLI(例如 `scripts/notlumos`、`scripts/my_lumos`)都會被吃進這個分支,後面的 `show`/`context`/`contracts`/`search` 子指令跟著被誤判成「敲了 lumos」。我直接呼叫 `classify_bash('python3 scripts/notlumos show Systems/a.md', slug)`,`lumos_terms` 回傳 `{'Systems/a.md', 'a'}`——不是真正呼叫 lumos 卻被算進讀取證據。命中面比 Finding 1-4 窄(要求腳本檔名剛好無副檔名且以 `lumos` 結尾),但既然已經在改「認前綴」這件事,順手把判準收緊成 `== "lumos"` 成本很低。

---

## 一併記一句(不單獨列 finding)——Codex 與 Claude 兩種列的 `ambiguous` 欄位有無不一致

`scan_file`(Claude 路徑)的 row 一律在初始 dict 裡放 `"ambiguous": []`;`scan_codex_file` 只在 `if anchor is not None and pins:` 成立時才補上這個 key(`recount.py:308`)。目前 `main()`/`_render()` 都沒有讀這個 key,不會炸;但合併後的 `rows` 清單(連同 `--json` 輸出)兩種 harness 的 schema 不一致,之後如果有人要統一處理 `rows` 就會踩到 KeyError。沒有具體失敗場景,只記一句備查,不算 finding。

---

## 本案特定鏡頭:測試有沒有真的釘住行為

兩支新測試(`t_codex_s3_recount_codex`、`t_codex_s3_probe_codex_parser`)本身不是永真斷言——我把 `check()` 的斷言值跟直接執行 `scan_codex_file`/`tool_calls_from_codex_json` 的真實回傳值對過,兩者一致,測試會咬人。Fixture 形狀我用本機真的 `~/.codex/sessions` 逐字稿(0.144.1、cwd 落在本 repo 的稿子)交叉核對過幾個關鍵欄位:
- `session_meta.payload` 真的有 `cli_version`/`cwd`/`source`/`thread_source`/`session_id`,跟 fixture 一致。
- `custom_tool_call.input` 真的是 `const r = await tools.exec_command({cmd:"..."})` 這種 JS 字串,且 `cmd` 鍵有帶引號也有不帶引號的形狀,`_CX_CMD_RE` 兩種都吃得到(用真樣本現場測過)。
- `*** Begin Patch` 的 JS 變數包法(`const patch = "*** Begin Patch\n..."`)在真逐字稿裡也找得到,`_CX_PATCH_RE`/`_CX_HDR_RE` 對真樣本能正確解析出目標檔。
- 輪次邊界兩種型別(`event_msg/user_message` 與 `response_item/message role=user`)在真逐字稿裡都真實出現,`_is_boundary` 兩種都認得,不會跨輪誤抓 apply_patch(這點我用真樣本驗證過是對的,不是 finding)。

但測試的覆蓋範圍明顯不夠廣——沒有任何 fixture 覆蓋 Finding 1(同輪兩次注入)、Finding 3(同輪無 apply_patch 的 fallback)、Finding 4(codex 非零退出/timeout 但部分輸出已符合 expect)。這三個都是我用最小重現直接打中的路徑,測試綠燈不代表這些路徑是對的。另外,`response_item/message role=developer` 這個型別在真實(未接 lumos hook 的)Codex session 裡其實被拿來放好幾種不相干的系統訊息(permissions/skills/apps/plugins instructions),我在本機真逐字稿裡實際看到四則不同的 developer 訊息;程式碼靠「首行是否符合 `必看——`/`必看(合約...)`/`LUMOS-LENS range=`」這個嚴格判準去篩,這部分我核對過是對的、不會誤吃到那些系統訊息,但這也代表 role=developer 本身不是可靠的篩選依據,純粹是巧合命中——README 沒有講清楚這點是它的假設而非保證。

---

## 固定席逐條判定(LUMOS-IMPACT)

這份 diff 只動了 `governance/eval/lens-utilization/recount.py`、`governance/eval/lens-utilization/README.md`、`scripts/scenario_probe.py`、`scripts/test_lumos.py`(新增測試)。以下固定席都不是這幾個檔案的邏輯所在地,診斷結果一律「不影響」:

- `Systems/lumos-cli-lifecycle.md`(CLAUDE.md sentinel 冪等注入/保留)——不影響。這份 diff 沒有碰任何 CLAUDE.md 注入/re-inject 邏輯,`scripts/lumos` 本體完全沒改。
- `Systems/bound-tests-gate.md`(code-loop 對固定席綁定測試真跑)——不影響。這份 diff 沒有改 code-loop 的綁定測試執行邏輯,只是新增了兩支會被納入語料庫的測試函式本身。
- `Systems/canary-audit.md`(canary record/second 落盤與 telemetry-only)——不影響。diff 沒有碰 `lumos canary`/`.canary-log.jsonl` 相關程式碼。
- `Systems/guard-kill.md`(guard kill rc 優先序、`--json` 純淨)——不影響。diff 沒有碰 `lumos guard kill`。
- `Systems/slim-get-一行安裝.md`(三支 `.ps1` ASCII/無 BOM、不用 `$Args`)——不影響。diff 沒有碰任何 `.ps1`。
- `Systems/slim-install-安裝器.md`(CLAUDE.md 注入原地取代/冪等/FULL-BACKUP/manifest/三層守衛/Windows 直譯器與 shim 偵測)——不影響。diff 沒有碰安裝器程式碼。
- `Systems/slim-uninstall-一行卸載.md`(四步驟互不阻擋、manifest 基準、skill 目錄備份、CLAUDE.md 精確還原、`lumos.cmd` 獨立判斷、manifest 自清)——不影響。diff 沒有碰卸載器程式碼。
- `Systems/測試假綠形態.md`(修 bug 的回歸測試要有「現場真的被執行到」的前置斷言)——這份 diff 本身不是「修 bug 附回歸測試」的形態(是新功能的新測試),嚴格說不是這條 INVARIANT 的適用對象;但我借用同一個精神去檢查兩支新測試,確認斷言值都是我獨立重跑程式碼核對過的真實回傳值,不是照抄程式碼自我循環的假斷言——這點通過,但測試覆蓋的路徑明顯少於這份 diff 實際新增的邏輯分支(見上一節)。
- 其餘列名未展開的節點(`lumos-cli-read.md`、`design-loop.md`、`lumos-deinit.md`、`cochange-guard.md`、`check-r-guard.md`)——同樣不影響,這份 diff 完全不觸及這些系統的程式碼路徑。

---

## 總結

max severity: major(4 條:Finding 1-4)
blocking 條數:0(我對這份診斷用途、不寫治理帳、不影響任何 gate 的量測工具的判斷是 severity 高但不 blocking;若採用更保守的標準——量測工具本身的正確性就是這次交付的唯一目的——Finding 1/3/4 值得在合併前先補測試/修掉,不必卡 CI)

補充:governance/review-reports/code-codex-s3/ 目錄下已有另外兩份同輪報告(`r1-外家否決.md`、`r1-架構對齊.md`)。我是先重現完自己的結果才對照,`r1-外家否決.md` 的 finding 1(距離而非方向優先)、finding 2(fallback 錨點灌分母)、finding 3(returncode/timeout 假過)、finding 4(`endswith("lumos")`)分別對應到我這份報告的 Finding 1 前半(方向優先問題,但我額外指出即使改成最近距離、跨注入誤配依然存在)、Finding 3、Finding 4、Finding 5。Finding 2(basename 假陽性)在另外兩份報告裡沒看到,是我這份新增的。工作樹目前有一輪未 commit 的修正(`t_codex_s3_r1_fixes` 等),已經處理了「fallback 灌分母」「`endswith` 誤判」「單一注入時方向優先選錯」,但沒有處理跨注入誤配(Finding 1 完整版)、basename 假陽性(Finding 2)、returncode/timeout 假過(Finding 4)。
