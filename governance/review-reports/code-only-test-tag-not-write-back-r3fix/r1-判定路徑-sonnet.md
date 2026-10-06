severity: minor

# 第三輪修正驗收:判定路徑鏡頭(假設者立場:判定說有、其實沒有)

驗收範圍:`_NODEHOME_TAG_NAME_RE` 先擋、再交 `_NsTrJudge`。實驗都在臨時 repo(mktemp),用 `python3.14 scripts/lumos home check --staged|--diff A..B --repo <臨時 repo>` 實跑,腳本在 scratchpad/x/exp.py、exp2.py。

## 四問結論

1. 單一識別字:`_classify_test_refs` 用的是「整個名稱 in 測試方法集合」(`method in mset`),不是子字串或前綴。真測試只有 test_alive_and_well 時實跑:`test_alive`、`Test_alive_and_well`、`test_ALIVE_AND_WELL`、`t_alive_and_well` 全部 rc1(不豁免);`test_alive_and_well` 與帶尾端空白的同名 rc0。第一道找不到「不是真測試卻判 yes」的單一識別字。
2. `平台:名稱`:單平台(legacy,`split` 為空、不切分)整串含冒號,過不了 `_KILL_METHOD_OK_RE`,判 bad-name,`py:test_alive_and_well` 實跑 rc1(不豁免)。多平台:前綴是已定義平台且名稱在該平台測試集合裡 rc0(`py:`、`py2:`),名稱不在該平台 rc1(`py:test_alive`),前綴不存在 rc1(`nosuch:`,`resolve_test_refs` 丟 ValueError 判 bad-name)。行為一致、無洞。
3. 第②道 `_test_in_tree`:會判 found。它只用 `git grep -w -F` 在平台根下「副檔名符合」的所有檔找整字,沒套檔名錨(python 的 `test_*.py`),也不分註解、字串、非測試檔。第一道看的是工作目錄,所以「未追蹤、沒提交的測試」只要名字在已提交的任何 .py 出現一次,第②道就被騙過。實跑見下方 finding。
4. 綁定寫在毫不相干的筆記:跟設計〈天花板〉1 同級,沒找到更嚴重的,不另報。

## Finding 1:推送時第②道只要名字在任一已提交 .py 出現就算找到,擋不住未提交的測試

severity: minor
blocking: 否。判準:要先寫一支未追蹤的測試、名字又剛好在別的已提交 .py 的註解或字串出現,才能繞過;後果只是「只換測試綁定」的豁免多放一次,不是資料毀損,可在推送前人工或 CI 的筆記測試綁定要存在補回。

引句:「只掃該 profile 的測試副檔名、排除 docs/ 與 governance/(r1 外家 finder f3:治理帳本身寫著 evidence 的」
file: `scripts/lumos:44519`

重現(臨時 repo,python 測試棧;B 的測試綁定新增 `[test:test_ghost]`,A 的程式被改):
- 未追蹤的 tests/test_ghost.py 定義 `def test_ghost()`,已提交的 src/a.py 多一行註解 `# test_ghost`。指令 `home check --diff base..HEAD`,輸出 rc0(只剩提醒「src/a.py 改了,它的家 Systems/A 這次沒動」),被豁免。
- 同樣的未追蹤測試、但沒有那行註解:rc1,點名 Systems/B(第②道正確擋下)。
- 名字改放已提交的 tests/test_x.py 的字串 `S='test_ghost'`:rc0,同樣被豁免。

根因:`_test_in_tree` 的搜尋範圍是「副檔名」不是「測試檔」(python 的 `file_name_match` 沒用上),而且是文字搜尋不是宣告搜尋;`_ns_tr_guard` 用 `git diff HEAD` 只看已追蹤檔的修改與刪除,未追蹤的新測試檔不在內。兩個缺口疊起來,第②道只擋得住「名字完全沒出現在樹裡」的未提交測試。

## 沒有找到問題的點

- 第一道精確比對、無大小寫或前綴混淆。
- 平台前綴三種情形行為正確。
- 說明藏在「選了哪支真測試」本身,屬設計已列天花板。

總結:全份最高等級 minor
