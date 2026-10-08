severity: minor

# 第 3 輪(末輪)併發資源席報告

審查範圍:/tmp/code-tail-r3.patch 全文(計劃與筆記 5 篇、scripts/lumos、scripts/test_lumos.py、skills 一篇)。實驗都在 scratchpad 的複製目錄(e3、e4)做,沒動 repo。
基線:複製後跑 `-k ns_append`(88 案)、`-k ns_nfc`、`-k note_audit_dispute`、`-k gate_event_fit` 全綠;本席找到的問題都是這些測試沒蓋到的角落。

先講結論:這輪沒有找到 major 以上的洞。上一輪的修法在「總量上限回 cap、位元組總和、NFC 並存、申訴分範圍」這幾條上方向都對,而且我試著把候選塞滿、把大檔塞滿,記憶體峰值都被 32 MiB 的總和上限壓住。下面五條都是修法自己帶來的小副作用。

## 發現

**K1 回頭條件兩條規則也被一起停止扣減,跟計劃〈做法〉2 還在寫的「鍵(規則, 改法)」對不上**
severity: minor
blocking: 否 — 只會多擋(偏嚴),擋下訊息講得清楚,作者把舊 REVISIT 行本身修好就過;但行為跟計劃現文互相矛盾,且 `_ns_viol_key` 的 `_NS_REVISIT_RULES` 分支變成死碼
引句:「if v[2] not in _NS_FRAG_KEY_RULES:」
佐證: file: `scripts/lumos:27694`(`_NS_REVISIT_RULES` 仍在)與 file: `scripts/lumos:27930`(`_ns_revisit_violations`)
1. 輸入:起點版本有一行 `REVISIT:以後再說這件事情`(第一個位置不是日期,舊帳,本來就犯「回頭條件格式不合」),作者只在句尾補 `(更正:補一句說明 [來源:人工])`。
2. 走到 `_ns_append_subtract`:新判準只認 `_NS_FRAG_KEY_RULES`(行號引用、釘版本),「回頭條件格式不合」「條件寫錯」不在裡面,直接 `keep.append(v)`,舊行本來就有的這條違規被當成新寫。
3. 我在複製目錄用 `_tail_repo(body=old)` 加 `_tail_try(root, body=old + "(更正:…)")` 實跑:rc=1,輸出 `回頭條件格式不合 REVISIT:以後再說這件事情(更正:…)`;`REVISIT:[when-file:src/x.py] 之後處理這個` 補括號同理,rc=1、報「條件寫錯」。把判準改成 `_NS_FRAG_KEY_RULES + _NS_REVISIT_RULES` 兩個探針都 rc=0,證明就是這一行造成。
4. 為什麼說不是刻意:這兩條只讀行首標記(`_ns_revisit_violations` 的 `_revisit_split(probe)`),句尾補括號不可能讓它們的判定改變,N 與 O 的違規必然相同,扣減不會被拿來借債;只有「條件寫在不評估的地方」(括號裡可新增標記)才有借債風險。r2 的 SEE 與不評估兩條才是要收的,這一刀砍到了鄰居。
5. 文件矛盾:計劃 `舊行尾追加不算新寫_計劃.md` 〈做法〉2 末條(patch 第 102 行,本輪沒改)仍寫「`_ns_revisit_violations` 對 N 與 O 各算…鍵(規則, 改法)」;天花板 1 又寫「整行層級的規則也不扣」。新增的 [S47] 測試只蓋 SEE 與不評估兩條,沒有蓋這兩條。

**K2 放寬帳改用(路徑, 行號)去重:兩條分支的同一個行號、不同內容,第二條被整筆吞掉,「只多記、不少記」這句不成立**
severity: minor
blocking: 否 — 只影響放寬帳的筆數(RETIRE-IF 與 REVISIT:2026-12-01 要數的就是這個),不影響任何擋與放的判定
引句:「fin = {k: r for k, r in (relaxed.get("by_line") or {}).items() if k not in seen}」
佐證: file: `scripts/lumos:29531`
1. 輸入:同一次推送(同一個 `LUMOS_PUSH_ATTEMPT`)兩條分支從同一個起點分出,各自在同一篇 `A.md` 的第 14 行補不同的括號(兩個不同提交)。
2. 走到 `_ns_relaxed_record`:第一條分支記了 `[["…/A.md", 14]]`;第二條的 `fin` 是 `{("…/A.md", 14): […]}`,被 `k not in seen` 整筆濾掉。舊版鍵含起點、終點與配對,不會吞。
3. 實跑(複製目錄,`_tail_repo` 後 `checkout -b br1` / `br2`,各補一段不同括號,同一個 att 各跑一次 `--diff base..tip`):兩次都 rc=0,`state=done` 的 relaxed 事件只有 1 筆(head_sha 只有 br1 的),第二條分支的放寬完全沒帳。
4. 計劃〈做法〉5(patch 第 122 行)寫「帳裡 pairs 被裁掉的行會再記一次(只多記、不少記)」,K2 是「少記」的反例;[S48] 的測試只用「同一條線上延伸的兩個範圍」,沒蓋「不同線、同行號」。

**K3 `pairs` 被 4 KB 裁掉後,去重只認得到留下的那幾十筆:同一個範圍重跑會反覆再記,條數重複計入**
severity: minor
blocking: 否 — 只多記,不影響判定;計劃第 122 行已承認「被裁掉的行會再記一次」,但 [S46] 的「應只記一筆」沒跟著改,而且不是記一次,是每跑一次就再記一批
引句:「got.update(tuple(x) for x in d.get("pairs") or [] if isinstance(x, list) and len(x) == 2)」
佐證: file: `scripts/lumos:29507`
1. 輸入:200 行舊句各補括號(都帶一個行號引用),同一個 att 先跑 `base..mid`、再跑兩次 `base..tip`(範圍重疊)。
2. 走到 `_ns_relaxed_recorded`:帳上每筆事件的 `pairs` 被 `_gate_event_fit` 裁到約 85 筆,`seen` 只有這 85 筆;其餘行每次都算「沒記過」。
3. 實跑結果:`relaxed` done 事件 3 筆,`(violations, 留下的 pairs, pairs_total)` 分別是 (200, 87, 200)、(113, 85, 113)、(28, 28, 28)。第三次跟第二次是完全一樣的呼叫,仍多記一筆。真實只有 200 行,帳上加總 341 條。
4. 影響:一次清舊筆記補上百行括號的人,多分支或重試推送時,放寬帳的 `violations` 加總會膨脹;REVISIT:2026-12-01 要「數近八週筆數」,筆數與條數都被灌水。舊版的鍵是整張清單的雜湊,這一點上舊版反而是冪等的。

**K4 只判句尾的申訴對「已有整行 CODE 判定」的項目完全無效,而且申訴照收、不報錯**
severity: minor
blocking: 否 — ⚠ 只做到單元層級重現,沒跑通整條真實推送;作者另有出路(用一個配不上對的範圍重新 prepare 出整行申訴,或直接改掉那行),不是死路
引句:「got = [m[k] for k in {None, row.get("tail")} if k in m]」
佐證: file: `scripts/lumos:29998`(`_note_audit_dispute_for`)、file: `scripts/lumos:30052`(`_note_audit_class_for` 對帶 tail 的項目取整行與句尾的最重)
1. 輸入:判定檔 v1 對內容編號 X 記了整行判定 CODE(例如當時範圍配不上對,整行送審);之後換了範圍(例如總量上限解除、分次推送),X 變成「帶 tail 的項目」,作者依現在的清單 prepare 申訴,申訴列帶 `tail`(`_note_audit_scoped_row` 會帶)。
2. 走到 `_note_audit_dispute_for`:申訴有 tail,只換 `tail` 相同的判定列;整行的 CODE 列(tail=None)不動。再走 `_note_audit_class_for`,帶 tail 的項目取「整行判定」與「同 tail 判定」的最重 → 仍是 CODE。
3. 重現(複製目錄,直接呼叫):`docs={"v1.json":{"kind":"判定","rows":[{"id":"X","class":"CODE"}]},"a1.json":{"kind":"申訴","disputes":"v1.json","rows":[{"id":"X","class":"CONTEXT","tail":"0123456789abcdef"}]}}`,`_note_audit_class_for(_note_audit_fold_scoped(docs), {"id":"X","tail":"0123456789abcdef"})` 回 `CODE`。
4. 壞在:r1 的「申訴不分範圍」會讓這個申訴生效,r2 為了不讓句尾申訴蓋整行 CODE(正確的目標)連帶讓「對整行 CODE 申訴、但清單已是句尾範圍」變成靜默無效。新測試 [S50] ①②只驗了「項目沒帶 tail」與「同 tail」兩種,沒蓋「整行 CODE + 項目帶 tail + 句尾申訴」。

**K5 每次推送都無條件讀一次治理帳尾(最多 24 MB),即使這次沒有任何放寬可記**
severity: minor
blocking: 否 — 量測下每次約 0.25 秒、尖峰多約 60 MB,不會壞事,但是純粹可省的成本,而且「一次推多條分支」會逐條乘上去
引句:「seen = _ns_relaxed_recorded(root, os.environ.get("LUMOS_PUSH_ATTEMPT", "").strip())」
佐證: file: `scripts/lumos:29531`、file: `scripts/lumos:3530`(`_GOV_TAIL_CAP = 24 * 1048576`)
1. 輸入:推送前掛鉤(`LUMOS_PUSH_ATTEMPT` 一定有)跑 `note-shape --diff`,筆記沒有任何補括號的行(`by_line` 為空,`capped` 假)。
2. 走到 `_ns_relaxed_record`:`relaxed` 在推送模式是 `_ns_relaxed_settle` 填過鍵的字典,為真;`seen = _ns_relaxed_recorded(...)` 在 `if fin:` 之前無條件執行,整段 `_gov_tail_bytes` 讀檔、decode、逐行 `json.loads`。
3. 實測(複製本 repo 的 16.7 MB 治理帳,直接呼叫 `_ns_relaxed_recorded`):0.25 秒、最大常駐 107 MB;帳到 24 MB 上限時約 0.35 至 0.4 秒。每條分支一次。
4. 修法一行:`by_line` 為空就不讀(`if not relaxed.get("by_line"): 略過`),或把 `seen` 的讀取移進 `if` 內。

## 固定席節點

逐條判這份 diff 對牽連節點宣稱的行為或合約有沒有破壞。

- Systems/reversibility-governance-ledger(風險席):該篇宣稱放行不寫帳、只有少數例外。本輪新增 `capped` 狀態的 relaxed 事件,仍然只在推送模式、且只在配對表真的被叫用(有違規要扣)時才記,沒有擴大「放行也寫帳」的範圍;事件走既有 `_gate_event_or_warn`。去重改讀帳(K2、K3、K5 是這裡的副作用),對「擋人一定有帳」的承諾沒有影響。判不破壞。
- Systems/lumos-cli-read(search 預設排除 superseded 不排除 stale):diff 沒碰 search、索引、濾網。判不影響。
- Systems/bound-tests-gate:本輪新增測試 `t_ns_append_line_rules`、`t_ns_append_ledger_dedupe`、`t_ns_nfc_clash_errs`、`t_note_audit_dispute_scope`,計劃的 [S47] 至 [S50] 綁到它們;本席複製後 `-k ns_append`、`ns_nfc`、`note_audit_dispute` 都真跑過且存在、全綠,沒有懸空綁定。被改名或刪掉的測試(`t_ns_append_old_line` 等)名稱仍在。判不破壞(K1 的缺口是「沒有測試蓋到」,不是綁定壞掉)。
- Systems/guard-kill:diff 沒碰 `guard kill` 的 rc 優先序與 `--json` 輸出。判不影響。
- Systems/授權與歸屬:diff 沒動 `_VENDORED_TOOLKIT`、授權檔、`scripts/lumos` 檔頭的 SPDX 與 MIT。判不影響。
- Systems/測試假綠形態(修 bug 的翻紅釘要配前置斷言):本輪把七支配對測試的探針換成「舊行就有的行號引用加帶來源的括號」,並補了前置斷言(例如 `①a 前提:改一個字配不上時…照報`、`rc0 == 1`),方向符合這條合約。例外:K1 說的兩條規則完全沒有測試,新的牆上時鐘改計數(`calls[0] <= 40`)與相對倍數(`big < 30 * max(small, 1e-4)`)是合理的去不穩定化。判符合。
- Systems/pitfalls-code-loop、Systems/design-loop:diff 沒動風險分級與設計審迴圈本體;`design-loop` 那條處置閘第五步要求設計審材為 .md 計劃,本輪只改了計劃內文,沒碰它。判不影響。
- 只列名的節點(lumos-cli-lifecycle、loop-convergence-recording、節點範圍與索引守衛、lumos-deinit、check-t-sentinel、cochange-guard、check-r-guard、doctor-irreversible-hint、lumos-refcheck、canary-audit、slim 系列、規格落成可驗收條件_計劃、雙向門放行_計劃、逃逸自動記_計劃、core-invariant-baseline、judge-severity-gate):沒有內文可對,diff 也沒有直接碰它們各自的主題;其中 `_ns_deleted_summary_lines` 補上的兩個 git 旗標只影響筆記形狀擋自己的讀 diff,不影響 deinit 與 slim 這幾條。判不影響。

## 沒問題的項目(試過、沒壞)

- 位元組總和上限:`_ns_append_read_blobs` 先 `cat-file --batch-check` 問大小再決定要不要讀,總和只算單篇上限內的,200 篇乘兩個版本乘 512 KB 最壞約 200 MB 的輸入會在讀之前回 cap;實際讀入最多 32 MiB,加上 `cat-file --batch` 的 stdout 與切片,尖峰約 100 MB 量級,可接受。多問一次大小(`_nodehome_cat_blobs_capped` 內部又問一次)是多一個 git 行程,不是正確性問題。
- 候選篇數與對數的上限先於讀檔檢查,超過回 `"cap"` 且 `_t` 已快取成空表,`table()` 只印一次提醒(`t_ns_append_caps` ② 驗過)。
- 記號檔拿掉後不再有「多個會談同時寫同一個記號檔」的競爭;改讀帳是只讀、讀到被另一個進程寫一半的最後一行時 `_drift_jsonl_iter` 會略過壞行,不會丟例外。帳檔不存在時 `_gov_tail_bytes` 的 `stat` 丟 `OSError`,被外層 `except OSError` 接住回空集合。
- `_ns_nfc_clash_errs` 用 `_nodehome_list` 回傳的不去重路徑清單數並存,我在 macOS 暫存區的端到端測試(`t_ns_nfc_clash_errs` ④⑤⑥)重跑過綠;`_note_audit_items` 只在有送審項目時才多一次 `ls-tree`,成本隨檔案數線性,可接受。
- `_note_audit_dispute_map` 形狀改成巢狀字典後,全 repo 只有 `_note_audit_dispute_for` 一個讀取點,沒有漏改的舊讀法(grep 過)。
- `_ns_deleted_summary_lines` 新加的 `--inter-hunk-context=0 --diff-algorithm=myers` 與 `_ns_diff` 對齊,沒有改變輸出格式,既有守衛測試仍綠。

最高 severity: minor
