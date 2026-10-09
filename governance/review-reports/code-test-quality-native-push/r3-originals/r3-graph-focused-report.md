severity: major

## Finding 1

severity: major  
blocking: 是

有效決策仍宣稱白名單只有 5 檔；修前、修後的程式實際都是 8 檔。修訂雖移除了正文中的重複列舉，卻漏掉同一節點內權威更高的 `decisions` 紀錄。

引句:「_VENDORED_TOOLKIT(5 檔常數)為 vendor 端與 deinit 端共用白名單」

佐證 file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:56`  
佐證 file: `scripts/lumos:22148`

- input：`598e41…` 與 `03a46d…` 的 `scripts/lumos`、`Systems/lumos-cli-lifecycle.md`。
- expected：依 `CLAUDE.md`「怎麼用」第 3 條，結構化 `decisions:` 可以挑戰程式碼；因此不得保留可由程式推導、且已錯誤的「5 檔」快照。應移除數字，或作廢 d3 後新增不重複列舉成員的決策。
- before：
  - AST 解析 `_VENDORED_TOOLKIT`：8 項，rc=0。
  - 搜尋 `_VENDORED_TOOLKIT(5 檔常數)`：命中，rc=0。
- after：
  - AST 解析 `_VENDORED_TOOLKIT`：仍為 8 項，rc=0。
  - 同一錯誤決策仍命中，rc=0。
  - 實際載入 `/private/tmp/lumos-readme-oct-audit/scripts/lumos`：8 項，rc=0；載入檔 SHA-256 `17aea721f96b7a8c2cfefc9c5366f402d581da9bc7e1ff3c9c824df958b47ddb`。
  - `python3 scripts/lumos lint Systems/lumos-cli-lifecycle`：rc=0，表示現有 lint 沒有捕捉這種語意衝突，不表示內容正確。
- comparison/attribution：錯誤決策在修前已存在，不是本輪新增的產品退化；但本輪正好修改同一節點、宣稱收斂單一來源，修後仍留下更具資格的舊決策，因此原問題只修了一半。
- case_source：`graph-focused-repair.patch` SHA-256 `40ec92fdbff06fd72040d2abe5337b6ed863f4ca0e971235f2522a8aeac4c96d`；after blob `b92fde6b0b34b7d7ec4096125710c58142a25ff2`。

## 正向修復與保留證據

1. 正文的重複白名單確實已改成查程式單源。

   - before：舊「vendor 共用白名單＋成員列舉」命中 rc=0；新 WHY 不命中 rc=1。
   - after：舊段落不命中 rc=1；新「清單從 `_VENDORED_TOOLKIT` 查」命中 rc=0。
   - 佐證 file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:134`
   - 判準：程式可推導的現況不在圖譜保存第二份。
   - 結論：此局部修復有效，但被 Finding 1 的有效決策衝突抵銷。

2. 新驗證紀錄有明確資格邊界及重驗條件。

   - `valid_under` 排除原生裝置重跑與最終代碼審；正文也將治理節點聲明限縮為「只核對副檔名清單一致性」。
   - `revalidate_when` 與事件式 `REVISIT` 均存在。
   - `lumos context Verification/測試品質分支第二輪修復驗證 --brief`：rc=0，實際載入 10 條連出、9 條連入。
   - `lumos lint Verification/測試品質分支第二輪修復驗證`：rc=0。
   - 佐證 file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支第二輪修復驗證.md:5`
   - 佐證 file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支第二輪修復驗證.md:18`
   - 佐證 file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支第二輪修復驗證.md:24`
   - 佐證 file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支第二輪修復驗證.md:28`
   - case_source：after blob `2b71b57018d073734879fedc8effa0928d1e75a7`。
   - 限制：本席未重跑或重讀 R2 證據，因此只判定「資格文字與圖譜接線成立」，不判定其中測試數量及五棧結果為真。

## 固定圖譜鏡頭

- 圖譜新舊衝突：正文的新單源說法與 d3 的「5 檔」有效決策互相衝突；程式固定版本為 8 檔。
- 決策／驗證資格：d3 是結構化有效決策，不能當普通舊正文忽略；新驗證紀錄則有 `valid_under`、`revalidate_when` 與限縮聲明。
- 程式碼家責任：本輪 focused delta 將 handbook 總測試入口補入其節點，cochange、推播及治理帳說明也各落在相應 Systems 節點；未發現本輪新增的明確越界，但未重跑完整 S8–S10。
- 單源與重驗：正文單源修復成立；決策中的數量快照仍破壞單源。驗證重驗條件存在。
- 正常／錯誤／相鄰路徑：只確認圖譜文字及連結保留；沒有重跑產品行為，因此不宣稱整體無回歸。

## 覆蓋與限制

實際覆蓋：

- `binding-source.json`
- `graph-focused-full.patch`
- `graph-focused-repair.patch`
- 固定手動鏡頭
- `CLAUDE.md`、MOC、`lumos-project-notes`
- focused delta 的 7 個圖譜檔
- 固定版本 `_VENDORED_TOOLKIT`、完整 `_deinit_remove_vendored`、`_vendor_toolchain` 及必要呼叫上下文

來源指紋：

- binding：`52c39bf8612d87bdfb2d383e28d55842a0e9586275e6487e9de4bcd43e227ddc`
- full focused patch：`01bcb3d4f2173b164db990edee622b79a7c49a61900511aaad84299b14e20711`
- repair focused patch：`40ec92fdbff06fd72040d2abe5337b6ed863f4ca0e971235f2522a8aeac4c96d`
- fixed lens：`54e26b2dd342fafe742b47a5fcf12487e030f1be2de1ee9bad77ed6ea474b93e`

來源欄原樣保留：

> Includes product repairs, moved tests, mechanical classifiers, graph decision context and historical report archival; ancestor alone does not establish causality.

未驗範圍：

- 未讀 R1/R2 席報告及作者 intake。
- 未讀完整 `archive_only`。
- 未重讀百萬行完整 snapshot；其他席負責的檔案不在本結論內。
- 未執行 Windows 原生案例。
- 未重跑 R2 行為證據、五棧 runner 或完整 doctor。
- 一次收證命令因 zsh 參數展開與無副檔名載入器失敗；修正後已重跑，該失敗未當成產品紅。
- doctor 過濾命令未在 30 秒內產出結果，故未判定。

閱讀量保守記錄為約 1,926 行，已超過 1,800 行上限；因此本回覆只報告已確認的阻擋 finding，不冒稱完成整個修訂 delta 審查。剩餘範圍需另拆一席。