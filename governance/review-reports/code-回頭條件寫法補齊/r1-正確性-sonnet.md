severity: minor

審查範圍:/tmp/code-revA-r1.patch(回頭條件寫法補齊)。實驗在 /tmp/codeRevA/x1 的複本做,沒動 repo。已跑 `python3.14 scripts/test_lumos.py -k revisit`(72 過 0 敗),並做了反向實驗:把 `_probe_lines` 的結案跳過拿掉,`t_revisit_closed_silences` 有 4 條翻紅(②④⑤⑥),所以那支測試的被測路徑確實走得到。

**C1 落單的引號會讓同一行後面所有句中 REVISIT 被當成「在引號裡」而放過**
severity: minor
blocking: 否 — 只會漏擋(放過一條死條件),不會誤擋;出現需要行內有落單的引號,頻率低
引句:「    return [i for i, q in zip(hits, inq) if i != head and not q]」
1. 輸入:一行 `他說 5" 螢幕 這裡 REVISIT:2026-10-05 x`(行內有一個沒成對的半形 `"`,例如英寸記號)。
2. 走到 `_revisit_quote_states`:半形引號用 `straight = not straight` 翻轉,奇數次後 `straight` 一直是 True,直到行尾都不會復原;`「` 開了沒收也一樣(`open_` 只被對應收引號清掉)。
3. 結果:`_revisit_misplaced` 回 `[]`,第一層不擋、doctor Z 段不列,這條句中 REVISIT 照樣是死條件。對照 `這裡 REVISIT:2026-10-05 x` 回 `[3]`。實測指令:`m._revisit_misplaced('他說 5" 螢幕 這裡 REVISIT:2026-10-05 x')` 輸出 `[]`。
4. 計劃〈做法〉1.1 與 S3 寫的是「一對引號裡面」,落單的引號不是一對;實作比計劃寬。S3 的測試只用成對的引號,沒蓋到落單的。
未能做成翻紅測試以外的更強重現(這不是 blocker/major,故不降級)。

**C2 驗收條款 S9 的 E5 提示那一半,綁到的測試沒有檢查它**
severity: minor
blocking: 否 — 行為本身正確(`t_doctor_revisit_reminder` 有逐字比對新句),只是條款與綁定測試對不上
引句:「- [S9] 當 Issue 改成結案值,列出還留著的回頭條件時 應 不列已寫合格 `[closed:]` 的那幾行,提示 應 提到 `[closed:日期 理由]` 寫法;doctor E5 的處理提示 應 提到 `[closed:日期 理由]` [test:t_revisit_closed_issue_listing]」
1. S9 綁的 `t_revisit_closed_issue_listing` 只跑 `set Issues/I status done` 與 `drift ack`,整支沒呼叫 `doctor`。
2. 把 `_head5` 的 E5 提示改回舊句「日期改下一次或刪行」,這支綁定測試仍綠;紅的是未被計劃綁定的 `t_doctor_revisit_reminder`。
3. 影響:條款宣稱「有綁測試守住」的後半句,實際守的是另一支沒列在條款上的測試;之後有人改掉那支測試的比對,S9 後半句就沒有任何綁定測試。

**C3 doctor Z 段的「N 處」實際數的是行數**
severity: minor
blocking: 否 — 只是顯示的數字偏小,不影響擋與不擋
引句:「        parts.append(f"寫在句中的 REVISIT {len(mis)} 處(例:{ex})——搬成獨立一行,要結案就在那一行加 [closed:日期 理由]")」
1. `mis` 來自 `_revisit_misplaced_lines`,它每行只回一筆 `(行號, 原文)`,不管那行有幾處。
2. 輸入 `a REVISIT:2026-10-05 x REVISIT:2026-10-06 y`(一行兩處句中):`_revisit_misplaced_lines` 回 1 筆,Z 段印「1 處」;第一層同一行會算出 2 個位置。
3. 計劃 S5 與同行前半段「寫在不評估的地方 N 處」也用「處」;前者是數行、後者 `dead` 也是數行,兩邊口徑一致但字面是「處」,一行多處時低報。

## 沒問題的項目

- 結案標記語法:`2026-13-45`、`20261003`、`2026-02-30`、理由不足、一行兩個、全形空白或 tab 隔開日期與理由,實測都得到 `errs`(擋下並說原因);合格者回原文。`[closed:` 緊貼日期或緊貼 `REVISIT:` 都落到既有的 `bad`,報格式不合。不比結案日期與今天,沒有時區問題。
- 可見文字:`[closed:` 的理由裡有行內程式碼,先剝掉再數字,與計劃一致。
- `_probe_parse` 遇到 `closed` 只跳過,夾在條件標記與 `[by:]` 之間時 `[by:]` 照讀(測試 ③ 也釘了)。
- 結案的讀取端:`_revisit_lines`(E5、Issue 結案列出)、`_probe_lines`(推送判定、drift scan、Z 段條件計數)、`_drift_ack_line_err` 都只認合格的 `closed`;寫錯的當沒寫,照到期、照評估。重新打開(拿掉結案標記)被點名,有測試。
- 舊行尾補括號:新兩條規則不在 `_NS_FRAG_KEY_RULES`,所以不被扣,與 S4 一致。
- 效能:`_revisit_misplaced` 一行 4 萬處 0.055 秒、一行 300 萬字 0.09 秒,線性。`_REVISIT_CLOSED_RE` 對 `[closed:` 重複幾千次且無 `]` 的怪行是平方級(8000 次約 2.9 秒),但跟既有的 `_PROBE_ANY_RE` 同型(8000 次 1.4 秒),不是這次新引入的新類別,也只在 REVISIT 行上跑。
- 存量掃描:把 `_revisit_misplaced_lines` 跑在這個 repo 的圖譜上得 68 行,與計劃量測一致;抽 25 筆人工看都是真句中(含「一行第二條」與刪除線)。`note-shape --diff 60a39f02..HEAD` 對這份變更自己的筆記無輸出,沒有自擋。
- 衍生資料:Z 段句中清單只接第一行、不與 `dead` 重算;`drift scan` 問題清單不變(測試 ④)。
- 治理帳:`rules` 只加在 `viol` 非空時;與格子欄位 `slots_*`、測試綁定欄位不同名,沒覆蓋。
- 測試被測路徑:各支測試都有前置斷言(獨立一行不擋、前提「每一處都判成句中」、`drift ack` 對照行照常表態、「拿掉前不擋」對照),反向實驗確認會翻紅。

## 固定席節點

- Systems/bound-tests-gate、guard-kill、授權與歸屬、lumos-cli-lifecycle、lumos-cli-read、design-loop、pitfalls-code-loop:這份 diff 沒有動它們宣稱的行為。bound-tests-gate 的合約是「綁的測試逐支真跑」,新增的 S1–S12 綁的 7 支測試名在 `scripts/test_lumos.py` 都存在(對 C2 見上,綁定存在但覆蓋有缺);guard-kill 的 rc 與 JSON 純度、授權檔白名單、SPDX 檔頭、re-inject 的 sentinel 區都不在改動路徑上;lumos-cli-read 的 search 排除 superseded 沒被碰;design-loop 處置閘第五步要求計劃條款綁測試,本案七個 `[test:]` 皆存在。
- Systems/測試假綠形態:合約要求還原翻紅釘配前置斷言。本案新測試符合;反向實驗(拿掉 `_probe_lines` 的結案跳過)會翻紅,證明被測路徑走得到。例外是 C2 那一半(E5 提示)沒綁在 S9 的測試上。
- 其餘「超出上限只列名」的節點(loop-convergence-recording、reversibility-governance-ledger、節點範圍與索引守衛、check-t-sentinel、lumos-deinit、cochange-guard 等):只有名字、沒有內文可讀,未逐篇判;這份 diff 沒有觸及它們的名稱所指的功能(去格式化、部署解除安裝、共改守衛等),僅 reversibility-governance-ledger 與治理帳有關,本案只在 note-shape 事件 `extra` 多一欄 `rules`,整行仍在 4 KB 內(測試 ②)。

最高 severity: minor
