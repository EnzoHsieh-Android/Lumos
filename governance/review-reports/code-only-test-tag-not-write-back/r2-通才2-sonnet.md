severity: blocker

# code r2 通才席 報告(只換測試綁定不算寫說明)

結論:r1 的洞換了個標記名仍然開著。豁免把 [test-gone:…] 一起拿掉,而「筆記測試綁定要存在」對 test-gone 只驗「測試還在就擋」,不驗「名稱像不像真測試名」;指不到的一句英文說明反而是它的合法輸入。兩道檢查都放行。

severity: blocker
blocking: 是——繞過「改程式要把說明寫進家」的核心守衛,且兩道檢查都 rc0,沒有第二層網
file: `scripts/lumos:26892`(豁免拿掉 test-gone)、`scripts/lumos:29770`(_ns_tr_gone_viol 只擋空名、佔位字、測試還在三種)
引句:「line, k = _slot_strip_keys(line, ("test", "test-gone"), keep=lambda v: not _nodehome_test_tag_value_ok(v))」
引句:「那道會在同一段推送裡核對新寫的測試名真的存在,一句英文說明包成 [test:…] 會在那裡被擋」
失敗場景:改 `src/a.py`,同一提交在不是家的 Systems/B 寫 `[test-gone:a now retries three times then logs]`。值通過 _nodehome_test_tag_value_ok(英數加空白,少於 200 字),標記被拿掉,內容比對判「沒變」,每支檔有家放行。test-gone 在 _ns_tr_gone_viol 只有「名稱空、佔位字、同名測試還在」才違規;一句話不是任何測試名,judge 回 no,test_refs 也放行。上述引句「會被擋」的前提只對 [test:] 成立,對 [test-gone:] 不成立。
附帶同根變體,同樣兩道都過:加 `@abc1234` 尾巴(test-gone 解析時 @ 後面被丟掉);把說明拆成多個 [test-gone:…] 標記。
最小重現(臨時 repo,沿用 _tr_repo、_nh_check、_tr_push;腳本 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/e3f520f1-d42a-46c6-9fbc-9facf25c84a0/scratchpad/x/probe.py`,用 python3.14 跑),輸出:
- test-gone sentence:homecheck rc 0 | testrefs rc 0
- test-gone sentence @sha:homecheck rc 0 | testrefs rc 0
- many tags(三個 test-gone 拆句):homecheck rc 0 | testrefs rc 0
- 對照 [test:一句話]:homecheck rc 0 | testrefs rc 1(指不到真測試(dangling),r1 的修法只擋到這條)
- 對照 [test:python:一句話](平台前綴):testrefs rc 1(bad-name),也被擋,前綴路徑沒洞
修法方向(不是建議考慮,是缺口所在):豁免拿掉的 test-gone 值,必須在同一道檢查裡也驗「像測試名且曾經是這個 repo 的測試」,或豁免只拿 [test:] 不拿 [test-gone:]。

其餘檢查項(已跑,無洞):
- 平台前綴:`[test:python:一句話]` 被 test_refs 擋(bad-name),無洞。
- 豁免開關:`_nodehome_tag_exempt` 以被檢查版本的 config 判,未設 test_refs 預設 warn → 豁免關,保守。
- ⚠ 提交時(staged)那道只提醒:豁免開關在提交時按 push 語意算 block,提交端對藏句不擋,全靠推送端;推送端若被 LUMOS_SKIP_NOTE_SHAPE=1 單次跳過(會留帳),豁免仍開。判不準是否算洞,不另列 finding。

總結:全份最高等級 blocker
