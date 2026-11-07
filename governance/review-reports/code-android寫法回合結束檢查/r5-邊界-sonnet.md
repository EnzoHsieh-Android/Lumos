severity: major

第四輪邊界席 F1(子目錄專案路徑基準)的核心問題修好了。我在 monorepo 實跑,專案目錄設在 `sub/`,檢查結果跟 `git status --porcelain` 一致:
- 乾淨的樹回空清單。
- 改檔、刪檔、未追蹤檔、結尾 CR 的檔名、含空白的檔名,路徑都是 repo 根相對。
- `_impact_wt_nofilter` 在根與子目錄給出的候選、模式、查詢文字相同。

但同一個根因還有一半沒收,見 F1。

**F1:鉤子拿 repo 根相對的路徑,接到子目錄專案根上,在 monorepo 子目錄會誤擋收工、也會漏掉沒副檔名的腳本**
- 輸入:repo 根有 `sub/` 與 `other/`。`sub/docs/x-knowledge/Systems/n.md` 已提交,`sub/a.py` 是程式碼。`sub/tool` 是沒副檔名、首行 `#!/bin/sh` 的腳本,已設執行權限。這三支都有改動,transcript 裡 `Write` 過 `sub/a.py` 與那篇筆記。`CLAUDE_PROJECT_DIR` 設成 `repo/sub`,餵 `check-graph-sync.py` 一份 Stop 的 stdin。
- 實際:
  - 輸出 `decision: block`(LUMOS-STOP),只點名 `` `sub/a.py` ``,說筆記沒動。
  - 筆記其實改了,卻沒被認成圖譜檔。
  - `sub/tool` 沒被點名。
- 預期:專案根設在 repo 根時,同一批改動靜默放行(rc0、無輸出)。我實跑確認過。子目錄專案也應該認得筆記已動,並點名 `sub/tool`。
- 原因:修補後 `_wt_changed_nofilter` 回傳 repo 根相對路徑(`sub/a.py`),但 `main()` 用 `project_root / r` 去接。接出來的是 `repo/sub/sub/a.py`,不存在。受影響的是 `is_graph_file(str(project_root / r), graph_root)` 與 `_entry_is_code` 裡的 `is_code_file(str(project_root / relpath), ...)`。`src_files` 傳給 `_impact_missing` 也是這種壞路徑。
- 對照:我用 7eaad22 的舊版鉤子跑同一情境,輸出一樣,所以這不是這輪新造的退步。但 r4 F1 的修法註解寫「回傳的路徑從 repo 根算起」,消費端沒跟著改基準,同一族問題沒收乾淨。這輪該把消費端一起收掉,或把回傳路徑改成相對 `repo_root`。
- 單元測試只驗了函式回傳,沒驗到消費端,所以綠。

引句:「paths 是相對 repo_root 的,前面補 --show-prefix。回傳的路徑從 repo 根算起(同 git status --porcelain)。」
severity: major
blocking: 是

其他核對沒找到問題:
- `_trusted_lumos` 的相對路徑拒絕會讓 PATH 前面的相對項遮住後面的合法 lumos,最多退回預設來源位置,屬 fail-open,不算問題。
- 工作樹模式的影響分析:8MB 總量上限正確。超限的檔只用路徑當查詢,行為符合設計。結尾 CR 的檔名改走路徑查詢。刪除的無副檔名腳本會取 HEAD 的首行。
- 我另外留意到一件事,但它不在這份 patch 內:`check-graph-sync.py` 收到 `{"cwd":5}` 這種非字串 cwd 時,`Path(5)` 會 TypeError,rc1,不會擋收工。真實的 Claude Code 不會送這種值,所以我沒列為 finding。

總結:最嚴重是 major(子目錄專案下,repo 根相對路徑被接到 `project_root` 上,筆記改了仍誤擋收工、沒副檔名的腳本被漏掉),會擋 1 條。

我的臨時目錄已刪除。
