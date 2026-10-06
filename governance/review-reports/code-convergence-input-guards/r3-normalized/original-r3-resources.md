severity: minor

## resources-F1

severity: minor  
blocking: 否  
file: `scripts/lumos:30041`

引句:「        if staged_route_tests and (index_before is None or _nodehome_git(root, "ls-files", "-s", "-z") != index_before):」

觀察：暫存區只比較檢查開始與路由蒐集結束時的 `ls-files -s`。競爭者若在 `_nodehome_route_tests` 讀取期間換入另一索引內容，再於第二次比較前恢復原值，兩端完全相同，`staged_route_tests` 不會被清除。

判準：同一次判定採信的路徑清單、檔案內容與 shebang 分類必須來自同一個不可變索引快照；只比較兩個端點不能排除 ABA 時序。

具體失敗場景：

- 初始及最終索引的 `tests/check` 都沒有 shebang，依法不能作測試寫回證據。
- 同一提交另暫存 `src/a.py` 與 `Systems/TestHome.md`，後者只擁有 `tests/check`。
- 路由計算期間，另一程序暫時把索引中的 `tests/check` 換成帶 Python shebang 的 blob。
- `_nodehome_required(..., include_tests=True)` 因而把它收入路由證據。
- 競爭者在末次 `ls-files -s` 前恢復原 blob；端點比較相等，錯誤證據仍進入 `g_route_code`，原應以「不是任何一支改動檔的家」拒絕的提交可被放行。

靜態定位命令：

`awk 'NR==30041 {print NR ":" $0}' /tmp/lumos-future-repair-regression-research/scripts/lumos`

原輸出：

```text
30041:        if staged_route_tests and (index_before is None or _nodehome_git(root, "ls-files", "-s", "-z") != index_before):
```

最小實驗準備命令：

`review_tmp=$(mktemp -d /tmp/lumos-resources-review-XXXXXX)`

原輸出及退出狀態：

```text
mktemp: mkdtemp failed on /tmp/lumos-resources-review-u2847x: Operation not permitted
```

退出碼 1；固定兩版抓取及 ABA fixture 均未開始，沒有冒稱產品行為已翻紅。

歸因：未判定。新增行顯示問題落在修後端點檢查，但修前 `f6787629227f40761e0969ae6e871198551f3e35`、修後 `95735eff7f3e17c930d43eecde5dd9d7c4fe9eff` 都未能以同一案例實跑，不能列為有證據的修復回歸。

嚴重度說明：若重現，後果是治理閘誤放行，原可達 major；本席受唯讀環境限制未能建立 fixture 翻紅，依派工規則自降一級為 minor，故不阻擋。

建議方向：讓清單、內容及分類全程讀同一份私人索引快照，而不是依靠開始／結束內容相等；或持有能排除中途換入換出的索引鎖。

## Manifest 判讀

- `scripts/lumos:29558` 的 C901 只指出既有判定函式複雜，沒有獨立失敗場景，不列 finding。
- `scripts/test_lumos.py:26025-26034`、`26133-26143` 的 B023 閉包都在當次迴圈內同步呼叫，未見跨迭代延後執行的路徑。
- `scripts/test_lumos.py:49074-49083` 的 B023 物件生命週期在每輪內以 `gc.collect()` 與 `alive` 斷言收束；沒有具體晚綁定誤判場景。
- `scripts/test_lumos.py:48822` 的 C901 是測試維護性訊號，沒有行為失敗場景。
- 快取測試量的是容器存活量與呼叫次數；本席不把它解讀為 RSS 或速度證據。

## 固定合約逐條回答

- design-loop 處置閘 `.md` 計劃要求：不影響；補丁沒有改其材料類型或時間判定。
- search 排除 superseded、保留 stale：不影響；沒有 search 路徑 hunk。
- bound-tests 固定席真跑與 blocked 規則：不影響；沒有修改 bound-tests 執行或退出碼。
- guard-kill `survived/drifted/abort/error` 退出碼優先序：不影響；文件只收窄如何解讀殺傷力，沒有改 runner。
- guard-kill JSON 純度：不影響；沒有 stdout/stderr 或 JSON 分支變更。
- 授權檔不得進 `_VENDORED_TOOLKIT`：不影響；沒有 vendored/deinit 白名單變更。
- `scripts/lumos` SPDX 與 MIT 全文：不影響；補丁未改檔頭或複製集合算法。
- 假綠測試需前置斷言：未見破壞；新增測試反而逐項確認 staged 路徑、歸屬、索引內容及故障注入已到達，但因本席未實跑，僅能確認文字存在，不能宣稱測試實際有效。

## 修復／保留／新發現三問

1. 原問題修復效果：

   - `cmd_canary` 根因組：repair 候選為非法 UTF-8／首次 `read_bytes` 暫時失敗時不得寫帳；preserve 候選為合法全錨 UTF-8 載體仍落帳，且非載體仍保存原始 bytes 指紋。理由分別來自函式的驗句順序、呼叫者記帳語意及載體限定合約。兩版均未實跑，結果未判定。
   - nodehome 根因組：repair 候選為同提交修改正式程式、已宣告且確實變更的測試及其家；preserve 候選為 untouched、ignored、unowned、symlink 或無 shebang 的測試不得替錯家提供路由。理由分別來自 `_nodehome_route_tests`、`cmd_home_check` 呼叫邊界及「測試免強制安家但只有合格證據可借用」合約。兩版均未實跑，結果未判定。

2. 正常、錯誤及相鄰路徑是否仍成立：沒有同案例兩版實跑證據，因此所有正向行為主張均未判定；補丁內新增測試文字不能代替執行結果。

3. 新發現兩版結果：resources-F1 的 ABA 案例在修前、修後都未執行，故兩版行為及修補因果均未判定；目前只有修後新增端點比較的靜態可達路徑。

已讀材料：

- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-source.patch`：1178 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-scope-binding.txt`：15 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-graph-lens.txt`：57 個邏輯行（`wc -l` 為 56，末行無換行）
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-pitfalls.json`：198 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-test-layers.txt`：0 行，空檔
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- 指定材料合計：1681 個邏輯行；另讀派工內容 20 行

額外上下文：

- `/tmp/lumos-future-repair-regression-research/AGENTS.md`：97 行
- `/tmp/lumos-future-repair-regression-research/scripts/lumos:30041`：1 行
- 額外定點上下文合計：98 行；未讀其他席、前輪報告或巨型 CLI 其他正文

最高級：minor  
阻擋數：0  
三問未判定範圍：兩個根因組的全部兩版執行結果、resources-F1 的兩版歸因、所有未被指定材料涵蓋的路徑；本席 clean/單一 finding 均不代表全輪無回歸。