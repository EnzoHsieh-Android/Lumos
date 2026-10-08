severity: clean

本席在指定極端輸入鏡頭內未發現具體可達的新缺陷。這只代表已驗案例乾淨，不代表全輪或未驗區域無回歸。

## Findings

0 條；無 boundary-F*。

## 三問

### 1. 修復效果

根因組 A：載體快照讀取／解碼

- 函式：`cmd_canary`；呼叫者：`canary record` 載體席；合約：引句必須用同一份 UTF-8 快照核對，失敗時不得落帳。
- repair 候選：非法 UTF-8、首次讀取拋 `OSError`。
- 固定兩版均已回傳 rc2、未 append；所以這不是 `f678…→95735…` 新修好的行為，不能歸因於本輪修補。
- preserve 候選：單一合法引句、空快照、未知解析例外。
- 兩版結果相同：合法單句成功且捕獲一次 append；空快照受控拒收；未知 `RuntimeError` 原樣上拋。

相關原輸出：

```text
before ... single-valid rc=None appends=1 reads=1
before ... empty-snapshot rc=2 appends=0 reads=1
before ... invalid-utf8 rc=2 appends=0 reads=1
before ... read-oserror-transient rc=2 appends=0 reads=1
before ... unknown-parser-runtime EXC=RuntimeError:probe-unknown-parser appends=0 reads=1
after ... single-valid rc=None appends=1 reads=1
after ... empty-snapshot rc=2 appends=0 reads=1
after ... invalid-utf8 rc=2 appends=0 reads=1
after ... read-oserror-transient rc=2 appends=0 reads=1
after ... unknown-parser-runtime EXC=RuntimeError:probe-unknown-parser appends=0 reads=1
```

根因組 B：`home check --diff` 未把同提交、已宣告歸屬的測試當作寫回路由證據

- 函式：`_nodehome_group_route_tests`／`_nodehome_mark_note_content`；呼叫者：`cmd_home_check --diff`；合約：測試仍免強制安家，但已宣告歸屬且同提交變更時可作路由證據。
- repair 候選：單一提交同時改正式碼、測試及該測試之家。
- 同一個記憶體案例實跑：修前只產生 `content_notes`、`route_tests` 不存在；修後產生 `route_tests={'tests/check.py'}`。
- preserve 候選：空提交群、缺失 repo、空／單字節／非法 UTF-8 筆記、未知解析例外。
- 兩版結果相同：空群回 `[]`；缺失 repo 清單回 `None`；三種筆記均受控解析；未知解析錯誤原樣上拋。
- 因唯讀 sandbox 禁止建立臨時 git repo，CLI 端到端 rc 尚未判定；只確認函式邊界修復。

相關原輸出：

```text
before single-group ... 'route_tests': 'ABSENT'
after single-group ... 'route_tests': {'tests/check.py'}
before empty-groups []
after empty-groups []
before list-missing None
after list-missing None
before parse invalid-utf8 OK ... '�'
after parse invalid-utf8 OK ... '�'
before unknown-parser EXC RuntimeError probe-unknown-note-parser
after unknown-parser EXC RuntimeError probe-unknown-note-parser
```

### 2. 正常、錯誤與相鄰路徑是否保留

在上述函式級同案例範圍內保留：

- 單一合法載體仍走成功 append。
- 空快照仍因唯一引句無法錨定而 rc2。
- 非法 UTF-8 與暫時 `OSError` 仍受控 rc2，沒有誤落帳。
- 未知引句／筆記解析例外沒有被寬泛捕捉或吞掉。
- 空提交群與讀不到版本清單仍採 fail-closed 結果。
- 非法筆記編碼的既有替換字元解析行為未改變；這是既有行為，未判定其產品規格是否理想。

### 3. 新發現的兩版結果

沒有新 finding。已驗極端案例不是兩版一致保留，就是單一測試路由案例出現預期修復差異；未見修後獨有失敗。

## 固定來源證據

```text
before f6787629227f40761e0969ae6e871198551f3e35 scripts/lumos-bytes-sha256 c4e55c0a5893ae3bb5b89e5b148ca235b1c0c7b24aad16baeed58bd8ed6dd6f8
after 95735eff7f3e17c930d43eecde5dd9d7c4fe9eff scripts/lumos-bytes-sha256 da19fe5403c871830f5a468415dbdf164cf550ca44aa058daee08dfa39c3ad6e
_nodehome_route_tests before=...:e5d435... after=...:e5d435...
_nodehome_group_route_tests before=absent after=29470:29490:18ba7c...
_nodehome_mark_note_content before=...:8c042a... after=...:008326...
_nodehome_evaluate before=...:85c104... after=...:85c104...
```

實驗以 `python3 -c` 從固定提交的 `scripts/lumos` bytes 直接載入；只替換檔案、ledger 與 git 清單協作者為記憶體 fixture，產品函式本體取自各自固定版本。沒有拼裝兩版產品。

臨時目錄實驗未執行，原始阻擋輸出：

```text
mktemp: mkdtemp failed on /tmp/lumos-boundary-r3.hGvti9: Operation not permitted
```

## 圖譜固定合約逐條

1. design-loop `.md` 計劃與綁定測試合約：不影響；未改 design-loop 判定入口，新文字只擴充 code-loop 修訂流程。
2. search 排除 superseded、不排 stale：不影響；沒有修改 search 濾網。
3. bound-tests gate：不影響；沒有修改測試解析、執行或 blocked 判定。
4. guard-kill rc 優先序：不影響；文件只收窄「仍綠」的推論，未改 rc 計算。
5. guard-kill JSON 純度：不影響；沒有修改 JSON 輸出路徑。
6. 授權檔不得進 vendored whitelist：不影響；未動 vendored/deinit 清單。
7. `scripts/lumos` SPDX／MIT 自包含：不影響；改動不在檔頭或複製檔集合。
8. 修 bug 測試須有現場前置斷言：未見破壞；新增測試含現場／來源斷言，但因 sandbox 未實跑，測試整體通過仍未判定。

外部碼表補選顯示因時間上限中止；本片段沒有外部回應碼比較，因此未據此作任何正向判定，也不冒稱 hook 成功。

## Manifest 判讀

只把落在新增行的 C901／B023 當注意力：

- `_nodehome_evaluate` 的 C901：兩端函式指紋相同，且複雜度本身沒有具體極端輸入失敗。
- 新增測試內的 B023：閉包均在該次迴圈內同步呼叫；未找到迴圈變數推進後才執行的路徑。
- `t_nodehome_optional_test_home_writeback` 的 C901：測試長度本身不是行為失敗。

因此不列 finding；也不把 manifest 當成兩版新增警告判定。

## 已讀材料（原樣）

- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-source.patch`：1178 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-scope-binding.txt`：15 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-graph-lens.txt`：57 個文字行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-pitfalls.json`：198 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-test-layers.txt`：0 bytes
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- `/tmp/lumos-future-repair-regression-research/AGENTS.md`：97 行，唯讀指令材料

## 額外上下文及行數

`scripts/test_lumos.py` 的符號／runner 定點輸出共 99 行；包含一次 chunk 邊界重讀，未讀完整巨型測試檔。`CLAUDE.md` 因 101 行超過剩餘 99 行限制而未讀。

最高級/阻擋數：clean / 0

三問未判定範圍：`home check --diff` 真實臨時 git repo 端到端 rc、`python -O`、成功 ledger 實際落盤與現有新增測試子集；以及本席鏡頭外的完整來源、直接修補、圖譜和控制覆蓋。