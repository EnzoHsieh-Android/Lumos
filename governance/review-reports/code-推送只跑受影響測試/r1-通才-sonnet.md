severity: minor

沒有會擋的問題。我讀完了掛鉤、`scripts/lumos`、新測試三段 diff 與被改到的函式本體。`t_pitfalls_pushed_mainline` 和 `t_prepush_feature_branch_*` 在 push-subset 跑了,共 16 項全過,最慢 50.7 秒(超時上限 180 秒,餘裕約 4 倍)。我沒有做變異實驗,下面「測試保護力」是靠讀測試推論的。

## 找到的疑慮

severity: minor
blocking: 否
功能分支只改測試檔時,本機一支測試都不會跑到
引句:「刻意不受 light_ok 約束(改到測試檔、守衛檔也降)」
`scripts/hooks/pre-push` 新增降級段,在 `_suite_this == full` 且 `pushed_mainline: false` 加 `suite_computed: true` 時,直接判成 light。
`_affected_test_keys` 只讀 `code_files`,而測試檔不算程式檔(`light_ok` 的 docstring 自己這麼說)。
失敗情境:功能分支只改 `scripts/test_lumos.py`(新增或改壞一個測試),`code=[]`,關鍵字為空,本機只跑文件子集。新測試推送前一次都沒跑,要等 PR 的 CI 才第一次執行。
改到 `governance/anchor-baseline.json` 或 `governance/code-loop/` 時同理:`_test_suite_for_range` 的守衛檔提早回傳仍帶 `computed=True`,所以也被降級。
這是設計明講的取捨(S6、計劃的守衛面),補償靠 PR 的 CI。我只標出來,不是缺陷。

severity: minor
blocking: 否
`_test_suite_for_range` 的 docstring 沒寫新欄位 `computed`,守衛檔分支的語意也和它對不上
引句:「回 dict:suite(docs|full)、reason、code(非文件且是程式檔的清單)」
`scripts/lumos` 的 `_test_suite_for_range` 回傳多了 `computed`,docstring 沒補。
守衛檔那一支仍寫「要全套」,卻帶 `computed=True`,在功能分支上實際會被降級。
下一個讀 docstring 的人會以為守衛檔一律本機全套,而現在不是。

severity: minor
blocking: 否
掛鉤裡「抽關鍵字、記自主迴圈全套」的三行重複貼了兩份
引句:「_k="$(printf '%s' "$pf_json" | "$PY" -c 'import json,sys; print(",".join(json.load(sys.stdin).get("affected_keys", [])))' 2>/dev/null || true)"」
light 區塊和新的降級區塊各有一份,每個 ref 都會多起一次 python 子程序。
具體風險:將來有人改 `affected_keys` 的取法,只改其中一份,功能分支與 light 兩條路徑的關鍵字就分叉。

## 其他角度

- **被刪掉的行為**:被拿掉的是「嫌久可 --no-verify,CI 會兜底」(光文件子集那句)與「CI 會跑全套當後盾」。全套路徑上的 `--no-verify` 提示原樣保留,推 main 時仍成立。降級後的訊息和新增的 `t_prepush_feature_branch_*` 測試取代了舊句。
- **跨檔追蹤**:`_pitfall_diff_mode` 只在 `pushed_ref is not None` 時多加欄位,舊呼叫端的回傳不變。`_test_suite_for_range` 其他取用處都是 `_sr["…"]` 或 `.get`,不受新欄位影響。
- **新函式的邊界**:`_pitfalls_pushed_mainline` 對 `refs/tags/`、空字串、`refs/heads/` 都回 true(保守倒向全套)。
  - 它呼叫的 `_note_reread_mainline_names` 查候選失敗時退回 `{main, master}`。
  - 那個函式有 10 秒期限,不會阻塞推送。
  - 舊版 lumos 靠探 `dest="pf_pushed_ref"` 字樣不帶新旗標,`t_prepush_feature_branch_old_lumos` 驗到會退回全套。
- **重用**:主線集合沿用既有的 `_note_reread_mainline_names`,沒有重做。
- **測試保護力**(讀測試推論,未實際變異)
  - 把 `pushed_mainline` 改成恆 false:`t_prepush_feature_branch_failclosed`(推 main)與 `t_prepush_feature_branch_mixed_with_main` 會紅。
  - 拿掉 `suite_computed` 判斷:`t_prepush_feature_branch_failclosed` 的「算不出範圍」那段會紅。
- **慣例**:新函式和旗標看不出違反全域或專案 CLAUDE.md 的條文。
- **併發類**:manifest 裡只有 lint 項,沒有併發類要判。

## 八篇固定席圖譜節點

用 `scripts/lumos show <節點> | grep` 只讀了合約行與 PITFALL 行,沒有整篇通讀。`Issues/code-loop守衛main-direct盲區` 查不到合約行或 PITFALL 行,所以這篇沒有判。

| 節點 | 判斷 |
|---|---|
| `Systems/pitfalls-code-loop` | 不影響。`pitfalls --json` 只新增欄位,原有 key 都沒動。 |
| `Systems/bound-tests-gate` | 不影響。合約是 code-loop check 逐支真跑綁定測試,這次沒碰那條路,只改 pre-push 的測試範圍選擇。 |
| `Systems/lumos-cli-read` | 不影響。看到的 INVARIANT 與 PITFALL 都在 security list、lint 一帶,`pitfalls` 仍是唯讀提示器。 |
| `Systems/design-loop` | 不影響。處置閘與凍結沒被碰到。 |
| `Systems/guard-kill` | 不影響。`guard kill` 的 rc 與 JSON 輸出合約沒被碰到。 |
| `Systems/lumos-cli-lifecycle` | 不影響。`re-inject` 與 sentinel 沒被碰到。 |
| `Systems/測試假綠形態` | 新測試沒有已知的假綠形態。「全程帶 --suite」用 `all(...)`,同時有「有關鍵字那一趟」的肯定斷言。降級行用 `count == 1` 加訊息字樣。 |
| `Issues/code-loop守衛main-direct盲區` | 未判,見上。 |

我沒有建立臨時目錄,不需要清理。
