severity: minor

# 第 3 輪 判定路徑席(測試名判定說有、其實沒有)

實驗都在 mkdtemp 臨時 repo 跑(腳本 scratchpad/exp3.py),指令是 `python3.14 /Users/enzo/harness/lumos-rtb3/scripts/lumos home check --staged --repo <臨時 repo>`;沒改任何 repo 檔。
設定:python 測試棧,src/b.py 的家 B 已綁 [test:test_old],同一提交改 src/a.py(家 A 沒動)、B 只新加 [test:test_new]。rc0 = 當成只換綁定而豁免;rc1 = 擋。

## 對四題的直接答案

1. 提交前只查工作目錄索引,工作目錄有、提交索引沒有時會判 yes 放行(下方 F1),推送前那道補得回來(實測 P1 轉 rc1)。
2. 口徑:類別.方法只比最後一段、類別不存在也判 yes(F2);Kotlin 反引號名帶連字號或括號會誤擋(F3);沒設 test_profile 的專案預設 csharp-xunit,python 測試掃不到,tag-only 一律不豁免(誤擋,同 F3 的保守方向)。
3. 時間預算用完回 ("skip", "時間用完"),平台跳過回 ("skip", "平台跳過"),都不是 "yes"。`_nodehome_tag_only_change` 只認 `j(nm)[0] != "yes"` 就 return False,所以 skip、undecidable、no 都是不豁免,方向正確。`_ns_tr_test_viol` 對 skip 不報違規是 note-shape 自己的 fail-open,與每支檔有家無關。
4. 推送的三種情況只看:簽出提交不是終點、config 有未提交改動、已追蹤測試檔有 M/D。工作目錄的未追蹤測試檔不在這三種裡,索引會掃到它;但第②道 `_test_in_tree` 是對終點的樹做 git grep,未追蹤的檔不在樹裡,所以仍判 notfound、不會被它放行。實測 P1 證明。

## 實測表

| 情境 | 結果 |
|---|---|
| 0 完全沒有 test_new | rc1(正確擋) |
| 1 tests/test_new.py 未 git add | rc0 |
| 2 已 git add 的 tests/test_new.py | rc0 |
| 3 test_new 在 .gitignore 的目錄 | rc0 |
| 4 `NoSuchClass.test_new`(類別不存在) | rc0 |
| 5 測試檔放 src/ 底下、未追蹤 | rc0 |
| 6 沒有 .lumos/config.json | rc1 |
| P1 推送時(`--diff HEAD~1..HEAD`),測試檔未追蹤、提交只含標記 | rc1(補回來) |
| P4 推送時 `NoSuchClass.test_new`、測試已追蹤 | rc0 |

## findings

severity: minor
blocking: 否(提交前只是較鬆的一道,推送前與 CI 以樹為準會補回來;實測 P1 rc1)
F1 提交前判定讀工作目錄而非提交索引:測試檔寫了沒 git add(或放在 gitignore 目錄)時 tag-only 編輯判 yes 而豁免。
引句:「_NsTrJudge(提交時 tip=None 只查測試索引;推送時再到終點版本找)」
file: `scripts/lumos:29871`
重現:情境 1 與 3 的 `home check --staged` 回 rc0;同樣的提交 commit 後跑 `home check --diff HEAD~1..HEAD` 回 rc1。影響僅限提交時多放行一次,且提交前掛鉤不是唯一關卡。

severity: minor
blocking: 否(判準:放行的是「名稱指到真有的方法名」,沒有造成錯誤綁定被當成真;推送時同樣判 yes,屬 `_classify_test_refs` 既有的扁平方法名口徑)
F2 「類別.方法」只比最後一段,類別寫錯或不存在也判 yes,提交前與推送前兩道都一樣。
引句:「method if method in mset else method.rsplit(".", 1)[-1]」
file: `scripts/lumos:43481`
重現:情境 4(提交前)與 P4(推送前,測試已追蹤)皆 rc0,`[test:NoSuchClass.test_new]` 被當成指得到真測試。

severity: minor
blocking: 否(判準:誤擋方向,走拆提交或把說明寫進家的既有出口,不會放過壞綁定)
F3 Kotlin 反引號名帶連字號、括號,或沒設 test_profile 的專案(預設 csharp-xunit)時誤擋 tag-only 編輯。
引句:「_nodehome_tag_judge(root, None if staged else tip_where)」
file: `scripts/lumos:14564`(`_KILL_METHOD_OK_RE` 只放行 `[\w .]+`)
重現:kotlin-junit 專案、測試 `` `returns-zero when empty` `` 真的存在,只換綁定的提交 rc1;同形但 `returns zero when empty` rc0;情境 6 rc1。

## 沒問題的部分

時間預算與平台跳過回 skip,三個「不是 yes」的回傳值(skip、undecidable、no)在 `_nodehome_tag_only_change` 都當不豁免;`_nodehome_tag_judge` 例外時回 None,也當不豁免。
引句:「j = judge() if judge else None」

總結:全份最高等級 minor
