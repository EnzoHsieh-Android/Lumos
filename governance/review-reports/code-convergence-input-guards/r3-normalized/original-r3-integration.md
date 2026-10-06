severity: minor

審查範圍：指定鏡頭內發現 1 項文件／歷史證據缺口；未把靜態閱讀冒稱為兩版實跑結果。

## integration-F1

severity: minor  
blocking: 否  
file: `skills/lumos-design-loop/templates.md:187`  
file: `skills/lumos-design-loop/templates.md:195`

引句:「中間點可用暫時本機提交；推前仍按一功能一提交整理，最後可一起PR，不因此增加輪數。」

觀察：流程允許暫時提交之後 squash／rebase，binding 卻只要求記提交碼、tree 碼與 patch 指紋，三份新增手冊都沒有要求保存可取回兩棵完整 tree 的 ref、bundle 或物件封存。提交變成 unreachable 且被剪枝後，SHA 只是識別碼；repair patch 又只是兩端差異，不能單獨還原修前完整產品及未變更的相依檔。

判準：歷史證據若要支持同案例兩版重跑，接手者必須能實際載入兩份完整來源，而不只是核對雜湊。當前案例的 scope-binding 另稱有 `r2-source-history.bundle`，但共用手冊沒有把這項必要保存動作制度化。

具體輸入路徑：上一輪被審提交 A → 本機修補提交 B → 推前 squash／rebase → unreachable 物件遭剪枝 → 接手者依 `rN-repair-binding.json` 執行 `git show A:<檔案>`。預期問題是 A/B 完整 tree 不可取得，repair／preserve 兩版驗證只能記未判定。

靜態查核命令與原輸出：

```text
$ rg -n '中間點可用暫時本機提交|before_commit|patch_sha256|bundle|git bundle|prune|gc|archive.*object|物件封存' skills/lumos-design-loop/templates.md skills/lumos-code-loop/SKILL.md skills/lumos-project-notes/commands/06-代碼審與推送.md
skills/lumos-design-loop/templates.md:187:   - 中間點可用暫時本機提交；推前仍按一功能一提交整理，最後可一起PR，不因此增加輪數。壓提交或換基底後按原規則重新固定派工版本與留痕，歷史中間結果不可挪成新版本通過。新席從完整改動核對作者分類，不以分類排除檔案。
skills/lumos-design-loop/templates.md:195:3. **留來源**：建立 `rN-repair-binding.json`，記 `before_commit`、`after_commit`、兩端 `git rev-parse "<提交碼>^{tree}"` 的樹碼、`patch_sha256`、上一輪派工單與 fix-check 結果檔的位置及 SHA-256（沒跑則記未執行）、`ancestry`（`git merge-base --is-ancestor` 的 rc0/rc1；其他退出碼是查詢失敗）、`attribution_limits`。指紋用讀檔 bytes 計算；派下一輪時再核對一次，版本與材料不符就重做。另在 intake 保留本輪 fixed/unaffected 路徑的說明，不能讓它代替完整差異。
skills/lumos-design-loop/templates.md:209:修補鏡頭：修前 {before_commit} → 修後 {after_commit}。
```

動態重現未執行；唯讀環境不能建立自己的 temp：

```text
$ review_tmp=$(mktemp -d /tmp/lumos-r3-review.XXXXXX)
mktemp: mkdtemp failed on /tmp/lumos-r3-review.YXhsCd: Operation not permitted
```

因此未能實際執行 squash＋prune 翻紅，依規則由 major 候選降為 minor。  
歸因：未判定；可確認缺口位於本輪新增流程文字，但沒有可比的兩版行為實驗證明它由上一輪修補造成。

建議保留一種可驗證的完整來源：例如在 binding 記錄並核驗 history bundle 的 SHA／heads，或用受保護 ref 保留兩端物件；不能只留 commit/tree ID。

## 三問

1. 原問題修復效果

- 快照根因組：
  - repair 候選：`cmd_canary` 的載體席讀到非法 UTF-8 快照，應 rc2、指出 `--snapshot`，且不新增帳。
  - 推導：由 `_quote_rows` 的直接呼叫者及「載體引句須錨回同份原始快照」合約選出。
  - 結果：未判定；兩版同案例未實跑。

- node-home 根因組：
  - repair 候選：同一提交修改正式程式、已宣告歸屬且確實變更的測試、以及該測試之家正文，應容許測試成為寫回路由證據。
  - 推導：由 `_nodehome_route_tests`、`_nodehome_evaluate` 呼叫鏈及測試免強制安家但可自願宣告歸屬的合約選出。
  - 結果：未判定；兩版同案例未實跑。

- 修訂輪證據流程：
  - repair 候選：固定 before/after、完整 repair patch、tree 與 patch 指紋應能讓接手者重建兩端。
  - 結果：當前 scope-binding 宣稱另有 history bundle，但本席未讀封存；共用流程存在 integration-F1，不能下「來源可長期還原」結論。

2. 正常、錯誤及相鄰路徑是否保留

- 快照 preserve 候選：合法 UTF-8／CRLF 載體仍成功，並以原始 bytes 記指紋；理由來自 caller 原有成功契約。
- node-home preserve 候選：被設定 ignore 的測試不得成為路由證據，新增無家的正式程式仍須阻擋；理由分別來自 `_nodehome_required` 排除條件及每支正式程式須有家的合約。
- fix-check preserve 候選：它仍只證修後指定測試綠，不證修前紅或修補因果；`r3-scope-binding.txt:12` 明確維持此界線。
- 結果全部未判定：未取得同案例、同夾具、同環境的兩版原始輸出。

3. 新發現兩版結果

- integration-F1 是新增手冊的靜態缺口。
- 修前：該流程尚未存在，不能當作產品案例成功。
- 修後：文字允許暫時提交與整理歷史，但未要求保存完整物件。
- 動態結果與修補因果：未判定；沒有拼版本或把 temp 建立失敗冒稱產品翻紅。

## Manifest 與固定合約

- `_nodehome_evaluate` 的 C901：manifest 明載不是雙版本新增判定；只有複雜度警示，沒有具體錯誤輸入，不列 finding。
- 新測試的 B023：閉包皆在各自迴圈迭代內同步使用，未看到延後到下一迭代的具體路徑，不列 finding。
- 測試函式 C901：僅維護性訊號，沒有行為失敗場景，不列 finding。
- design-loop 計劃 `.md`／綁定條款合約：不影響；改的是派工範本，未改判閘路徑。
- search 排除 superseded 合約：不影響；沒有修改 search 實作。
- bound-tests 阻擋語意：不影響；沒有修改 bound-tests 執行或 rc 判定。
- guard-kill rc 優先序：不影響；只收窄手冊對「有效翻紅」的人工判讀，CLI 判定碼未改。
- guard-kill JSON 純度：不影響；沒有修改 JSON 輸出路徑。
- vendored whitelist 不含授權檔：不影響；沒有修改 whitelist／deinit。
- scripts/lumos SPDX＋MIT 全文：不影響；檔頭與複製集合未修改。
- 假綠前置斷言合約：靜態上新增測試有現場前置斷言及普通／`-O` 控制；因未實跑，執行結果仍未判定。

## 已讀材料

- `governance/review-reports/code-convergence-input-guards/r3-source.patch`：1178 行
- `governance/review-reports/code-convergence-input-guards/r3-scope-binding.txt`：15 行
- `governance/review-reports/code-convergence-input-guards/r3-graph-lens.txt`：57 邏輯行（56 個換行，末行無 LF）
- `governance/review-reports/code-convergence-input-guards/r3-pitfalls.json`：198 行
- `governance/review-reports/code-convergence-input-guards/r3-test-layers.txt`：0 行
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- 派工詞：20 行
- 必讀審材＋派工：1701 行
- 額外定點上下文：98 個唯一來源行（`scripts/lumos` 88、`scripts/test_lumos.py` 7、`skills/lumos-design-loop/templates.md` 3）
- 審查上下文合計：1799 行
- 另讀適用規則：`/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md` 70 行、repo `AGENTS.md` 97 行；屬操作規則，不計審材上下文。

最高級：minor  
阻擋數：0  
三問未判定範圍：兩個程式根因組的修前／修後同案例實跑、history bundle 實際可讀性、所有綁定測試與完整來源重生；原因是唯讀環境禁止建立自己的 temp。