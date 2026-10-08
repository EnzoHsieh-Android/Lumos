severity: major

# code r2 正確性席2(sonnet)

範圍:r2-delta.patch 逐 hunk 走輸入。設定檔不存在、壞 JSON、note_shape 不是物件、捷徑檔,全部讀程式後判為豁免關(strict 方向),沒找到洞。_nodehome_evaluate 只有 cmd_home_check 一個呼叫端,cfg.get("tag_exempt") 缺鍵時回 None 走 sig,安全。推送範圍中途改設定:豁免與 _nodehome_mark_note_content 都只看終點版本設定(tip_where),起點 block 終點 warn 一律不豁免(strict),起點 warn 終點 block 則整段都豁免,後者靠終點 test_refs 擋,見 F1 的洞。下面三條是實跑出紅的。

## F1 豁免靠 test_refs 補洞,但 [test-gone:句子] 兩道都不擋
severity: major
blocking: 是——這輪新增的 S6 宣稱「藏在綁定裡的句子由 test_refs 擋」,對 test-gone 不成立,讓程式碼改動加一段不是家的散文說明繞過寫回落點檢查,擋的門等於沒關
file: `scripts/lumos:26902`、`scripts/lumos:26882`
引句:「line, k = _slot_strip_keys(line, ("test", "test-gone"), keep=lambda v: not _nodehome_test_tag_value_ok(v))」
引句:「gate, _w = _note_shape_config(cfg_text)」
失敗場景:豁免開著(test_refs=block)時,在不是家的筆記 B 加 `[test-gone:a now retries three times then logs]`(值字元合規,≤200)。test-gone 的語意是「這名字不該存在」,所以 test_refs 找不到這個名字反而判合格。每支檔有家把整個標記拿掉當沒寫,note-shape 也不擋。同一句改寫成 [test:…] 才會被 note-shape 擋(rc1),可見補洞只補了一半。
重現(臨時 repo,用 test_lumos 的 helper):
```
python3.14 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/e3f520f1-d42a-46c6-9fbc-9facf25c84a0/scratchpad/x1.py
test-gone sentence home: 0 | shape: 0
test sentence home: 0 | shape: 1
```
(home=lumos home check --diff base..HEAD 的 rc,shape=lumos note-shape --diff 的 rc;同一提交改 src/a.py 並在 B 加句子。)修法方向:豁免只拿 [test:] 不拿 [test-gone:],或 test-gone 的值要求長得像識別名(無空白)。

## F2 空白壓平讓縮排、清單巢狀、圍欄內空行的改動被判成沒變
severity: minor
blocking: 否——只有豁免開著、且同一提交改了程式時才漏放,放過的是縮排類的改動,沒有直接擋住使用者
file: `scripts/lumos:26892`
引句:「line = " ".join(line.split())」
失敗場景:豁免開著,B 的正文未圍欄的縮排程式碼 `    if x:\n        y()` 改成 `    if x:\n    y()`(語意變了),或清單 `- a\n  - b` 改成 `- a\n- b`(子項升格),或圍欄內空行 1 行變 3 行。三種都判 sig_t 相同,rc0;豁免關的版本(sig 只 rstrip)同一輸入 rc1。順帶:docstring 寫「程式碼圍欄裡的行原樣留」,但
引句:「if not line.strip() and out and not out[-1].strip():」
這行對圍欄內也生效,圍欄裡連續空行被收掉,docstring 與行為不符。
重現:x2.py 前三組 py indent、py nest change、list nest、fence blank lines 全部 `home: 0`。

## F3 sig_t 圍欄內的行不做 rstrip,行尾空白或 CRLF 轉換讓豁免專案多出假的內容有變
severity: minor
blocking: 否——只在豁免開著的專案、筆記有圍欄、行尾空白或換行字元整份改過時發生,多擋一次且有跳過逃生口
file: `scripts/lumos:26935`
引句:「"sig_t": (_nodehome_strip_test_tags(summ).strip(), dec, _nodehome_strip_test_tags(body).strip()),」
失敗場景:原 sig 對每行 rstrip 且用 splitlines(CRLF 與行尾空白不算變);sig_t 改走 _nodehome_strip_test_tags,圍欄外的行靠 split() 吃掉 \r 與尾空白,圍欄行(含 ``` 標記行)原樣留,所以圍欄內加行尾空白、或整篇 LF 轉 CRLF 在 sig_t 都算變。實跑同一輸入:test_refs=warn(用 sig)rc0,test_refs=block(用 sig_t)rc1。
重現(x3.py):
```
fence trailing space only warn home: 0
CRLF only warn home: 0
fence trailing space only block home: 1
CRLF only block home: 1
CRLF only no fence block home: 0
```
修法方向:strip 函式回傳前對每行(含圍欄行)rstrip,並用 splitlines 切行。

## 未成立
- 設定中途翻轉:起點 warn、終點 block,整段都用 sig_t,但終點 test_refs 對 [test:] 句子照擋(F1 之外),未找到新洞。
- 沒摘要或正文:summ 為空字串、body 為空,sig_t 為 ("", dec, ""),比較正常。

總結:全份最高等級 major
