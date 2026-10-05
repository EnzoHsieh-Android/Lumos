severity: major

# 代碼審 r2 邊界席(極端輸入)

做法:用 importlib 載入 /Users/enzo/harness/lumos-rtb3/scripts/lumos,對 `_nodehome_strip_test_tags` 跑 31 組輸入(核取方塊、`10)`、`+`、tab、全形空白、不換行空白、\r、整段只有標記、圍欄標記行、圍欄沒收尾、多行續行縮排、全空白行、單獨「-」),再對 `_ns_tr_gone_viol`、`_ns_tr_test_viol` 實跑。清單符號、空白、\r、圍欄這幾類都過關:`- [ ] [test:x]`、`- [x] [test:x]`、`10) [test:x]`、`+ [test:x]`、tab 與全形空白前的單獨標記行都判成「沒變」,圍欄內的標記與圍欄標記行上的標記都判成「有變」,原本就存在的單獨「-」行拿掉別行標記後仍保留。這些沒有問題。

## F1 豁免的前提不成立:[test-gone:] 與合約行、條款行的 [test:] 不會被 test_refs 擋,英文句子仍可藏進去

severity: major
blocking: 是——內容有變卻判沒變(守衛被繞過),而且直接推翻 r1 通才席修正的前提「test_refs 會擋英文說明」。

引句:「那道會在同一段推送裡核對新寫的測試名真的存在,一句英文說明包成 [test:…] 會在那裡被擋」

事實:`_nodehome_tag_exempt` 只看 test_refs 是不是 block,但 test_refs 並不會對所有被拿掉的標記核對存在。
1. `[test-gone:名稱]` 只驗名稱非空、非佔位字、測試不存在(`_ns_tr_gone_viol`),不存在才是正常情形,所以一句英文永遠過。
2. 合約行(kind contract)與條款定義行(kind clause)的 `[test:]` 在 `_ns_tr_test_viol` 裡直接 `return None`(只免判存在),英文句子同樣過。
而 `_nodehome_test_tag_value_ok` 的字元集允許英數、空白、逗號、句點、括號,200 字內的一句英文整句符合。

最小重現(rc 看輸出,三行都當場翻紅):
```
python3.14 - <<'PY'
from importlib.machinery import SourceFileLoader
import importlib.util
l=SourceFileLoader("lm","/Users/enzo/harness/lumos-rtb3/scripts/lumos")
s=importlib.util.spec_from_loader("lm",l); m=importlib.util.module_from_spec(s); l.exec_module(m)
f=m._nodehome_strip_test_tags
base="WHY: 舊決定\nRULE: x"
new=base+"\n[test-gone:Never delete the audit log, compliance requires 7 years retention]"
print(f(base)==f(new))                                   # True:判沒變
nms,_=m._test_names_of(m.slot_parse("[test-gone:Never delete the audit log, compliance requires 7 years retention]"),"test-gone")
print([m._ns_tr_gone_viol("r",1,n,lambda n:("no","")) for n in nms])   # [None, None]:test_refs 不擋
print(m._ns_tr_test_viol("r",1,"INVARIANT","contract","Never delete the audit log compliance",set(),lambda n:("no","")))  # None
PY
```
結果:True / [None, None] / None。一篇家節點新增一整句英文規則包在 [test-gone:…] 或合約行 [test:…] 裡,[S12] 判沒寫說明,test_refs 也不擋。
file: `scripts/lumos:29770`(`_ns_tr_gone_viol`)、`scripts/lumos:29756`(`_ns_tr_test_viol` 對 kind 非 plain 直接放行)

## F2 空白壓平套在每一行,連縮排的改動都判沒變

severity: minor
blocking: 否——被放過的只有縮排與連續空白,不是新增文字;但它是「該算內容有變卻判沒變」,且影響範圍超出標記本身,只有豁免開著才發生。

引句:「line = " ".join(line.split())」

重現:`f("- a\n  - b") == f("- a\n- b")`、`f("para\n\n    code line") == f("para\n\ncode line")`、`f("a  \nb") == f("a\nb")` 都是 True。清單巢狀層級、縮排程式碼區塊變成散文、兩個空白的硬換行,改了都不算有變。不換行空白(U+00A0)也被當空白壓成一般空格(`f("a b")==f("a b")`)。零寬空白 U+200B 不被壓,判有變(一致,沒洞)。
file: `scripts/lumos:26895`

## 其他極端輸入(確認無洞,不計 finding)

引句:「if k and (not line.strip() or _NOTELINES_BARE_LIST_RE.match(line)):」

- 標記前緊貼文字(`a[test:x] b` 對 `a b`)與表格格(`| 1 | [test:x] |` 對 `| 1 |`)分別判沒變與有變:前者合理,後者是誤擋方向,不是繞過。
- `a\n[test:x]\nb` 對 `a\n\nb` 判有變(誤擋方向,可接受)。
- 未收尾圍欄(`` ```\n[test:x]\ncode``)標記行在圍欄內,不被拿掉,判有變,正確。

總結:全份最高等級 major
