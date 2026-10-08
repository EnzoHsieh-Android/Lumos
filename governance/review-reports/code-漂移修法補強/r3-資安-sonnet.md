severity: minor

## F1 補充指令貼上執行後,現存目錄名原樣印到終端(C1 控制碼、方向控制字元沒跳脫)
severity: minor
blocking: 否
引句:「    return (f"git --literal-pathspecs -c core.quotePath=off show --name-only --diff-filter=AR --format= {sha} -- {rr}/"」
佐證行:file: `scripts/lumos:28032`(修正後 clone 內 `_drift_c4_more_cmd`)
1. 證據頁自己列的目錄名有走 `_drift_c4_show_name`(Cf 跳脫)加 `_esc_clean`(C0 與 0x7f-0x9f 換空格);但超過 20 個時印給人貼的補充指令,最後一段是 `while ... printf '%s\n' "$d"`,直接把現存目錄名原樣輸出,完全沒過同一套消毒。
2. 重現:在臨時 repo 提交一個目錄 `governance/review-reports/code-<U+009B>31mEVIL<U+202E>abc/r1.md`,取 `_drift_c4_more_cmd(<該提交 sha>)` 印出的指令存成 sh 跑,`od -c` 輸出含 `302 233`(U+009B,CSI)與 `342 200 256`(U+202E,RLO),證據頁直接列同名目錄時 `_esc_clean(_drift_c4_show_name(..))` 已把這兩者換成空格與 `‮`。
3. 為什麼只到 minor:C0(ESC、換行)git 在 `core.quotePath=off` 仍會加引號,`[ -d ]` 對不上所以不印;能進終端的只有 C1 與 Cf。要有人把指令貼上執行才生效,且需要卷證目錄超過 20 個、名字是攻擊者提交的(整批匯入);UTF-8 終端是否把 U+009B 當 CSI 因終端而異。⚠ 未在真終端驗證逃逸序列的視覺效果,只驗證輸出位元組。

## 其餘角度判定(無 finding,附實測)
- 兩態讀取的路徑:`_vendored_state` 對 `f"{ref}:{p}"` 的 p 只來自常數 `_VENDORED_ALL`、ref 只有 `HEAD` 或空字串(`:路徑` 讀暫存區),不會被當選項或指到別處;`_json_at_ref` 同型。
- 單提交偽造兩態:改之前讀 HEAD 的清單與 HEAD 的檔,同一提交裡改清單+改檔只影響「改之後」那份,`+` 行不收回收表,只會變多報不會少報;刪除行要 HEAD 已對上才跳,單一提交躲不掉。改名路徑:刪除行照 `rename from` 來源、來源要是 HEAD 原封不動的工具檔,被刪的行就是工具原文,專案名稱躲不了。
- 提早離開:`any(p in diff_text for p in _VENDORED_ALL)` 用的是 diff 內文字串,檔頭與 `rename from` 都含 ASCII 精確路徑(不受 quotePath 影響),只會多算不會少算;缺 HEAD、git 跑不起來都落成「不跳」。
- 補充指令注入:sha 來自 `git log --format=%H`,其餘為常數;`"$d"` 在雙引號內不二次展開,`--literal-pathspecs` 已加。無注入。
- `lumos set` 佔位字改動:正規式為線性、只擋不放,無資安面。
- ⚠ 既有性質(非本次引入、且計劃列為刻意不做):清單檔本身在兩態都由專案控制,先一個提交把清單與工具檔一起改成一致、再下一個提交同樣做,即可讓後一提交的刪除行被跳過;守衛為 advisory(恆 rc0),不評等級。

## 圖譜鏡頭逐條判定
- 存量漂移守衛:c4 證據頁只列不寫檔的合約未動,不影響;佔位字擋下範圍縮小是放寬,不影響既有擋下語意。
- bound-tests-gate / guard-kill / design-loop / lumos-cli-read / lifecycle:diff 不動這些機制,不影響。
- 授權與歸屬:`_VENDORED_TOOLKIT` 未改,不影響。
- 測試假綠形態:只讀 patch,未見還原翻紅釘被移除,不影響。

最高等級:minor
