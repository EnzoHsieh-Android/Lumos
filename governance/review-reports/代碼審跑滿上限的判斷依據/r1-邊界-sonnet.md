severity: major

## F1 信號一「整輪各席加總」與現行帳本結構不符,照字面實作會拿到失真數字
severity: major
blocking: 是——照字面實作,`--finding-class` 之外的「折入走勢」訊號很可能拿到的是加總過的原始 findings 數而不是折入(accepted)數,建議規則(下降/持平)整套算錯。
引句:「每一輪折入幾條(帳本的折入清單,整輪各席加總)」
file: `scripts/lumos:18342` — `_loop_status_disposal` 明文擋「第 {rid} 輪有 {len(carriers)} 筆記錄都帶了處置結果,一輪只能有一筆」
file: `scripts/lumos:18344` — 同函式註解:「多席審查(2026-08-25 甲裁後)一律彙總記帳:處置清單只掛一席,其餘席只留痕(severity/report)」
file: `docs/.canary-log.jsonl:52-54` — 實帳 code-kill r1 三席記錄各自帶 `findings: 12 / 12 / 0`,三筆都沒有 `findings_set`/`folded_set`(這是舊 canary caught/missed 協議的散文 findings 計數,不是折入後的處置集合)
現況是:2026-08-25 甲裁後,一輪裡只有一筆「carrier」記錄帶 `findings_set`/`folded_set`(已是彙總後的處置結果),其餘同輪席位的記錄根本沒有這兩個欄位,只有各自的 `severity`/`findings`(原始發現數,不是折入數)。S1 的括注「整輪各席加總」暗示每席各自帶一份折入清單、要逐席相加,但實際只有一筆帶得到折入清單。若實作者依字面把同輪每筆記錄的 `findings`(而不是 carrier 的 `folded_set` 長度)加總,拿 code-kill r1 這種真實資料算,會得到 24(12+12+0)這種跟「折入幾條」毫無關係的數字——因為 12/12/0 是各席自己主張的發現數,不是經處置後被接受折入的條數。計劃全篇沒有一處寫「只取 carrier 的 folded_set,其餘席位的 findings 欄不算進折入」,這個區分在信號一、S2、S8、S9 都要用到,卻只在這裡被「各席加總」這個誤導措辭帶過。

## F2 「沿用 quote-check 的引句定位」判斷不出「新增行」,S2/S7 需要的是一個不存在的新能力
severity: major
blocking: 是——S2(換做法 vs 再一輪的主要判準)與 S7(引句定位不到算判不了)兩條的可執行性都建立在一個目前程式碼裡沒有的比對邏輯上,PRIOR-ART 卻宣稱「不加新依賴」。
引句:「拿它的第一句引句去最後一輪的凍結審材定位(沿用 quote-check 的比對);定位到的那行是新增行,而且這行不在上一輪凍結審材的任何地方」
file: `scripts/lumos:17865-17895` — `_quote_rows`(quote-check 的唯一實作)只做「norm 後的引句是不是某份凍結快照 norm 後文字的子字串」的存在性檢查(`anchored = nq in hay or ...`),回傳裡只有 `quote`/`ok`/`too_short`,完全沒有行號、沒有「這行是不是新增的」概念,也不比對兩份快照
file: `scripts/lumos:18588-18622` — `cmd_quote_check` 同樣只吃「一份 report + 一份 spec/snapshot」兩個檔案做存在性比對,沒有「上一輪快照 vs 這一輪快照」的雙檔案輸入
quote-check 從設計上就是單檔案子字串比對,不是逐行定位、也不是跨版本 diff;要判斷「這句引句錨到的那一行,是不是這一輪凍結審材裡新出現、上一輪沒有的行」,需要新寫一段逐行 diff(找出引句落在哪一行、再拿這一行去跟上一輪整份快照比對是否存在)——這是一段全新的邏輯,不是「沿用」既有函式就能白拿到的能力,PRIOR-ART 段「不加新依賴」這句話在這一項上不成立。

## F3 逾半凍結審材是 git patch,「新增行」在 patch 格式下語意不明、逐行比對會被 hunk 偏移污染
severity: major
blocking: 是——照 S2 字面對 patch 格式的凍結審材做逐行存在性比對,程式行號因 rebase/上下文行數變動而漂移時,同一段未變動的程式碼會被誤判成「新增行」,或反過來把真正新增的行誤判成「上一輪也有」。
引句:「定位到的那行是新增行,而且這行不在上一輪凍結審材的任何地方」
file: `docs/.canary-log.jsonl`(機械數,`python3 -c "import json;exts={};[exts.__setitem__(r['snapshot_path'].rsplit('.',1)[-1], exts.get(r['snapshot_path'].rsplit('.',1)[-1],0)+1) for r in (json.loads(l) for l in open('docs/.canary-log.jsonl') if l.strip()) if r.get('snapshot_path')]; print(exts)"`)——現有帳上 `snapshot_path` 的副檔名分布是 `{'md': 765, 'patch': 693, '(none)': 1, 'diff': 4}`,即約 47% 的凍結審材是 git patch/diff,不是純文字說明檔
計劃全文(包含「做法」「誠實界線」兩節)只講「新增行」「這行不在上一輪凍結審材的任何地方」,沒有一處區分「凍結審材是完整原始碼/文件」與「凍結審材本身就是一份 diff」兩種情況。git patch 每次重新產生時,同一段未改動的程式碼常因為上下文行數(`-U` 參數)或 hunk 起始行號(`@@ -x,y +a,b @@`)不同而讓整段文字位移,逐行文字比對會把「同一段沒改的程式碼,只是這次 diff 的上下文多印了一行」判成新增行,反之亦然。計劃沒有講清楚「新增行」比對的對象是 patch 檔案本身的文字行,還是 patch 所代表的原始碼行,這兩者在 code-loop 實務上結果會不一樣。

## F4 S1 明確限定「代碼審迴圈」,S6 沒有同樣限定——設計審迴圈是否也印這段,條款自相矛盾
severity: major
blocking: 是——`loop status --disposal` 是 design-loop 與 code-loop 共用的同一支函式(`_loop_status_disposal`),S6 若照字面實作在這支函式裡,會對設計審迴圈也印出這段建議,但設計審迴圈的處置規則跟代碼審不同(例如 major 可以 accepted 附理由放行、code 迴圈則不行),計劃的建議規則(換做法/再一輪/附理由放行)是不是同樣適用於設計審,全文沒有交代。
引句:「當代碼審迴圈的輪數達到該分級上限且閘未過」
引句:「應印出與 S1 相同的一段,且不改變原本的過關判定與退出碼」
file: `scripts/lumos:18265` — `_loop_status_disposal` 的 docstring 開頭寫「[T4] 處置閘(design-loop重設計 三)」,函式本身不分 loop 前綴,design-loop 與 code-loop 的迴圈都會呼叫它
file: `scripts/lumos:9882` — `_roster_kind(loop_id)` 靠 `code-` 前綴分辨審查種類,證明兩種迴圈目前是同一套機械、只靠字串前綴區分行為;S6 沒有比照 S1 加上同樣的前綴限定詞
file: `scripts/lumos:18455` — 處置閘既有的「code 迴圈輪內有 major 以上的席,accepted 必須為空」判定就是照 `loop_id` 前綴 `code-` 特判,證明「代碼審」與「設計審」在同一支函式裡是刻意分流處理,而 S6 沒有這道分流語句
S1 的主詞明寫「代碼審迴圈」,但 S6 只寫「當輪數已達上限」,兩條放在同一份計劃、講的是同一段輸出,範圍卻不一致。若實作者照 S6 字面把印出邏輯掛在 `_loop_status_disposal` 裡不加前綴判斷,設計審迴圈(散文 spec,允許 major 附理由放行)也會被套上這套用「code 迴圈折入趨勢」推出來的建議規則,跟計劃自己在「為什麼不是把上限拉高」一節只舉代碼審例子的立論基礎脫鉤。

已看,無:計劃裡「印在哪裡」一節指名的兩個掛載點(`loop next` 的 cap-reached 分支、`loop status --disposal`)在現行程式碼裡確實存在且可掛(`scripts/lumos:10676-10678` 的 `emit("cap-reached", ...)`、`scripts/lumos:18265` 的 `_loop_status_disposal`),不影響過關判定與退出碼這條回退承諾在現行架構下可行(disposal 函式本就是先算完 fails 清單才在最後統一印結論,插入一段唯讀的印出不會動到 rc)。`--finding-class` 作為 `canary record` 的新選填旗標,在現有 `cmd_canary` 的參數風格(其他選填欄如 `capture_counts`/`clusters` 都是「不給不寫鍵」慣例)下沒有命名衝突,也沒有既有旗標同名,新增本身不影響舊帳讀取。cap 上限的分級表(`_TIER_PARAMS`:light=2、standard/high=3、legacy=6)確實顯示 cap-reached 至少要 2 輪才會發生,信號一「最後一輪 vs 第一輪」用兩個資料點做趨勢判斷在最小案例(light,2 輪)下不會除以零或索引越界。提早熔斷 S8「連續兩輪」在只有 1 輪時自然不會觸發(沒有「上一輪」可比),計劃沒特別寫這個起始狀態但也沒有因此產生錯誤行為,判定為「不影響」。

總結:severity 最高 major,blocking 共 4 條。
