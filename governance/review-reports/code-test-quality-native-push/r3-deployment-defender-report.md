觀察

表態：`evidence`

半寫風險本身成立，但不足以維持「本次配套指紋修復造成的 major」。它是修前已存在、可恢復的通用 installer 非原子更新問題；本次差異沒有修改 `_vendor_toolchain`，相關設計也明示不重建安裝器。建議移出本輪 finding，另列既有 installer hardening；業務嚴重度不代替負責人裁定。

判準

1. 可達性：目的檔被截斷後、資料尚未完整寫入時若發生 `OSError`，是否可能留下半檔。
2. 本輪歸因：風險是否由 `598e… → 03a4…` 引入或擴大，或違反本次明示合約。
3. 影響：失敗後是否不可恢復、是否破壞使用者資料，以及 source/global 入口是否仍可重跑修復。

證據

- 實際可達：成立，但限於複製 `scripts/lumos` 本身時發生中途 I/O 失敗。`copy2` 沒有暫存檔加 rename：

  file: `scripts/lumos:22565`  
  引句:「for rel in _vendored_pending(src, root)」

  file: `scripts/lumos:22568`  
  引句:「shutil.copy2(s, t)」

  Python 3.14.6 標準庫靜態檢查顯示 `copyfile` 以 `open(dst, 'wb')` 開啟後串流寫入；純記憶體故障注入得到：

  `OSError simulated mid-write b'abcd'`

  因此演算法上確會保留部分資料，沒有 rollback。依唯讀限制，未做實體磁碟 ENOSPC／程序終止故障注入；各平台、檔案系統的具體半寫結果未判定。

- 這不是本次新增。修前、修後完整 `_vendor_toolchain` 函式雜湊完全相同：

  `5df69ccf…d0e00e5e`  
  `5df69ccf…d0e00e5e`

  file: `scripts/lumos:22564`（598e 修前）  
  引句:「shutil.copy2(s, t)」

  file: `scripts/lumos:22568`（03a4 修後）  
  引句:「shutil.copy2(s, t)」

- 與本次指紋修復的必要關聯不成立。本次控制只綁三支 `test_quality*` sidecar，沒有承諾 updater transaction：

  file: `scripts/lumos:49227`  
  引句:「def _test_quality_bundle_sources()」

  file: `scripts/lumos:49233`  
  引句:「for name, expected in _TEST_QUALITY_BUNDLE_DIGESTS.items()」

  file: `docs/lumos-toolchain-knowledge/Projects/測試品質部署配套校驗_計劃.md:19`  
  引句:「不新增依賴、不重建安裝器、不宣稱簽章或安全沙盒」

  file: `docs/lumos-toolchain-knowledge/Projects/測試品質部署配套校驗_計劃.md:24`  
  引句:「這只證版本配套一致，業務 oracle 與報告真實性仍由呼叫者負責」

- 複製順序也縮小了缺口：`scripts/lumos` 排第一，sidecar 隨後；因此後續 sidecar 半寫時，新 launcher 已在位，指紋 gate 會拒絕混裝。只有第一支 launcher 自己半寫，gate 才無法啟動。

  file: `scripts/lumos:22148`  
  引句:「_VENDORED_TOOLKIT = ("scripts/lumos", "scripts/test_lumos.py"」

  file: `scripts/lumos:22444`  
  引句:「for rel in list(_VENDORED_TOOLKIT) + list(_VENDORED_TREE_FILES)」

- 相關計劃與系統節點沒有要求 installer 原子發布的明示合約；系統界線反而限定此處只負責測試品質子命令的配套完整性：

  file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:56`  
  引句:「scripts/lumos 在此節點只負責測試品質子命令的部署完整性與註冊入口」

- `_vendor_toolchain` 沒有原子防護或自動 rollback，但有獨立 source/global 恢復路徑。Unix 全域 `lumos` 是指向來源 clone 的 symlink，專案內 `scripts/lumos` 半寫不會破壞它：

  file: `scripts/lumos:21339`  
  引句:「dst = bindir / "lumos"」

  file: `scripts/lumos:21347`  
  引句:「dst.unlink(); dst.symlink_to(src)」

  source `install.sh` 也直接執行來源 repo 的 launcher：

  file: `install.sh:63`  
  引句:「scripts/lumos" install --force」

  因此可從消費 repo 以全域/source `lumos update` 重跑修復；`install.sh` 本身只重建全域入口，不直接修復專案副本。

實際版本與來源綁定

- HEAD：`03a46da6b5179cfc5b42ced08e257ee127cc654e`
- before tree：`db550fcccddc4f832cd6a39cfe94087f2a75899f`
- after tree：`8aeb81d62fb6069bef85a39cd1d12b8777425600`
- ancestry：`598e…` 是 `03a4…` ancestor，rc `0`
- 與 `/tmp/lumos-r3-seat-prompts/binding-source.json` 完全相符。

查證命令結果

- 固定 `git show <commit>:<path>` 讀函式、caller、計劃與系統節點。
- 固定 `git grep <commit>` 定位 before/after 行號。
- 函式抽取後 `shasum -a 256`：before/after 相同。
- Python 標準庫靜態檢查：目的檔以 `wb` 開啟後串流複製。
- 純記憶體 partial-write：留下 `b'abcd'` 後拋 `OSError`。
- 未寫 repo、未建暫存檔、未讀其他席報告、未呼叫外部或付費模型。

實際閱讀量：1,315 行，以本席實際顯示的工具輸出行數計；低於 1,800 行上限。