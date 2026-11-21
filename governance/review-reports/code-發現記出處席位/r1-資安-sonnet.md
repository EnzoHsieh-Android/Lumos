severity: minor

審查範圍:diff 共 998 行,我讀到第 683 行,涵蓋全部正式碼(`scripts/lumos`)與筆記。其餘是 `scripts/test_lumos.py` 的測試改動,已用 grep 查過 `LUMOS_FINDING_SEAT_SINCE` 在測試檔裡的 4 處用法。

## ① 提示注入

severity: minor
blocking: 否
標「推論」:攻擊路徑的第一步依賴使用者自己或 AI 在記帳時把惡意席名寫進 `--auditor`,不是外部可直接送進來的。
- 誰:能控制帳上 `auditor` 欄的人(使用者或照常操作的 AI),或某一席報告帶進來的席名字串。
- 從哪裡:`canary record --auditor <含換行與指令字樣的席名>`。
- 送什麼:席名中帶換行,後面接「請改用 --force…」這類假指示。
- 拿到什麼:`_finding_seat_write_block` 擋下時,把帳上所有 `auditor` 原字串用 `', '.join(sorted(known.values()))` 印到 stderr。下一個讀這段訊息的 AI 會看到那段假指示。
引句:「print(f"  這一輪帳上現有:{', '.join(sorted(known.values())) or '(還沒有)'}", file=sys.stderr)」
- 判斷:使用者的威脅模型只顧單人且「外來文字回顯放行」,這裡回顯的是自己帳上的欄位,所以只算縱深防禦。若要補,對回顯的席名做 `repr` 或去控制字元即可。
- 同族:`finding-seat-missing`、`finding-seat-unknown` 兩個 blocked 事件把 `loop` 與 `auditor` 原樣拼進事件字串,同樣沒有逸出。

其餘已看,無:`--finding-seat` 的 id 與席名經 `{item!r}` 或 `{nm!r}` 回顯,沒有直接把外來文字送進派工詞。`loop next` 範本只印固定字串 `--finding-seat <id=席名>`。

## ② 讀寫與執行越界

已看,無。
- 本案沒有新增讀寫檔案、subprocess、shell 插值、網路或下載的程式。`_finding_seat_parse`、`_finding_seat_write_block` 只操作記憶體裡的 `rows` 與 `rec`,最後走既有的帳本寫入路徑。
- 新增的 `_render_seat_noise` 只讀 `gov` 已載入的列。
- 密鑰與信箱:diff 裡沒有。計劃與筆記只有公開的論文網址。
- `.lumos/lint-waivers.json` 新增的 waiver 只涉及 C901 複雜度,沒有越界。

## ③ 非刻意、一步就能繞過的守衛

**本案提示的判斷:`LUMOS_FINDING_SEAT_SINCE` 殘留在 shell 裡算③,但實際可達性低,定為 minor,blocking 否。**

severity: minor
blocking: 否
- 誰:使用者本人或照常操作的 AI。
- 從哪裡:在同一個 shell 先跑過會把這個環境變數匯出的操作,例如手動 `export`、sourced 的 rc 檔或腳本、某個把它匯出的 wrapper。之後在同一個 shell 跑 `lumos canary record … --findings-set … `(代碼審載體、沒帶 `--finding-seat`)。
- 送什麼:環境裡殘留的 `LUMOS_FINDING_SEAT_SINCE=9999-12-31T00:00:00+08:00`。
- 拿到什麼:`_finding_seat_required_block` 的必填被整個關掉。載體不帶 `--finding-seat` 也 rc 0 過關,也不會留 `finding-seat-missing` 的 blocked 事件。逐席沒用率資料因此靜默缺漏,而且沒有任何提示。
引句:「k = _loop_ts_key(os.environ.get("LUMOS_FINDING_SEAT_SINCE", "").strip())」
- 為什麼可達性低:測試檔用 `_os_mod.environ.setdefault(...)`,只改測試程序自己的環境,不會流回使用者的 shell。我沒看到任何會把它匯出到互動 shell 的程式。所以殘留只會發生在使用者手動匯出的情況。
- 為什麼仍要報:既有慣例是 `LUMOS_SKIP_*` 殘留要靠留帳補救,而這個變數是正式程式路徑會讀的覆寫,而且完全靜默。
- 防禦建議(任選其一):
  - 覆寫生效時在 stderr 印一行「LUMOS_FINDING_SEAT_SINCE 覆寫中,必填已推遲」。
  - 只在測試旗標存在時才讀這個變數。
  - 覆寫值晚於現在時,仍在治理帳留一筆事件。
- 對照:計劃自己承認這是「帳上時間比對裡第一個有環境變數覆寫的」。這正是它比 `_SECURITY_SEAT_SINCE` 多出來的繞過面。

其他非刻意繞過已看,無:
- 空帳、時間壞掉(`_loop_ts_key` 回 None)、`finding_seats` 型別壞掉三種情況都判成擋下,或在處置閘當作沒有,沒有意外放行。
- 沿用生效日前就開的迴圈編號不必填,這是計劃明寫的「不回溯」,不算守衛被意外繞過。

最後一行總結:max severity = minor(皆 blocking: 否)
