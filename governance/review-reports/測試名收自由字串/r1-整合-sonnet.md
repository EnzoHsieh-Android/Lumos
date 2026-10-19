severity: major

整合/知識同步鏡頭。我開了 `scripts/lumos`、`scripts/test_lumos.py`、skills/、Systems 筆記逐項核對。前掃已修的不重報。

## 逐節結論
- 前言、舊決策與為何翻案:已讀,無 finding。交叉引用的節點都存在。全庫 grep 確認本 repo 沒有 `[test:` 值用全形逗號或冒號。
- 做法 1、2、4、5:已讀。除下面 F5、F6 之外無 finding。
- 做法 3:已讀,無 finding。
- 做法 6、7、〈驗收條款〉、〈不做〉:見 F1 到 F4、F7。

## F1 落點把 `lumos-guard` 寫成「guard 那組」的家,實際是別的東西
- spec 段落:做法 7 最後一條,以及 frontmatter 的 `lands_in`。
- 引句:「guard 那組落在 [[Systems/lumos-guard]] 與 [[Systems/guard-kill]]」
- 問題:
  - `Systems/lumos-guard` 管的是審查席隔離外掛。它的檔是 `mods/claude/lumos-guard/hooks/register.ts` 等 TypeScript,`responsibility` 也只寫審查席白名單。
  - 這份計劃改的 `guard bind`、`guard settle`、`guard scaffold`、`guard trace`、`cmd_archive`,跟那個外掛無關。
  - 計劃真正要改寫的 Systems 說明沒被指名。`Systems/guard-kill.md:109,112` 寫的「test 名白名單」「test 名不合法」會變舊。`Systems/lumos-cli-write.md:112` 的 archive 那列也會牽連。
- 具體例:三個月後的人照 spec 把說明寫進 `lumos-guard`。「每支檔有家」要求寫進改到那支檔的家,所以這是錯的家,圖譜裡 `guard bind` 的規則仍寫「method 維持識別字」。
- 佐證:file: `docs/lumos-toolchain-knowledge/Systems/lumos-guard.md:6-17`(about_code 全是 mods/claude/lumos-guard 的 .ts)
severity: major
- blocking: 是。照 spec 字面做,說明寫進錯的節點,對的節點留下舊規則(實作者會做錯決定)。

## F2 守衛指令印出「可貼上的命令」的路徑漏列,放寬白名單後會印出不可貼或錯誤的指令
- spec 段落:做法 6 表格 `guard kill` 那列與 `guard settle`、`guard bind` 那兩列。
- 引句:「跑的時候照做法 4 跳脫」
- 問題:同一個根因(名稱放寬後,有些地方把名稱原樣印進給人貼的命令或判斷語),spec 只列了判定端,印出端漏了:
  - `_kill_binding_msg` 裡有兩處 `IDENT_RE`。
    - file: `scripts/lumos:18525` 的 `show()`。
    - file: `scripts/lumos:18536` 判「這種名字 guard bind 綁不了」。
    - 這兩處都不在表格內。
  - `_kill_binding_msg` 的 else 分支把 `{meth}` 原樣接進 `lumos guard bind {na} {inv} {meth}`,沒有經 `_kill_cmd_arg`。
    - file: `scripts/lumos:18541-18543`。
    - 那一格現在靠 `IDENT_RE` 保證名稱安全。
    - 實作者若照其他列的慣性把這處換成 `_test_name_ok`,就會把含空白、`$`、單引號、分號的句子名直接印進建議貼上的指令。
  - 如果不換,`18536` 那句「guard bind 綁不了」就說錯了,因為本計劃讓 `guard bind` 收句子名。
  - `skills/lumos-project-notes/commands/06-代碼審與推送.md:29` 有同一句「方法名不是識別字…的 bind 綁不了」。
  - `_guard_settle_record` 的補救提示印 `lumos guard settle {rel[:-3]} --test {method}`,沒有引號。
    - file: `scripts/lumos:17810`。
    - 放寬後,句子名貼上去會被 shell 切成多個引數。
- 具體例:合約綁 `[test:web:下單後 按鈕會停用]`,kill-add 配方的測試不在清單上。
  - 照 spec 只換 `_KILL_METHOD_OK_RE`:提醒仍說「guard bind 綁不了,請 kill-rm」,但 `guard bind` 其實綁得了。
  - 若順手換 `IDENT_RE`:印出 `lumos guard bind … 下單後 按鈕會停用`,貼上會報錯。名字含 `$(…)` 時更危險。
- 佐證:file: `scripts/lumos:18506-18514`(`_kill_cmd_arg` 的設計目的就是「貼進指令的字一律走這一支」)
severity: major
- blocking: 是。守衛面「拒注入白名單」放寬,印出端漏改會得到錯誤提示或不安全的指令。

## F3 文件與手冊的同步清單不完整,S25 的檢查範圍太窄
- spec 段落:做法 7;驗收條款 S25。
- 引句:「當讀 profile 的提示文字與 Systems/test-profile-multiplatform 時」
- 問題:改了規則之後,下列地方還留著舊說法,spec 沒列,S25 也不會抓到:
  - `skills/lumos-project-notes/reference.md:620`:「playwright … 含空白 title 不可綁」,以及 node-jest 那段只講 `'id'`。
  - `skills/lumos-project-notes/reference.md:625`:「`--method` 維持識別字…」。
  - 同檔 `reference.md:620`:逃生口 `method_regex` 的說明只講單平台,做法 5 讓多平台也能用,要補一句。
  - `Systems/test-profile-multiplatform.md:27`:maestro 與 playwright 寫在同一行 KEY 裡,兩者都標「NO MATCH」。
    - 只有 playwright 要改,maestro 照舊。
    - spec 說「那兩行」,實際要拆開改半行。
  - `Systems/test-profile-multiplatform.md:29`:「guard bind/scaffold --platform 旗標——method 維持識別字」。
    - 這句對 bind 會變錯。
    - spec 只提 playwright 與 dart 兩行,這是第三行。
  - `scripts/lumos` 裡的原始碼註解也有舊句:`5636`、`5642`、`5645`、`5657`、`5803`。
    - spec 只改 `attr_hint`。
    - 註解讀到的人是下一個改這段碼的 AI。
  - `Projects/多平台合約測試綁定_計劃.md:104,107`:「與 D4 Playwright 對稱」「name: 必須是識別字…配合 guard scaffold --method 限制」。
    - 做法 7 只在 D4 開頭加一行。
    - 對稱關係已不成立,但 Maestro 那段應保留並說明為何不跟著改。
  - `Projects/Web示範前端缺口_調研.md` 的 W1 列仍寫「仍存在(部分緩解)」,沒有指向本計劃。
- 具體例:AI 讀 `reference.md:620`,看到「含空白 title 不可綁」,於是不用句子名綁測試,改寫成識別字。這正是本計劃要消除的情況。
severity: major
- blocking: 是。S25 只 grep 兩處,通過後出貨的手冊仍與新行為矛盾(漏掉合約)。

## F4 計劃沒有列出必須翻轉的既有測試
- spec 段落:〈驗收條款〉整節。
- 問題:下列既有測試會因新行為變紅或失去意義,spec 沒指名要改:
  - `scripts/test_lumos.py:10547`:斷言輸出含「懸空 2 只提醒不擋」。
  - `scripts/test_lumos.py:8084-8112`(`t_playwright_profile_discover`):文字與註解都寫「多字 title NO MATCH」。
    - 斷言現在碰巧不紅。
    - 但新行為下 'should show menu' 會被收進集合,註解與意圖已反。
  - `scripts/test_lumos.py:92057`:用全形逗號的 `[test:test_alive，test_dead3]` 期待被切開。
    - 做法 1 改成全形逗號不切後,這條行為變了。
- 具體例:implementer 改完 `_clause_check` 後跑 `-k` 子集,10547 紅,他得自己猜是更新斷言還是退回實作。
- 附帶:memory 規則「改 test_lumos.py 要先簽名」也該寫進實作步驟。
severity: minor
- blocking: 否。紅了立刻看得到,不會悄悄做出壞系統。

## F5 「整串相等」的宣稱與 `類別.方法` 後綴比對衝突
- spec 段落:做法 1 最後一條。
- 引句:「名字比對一律整串相等(去頭尾空白後),不做大小寫或空白正規化。」
- 問題:三處仍保留「含 `.` 就拿最後一段去比」的規則:
  - `_classify_test_refs` 的 `method.rsplit(".", 1)[-1] in mset`,file: `scripts/lumos:54172`。
  - `_NsTrJudge._judge`,file: `scripts/lumos:36406`。
  - `_test_in_tree` 的呼叫端,取的是同一段 `gname`。
- 具體例:`[test:購物車.下單後 按鈕會停用]`,且真有 `下單後 按鈕會停用`。判成 real,而不是依 spec 的整串相等判懸空。
- 實際碰到的機率低(中文句子的句點多半是全形,英文句點後有空格而不吻合),所以標 minor。
- 建議歸類:這屬於「前綴/後綴部分比對」同類,應在做法 1 明寫「句子名走 `.` 後綴規則的範圍」,或在 S5 旁補一條後綴反例。
severity: minor
- blocking: 否。極端輸入才會出現,不影響主流程。

## F6 〈不做〉裡「只換測試綁定」豁免的敘述不精確
- spec 段落:〈不做〉第四條;做法 6 表格 `_nodehome_test_tag_value_ok` 那列。
- 問題:
  - 「不放寬的代價只是換一個中文名」不準。
  - `_NODEHOME_TAG_NAME_RE` 是單一識別字(file: `scripts/lumos:32860`),所以英文句子名(`shows error (500)`)也不在豁免內。
  - `_nodehome_strip_test_tags` 會間接呼叫 `_test_names_of`,做法 1 會動到它。
  - 該呼叫只在值通過 ASCII 白名單後才進來,所以全形逗號改動不影響結果,但表格只寫「不改」,沒講這條間接路徑。
- 影響:三個月後的人會以為英文句子名可以豁免,查證時看到相反行為。
severity: minor
- blocking: 否。方向安全(多擋),只是理由敘述不完整。

## F7 相容宣稱只掃本 repo
- spec 段落:〈實務隱患〉「相容」;做法 1 全形逗號那條。
- 引句:「舊筆記一字不改照讀;全形逗號、全形冒號不再切的那條,2026-10-15 全庫 0 處受影響。」
- 問題:我重跑了 grep,本 repo 的 docs、skills、templates 確實 0 處。但「全庫」沒涵蓋消費專案(order-web、taroko_app 等)的筆記。這個行為改動只對全形逗號與全形冒號生效,對消費專案舊筆記無法保證。
- 這不是要求補資料,而是需要在 spec 註明範圍是 lumos-toolchain 本身,否則「相容」的宣稱會被當成已涵蓋消費專案。
severity: minor
- blocking: 否。回退段落已說明風險是回到懸空,不會壞檔。

最嚴重 severity:major;blocking 共 3 條(F1、F2、F3)。
