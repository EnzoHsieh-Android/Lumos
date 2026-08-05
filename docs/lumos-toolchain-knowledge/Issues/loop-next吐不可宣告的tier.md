---
type: issue
status: done
created: 2026-08-04
updated: 2026-08-04
related:
  - "[[Systems/loop-convergence-recording]]"
  - "[[Projects/loop機械脊椎M1包_計劃]]"
  - "[[Systems/測試假綠形態]]"
tags:
  - type/issue
  - status/done
summary: |-
  FLAG:TECHNICAL
  KEY:症狀=`loop next` 在無 tier 定錨的 legacy loop 上,吐出的 `record_cmd` 帶 `--tier legacy`,而 `--tier` 的 choices 只有 light/standard/high(LOOP_TIERS)——★複製貼上會被 argparse 當場 rc2★
  KEY:★這個 bug 自己維持自己★——碰到 rc2 最自然的修復是「把 --tier 拿掉再跑」,拿掉就記不上定錨 → 下一輪 next 又推成 legacy → 又吐一條跑不動的指令。不是「誰忘了標」,是機制在教錯誤的習慣
  KEY:代價=legacy 的 cap 是 6,比 standard 的 3 鬆;2026-08 三個走循序的 loop(code-slim-python / code-teardown-windows / code-slim-handoff)全數 tier=None,其中 code-slim-python 吃滿 6 輪才被逼停「達 cap 未收斂、人裁放行」
  KEY:★發現路徑值得記★——起點是使用者問「循序早就不用了不是嗎」;查帳發現 8 月 panel 13 / 循序 13(不是不用了),再問「tier 為何全 None」才撞到這條。★我的第一版歸因是錯的★:我說「沒人決定、掉進 fallback」,使用者反問「非 high 不就預設單 reviewer 嗎」——對,單席循序是設計行為,不是坑。真正的坑只在 cap 與那條跑不動的指令
  DECISION:[2026-08-04]修 record_cmd 不吐不可宣告值(`eff_tier in LOOP_TIERS` 才帶 --tier),並補 `tier_hint` 講清楚★這個 loop 補標不了、要開新 loop id★;不動 legacy 的 cap 6(那是收斂判準=守衛面,要走 design-loop 另案)
  DEP:scripts/lumos cmd_loop_next 的 emit()｜LOOP_TIERS｜_TIER_PARAMS
  TEST:t_loop_next_legacy_emits_a_command_that_actually_runs(7 條斷言;含還原翻紅釘與兩條現場成立前置)
aliases:
  - "invalid choice: 'legacy'"
---
# loop next 吐出一條跑不動的指令（而修復它的自然反應會複製這個狀態）

## 症狀

`lumos loop next <legacy-loop> --json` 的 `record_cmd` 長這樣：

```
lumos canary record caught|missed --loop <id> --auditor <席> ... --tier legacy --scope-lines <N>
```

照著跑：

```
usage: lumos canary record [-h] ...
lumos canary record: error: argument --tier: invalid choice: 'legacy'
```

`LOOP_TIERS = ("light", "standard", "high")`。**`legacy` 不是可宣告值**——它只是「無定錨舊帳 ＋ legacy 格式」的推導結果（見 [[Projects/loop機械脊椎M1包_計劃]] 的「無 `--tier` 的身分推導」條）。

## ★為什麼這比「一條壞指令」嚴重★

碰到 rc2 之後，最自然的修復是**把 `--tier` 拿掉再跑一次**。

拿掉 → 記不上定錨 → 下一輪 `loop next` 又推成 legacy → **又吐一條跑不動的指令**。

**這個 bug 自己維持自己。** 它不是「誰忘了標 tier」的紀律問題，是機制在每一輪主動教出那個錯誤習慣。

帳面證據（`.canary-log.jsonl`，329 筆）：2026-08 走循序的三個 loop
`code-slim-python` / `code-teardown-windows` / `code-slim-handoff` **`tier` 欄全部是 `None`**。

## 實際代價（只有一項，不要誇大）

| | 席數 | cap |
|---|---|---|
| `legacy`（推導） | 1 | **6** |
| `standard`（該標的） | 3 | **3** |

**席數不是問題**——code-loop skill 本來就規定 `standard` 走單 reviewer，單席循序是設計行為。
差別只在 **cap**：`code-slim-python` 跑滿 6 輪才「達 cap 未收斂、人裁放行」，
標了 standard 的話第 3 輪就會停下來攤給人。**多燒了三輪才被逼停。**

## ★我第一版歸因是錯的（留著，因為錯法有代表性）★

我最初的說法是「不是有人決定走循序，是沒人決定，然後掉進 fallback」。

使用者反問：**「但是如果 tier 不是 high，我們不是預設單 reviewer 嗎」**——對。

我把「單席」跟「寬 cap」兩件事綁成一個故事講，而只有後者站得住。
**看到帳面異常（tier 全 None）就假設整條路徑都是錯的**，是這次的錯法。

## 修法

```python
# legacy 不是可宣告值,不得吐進 record_cmd
_tier_flag = f" --tier {eff_tier}" if eff_tier in LOOP_TIERS else ""
```

外加 `tier_hint`，明講**這個 loop 補標不了**：帳面已是 legacy 格式（記錄不帶 `--round`），
補 `--tier standard|high` 會被既有的格式一致性檢查擋掉（rc2）；`--tier light` 格式相容但
cap=2 且帶 ratchet 語意。**要走分級判準只能開新 loop id，並在第一筆 record 就帶 `--tier`**
——與既有的定錨衝突錯誤訊息「要換 tier 開新 loop id」同一條規則。

## 驗證

`t_loop_next_legacy_emits_a_command_that_actually_runs`，7 條斷言。

★**oracle 是「真的跑一次」不是字串比對**★：測試把 `record_cmd` 的佔位符填掉後
**原樣執行**，斷言 rc0。字串斷言只證「長得對」，真跑才證「用得了」。

**還原翻紅釘**：把 `--tier {eff_tier}` 無條件版本放回去 → 「必須真的跑得動」翻紅（實測 `rc=2`），
「legacy 不得出現在 --tier」翻紅。
**兩條現場成立前置**：① `tier == "legacy"` 且 `phase == "plant-canary"`（證明真的走到 legacy 推導路徑）
② 填完無殘留 `<` 佔位符（證明跑的是那條指令、不是別的東西）。
**反誤傷**：standard / light 仍須帶 `--tier`。

## 沒做、留著的

- **`legacy` cap 6 要不要收緊**：這動到收斂判準＝守衛面，依 `lumos-design-loop` 進場硬否決，
  不得逕改。但推測修完本條後它會自然萎縮——tier 標得上了，掉進 legacy 的路徑就少了。
- **`_TIER_PARAMS` 的命名撞名**：`standard: (3, 3)` 的 `3` 是 design-loop 的 panel 席數，
  與 code-loop skill 的「standard 走單 reviewer」是兩套語意共用一張表。目前只有傳
  `--min-seats` 才啟用，**沒炸，不是活的 bug**，但值得知道。
