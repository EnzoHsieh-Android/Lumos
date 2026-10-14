severity: major

審查對象是 `/tmp/推送前一次列出全部擋下原因-r1.md`,對照 prepush-collect 的 `scripts/hooks/pre-push` 與 `scripts/lumos`。共 5 條 finding,2 條 major、3 條 minor。

**1.** 做法第 4 點(`code-loop check --collect`)

severity: major
blocking: 是 — 合約測試紅之後,pitfalls 失敗的 fail-open 回傳會把已收集的擋下蓋成放行。

引句:「合約測試先紅時照樣算風險分級,第四道才判得了。」

問題:`_codeloop_guard_verdict` 在第 2.5 步之後有很多 `return {"blocked": False, ...}` 的路徑。spec 只說「四道都跑完」,沒說這些路徑要怎麼處理。若實作只是把第 2.5 步的提早 return 拿掉,之後任何一個 `blocked: False` 的 return 都會把先前收集到的擋下丟掉。

這些路徑在 `scripts/lumos:51074-51083` 和 `scripts/lumos:51164-51211`:
- pitfalls 回非零時 fail-open,在 `scripts/lumos:51074`。
- pitfalls 沒有 JSON 輸出時 fail-open,在 `scripts/lumos:51078`。
- pitfalls 丟例外時 fail-open,在 `scripts/lumos:51083`。
- `tier != "high"` 時直接回放行,在 `scripts/lumos:51164`。
- 留痕有效時回放行,在 `scripts/lumos:51173` 和 `scripts/lumos:51187`。
- `_codeloop_review_block` 的 env 跳過和合併側放行,在 `scripts/lumos:51211`。

具體失敗情境:
1. 合約測試紅,`pf_json` 為空(掛鉤因此不帶 `--bound-tests-advisory`)。
2. 收集模式記下合約測試紅,然後 pitfalls 失敗,走 `scripts/lumos:51074` 回 `blocked: False`。
3. 最終 rc 是 0,掛鉤放行。原本這種情況在 `scripts/lumos:51059` 會直接擋下。

S6 和 S4 的測試只涵蓋掛鉤層和兩組正常組合,沒有「已有擋下,後面遇到 fail-open 或有效留痕」的案例。spec 需要明講「blocks 非空就不能被後面的放行 return 覆蓋」,並為每個 return 站點各補一支先紅的測試。

**2.** 做法第 4、5 點(掛鉤傳 `--collect`、`LUMOS_PUSH_PREVIEW=1`)

severity: major
blocking: 是 — 新版掛鉤配舊版 lumos 時,code-loop 擋下被靜默吞掉。

引句:「掛鉤呼叫時帶上 `--collect`。」

問題:`ap.parse_args()` 是嚴格解析,在 `scripts/lumos:53415`。舊版 lumos 遇到 `--collect` 會回 rc2。掛鉤對 rc 不是 1 的情況一律當工具錯誤放行,見 `scripts/hooks/pre-push:482`。

具體失敗情境:
- 掛鉤是 symlink 或複製出來的,lumos 部分更新,於是掛鉤是新版、`scripts/lumos` 是舊版。
- 帶 `--collect` 的 `code-loop check` 回 2,掛鉤放行。tier=high 沒留痕、合約測試紅、表態不完整三種擋下全部變成放行,而且沒有訊息。
- `scripts/hooks/pre-push:549` 已有同型的「舊版工具不認得 --gate」雜訊提示,但那是 reread 這道,只講一句。code-loop 這道原本是硬擋。

spec 沒有「新舊互讀」的處理。需要二選一:掛鉤先探測 lumos 是否認得 `--collect`,不認得就退回不帶旗標的舊行為(第一個擋下照舊擋);或把 rc2 在 code-loop 這道當成擋下。

反方向也有同型問題。舊版掛鉤配新版 `lumos push-preview` 時,舊掛鉤不認 `LUMOS_PUSH_PREVIEW`,會真的跑完 8 分鐘全套測試才回,違背「不跑測試」。spec 沒有版本握手。

**3.** 做法第 5 點(`LUMOS_PUSH_PREVIEW=1` 讓掛鉤在統一判斷處停下)

severity: major
blocking: 是 — 任何真推送只要環境裡有這個變數,就能跳過全套測試且不留帳。

引句:「帶環境變數 `LUMOS_PUSH_PREVIEW=1` 跑掛鉤;掛鉤看到它,到統一判斷那一步就停:有擋下回 1,沒有回 0」

問題:掛鉤分不出這是預演呼叫還是真的 `git push`。真推送時只要環境有 `LUMOS_PUSH_PREVIEW=1`(`.zshrc`、CI 設定、被汙染的 session),掛鉤就在全套測試前回 0,git 照常推出去。

這是一道沒有帳可查的測試閘繞法。既有的跳閘環境變數如 `LUMOS_SKIP_DRIFT_CHECK`、`LUMOS_SKIP_CODE_LOOP` 都會留治理帳,這個不會。spec 的「實務隱患」把它列成已排除的對外送出風險,沒有檢查這條路徑。

具體失敗情境:`export LUMOS_PUSH_PREVIEW=1` 之後 `git push`,全套測試是紅的也推得上去。

spec 需要加機械接縫,讓預演模式只在預演呼叫時成立。例如預演指令傳一個每次不同的 token,同時掛鉤要驗證 stdin 或 `$2` 等條件。或者預演模式回 0 時一律在掛鉤層寫帳,並讓真推送路徑忽略這個變數。

**4.** 做法第 5 點(預演會跑逃逸記帳和各閘的帳務副作用)

severity: minor
blocking: 否 — 只是預演的副作用多於「不推送」所暗示的,不影響擋下判定。

引句:「不推送、不跑測試;用目前分支推到它追蹤的遠端分支」

問題:預演整套重跑掛鉤,其中有帳務寫入。逃逸記帳 `loop escape --auto`、`_gate_event_or_warn`、`_gate_failopen`、`LUMOS_SKIP_*` 的留帳,都在 `scripts/hooks/pre-push:464-471` 和 `scripts/lumos:51250` 一帶。每跑一次預演,同一個擋下就多記一筆「推送閘擋下」逃逸。這會把逃逸統計灌水,也讓 `docs/.governance-log.jsonl` 變髒,而它是被追蹤的檔案。

spec 的對外送出一節寫「預演不推送;只有真推送才連遠端」。但預演需要「遠端查不到那個分支」這個判斷,而 spec 沒說是查本機遠端追蹤 ref 還是 `ls-remote`。若是 `ls-remote`,這句話就不成立。⚠ 判不準,spec 沒有明講查法。

預演需要說明:預演時逃逸記帳要不要寫、帳寫到哪,以及遠端判斷是否連網。

**5.** 做法第 2 點(裁判簽名擋下之後仍繼續跑別的閘)

severity: minor
blocking: 否 — 擋下結論不變,只是在裁判檔被改的前提下仍執行有副作用的工具。

引句:「下面其他道的結果是用被改過的工具算的,只供參考」

問題:原本 `anchor verify` 失敗就 `exit 1`,在 `scripts/hooks/pre-push:277`,被改過的工具完全沒機會執行。收集模式下,被標為不可信的工具會繼續跑 `drift check`、`loop escape --auto` 等。其中 `loop escape --auto` 和各道閘的 ledger 寫入是有副作用的。

擋下本身不會被吞掉,因為 `anchor` 這筆已記錄,最終仍回 1。但「只供參考」只涵蓋輸出可信度,沒涵蓋副作用。spec 可以讓 `anchor verify` 失敗時只收集不寫帳,或乾脆維持立刻結束。

**逐道走 9 道閘**(收集模式下是否讀到前一道的半成品狀態):
- anchor verify、簽名檔沒提交、`doctor --ci`:互相獨立,不共用狀態。已讀,無 finding(副作用見第 5 條)。
- `home check` 與 `note-shape`:只用 `_hrange`,獨立。已讀,無 finding。
- `spec-gate --push-check`:`_sg_out` 只在判 light 時用,擋下後必然 `exit 1`,不會誤用。已讀,無 finding。
- `code-loop check`:先讀 `_IMPACT_JSON`,`impact_once` 在 `home check` 和 `note-shape` 之後。收集模式不會讓它變成半成品,因為 `impact_done` 在迴圈末尾仍會執行。已讀,無 finding(行為見第 1 條)。
- `drift` 與 `reread`:用 `_rsha.._lsha`,跟前面各道無共用狀態。已讀,無 finding。
- 每個 ref 開頭會重設 `sg_rc`、`cl_rc`、`nh_rc`、`ns_rc`;`pf_json` 與 `_tier_high` 每個 ref 重新賦值,所以跨 ref 不會帶入前一個 ref 的結果。

**`--json` 加 `blocks` 對掛鉤的影響**:無。掛鉤呼叫 `code-loop check` 沒帶 `--json`,而 `pf_json` 來自 `pitfalls --json`,不是 `check` 的輸出。spec 把兩者放在同一句審查要求裡,但實際不相干。補充一點:合約測試擋下的 verdict 目前沒有 `reason_kind`,見 `scripts/lumos:51060`,`blocks` 要另外給它一個值。

**實務隱患類**:
- 守衛面:見第 1 至第 3 條。
- 不可逆與金流:無,spec 說得對。
- 輸出變長:無新問題。
- 寫一半(收集到一半被中斷):`pp_stop_if_signaled` 會在 rc 128 以上時立即結束,所以中斷不會變成放行。無 finding。

最嚴重:major,blocking 共 3 條(第 1、2、3 條)。
