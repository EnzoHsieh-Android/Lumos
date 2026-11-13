severity: minor

## t1 人裁寫回把計劃裡單獨的 CR 或其他行分隔字元悄悄改成 LF
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前 6ccb7a46 的 `nl = "\r\n" if "\r\n" in text else "\n"` 已有同一行為;修後只擋了 CRLF,沒擋單獨的 `\r`)
引句:「(原本用通用換行讀、寫回整份變 LF,diff 整份重寫;代碼審 r1 b1、c8)」
file: `scripts/lumos:5362`(`_note_lines` 認 `\n`、`\r\n`、`\r` 三種行尾)、`scripts/lumos:75519`(`_situation_rule_insert` 用 `"\n".join` 重組全文)

1. `_situation_rule_read` 只用 `b"\r\n" in raw` 拒絕 CRLF。單獨的 `\r` 放行。
2. `_situation_rule_insert` 用 `_note_lines` 切行,再用 `"\n".join` 接回。計劃裡其他位置的單獨 `\r` 因此被換成 `\n`。
3. 實跑:餵入 `text="# P\n\n## 驗收條款\n\n- [S1] 當 A 時,應回 B [test:t_a]\n  續行\n\n## 其他\n備註\x0c含換頁\rCR殘留 x\n"`。
   - 結果是 `...備註\x0c含換頁\nCR殘留 x\n`,`\r` 變成 `\n`,插入點以外的內容被改了。
   - 這跟 `_situation_rule_read` 註解「不靜默改成 LF」的承諾不符。
   - 寫回後的讀回比對只比「要寫的」跟「讀回的」,抓不到這件事。
4. 修前同樣會改(沒有 `\r\n` 時 `nl` 是 `"\n"`),所以不是這輪修補弄出來的。
5. 實際計劃檔幾乎不會有單獨的 `\r`,所以只列 minor。

## t2 寫完讀回不一致時回 rc 2,但計劃檔其實已被取代
severity: minor
blocking: 否
歸因:有證據的修復回歸(讀回比對是本輪新增,見修後 `_situation_rule_write`;修前自寫的原子寫在暫存檔上比對,不會在取代之後才發現)
引句:「計劃寫完讀回跟要寫的不一樣({'讀不回來:' + back.__class__.__name__ if isinstance(back, OSError) else '內容不同,可能有別的程式同時改它'});」
file: `scripts/lumos:75516`(`cmd_situation_rule` 文件字串寫「2 拒絕(計劃與治理帳都不動)」)

1. 新碼先 `_write_bytes_atomic`(已 `os.replace`)再讀回比對。不一致時回原因,上層 `_situation_rule_say` 回 rc 2。
2. 這時計劃已經換成新內容,新條款已寫入,治理帳沒記。
3. 文件字串的 rc 契約把 2 定義成「計劃與治理帳都不動」,這條路徑違反它。訊息本身有講「治理帳沒記——先看計劃現在的內容」,所以呼叫端不會被誤導,只是契約與實際行為不一致。
4. 修前沒有這條路徑,是新增的。
5. 後果有限:再跑一次會被 `_situation_rule_insert` 的「計劃已寫過 S<n>」擋下,並指向補記帳的做法。用單獨的 rc 或訊息講清楚「計劃已動」即可。

## 附:三問、圖譜鏡頭

**①原問題修復效果的行為證據**
- `_spec_gate_ruled_ids` 現在要求「條款文字指紋相同,且該行綁的測試集合恰好等於帳上的 `test_name`」。`refs` 是 `invariant_test_refs` 直接取原字串,寫帳時用的 `test` 也是原字串,兩邊口徑一致。命令:`grep -n '"refs"' scripts/lumos`,看到 15821 行 `refs = invariant_test_refs(seg)`,與 75508、75524 行的比較方式相符。
- `_expected_requirement` 把讀帳移到門判斷與生效日之後。呼叫端只有 16243(規格閘)、17321(推送前,帶 ctx)、17645(簽核)。`ctx["exp_gov"]` 只在 `_expected_gov` 與 `_expected_push_one` 兩處使用(`grep -n exp_gov scripts/lumos`),且 `_expected_push_one` 之後只過濾 `kind == "expected-signed"`,混進 situation-rule 事件不影響。
- `_gov_vc_gate_events` 確實接受 tuple 閘名(`scripts/lumos:23559`)。
- `_isolated_worktree` 的 keep 標記:`guard kill` 在 `recipes_override` 時 `sweep_repo=proot`(`scripts/lumos:27849`),前綴 `lumos-kill-` 與 keep 現場前綴相同,所以標記確實有作用。`parent` 在 `try` 之前已建立,`finally` 裡用得到。
- `_confirm_tty_dev` 改用 `_confirm_tty_open` 後,原本的 `tty_path` 變數沒有其他使用處(`grep tty_path` 無殘留)。舊的 `_tty_reachable` 在全 repo 已無殘留。

**②修補處的正常、錯誤與相鄰呼叫路徑**
- `_situation_rule_recipe_problem` 改走 `_kt_sit_read_many`,錯誤類別 `_KtSitUnverifiable`、`_KtSitOverBudget` 都有定義,`subprocess` 在模組層 import(65921 行),不會在例外分支才炸。
- 行為差異:新讀法會把 CRLF 正規化成 LF。CRLF 的 .kt 檔現在會通過「恰好一次」的檢查,實際套壞法時才找不到原文,得到非 killed 的判定而被擋下。結果仍是安全地拒絕,只是訊息比修前差,不構成 finding。
- `_kt_sit_has_applies` 現在只要有任一列填了非空 spec 就會算對應計劃名單。名單算不出來時整題被擋,這是計劃所要的「填了照樣核對」,不是退化。
- `_KT_SIT_CID_RE` 在 `_kt_sit_spec_parse` 之後才定義,但只在呼叫時才用,模組載入完成後不會有名稱錯誤。
- `_situation_rule_platform` 改用 `_kill_plat_top` 後仍保留「在平台根底下」的第一道檢查,再從 repo 頂算 kfile。`log_recipe_id` 取 `res["recipe_id"]`(殺傷力帳本實際值),錯誤列沒有該欄時為空字串。只有 killed 的列會被用到,不影響。

**③新發現案例在修前與修後**
- t1(單獨 `\r`):修前與修後行為相同,都會改行尾(見上)。
- t2(讀回不一致):修前沒有這條路徑,修後新增,rc 契約不符。

**圖譜鏡頭**:這次沒附固定席筆記(鏡頭計算超時),只看了 patch 內改到的筆記。
- `Systems/guard-kill`、`Systems/規格閘`、`Systems/棧別提問表態閘` 的 WHY 行跟程式一致:`_clause_sha`、`log_recipe_id`、`.lumos-keep`、讀帳時機都對得上。
- 沒找到筆記與程式對不上的地方,因此不另立 Issue。

**未覆蓋或未能驗證**
- 我沒有實跑 `t_situation_rule_term_signal` 與 `t_isolated_worktree_keep_marker`。
- `t_kt_bj_specs_are_data` 只檢查提示字串存在,對「條款原文是資料」這件事沒有行為證據。它守的是提示字串,不是盲判的實際行為。這是設計上的天花板,我當作覆蓋面事項,不立 finding。

最嚴重 severity: minor,blocking 共 0 條。
