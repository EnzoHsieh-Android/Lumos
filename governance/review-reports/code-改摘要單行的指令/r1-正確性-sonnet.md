severity: minor

審查方式:把 diff 對上 `scripts/lumos` 現行實作,用 mktemp 目錄建假筆記、跑 `lumos summary-line` 實測(實驗腳本在 scratchpad/x/exp.py,沒動 repo)。實測過且沒問題的:`summary: >` 與 `|` 都能改;`--nth 0` / 負數擋下;全形空白片段可換;舊片段含 `summary:` 擋下(找不到);片段縮排被改掉(`  KEY:甲` 換成 `KEY:甲`)寫入自驗擋下、原檔不動;新片段是 `status: done` 自驗擋下;CRLF/BOM 由 `load_raw_for_edit` 擋;`updated` 在摘要之後或之前都對;刪第一行、刪重複行都對;寫入走暫存檔再換名,失敗原檔不動;鎖從讀包到寫(`_summary_line_locked` 整支在鎖內)。

## F1 新片段含單獨的回車字元(CR)或 Unicode 行分隔字元,寫進檔案後毀掉開頭欄位
severity: minor
blocking: 否 判準:要人刻意餵特殊字元才觸發,且 lint 與自驗都放過,但寫進去的檔在標準 YAML 讀法下會斷行。

file: `scripts/lumos:18024`(`cmd_summary_line` 的輸入檢查),`scripts/lumos:18232` 一帶(`_summary_line_locked`)。
場景:`summary-line Systems/Pay 乙 $'a\rb'`(新片段含單獨的 `\r`,不含 `\n`)。輸入檢查只看 `"\n"`,放行;`atomic_write_verify` 的 check 用 `split("\n")` 與 `strip()`,也讀得通;實測 rc0、`lumos lint` 回 0 問題,但檔案裡摘要那行中間夾了一個裸 CR(用 `read_text` 看會被換成換行所以看不出來,要看 bytes)。Obsidian 或標準 YAML 把裸 CR 當換行,`b` 會落在第 0 欄,開頭欄位壞掉。` `、`\x85`、`\x0b` 同樣被原樣寫進去(實測 rc0)。計劃 S3 寫的是「新片段含換行應擋」,這裡只擋了 `\n`。
引句:「if not old or "\n" in old or "\n" in (new or ""):」
佐證:`load_raw_for_edit` 只拒 `\r\n`(`scripts/lumos:17842` 起),裸 CR 不在它的防線內。建議改成拒絕任何 `str.splitlines()` 會切開的字元。

## F2 舊片段與新片段讓整行 strip 後不變時,rc2 但訊息講錯原因
severity: minor
blocking: 否 判準:只是沒寫入(安全方向),錯在訊息誤導。

file: `scripts/lumos:18270`(`check` 內 `return n == before_n - 1 if delete else n == before_n + 1`)。
場景:
- `summary-line Systems/Pay 甲 甲`(新舊相同)。
- `summary-line Systems/Pay 乙 "乙 "`(只改行尾空白)。
兩個都是 `new_line.strip() == old_line.strip()`,`before_n` 已經把這一行算進去,換完 n 沒增加,check 判敗,印「寫完讀回來檢查,summary 的值跟要寫的不一樣,這次寫入不算成功」,實測 rc2、檔不動,但使用者看到的是像寫入壞掉的訊息,而且前面已經印了「改前/改後」。同族:check 的 `before_n` 數整個開頭欄位(`lines[1:e]`),n 只數 summary,新行或被刪行的文字剛好等於別的欄位的一行(例如 `- type/system`)時會假敗,同樣只是安全方向的誤報。
引句:「before_n = sum(1 for ln in lines[1:e] if ln.strip() == target)」
佐證:應在寫入前先判 `new_line == old_line` 直接講「沒有變化」;`before_n` 只數摘要區那幾行即可跟 check 對齊。

## F3 摘要寫成單行值 `summary: 一句` 時,計劃寫的「那一行本身算唯一一行」沒實作
severity: minor
blocking: 否 判準:計劃明講支援的輸入被誤報「找不到」,但沒寫壞東西。

file: `scripts/lumos:18196`(`_summary_line_hits`)、`scripts/lumos:28648`(`_notelines_regions` 把 `summary:` 那一行標成 other)。
場景:筆記是 `summary: KEY:一句`,執行 `summary-line Systems/Pay 一句 二句` → rc2「摘要裡找不到「一句」」(實測)。使用者會以為字不在摘要裡。計劃〈做法〉1 與天花板都寫單行值要支援;測試也沒有一支覆蓋。另外 `delete = ... or new_line.strip() == "summary:"` 這個條件在現行區域判定下走不到(`summary:` 那行永遠不是 summary 區),是死碼。
引句:「delete = not new_line.strip() or new_line.strip() == "summary:"」
佐證:要嘛實作單行值,要嘛擋下時講「摘要是單行值,這個指令不支援」並修計劃。

## F4 測試覆蓋有洞,現有六支沒有假綠但釘不住上面幾條
severity: minor
blocking: 否 判準:現有測試各自能翻紅所宣稱的變異,缺的是未覆蓋輸入。

file: `scripts/test_lumos.py` 新增 `t_summary_line_*` 六支。
- `t_summary_line_verify` ① 是 monkeypatch `atomic_write_verify` 拋例外,證明「例外 → rc2、不動」,但沒走真的 `check` 回 False 那條;`check` 內的 `before_n ± 1` 算式完全沒有測試釘(F2 的新舊相同就是那條)。
- 沒有測:單行值摘要(F3)、新片段含 `\r`(F1)、新舊相同、舊片段含前導縮排(自驗擋下那條實際有效,但沒釘)、`--nth` 在多行(不同行)候選上指定第二行。
- `t_summary_line_replace` ③ 的 `"WHY:用 A 方案" in r.stdout` 只靠「改前」那行就成立,不證明「改後」印對;但 ① 已驗內容,所以只是冗餘。
引句:「check("③印改前改後", "WHY:用 A 方案" in r.stdout and "WHY:改用 B 方案" in r.stdout, r.stdout)」

## 圖譜鏡頭
這次沒附固定席節點(派工詞說明鏡頭超時),不逐條答。就 diff 內可見的部分:新增計劃筆記寫回 `Systems/lumos-cli-write`,指令總數(ARCHITECTURE.md、reference.md、INDEX.md)都同步成 82;沒看到這份 diff 破壞既有指令行為或合約(只新增一個指令與 `main` 一個分支)。角色卡:尾端沒附,略過。

總結:max severity minor,blocking 0 條(F1-F4 皆為 minor、非阻擋)。
