### ext-f1
severity: clean
引句:「parse 不到或不等=**拒絕入帳 rc2**,訊息指路」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:28`
說明:已解。新帳缺少合法 severity 行不再降為提醒，而是在 record 寫入前直接拒帳，原缺行逃逸門已封閉。

### ext-f2
severity: clean
引句:「寫側強制擋的是**疏忽轉錄錯**」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:41`
說明:已解。設計已把能力邊界限縮為防止疏忽轉錄，不再宣稱能抵抗編排者同時篡改報告與帳面的共謀；對抗性造假明確交由獨立審計層處理，威脅模型與控制能力相符。

### ext-f3
severity: clean
引句:「本案第一層是寫側前置驗證」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:19`
說明:已解。record 寫側在入帳前驗證報告最高 severity 並以 rc2 拒絕不一致，severity-check 則降為歷史補掃與縱深重驗，層次已依 r1 要求反轉。

### ext-f4
severity: clean
引句:「第一層(寫側)天生是硬擋(拒帳 rc2)」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:40`
說明:已解。保護不再依賴掃描器先抓到事件才升級；新帳從第一筆起即硬擋。另有固定日期盤點第二層告警，原本「逃逸因此永遠不觸發升級」的循環已不存在。

### ext-f5
severity: minor
引句:「parse 全部嚴格整行 `^severity:\s*(clean|minor|major|blocker)\s*$`」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:28`
說明:新洞。若 Python 以 MULTILINE 對整份文字執行此 regex，`\s*` 能吞換行，因此 `severity:` 與下一行的 `major` 仍可能跨行匹配，不完全符合「嚴格整行」承諾。應逐行套 fullmatch，或把空白限制為 `[ \t]*`，並補「標籤和值分成兩行不得匹配」fixture。這主要造成格式界線與規格不一致，尚未形成可把 major 降成 minor 的直接逃逸，因此列 minor。

### ext-f6
severity: clean
引句:「生效日前舊帳一律豁免(機械時間邊界,不靠人判「新舊」)」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:32`
說明:未發現新的時間邊界逃逸。現行 record 的 ts 是程式在寫入當下產生，不是呼叫者參數；依此落實常數比較，新寫入者不能自行偽裝成生效日前舊帳。實作時仍應釘出生效瞬間前後各一例並使用帶時區時間。

### ext-f7
severity: clean
引句:「生效日後的新帳=縱深重驗,抓到低報=**寫側有 bug**」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:29`
說明:掃描器降為第二層後定位一致：歷史相容性維持 advisory，新帳異常被定義為第一層失效並要求開 Issue，且不假裝事後撤銷已產生的 converged 結果。

### ext-f8
severity: clean
引句:「寫進既有 `roster-alerts.log` 同一寫入路徑」
佐證:file: `governance/review-reports/severity-scan/r2-snapshot.md:30`
說明:留痕已併入既有異常帳並以 kind 區分，另有固定日期按 kind 計數的消費條款，未再形成無讀者的孤兒檔。已掃過 record rc2、時間邊界、整行 regex、第二層掃描器、disposal 串接及 roster-alerts.log 留痕面；除 ext-f5 外未見新洞。

結論:否決解除。四項 r1 否決理由均已解除；新增 regex 邊界問題屬可在實作與 fixture 中局部修正的 minor，不足以維持整案否決。
