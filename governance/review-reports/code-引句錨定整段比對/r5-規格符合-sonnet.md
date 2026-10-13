severity: minor

整體:第一階段的實作大致照規格字面做到。我跑了 `-k quote_full_span`,82 條斷言全過。抽取規則、讀章、處置閘接住例外、寫側蓋章、擋下事件、`gov --stats` 四格、`quote-check --rule` 都對得上。

另外自己抽樣驗證的結果:
- 舊判準 `_quote_rows_legacy` 本體與基準提交 cb832b56 的 `_quote_rows` 逐字相同。
- 5000 個未閉合標籤抽完約 0.008 秒。
- 尾段落單只算給最近的那一條引句。
- 未閉合的列,`quote` 欄最多 200 字,超過加「…(截斷)」。
- 章值 `""`、`None`、`5`、list 都判失敗,沒有 traceback。
- `--compare-rules` 沒有殘留在 `scripts/`、`skills/` 和圖譜裡。

差異如下,全是 minor。

1. 程式裡留有已不成立的舊註解
severity: minor
blocking: 否
引句:「片段是審查席可控的文字(代碼審 r1 資安席):先截一段再用同檔的顯示消毒 _esc_clean(控制、雙向覆寫字元換空格;r2 架構對齊席:」
file: `scripts/lumos:25835`
- 這段是舊版註解。下一段註解和程式已改成 `_kill_esc` 的 `\uXXXX` 跳脫,兩段並排矛盾。
- 規格〈擋下事件〉寫的是 `_kill_esc`,程式也是,所以行為對、只有註解是殘骸。

2. 處置閘診斷行的註解宣稱「整行再過 `_esc_clean`」,程式沒做
severity: minor
blocking: 否
引句:「(要引號才加、開頭是 - 補 ./;r3 架構對齊席:不另寫一套),整行再過 _esc_clean(路徑裡的控制字元不印到終端;r3 資安席)」
file: `scripts/lumos:26522`
- 實際做法是路徑含控制字元就改印說明,不印指令,與規格一致。
- 這句註解是 r5 修補前的殘骸,會誤導下一個讀的人。

3. 驗證紀錄裡的斷言數沒隨拿掉比較模式更新
severity: minor
blocking: 否
引句:「代碼審四輪修補後 `-k quote_full_span` 是八支 95 條斷言(推送前以推送閘全套為準)。」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-13_引句判準第一階段推送前驗證.md`
- 現在實跑是 82 條,規格〈量測與留痕〉說 S6 與測試同步縮小。
- 驗證紀錄第 4 點仍把「比較模式路徑與讀檔與大小上限」列為變異對象,但那條路徑已拿掉。

4. 規格自己的兩處前後不一致,程式沒錯
severity: minor
blocking: 否
引句:「寫側求 `kind` 那一次與比較模式同一規則(r2 架構對齊席)」
file: `docs/lumos-toolchain-knowledge/Projects/引句錨定整段比對_計劃.md:73`
- 這句仍提「比較模式」。人裁拿掉它之後,規則只剩 `MemoryError` 照常往外丟,程式也是這樣。
- 〈兩階段上線〉寫第一階段帶「兩篇 Issue」,實際是三篇,多了「舊判準未閉合標籤二次方成本」。規格〈實務隱患〉有連到它,所以是〈兩階段上線〉那句沒更新。
- 〈同步改的地方·第一階段〉的測試替身只列兩個,實際還改了第三處 `t_gov_stats_review_yield`(期望字串多一格「引句判準 0」)。這是必要改動,規格沒列。

5. 標籤正規式在程式裡有兩份
severity: minor
blocking: 否
引句:「_QUOTE_LABEL_RE = r"引句(?:（[^）\n]{0,40}）)?\**[：:]\s*"   # 與 legacy 分支內的標籤規則同一條」
file: `scripts/lumos:25787`
- 規格只說「與現行標籤規則相同」,沒說要抽出常數。
- 舊判準因為要求一字不改,所以不能共用,新常數成了第二份。目前兩份相同。
- 這是規格沒寫、程式多做的點。沒有測試釘兩份相等,之後只改一邊會悄悄分叉。

總結:最高等級 minor,blocking 共 0 條
