---
type: issue
status: resolved
created: 2026-08-01
updated: 2026-08-01
related:
  - "[[Systems/lumos-cli-lifecycle]]"
  - "[[Systems/lumos-deinit]]"
pitfall_when:
  - "content:cmd_teardown"
  - "content:_teardown_global_claude"
tags:
  - type/issue
  - status/resolved
summary: |-
  FLAG:ORIGIN
  KEY:我寫測試驗「teardown 該擋下 Windows 自刪」,現場沒隔離 HOME、又用了自己編的 `LUMOS_SIMULATE_WINDOWS`(當時 CLI 根本沒這個接縫)——於是 `teardown -y` ★真的跑了★:刪光真機 `~/.claude/hooks/` 四支、移除全域 `~/.local/bin/lumos`,而 `settings.json` 註冊還留著指向已不存在的檔 → Claude Code 的 PostToolUse hook 每次都報錯
  KEY:★會半做正是因為打到不完整的來源★——`_teardown_global_claude(src_repo)` 拿臨時 repo 當 src,那裡沒有 `merge-claude-settings.py`,所以「刪 hook 檔」做了、「剪懸空註冊」跳過。這恰好就是該函式 docstring 自己警告的「不半做」情境,只是從另一個方向撞進來
  KEY:★通則:破壞性指令的測試,假 HOME 是最低門檻不是可選項★——同檔既有的 `_teardown_run(home, fn)` 就是為此存在的 helper,我沒用它。另一條:★不要假設接縫存在★,`LUMOS_SIMULATE_WINDOWS` 是我以為有的,實際上要自己加;假設落空時測試不是紅,是「真的執行」
  DECISION:[2026-08-01]復原=重跑 `lumos install`(重建全域指令+skills+`_sync_global_claude` 補回 hooks 與註冊),已逐項核對;測試改成假 HOME + 假 repo 雙隔離,並真的把接縫加進 CLI
---
# 測試未隔離 HOME，刪掉真機的 Claude hooks

## 發生什麼

要驗「`teardown` 在 Windows 上應該擋下用專案自帶那份拆自己」，我寫了測試，用子進程跑 `python <temp>/scripts/lumos teardown -y`，環境變數帶 `LUMOS_SIMULATE_WINDOWS=1`。

兩個假設同時錯：

1. **`LUMOS_SIMULATE_WINDOWS` 這個接縫當時不存在**（那是精簡版才有的 `LUMOS_SLIM_SIMULATE_WINDOWS`）。所以它沒有模擬任何東西，只是一個被忽略的環境變數。
2. **沒有隔離 `HOME`**。

於是 `teardown -y` 不是「被守衛擋下」，而是**真的執行了**，打在我自己的機器上：

- `~/.claude/hooks/` 四支（`check-graph-sync.py`／`verification-rot-check.py`／`impact-hook.py`／`ci-status-hook.py`）全被刪
- `~/.local/bin/lumos` 全域指令被移除
- **`settings.json` 的註冊卻留著**，指向已經不存在的檔 → Claude Code 每跑一個 Bash 指令，PostToolUse hook 就報 `can't open file`

## 為什麼會「半做」

`_teardown_global_claude(src_repo)` 的第③步是跑 `src_repo/scripts/merge-claude-settings.py --prune-only` 去剪懸空註冊。這次 `src_repo` 是那個臨時 repo，**裡面沒有那支 .py**，所以第③步靜默跳過——「刪檔」做了、「剪註冊」沒做。

諷刺的是，這正是該函式 docstring 自己警告要避免的「不半做」情境（它為了壞掉的 `settings.json` 做了防護），只是我從另一個方向撞進來：不是 settings 壞，是 src 不完整。

## 復原

重跑 `python3 scripts/lumos install`——它會 `_sync_global_claude`，把 hooks 複製回去並重新 merge 註冊，同時重建全域指令與 skills。逐項核對過：四支 hook 回來、symlink 回來、lumos 家族 skills 齊、`settings.json` 無懸空註冊。來源 clone 與本 repo 的 `core.hooksPath`／`CLAUDE.md` 全程未受影響（`deinit` 打的是臨時 repo）。

## 教訓（兩條，都比這次的損害值錢）

**① 破壞性指令的測試，假 `HOME` 是最低門檻，不是可選項。**
同一支測試檔裡早就有 `_teardown_run(home, fn)` 這個 helper，就是為了假 HOME 隔離而存在的（`t_teardown_global_claude` 用得好好的）。我沒用它，自己另起爐灶。**現成的隔離 helper 沒用，等於自己把安全網拆了。**

**② 不要假設接縫存在。**
我以為 CLI 有 `LUMOS_SIMULATE_WINDOWS`，其實沒有。**假設落空時，測試不是「紅」，而是「真的去執行」**——這比斷言寫錯危險得多，因為紅燈會叫你，真執行不會。

這是同一天內第二次「為了驗證某個危險行為，直接在真環境上把那個危險行為做出來」——前一次是為了驗證 `GIT_DIR` 污染，直接把 127 筆測試 commit 寫進本 repo 的 main（見 [[Issues/prepush測試閘假紅-git環境洩漏]]）。**兩次的共同形狀：想證明「X 會造成傷害」，就在真環境造成了 X。** 正確做法一律是拋棄式環境（假 HOME／臨時 clone），沒有例外。

## 修法

- 測試改成 **假 HOME + 假 repo 雙隔離**，並在每個子案例前重新布置現場。
- **真的把接縫加進 CLI**：`_selfdelete_risk()` 讀 `LUMOS_SIMULATE_WINDOWS`——只有這道守衛用它，不動全域 `_IS_WIN`（否則會讓所有 Windows 分支在測試裡活起來）。
