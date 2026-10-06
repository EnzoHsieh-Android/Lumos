severity: major

# 架構對齊審查 r1(只換測試綁定不算寫說明)

## 問 1 分層與依賴方向
結論:大體一致,有一處跨層直呼私有函式,判 minor。

- 新的 `_slot_scan` / `_slot_strip_keys` 放在 slot_parse 旁、`slot_parse` 改走 `_slot_scan`,同區共用同一份掃描,方向正確(沒有另寫第二套掃描器)。
- `_nodehome_strip_test_tags` 直接呼叫 `_slot_strip_keys`(私有、底線開頭、在 4188 行的 slot 區),而 `_nodehome_` 區(26539 起)原本沒有呼叫 `_slot_*` 私有函式的先例;`slot_parse` 在 slot 區外是用公開名呼叫。屬跨區私有直呼,但因為是「共用單一掃描」的刻意設計且改動小,不到引入第二種做法。
severity: minor
blocking: 否 + 結構是單向依賴(nodehome → slot),沒有重複實作,只是私有名跨區;可改名成無底線的公開名或維持並在 docstring 註明
引句:「line, k = _slot_strip_keys(line, ("test", "test-gone"), keep=lambda v: not _nodehome_test_tag_value_ok(v))」
既有碼佐證:file: `scripts/lumos:4223`(slot 區內自己用 slot_parse),`scripts/lumos:26539-26551`(_nodehome 區常數都放在函式群之前)

- 常數 `_NODEHOME_BARE_ITEM_RE` 定義在使用它的 `_nodehome_strip_test_tags` 之後(26897 對 26882),而同函式的 `_NODEHOME_TEST_TAG_VALUE_RE` 卻放在函式前;鄰居慣例是常數集中在區頭(`scripts/lumos:26539-26551`)或緊接在使用者之前。同一組新碼內部也不一致。
severity: minor
blocking: 否 + 執行期不出錯(呼叫時模組已載入完),只是擺放不一致
引句:「_NODEHOME_BARE_ITEM_RE = re.compile(r"\s*(?:[-*+]|\d+[.)])?\s*")」

## 問 2 命名與錯誤處理
結論:一致。
- 命名 `_nodehome_*` / `_slot_*` / `_NODEHOME_*_RE` 都沿用前綴;`_nodehome_test_tag_value_ok` 對應 `_nodehome_resp_ok`(`scripts/lumos:26646`)的 `_ok` 後綴判斷函式。
- docstring 為繁中、一句帶冒號說明「輸入 → 輸出」,跟 `slot_parse` 的口吻相同(`scripts/lumos:4150` 附近)。錯誤處理:純函式、不丟例外,沒收尾欄位以錯誤欄回傳,承襲 slot_parse 的 `(key,val,err)` 慣例。
引句:「def _nodehome_test_tag_value_ok(v):」

## 問 3 第二種做法
- 「整行只剩清單符號」:專案已有 `_NOTELINES_BARE_LIST_RE`(`scripts/lumos:28477`,`^\s*(?:[-*+]|\d+[.)])(?:\s+\[[ xX]\])?\s*$`)判同一件事,另有 `_CLAUSE_LEAD_RE`、`_EXCL_LEAD_RE`(`scripts/lumos:6741`)等清單前綴正則。diff 另造 `_NODEHOME_BARE_ITEM_RE`,功能重疊(差別只在能否空白行、核取框)。判:自創同功能常數而鄰居已有。
severity: major
blocking: 是 + 同功能已有既有正則卻另寫一份(引入第二種做法);可複用 `_NOTELINES_BARE_LIST_RE` 加空行分支,或說明為何語意不同並在 docstring 指向它
引句:「_NODEHOME_BARE_ITEM_RE = re.compile(r"\s*(?:[-*+]|\d+[.)])?\s*")」
既有碼佐證:file: `scripts/lumos:28477`

- 測試把舊版實作整段抄一份當對照組(`_slot_parse_reference`):在 test_lumos.py 搜尋 `_reference` 的函式定義只有這一處(`scripts/test_lumos.py:47108`;其餘 `_reference` 命中是 skill reference 測試,無關),專案內無「抄舊實作當 oracle」先例。判:新做法,但是重構等價性的一次性對照、且附日期與計劃出處,風險低;⚠ 無法確認是否算「第二種做法」,保守列 minor。
severity: minor
blocking: 否 + 只在測試內、不進產品碼,但屬專案首例,建議確認是否接受(或改用既有「全 repo 筆記行 snapshot」之類做法)
引句:「"""slot_parse 抽成共用掃描之前的實作原樣(2026-10-05,只換測試綁定不算寫說明_計劃 [S5] 的對照組)。"""」

- 測試夾具 `_nh_repo/_nh_node/_nh_commit/_nh_check` 沿用既有 t_nodehome_* 寫法,一致。
引句:「root = _nh_repo()」

不對齊共 4 條,其中 major 1 條
