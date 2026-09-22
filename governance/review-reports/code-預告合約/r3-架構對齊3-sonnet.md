severity: major

## F1 PLANNED_TAIL_RE 只有一個呼叫點,卻沒有跟同檔其他「窄範圍正則」一樣加底線私有前綴

severity: major
blocking: yes

引句:「PLANNED_TAIL_RE = re.compile(r"\s*\[watch:[^\]]*\]\s*\[due:[^\]]*\]\s*$")」

**觀察到什麼**:這次新增的 `PLANNED_TAIL_RE` 全檔只在一個地方真的被呼叫(`_guard_planned_line` 裡的 `PLANNED_TAIL_RE.sub("", m.group(1)).strip()`),而且呼叫它的 `_guard_planned_line` 本身就是底線開頭的私有函式。但這個新正則卻沿用了 `PLANNED_RE` / `WATCH_REF_RE` / `DUE_REF_RE`(這三支都是被兩個以上函式共用的「標記詞彙」,例如 `WATCH_REF_RE`/`DUE_REF_RE` 同時被 `cmd_context` 跟這個抽取區用到)那種**不加底線**的公開命名。

這檔案對「正則要不要加底線」其實有清楚的既有慣例,而且不是只有一兩個孤例:專門服務單一窄範圍用途、只有自己那一小塊邏輯在用的正則,一律加底線前綴——`_NODE_SUFFIX_RE`(`scripts/lumos:18016`,只在同一支節點名正規化的小函式用)、`_KEEPS_RE`(`scripts/lumos:5091`)、`_EXCL_LEAD_RE`(`scripts/lumos:5088`)、`_SEV_DECL_LINE_RE`(`scripts/lumos:6850`)、`_CLAUSE_LEAD_RE`(`scripts/lumos:4930`)、`_GIST_BAI_RE`(`scripts/lumos:9852`)全是這個模式。相對地,`INVARIANT_RE`/`DEBT_RE`/`TEST_REF_RE`/`AUDIT_REF_RE` 這些會被好幾支不同 `cmd_*` 函式共用的「標記詞彙」才不加底線。`PLANNED_TAIL_RE` 的實際使用範圍(單一私有函式、單一呼叫點)完全符合前者那一類的判準,卻用了後者的命名,等於在同一個正則家族裡引入第二套「什麼時候加底線」的判準。

**怎麼重現**:
1. `grep -n 'PLANNED_TAIL_RE' scripts/lumos` → 只出現三行:定義(`scripts/lumos:3679`)、搬移註解裡提到的名字(`scripts/lumos:10568`,純文字提及不算呼叫)、真正的 `.sub()` 呼叫(`scripts/lumos:10746`)。對照 `grep -n 'WATCH_REF_RE\|DUE_REF_RE'`,這兩支除了定義外,分別在 `scripts/lumos:11852` `scripts/lumos:11853` `scripts/lumos:11854`(`cmd_context`)又各被用了一次,證實它們是真的跨函式共用、公開命名合理。
2. `grep -n '_NODE_SUFFIX_RE\|_KEEPS_RE\|_EXCL_LEAD_RE' scripts/lumos` 可看到這幾支窄範圍正則都帶底線,佐證這個檔案裡「用途窄就加底線」是既有、一致的慣例,不是偏好。

**為什麼是 bug 而不是風格偏好**:任務鏡頭的判準是「引入第二種做法或跟同層對照相反才算 major」。這裡同一個正則家族(`PLANNED_RE`/`WATCH_REF_RE`/`DUE_REF_RE`/`PLANNED_TAIL_RE`)裡,前三支的「不加底線」有實際跨函式使用的事實撐著,是對的;`PLANNED_TAIL_RE` 只是抄了鄰居的命名外觀,底下的使用範圍其實跟 `_NODE_SUFFIX_RE` 這類窄範圍正則是同一種情況,卻沒有照那條線走——這正是跟「同層對照(其他窄範圍正則一律加底線)」相反,不是純粹排版或用字的偏好問題。下一個人看到 `PLANNED_TAIL_RE` 沒有底線,會誤以為它跟 `WATCH_REF_RE` 一樣是可以跨函式共用的標記詞彙,結果去別處直接拿來用,而它其實是綁死在 `_guard_planned_line` 內部字串還原邏輯上的實作細節(必須先經過 `PLANNED_RE` 命中、且只對「行尾剛好接兩個標籤」這個特定形狀有效)。

## 已驗證但沒發現問題的路徑(第三輪指定的另外兩點)

- **正則搬移是否造成定義順序或遮蔽問題**:`grep -n 'PLANNED_RE\s*=\|WATCH_REF_RE\s*=\|DUE_REF_RE\s*=\|PLANNED_TAIL_RE\s*=\|PLANNED_MARK\s*='` scripts/lumos` 確認每個名字全檔只定義一次(`scripts/lumos:3672-3679` 與 `scripts/lumos:10567` 的 `PLANNED_MARK`),搬移後沒有殘留舊定義、也沒有兩處重複定義互相遮蔽。Python 模組層級的 `def`/全域正則在檔案載入時全部先跑完,`cmd_guard_plan`(定義於 `scripts/lumos:10553` 之後)等函式的函式體要等被呼叫才執行,所以正則定義搬到檔案前段(`scripts/lumos:3672` 一帶)不影響任何呼叫順序,行為不變。
- **新測試 `t_guard_claim_with_bracket_tags_still_settles` 的寫法跟同檔既有測試一不一樣**:比對 `scripts/test_lumos.py:4326`(`t_guard_plan_creates_marker_and_node`,前一輪已審過、當基準)與這次新增的 `scripts/test_lumos.py:4354`,兩者都用同一套 `mkvault()`/`write()`/`run()`/`check()` 輔助函式、docstring 都是「一句話說明 → 空行 → 出身: 段落 → 翻紅釘: 段落」、`check()` 訊息都用①②③這種圈碼標步驟。這支新測試沒有引入新的斷言風格或新的測試骨架,寫法跟鄰居一致。
