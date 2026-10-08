severity: minor

## logic-F1

severity: minor  
blocking: 否  
file: `scripts/lumos:30041`  
file: `scripts/lumos:29668`

引句:「            staged_route_tests.clear()                     # 觀察到索引變動時撤回借用證據,不改既有正式程式退路」

觀察：提交前檢查只比較開始與結束兩次 `ls-files -s -z`。索引若暫時改動後恢復成原值（ABA），兩次內容仍相等，但中途 `_nodehome_reader(..., from_git=True)` 已可能採信不屬於最終索引的測試內容。

判準：路由證據必須與被判定的同一份不可變索引快照一致；只證明開始值等於結束值，不能證明中間讀取也來自該版本。

具體輸入路徑：

1. 暫存 `src/a.py`、`tests/check`、`Systems/TestHome.md`。
2. 最終索引中的無副檔名 `tests/check` 沒有 shebang，因此不是可借用的測試程式；`TestHome` 又不擁有 `src/a.py`，正常應拒收。
3. `N` 與 `changed_paths` 建立後，另一程序暫時把 `tests/check` 換成含 Python shebang 的索引版本。
4. `_nodehome_route_tests` 從當下索引讀到 shebang，把它加入 `staged_route_tests`。
5. 另一程序在最終比較前恢復原本無 shebang 的 blob。
6. 起終兩次 `ls-files` 完全相同，集合不會清除；`g_route_code` 仍含 `tests/check`，錯誤放行最終索引。

根因推導：

- 函式：版本清單與檔案內容不是從同一個不可變索引樹讀取。
- 呼叫者：`cmd_home_check --staged` 把多次即時索引讀取當成同一提交候選。
- 合約：新增註解要求只有「實際變更且已宣告歸屬的測試」能作證；瞬時內容不是最終待提交內容。

修補候選：開始時取得不可變索引樹並讓 changes/list/reader 全部從該樹讀取；結束再確認目前索引仍對應該樹。  
保留候選：穩定索引下，合法的 production＋owned-test＋TestHome 寫回仍應 rc0；測試未變更時仍應 rc1。兩項須分開驗。

歸因：未判定。來源差異顯示修前沒有 `staged_route_tests` 放行路徑，但兩版未實跑，不能據此列為有證據的修復回歸。

嚴重度說明：若翻紅，後果是治理閘錯誤放行，原應為 major；因唯讀環境無法建立隔離 fixture，未能翻紅，依派工規則降為 minor。

命令原輸出：

```text
$ review_tmp=$(mktemp -d /tmp/lumos-r3-review.XXXXXX)
mktemp: mkdtemp failed on /tmp/lumos-r3-review.KSAQBB: Operation not permitted
```

```text
$ mktemp -d "$PWD/lumos-r3-review.XXXXXX"
mktemp: mkdtemp failed on /private/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-r3-logic-review-5ugf84ih/lumos-r3-review.HHdMqN: Operation not permitted
```

修前結果：未執行；無法建立自有 temp。  
修後結果：未執行；無法建立自有 temp。  
未改在來源 repo 執行 git，也未拼接版本。

## Manifest 判定

- `scripts/lumos:29558` C901：複雜度本身沒有具體錯誤輸入；不另列 finding。
- `scripts/test_lumos.py:26025-26034`、`26133-26143` B023：閉包均在該次迴圈內同步呼叫，沒有跨迭代晚綁定；不列 finding。
- `scripts/test_lumos.py:48822` C901：測試函式複雜度未提供行為失敗；不列 finding。
- `scripts/test_lumos.py:49074-49083` B023：量測器在迭代內使用，`finalize` 綁定的是當下 `alive.discard`；未得出現行失敗。
- 以上只判新增行注意力 claims，不冒稱為雙版本新增警告結論。

## 固定合約逐條判定

- design-loop 審材型別與條款綁定：不影響；本補丁沒有改該判定。
- search 排除 superseded、保留 stale：不影響；搜尋路徑未改。
- bound-tests 紅燈／懸空／不可證執行即阻擋：不影響；runner 與 rc 聚合未改。
- guard-kill rc 優先序：不影響；執行判定未改。
- guard-kill JSON 純度：不影響；輸出路徑未改。
- LICENSE／NOTICE 不得進卸載白名單：不影響；白名單未改。
- `scripts/lumos` SPDX 與 MIT 文字：不影響；檔頭未改。
- bug 測試須有現場前置斷言：現有新增案例有 staged paths、競態觸發等前置檢查；未見直接破壞。logic-F1 是缺少 ABA 案例，不等同現有案例沒有前置斷言。

## 五問

- 新舊互讀：沒有新增持久格式；提交圖讀取仍涵蓋父版與修後版。兩版實跑未完成，整體相容性未判定。
- 半寫：canary 解碼／讀取錯誤在追加帳本前返回；來源上未見半筆成功帳。未實跑。
- 衍生資料：`route_cache` 是有界暫存；`staged_route_tests` 卻可能採信瞬時索引，見 logic-F1。
- 時間：起終相等不能排除中途 ABA，這是本席新發現。
- 不可逆：新程式沒有新增外部不可逆動作；canary 帳仍是追加式，但錯誤路徑移到追加前。未實跑驗證。

## 修復／保留／新發現三問

1. 原問題是否修復：未判定。  
   - canary repair：非法 UTF-8 應由未受控例外改為 rc2 且不落帳；來源可見修法，兩版未跑。  
   - nodehome repair：production＋owned changed test＋TestHome 寫回預期由 rc1 變 rc0；兩版未跑。

2. 正常、錯誤與相鄰路徑是否保留：未判定。  
   - canary preserve：合法 CRLF 載體仍應成功並記原始 bytes 指紋。  
   - nodehome preserve：untouched test 仍應拒收，穩定合法 mixed case 仍應放行。  
   - 上述候選皆有來源測試，但沒有本席兩版實跑證據。

3. 新發現同一案例的修前／修後結果：未判定。  
   - 修前來源沒有測試路由借用，理論上會拒收。  
   - 修後存在 ABA 瞬時證據放行路徑。  
   - 因兩版均未執行，不把來源推導升格為修復回歸。

## 已讀材料

- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-source.patch`：1,178 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-scope-binding.txt`：15 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-graph-lens.txt`：57 邏輯行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-pitfalls.json`：198 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-test-layers.txt`：0 行、空檔
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- 派工詞：20 行

額外上下文及行數：

- `/tmp/lumos-future-repair-regression-research/AGENTS.md`：97 行
- 其餘程式上下文：0 行

最高級：minor  
阻擋數：0  
三問未判定範圍：固定 HEAD 獨立核對、兩版產品載入、repair/preserve 實跑、logic-F1 兩版歸因；原因均為執行環境禁止建立自有 temp。