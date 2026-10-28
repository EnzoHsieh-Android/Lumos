severity: clean

三問都對齊,沒有不對齊的發現。

**1. 分層與依賴方向:對齊。**
- 改動只在測試層:三處 `gov` 呼叫加 `--since 9999`,沒有碰 `scripts/lumos` 本體,也沒有新增 import 或 helper。
- 鄰居也是同一種呼叫方式,都是測試經 `run(...)` 或 `_ci_run(...)` 走 CLI。例如 `scripts/test_lumos.py:8685-8687`、`9503`、`10198`、`36488`、`37327`、`47727`。
- 改動的 `_ci_run`(`scripts/test_lumos.py:37893`、`37897`)和 `run(vault, ...)`(`scripts/test_lumos.py:94500`)沿用各自測試原本的呼叫函式,沒有跨層直呼。

**2. 命名與錯誤處理:對齊。**
- 參數寫法和既有慣用法一致。鄰居有 `"gov", "--since", "9999", "--full"`(`scripts/test_lumos.py:9503`、`9521`)和 `"gov", "--since", "9999", "--stats"`。這次的 `"gov", "--since", "9999", "--full"` 與前者同序。
- 這次補的行內註解是說明為什麼帶這個參數,沒有別的格式。
- 新增的 PITFALL 行在 `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md` 第 35 行附近。必有鍵齊全:`[出處:]`、`[根因:]`、`[修法:]`、`[test:t_ci_status_and_gov]`。`[test:]` 屬於 `[test:]`、`[repro:]`、`[防回歸:]` 三選一。
- 格式與同檔鄰居一致:前綴 `PITFALL:` 加症狀,再接一串方括號鍵(同檔第 19、20、24 行)。
- 帳本與簽章(`docs/.governance-log.jsonl` 的 anchor-approve、`governance/anchor-baseline.json`)是照專案流程的例行更新。

**3. 第二種做法:沒有。**
- 我在 `scripts/lumos` 和 `scripts/test_lumos.py` 搜了 `LUMOS_NOW`、`LUMOS_FAKE_NOW`、`FROZEN_NOW`、`_now_override`、`freeze_time`,沒有命中,所以專案沒有凍結時間或注入 now 的機制。
- 「讓 gov 看全部紀錄」的既有做法就是 `--since 9999`。測試檔裡有二十多處用它,例如 `scripts/test_lumos.py:8685`、`9503`、`10198`、`12063`、`36488`、`37327`。這次沿用同一種做法。
- ⚠ 次要觀察,不列 finding:`scripts/test_lumos.py:3847`、`3853`、`3861`、`3923` 與 `8721` 的 `gov` 呼叫沒帶 `--since`。我沒有驗它們的 fixture 是否也寫死日期,那屬於 bug 面,不歸我判。從架構一致性看,這次改動沒有引入新做法。

不對齊共 0 條,其中 major 0 條
