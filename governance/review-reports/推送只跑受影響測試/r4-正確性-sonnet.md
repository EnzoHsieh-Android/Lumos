severity: minor

我逐情境走過 spec 與程式。三項驗證結果:
- `root` 在 `cmd_pitfalls` 裡拿得到。
- `tip` 能從 `--diff` 的終點取得。
- `suite_computed` 不能直接從 `_test_suite_for_range` 的回傳分辨出來。

**情境推演**(掛鉤路徑以 `scripts/hooks/pre-push` 為準)

| 情境 | 走到哪、跑了什麼、印了什麼 |
|---|---|
| 推功能分支 | `pitfalls` 回 `pushed_mainline:false`、`suite_computed:true`,降成 light。跑文件子集加關鍵字子集,迴圈後印一次「全套由 PR 的 CI 跑」。 |
| 推 `refs/heads/main` | 分支名在 `_note_reread_mainline_names` 回的集合裡,回 true,照全套。 |
| 推網址到 main | 集合不看遠端名,仍回 true,照全套。 |
| 混推(main 加功能分支) | main 的 ref 讓 `_SUITE_FULL=1`,整體全套,不印那行。 |
| 標籤 | 非 `refs/heads/` 回 true,照全套(與現況一致)。 |
| 新分支首推 | `_brange` 由 `pp_block_range_for` 算成與主線的分岔點,降級照常。 |
| `pitfalls` 出錯 | 掛鉤用 `\|\| true` 吞掉,`pf_json` 為空,照全套。 |
| 舊版 lumos | argparse 拒絕新旗標,`pf_json` 為空,照全套(見 finding 3)。 |
| 範圍算不出 | `suite_computed:false`,照全套(見 finding 1)。 |
| 守衛檔改動 | 清單算得出來,`suite_computed:true`,降成 light。但 `code` 是空的,所以關鍵字為空,只剩文件子集。 |
| 帳本提交推到已開 PR 的分支 | 本機只跑小子集。PR 事件的 CI 一律全套(`ci.yml` 的 prep 對 `pull_request` 直接設 `suite=full`),PR 以編號分組並取消進行中的。 |

**各項驗證**

1. 掛鉤逐 ref 的讀取順序(`pf_json` 的 `grep` 讀法)、新降級分支的放置位置、迴圈後印一次訊息,都接得上現有結構。已讀,無 finding。
2. `_note_reread_mainline_names(root, tip)` 的參數拿得到。
   - `root` 是 `cmd_pitfalls` 的 repo 根。
   - `tip` 在 spec 沒寫來源,但可用 `_diff_range_ends(root, diff_range)` 的終點。掛鉤給的 `_brange` 終點是 `_lsha`。
   - `tip` 只用來選「哪個遠端」(`_lens_default_remote`)。`HEAD` 或 sha 都能用。
3. CI 前提屬實。push 只限 main 與 tag,`pull_request` 一律全套。這一點已核對,無 finding。

---

severity: minor
blocking: 否(措辭與實作指引不足,照字面實作不會出錯行為)
spec 段落:做法 1、S5。問題:`suite_computed` 無法從 `_test_suite_for_range` 現有的回傳分辨。三種回傳的 `suite` 都是 full、`code` 都是空,只有 `reason` 文字不同:
- 守衛檔(算得出)。
- 算不出改動清單。
- 範圍算不出來。

實作必須在那兩個失敗回傳點加新鍵,或在 `cmd_pitfalls` 兩處輸出(`--no-lint` 與有 config 兩條路)比對 `reason` 字串。字串比對會被守衛檔檔名誤觸發(reason 內含檔名)。spec 應寫明「在 `_test_suite_for_range` 的回傳 dict 加布林鍵」。
引句:「`--json` 一律多輸出 `suite_computed`:`_test_suite_for_range` 算得出改動清單時 true」
佐證:`scripts/lumos:61705-61734`、`scripts/lumos:61913`、`scripts/lumos:61980`

severity: minor
blocking: 否(spec 內部不一致,但隱患節已明講接受)
spec 段落:範圍 ③ 與實務隱患「主線判定查候選失敗」。範圍 ③ 說「算不出主線時照全套」,但程式的行為相反。`_note_reread_mainline_names` 查候選失敗或逾時只回固定名 `main`、`master`,不是回「算不出」。結果是預設分支不叫 main 或 master、且遠端追蹤 ref 缺席時,推主線會被當功能分支降級。隱患節接受了這件事,範圍 ③ 的字面要改。
引句:「③算不出範圍、算不出主線時照全套」
佐證:`scripts/lumos:53734-53747`

severity: minor
blocking: 否(只影響提醒,不影響擋不擋)
spec 段落:做法 2、實務隱患「算不出來的方向」。掛鉤唯一一次 `pitfalls --json` 呼叫的結果還供其他閘讀:
- `_tier_high` 的高風險提醒。
- 標籤路徑的技術棧題提醒(`stack_questions_applicable`)。
- `_ba` 是否帶 `--bound-tests-advisory`。

舊版 lumos 因新旗標被 argparse 拒絕、`pf_json` 變空時,這些全部一起靜默掉,不只推送變全套。隱患節只提「純文件推送也變全套」。`--pushed-ref` 在別的子命令早已存在,所以掛鉤用 `grep '"--pushed-ref"'` 探測會誤判。探測字串要綁 pitfalls 專屬的 `dest` 名。
引句:「舊版 lumos 不認得新旗標時連純文件推送也會變全套(比現在慢,方向安全)」
佐證:`scripts/hooks/pre-push:540-546`、`scripts/hooks/pre-push:591`、`scripts/hooks/pre-push:675`

severity: minor
blocking: 否
spec 段落:做法 3、做法 4。掛鉤現有的 light 路徑已有兩句會說「CI 會兜底」或「CI 會跑全套當後盾」:
- 關鍵字為空時印「抽不出函式或檔名當關鍵字…CI 會跑全套當後盾」。
- 推送前先跑子集那行印「嫌久可 --no-verify,CI 會兜底」。

降級後的功能分支若沒開 PR,這兩句不成立,而且與新增的那行並存會雙印、互相矛盾。做法 4 逐處清單只列了 `_suite_word`,沒列這兩處。
引句:「掛鉤 `_suite_word` 的說明句」
佐證:`scripts/hooks/pre-push:893-895`、`scripts/hooks/pre-push:946`

severity: minor
blocking: 否
spec 段落:做法 2。降級不受 `light_ok` 約束,而關鍵字在範圍很大時沒有上限。遠端舊值本機找不到(別人推的、強推後)時,`pp_range_for` 改用空樹範圍。我在本 repo 量到這個範圍的頂層 def 關鍵字有 6862 個(`scripts/lumos` 單檔約 52KB 的逗號串),整串進 `--keys`。這等於幾乎選中所有測試,「冒煙」名實不符;Linux 單一參數上限 128KB,逼近。spec 只處理了新分支首推。建議關鍵字超過上限就不降級,或不帶 keys。
引句:「降級刻意不受 `light_ok` 約束(改到測試檔、守衛檔也降)」
佐證:`scripts/hooks/pre-push:41-47`、`scripts/lumos:61744-61800`

severity: minor
blocking: 否
spec 段落:做法 2。「用掛鉤既有的 `pp_q` 引號寫法」不適用於這個呼叫。這個呼叫是陣列式帶參(`"$PY" "$GRAPHCTL" pitfalls --diff "$_brange" …`)。`pp_q` 是給組字串(例如 `_push_args`)用的,用在這裡會把單引號當字面值傳進去。直接 `--pushed-ref "$_rref"` 即可。
引句:「用掛鉤既有的 `pp_q` 引號寫法」
佐證:`scripts/hooks/pre-push:117-125`、`scripts/hooks/pre-push:540`

**實務隱患**

- 守衛面:已由 CI 的 PR 全套與合併前 `ci-wait` 補上。沒走 PR 或沒等綠就合的洞,spec 已誠實列出,無新增。
- 時間與逾時:`_note_reread_mainline_names` 不帶 deadline 呼叫,git 卡住會卡推送。這是現況慣例,風險低。

總結:最嚴重等級是 minor,共 6 條,blocking 0 條,沒有會擋的問題。
