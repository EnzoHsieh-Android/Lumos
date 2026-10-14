severity: major

資安席第三輪報告。這輪做了縮排鏈本身的碰撞搜尋,和三個繞過實驗。

縮排鏈本身沒找到可利用的洞(見最後一節)。找到三個繞過:逾時不擋、起點可被偽造、替身提交。這三個都不靠搬同一段改動,而是讓「指紋沒算到真正的改動」。

## finding 1:撐到逾時,整篇不擋

severity: major
blocking: 是 — 沒有任何對照紀錄、也沒設跳過環境變數,攻擊者靠堆檔案就能讓 `--gate` 回 0。
引句:「因逾時沒算出新版指紋的篇不擋」

攻擊步驟:
1. 從主線分出分支,在 `scripts/lumos` 的 `_note_reread_diff_fits` 改成 `return True`。
2. 加 3000 個垃圾小檔 `junk/f0.txt` 到 `junk/f2999.txt`。
3. 在 `Systems/lumos-cli-read.md` 的 about_code 把這 3000 個檔全部列上。
4. 執行 `note-audit reread-check --repo . --diff origin/main..HEAD --gate`。

結果:
- 約 27.6 秒後 rc=0,沒有任何紀錄。
- 輸出標明「這篇因為逾時沒算新版指紋,這次不擋」,最後印「這只是提醒、不擋,忽略照推也可以」。
- 同一支程式、同一篇筆記只做一行改動、沒有垃圾檔時,輸出是「擋下:回頭重讀」。

計劃說這條退路不會被拿來繞,理由是「要改到上千支檔」。但攻擊者能手改檔案,about_code 又是他自己寫的,3000 個垃圾檔很容易造。帳上只多一個 `late` 欄,沒有人會看。

建議:逾時沒算出新版指紋的篇改成照擋(要退路就給明確的跳過指令),或限制 about_code 的列檔數。

佐證:`scripts/lumos:37675`(`_note_reread_blocking`)。

## finding 2:指紋的起點取自本機遠端追蹤 ref,可被偽造

severity: major
blocking: 是 — 惡意程式藏進「起點」,diff 裡完全看不到。
引句:「分岔點:_lens_default_base(頂端是解析好的提交編號、只看遠端主線)」

攻擊步驟(`/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp` 的 `git clone --local`,用該 repo 的 `scripts/lumos`):
1. 誠實版:從 f77befc4 分出,在 `_note_reread_fp_expired` 加一行 `_ = 0`,並在 `lumos-cli-read.md` 加一行。reread-check 印出對照指紋 `5548b7a054108153`。
2. 攻擊版:先提交惡意改動 `_note_reread_diff_fits` 改成 `return True`,再執行 `git update-ref refs/remotes/origin/main HEAD`,把本機的遠端主線指到這個提交。
3. 在攻擊版上再提交跟誠實版一模一樣的 `_ = 0` 與筆記改動,然後執行 reread-check。

結果:
- 對照指紋同為 `5548b7a054108153`,所以誠實版的對照紀錄會被當成已對照。
- 用 `git diff f77befc4 HEAD` 看,真實改動有 3 行程式改動,其中含惡意那行。

原因:分岔點只讀本機 refs,沒有跟真正的遠端核對。

建議:分岔點要和 pre-push 從 stdin 拿到的遠端 sha 核對,至少要確認它是遠端主線的祖先。

佐證:`scripts/lumos:36423`(`_note_reread_fp_base` 的 `_lens_default_base` 呼叫);`scripts/lumos:48198`(`_lens_default_base`)。

## finding 3:git replace 替身提交,讓指紋讀到誠實版

severity: major
blocking: 是 — 完全不用偽造遠端 ref,推出去的是帶惡意的真提交。
引句:「分岔點:_lens_default_base(頂端是解析好的提交編號、只看遠端主線)」

攻擊步驟:
1. 沿用 finding 2 的誠實版提交 H 與攻擊版提交 C2。攻擊版的主線 ref 維持真實的 f77befc4。
2. 執行 `git replace C2 H`(C2 是帶惡意的真提交,H 是只有誠實改動的提交)。
3. 執行 `reread-check --diff origin/main..attack2 --gate`。

結果:
- 對照指紋是 `5548b7a054108153`,跟誠實版相同。
- `git --no-replace-objects diff --stat f77befc4 C2` 顯示 `scripts/lumos` 有 3 處增刪(含惡意那行)。
- `git push` 只傳真物件,替身不會傳出去。
- 全專案 grep 不到 `no-replace-objects` 或 `GIT_NO_REPLACE_OBJECTS`。

建議:`_note_reread_git` 與 `_lens_git_dl` 的 git 呼叫都加 `--no-replace-objects`(或設環境變數 `GIT_NO_REPLACE_OBJECTS=1`)。

佐證:`scripts/lumos:36442`(`_note_reread_git`)。

## 沒有構成洞的項目

- **搬到外層那行原文相同的兩個函式**:用 `_note_reread_hunk_tags` 對 `scripts/lumos` 與 `scripts/test_lumos.py` 找「7 行視窗相同且鏈相同」的重複。
  - `scripts/lumos` 在視窗超過 40 字元的條件下 0 組。
  - `scripts/test_lumos.py` 有 14 組,全是同一個函式內的重複區塊(例如 18642 與 18673 都在 `t_prepush_range_scan`)。
  - 沒有跨函式的碰撞,因為 def 行會進鏈。
- **頂格行截斷鏈**:本輪沒做實驗,所以沒有結論。靠頂格行截斷鏈要兩邊函式本來就有同一行頂格內容,加上完全相同的前後三行,自然碰撞數是 0。這條靠的是「原本就存在」,攻擊者在同一份 diff 裡造不出來。
- **查大小失敗退回舊版**:舊版指紋含 about_code 每支檔在頂端的 blob 編號,程式一改編號就變,配舊版紀錄對不上,所以安全。

最高等級 major,blocking 3 條。
