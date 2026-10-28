severity: minor

我在修後版本(33255745)和修前版本(7cdb7d49)各跑了實驗。實驗放在 `/tmp/lumos-seat-work/code-room資料庫測試守衛/正確性-sonnet/`(clone 與 exp.py、exp2.py)。固定席筆記因鏡頭超時沒附,沒有「殘留」段,也沒有角色卡,這三項我略過。

## F1 刪掉同名多載的其中一個,會要求留下的那個補測試
severity: minor
blocking: 否 只有留下的同名方法本來就沒有真 Room 測試時才會誤擋,可用單次跳過放行。

引句:「hit_old = {n for n, a, b in oms + ocs if any(x <= b and a <= y for x, y in dels[p])}」
引句:「hit = [(n, is_new or n in hit_old or any(a <= x <= b for x in added)) for n, a, b in ms + cs]」

- **失敗場景**:DAO 有 `getById(id)` 和 `getById(id, x)` 兩個多載,測試只呼叫 `getAll`。只把第二個多載整段刪掉。
- **走到哪一行**:舊檔被刪的行落在第二個 `getById` 的範圍,`hit_old` 收進名字 `getById`。終點還有第一個 `getById`,上面第二句用名字比對,於是它被當成改到。
- **結果**:輸出「OrderDao.getById 這次改了,沒有測試以 .getById( 呼叫它」,rc 1。這個方法行為沒變,是誤擋。
- 對應 [S28] 說的「整段刪掉的方法終點不在就不要求」,只在名字唯一時成立。
- **歸因:有證據的修復回歸**
  - 修前 7cdb7d49,`python3.14 exp.py overload`:rc 0。
  - 修後 33255745,同一指令:rc 1。
- 這個誤擋不影響名字被測試呼叫過的多載,所以只會擋沒有測試的方法。

## F2 body 方法只剩 @Transaction 一個註記,刪掉它守衛放行
severity: minor
blocking: 否 這是修前就有的洞,而且守衛只負責要求測試,不是直接破壞資料。

引句:「刪最上面的註記行都要求測試」
引句:「hit_old = {n for n, a, b in oms + ocs if any(x <= b and a <= y for x, y in dels[p])}」

- **失敗場景**:abstract class DAO 裡有 `@Transaction open suspend fun repl() { a(); b() }`,它只有 `@Transaction` 這一個註記。只刪那一行。
- **走到哪一行**:終點的 `_rg_methods` 靠註記辨認方法,這個函式已不是 Room 方法,名字不在 `ms` 裡,所以舊檔那邊對得到也沒有東西可點名。
- **結果**:交易語意被拿掉,rc 0,沒要求任何測試。
- 這和計劃宣稱的「刪最上面的註記行都要求測試」不符。同樣是刪 `@Transaction`,方法還有 `@Query` 時(測試案例 getTx)會擋,只剩它一個註記時不擋。
- **歸因:有證據的原有漏查**
  - 修前 7cdb7d49,`python3.14 exp2.py txonly`:rc 0。
  - 修後 33255745,同一指令:rc 0。
  - 兩版結果相同,不是這次修補造成的。

## 已驗主張(同一案例證據)

| 主張 | input | expected | 修後結果 | 修前結果 | 歸因 |
|---|---|---|---|---|---|
| 刪方法最上面的註記行會被要求 | getTx 刪 `@Transaction` | 要求 getTx | 擋 getTx(`t_room_dao_partial_deletion_edges_required`) | 原稿漏掉這種(r2 席報告提過,我沒重跑) | 修復有效 |
| 註記行換成空白行會被要求 | `@Transaction` 換成空白行 | 要求 getTx | 擋 | 未判定(沒在修前跑) | 修復有效 |
| 上面加方法讓行號錯開,刪下面的註記仍對得上 | 前面多加兩個方法,再刪 getTx 的註記 | 要求 getTx | 擋 | 未判定 | 修復有效 |
| 整段刪掉的方法不要求、不點名鄰居 | 整段刪一個方法 | rc 0 | rc 0(`t_room_dao_whole_method_deletion_no_neighbor`) | 同上 | 保持成立 |
| 整個 DAO 檔刪掉 | `unlink` 後提交 | rc 0 | rc 0 | 未判定 | 保持成立 |
| 改名加刪行,舊路徑對得上 | 搬到 `p/data/` 並刪 `@Transaction` | 要求 getTx | 擋 | 未判定 | 保持成立 |
| Java 的 DAO | 刪 `@Transaction` | 要求 getTx | 擋 | 未判定 | 保持成立 |
| abstract class 的有本體方法 | 刪本體一行 | 要求 repl | 擋 | 未判定 | 保持成立 |
| 替換型 hunk | 改已有測試的 getAll 的 SQL | rc 0 | rc 0 | 未判定 | 保持成立 |
| 方法改名 | `getById` 改成 `getOne` | 要求 getOne | 擋 | 未判定 | 保持成立 |
| 只刪空白行或註解行 | 方法之間的空白行、方法上的 `//` 註解 | rc 0 | rc 0 | 未判定 | 保持成立 |
| exportSchema = false 的提醒不被「沒有結構檔」吃掉 | 沒有結構檔、`exportSchema = false`、這次改了 | rc 0 且印提醒 | 通過 | 修前會吃掉(依 r2 宣稱,我沒重跑) | 修復有效 |

- **新測試的獨立判準**:我拿掉了兩道關鍵判斷,測試都會紅。
  - 把舊檔範圍換成終點範圍:`t_room_dao_partial_deletion_edges_required` 有 2 條紅,`t_room_dao_whole_method_deletion_no_neighbor` 有 4 條紅。
  - 拿掉最前面的 exportSchema 提醒:`t_room_mig_never_exported_export_false_still_warns` 有 1 條紅。
- **現有測試**:修後版本 `-k room_dao` 38 過,`-k room_mig_` 44 過,`-k export` 33 過,全部 0 失敗。
- **未驗範圍**:
  - git diff 的刪除區段位移,也就是兩個方法之間有相同行時。
  - 舊檔讀不到的退路。程式讀碼上是退成不要求,我沒造出實例。
  - 大量檔的效能。我只讀碼:每支有刪除的 .kt/.java 檔,不管是不是 DAO,都多讀一次舊檔並剝註解。

## 三問
1. **原問題的修復效果有何行為證據?** 有。上表前三列和整段刪掉方法那列都有同案例的實跑結果,新測試拿掉判準會紅。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 大致成立,只有 F1 一處修後新增的誤擋(同名多載且未測試)。F2 是修前就有的洞。
3. **新發現的同一案例在修前、修後各是什麼結果?** F1 修前 rc 0、修後 rc 1。F2 修前、修後都是 rc 0。

最嚴重 severity 是 minor,blocking 共 0 條。
