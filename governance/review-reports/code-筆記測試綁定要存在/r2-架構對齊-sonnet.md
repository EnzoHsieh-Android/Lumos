severity: minor

## 問一:分層與依賴方向
對齊。`_ns_tr_add_extra` 仍放在 `_ns_tr_extra` 旁,三個呼叫端(`_ns_skip_slot_extra`、`_note_shape_report`)都走它,沒有跨層直呼。doctor S20 改走 `env_text`,跟 `scripts/lumos:13640`、`31001` 等既有呼叫一致,沒有自己讀磁碟的第二條路。`_ns_tr_is_new` 是純函式,放在 `_ns_tr_profile` 前面,位置合理。保險 `_ns_tr_guard` 提前到判之前,仍在 `_ns_test_refs_collected` 內,層次沒變。

## 問二:命名與錯誤處理
大致對齊。清控制字元整行 `_esc_clean(..., _DOCTOR_LINE_MAX)` 跟 S16–S19 一致(`scripts/lumos:3478`、`3601`、`3658`)。`_ns_tr_add_extra` 的 check 鍵用 `+` 串接,跟 `_ns_slot_extra` 的 `shape+slots`(`scripts/lumos:28419`)同一套寫法。有兩處小不一致,見 F1、F2。

## 問三:第二種做法
沒有:帳本分類鍵、清控制字元、`env_text` 讀文都沿用既有做法。行號計算(`_ns_test_ref_lines` 的 span)是新增能力,不是另一套;它重用 `_notelines_regions` 與 `_note_summary_entries`。

## F1 子模組清單逾時沒照鄰居記「逾時」狀態
severity: minor
blocking: 否
引句:「if r is None or r.returncode != 0:」
佐證行:
1. file: `scripts/lumos:28880-28883`(同檔 `_NsTrJudge` 判第②道時,git 逾時會設 `self.st["out"] = True` 並寫 notes,後面的名稱不再查)
2. file: `scripts/lumos:39228-39240`(`_lens_git` 把 TimeoutExpired 吞掉回 None)
3. 新寫的 ls-tree 路徑把「逾時」跟「git 失敗」混成同一個 `gitlinks=False`,不設 `st["out"]`,每個後續名稱都會走一次這條判不了。結構對,只是跟鄰居的逾時處理不一致;預算內重試成本小。

## F2 `_ns_tr_add_extra` 就地改傳入的 dict
severity: minor
blocking: 否
引句:「ex["test_refs"] = _ns_tr_extra(trmode, trviol, info)」
佐證行:
1. file: `scripts/lumos:28419`(鄰居 `_ns_slot_extra` 回新 dict,不改參數)
2. `_ns_tr_add_extra` 改參數又回傳同一個 dict,呼叫端兩處都忽略回傳值。可接受,屬命名/約定上的小不一致。

不對齊共 2 條,其中 major 0 條
