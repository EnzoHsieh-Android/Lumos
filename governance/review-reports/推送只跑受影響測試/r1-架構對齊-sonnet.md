severity: major

**1. 分層與依賴方向**

severity: minor
blocking: 否(結構大致對,只有旗標命名不齊)
- spec 段落:做法 1「`--target-ref <ref>`」。
- 問題:「這次推到哪個遠端 ref」這個資訊,鄰居已經有一套傳法,叫 `--push-remote` 加 `--pushed-ref`。這份 spec 另取名 `--target-ref`。
- 佐證:`scripts/hooks/pre-push:58`、`scripts/hooks/pre-push:698`、`scripts/hooks/pre-push:700` 都用 `--pushed-ref`。`scripts/lumos:65263` 的 `_push_mainlines(repo_root, remote, pushed_ref)` 同樣用 `pushed_ref`。
- 層次本身對得上。選測判斷放在 `scripts/lumos` 的 `_test_suite_for_range`(`scripts/lumos:61705`),pre-push 和 CI 只讀 `pitfalls --json` 的結果,跟現行一樣。
- 「不是 main 或 master」的口徑如果要跟 `_push_mainlines` 一致,就該直接重用它的候選與跳過規則,不要另寫。

**2. 命名與錯誤處理**

severity: minor
blocking: 否
- 逃生環境變數:鄰居是 `LUMOS_SKIP_*`(`scripts/hooks/pre-push:532`、`:693`、`:724`、`:734`),意思是「少做」,而且 `LUMOS_SKIP_NOTE_SHAPE` 會留帳。spec 的 `LUMOS_PREPUSH_FULL=1` 方向相反(多跑),也不留帳。前綴 `LUMOS_PREPUSH_*` 在 repo 裡也沒有先例。
- 這個差別 spec 有交代理由(多跑不是少跑),所以我只列 minor。
- 失敗退路對齊鄰居:算不出一律退全套,跟 `scripts/lumos:61710-61716` 的 fail-safe 同向。
- 輔助函式 `_affected_test_keys_wide` 的命名跟 `_affected_test_keys` 一致,沒問題。

**3. 第二種做法(重點)**

severity: major
blocking: 是(多一套選測算法,與現有的 light 並存)
- spec 段落:做法 1。
- 引句:「關鍵字改成新函式 `_affected_test_keys_wide`(既有 `_affected_test_keys` 留給 light 用、不改)」
- 問題:這是第二套「怎麼從 diff 抽關鍵字」。現有那套只取動到的頂層函式名加檔名(`scripts/lumos:61758`)。新的多了三項:往上追一層呼叫者、大檔不用檔名、把 `t_` 函式名算進去。
- 這會讓同一個 repo 並存兩套選測,輸出也不同。spec 沒說 light 什麼時候還會用到,也沒說兩者何時該合併。
- 更貼近既有做法的選項:直接擴充 `_affected_test_keys`,加一個參數,或把 light 一起升級成同一套。

severity: major
blocking: 是(第三套主線起點算法)
- spec 段落:做法 7 和做法 4 的 PR 起點。
- 引句:「先找各遠端的 `main`/`master` 追蹤分支(同 `_push_mainlines` 的候選),取跟頂端分岔點最新的那個」
- 問題:repo 裡已經有兩套起點算法並存,而且 `_lens_push_base` 與 `_push_range_start` 的 docstring 明講有收斂計劃(`scripts/lumos:65184-65210`、`:65263-65290`)。`_mainline_ref`(`scripts/lumos:65710`)是其中一套。
- spec 在 `_mainline_ref` 裡重刻 `_push_mainlines` 的候選邏輯,等於又加一份。`_push_range_start` 的 docstring 寫「起點只在這裡算一處」,這項正好違反它。
- CI 的 PR 範圍也用「`origin/main` 與 PR 頭的分岔點」自己算,同樣是新的第三套。
- 更貼近既有做法:`_mainline_ref` 直接呼叫 `_push_mainlines`,或表態閘改走 `_push_range_start`。這也是 `Issues/推送前其他閘的範圍在合過主線時會多算` 記的收斂路。
- spec 只說同一族,沒有說明這次是收斂還是另開第三條。

severity: major
blocking: 是(第二種通知方式)
- spec 段落:做法 4 `notify` 工作與做法 5。
- 問題:現行 `.github/workflows/ci.yml` 沒有任何開 Issue 或留言的步驟,`permissions` 全域只給 `contents: read`(`ci.yml:14-15`),workflow 裡 grep 不到 `issues` 或 `GITHUB_TOKEN`。
- 專案裡 CI 結果的回流管道是 `lumos ci-wait` / `ci-status`,要進治理帳(專案 CLAUDE.md 寫明不要用 `gh run list`)。專案自己的「Issue」是知識圖譜裡的 `Issues/` 筆記,不是 GitHub Issue。
- 新機制引入三樣東西:GitHub Issue 這個通知出口、`main-red` 與 `subset-miss` 標籤、`issues: write` 權限。同一個詞「Issue」還和圖譜 `Issues/` 撞名。
- spec 的 PRIOR-ART 只講業界做法,沒對照 `ci-status` 與治理帳。沒說為什麼不讓 `ci-status` 去偵測主線紅,也沒說為什麼不建圖譜 Issue。

severity: major
blocking: 是(CI 第一次引入「子集」)
- spec 段落:做法 4 prep。
- 問題:現行 CI 的範圍判斷是 `[ "$suite" = docs ] || suite=full`(`ci.yml:96`),也就是 CI 從來不跑 light 的關鍵字子集,只有本機掛鉤跑。
- spec 讓 CI 首次跑「文件子集加關鍵字子集」,並把 PR 事件從「一律全套」改成問 lumos。這改變 prep、shards、gates 三段的拆法(CI 加速計劃建立的結構)。
- 而且漏抓統計還要在 notify 裡重算一次選測(做法 5),等於在 CI 內部又長出一段選測呼叫。
- 這不是不能做,但和 `Projects/CI加速_計劃` 的「CI 只有 docs 子集」是不同的做法,spec 需要明說是刻意修訂,並同步更新那篇。

**4. 落點**

severity: minor
blocking: 否
- `Systems/bound-tests-gate` 本來就收了推送與 CI 提速的 WHY(分片、耗時表、CI 三工作,見該篇 summary 的 `[[Projects/推送與CI提速_計劃]]` 與 `[[Projects/CI加速_計劃]]` 行)。選測與 CI 範圍判斷落在這篇是對齊的。
- 但 spec 只列一個落點,不夠:
  - 做法 7(表態閘起點)該寫進 `Systems/棧別提問表態閘`。這篇有提到 `_test_suite_for_range`/範圍相關內容,而且 `Systems/存量漂移守衛` 負責 `_push_range_start`。
  - notify 與 Issue 通知是新職責,量夠大的話值得獨立一篇,或至少放進 `Systems/測試假綠形態` 或 CI 回流相關節點。這是 ⚠ 我判不準:取決於 notify 會長多大。
- 另外 `Systems/bound-tests-gate` 的負責範圍現在是空的(沒寫負責範圍,已掛 0 份計劃)。再塞進選測、notify、起點,這篇會繼續膨脹。

不對齊共 6 條,其中 major 4 條。

最嚴重等級 major,會擋的問題 4 條。
