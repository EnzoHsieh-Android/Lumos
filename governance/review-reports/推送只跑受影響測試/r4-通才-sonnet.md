severity: major

我對照了 push-subset 的程式碼逐節查證,沒有改動任何檔,也沒有建臨時目錄。

做法 1、2、4、回退、現況:已讀,除下列 finding 外無問題。以下三項是查證後確認成立的現況宣稱。
- `ci.yml` 的 PR 事件一律全套。
- `_note_reread_mainline_names` 確實不看遠端名。
- pre-push 讀 `pf_json` 用 grep,缺欄位時自然落到 full。

主線判定、`pf_json` 缺欄位時的失效方向、跟 r3 殘留的「CI 推分支」舊說法都已核過。「推任何分支都跑」只剩在 PRIOR-ART 與審計修正紀錄裡當歷史,沒有殘留矛盾。

severity: major
blocking: 是(照字面實作會讓本機對沒開 PR 的功能分支印出不實的「CI 會跑全套」保證,違反範圍「④訊息照實講」)
- spec 段落:做法 3、做法 4 的逐處清單、S1。
- 問題:做法 4 逐處清單只列「掛鉤 `_suite_word` 的說明句」,但降級後走的那條路徑上,pre-push 還有至少四處寫死「CI 會跑全套當後盾」或「CI 會兜底」。
- 這四處的效果:
  - 關鍵字抽不出時印「CI 會跑全套當後盾」。
  - 關鍵字沒對到任何測試時印「CI 會跑全套當後盾」。
  - 開跑前的提示都寫「嫌久可 --no-verify,CI 會兜底」。
  - 掛鉤內 spec-gate light 的註解。
- 後果:功能分支沒開 PR 時 CI 根本不跑,spec 自己的實務隱患也這樣承認。降級後使用者會同時看到新訊息(PR 的 CI 才跑)和舊訊息(CI 會跑全套當後盾、CI 會兜底),兩者矛盾。
- 驗收缺口:S1 只斷言新訊息「只印一次」,抓不到舊句,也沒有條款綁這幾處。
- 修法:把它們列進做法 4,並加一條斷言降級路徑輸出不含「CI 會跑全套當後盾」。

引句:「掛鉤 `_suite_word` 的說明句」
佐證通道:
- file: `scripts/hooks/pre-push:894`
- file: `scripts/hooks/pre-push:946`
- file: `scripts/hooks/pre-push:963`
- file: `scripts/hooks/pre-push:569`

severity: minor
blocking: 否(措辭精度,不影響實作行為)
- spec 段落:實務隱患〈守衛面〉。
- 問題:把剩下的洞寫成「沒走 PR 直接合」。直接推 main 在 pre-push 是 `pushed_mainline` 為 true,照樣本機全套(S2、S3 自己也這樣寫)。
- 真正的洞:只有在 GitHub 上合併 PR 時沒等全套綠。
- 修法:改寫洞的描述,避免讀的人以為直接推 main 也沒擋。

引句:「main 沒有分支保護,靠訊息與既有規矩,機械擋是 Q2。」
佐證通道:file: `scripts/hooks/pre-push:540`

severity: minor
blocking: 否(撤除條件可量,但跟動機對不上)
- spec 段落:RETIRE-IF、白話、現況 FACT。
- 問題一:撤除條件數的是「PR 頭提交上紅的比例」,但撤除的理由寫成「來回修 CI 的時間已經比本機多跑的時間多」。比例不等於時間,量出來也推不回時間。
- 問題二:它要求先記「上線前八週的同一比例」當基準,卻沒說基準怎麼用。判準是固定的三成,基準沒進任何比較,是裝飾。
- 問題三:動機的對照是單次「同次本機約一小時」,但白話與專案說明寫的常態是本機 5–10 分,CI 要 15–20 分。多數情況下全套等待時間不降反升,只有「推送時人不用等」成立。
- 修法:把「推送前被擋住的等待時間 vs PR 等 CI 的時間」併進撤除條件;或明講這步的價值是不阻塞推送、不是總時間下降。
- 量測面可行:近八週約 143 個 PR,分母夠大。

引句:「基準先記上線前八週的同一比例(上線當天量)。」
佐證通道:`git log --since=2026-09-10 --merges` 查得 143 筆 `Merge pull request`。

severity: minor
blocking: 否(條款綁定缺口,實作仍可翻紅)
- spec 段落:做法 2「降級刻意不受 `light_ok` 約束」、驗收 S1、S5、S6。
- 問題一:這是本計劃最特別的決定(改到測試檔、守衛檔也降),卻沒有條款專綁。S1 的 fixture 若只用單純程式檔,日後有人把 `light_ok` 條件加回去,S1 照綠。
  - 守衛檔在 `_test_suite_for_range` 的行為是提早回 `full`,`code` 空、`light_ok` 為 false。
  - 要有一條以守衛檔或測試檔為 fixture 的條款,並要求 `suite_computed` 在該情境為 true。
- 問題二:S1 與 S6 綁同一個測試名 `t_prepush_feature_branch_skips_full`,兩個不同斷言(迴圈後只印一次訊息、`autoloop_full` 時自主迴圈整支跑)擠在同一函式,回退時「刪 S1、S6」變成同一件事,無法分開翻紅。
- 問題三:做法 2 說「原本判 docs 或 light 的照舊」,但沒有條款鎖「原本就是 light(spec-gate 判的)的功能分支不印降級訊息」。
- 另:`suite_computed` 目前在 `_test_suite_for_range` 回傳的 dict 裡沒有對應欄位,只有 `reason` 文字。做法 1 沒說明由哪裡加這個旗標,實作者得自己決定;建議在做法 1 點明在 dict 加欄位,不要靠比對 reason 字串。

引句:「降級刻意不受 `light_ok` 約束(改到測試檔、守衛檔也降):全套由 PR 的 CI 跑。」
佐證通道:file: `scripts/lumos:61705`

severity: minor
blocking: 否(指涉不唯一)
- spec 段落:做法 4 最後一項。
- 問題:「父計劃 [[Projects/推送與CI提速_計劃]] 的 REVISIT 2026-11-14 那行」指涉不唯一,父計劃裡有兩行 `REVISIT:2026-11-14`。
- 該加 `[closed:]` 的是第二行「推送前掛鉤的大改合併後,開第二階段」。
- 修法:寫出行首文字或在計劃裡指明是哪一行。

引句:「父計劃 [[Projects/推送與CI提速_計劃]] 的 REVISIT 2026-11-14 那行」
佐證通道:file: `docs/lumos-toolchain-knowledge/Projects/推送與CI提速_計劃.md:75`、file: `docs/lumos-toolchain-knowledge/Projects/推送與CI提速_計劃.md:76`

實務隱患逐類:
- 守衛弱化:見上。其餘 spec 已寫。`ci-wait` 以 `--commit <sha>` 查,PR 事件的 run 也算在該 sha 下,所以「對 PR 頭提交判定」可行。
- 算不出來的方向:fail-closed 與 grep 寫法成立。新增旗標被舊版 `argparse` 拒絕、`|| true` 吞掉、`pf_json` 空,三者都落全套。
- 資安與外部輸入:grep 對 JSON 字串裡的引號是跳脫過的,claims 裡的內文不會偽造 `"pushed_mainline": false`。無新增風險。
- 併發與負載:spec 已涵蓋,沒有新問題。
- 金流、對外送出、不可逆:沒有新增風險,spec 已排除。

最嚴重等級 major,會擋的問題 1 條。
