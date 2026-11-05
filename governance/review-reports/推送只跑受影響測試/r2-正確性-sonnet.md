severity: major

**逐情境走查,以 scripts/hooks/pre-push 現況加 spec 字面改動為準**

| 情境 | 走到哪、跑什麼、印什麼 |
|---|---|
| 推功能分支,原判 full 且 spec-gate 判 light 又 light_ok | 約 572–576 行已有。跑文件子集加關鍵字子集,自主迴圈照 `autoloop_full`。spec 只多印一行。 |
| 推功能分支,原判 full 因守衛檔(anchor-baseline、governance/code-loop/) | 見 finding 2。降成 light,但關鍵字是空的。只跑文件子集,自主迴圈整支跑。訊息卻寫「跟改動有關的測試」。 |
| 推功能分支,原判 full,spec-gate 沒判 light 或 light_ok 為假 | 見 finding 3。spec 沒講清楚。 |
| 推 main 或 master | 維持 full,沒問題。 |
| 一次推 main 加功能分支 | main 那個 ref 讓 `_SUITE_FULL=1`,整次全套,沒問題。但功能分支那個 ref 的「全套由 PR 的 CI 跑」仍會印出,見 finding 4。 |
| 推標籤 | `refs/tags/*` 不符合 `refs/heads/*`,維持 full,與 spec 相符。 |
| 只刪遠端分支 | 見 finding 5。`_SUITE_SEEN` 仍為 0,`_suite_mode` 落在 full,會跑全套。 |
| 新分支首推 | 範圍改用 `_brange`,降級邏輯相同。沒新問題。 |
| 原判 docs | 不受影響,沒問題。 |
| 原判 light | 不受影響,沒問題。 |

**已讀,無 finding 的部分**
- 〈舊否決對照〉、〈範圍〉、〈回退〉、〈審計修正紀錄〉。
- CI 的 PR 事件一律全套這句成立。ci.yml 的 `suite=full` 預設,只有 push 事件且 pitfalls 判 docs 才改成 docs,`pull_request` 沒有 before,所以一律全套。

severity: major
blocking: 是(照字面實作會修錯根因,而且 S2 的測試先行做不出來)
spec 段落:〈做法〉第 4 點、S2
問題:spec 說「選中支數比片數少時必有空片」,所以 `run_group` 會回 3,掛鉤才印假警報。但執行器對這種空片回的是 0,不是 3。rc 3 只出現在整個子集一開始就是 0 支的時候,那時每一片都是 3,`run_group` 本來就正確。所以 spec 描述的混合 3 和 0 的情形不會發生。
- 子集在分片前先挑,空片會印「子集比片數少,別片有跑」然後 `return 0`。
- 實測:`--suite keys --keys _keys_mentioned` 選中 2 支,切 4 片,四片 rc 全是 0。
- 因此「改成每片都回 3 才算 3」行為不變,S2 那支測試不可能先紅。
- 真正印出假警報的原因,spec 沒找到。
- `_krc_all3=1` 設在外層,而 `run_group` 是在 `( run_group ... ) &` 子殼裡跑,外層變數改不到。照字面「用 `_krc_all3`」實作不可行,得改成函式內區域變數。
引句:「`run_group` 只要任一片回 3(這片分到 0 支)就整組回 3,選中支數比片數少時必有空片,掛鉤就印」
佐證:`scripts/test_lumos.py:48896`、`scripts/test_lumos.py:48899`、`scripts/hooks/pre-push:914`、`scripts/hooks/pre-push:954`

severity: major
blocking: 是(spec 主打的使用情境,實際一支跟改動有關的測試都不跑)
spec 段落:〈做法〉第 2、3 點、〈現況〉
問題:spec 的動機是「改了測試檔,基準變,守衛檔判全套」。但 `_test_suite_for_range` 碰到守衛檔會提早回傳 `code: []`。
- 結果是 `_affected_test_keys` 回空清單,`affected_keys` 為空。
- 每個走過代碼審的功能分支都會改到 governance/code-loop/,也屬守衛檔,所以這是常態,不是例外。
- 降成 light 後只跑文件子集(讀 README、docs 路徑的測試),加上整支自主迴圈(因為關鍵字為空,`autoloop_full` 為真)。
- 被改動的測試、被改動的函式相關測試,本機一支都沒跑。
- 第 3 點要印的「跟改動有關的測試」在這種情況是假話。
- RETIRE-IF 用「CI 紅而本機綠」計數,會因此被系統性灌水。
- spec 沒處理這件事,也沒在 S1 加「守衛檔分支」的案例。
引句:「改了測試檔,測試檔簽名基準 `governance/anchor-baseline.json` 就跟著變;它在守衛檔清單 `_DOCS_ONLY_NEVER`,所以幾乎每個功能推送都判成全套。」
佐證:`scripts/lumos:61705`(守衛檔的提早 `return dict(full, ...)`,`code` 為空)、`scripts/lumos:61758`(`not code_files` 回 `[]`)、`scripts/lumos:61744`(`autoloop_full` 在空關鍵字時為真)

severity: major
blocking: 是(照字面改會讓 S3 紅,並拿掉既有的安全條件)
spec 段落:〈做法〉第 2 點、S3
問題:`_AUTOLOOP_FULL` 和 `_SUITE_KEYS` 目前只在「spec-gate 印出 light 且 `light_ok`」的 if 區塊裡賦值(572–577 行)。spec 說「改判 light(沿用 `_SUITE_LIGHT`,不新增狀態)」,又說關鍵字和 `autoloop_full` 照現行取,但沒說取值區塊的進入條件怎麼改。
- 只把 `_suite_this` 改成 light,不動那個 if:`_SUITE_KEYS` 為空、`_AUTOLOOP_FULL=0`,自主迴圈只跑 `-k real_claude_md`。與 S3 相反,而且空關鍵字時應整支跑的保護也失效。
- 把取值搬到 if 外面:就繞過 `light_ok`。該條件原本是 r1 資安席加的,防止測試檔、skills、workflow 這類既不是文件也不是程式的檔,從小改動閘眼皮下溜過少跑全套。spec 沒討論這項保護被取消,是否有意。
- 功能分支原判 full 但不是 light(spec-gate 沒判 light)時,spec 沒說要不要降。
引句:「這個 ref 原本判 `full` 時改判 `light`(沿用 `_SUITE_LIGHT`,不新增狀態);關鍵字照現行從 `pf_json` 的 `affected_keys` 取、自主迴圈照現行 `autoloop_full`。」
佐證:`scripts/hooks/pre-push:572`、`scripts/hooks/pre-push:575`、`scripts/hooks/pre-push:576`、`scripts/hooks/pre-push:818`

severity: minor
blocking: 否(訊息不實,但閘的行為仍正確)
spec 段落:〈做法〉第 3 點、S1
問題:訊息在每個 ref 的迴圈裡印。同一次推送另有推 main 時,最後仍跑全套,但功能分支那個 ref 已經印了「本機只跑文件子集,全套由 PR 的 CI 跑」,與實際相反。
- 還有一個類似情況:`_SUITE_GRAPH=1` 但執行器不認得 `--graph` 時,`_suite_mode` 退回全套,同樣與已印的訊息矛盾。
- 訊息應該放在迴圈之後,看最終的 `_suite_mode` 再印。
引句:「同一次推送有推 main 的 ref,就全套。」
佐證:`scripts/hooks/pre-push:878`、`scripts/hooks/pre-push:818`

severity: minor
blocking: 否(沿用現況,但和 spec 的目標方向不一致)
spec 段落:〈做法〉第 1 點、〈範圍〉
問題:只刪遠端分支時,刪除行在 482 行 `continue`,`_SUITE_SEEN` 保持 0。於是 `_suite_mode` 預設 full,刪分支(合併後的日常清理)也要跑整套全套。spec 的情境清單與 S1 都沒涵蓋。
- 「功能分支」判斷只看遠端 ref 名字是不是 `refs/heads/` 底下、非 main 或 master。
- 推到 release 或長期分支(例如 `release/*`)也被降級。
- ci.yml 只對 PR 和 push main 觸發,所以推到沒開 PR 的非 main 分支,本機不跑全套,CI 也不跑。
- spec 的「全套由 PR 的 CI 跑」這句,在沒開 PR 時不成立。
引句:「目的是 `refs/heads/<名>` 而且名字不是 `main` 或 `master` → 這個 ref 算功能分支」
佐證:`scripts/hooks/pre-push:482`、`scripts/hooks/pre-push:818`、`.github/workflows/ci.yml:4`

**實務隱患**
- 守衛面:finding 2 和 finding 3。spec 自己列的守衛面隱患只寫「等 PR 的 CI 才看到」,沒提到本機在最常見的守衛檔情境連冒煙測試都沒有。
- 併發、金流、對外送出、不可逆:無。理由是只動本機掛鉤的測試範圍,不碰這些面向。
- 新舊版本錯開:無。理由是不改 `pitfalls --json` 的欄位。

總結:最嚴重等級是 major,會擋的問題有 3 條(finding 1、2、3),不會擋的有 2 條。
