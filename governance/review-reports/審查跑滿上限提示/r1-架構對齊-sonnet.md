severity: major

## F1 「每輪折入數」已有現成純函式在算(_review_yield_round 的 F 欄),計劃沒提也沒打算沿用

severity: major
blocking: 是
引句:「折入數用每輪彙總那筆的折入清單,不用每席的 findings 加總也不沿用 verify-progress 的 findings_trend」

計劃在「二、印什麼」定義的「每輪折入數」= 那一輪彙總那筆帳的 `folded_set` 條數(`那一輪彙總那筆帳的折入清單條數`)。這個數字已經有現成函式在算,而且是逐輪都會叫到的:

- file: `scripts/lumos:7364` — `def _review_yield_round(rows):`,docstring 自己就寫明「純函式,disposal 尾與 gov --stats 共用」,是特意留給多處呼叫的共用計算。
- file: `scripts/lumos:7381` — `F = len(carrier.get("folded_set") or []) if carrier else None`,跟計劃要印的「折入清單條數」逐字同義(同一顆 `folded_set`、同一種取長度算法)。
- file: `scripts/lumos:18549-18552` — `_loop_status_disposal` 尾端已經每輪呼叫 `_review_yield_round(latest)` 並印出 `[disposal] 審查有沒有用(觀測,不進合取): 席位報 N(機器數)→ 存活 M / … → 折 F / 放行 A`,`latest` 正是計劃想逐輪取用的那個「同一輪的帳列」分組(`groups.items()`,scripts/lumos:18293-18310)。

計劃的 WHY(第 13 行)明確交代了為什麼不沿用 `findings_trend`(各席原始報數、會重複算)和不沿用「每席 findings 加總」,理由成立、也記了出處(三席獨立指出)。但同一份現存函式 `_review_yield_round` 算的正是計劃想要的東西(彙總帳的折入清單長度,不是各席原始報數),計劃完全沒提到它、也沒交代不沿用它的理由——如果沒看到就另外重寫一次「逐輪取 carrier→算 folded_set 長度」,就是同一件事在 repo 裡出現第二份平行實作(這份 F 欄跟計劃要印的「折入數」是同一個數字、同一個資料來源、同一顆迭代結構 `groups`/`latest`)。

要嘛在做法段落裡明講「沿用 `_review_yield_round` 的 F 欄,不重算」,要嘛寫一句 WHY 交代跟這顆現成函式的差異在哪(例如它是「觀測不進合取」的單輪視角、這份要做的是跨輪比較,兩者用途不同所以另開)——目前兩者都沒有。

## 已看,無:

1. **分層與依賴方向**:`loop next 改成呼叫處置閘` 這個方向本來就存在——`cmd_loop_next` 已經在呼叫 `cmd_loop_status`(scripts/lumos:10664-10668,目前傳的是 `gate=True`),計劃只是把這條既有的向下呼叫換一個旗標(`disposal=True`),沒有新增反向或跨層呼叫。`_loop_status_disposal` 呼叫「報告函式」的做法也是既有模式的延伸:它已經在呼叫一串私有 step 函式(`_disposal_security_step`、`_disposal_clause_step`、`_disposal_landing_step`,scripts/lumos:18067/18153/18214,由 `_loop_status_disposal` 在 18549-18565 一帶依序呼叫),新的報告函式照同一種「`cmd_loop_status`/`_loop_status_disposal` 呼叫底線私有 helper」的方向走,不會形成循環。「上限函式共用」——`_TIER_PARAMS`(scripts/lumos:9801)與 `_loop_anchor_tier` 本來就是模組層級共用的表與函式,`cmd_loop_next`(10398)已經在用,不是計劃要新引進的東西。
2. **命名與錯誤處理**:計劃講的「只印不改判定與退出碼」跟既有的 advisory 輸出慣例一致——`scope_cap`/`cluster_hint`/`tier_hint` 這幾個既有欄位(scripts/lumos:10467-10509)就是同一種「印出來但不進 rc」的做法;`[disposal] 審查有沒有用(觀測,不進合取): …` 這行(scripts/lumos:18552)也是同樣「觀測不進合取」的措辭慣例,計劃要印的段落沿這個慣例走不算新花樣。讀帳失敗的處理(壞行 fail-closed、擋下訊息格式)計劃第四節講明「處置閘因帳本壞行等原因先擋下時,這段不印」,跟 `_loop_status_disposal` 現有的「先擋 n_badlines 再往下跑」順序(scripts/lumos:18279-18285)一致,沒有另開讀帳路徑繞過既有擋法。
3. **落點**:`Systems/loop-convergence-recording` 的 `about_code` 就是 `scripts/lumos`(該節點:76-77 行),DEP 行(46 行)也點名 `cmd_loop_status`;這份計劃動的正是 `cmd_loop_next`/`cmd_loop_status`/`_loop_status_disposal` 這幾支同一支檔案裡的函式,落這篇既有節點合理,不需要另開。

不對齊共 1 條,其中 major 1 條。
