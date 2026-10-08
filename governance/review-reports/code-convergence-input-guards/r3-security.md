severity: clean

本席在指定安全鏡頭內未發現可利用的新洞；這不是全輪無回歸保證。

安全鏡頭結論：

- 不可信輸入：repo 投稿者可控制追蹤檔名、節點歸屬路徑；CLI 使用者可控制 report/snapshot 路徑。新增測試路由先與提交變更及版本檔案清單取交集，再要求分類為測試。選項狀輸入 `-c core.sshCommand=sh -c id` 在兩版皆得到空集合，沒有命令執行或路由權。
- 權限：沒有新增 chmod、chown、sudo、權杖或跨使用者存取；讀取仍以執行 CLI 的本機使用者權限進行。
- 秘密：沒有讀取或輸出環境變數、憑證或檔案內容。UTF-8 錯誤只輸出解碼位置；`OSError` 可能顯示呼叫者自己提供的本機路徑，未形成跨權限洩漏。
- 加密：SHA-256 僅用於同一份 bytes 的內容指紋，沒有被誤作身分驗證或秘密保護。
- 執行邊界：新增 production 路徑未使用 `shell=True`、`eval`、`pickle` 或動態載入投稿內容；Git object spec 仍作單一參數傳入。補丁中的 `runpy`／inline Python 注入均位於測試碼，輸入由 fixture 產生。
- 行動端／依賴：純 Python CLI，沒有行動端面；未新增第三方依賴，維持零依賴。

manifest 判讀：C901 是複雜度提醒；B023 均位於測試閉包，且補丁中的呼叫發生於相同迴圈迭代內。沒有可指出攻擊者、入口、具體輸入及所得的安全後果，因此不立 finding；也未把 manifest 冒稱雙版本新增警告判定。

固定合約逐條核對：

- design-loop「計劃必為 `.md`、條款須有綁定測試」：不影響；沒有修改 spec 類型或條款綁定判定。
- lumos-cli-read「search 排除 superseded、不排 stale」：不影響；沒有修改 search 路徑。
- bound-tests「綁定測試紅／懸空／偽證據／不可證明執行即擋」：不影響；沒有修改 bound-tests 執行或結果判定。
- guard-kill「survived／drifted／error 的 rc 優先序」：不影響；只改使用說明，未改 runner。
- guard-kill「成功 JSON 模式 stdout 恰一行」：不影響；沒有修改 JSON 輸出路徑。
- 授權「LICENSE/COPYING/NOTICE 不得進 vendored 清單」：不影響；沒有修改清單或卸載流程。
- 授權「scripts/lumos 檔頭與複製檔 SPDX」：不影響；沒有修改檔頭或檔案集合算法。
- 測試假綠「修復測試須有現場前置斷言」：未見破壞；新增測試含候選、索引狀態及注入是否發生的前置檢查。但沙箱不能建立 fixture，完整測試是否通過未判定。
- pitfalls-code-loop 是 ★RISK★ 而非固定合約；新增修訂輪證據規則沒有擴大執行權限。

三問：

1. 修復效果：函式層有證據。固定修前版沒有逐提交測試路由抽取器；修後版對同一組版本及候選辨識出 `scripts/test_lumos.py`。完整 `home check --diff` 端到端效果因唯讀沙箱不能建立 Git fixture，未判定。

2. 保留行為：同一探針中，正式程式 `scripts/lumos` 在兩版皆不被借作額外測試路由；選項狀惡意候選在兩版皆為空。非法 UTF-8 載體快照在兩版皆受控 rc2，未退回 traceback。

3. 新發現：沒有具體安全 finding；未測區域不能推論為無回歸。

同案例兩版實跑原輸出——路由修補及正式程式保留候選：

```text
f6787629227f40761e0969ae6e871198551f3e35
exit=0
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
test_candidate=[]
production_candidate=[]
95735eff7f3e17c930d43eecde5dd9d7c4fe9eff
exit=0
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
test_candidate=['scripts/test_lumos.py']
production_candidate=[]
```

不可信選項狀候選原輸出：

```text
f6787629227f40761e0969ae6e871198551f3e35
exit=0
untrusted_candidate=[]
95735eff7f3e17c930d43eecde5dd9d7c4fe9eff
exit=0
untrusted_candidate=[]
```

非法 UTF-8 載體快照原輸出：

```text
f6787629227f40761e0969ae6e871198551f3e35
exit=2
擋下:--snapshot 不是有效 UTF-8: 'utf-8' codec can't decode byte 0xca in position 0: invalid continuation byte
95735eff7f3e17c930d43eecde5dd9d7c4fe9eff
exit=2
擋下:--snapshot 不是有效 UTF-8: 'utf-8' codec can't decode byte 0xca in position 0: invalid continuation byte
```

測試限制：定點測試 `t_canary_carrier_invalid_snapshot_encoding()` 在建立 fixture 前失敗，原始原因為：

```text
FileNotFoundError: [Errno 2] No usable temporary directory found in [...]
```

HEAD 終場仍為 `95735eff7f3e17c930d43eecde5dd9d7c4fe9eff`；未修改 repo/git。工作樹已有其他會談／編排產物，本席未讀其內容、未清理。

已讀材料：

- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-source.patch`：1178 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-scope-binding.txt`：15 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-graph-lens.txt`：57 邏輯行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-pitfalls.json`：198 行
- `/tmp/lumos-future-repair-regression-research/governance/review-reports/code-convergence-input-guards/r3-test-layers.txt`：0 bytes
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- `/tmp/lumos-future-repair-regression-research/AGENTS.md`：97 行

額外上下文及行數：固定 HEAD `scripts/lumos:9675-9733` 59 行、`scripts/lumos:28918-28957` 40 行；合計 99 行。

最高級／阻擋數：clean／0。

三問未判定範圍：完整 CLI Git fixture、完整測試層、未實跑的固定合約測試，以及本席安全鏡頭外的正確性、整合、圖譜與控制覆蓋。