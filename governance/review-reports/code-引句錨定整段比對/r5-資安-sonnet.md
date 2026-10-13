severity: minor

我沒找到能讓編造引句錨定的繞過,也沒找到 `_kill_esc` 之後還能寫進治理帳的終端控制字元。下面兩條 minor 是實測出來的。

**1. `quote-check` 文字輸出把審查席的引句原樣印到終端**
severity: minor
blocking: 否
引句:「print(f"  {mark} #{i} 」
file: `scripts/lumos:26546`(base 版本 `cb832b56` 已有這行,不是這次新增,但 patch 內可見,見 `r5-snapshot.patch:765`)
- 誰、從哪、送什麼:不可信的審查報告裡,「引句:」後面放 ESC/OSC 序列或換行。
- 走到哪:處置閘判失敗時會印 `診斷:lumos quote-check <報告> --spec <快照> --rule <章>`。這次新增的診斷行本身是乾淨的,但它叫人去跑的 `quote-check` 文字模式,會對引句取 `[:60]` 後原樣印出。
- 實測(報告含 `\x1b]0;pwned\x07`,legacy 與 full-span-v1 都一樣):輸出裡的 ESC 與 OSC 原樣出現,不是跳脫文字。
- 偽造畫面(full-span-v1 的多行引句):前 60 字內放換行,就能印出假的 `✓ #2 「…」` 與 `✅ 全數錨定:報告裡每句引…` 行。
- 拿到什麼:騙讀者,或操控終端標題與游標。真正的 `⛔` 行和 rc=1 仍在,所以不影響閘的判定。
- 建議修法:列印時對 `r['quote'][:60]` 套同檔既有的 `_kill_esc`。

**2. 引句比對成本隨引句數乘上快照大小,報告作者能拖死閘與寫側**
severity: minor
blocking: 否
引句:「anchored = nq in hay or nq.replace(" ", "") in hay_ns」
file: `scripts/lumos:25855`
- 誰、從哪、送什麼:審查席交一份有數萬條「引句:「(12 個快照裡不存在的字)」」的報告。
- 走到哪:每條引句各對整份快照做兩次子字串搜尋,沒有條數上限。
- 實測(2MB 快照):90KB、5000 條要 7.2 秒;360KB、20000 條要 29 秒,兩種判準都一樣。
- 拿到什麼:寫側擋下事件的 `other_rows` 會再算一次,處置閘和回放也各算一次,所以成本是倍數。
- 其他病態輸入都是線性:10 萬個未閉合標籤 0.15 秒,50 萬層巢狀 0.17 秒。
- 這個問題在 legacy 就有,不是這次修補造成的,但 `_QUOTE_MALFORMED_CAP` 只封了未閉合那條路。

**查過、沒開槍的項目**
- 新判準繞過:試過 LIFO 配對劫持、型別不符的 `』`、`covered` 吞掉標籤、尾段落單收尾引號。
  - 編造的文字不是被併進必須錨定的整段,就是被判 `stray` 或 `unclosed`;`stray` 掃描只看到下一個標籤為止,整體線性。
  - 沒找到可構造的繞過。
- 擋下事件片段:`_kill_esc` 逐字處理 Cc、Cf、Zl、Zp、Cs,片段排在 note 最後,偽造欄位出現在第一個 `report=` 之後。
  - 殘留:字面寫出的 `\u202e` 和跳脫結果無法區分(不是無損),只影響閱讀,不能操控終端。
  - 殘留:note 的 `report=`、`loop=`、`auditor=` 沒有跳脫。但寫入的是 JSON,控制字元會被逸出,這些值也來自編排者的命令列,不是審查席。
- 處置閘診斷行:`_qrule` 只能是 `_QUOTE_RULES` 兩個值,路徑含 Cc、Cf、Zl、Zp、Cs 或超過 1000 字就改印說明,其餘過 `_drift_sh`。`_qerr` 用 `!r`,控制字元會被逸出。
- 手改帳上的 `quote_rule`:未知值、`null` 都判失敗;刪掉該欄位會降成 legacy。
  - 但改 `report_sha` 之類的欄位同樣是改帳,走的是同一個信任邊界,所以不算新洞。
  - 帳有凍結列指紋(`all_row_shas`),凍結後的手改會被抓到。
- 拿掉比較模式:在 `scripts/lumos` 和 docs 都搜不到 `compare-rules` 殘留。
  - `--rule` 有 `choices` 限制。
  - 不可信路徑的入口只剩原有的 `--report`、`--spec` 和 `--snapshot`。

我建的實驗目錄已刪除,沒有改 repo。

總結:最高等級 minor,blocking 共 0 條
