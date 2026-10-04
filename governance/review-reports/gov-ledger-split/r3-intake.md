# r3 收貨與重現

## 引句截斷

整合 #5 的引句被審稿原文的「」截斷成不到 10 字(工具印 <10 字下限),不採信這句引句;該條是 minor,內容由同席佐證行支撐,照常處置。

## blocking 重現

| finding | 重現 | 結果 |
|---|---|---|
| bound-tests green 藏沒跑的平台(正確性 c1) | `sed -n 42725,42735p scripts/lumos` 與 42895、42952 附近 | 採信:正確性席給出三個呼叫點,green 的判定不看是否每個平台都跑過;改為整個閘移出本機名單,偏保守 |
| 補建 docs/.gitignore 套整份清單會忽略另五本帳(正確性 c2、回滾 rb2、邊界 b 小) | `sed -n 20878,20881p scripts/lumos` | HIT:新建 vault 的清單含 .bypass-log、.canary-log、.kill-log、.signoff-log |
| 本 repo 還原後本機帳變未追蹤檔(回滾 rb1) | 根 `.gitignore` 是本 repo 唯一的忽略來源(本 repo 沒有 docs/.gitignore) | HIT:`ls docs/.gitignore` 不存在 |
| 本機帳誤提交讓留痕失效(邊界 b1) | `sed -n 24193,24200p scripts/lumos` | HIT:`_BOOKKEEPING_FILES` 是明列檔名,不含新檔名 |
