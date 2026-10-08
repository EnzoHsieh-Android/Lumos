severity: minor

## Finding

repair3-F1

severity: minor

blocking: 否

引句:「    before_n = sum(1 for ln in lines[1:e] if ln.strip() == target)」

file: `scripts/lumos:19458`

觀察：`summary-line` 的寫後驗證以整個 frontmatter 計算 `before_n`，但寫後只在解析出的 `summary` 計數。若改後摘要整行剛好等於既有 metadata 行，例如 `updated: 2026-01-01`，合法替換會被驗證器誤拒並回 rc=2。

判準：寫前與寫後計數必須使用同一資料範圍；此處應只計算原始摘要區，不能把 metadata 同名行算進基準。

具體輸入路徑：含 metadata `updated: 2026-01-01`、摘要行 `old` 的 `Systems/x.md`，執行等價於 `lumos summary-line Systems/x old "updated: 2026-01-01"`。

最小不落盤命令：載入固定 HEAD，猴子補丁檔案讀寫邊界，實際呼叫 `_summary_line_locked(..., "old", "updated: 2026-01-01", ...)`；`atomic_write_verify` 只執行真正的 `check` 閉包。

原輸出：

```text
擋下:synthetic verify rejected
改前:old
改後:updated: 2026-01-01
new_lines=['---', 'updated: 2026-10-07', 'summary: |', '  updated: 2026-01-01', '---']
verify=False
rc=2
```

普通、不碰 metadata 同名值的保留案例在修後為：

```text
改前:old
改後:new
verify=True
✓ 改好了 Systems/x.md(updated 改成 2026-10-07);接著跑 lumos lint Systems/x 看這一篇
rc=0
```

影響是狹窄合法輸入被拒；沒有資料毀損證據，因此定為 minor。

## 修補／保留候選

| 根因群 | 修補候選 | 保留候選 | 結果 |
|---|---|---|---|
| guard-kill 提醒 | 配方連同合約行帶出，新增測試清單提醒 | `--try` 仍以原配方產生 recipe id | 靜態路徑成立；雙版未跑，修復未判定 |
| updated 落後判定 | 淺複製、一天寬限、非法日期、單篇寫失敗 | 明確節點、`--dry-run`、無 `updated` 跳過 | 靜態路徑成立；雙版未跑 |
| summary-line | 換行、歧義、續行及空摘要守衛 | 一般單行替換 | 修後一般案例通過；另有 repair3-F1 |
| Claude 外掛 | 兩支外掛分開安裝／移除、安裝後重查 | 外來同名市集不動、只處理 user scope | 靜態成立；外部 CLI fixture 未跑 |
| 跑滿回顧 | 第八步、共用帳檔路徑守衛與單一失敗橫幅 | 既有七步與不適用迴圈 | 靜態未見移除既有步驟；雙版閘結果未判定 |
| nodehome 額外證據 | 共用雙版本快取、檢查期間索引變動即撤回 | 版本清單讀不到仍回空證據 | 靜態成立；索引競態 fixture 未跑 |
| drift 連結文字 | 待定詞只在 wiki 連結中時不誤報 | 待定詞在連結外仍判待定 | 修後純函式分別得到 `[]` 與一筆命中；雙版未比較 |
| 治理帳與日期 | 非一般帳檔拒絕、共用 `_ledger_lines`、實體路徑算 git 日期 | 硬連結／符號連結守衛及既有讀者 | 靜態成立；檔案 fixture 未跑 |
| 測試守衛 | AST 定位 nodehome 寫入點、quote parser 補 OSError | 原 RuntimeError 路徑 | 僅讀測試改動；runner 因無可寫 temp 未執行 |

## 固定合約逐條回答

以下「不影響」只限指定 patch 的靜態隔離判斷；共同主線變更沒有隔離證據，故不提升為全產品雙版結論。

- design-loop 計劃／條款綁定：片段不影響；第五步仍原樣呼叫，第八步在其後追加。雙版實跑未判定。
- search 排除 superseded、不排 stale：片段沒有 search/filter hunk；不影響僅限分配片段。
- pitfalls-code-loop：片段改 disposal 與提示呼叫，但未改 tier 計算；全鏈未跑，未判定。
- bound-tests gate：片段未改 bound-test 收集或 rc 合取；不影響僅限片段，完整 check 未跑。
- guard-kill rc 優先序：改的是 kill-add 提醒，不是 kill 執行結果判級；片段不影響。
- guard-kill JSON 純度：新增提醒位於 add／try 前置流程，未見 JSON 執行路徑改動；完整 JSON 測試未跑。
- 授權與歸屬兩條：外掛 teardown 沒改 `_VENDORED_TOOLKIT`、LICENSE 白名單或檔頭；片段不影響。
- 測試假綠前置斷言：指定 patch 未刪綁定測試或其前置斷言；殺傷力實跑未判定。

`r3-pitfalls.json` 的 C901／B023 claims 沒有一項落在本席指定 patch 的新增行；依派工規則不選入 finding，也不冒稱為雙版本新增告警。父席的 lint-new 結果不由本席代答。

## 三問結論

- 修復了嗎：未判定。唯讀沙箱無法建立同案例 before/after fixture，不能把修後綠或靜態閱讀冒稱修復成功。
- 保留了嗎：僅有修後普通 `summary-line` 與 drift 純函式觀察；因沒有同案例雙版實跑，跨版本保留仍未判定。
- 有新發現嗎：有，repair3-F1；最高 minor、非阻擋。此席不代表全輪無回歸。

雙版本建立原始失敗：

```text
mktemp: mkdtemp failed on /tmp/lumos-r3-seat.81WM86: Operation not permitted
fatal: could not create work tree dir 'after': Operation not permitted
fatal: could not create work tree dir 'before': Operation not permitted
```

定點測試 runner 亦在建立隔離環境前失敗：

```text
FileNotFoundError: [Errno 2] No usable temporary directory found
```

## 已讀材料

- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-segments/repair-3.patch`：1067 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-scope-binding.txt`：15 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-graph-lens.txt`：56 個換行、57 個邏輯行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-pitfalls.json`：198 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-test-layers.txt`：0 行、0 byte
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- `/tmp/lumos-future-repair-regression-research/AGENTS.md`：96 行
- `/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md`：70 行

額外定點程式上下文：`scripts/test_lumos.py` 測試名稱索引 65 行；`scripts/lumos` 精確佐證 2 行。未讀其他席、前輪報告、完整來源或巨型 CLI 其他段落。

最高級：minor；finding 1；阻擋數 0。