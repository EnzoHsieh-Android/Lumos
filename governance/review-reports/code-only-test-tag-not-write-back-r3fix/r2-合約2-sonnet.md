severity: minor

# 驗收審 r3fix 第二輪:合約與圖譜一致鏡頭

## 做了什麼
逐句拿 `scripts/lumos` 核對〈範圍〉〈天花板〉1 到 10 與 Systems/每支檔有家、Systems/筆記內容閘、Projects/每支檔有家_計劃;S1 到 S6 對測試格;綁定的 [test:] 名稱逐個 grep;跑 lint、doctor、相關測試子集(`-k t_nodehome_test_tag` 45 過、`t_nodehome_diff_test_tag` 2 過、`t_nodehome_tag_only` 6 過、`t_slot_parse_unchanged` 2 過,皆 0 失敗)。`lint Projects/只換測試綁定不算寫說明_計劃` 0 問題;`doctor` 圖譜健康 0 issues(提醒段是既有舊帳,與本改動無關)。

## 逐句核對結果(皆對得上)
- 空白規則:程式 `if b >= len(line) or not line[b].isalnum():` 對上計劃與兩篇 Systems 的「後面不是緊接著字(空白、標點、行尾)才連前面空白一起拿、緊接英數或中文就留著」;實測 `a [test:x]b`→`a b`、`a [test:x]。`→`a。`、全形空白、連續兩標記、核取方塊行(`- [ ]` 留著)皆如文。
- test-gone 整串一致:`old_tests = {nm for k, nm in b["tag_names"] if k == "test"}` 與 `if nm not in old_tests`;`_NODEHOME_TAG_PREFIX_RE` 已全 repo 消失(grep 只剩計劃歷史句);計劃〈範圍〉、天花板 6、Systems WHY 三處同一說法。
- @ 規則:`_NODEHOME_COMMIT_RE = [0-9a-f]{7,40}` 套在 `_nodehome_test_tag_value_ok` 所有含 @ 的段(一般綁定也套),對上「小寫 7 到 40 碼、一般綁定的值也套」。
- [test:] 新名稱帶平台前綴不能夾帶說明:實測 `Every-order-needs-approval:<真測試名>` 判 ('no','bad-name')(`resolve_test_refs` 要求前綴是已定義平台,legacy 單平台整串含冒號判 dangling),所以 `_NODEHOME_TAG_NAME_RE` 放行前綴不開 r1 那種洞。
- 效能、判定失敗印一句、例外當不豁免、`_ns_tr_guard` 回 None 不豁免:程式與〈做法〉3、〈實務隱患〉、天花板 5/8 一致;`tag_judge` 是用到才建、快取一次。
- S1 到 S6 對測試格:S1/S3 → `t_nodehome_test_tag_only_edit_is_not_write_back`(⑤b 四種非識別字、⑤c @ 非提交編號、⑤d 兩種前綴、⑤e 大寫與一般綁定帶 @);S2 → `t_nodehome_diff_test_tag_only_edit_is_not_write_back`;S4 → `t_nodehome_test_tag_strip_edges`(⑫ 六個標籤含 tab、句號、全形逗號,⑫b、⑫c、⑮ CRLF 皆在);S5 → `t_slot_parse_unchanged_after_scan_refactor`;S6 → `t_nodehome_tag_only_new_names_must_be_real_tests`(①②③、④、④b、⑤)。七個被綁的方法名各在 `scripts/test_lumos.py` 恰好 1 個 def。
- ⑤e 的大寫十六進位格有殺傷力:`test-gone:test_drop@1A2B3C4` 若拿掉 @ 規則會因名稱在上一版綁過而放行(rc0),測試會翻紅;`test:test_new@…` 那格另被 `_NODEHOME_TAG_NAME_RE` 擋住,所以 @ 規則在 [test:] 一般綁定上靠兩道保護、不是單靠 @ 規則(不影響行為)。
- 其他筆記沒變假話:全 `docs/` grep `平台前綴|TAG_PREFIX|_nodehome_tag_exempt`,舊名只在本計劃歷史段;Systems/每支檔有家的 KEY(推送前逐提交、專案開關兩行)與 Projects/每支檔有家_計劃 [S12]、「誤擋」仍成立。

## Findings

severity: minor
blocking: 否——只是紀錄的完整度,程式與規則行為都沒錯;判準:不會讓接手者做出錯誤改動。
引句:「只認「測試刪了、改標成已刪」」不在 diff 內,改引 diff 的程式句:「if nm not in old_tests:」
file: `docs/lumos-toolchain-knowledge/Projects/只換測試綁定不算寫說明_計劃.md:31`
說明:計劃寫 test-gone「只認「測試刪了、改標成已刪」」,程式只要求名稱是上一版綁過的 `[test:]`,並不核對那支測試真的刪了(測試還在也放行)。放行的是沒有新字的改標,不能夾帶說明,所以不構成洞;但句子比程式強,三個月後的人會以為有核對。處理:把句子改成「只要求上一版綁過這個名稱,不核對測試是否真的刪了」。

severity: minor
blocking: 否——歷史紀錄的數字、不是現況宣稱;判準:有日期、其後有更正段。
引句:「每支檔有家(265 條)、筆記形狀(267 條)、slot 系列(198 條)測試全綠」(file: `docs/lumos-toolchain-knowledge/Projects/只換測試綁定不算寫說明_計劃.md:93`)
說明:同一句開頭「五條驗收測試先紅後綠」現在是 S1 到 S6 六格、測試數也已變(實跑 `-k t_nodehome_test_tag` 為 45 條)。這是 2026-10-05 當天紀錄,但沒標成「當時」。接手者拿它當現況會誤算。處理:句首補「(當時,未更新)」或刪掉數字。r3 那段仍寫「test-gone 比對去平台前綴」,後面有 r3fix r1 的更正,可讀,但建議在那句後補「(已於 r3fix r1 改回整串一致)」。

severity: minor
blocking: 否——只是不完整,不是假話;判準:被省略的條件在計劃與 Systems 都有寫。
引句:「只換、加、刪測試綁定、而且新出現的名稱指得到真測試也不算」(file: `docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md:123`)
說明:[S12] 的補充只提「名稱指得到真測試」,沒提 test-gone 要整串一致與 @ 規則;細節在被連結的計劃與 Systems WHY 裡,讀 [S12] 單句的人會以為 test-gone 隨便寫都行。處理:補半句「(test-gone 要是上一版綁過的名稱)」。

severity: minor
blocking: 否——效能描述略不精確,不影響行為;判準:實測 `tag_judge` 只在 `_nodehome_tag_only_change` 走到新的 `[test:]` 名稱才呼叫。
引句:「測試名判定要掃測試檔建索引,只在某篇「sig 不同但 sig_t 相同」時才建」不在 diff 內,改引程式 docstring:「測試名判定,第一次真的需要(某篇只差測試綁定)才建——建索引要掃測試檔。」
file: `docs/lumos-toolchain-knowledge/Projects/只換測試綁定不算寫說明_計劃.md:55`
說明:只拿掉綁定或只新增 test-gone 時也是 sig 不同、sig_t 相同,但不會建索引;條件實際多了「有新的 `[test:]` 名稱」。計劃說法比實際保守,無害。

## 結論
合約、圖譜與程式逐句一致;本輪 r3fix 修正(test-gone 整串一致、標點後空白、@ 規則測試格)在計劃、Systems/每支檔有家、Systems/筆記內容閘三處同步,沒有找到假話或斷鏈的 [test:]。只有四條文字精確度的 minor。

總結:全份最高等級 minor
