severity: minor

## 1. top_compose_fn 同分時的挑法沒有測試釘住
severity: minor
blocking: 否
引句:「ROW_NUMBER() OVER (PARTITION BY frame_id ORDER BY SUM(self_ns) DESC, name) AS rk」
file: `scripts/templates/android-ui-attribution.sql:70`
歸因:有證據的原有漏查。修前 `f96ffe70` 與修後 `46773fe6` 都有 `, name` 這個同分決勝,這次修補沒碰它。

- **失敗場景:** 同一幀有 `a.B (B.kt:1)` 和 `a.A (A.kt:1)`,自身時間都是 50。
- **查證命令:** 在修後樹的 SQL 檔把 `ORDER BY SUM(self_ns) DESC, name` 改成 `ORDER BY SUM(self_ns) DESC`,再跑 `python3.14 scripts/test_lumos.py -k android_ui_attribution`。
- **結果:** 47 passed, 0 failed,改壞沒被抓到。
- **影響:** 同分時回哪一個,要看引擎怎麼排。Python 內建 sqlite3 和 trace_processor 可能挑出不同的函式名。`rerun.sh` 的 expect 能比對字串欄位,所以收據若把 `top_compose_fn` 寫進 expect,就可能在重跑時意外報不符。
- **為何只算 minor:** 文件沒有承諾同分時的結果,只是覆蓋可以更完整。

## 三問的回答

**① 原問題的修復效果有何行為證據?** 修前用 f96ffe70 的範本檔跑修後的測試,修後的檔跑修後的測試。修後 SQL 再用手寫假表直接比對(無 SQL 修改的授權守衛一項,是修前樹跑同一支授權測試)。

| 修復項 | 修前結果 | 修後結果 |
|---|---|---|
| NULL 名稱區段 | `other` 4,子樹整段消失 | 四類為 (0, 0, 3, 7),加總等於幀長 |
| Compose 底下的 `drawChart` | `pipeline` 50 | 算 Compose 60 |
| 子區段(150)比幀(100)長 | `other` -50 | `other` 0 |
| 整份範本貼進收據重跑 | `rc=1 BAD Q1` | 重跑通過 |
| 授權守衛 | `.sql` 被判缺標示 | 8 passed |

- 修前和修後都在同一個 `drawable` 輸入上驗過:只有名稱 `drawChart` 的區段,修前算 pipeline 50,修後算 other 100(跟祖先)。
- 授權守衛的反向確認:
  - `.sql` 的 SPDX 行改成 `#` 開頭,守衛仍紅。
  - `.sh` 的 SPDX 行改成 `--` 開頭,守衛也紅。
  - 所以「其餘檔照舊只認 `#`、`.sql` 只認 `--`」兩邊都成立。
- 範本內沒有以 `;` 結尾的註解行,只有最後一行 `ORDER BY f.ts;`。`-- [Qn]` 範例行不會被重跑腳本誤認成標頭。
- 把兩份範本一起貼進 `queries.sql`,用重跑腳本的正則解析,得到 Q1、Q2 兩條完整查詢,各以 `ORDER BY f.ts;` 結尾。
- 用 20 種改壞逐一檢查 `-k android_ui_attribution`:
  - 抓得到:
    - 拿掉 `name='draw'`
    - 改成 `draw*`
    - `IS` 改回 `=`
    - 拿掉單一空白判斷
    - 拿掉 `dur>=0`
    - 拿掉 `tid=pid`
    - 拿掉下限 0
    - 拿掉小寫 `compose:`
    - 拿掉 `Recomposer:`
    - 拿掉 `RV `
    - 拿掉 `postAndWait`
    - 拿掉 `setupListItem`
    - 拿掉 `obtainView`
    - 拿掉 `input`
    - 拿掉 `animation`
    - 同分改升冪
    - doFrame 限最上層
  - 沒抓到兩項:
    - 拿掉 `, name`,就是上面的 finding 1。
    - `kids` 改讀 `slice`,只在「已收尾的父區段底下有沒收尾的子區段」才有差,這種形狀在 Perfetto 的巢狀資料裡不會出現。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 正常路徑:修後測試 47 passed;跑 `-k vendor` 98 passed、`-k android` 71 passed。
- 錯誤路徑:NULL 名稱、子區段超長、註解含分號,都有上表的修前紅、修後綠。
- 相鄰路徑:
  - `rerun.sh` 沒改,正則行為不變。
  - 18 萬個區段、3000 幀的假資料,修前 1.0 秒、修後 1.05 秒,`IS` 沒有造成效能退步。
  - 授權守衛仍照檔案類型認註解符號。
  - 所有 pitfalls 題都是誤報:5 條 N+1 是 CTE 不是迴圈,SARGable 的 `COALESCE` 不在 WHERE。

**③ 新發現的同一案例修前、修後各是什麼?** 只有 finding 1 一條,修前修後行為相同(都有 `, name` 且都沒有測試釘住)。

**角色卡:**
- be-api-compat:輸出欄位名稱和順序兩版相同。舊收據在 `queries.sql` 裡存的是自己貼的 SQL 全文,重跑不受範本改動影響,只有新貼的範本會套用 `draw` 新規則。結論是不影響。
- be-authz:沒有端點,不適用。

**圖譜固定席:**
- `授權與歸屬` 的 ★INVARIANT★「每支被複製的檔至少要有 SPDX 註解行」:`.sql` 用 `--` 正確,且 `.sql` 與 `.sh` 的反向改壞都會翻紅,合約沒被破壞。
- 其餘固定席(`lumos-cli-read`、`guard-kill`、`bound-tests-gate` 等)牽連檔是 `scripts/lumos`、`scripts/test_lumos.py`,這次只多一筆複製清單和測試,不碰它們宣稱的行為,判不影響。

**未驗範圍:**
- 真實 trace_processor 上的行為:這次只用 sqlite 假表。
- 巢狀的 `Choreographer#doFrame - resynced…` 區段:我試過手造巢狀幀,內外兩幀會各出一列且共用同一個 `f<ts>` 鍵。但真實 Android 是否會產生這種巢狀,我沒有證據,所以不列為 finding。
- 新增的套件名字元檢查是文字指示,沒有測試。

**環境提醒:** 我曾短暫把審查用的工作樹切成 detached HEAD(指向同一個提交),隨即切回 `EnzoHsieh-Android/android-ui-kind`,HEAD 仍是 46773fe6。暫存目錄已刪。

總結:最高嚴重度 minor
