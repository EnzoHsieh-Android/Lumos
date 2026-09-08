severity: blocker

### f1 總結白名單可夾帶 blocker 並低報
severity: blocker
blocking: 是
file: `scripts/lumos:4992`
引句:「if _SEV_SUMMARY_LINE_RE.search(ln):」
`severity: clean\n總結: severity: blocker\n` 會被跳過，`_report_normalize_issues` 回 `[]`、reported 回 `0`，因此可用帳面 clean/0 記入並走零發現處置。重現（已實跑純函式）：該輸入輸出 `summary [] 0`。

### f2 中文 refuted id 的「整字」比對其實可匹配前綴
severity: major
blocking: 是
file: `scripts/lumos:5454`
引句:「_pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(k) + r"(?![A-Za-z0-9])")」
`--refuted-set 甲=…` 在 intake 僅有 `| 甲乙 | MISS |` 時仍通過，因為 lookaround 只把 ASCII 字母數字當字界，能把不存在的 `甲` 偽裝成已重現列。重現（已實跑）：`bool(p("甲").search("| 甲乙 | MISS |"))` 輸出 `True`。

### f3 同秒兩次 rejected 仍被 gov 去重為一次
severity: major
blocking: 是
file: `scripts/lumos:4704`
引句:「"token": d.get("ts", "") if (d.get("gate") == "canary" and d.get("kind") == "rejected") else ""})」
寫側時間戳精度只有秒，兩次同 commit、空 nodes 的 canary/rejected 取得相同 token，gov 的五元去重鍵仍相同，違反「每次各算一筆」。重現（已實跑）：兩筆同秒 rejected 的去重結果為 `written=2 counted=1`。

### f4 UTF-8 BOM 報告被永久誤擋，normalizer 也修不了
severity: minor
blocking: 否
file: `scripts/lumos:5060`
引句:「text = Path(path).read_text(encoding="utf-8", errors="replace")」
首行為 `\ufeffseverity: clean` 時，首行規則與殘留掃描各報一次錯；`normalize_report_text` 回傳 `changed=0`，所以 `report-normalize --write` 無法移除 BOM。這會無故拒絕帶 BOM 的外部席報告。

### f5 refuted-set 的空項被靜默當成 none，ASCII 逗號理由又無法表達
severity: minor
blocking: 否
file: `scripts/lumos:5429`
引句:「for item in str(refuted_set).split(","):」
載體給 `--refuted-set " ,"` 時所有空項都被略過，跳過 intake 驗證後落帳為 `[]`，與明示 `none` 無從區分；已實跑解析輸出 `empty-refuted-set [] False`。反過來，理由 `f1=先跑 A, 再跑 B` 會把後半拆成無 `=` 的項而 rc2，介面沒有跳脫規則。

### f6 findings 超過 reported 的拒收沒有 rejected 事件
severity: minor
blocking: 否
file: `scripts/lumos:5592`
引句:「if findings is not None and findings > rec["reported"]:」
正規化報告有兩條、呼叫端填 `--findings 3` 時直接 rc2，卻沒有呼叫 `_gate_event_or_warn`；新段的「寫側擋下次數」少算此類撞牆。重現（已實跑精確分支）：輸出 `rc 2 gate_events 0`。

驗證：四支新增子集測試因唯讀沙箱沒有可用 temporary directory 而無法啟動；上述重現皆為已實跑的唯讀純函式／分支輸入。

### 圖譜鏡頭

`Projects/審查有沒有用記帳_計劃`：破壞。f1 可把明示 blocker 計成 reported=0，f2 可偽造 intake 對應，均違反其「拒收未正規化、整字驗、機器數」宣稱。

`Systems/loop-convergence-recording`：破壞。新增 S1/S2 的觀測數會接受低報與錯誤 refuted 證據，問閘尾端不再是可信漏斗。

`Projects/閘觸發帳統計_計劃`：破壞。f3 使同秒 rejected 少算，新增 gov 段宣稱的「擋下 N 次」不再可由原帳正確重算。

`Verification/2026-09-09_審查有沒有用記帳落地`：破壞。其驗證沒有覆蓋總結夾帶、CJK 邊界、同秒 token 碰撞或 findings-over-reported 的拒收留痕，故「落地」結論不足。

`Projects/loop數據收集_計劃`、`Projects/enforcement可觀測性_計劃`、`Systems/reversibility-governance-ledger`：受影響。它們依賴能如實回讀的治理帳；f1、f3、f6 令新增審查記帳資料不能作為可靠樣本。

`Systems/design-loop`、`Systems/judge-severity-gate`：不直接破壞既有處置閘／judge 合約；本 diff 沒改其合取判定，但其旁的新觀測帳受上述漏洞污染。

最嚴重 severity: blocker,blocking 條數 3
