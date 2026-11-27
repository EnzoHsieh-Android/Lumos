severity: clean

四個對照點都沒有發現第二種做法,以下是各點對照到的既有寫法。

**1. os.walk 的走訪順序**
- `scripts/lumos` 裡有 7 處 `os.walk(`,分別在 `:4054`、`:6746`、`:6820`、`:37180`、`:42903`、`:65874`、`:80363`。
- 前 6 處都不排序,只用 `dirs[:] = [...]` 原地過濾資料夾,或直接走訪。
- 這次 `:80367` 的 `subs.sort()` 接在原地過濾之後,是 os.walk 走訪時控制資料夾順序的標準寫法,同一處的 `sorted(files)` 也一樣。
- 既有程式裡沒有「走訪順序固定化」的別種做法,所以不算引入第二種。
- 其他 `.sort()` 和 `sorted(files)` 的用法(例如 `:30744`、`:51215`)是對結果排序,跟走訪無關。
- 這是第一處需要「看滿上限時每台機器收到同一批」的 walk,排序有理由。

**2. 測試怎麼替換 os 函式**
- `scripts/test_lumos.py` 其他替換 os 函式的寫法是 `m.os.replace = ...`(`:53033`)和 `lm.os.write = ...`(`:3496`)。
- 它們都是先存 `real_*`、再在 try/finally 還原,新測試也是這樣(`:150539-150552`)。
- 新測試用的是 `_os_mod.walk`,不是 `m.os.walk`,但兩者是同一個 `os` 模組物件,效果相同。
- 同一支測試前面也已經用 `_os_mod.mkfifo`(`:150506-150507`),所以在這支測試裡是沿用,不是新風格。

**3. 規格閘 PITFALL 行格式**
- 新增的 PITFALL 行帶 `[出處:]`、`[根因:]`、`[修法:]`、`[test:]` 四個欄位。
- 同篇 `規格閘.md` 其他 PITFALL 行(例如 patch 第 31、32 行)也是這個順序和欄位,格式一致。

**4. INDEX.md 的萬用寫法**
- `commands/INDEX.md` 同一列(06 代碼審與推送)已有 `reread-*` 的萬用寫法,這次把 `choice-points·choice-kill·choice-layer` 改成 `choice-*`,沿用的是同一種寫法。

對照的檔案:`/Users/enzo/harness/lumos-ci-fix/scripts/lumos`、`/Users/enzo/harness/lumos-ci-fix/scripts/test_lumos.py`、`/Users/enzo/harness/lumos-ci-fix/skills/lumos-project-notes/commands/INDEX.md`。
