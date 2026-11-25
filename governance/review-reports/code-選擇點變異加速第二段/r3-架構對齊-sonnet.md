severity: minor

報告開頭:使用者訊息裡的 LUMOS-IMPACT / 表態記錄 / 固定席節點段已附上。我當它們是參考資料,判斷都以真實代碼為準。

## 問 1 分層與依賴方向:對齊

- 中斷與時限到的分法沿用既有分工。`mg.interrupted` 只代表第一個終止訊號,由 `_KillMerge.on_signal` 設定(`scripts/lumos:28912-28917` 一帶)。`_KillHalt` 的另一個來源 `should_stop` 是「收到訊號或總時限到」(`scripts/lumos:79062`,`28715`)。
- 新寫的 `"中斷" if mg.interrupted else "時限到"`(`scripts/lumos:29169`)是從這兩個既有事實推出來的。它只讀 `mg.interrupted`,沒有另開狀態旗標。
- 呼叫鏈沒有跨層:`_kill_merge_iter` 呼叫 `_kill_merge_off`,寫入 `mg.plats`。`_choice_kill_report` 再從 `mg.plats` 算出 `merge_off`(`scripts/lumos:79103` 一帶),方向跟修補前一樣。
- `_CHOICE_MERGE_TRIPPED` 放在 `scripts/lumos:28732`,與其他 `_CHOICE_MERGE_*` 常數同區。`_kill_merge_breaker`(`:29098` 一帶)和 `_choice_kill_report` 兩處共用它,跟 `_CHOICE_MERGE_BASE_WHY`(`:28744`)的共用方式一致。

## 問 2 命名與錯誤處理:大致對齊,有 1 條 minor

- 命名:`_CHOICE_MERGE_TRIPPED` 符合 `_CHOICE_MERGE_*` 前綴,註解格式也跟同區常數一致。
- 印字:「中斷」和「時限到」都走 `quiet=True`,不印。這跟 `scripts/lumos:29012` 的 quiet 用法一致,理由是接著就停。
- 原因字串:既有的原因字串(「時限不夠」「指令過長」「基準量不齊」等,`:28943-28999`)全是字面值。新增的「時限到」也是字面值,所以跟這一族一致。
- 不一致之處:`"斷路器"` 抽成常數,`"中斷"` 和 `"時限到"` 沒有抽。抽常數的理由是 `_choice_kill_report` 要拿它過濾,算有跨處比對。另兩個字串只寫入、不被比對,所以結構上說得通,但同一張原因表內有的有常數、有的沒有。

severity: minor
blocking: 否
引句:「_CHOICE_MERGE_TRIPPED = "斷路器"         # 斷路器跳開時 _KillMerge.plats 記的原因」
file: `scripts/lumos:28732`、`scripts/lumos:29169`
說明:原因字串只有一個有常數,其餘仍是字面值。目前不影響行為,而且既有慣例本來就是字面值。
歸因:未判定

## 問 3 第二種做法:沒有

- 沒有長出第二份原因表。原因仍只記在 `mg.plats[平台] = (False, 原因)` 一處,`merge_off` 由它推出,斷路器、中斷、時限到都走這一處。
- 沒有第二種判斷中斷的方式。用的是既有的 `mg.interrupted`(`:29169`、`:29006`、`:29138`)。
- 有一個既有的不對稱,不是這次造成的:`:29138` 的訊號路徑沒有記 `mg.plats`。`_kill_merge_iter` 的 `except _KillHalt` 只涵蓋量基準階段。壞法迴圈裡由 `c.hk.between()` 丟出的 `_KillHalt` 不經這個 except,所以不會記「中斷」或「時限到」。這是結構上的缺口,不是新做法,我也沒查到修補前就是這樣以外的證據,標 ⚠ 供參考,不計入不對齊。

不對齊共 1 條,其中 major 0 條。
