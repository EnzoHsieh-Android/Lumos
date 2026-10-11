severity: major

審查範圍:/tmp/後端工程提問與證據擴充-r1.md 全文 211 行,逐節讀完。已修的首輪項目沒有重報。

**1. 〈做法 A「機械把關」〉與 S1:規格閘「不放行」與現行語意衝突**
severity: major
blocking: 是(照做會讓同一個閘有兩套互相矛盾的放行語意)
- 段落:spec 第 104 行、第 155 行(S1)。
- 問題:S1 要求高風險計劃有未決阻塞題時 `lumos spec-gate` 判不放行。現行風險高的路徑只印紅綠、不擋,函式最後恆回 0。
- 查證:file: `scripts/lumos:7800-7834` 的 `cmd_spec_gate` 對風險高只印「紅綠只印不擋」。只有相依回歸失敗和風險低的雙向門會回 1。
- 查證:這份計劃自己有 Q2 阻塞、待人,又有高風險訊號,是最先撞上的案例。
- spec 沒說要改高風險那條路徑,還是新增第三種擋法,所以這個新規則放在哪裡不明。

**2. 〈C「pass 要有證據」〉與 S8:驗證筆記 pass 多了第二套判定**
severity: major
blocking: 是(新舊兩套判定並存,舊的又不改)
- 段落:spec 第 123-125 行、第 162 行(S8)。
- 問題:新建的驗證筆記要設 pass,證據帳就得有 `evidence run` 寫下的 PASS 列。這等於要求所有新驗證筆記都改走新指令。現行的 pass 來源有:`spec-gate` 真跑 `[test:]` 並留痕、`guard kill` 的 kill-log、`ci-wait`、`signoff`,spec 沒有一個豁免。
- 查證:file: `scripts/lumos:8250` 的 `cmd_signoff`,以及 `scripts/lumos:7278` 的 `_spec_gate_record`(留痕含 `tests` 和 `clause_sha`)。這些路徑現在就讓驗證筆記合法 pass。
- 查證:file: `scripts/lumos:18475-18484` 的 `_STATUS_ENUM`,驗證筆記共 295 篇。多數是圖譜實驗和文件類,沒有可 `evidence run` 的指令。2026-10-19 之後每篇新驗證筆記設 pass 都會被擋,除非硬跑一個假指令湊 PASS 列。

**3. 〈B 能力清單與 `lumos capabilities`〉:自建權限分類,而且沒有任何東西執行它**
severity: major
blocking: 是(spec 自己說權限「不自建」,卻又建了一張)
- 段落:spec 第 110-112 行、第 165 行(S11)、第 174 行。
- 問題:PRIOR-ART 寫「工具權限用 Claude Code 原生的 permissions,不自建」,卻另建 READ/WRITE/EXECUTE/ADMIN 四級的能力清單和驗證器。它只檢查自己宣告的 config,沒有任何一次真實工具呼叫會去查它。S11 只測 config 驗證,擋不到任何實際呼叫。
- 問題:第 174 行把 S11 當成「不可逆」隱患的處理,但它擋不住實際操作。
- 問題:現在沒有任何後端 MCP(spec 第 88 行自承),Q4 還是待查。這是為「以後可能用到」預先建的指令。
- 查證:file: `scripts/lumos:50576` 之外,整份腳本沒有 `capabilities` 設定欄位的讀寫,是全新概念。`.lumos/config.json` 現有欄位(`test_profile`、`platforms` 等)都是 lumos 自己執行時會讀的,這個欄位沒有人讀。
- 該刪的是 `lumos capabilities` 指令和 `capabilities` 區塊,保留一段「寫入類 MCP 在 Claude Code 設 `permissions.ask`」的說明文字就夠。

**4. 〈RETIRE-IF〉:量法與設計本身矛盾,而且量不到**
severity: major
blocking: 是(撤除條件會對正常運作誤判,或永遠不成立)
- 段落:spec 第 86 行,對照第 101、183 行。
- 問題一:①寫「超過八成題目是自答且沒連決策或證據」就撤。但「先查後問」(第 101 行)正是要 AI 把能自查的題自答,自答只需附出處、不需連結。Q3 自己就是自答沒連結。設計預期的健康狀態會被判成該撤。
- 問題二:②「8 週內少於 10 筆證據列」。示範 repo 的 S12、S13 加開發時的試跑就會超過 10 筆,條件幾乎不可能成立,撤不掉。
- 問題三:③「誤擋比真擋多」。沒有任何帳記錄擋下事件,也沒有「誤」的判法。
- 問題四:量法寫 `lumos gov --stats`,但 `cmd_gov` 的載入來源是 gov、local、signoff、kill、canary、ci 等帳,沒有證據帳,也不看〈待決問題〉。
- 查證:file: `scripts/lumos:8718-8730` 的 `cmd_gov` 各 `load(...)`,沒有 evidence 帳。
- 另外,「值得建」的唯一直接證據是反例:同類實驗(`設計審後端失敗與未知狀態_計劃` 2026-10-02)沒過門檻(spec 第 81 行),spec 自己承認。

**5. 〈C `evidence check`(S9)、D 第 7 關、A 機械把關、RETIRE-IF ③〉:同一件事有三個名字,兩處沒有落地條款**
severity: major
blocking: 是(同一個「交付前檢查」有 `evidence check`、`spec-trace [evidence:]`、一段「交付前證據檢查」三個說法,範圍沒寫清)
- 段落:spec 第 104、137、163-164 行。
- 問題:
  - S9 的 `lumos evidence check` 只查重複失敗。
  - S10 的 `spec-trace [evidence:]` 查 PASS 列存在。
  - A 說的「交付前證據檢查」要查「標了要驗的已決題沒有證據列」,這一條沒有任何 S 條款,也不是 `spec-trace`。
  - E 說 BLOCKED「不准把計劃設成 done」,也沒有對應 S 條款。S7 只擋驗證筆記設 pass。
  - RETIRE-IF ③ 量的就是這個沒有定義的東西。
- 查證:file: `scripts/lumos:8168` 的 `cmd_spec_trace` 是現成的條款追溯。把 `[evidence:]` 併進它、`evidence check` 併進它(一個指令兩種檢查)即可,不需要兩個入口加一個未命名的檢查。

**6. 〈E 停止條件〉:雜湊規則可刪**
severity: minor
blocking: 否(沒有第二套機制,只是多餘)
- 段落:spec 第 143-144 行、第 163 行(S9)。
- 問題:「連續兩列 FAIL 且摘要雜湊相同就停」被「累計三列 FAIL 就停」完全包含,只提早一次。去掉時間與路徑再雜湊是一段要維護的正規化,很容易誤判。具體場景:兩次失敗輸出含不同的暫存目錄或埠號,雜湊不同,規則靜默失效。
- 查證:file: `scripts/lumos:12139` 的 `_TIER_PARAMS` 已有輪數上限加交人的前例,只用計數。

**7. 〈A 決策紀錄擴三欄〉與 S4:與既有欄位重複**
severity: minor
blocking: 否
- 段落:spec 第 106 行、第 158 行。
- 問題:`--rejected` 重複 `why_chosen` 的「不選:」慣例。這份 spec 自己的 d1、d2 就是把不選寫在 `why_chosen` 裡(第 47、52 行)。`--answers Q3` 是 Q 行 `→ #dN` 的反向連結,S1、S2 檢查的就是 Q 行那一邊。`--by` 在這個流程裡實際上都是人。
- 查證:file: `scripts/lumos:20434-20470` 的 `cmd_decision_add` 目前只有 `content/decided/context/why`。S4 也不在「先量再接」的門檻裡(第 105、193 行只管 S1-S3),A 沒過實驗它仍會建。

**8. 〈A 時機 `--stage`〉:沒有驗收條款**
severity: minor
blocking: 否
- 段落:spec 第 103 行,對照第 155-167 行。
- 問題:`--stage` 參數和「風險面→階段」對照表是新增的,但 S1-S13 沒有一條測它。S3 只測排序和三題上限。六個階段值裡,規格閘只帶「需求、架構」,實作靠人手動,真正會被機器用到的只有一兩個值。
- 查證:file: `scripts/lumos:42832` 的 `cmd_pitfalls` 簽章沒有 `stage`。

**9. 〈A 待決問題格式〉:`答` 與 `狀態` 兩個欄位重複**
severity: minor
blocking: 否
- 段落:spec 第 97-99 行、第 181-185 行。
- 問題:`[答:人]` 與 `[狀態:待人]`、`[答:自查]` 與 `[狀態:自答]` 在 Q1、Q2、Q3、Q5 同時出現,同一資訊寫兩遍。具體場景:改了其中一個忘了另一個,S2 的 lint 只驗已決和延後,兩欄矛盾不會被抓到。

**10. 〈S13〉:與 kill-log 重疊**
severity: minor
blocking: 否
- 段落:spec 第 167 行、第 68 行。
- 問題:「拿掉保護、測試紅、還原後綠」就是 `guard kill` 的職責,第 68 行也這麼寫。S13 又要求 `evidence run` 另記一份前後對照,等於同一次破壞測試在 kill-log 和證據帳各記一遍。
- 查證:file: `scripts/lumos:17527-17540` 的 kill-log 寫入含 `commit`、`verdict`、`test`。

**實務隱患鏡頭(payment / external-send / prod-irreversible)**
- payment:無。本案無付款路徑(spec 第 175 行),查 `scripts/lumos` 的新增面也沒有碰金流。
- external-send:疑點但不標。`evidence run` 代跑任意指令(第 117 行),「只打 localhost」只寫在示範 repo 的 k6 設定(第 176 行),指令本身沒有網路限制。具體失敗場景給不出本案會用到的,故不列為 finding。
- prod-irreversible:見 finding 3。能力清單的「禁止正式環境 WRITE」只驗設定檔,不擋真實呼叫。

最嚴重 severity:major,blocking 共 5 條(finding 1、2、3、4、5)。

固定席逐條判(`後端工程提問與證據擴充_計劃.md` 節點宣稱的行為與合約):這份計劃自己的節點是 `status: doing`,沒有 ★INVARIANT★ 合約行。對它宣稱的行為判斷如下:
- 「不新增節點類型、薄層掛既有機制」(d2):被 finding 2、3 弱化。pass 判定和權限分類實質上各多了一套機制。
- 「舊否決(不做模板化盤問)作廢」(d1):不影響既有合約,但 RETIRE-IF ① 無法判定何時復活(finding 4)。
- 「壓測毫秒數不進推送關卡」:不影響,spec 沒有把證據檢查掛進推送閘。

## 補引句(編排者續談請同席補,只補不改判)

- F1 引句:「規格閘讀這一節——還有標阻塞、狀態是待查或待人的題目,規格閘不放行」
- F2 引句:「2026-10-19 之後新建的驗證筆記,狀態要設成 pass,證據帳裡至少要有一列指向它、結果 PASS」
- F3 引句:「工具權限用 Claude Code 原生的 permissions(allow/ask/deny)與 PreToolUse 掛鉤,不自建」
- F4 引句:「消費專案的計劃裡,超過八成的題目狀態是」
- F5 引句:「交付前證據檢查讀這一節——標了要驗的已決題沒有證據列,不放行」
- F6 引句:「同一條款連續兩列 FAIL、而且失敗原文摘要(去掉時間與路徑後的雜湊)相同」
- F7 引句:「加選填的 `--answers Q3`、`--by <誰>`、`--rejected」
- F8 引句:「現行 `lumos pitfalls <計劃>` 沒有階段概念、一律全列」
- F9 引句:「- [Q3] <問題> [類:併發][階段:實作][答:人|自查|工具][阻塞][狀態:待人] → <決策或證據連結>」
- F10 引句:「還原保護後同一測試與相關回歸應留下 PASS 列,交付報告應從證據帳產生前後對照」
