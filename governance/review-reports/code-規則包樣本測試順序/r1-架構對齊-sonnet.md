severity: minor

整體判斷:結構跟鄰居一致,沒有引入第二種挑檔做法,只有一條放置位置的小出入。

**1. 分層與依賴方向**
- 新碼全放在 `t_kotlin_rulepack_samples` 內,沿用同一個 `mc = _ktpack(copy=True)` 改壞複本,跟鄰近測試同層。
- 它呼叫的是 `mc.HERE`、`mc.REVIEW_FP_PREFIX`。常數 `REVIEW_FP_PREFIX` 是 `configs/ast-grep/kotlin-android/check.py:27` 公開定義、`check.py:277` 也在用,所以測試重用規則包自己的常數,沒有在測試裡再抄一份字串。
- 這是對齊的,不列為不一致。
- 圖譜筆記、`governance/anchor-baseline.json` 與 `.governance-log.jsonl` 的更新,是改測試檔必經的簽章流程,不是新做法。

**2. 命名與錯誤處理**
- 第一條 finding:`kotlin規則包.md` 新增的 PITFALL 行被加在 `SEE:` 行之後。
severity: minor
  blocking: 否
  引句:「PITFALL:規則包測試用 rglob 的第一個檔去改壞,在 Linux 上可能挑到剛放進去的 review-fp 樣本」
  對照:`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:21-22` 的兩條 PITFALL 都排在 `RULE:`、`REVISIT:`、`SEE:` 之前。新行在 `SEE:` 之後,順序跟既有行不同。欄位本身 `[出處:]` `[根因:]` `[修法:]` `[test:]` 是齊的,寫法也跟鄰居一樣。
- 第二條 finding:`[修法:]` 寫「照檔名挑或整個目錄都改」,但實際只用了這兩種做法裡的「照檔名」那一類。
severity: minor
  blocking: 否
  引句:「[修法:照檔名挑或整個目錄都改,不用 next(rglob)]」
  對照:`scripts/test_lumos.py:125029-125043` 的 `sorted(...)[0]` 和整個目錄清空,這兩種都有用到,所以字面上對得起來。這條只是提醒,不影響結構,實際不算不一致,我不計入。
- 錯誤處理:這份 diff 沒有新增例外處理,跟鄰居都靠 `check(...)` 斷言一致。

**3. 第二種做法**
- 測試檔裡原有的 `next(... .glob/.rglob(...))` 共約八處(例如 `scripts/test_lumos.py:23582`、`:61012`、`:105334`、`:106713`)。這次不是改成第二種做法,而是把容易受目錄順序影響的地方換成 `sorted(...)`。
- `sorted(...rglob(...))` 在同檔早有多處前例(例如 `:21372`、`:40269`、`:62445`、`:71582`),所以這是專案既有的挑檔寫法。
- 用 `if not f.name.startswith(mc.REVIEW_FP_PREFIX)` 過濾再 `sorted(...)[0]`,語意上跟 `check.py:276-278` 的 `good_cases` 排除 review-fp 檔是同一個做法。
- 「整個壞例目錄清空」的迴圈沒有 `sorted`,但它對每個檔做一樣的事,順序無關,所以不算不一致。
- 沒有引入新的挑檔機制,也沒有跨層直呼。

不對齊共 2 條,其中 major 0 條

(補充:上面第二條只是提醒,不算不一致;嚴格算只有第一條,即 PITFALL 行排在 `SEE:` 之後。)
