severity: major

## F1 scripts/lumos 出現兩份逐字重複的 `_review_yield_round`,是這次搬家造成的複製貼上殘留
severity: major
blocking: yes
這次修正把一大段函式(`_SEV_ORDER`…`_cap_hint_print`)插進 `_review_yield_round` 與 `_disposal_round_groups` 之間,但插入的那一大段★結尾★又完整重貼了一次 `_review_yield_round`(docstring、實作逐字相同),導致 `scripts/lumos` 現在同名函式定義兩份(第 7366 行與第 7630 行,已用 `grep -n "^def _review_yield_round"` 核對)。Python 只認最後一份定義,功能上因為兩份內容一致而不會走錯,但這正是這份程式碢自己反覆強調要杜絕的重複(例如同檔 `_SEV_DECL_LINE_RE` 註解寫「★獨立宣告行的唯一定義★」、`_intake_declared` 註解寫「★走全檔唯一那支剝圍欄實作★…自己寫的正則有兩個致命假設」),這裡卻自己留了一份死代碼跟既有寫法不一致。
引句:「[審查有沒有用記帳 S3] 一輪帳列 → 漏斗數字 dict(N 報/M 存活/R 重現不到/F 折/A 放行/S 存活多於席位報)。」
既有寫法對照:scripts/lumos:7366(原本就在的那一份,搬家後被晾在原地沒清掉)。

## F2 scripts/test_lumos.py 新測試裝飾器疊用兩次,緊接著下一支既有測試的裝飾器不見了
severity: minor
blocking: no
新測試 `t_disposal_cap_hint_fail_open` 上方是 `@_cap_real_cutoff` `@_cap_real_cutoff` 疊了兩層(scripts/test_lumos.py:33226-33227),而緊接在它後面的既有測試 `t_cap_hint_writes_no_extra_ledger`(33239 行)反而變成完全沒有 `@_cap_real_cutoff` 裝飾器——對照 patch,是把新函式插進舊的 `@_cap_real_cutoff` 正上方時,沒發現那一行本來是掛在下面 `t_cap_hint_writes_no_extra_ledger` 頭上,新加了一份自己的裝飾器卻沒把原本那份留給它。實測 `python3 scripts/test_lumos.py -k cap_hint_writes_no_extra_ledger` 目前仍綠(這支測試碰巧不依賴 `_cap_real_cutoff` 設的退役日環境變數也能過),但這是搬家造成的裝飾器錯位,跟本檔其他測試「一支測試一組自己的裝飾器」的既有寫法不一致,且日後這支測試若被改成依賴退役日就會悄悄壞掉而不報錯。
引句:「處置閘照常結束,不因提示段噴例外、退出碼不變(代碼審 r1 blocker)。」
既有寫法對照:scripts/test_lumos.py:33059-33226 一路每支測試各自一份 `@_cap_real_cutoff`,沒有疊用或缺漏的先例。

已看,無:
- `_cap_hint_print` 吞例外不印(scripts/lumos:7731-7738)跟同一支 cap-hint 機制既有的呼叫端寫法一致——`loop next` 那邊本來就是 `try: _ch = _cap_hint(rounds) / except Exception: _ch = None`(scripts/lumos:10949-10953),同一機制失敗時本來就是靜默跳過不印,不是新發明的寫法,也不算跟「觀測段失敗要出聲」那類慣例(如 `_roster_observe`/`_escape_auto_failed`)衝突,因為那些是「有做但做壞了」要出聲,這裡是「連算都算不出來」的情況,cap-hint 這條線本來就選靜默。
- 段首標籤第 1 點已照做:`_cap_hint_lines` 現在只有第一行帶 `[cap-hint] `,其餘全部改用縮排常數 `P = "  "`(scripts/lumos:7744-7768),跟處置閘裡其他多行段落(例如 `[disposal] canary(觀測,不進合取): …` 後面接 `  {rid}.{i}\t…` 的兩格縮排延續行,scripts/lumos:18861-18865)是同一種「標籤只在段首、後續縮排」寫法,一致。
- 分輪函式搬家後的位置合理:`_disposal_round_groups`(7654)→`_cap_hint`(7680)→`_cap_hint_print`(7731)→`_cap_hint_lines`(7740)四支連在一起,都是處置閘/跑滿上限提示這一族在用的步驟函式,搬回同一段落後彼此相鄰,查找與維護上合理,不再散在別處。
