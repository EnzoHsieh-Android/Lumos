severity: minor

# 第三輪修正驗收(正確性席)

驗法:用 importlib 載入 scripts/lumos,對 `_nodehome_strip_test_tags`、`_nodehome_test_tag_value_ok`、`_NODEHOME_TAG_NAME_RE`、真 judge(`_nodehome_tag_judge` 對 lumos-rtb3 工作樹)逐一餵輸入。腳本:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/e3f520f1-d42a-46c6-9fbc-9facf25c84a0/scratchpad/t1.py。角色鏡頭題(be-api-compat、be-authz)不適用:本改動是 CLI 內部判定,沒有對外端點或欄位。

## 發現

### F1 標記後緊接標點時,新空白規則造成誤擋(第三輪修正自己引入)
severity: minor
blocking: 否 + 只往「多算成寫了說明」的保守方向錯,不會放行真說明,可改成拆提交或把標記挪到行尾
file: `scripts/lumos:4202`
引句:「if b >= len(line) or line[b] in _SLOT_STRIP_WS:」
失敗場景:舊版 `說明。` 或 `a.`,新版改成 `說明 [test:t_x]。` 或 `a [test:t_x].`。第三輪前,標記前面的空白一律吞掉,拿掉後是 `a.`,兩版一致、不算寫說明。現在後面不是空白也不是行尾就不吞,實測 `_nodehome_strip_test_tags("a [test:x].")` 回 `a .`、`"a [test:x], b"` 回 `a , b`,跟沒標記的 `a.` 不同,sig_t 不一樣,整篇被當成有寫說明。同族:`"a [test:x]b"` 回 `a b`(這個是刻意的)。

## 逐題核對(都沒找到會放行真說明的輸入)

- 名稱形狀:`_NODEHOME_TAG_NAME_RE` 只收單一識別字加選配前綴。全形冒號寫法 `ios：testFoo` 不在 `_NODEHOME_TEST_TAG_VALUE_RE` 字元集,整個標記原樣留、不豁免(保守)。`Class::m`、`A.b` 會被 value_ok 收下當綁定拿掉,但新名稱形狀不符 `_NODEHOME_TAG_NAME_RE.fullmatch(nm)` 而不豁免。反引號整段包住的 `foo bar` 剝掉後含空白,同樣不豁免。真 judge 對 `python:`、`english:`、`a-b:` 前綴一律 no(bad-name),單字假名稱判 fake。
- 提交編號:大寫十六進位 `x@ABCDEF1`、六碼 `a@123456`、`@` 後接說明,整個標記都留下(算內容變動)。`a @ 1234567`(@ 前後空白)正確收下。逗號清單 `a@1234567,prose words` 會把 `prose words` 一起拿掉,但它進 tag_names,test-gone 要求上一版就是 `[test:]` 綁定,不在就不豁免;不是新洞。
- 核取方塊:`"[" not in line` 只會誤留核取方塊那一型(`_NOTELINES_BARE_LIST_RE` 只容許 `[ ]`、`[x]`),`- [x] [test:x]` 回 `- [x]` 保留。`* [[Systems/a]] [test:x]` 本來就不符合只剩清單符號,不受影響。
- 連續標記與行首:`a [test:x][test:y]`、`a [test:x] [test:y]` 都回 `a`;`- [test:x] [test:y]` 整行丟;行首、縮排、tab、全形空白拿掉後都跟沒寫過一致。
- 空行吞併:`x\n\n[test:a]\n\ny` 對 `x\n\n\ny` 不一致(舊版本身有兩個空行才會踩),屬保守方向,不另標。
- 去前綴:`_NODEHOME_TAG_PREFIX_RE` 的 `(?!:)` 讓 `Class::method` 不被去掉;只有 `ios:foo` 這型被去,`[test:android:foo]` 換成 `[test-gone:foo@…]` 會當同名,影響只是放行純標記變動,不涉說明。

總結:全份最高等級 minor
