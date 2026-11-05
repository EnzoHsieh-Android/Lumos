severity: minor

整份修補看過,掛鉤判定與降級流程沒有會做出錯行為的問題。有一條 minor:[S6] 後半的測試沒綁進驗收條款。

## finding

severity: minor
blocking: 否
[S6] 後半(原本就判 light 的功能分支不印降級那行)的守衛測試沒綁進條款
引句:「check("原本就判 light:不印「推功能分支:」降級那行", "推功能分支:" not in r.stderr, r.stderr[-600:])」
`docs/lumos-toolchain-knowledge/Projects/推送只跑受影響測試_計劃.md:75`

- [S6] 條款寫了「原本就判 light 的功能分支推送 應 不印降級那行」,但它只綁 `t_prepush_feature_branch_light_ok_false`。
- 守這半句的是 `t_prepush_feature_branch_already_light`,全 repo 只有 `scripts/test_lumos.py` 定義它,計劃、圖譜沒有任何引用。
- 只靠 `[test:]` 綁定的雙向門與條款閘不會跑到它。全套與 `-k` 會跑,所以推送前的全套還是守得住。
- 要補的話,把它加進 [S6] 的 `[test:]`,或另開一條 [S9]。設計判定已凍結,這條我不升級。
- 歸因:有證據的原有漏查(這個測試是這輪新增,綁定缺口是補測試時沒回頭改條款)。

## 逐項驗證結果

**1. 正確性,`_down` 判定段**
- 修前是兩段 `if`,第二段要求 `_suite_this == full`,第一段 light 命中後它已是 light,所以第二段不會再進。
- 修後的 `if/elif` 結果相同:
  - light 條件成立時只設 `_down="light"`,不設降級旗標。
  - 只有功能分支路徑設 `_SUITE_BRANCH_DOWN=1`。
- 兩條路徑都共用取關鍵字、`autoloop_full` 那段,走法跟修前一致。

**1. 正確性,`_sr["computed"]` 直接索引**
- `_test_suite_for_range` 的三條回傳都帶 `computed`:
  - 兩條失敗路徑明寫 `computed=False`。
  - 其餘由 `full` 預設 `"computed": True` 承接,守衛檔提早回 full 也在內。
- `_pitfall_diff_collect` 裡兩處讀取都是這個函式的回傳。真的漏帶就 `KeyError`,`pf_json` 變空,掛鉤照全套,方向是往全套。
- 新單元測試把函式換成漏帶 `computed` 的版本,確認會 `KeyError`。

**1. 多 ref、新舊互讀等邊角**
- 掛鉤的旗標探測:
  - 舊 lumos 沒有 `dest="pf_pushed_ref"`,掛鉤不帶 `--pushed-ref`,沒有 `pushed_mainline` 欄位,照全套。
  - 舊掛鉤配新 lumos 不帶 `--pushed-ref`,同樣沒有欄位,照全套。
- 刪除分支在迴圈開頭就 `continue`,不進判定。
- 標籤與空字串在 `_pitfalls_pushed_mainline` 回 true,走全套。
- 混推 main 與功能分支時,main 那個 ref 讓 `_SUITE_FULL=1`,整次全套,降級那行不印。
- 降級那行的條件是 `_suite_mode == light` 且 `_SUITE_BRANCH_DOWN == 1`。
- 舊 runner 沒有 `--suite`,或 `--graph` 不支援而退成全套時,`_suite_mode` 變 full,降級那行不會誤印。
- `pf_json` 的 grep 不會被檔名裡的字串誤觸:JSON 裡檔名的引號會跳脫成 `\"`,吻合不了 `"pushed_mainline": false`。

**4. 對照 [S1]–[S8]**
- 20 支 `-k prepush_feature_branch` 在 9918ed76 的複本上全過。
- 兩個改壞各跑一次:
  - 改壞 A:light 路徑也設 `_SUITE_BRANCH_DOWN=1`。`t_prepush_feature_branch_already_light` 轉紅,斷言是「原本就判 light:不印「推功能分支:」降級那行」。
  - 改壞 B:拿掉 `suite_computed` 條件。`t_prepush_feature_branch_failclosed` 轉紅,斷言是「算不出範圍:功能分支照全套、不印降級那行」(`rc=0`)。
- [S1]–[S8] 條款與綁定測試對得上實作。[S6] 後半的綁定缺口見上方 finding。
- 失敗往全套方向:`pf_json` 空、欄位缺、`suite_computed` 為 false、舊版 lumos 都走全套,沒有誤降成子集的路徑。

**2. pitfalls**
- 跑了 `lumos pitfalls --diff 4cc9c425..9918ed76`,輸出多是 `scripts/lumos` 既有 ruff 項目,與這輪改動無關。
- 掛鉤與測試檔上沒看到新增的違規。

**3. 圖譜鏡頭**
- 讀固定席 8 篇節點的步驟這輪沒做,範圍外,不是已判。
- 以掛鉤與 lumos 的實際行為對照判,沒有破壞任一條已宣稱的行為。

**修補鏡頭三問**
- ①修復效果:
  - 改壞 A 能被 `already_light` 抓出,表示「原本就判 light 不印降級」有行為證據。
  - 修前版本我沒另外取出對照,所以「修前紅」這半邊未判定。
  - 修後所有 `prepush_feature_branch` 斷言(20 支)全綠。
- ②相鄰路徑:推 main、light、混推、算不出範圍,各自有對應測試,修後仍成立。
- ③新發現:只有上面那條 minor,修前修後同樣存在。

臨時目錄 `/tmp/lumos-seat-work/code-推送只跑受影響測試/正確性-sonnet/` 下的複本已刪,只剩兩個小輸出檔 `outA.txt`、`outB.txt`。
