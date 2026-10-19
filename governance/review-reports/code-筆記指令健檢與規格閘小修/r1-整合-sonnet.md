severity: major

我在工作樹 `/Users/enzo/orca/workspaces/lumos-toolchain/web-notes`(HEAD 55da596f)逐項對照文件和實際行為,另在暫存專案裡跑了 `summary-add`、`refcheck`、`home check`、`set --help`。

核對過沒問題的:
- 頂層指令數:`lumos --help` 實際是 92,`ARCHITECTURE.md` 三處、`reference.md` 兩處都寫 92。
- 紀律範本、版本與注入:範本鐵則 2 列出了 `summary-add`,`LUMOS_VERSION` 是 v1.4。`CLAUDE.md` 與 `AGENTS.md` 的注入區塊版本號是 v1.4,內容和範本逐字一致(我把 `{{KG}}` 換成圖譜路徑後比對,兩邊都相同)。
- 指令行為:`summary-add` 的旗標、沒前綴被擋、重複不動檔、`--dry-run` 都和手冊一致。`refcheck` 的 `planned`/`ignored` 狀態、`home check` 不帶範圍照 `--staged` 也和文件一致。
- 筆記本身:`[test:]` 綁的測試在 `scripts/test_lumos.py` 都找得到。所有被改的筆記 `lumos lint` 都是 0 問題。
- 家與決策:`home check --diff` 通過,每支改到的檔都有家。決策 d1、d2、d3 都記在計劃裡,規格閘的家節點也寫了 WHY。

1. 這個提交讓 `doctor --ci` 回 rc=1,推送前的圖譜健檢會擋下。
   - 計劃第 S10 條寫 `值寫成 [[Systems/x]] 或 Systems/x.md`,這個 `[[Systems/x]]` 沒包反引號,被當成連到不存在的筆記。
   - 這是此次新增的:在 0beb6d7d 的 `docs` 底下搜不到這個字串。
   - README 也寫「筆記之間的連結斷掉一定擋」。
   - 重現:在 web-notes 跑 `python3.14 scripts/lumos doctor --ci`,rc=1、輸出「發現 1 個 issue」,唯一的警告是「連結連到不存在的筆記:[[Systems/x]]」。
   - 修法是把 `[[Systems/x]]` 包進反引號,或改成不會被當連結的寫法。
severity: major
   - blocking: 是
   - 引句:「值寫成 [[Systems/x]] 或 Systems/x.md 時,append 應改成純字串 Systems/x 寫入並印一句改了什麼」

2. 動到 `Systems/test-profile-multiplatform.md` 讓推送前的 `note-shape` 擋下。
   - 該筆記第 23、24、25、26、29 行是舊的示意用 `[test:plat:name]`、`[test:X]`、`[test:foo:X]`,指不到真測試。
   - 這個 repo 的 `.lumos/config.json` 設了 `note_shape.test_refs: "block"`,規則是「碰到的筆記整篇要乾淨,舊行也算」。
   - 筆記最後一次被動是 2026-09-12,早於 test_refs 開擋(10-03),所以這是第一次踩到。
   - 重現:`python3.14 scripts/lumos note-shape --diff 0beb6d7d..55da596f`,rc=1,列出上述五行「指不到真測試」。
   - 修法是把那五行的示意寫法包起來、改成 `[test-gone:]` 或不用 `[test:` 開頭,或改把 W10 那條 WHY 寫進別的家。
severity: major
   - blocking: 是
   - 引句:「平台 root 不存在的警告同一次執行只印一次(模組層集合記 (平台, root)),load_platforms 每個呼叫端共用」

3. `Systems/lumos-cli-write.md` 的數字沒跟著新增的兩列更新。
   - 原則表現在有 10 列,正文還寫「7 個子指令」和「## 八個原語」。
   - 下一段「走 `atomic_write_verify`」的列舉也沒補 `summary-add`、`summary-line`。
   - `Systems/lumos-cli-read.md` 第 152 行還寫「寫入走另 7 個原語」。
severity: minor
   - blocking: 否
   - 引句:「`scripts/lumos` 的**專案層圖譜寫入原語**(7 個子指令)」

4. `docs/command-reference.md` 和 `docs/指令參考.md` 第 53 行的「動工:邊做邊寫回」指令清單只有 `summary-line`,沒有 `summary-add`。計劃 §1.7 的同步清單沒列這兩份,所以漏了。
severity: minor
   - blocking: 否
   - 引句:「lumos summary-line <node> "<old fragment>" "<new fragment>"   # change one summary line without hand-editing the header fields」

5. 決策 d3 翻掉「推送前只看 doing」,但舊說法有兩處沒標。
   - `Projects/雙向門放行_計劃.md` 只在第 53 行補了指到本計劃的箭頭。第 212 行的〈推送前〉段仍寫「計劃仍 `doing`」,沒標註。
   - `Systems/規格閘.md` 第 34 行 KEY 寫「…的 doing 計劃,取最後一筆風險低留痕」,新增的 d3 WHY 在第 44 行,舊 KEY 沒標「已部分翻」。
   - 三個月後接手的人從第 212 行或第 34 行讀起,不會知道有例外。
severity: minor
   - blocking: 否
   - 引句:「推送前**:讀審查帳裡 `kind: spec-gate`、計劃仍 `doing`、**且本次推送範圍碰到該計劃檔」(`雙向門放行_計劃.md` 第 212 行原文,不在這份 diff 裡,是我另外查到的)

6. 計劃第 7 節寫 `refcheck` 文字輸出是「○ 將新增」,實際輸出是「○ planned」。程式把狀態名直接印出,「將新增」只出現在統計行。這是計劃文字與程式不符,以程式為準。
severity: minor
   - blocking: 否
   - 引句:「refcheck:路徑不存在時列成 `planned`(文字輸出「○ 將新增」,`--json` 的 status 是 `planned`」

7. 以下三篇筆記內文有動,但 `updated:` 沒更新,`lumos updated-sync --stale --dry-run` 會列出:
   - `Projects/改摘要單行的指令_計劃`(停在 10-06)
   - `Projects/否定現況句配回頭條件_計劃`(停在 10-03)
   - `Projects/雙向門放行_計劃`(我沒對它單獨跑過這個檢查)
severity: minor
   - blocking: 否
   - 引句:「2026-10-15 使用者裁定推翻「不做插行」:新增摘要行改由 `lumos summary-add` 做」

另外:計劃檔 `筆記指令健檢與規格閘小修_計劃.md` 的開頭欄位沒有 `summary:`,`lint` 沒報錯。這點我沒把握算不算問題,不列為 finding。

最嚴重 severity: major,blocking 共 2 條(第 1、2 條)。暫存目錄 `/private/tmp/lumos-seat-work/code-筆記指令健檢與規格閘小修/整合-sonnet` 已刪除。
