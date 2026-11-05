severity: minor

**finding 1:主線名不是 main/master、又查不到遠端主線候選時,推主線被當功能分支降級**
severity: minor
blocking: 否
引句:「分支短名在 _note_reread_mainline_names 的集合裡(永遠含 main、master,再加主線候選指到的分支名,不看遠端名)→ true;其他 → false。」
file: `scripts/lumos:62348`(`_pitfalls_pushed_mainline`)
失敗場景:主線叫 `trunk`、沒有遠端追蹤 ref(第一次推到空遠端、或 origin/HEAD 沒設)。
- 實跑結果:臨時 repo 分支名 `trunk`、沒遠端,`pitfalls --diff trunk..HEAD --json --pushed-ref refs/heads/trunk` 輸出 `pushed_mainline: False`,`suite_computed` 為 True,掛鉤會降成 light。
- CI 只在 main 和 tag 觸發 push 事件,這種主線本機和 CI 都不跑全套。
- 另一個路徑:`_note_reread_mainline_names` 查候選逾時(10 秒)或失敗時只剩固定名,同樣會降。
- 歸因:未判定。主線名集合沿用既有函式,修前版本的降級判定也走同一個 `pushed_mainline`,我沒另跑修前版本比對。
- 這個 repo 的主線是 main,實際不會踩到;記作邊界。

**已驗、沒問題的部分(用臨時 git repo 實跑 `pitfalls --json --pushed-ref`,範圍 `main..HEAD`)**
- ref 形狀:

| ref | `pushed_mainline` |
|---|---|
| `refs/heads/feat` | false |
| `refs/heads/中 文/x main`(含空白、中文、斜線、以 main 結尾) | false |
| `refs/heads/main` | true |
| `refs/heads/master` | true |
| `refs/tags/v1` | true |
| 空字串 | true |
| `refs/heads/` | true |
| `main`(沒有 refs/heads/ 前綴) | true |
| `refs/heads/main/` | false |

  - `main/` 結尾這種 ref 名本來就不合法,不計為問題。
  - 以上除 `refs/heads/main`、`refs/heads/master` 外,結果都與設計意圖相符。
  - 這輪的修補(`_pitfalls_pushed_mainline` 的 ref 判定)和修前相比沒有改動,沒有修補回歸證據。
- `computed` 缺鍵:
  - `_test_suite_for_range` 的 4 個回傳(git 起不來、範圍錯、守衛檔、docs、full)都帶 `computed`;守衛檔那條用 `dict(full, ...)`,繼承 True。
  - 壞範圍 `nonexist..HEAD`:pitfalls 印「擋下:git 算不出…」、退出碼 2、stdout 沒有 JSON。掛鉤的 `pf_json` 為空,`_suite_this` 維持 full,不降級。
  - 測試 `t_pitfalls_suite_computed` 新增的 KeyError 斷言守住了「漏帶 computed」。
- 空範圍 `HEAD..HEAD`:`suite=docs`,不進降級。
- 守衛檔改動(`governance/anchor-baseline.json`)推功能分支:`suite=full`、`suite_computed=True`、`pushed_mainline=False`,會降成子集。這是設計明說的行為(註解:刻意不受 light_ok 約束),不是缺陷。
- 新的 `_down` 判定:
  - 兩個條件同時成立時 light 先走,`_SUITE_BRANCH_DOWN` 不被設,所以不印降級那行。
  - 只有 branch 條件成立時才設旗標並印提示。
  - `_suite_this` 不是 full 時整段略過。
  - 混推 main 時 main 那個 ref 是 full,整次推送照全套。
  - 圖譜子集不被 `--graph` 支援而退成全套時不印降級句,與實際行為一致。
  - 提示句只在 light 模式且旗標為 1 時印,標籤與主線推送都走不到。
  - 降級句用 grep 匹配 `pf_json` 的 `"pushed_mainline": *false`;檔名內的引號在 JSON 裡會被跳脫成 `\"`,偽造不了這個匹配。
- `t_prepush_feature_branch_already_light`:
  - 前置斷言有兩條:push-check 印「改動風險分級:light」,且 keys 子集有 2 片。
  - 若把 `_down` 的兩個分支順序對調,或 light 分支也設 `_SUITE_BRANCH_DOWN`,降級那行會印出,第三條斷言變紅。
  - 若 light 條件沒成立,會改走 branch 降級,同樣印出降級那行而變紅。
  - 沒有獨立斷言 `light_ok` 為 true,但由上面兩條斷言間接覆蓋,不算缺口。
  - 我沒另做變異實測。
- 跑了 `python3.14 scripts/test_lumos.py -k prepush_feature_branch`:20 passed, 0 failed。沒跑 `t_pitfalls_*` 兩支與全套。

**三問**
- ①修復效果的行為證據:上述 `_down` 路徑與 `already_light` 測試通過;修前版本我沒另外取出對照,只算現況通過,無法歸因為修補造成。
- ②相鄰路徑:推 main 全套、算不出範圍、舊版 lumos、混推 main 這幾條相關測試都在 20 條通過之內。
- ③新發現的同一案例修前修後:只有 finding 1,未判定。

**圖譜鏡頭(8 篇)**
- 我只用 `lumos show` 搜了 `INVARIANT`、`pre-push`、`全套`、`light` 這幾個字,沒逐篇細讀,判斷有限。
- 讀到的內容都沒有講到「推功能分支降成子集」或 `_pitfalls_pushed_mainline`。
- 「code-loop守衛main-direct盲區」那篇講的是 tier=high 的 code-loop 守衛,這次改動沒動那條路徑,判不影響。
- 其餘 7 篇沒讀到與這次改動衝突的句子;未逐篇確認的部分標未判定。

我的臨時目錄 `/tmp/lumos-seat-work/code-推送只跑受影響測試/邊界-sonnet` 已刪。
