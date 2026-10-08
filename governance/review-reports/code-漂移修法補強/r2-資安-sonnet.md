severity: minor

## F1 刪除守衛的「原封不動」只看工作目錄檔加安裝清單,暫存區內容與清單本身都不查
severity: minor
blocking: 否
引句:「暫存區跟工作目錄不一樣時只會在「暫存的改過、工作目錄的剛好跟清單一致」這種少見情形少掃。」
佐證行:file: `scripts/lumos:17799`(`_vendored_state(root)` 以 ref=None 讀工作目錄檔與 `.lumos/vendored.json`,兩者都不是暫存區內容)
1. 重現(臨時消費專案 + `_vendored_state` / `_delguard_parse_diff`,腳本 fix-r2/sec1.py):裝好 `scripts/lumos`(含清單),把裡面的函式 `secret_gate_check` 刪掉,再用 `_vendored_manifest_write` 重算清單,兩者一起 `git add`。輸出 `skip: frozenset({'scripts/lumos'})`,`parse` 的 tokens 只剩清單檔裡的一串 sha256,`parse no skip` 才有 `secret_gate_check`。也就是「改過的檔+同一提交裡改過的清單」被當成原封不動。清單沒有被檢查是不是也在這次暫存的 diff 裡。
2. 第二條路(同腳本):只把刪掉函式的版本暫存,再把工作目錄檔還原成原版、清單不動。輸出 `mismatch skip: frozenset({'scripts/lumos'}) []`——tokens 全空。上面那句註解承認的就是這條。
3. 影響:刪除守衛是提交時的提醒,提交者本人能用 LUMOS_SKIP 類旗標繞過,所以不算防惡意者;但被誤導的情形是 AI 代理或 `git add -p` 後還原檔案的人,守衛靜默少掃而不會顯示任何一行。比修正前(整份清單只比檔名)已收緊,不是回歸。
4. 便宜的收法:暫存的 diff 裡出現 `.lumos/vendored.json` 就一支都不跳;或改讀暫存區的 blob 算指紋。
5. 清單誰寫:唯一寫入點是 `_vendored_manifest_write`(install/update 結尾,在 copy2 自癒之後),工具檔在來源缺這支時不會被覆寫卻照樣被記進清單,只有這個窄情形會把本地改過的檔記成原版;一般路徑指紋是新複製的原版,判為可信。

## F2 佔位字變體正則把「<git-sha>」這類合法文字擋掉,跟自己註解宣稱的不一致
severity: minor
blocking: 否
引句:「只剩閉括號那側,sha 前面不能接英數(git-sha> 之類不算)」
佐證行:file: `scripts/lumos:15147`(`_set_cond_slot_variant_re` 的 `before` 只排除英數與底線,連字號可以接)
1. 重現(fix-r2/sec2.py):`_SET_COND_SLOT_VARIANTS` 對 `a-sha>` 回傳命中 `<sha>`;`<git-sha>` 走第二個分支同樣命中。註解說「git-sha> 不算」,實際被擋。
2. 壞在哪:使用者要在 valid_under 寫「提交 <git-sha> 之後」這種合法描述,`lumos set` 回 rc2 並說是佔位字沒換乾淨,訊息還叫他「換成真的提交編號」,無法照做。要繞得改寫掉角括號。
3. 未定義行為屬內部不一致:註解與行為對不上。未見災難性回溯:對 `<`+20 萬空白、`<`×10 萬、`< `×10 萬、`<sha`+20 萬空白+`-`、`sha`×10 萬等輸入,全部搜尋耗時 < 0.05 秒(兩個分支都沒有巢狀量詞,`\s*` 各自單層)。
4. 反向(不阻擋才是問題的那側):`<ｓｈａ>`(全形字母)、`<s ha>`、`<卷 證>` 不被擋。這個守衛只擋「忘了換」,不擋刻意繞過,不列洞。

## F3 證據頁印原名後,方向控制與零寬字元原樣進終端
severity: minor
blocking: 否
引句:「print("    " + _esc_clean(f"governance/review-reports/{_nodehome_show(d)}({src})", 300))」
佐證行:file: `scripts/lumos:9765`(`_esc_clean` 只換 C0、DEL、C1,不含 U+202A–202E、U+2066–2069、U+200B)
1. 重現(fix-r2/sec2.py):目錄名 `code-‮gnp.⁦x⁩/../evil​` 經 `_esc_clean(...)` 後 repr 仍完整含 `‮`、`⁦`、`​`,只有 ESC、換行等真控制字元被換成空格。
2. 場景:整批匯入的卷證目錄名(外部投稿的 PR 可帶)含 RLO,證據頁上「(同提交)」標籤與目錄名的視覺順序被重排,人挑目錄貼進 lumos set 時看到的與實際字串不同。原名不再 NFC 前後這一點沒差別(NFC 也不濾這些),所以是印原名之後仍未收的舊缺口,不是新增;危害限於顯示誤導,無法注入指令。
3. 換行 `\n`、ESC(`\x1b`)、C1 已實測被換掉,終端指令注入這條不成立。

## 其他攻擊面判定(無可利用洞,不列 finding)
- 「列完整清單」git 指令(`_drift_c4_more_cmd`):sha 來自 `_plan_first_commit` 的 `git log --format=%H` 並經 `split()`,只會是十六進位;路徑是寫死字面,不含任何目錄名。用 `sha="ab12"*10` 與 None 各印一次,輸出無使用者可控字串,shell 注入不成立(fix-r2/sec2.py)。
- 特製 diff 檔頭:`rename from` 的 src 只在 `in_head`(遇 `@@` 即關)時讀,被刪內容行是 `-rename from …` 開頭,不會被當檔頭;把專案自己的 `src/app.py` 改名成 `scripts/lumos` 並給 skip={scripts/lumos}:`-` 行照來源路徑,tokens 空是因為 100% 改名本來沒有 `-` 行,不是被跳過(sec3.py 印出的 rename 檔頭正確)。含 ` b/` 的檔名不能讓 `src` 等於工具路徑,因為 src 直接取自 `rename from` 整行。
- 舊有(不在本輪 diff 內,不列 finding,只供知悉):`_delguard_path_flags` 用 ` b/(.+)$` 取路徑,實體目錄 `x b/docs/` 底下的檔被刪時,c 被誤判成 `docs/…` 而落入排除,tokens 空(sec3.py,`diff --git a/x b/docs/lib.py b/x b/docs/lib.py` → `[]`);該函式在 base 提交就存在。若要處理,得改成用 `--` 前後行的完整路徑取代 regex。
- 佔位字正則 ReDoS:見 F2 第 3 點。

## 圖譜鏡頭
- 存量漂移守衛:c1/c3/c4 的改動只動訊息與證據頁列印,不寫檔、不放寬 `drift fix` 的寫入條件,不影響。
- bound-tests-gate / guard-kill / lumos-cli-read / lumos-cli-lifecycle / design-loop / 測試假綠形態:改動不碰綁定測試判定、guard kill rc、search 濾網、re-inject 或處置閘,不影響。
- 授權與歸屬:`_VENDORED_ALL` 內容沒改,只是刪除守衛不再直接拿它當跳過集合,LICENSE 不入清單的合約不受影響。

最高等級:minor
