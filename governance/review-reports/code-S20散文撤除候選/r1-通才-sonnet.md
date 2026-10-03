severity: minor

看了:全部 hunk(scripts/lumos 的 `_ns_tr_prose_retire`/`_ns_tr_prose_candidate`/呼叫處、新測試、三篇筆記)。在 shared clone 跑了 `python3.14 scripts/test_lumos.py -k t_doctor_s20_prose_retire` 8 項全綠,並用抄出來的 regex 與函式逐一探測輸入(結果見各條)。

走過沒問題的:
- 兩行說明、第一行改寫第二行才撤除:`_ns_tr_prose_candidate` 對第一行得 False 後繼續迴圈,第二行判到才回 True,不會提早判定。
- 全形空白:`str.lstrip()` 與 `\s*` 都吃 U+3000,`裁定:　改寫為X` 判不列。
- 「改寫為」「保留原樣」:startswith 前綴比對,過。
- 括號套括號(`裁定(2026-09-25),〈使用者裁定〉:改寫:…`,裁定到冒號 19 字內):判不列。
- 條款已作廢但沒掛 `[test:]`:`any(_test_names_of(sp)[0])` 本來就擋掉,不列,與「已作廢另有規則管」一致。
- 下一層是空行再接說明:`not ln.strip()` 直接 return False,不列(舊版同樣行為,不是這次引入)。
- 測試不空轉:②③案例要列、①④要不列,兩個方向都有,可見條款行有被認成 clause。

## F1 裁定與冒號之間超過 20 字就整個退回舊判法,原本要修的誤報又回來
severity: minor
blocking: 否
引句:「_NS_TR_VERDICT_RE = re.compile(r"裁定[^:：\n]{0,20}[:：]\s*")」
輸入:`  - 代使用者裁定(2026-09-25,依 Enzo 於對話中的明確指示與前述討論)：改寫,舊測試撤除`。走到 `_ns_tr_prose_retire` 的 `m = _NS_TR_VERDICT_RE.search(ln)`:裁定到冒號間有 24 字,m 為 None,落到最後一行 `"撤除" in ln and "保留" not in ln` 回 True,被列。實測 True。
這正是投稿要修的那類說明,只是括號寫長一點就失效;上限 20 是拍腦袋值。只是多列一條提醒(不擋、不計問題數),所以 minor。

## F2 只取第一個「裁定」,同一行後面的裁定不被評估
severity: minor
blocking: 否
引句:「    m = _NS_TR_VERDICT_RE.search(ln)」
輸入:`  - 裁定:改寫 x;另裁定:撤除這條`。search 只回最左邊那個 match,後面接改寫 → 回 False,第二個裁定的真撤除被漏掉(實測 False)。同一行兩個裁定罕見,但「漏列」方向比誤列更不好發現;至少本文說明應寫「只看第一個裁定」。

## F3 動作詞清單太窄,常見變體仍被誤列或漏列
severity: minor
blocking: 否
引句:「_NS_TR_KEEP_VERBS = ("改寫", "保留", "維持")」
輸入與實測:`裁定:改為新行為,舊守衛撤除`(「改為」)、`裁定:「改寫」舊守衛撤除`(前面有引號)都回 True 被誤列;反方向 `裁定:不改寫,撤除這條` 因 startswith 前綴比對而回 True 是對的,但 `裁定:改寫為X,撤除這條` 回 False(條款本身被撤也被放掉),取決於「改寫」的語意是否永遠表示條款有效,筆記沒寫。屬詞彙覆蓋缺口,低嚴重度。

## F4 新測試沒覆蓋本次設計最容易出錯的幾個形狀
severity: minor
blocking: 否
引句:「             ("②裁定後一句話講撤除", "- [S1] 當 x 時應 y [test:test_alive]\n  - 裁定:這條撤除了", True),」
缺的案例(都是審查要求會問的):①同一條款兩行說明,第一行改寫、第二行才撤除(鎖住「不因第一行提早判定」);②裁定與冒號超過 20 字(F1,現行為是誤列,測試若補上會暴露要不要調整);③「裁定」在句中且前有別的字;④空行後才有說明(鎖住既有行為)。目前 8 案都只有單行子項,`_ns_tr_prose_candidate` 的迴圈繼續分支沒有任何案例走到。mutation 面:把 `return False` 改成 `return` 以外的提早回傳不會被抓。
file: `scripts/test_lumos.py` 新測試 `t_doctor_s20_prose_retire_by_verdict_verb`(`cases` 清單只有單行子項)

最高等級:minor,blocking 共 0 條
