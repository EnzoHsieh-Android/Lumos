severity: minor

# code r1 邊界席(sonnet)報告

審查範圍:r1-snapshot.patch 全部 hunk(兩篇筆記、scripts/lumos 的 _slot_scan / slot_parse / _slot_strip_keys / _nodehome_test_tag_value_ok / _nodehome_strip_test_tags / _nodehome_parse_note、兩支測試)。唯讀。實驗用 SourceFileLoader 載入 `/Users/enzo/harness/lumos-rtb3/scripts/lumos` 直接呼叫函式。固定席筆記:派工詞說沒附,無須逐條判。

## Finding 1
severity: minor
blocking: 否 + 守衛放寬範圍與設計〈範圍〉第三條、〈天花板〉1 寫的一致,是已接受的上限,無新的失敗路徑
file: `scripts/lumos`(`_NODEHOME_TEST_TAG_VALUE_RE` 與 `_nodehome_test_tag_value_ok`)
引句:「_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")」
場景:值只要是 200 字內、只含上列字元的英文句子,整個標記就被拿掉,判成「內容沒變」。實測 `_nodehome_strip_test_tags("a [test:Always return 0 when empty, never raise]")` 回 `a`;`[test:Fix 3 bugs]` 也被拿。所以把 `[test:t_old]` 換成 `[test:Behavior now returns two on empty input]` 不算寫說明,英文說明可從這道藏過去。能擋住的只有中文、`! ? ; = + * "` 等字元、跨行、超長。能否被第二道(筆記形狀擋的 test_refs 判「指不到真測試」)補住取決於該檢查有開、沒被 LUMOS_SKIP_NOTE_SHAPE 跳過,這份 diff 沒改它。⚠ 未能確認第二道對「摘要裡 FACT/KEY 行以外、正文條款行」的 `[test:]` 是否一律檢查(審材外未查)。

## Finding 2
severity: minor
blocking: 否 + 只造成誤擋(該拿的沒拿乾淨),不是守衛被繞過
file: `scripts/lumos`(`_slot_strip_keys`)
引句:「out[-1] = out[-1].rstrip(" \t")」
場景:只吃標記前面的半形空白與 tab,且 `if out:` 在行首沒有前段時不吃標記後面的空白。三種寫法拿掉後與「沒標記」的同一行不等:
- 行首標記:實測 `_nodehome_strip_test_tags("[test:x] foo")` 回 `' foo'`,而 `foo` 回 `'foo'`。同一篇把 `foo` 改成 `[test:x] foo`(只加綁定)→ sig 不同,照舊被擋。sig 只對行尾 rstrip,行首空白留著。
- 標記前是全形空白:`a　[test:x] b` 拿掉後留 `a　 b`,而 `a　b` 不等。
- 標記黏在字後面又隔空白:`x[test:a] y` → `x y`,不影響;但 `foo  [test:x]bar` → `foobar` 與 `foo  bar` 不等。
這些都是「該拿的沒拿乾淨=照舊誤擋」方向,與派工詞排序一致,所以只標 minor。重現:上面三個字串丟給 `_nodehome_strip_test_tags` 與去掉標記的版本比。

## 逐項探測結果(無問題,供你確認有跑)
- 值剛好 200 字拿掉、201 字不拿;值只有反引號、``` `` ```、``` ``a`` ```、`` `a` `` 以外的多對反引號:都照留(只有整段單一對反引號且內容合格才拿)。
- 全形冒號、大寫鍵、鍵旁空白:`[TEST：x]`、`[ test : x ]` 會拿,與 slot_parse 一致。
- 值含 tab、全形空白、`=`、換行、組合字元(`é`)、中文:都留。
- 巢狀方括號:`[test:x[y]z]` 拿;`[test:x[y] b` 未閉合整段留。未閉合反引號到行尾當正文,後面的標記不拿。行內程式碼、圍欄(含 ~~~、未關圍欄)裡不拿。
- 清單符號:`-` `*` `+` `1)` `10.` `1.` 後接空白或 tab、行尾 `\r`、縮排都整行不算;`> [test:x]`、`- - [test:x]`、`|[test:x]|` 留殘字不整行丟(偏向算內容,安全方向)。`1)` 比設計〈範圍〉寫的 `1.` 多收一種,無害。
- 效能:10 萬行單行綁定 0.36s;5 萬個閉合標記 0.06s;10 萬個未閉合 `[test:` 0.03s;5 萬層 `[` 0.0s;未成對反引號 3 萬組 0.01s。皆線性,無退化。
- slot_parse 輸出對含未閉合欄位、行內程式碼的樣本與抽產生器前一致(測試 t_slot_parse_unchanged_after_scan_refactor 也在 diff 內)。
- 實作的字元集、200 字界、反引號整段包法與設計〈範圍〉第三條逐字一致。

總結:全份最高等級 minor
