severity: minor

**finding 1**

severity: minor
blocking: 否 — 兩份字表內容目前一致,也有指紋與釘值測試守著,但之後只改一份就會悄悄走歪。
引句:「_NOGO_NEG_HEADER_RE = re.compile(r"^(?:不做|不支援|不提供|不處理|不含|不包含|不實作|不開發|暫不|本期不|本版不|這一版不|不在本期|排除"」
對照:scripts/lumos: `scripts/lumos:7926`(`_NOGO_NEG_PREFIX_RE`,同一組否定片語);既有同類的單一源寫法如 `scripts/lumos:5620`(`NEG_LEXICONS` 一張字表)。
判定理由:`_NOGO_NEG_HEADER_RE` 把 `_NOGO_NEG_PREFIX_RE` 的整串片語逐字複製一份,只多接 `\s*[:：]`。同一組詞維護了兩處,這是在新程式碼內部造出第二份字表,風險是日後漂移。改法很小:先定義一個片語字串常數,兩支正則都用它組出來。這屬風格與維護性問題,不是跨層或引入第二種做法,所以只列 minor。

**其餘逐項判定,結論都是對齊,不列 finding**

- **不共用既有否定字表的理由成立。**
  - `NEG_LEXICONS`(`scripts/lumos:5620`)認的是「某符號已不存在」。
  - `_NS_NEG_*`(`scripts/lumos:33065` 起)認的是「還沒做」的待定詞。
  - `_REJ_NOGO_RE`(`scripts/lumos:19373`)只要子句裡出現「不做」就算,不看是否在開頭,而且用在查重舊否決,不是風險放行。
  - 新字表要的是「整句以否定開頭」,而且放過的是風險判定,語意不同,字表理應更窄。程式註解寫的理由屬實。
- **新切句正則不共用 `_NS_NEG_SEG_CUT_RE`(`scripts/lumos:33091`)的理由成立。**
  - 既有那支切「、」與破折號,不切「但、而是、and、but」。
  - 新語意需要切在轉折詞,才能擋「不做 X 但要做 Y」。
  - 兩支都是 `re.compile` 加 `.split` 的同一種寫法,沒有引入新手法。
- **`_ns_indent` 加 `fullwidth` 參數是對的方式。**
  - 這是擴充既有單一實作:預設值維持舊行為,筆記格子兩處呼叫不受影響;新程式沒有另寫第二套縮排計算。
  - 整段只多了新的 `_nogo_line_says_nogo`,並移除原本自寫的 `_nogo_width`,反而少了一份重複。
  - 規格閘的函式呼叫定義在檔案後段的筆記形狀函式,這是同一支檔案內的 helper 重用,沒有跨層。
- **兩層版本號與釘值測試與既有路線一致。**
  - 指紋進 `_door_rule_fingerprint`,再由 `t_door_rule_version_pin`(`scripts/test_lumos.py:59802`)釘住,這就是既有 `_DOOR_RULE_VERSION` 路線。
  - 新增的 `_NOGO_SKIP_LOGIC_VERSION` 加原始碼雜湊釘值是在既有路線上多一層,用來覆蓋指紋無法收進的函式原始碼,不是另一條平行機制。
  - 專案裡沒有別的 `getsource` 加雜湊的釘值先例,這是新增的形式,但範圍限在不做節,理由寫在註解與測試 docstring 裡。
  - `_DOOR_RULE_VERSION` 沒升:註解寫「2=2026-10-14 起」,同日的未釋出變更併在版本 2 裡,可以接受。

不對齊共 1 條(minor 1 條),major 0 條。
