severity: minor

我在派工詞尾端有看到「lumos 自動附加:本次改動的固定席節點」段(來源 impact --diff,列了測試假綠形態等節點)。沒有看到「圖譜沒有釘到節點」段。

## F1 計劃的落點欄列了 Systems/筆記內容閘,但這次改動沒有寫進它
severity: minor
blocking: 否
引句:「  - Systems/筆記內容閘」
佐證:``docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md`` 存在,我 grep 了 `_ns_tr_manual_clauses` 和 `S20`,各 0 筆。實際只改了 Systems/lumos-cli-read。
說明:專案規則是計劃的 lands_in 要列「現況落在哪幾篇」。實作紀錄 r2 說已把「落點欄位補上實際寫了說明的 Systems/lumos-cli-read」,但 lands_in 仍多留一篇沒落地的節點。這是落點對不上,只有 minor。

不對齊的地方只有這一條。

## 三問

**1. 分層與依賴方向:對齊。**
新函式 `_ns_tr_manual_clauses` 只用同層既有零件:`_notelines_regions`、`slot_parse`、`_test_names_of`、`_ns_tr_retired`,以及呼叫端傳進來的 `clause_bindings` 結果。這跟鄰居 `_ns_test_ref_lines` 用的零件一樣,沒有跨層直呼。
引句:「    lines, regions = text.split("\n"), _notelines_regions(text)」
佐證:``scripts/lumos:31986`` 的 `_ns_test_ref_lines` 也是 `regions = _notelines_regions(text)`,並且 `regions[no - 1] != "body"` 就跳過。
引句:「        rows = _ns_clause_rows(_note_from_text(rel, text), text)   # 同一篇只解析一次,[test:] 與 [manual:] 兩條路共用」
說明:`_ns_clause_rows` 是把 `_ns_test_ref_lines` 原有的 clause_bindings 呼叫(空索引、try/except 回空)原樣抽出來。`_ns_test_ref_lines` 改成接 `rows=None`,預設自己算,其他呼叫端不受影響。

**2. 命名與錯誤處理:對齊。**
命名沿用 `_ns_tr_*` 與 `_ns_*` 前綴,以及 `_doctor_test_ref_lines` 的 cats 結構。`prose` 類只改了列出的文字和修法提示。
引句:「    except Exception:」
佐證:``scripts/lumos:31976`` 的 `_ns_clause_rows` 是從 `_ns_test_ref_lines` 舊碼原樣搬出來,連 `except Exception` 吞掉都一致。
引句:「                or not 0 < no <= min(len(lines), len(regions)) or regions[no - 1] != "body":   # 跟 [test:] 那條路一樣只看正文」
說明:行號越界先防住,跟鄰居 `no > len(regions)` 的做法同向。

**3. 第二種做法:沒有引入。**
- 「靠人驗」的判定:直接取 clause_bindings 的 state,不自己解析 `[manual:]`。r3 被判成第二套的「單行丟回解析器重判」已拿掉。
引句:「        if r.get("state") != "manual" or all(v.startswith("已撤除") for v in r.get("manual") or []) \」
- 「有測試名」的判定:用跟 `[test:]` 那條路同一支 `_test_names_of`,另一條路在 ``scripts/lumos:32414`` 也是 `any(_test_names_of(sp)[0])`。
引句:「        if not _ns_tr_retired(sp) and not any(_test_names_of(sp)[0]):   # 同行的 [test:] 那條路認得(全形冒號等)就讓它列,不重複」
- 「已作廢」的判定:用同一支 `_ns_tr_retired`。
- 「下一層寫撤除」的判定:用同一支 `_ns_tr_sub_says_retire`。
引句:「            if _ns_tr_sub_says_retire(lines, no):」
- 「正文」的判定:用 `_notelines_regions` 判 body,跟 `[test:]` 那條路同一個函式。

⚠ 一個我判不準、不列為 finding 的細節:`_ns_test_ref_lines` 另外走 `_visible_lines`(跳過圍欄程式碼),新函式沒有自己再走一次。條款行本來就來自 clause_bindings 的 defined 行,而 clause_bindings 也靠 `_visible_lines`(``scripts/lumos:4688`` 定義、筆記的 ~~~ 圍欄條有紀錄),所以兩條路實際看到的行很可能一樣。我沒有造輸入實跑驗證。

不對齊共 1 條,其中 major 0 條
