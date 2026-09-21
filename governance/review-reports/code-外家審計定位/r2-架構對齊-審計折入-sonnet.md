severity: major

## F1 新加的 HTML 註解剝除法,重踩了 `_visible_lines`/`_strip_inline_markup` 明文禁止且已證實有洞的老路,而且真的繞得過去

severity: major
blocking: yes

`scripts/test_lumos.py` 新增的 `_note_convention_synced_to_skill` 家族,為了擋「把正確內容藏進 HTML 註解騙過去」這招,自己寫了一支剝註解函式：

引句:「把 <!-- --> 整段拿掉——註解裡的內容讀的人看不到,不能拿來充數。」

它的實作是 `re.sub(r"<!--.*?-->", "", text, flags=_re.S)`——一個沒有處理「未閉合」情形的樸素正則。

問題是,這支檔本來就有「全檔唯一」的可見文字判定,而且明文寫著「HTML 註解偵測本身就是洞」，理由正是同一種未閉合/先關再開會把後面整段藏起來或露出來：

- `scripts/lumos:168`:`_strip_inline_markup` 的 docstring——「跟 `_visible_lines`(行層級)配成一對,★全檔唯一★,別在別處自寫第二份」。
- `scripts/lumos:171`:「★不碰 HTML 註解★:-b r3 兩席證明「偵測註解」本身就是洞(先關再開、註解正則不認反引號邊界),註解裡的 [SN] 一律走「認不得→擋」。」
- `scripts/lumos:3085`:`_visible_lines` 的 `_scan` 內也重申「★不偵測 HTML 註解★(-b r3 單reviewer 兩條 blocker:`-->  <!--` 先關再開會把後面整份藏掉)」。

也就是說,這是「架構席」自己這一輪之前就審過、判過兩次 blocker 的老坑,現在新測試又在別的檔案裡重刻了一份同類機制——而且這次連 `_visible_lines` 對「未閉合圍欄」已經做的保守處理(讀不完整份就退回更嚴格判定,寧可少看不可多看)都沒有帶過來。`test_lumos.py` 本身也有「原地載入 `scripts/lumos` 呼叫內部函式」的既有慣例(`scripts/test_lumos.py:231`、`scripts/test_lumos.py:586` 等多處用 `SourceFileLoader` 把 `scripts/lumos`當模組載進來直接呼叫其函式),新測試完全可以照這個慣例去呼叫既有的可見性判定,卻選擇另開一支獨立正則。

**實際動手繞的重現**(唯讀,在 `/tmp/seat-架構對齊` worktree 裡跑,沒有改動 repo 任何檔案):

```python
import re
from pathlib import Path
root = Path(".")
block = ...(從 scripts/templates/graph-discipline.md 抽出〈寫筆記時〉整節,做法同 t_note_convention_synced_to_skill)
txt = (root/"skills/lumos-project-notes/SKILL.md").read_text(encoding="utf-8")
corrupted = txt.replace(block, block.replace("程式碼推不推得出來", "程式碼帥不帥"), 1)
attack_txt = corrupted + "\n\n<!-- 內部草稿備份,未收尾\n" + block + "\n"
visible = re.sub(r"<!--.*?-->", "", attack_txt, flags=re.S)
print(block in visible)   # → True
```

輸出:`block in visible` → `True`。也就是:把 SKILL.md 裡人真的會看到的那段規則改壞(範例改成「程式碼帥不帥」),只要在檔案任何地方(哪怕檔尾)貼一段**故意不寫收尾 `-->`** 的正確副本,新守衛就會判定通過——因為整份 SKILL.md 本來就一個 `-->` 都沒有(`grep -c -- '-->' skills/lumos-project-notes/SKILL.md` = 0),正則找不到收尾就完全不剝,於是「未閉合註解裡的正確副本」原封不動留在 `visible` 裡,騙過 `block in visible`。這正是 2026-08-03 圍欄治理史上第一個坑「①圍欄成對(未閉合就看不見)」的鏡像版本,只是這次是「未閉合反而看得見」——同一類錯誤重新長在一個沒有被舊護欄覆蓋到的新地方。

這不是風格問題:這支測試存在的唯一理由就是擋「藏起真內容騙過機械檢查」,而它自己就能被同一招數騙過,等於這道審計折入的第 5 條(漂移守衛可繞)在同一批修復裡又開了一個新洞。

## F2 `RULE:` 生命週期欄位另開一套「多欄位一行合併正則 + dict」解析法,跟本檔既有的「一欄位一正則」慣例是兩套做法

severity: major
blocking: yes

本檔既有的行內欄位剝取,一律是「一個欄位一顆獨立正則」,各自 `.findall()`/`.finditer()`/`in` 判斷:

- `scripts/lumos:3613` `TEST_REF_RE = re.compile(r"\[test:\s*([^\]]+)\]")`
- `scripts/lumos:3617` `AUDIT_REF_RE = re.compile(r"\[audit:\s*([^\]]+)\]")`
- `scripts/lumos:4080` `ROLLBACK_REF_RE`、`scripts/lumos:4081` `GUARD_REF_RE`
- `scripts/lumos:4086` `SRC_REF_RE`、`scripts/lumos:4087` `GIT_REF_RE`

而且「同一行有多個不同欄位」這個情境本檔已經有真實案例——regen 節點同一個 KEY 行可以同時有 `[src:]` 跟 `[git:]`,既有寫法是兩顆正則各自在同一行上 `finditer` 一次(`scripts/lumos:4353` `for m in SRC_REF_RE.finditer(line):`、`scripts/lumos:4362` `for m in GIT_REF_RE.finditer(line):`),不是合併成一顆正則。

這批新加的 `RULE:` 生命週期欄位解法完全不同——單顆正則把六個欄位名用 `|` 合併,`finditer` 出來直接塞進一個 dict:

引句:「把 RULE: 行裡的 [key:value] 抓成 dict(重複取最後一個)。」

同一段程式碼開頭還自稱是延用既有寫法:

引句:「欄位沿用本 repo 既有的 [test:]/[audit:] 行內寫法,不新發明語法:」

這句話只在「方括號 key:value 語法」這個表面層次成立,但「剝取邏輯」——也就是派工詞特別點名要查的那一半——並不是同一套:既有慣例是「N 顆獨立正則各自找」,新寫法是「1 顆合併正則 + dict 聚合」,而且這個新寫法帶出既有慣例從沒出現過、也完全沒被測到的新行為——同一行寫兩個 `[since:]` 會靜默只留最後一個,不會有任何警告(拿真實模組驗證:`parse_rule_fields("[since:2020-01-01][since:2021-01-01][retire:x]")` → `{'since': '2021-01-01', 'retire': 'x'}`,`rule_lifecycle_warnings` 對這個輸入回傳 `[]`,零警告)。這批新加的 `t_rule_lifecycle_fields`(五個案例)完全沒有涵蓋「同欄位重複」這條路徑,也就是這個新解析器獨有的行為連自己的翻紅釘都沒釘到。

## F3 `RULE:` 拿到跟 `decisions:`/★INVARIANT★ 同等「可挑戰程式碼」的裁決權,但配套的機械把關明顯更弱,兩邊不對稱

severity: minor
blocking: no

紀律範本把 `RULE:` 升格成跟 `decisions:` 欄位、★INVARIANT★、Issues、Verification 同一級的「有結構、有出處才能挑戰程式碼」名單(`AGENTS.md`/`CLAUDE.md` diff:「以及**寫齊出處、有效期與退場條件的 `RULE:` 行**。程式違反它們才算程式的問題」)。但既有的 ★INVARIANT★ 對應的機械把關是 err 級、會擋(`scripts/lumos` 既有邏輯:裸合約 lint 直接 `errs.append`,未審計的合約 `推送會擋`);`RULE:` 這邊新加的檢查全部只進 `warns`,不進 `errs`,`cmd_lint` 裡是 `warns.extend(context_marker_warnings(summ))` 而不是 `errs.extend`,pre-push 也沒有新增對應的擋法。程式碼自己也承認這個設計:

引句:「只唸警告不擋:規則是寫給人判斷的,機械只能看形狀,判錯就擋會逼人繞過去。」

這個選擇有寫理由,不是漏做,所以只列 minor:被授予同等裁決權的四個來源裡,三個(decisions/★INVARIANT★/Issues 的裸合約情形)有機械擋,`RULE:` 沒有——同一份紀律範本裡「誰能推翻程式碼」這件事,配套的強制力不對稱。值得在下一輪跟出處/退場條件的裁決權設計一起處理,但不構成這批本身要擋的理由。

## 驗過的範圍

- 完整讀過凍結 patch(966 行,sha256 對過)。
- 在 `/tmp/seat-架構對齊`(`git worktree add --detach` 出的唯讀副本,對應 `9896d81a..HEAD` 已提交的 `8c9dc3d3`)裡,用 `SourceFileLoader` 把 `scripts/lumos` 當模組載進來,實際呼叫 `parse_rule_fields`/`rule_lifecycle_warnings` 跑過重複欄位、空值、日期格式錯、`[retire:]` 內容含 `]`、欄位夾在中文裡、極長字串、欄位前後無空白貼著別的字等邊界輸入(未在正式發現裡逐條列出的,因為判下來不影響裁決權授予,不算架構分歧)。
- 針對 F1 的繞法,用真實的 `skills/lumos-project-notes/SKILL.md` 內容實測,不是憑空舉例;沒有寫回任何 repo 檔案。
- 沒有讀 `governance/review-reports/` 下任何 `rN-*.md` 席報告,沒有派子代理。
