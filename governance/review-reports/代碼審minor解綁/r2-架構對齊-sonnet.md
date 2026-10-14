severity: major

## 第 1 問:`--finding-source` 與 `finding_sources` 對照既有旗標

**大致對齊,有兩處形狀不同。**

- **對齊的部分:**
  - 旗標用 `action="append"`、`id=值` 切 `partition("=")`、錯誤一律 rc 2、訊息以「擋下:」起頭。這跟 `--finding-severity`、`--refute-verdict` 一致(`scripts/lumos:10852-10900`、`:55270-55274`)。
  - 寫側讀同迴圈別列帳也有先例,`--regression-set` 用 `_loop_records(env, loop)`(`scripts/lumos:10832`)。
  - 序號沿用 `_report_severities`,和 `reported` 同一支 parse,沒有另寫一套。
- **形狀差異一:鍵集合。**
  - `--finding-kind` 和 `--finding-severity` 要求鍵集合等於全集(`:10859`、`:10878`)。
  - `--refute-verdict` 是子集(`:10899`)。
  - 新旗標走子集,合理,但 accepted 內每個 id 都要有來源這條在閘側才查,和 `--refute-verdict` 把一致性在寫側就擋的做法不同。
- **形狀差異二:值型別與識別方式。**
  - 既有 dict 的值都是單一字串,`_gov_event_types_ok` 只驗字串(`:9732-9745`)。
  - 新欄位是 `dict[str, list[str]]`。設計說要同步加檢查,這項已寫到。
  - 報告在帳上一律用 `report_path` 全路徑加 sha(`_prov_check`),新欄位卻改用「檔名」識別第二種報告引用法。
- **漏列一處:** `canary record` 內「這些旗標要跟 `--findings-set` 一起給」的清單(`:10743`)沒有列 `--finding-severity`,設計也沒說新旗標要不要加進去。

severity: minor
blocking: 否
引句:「寫側只驗格式:id 要在 findings-set、檔名要是同輪某一列帳的 report_path 檔名、序號是正整數。」
file: `scripts/lumos:10743`
說明:帳上報告的標準識別是 `report_path` 全路徑加 sha,設計另用 basename。若不同目錄有同名報告,或同席重記沿用同檔名,basename 對不上唯一一列帳,設計沒寫撞名時怎麼辦。建議存 `report_path` 的相對路徑,或明寫撞名時擋下。同時要決定新旗標是否加進 `:10743` 的「須跟 `--findings-set` 同給」清單。

## 第 2 問:`_disposal_minor_release_step`

**形狀大致對齊,接線說明不完整。**

- **對齊的部分:**
  - 獨立函式、回 `"fail"/"ok"/"skip"`、自己印 `[disposal] …` 行,和 `_disposal_security_step` 一樣(`:26843`)。
  - 讀檔走 `_prov_check`,讀不到或 sha 不符就判不過,和資安席同語意(`:26888`、`:27177`)。
  - 讀整輪全部帳列,凍結閉包也已收「`round == rid` 的全部列」(`:1149`)。所以「含重記前舊報告」在閉包層成立。
  - `errors="replace"` 與資安席讀 patch 的寫法一致(`:26860`)。
- **未說明的接線點:** 既有步驟都有這幾樣,設計都沒寫。
  - 不適用時要印 `—(原因)` 並回 `"skip"`,資安席就是這樣(`:26851`)。
  - 步驟失敗要把名稱加進 `fails`。
  - 要加進成功橫幅的 `_extra` 清單(`:27365`)。
  - `_loop_status_disposal` 的 docstring 步序要更新。
  - 步驟編號:留痕是 ③、quote-check 是 ④,「放在留痕重驗之後」若插在 ④ 前會打亂既有編號,應明寫成 ⑨ 或接在 ⑧ 後。
- **訊息語意:** 既有步驟失敗訊息是「現象、在意的原因、接下來」三段(`:26894-26898`)。設計只寫「判不過並點名」,對不上這個慣例。

severity: minor
blocking: 否
引句:「等同一種寫法;只在上面第三種情況執行」
file: `scripts/lumos:27349-27366`
說明:實作者需要的接線清單(skip 行、`fails` 名稱、`_extra` 橫幅、docstring、編號)缺一不可,漏了橫幅就不會顯示新步驟。建議在設計補一行。

## 第 3 問:放行理由附 file:line,由閘驗存在

**有既有先例沒用上,而且這個做法會踩既有的回放完整性規則。**

1. **回放閉包規則(major)。**
   - 凍結閉包的既有規則:閘重讀的檔都要進閉包並版控,「回放的完整性檢查才蓋得到」(`:1146-1149`)。
   - 新步驟在閘裡讀 repo 工作樹的任意檔,驗它存在、行號不超過檔長。這些檔不在閉包。
   - 後果:放行當下通過的輪被凍結後,之後該檔被改短、改名或刪除,`loop replay` 會算出不同判定,被報成「邏輯漂移」。
   - 設計的 S11 只證明沒帶 `finding_sources` 的舊帳不變,沒涵蓋新帳。
   - 專案裡讀歷史狀態的既有解法是釘版本 `路徑@<提交>:行號`(`:28699-28705`)。設計要嘛要求釘版本,要嘛不在閘裡驗 repo 狀態。

2. **證據載體(minor)。**
   - 辯方降級的 file:line 目前已有兩處載體:
     - 設計審手冊只寫「審計紀錄標辯方反證:<file:line>」(`skills/lumos-design-loop/reference.md:146`)。
     - 同門「重現不到」證據則是 `--refuted-set` 加 `--intake` 重現表,寫側就驗整字加 HIT/MISS(`scripts/lumos:10804-10810`)。
   - 設計新增第三條路:把證據塞進 `accept_reasons` 自由文字,閘側再解析。
   - 一個專案裡出現兩種「辯方證據如何機械驗」的做法,且新法的驗證點(閘側)和既有法(寫側)不同。
   - 不需要新旗標,但可考慮改要求 `--intake` 裡對該 id 有 HIT 列,和 refuted-set 同形。

severity: major
blocking: 是
目標規則:「所以那些檔也要進閉包、要求進版控,回放的完整性檢查才蓋得到」
引句:「路徑在 repo 裡存在且行號不超出檔長(沿用 refcheck 的解析)」
file: `scripts/lumos:1146-1149`
說明:⚠ 我判斷這條是 major,但設計若打算把驗證改成釘版本或限制在凍結閉包內的檔,就不成立。

severity: minor
blocking: 否
引句:「本計劃只在處置閘多驗一件事:原報 major 經降級放行的 id,放行理由要附 file:line 佐證且找得到。」
file: `scripts/lumos:10804`
說明:既有的機械證據載體是 `--intake` 重現表加寫側整字驗證,新做法是自由文字加閘側解析。

## 第 4 問:判準與手冊落點

**判準落點對,同步清單有漏。**

- **判準放 `templates.md` §3,SKILL.md 第 4 步只放指標:對齊。**
  - SKILL.md:36 已寫席報告格式以 templates 為唯一來源。
  - 其他席位的錨(如架構對齊席 `templates.md:359`)也放在各自派工範本裡。
  - 設計對「第二種寫法」的處理是指回架構對齊席既有錨、不改動,和 `templates.md:359` 一致。
- **同步清單漏了這幾處,S12 的 `[manual:]` 也沒涵蓋:**
  - `skills/lumos-design-loop/reference.md:146` 仍寫「純記帳、不掛判閘」。
  - `scripts/lumos:55275` 的 `--refute-verdict` argparse help 同樣寫「純記帳不改判閘」。
  - `scripts/lumos:10884` 是設計列了的「寫側註解」,但同一段 `:10909` 還有第二處「本欄自稱純記帳」。
  - `scripts/test_lumos.py:11686` 的 docstring 寫著「純記帳不改判閘」。
  - `scripts/test_lumos.py:30603` 的 docstring 寫「severity==blocker ⇒ accepted 必空」,blocker 句不動,不用改。
  - 清單列了 `templates.md` 辯方範本那句(`:98`),這處是對的。
- 漏改的後果是下一個接手者在兩份文件之間猜哪個才算數。

severity: minor
blocking: 否
引句:「Systems/finding-refute 不再寫純記帳;scripts/lumos 舊訊息原句保留;散文設計審的 blocker 句不動」
file: `skills/lumos-design-loop/reference.md:146`
說明:S12 的驗收清單要加入 design-loop 的 `reference.md:146`、`scripts/lumos:55275` argparse help、`:10909` 第二處註解。

## 固定席節點

派工詞尾端沒有附固定席節點,不逐條判。

總結:不對齊共 5 條,其中 blocking 1 條
