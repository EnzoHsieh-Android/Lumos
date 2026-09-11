severity: minor

### F1 Gradle `src/` 測試資料夾分支沒有比照本輪新增的頂層 suffix 分支加副檔名錨,任何語言的檔案取巧放進 `src/.../androidTest`(或既有的 `test`)都會被靜默排除在需要家外
severity: minor
blocking: 否 — 需要刻意把非 JVM 副檔名的檔案放進 Gradle 保留目錄名字才會踩到,機率低,而且是既有「test/ 不分副檔名」慣例的延伸,不是全新機制;沒有在任何真消費專案(pos-ios)重現
引句:「return any(seg in under_src and "src" in parts[:i] for i, seg in enumerate(parts[:-1]))」
1. 本輪 delta 在頂層 suffix 分支(`scripts/lumos:17817-17819`)新增「只對貢獻那個結尾的棧的副檔名算」的錨,正是為了堵三席在第一輪造出的 ABTests/PaymentGatewayTests/LoadTests 反例;但 `src/` 分支(`scripts/lumos:17821`)完全沒有比照,`under_src` 判定只看資料夾名字,不看副檔名。
2. 在 /tmp 私有副本(scripts 整份複製,未動原 repo)實測:`_nodehome_is_test("module/src/androidTest/tools/gen.py", frozenset({"module"}))` 與同一目錄下的 `.sh` 檔皆回 `is_test=True`(需要家=False)——業務用的 Python/Shell 檔只要放進 `src/androidTest/` 就被靜默豁免,沒有任何擋。
3. 本輪新增的漂移守衛只測了 suffix 模式「不外溢到別棧副檔名」(⑤b),`src/` 模式沒有對應測試,這個不對稱沒被本輪任何測試覆蓋到。

---

## 逐項判定

- **風險掃描:模組層級延遲快取 `_NODEHOME_STACK_TEST_DIRS` 沒鎖** — 誤報。全檔（含本輪 delta）沒有新增 threading/multiprocessing/concurrent;CLI 是單一程序跑完就結束,`TEST_PROFILES` 全程只被讀不被寫,快取一旦算出就恆對。本輪只改了快取內部結構(從 `tuple(sorted(sufs))` 改成 `{suf: frozenset(exts)}`),沒有改變「模組級單例、無鎖」這個寫法本身,跟同檔既有的 `_STACK_GUESS_CACHE`(`scripts/lumos:14015`)、`_TESTMAP_DIR_RE` 同款,第一輪的判斷在第二輪仍然成立。
- **C1(第一輪 major:頂層 Tests 結尾資料夾不分棧別、不看副檔名整批免家)是否真的修好** — 已驗證修好,不是自報。私有副本各自載入改動前(bd0a8f26,把 r2-delta.patch 反向套用還原)與改動後(現版本)兩份 `_nodehome_is_test`,直接呼叫同一組路徑:`ABTests/ExperimentManager.swift`、`PaymentGatewayTests/reconciliation.py`、`LoadTests/db_schema.py`、`CheckoutIntegrationTests/pricing_engine.go` 在改動前全部誤判 `is_test=True`(免家),改動後全部正確回 `is_test=False`(要家)。另外把 `rstrip(".")` 手動突變掉重跑測試,`t_nodehome_stack_test_dirs_not_required` 確實翻紅(8 passed, 1 failed),印證釘子有咬到;`scripts/test_lumos.py -k nodehome` 全子集 177 passed 0 failed。
- **牽連鏡頭——誰還呼叫 `_nodehome_is_test`/`_nodehome_required`** — 全檔 grep,`_nodehome_is_test` 生產路徑只有 `_nodehome_required` 一個呼叫點(`scripts/lumos:18016`),且 `top_dirs` 是在 `_nodehome_required` 內部從當下那個 `side.all_paths` 現算(`scripts/lumos:18009`),`_nodehome_required` 的四個呼叫點(N/B/health-check side/G,`scripts/lumos:18222-18223`、`18497`、`18513`)各自吃到自己那個版本正確的 `top_dirs`,不存在「同一支檔在不同呼叫端判定不一致」的分岔;`_nodehome_is_test` 新增的 `top_dirs=frozenset()` 預設值只有測試檔直呼會用到,不影響生產路徑。
- **消費專案實跑(pos-ios,120 受版控檔,只讀)** — 用同一份私有副本分別載入 bd0a8f26(第一輪已提交的修正)與現版本(第二輪 delta 後)跑 `_nodehome_required`,兩邊算出的「需要家」集合完全一致(都是 32 支,差集為空)。pos-ios 是純 iOS Swift 專案沒有 `src/` 結構,不會踩到上面 F1 那個殘留缺口,也沒有新的假陽/假陰出現。
- **圖譜鏡頭——固定席節點逐條判** `bound-tests-gate`、`canary-audit`、`guard-kill`、`slim-get-一行安裝`、`slim-install-安裝器`、`slim-uninstall-一行卸載`、`授權與歸屬`:不影響。本輪 delta 只改了 `_nodehome_stack_test_dirs`/`_nodehome_in_stack_test_dir`/`_nodehome_is_test`/`_nodehome_required` 四支函式與一支測試,沒有碰 code-loop 綁定測試真跑、canary 落盤驗證、guard kill rc 優先序、`.ps1` 編碼、CLAUDE.md 注入還原、manifest 清理、SPDX/LICENSE 白名單這些機制,只是因為同一支 `scripts/lumos`/`scripts/test_lumos.py` 被列成間接相依。
- **`測試假綠形態`(還原翻紅釘的前置斷言要求)**:合規,不是空殼——上面「C1 是否真的修好」那條已經是這篇要求的具體實測:反向套用 delta 回到修前版本,四個反例全部從「要家」變回「不要家」,前置斷言成立;正向再套回去,同一組全部翻回「要家」。
- **其餘 15 篇「超出上限,只列名」的節點**(lumos-cli-lifecycle、lumos-cli-read、design-loop、pitfalls-code-loop、lumos-deinit、loop-convergence-recording、節點範圍與索引守衛、lumos-refcheck、cochange-guard、check-r-guard、doctor-irreversible-hint、reversibility-governance-ledger、check-t-sentinel、core-invariant-baseline、judge-severity-gate):不影響,理由同上——各自機制都沒被這支 delta 觸及,只是同檔案體積大導致 impact 把它們列成間接相依。

總結:最高 severity minor,blocking 共 0 條
