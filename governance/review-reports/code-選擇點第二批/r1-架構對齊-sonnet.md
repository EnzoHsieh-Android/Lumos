severity: major

## a1 依列號的放行「取最後一筆」用字串比時間,沒走既有的時區安全比較
severity: major
blocking: 是 — 引入第二種比時間的做法,同帳混時區時選錯筆、統計的放行標籤是錯的(依 severity 判準,照文件做會出錯算 major)。

引句:「if wk not in c["row_waive"] or ts >= c["row_waive"][wk][0]:」

- **問題**:`ts` 是帶時區的 ISO 字串(`_gov_ts` 文件寫「帶時區的時間」)。新碼直接用字串 `>=` 比大小,混了不同時區偏移的帳會選錯那一筆。
- **鄰居的做法**:
  - 比較兩個 ts 誰晚,專案有共用函式 `_loop_ts_newer`(`scripts/lumos:20860`),文件寫「比 UTC 秒數,否則退回字串」。
  - 把 ts 解析成時間有 `_gov_ts`(`scripts/lumos:1713`)。它的 docstring 明講當初就是為了避免「兩處各寫一份」才抽出來的(上一輪代碼審的架構對齊席)。
  - 其他讀帳處也都走它:`scripts/lumos:20970` 用 `_loop_ts_newer`,`scripts/lumos:1747`、`4732`、`28715`、`46711`、`70293` 用 `_gov_ts`。
- **重現**:在 `eebb8459` 的臨時副本裡直接呼叫 `_gov_choice_counts` 與 `_gov_choice_by_row`。兩筆放行同檔同行指紋,一筆 `2026-11-17T20:00:00+00:00`(UTC 20:00,較晚)標「較晚-不適用」,另一筆 `2026-11-17T23:00:00+08:00`(UTC 15:00,較早)標「較早-等價」。
  - 輸出:`Counter({'較早-等價': 1})`。
  - 對照 `_loop_ts_newer(rows[0]["ts"], rows[1]["ts"])` 回 `True`,即共用函式認為前一筆較晚。
  - 預期放行標籤是「較晚-不適用」,實際算到較早那筆。
  - 腳本在 `/tmp/lumos-seat-work/code-選擇點第二批/架構對齊-sonnet/repro.py`,在副本 repo 根目錄用 `python3.14 ../repro.py` 跑。
- **修法方向**:把這句換成 `_loop_ts_newer(ts, c["row_waive"][wk][0])`。
- **範圍說明**:這個專案只有一個人用,但同一台機器遇到夏令時間、換時區或不同機器的提交,帳裡就會混出不同偏移。`test_lumos.py` 的 `t_gov_stats_choice_by_row` 兩個 ts 都沒帶時區,所以抓不到這個壞法。

## 三問逐問
1. **分層與依賴方向**:對齊,只有 a1 一處例外。
   - 統計走既有的 `_gov_choice_counts`(`scripts/lumos:17894`),新增 `row_mut`、`row_waive` 兩個鍵,`_gov_choice_by_row` 只讀 `c`,沒有另讀一次帳。渲染接在 `_render_gov_choice` 尾端。
   - `choice_sample_mark_problems` 重用 `_choice_sample_marks` 與 `CHOICE`,在 `catalog_problems` 裡跟 `choice_sample_problems` 並列。`_choice_retired_problems` 接在 `choice_tables` 尾端,沿用 `rules_dir is not False` 的慣例。
   - `rules_dir` 在 `choice_tables` 開頭已經解析好,`Path(rules_dir)` 不會碰到 None。
2. **命名與錯誤處理**:對齊。
   - 新函式用 `_gov_choice_*`、`_choice_*` 前綴,問題清單沿用 `(列號, 文字)` 二元組。
   - 沒有新的帳本事件。choice-kill 事件本來就帶 `row`,`scripts/lumos:18462` 已經把它留進統計列。
   - `_CHOICE_BASE_RED` 定義在統計段(`scripts/lumos:17921`),跟 `_CHOICE_KILL_GATE`(`scripts/lumos:77736`,定義在判定側)的位置慣例相反。它是模組全域、運作正常,不列。
3. **第二種做法**:除 a1 外沒有。
   - `_CHOICE_NOT_MINE = object()` 這種哨兵,專案已有先例(`scripts/lumos:23633`、`59435`)。
   - `_choice_anchor_edits` 把原本 `_choice_edits` 裡的方法名分派搬進去,結構上多一層,但沒有另一套編輯產生機制。
   - C-34 照抄 `sbr.yml` 的 `value-pos`,檔頭註解已寫明「ast-grep 的 utils 只在同一份規則文件裡有效」並要求一起改。
   - 我對 C-34 另跑了 sbr.yml 當年「長函式輸出爆量」的場景:1500 條 `x.let{}` 的函式掃出 3000 筆(含 C-11 另 1500 筆),最長一行 1225 位元組,沒有爆量,C-34 也沒有誤命中非值位置的 let。

## 圖譜鏡頭
這次沒附固定席節點(派工附的 `LUMOS-LENS` 寫「這次沒附固定席節點」),所以沒有可逐條判的節點。`LUMOS-ARCH-TARGET: on` 我只做了程式碼層的對齊判定。

派工附的 `.warming` 鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/bee3b5b9dc06f1892927453312e887379169ca51a207a1fe8cc45ab1952890e2.json.warming` 不存在,不用處理。

不對齊共 1 條,其中 major 1 條
最嚴重:major;blocking 共 1 條

我在 `/tmp/lumos-seat-work/code-選擇點第二批/架構對齊-sonnet/` 留了三樣東西:`repo`(`eebb8459` 的 clone)、`big`、`ta`、`tb`(1500 行掃描用的暫存 kt 檔)。依規定要刪的話,請編排者收貨後用字面絕對路徑刪。
