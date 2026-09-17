severity: clean

**問一:剝括號走 `link_target`,合不合慣例——對齊**
`_plan_system_links` 改成 `link_target(x) for x in as_list(...)`(scripts/lumos:4937),跟 `link_target` 在本檔其他呼叫端的慣例完全一致:先 `as_list` 攤平、再逐項 map 過 `link_target`,例如 scripts/lumos:1128 的 `{resolve(link_target(a)) ...}`、scripts/lumos:11380-11381 的 `{env.resolve(link_target(x)) for x in as_list(n.fields.get("plan_refs"))}`、scripts/lumos:10238 同款。原本自刻的 `re.sub(r"^\[\[|\]\]$", ...)` 加上迴圈裡再手動 `lk.split("|",1)[0].split("#",1)[0]` 是第二套剝括號邏輯,r3 拆掉自刻邏輯改呼叫既有函式,是往「單一事實來源」收斂,不是引入新做法。
引句:「[[…]]/別名/錨點/引號一律交給既有 link_target(代碼審 r2/r3:別自己再刻一份剝括號)」

**問二:`_TRIGGER_WORDS` 用 generator 推子集,順序會不會被破壞——對齊**
`_TRIGGER_WORDS = ("若啟用", "當", "在", "若")`(scripts/lumos:4655)註解寫「長的先比」,這個順序只在 `next((w for w in _TRIGGER_WORDS if b.startswith(w)), None)`(scripts/lumos:4657 上方那行,取第一個匹配)那種「取首個命中」的場景才有意義。r3 新增的 `hard = tuple(w for w in _TRIGGER_WORDS if w != "在")` 只用在 `any(rest.startswith(w) for w in hard)`(scripts/lumos:4694),`any()` 不在乎順序、只在乎有沒有命中,而且 filter 是就地過濾不重排,產出順序仍是 `("若啟用", "當", "若")`,跟原本手寫常數字面值一致。從常數推導也讓「加新觸發詞要不要同步改這行複合判準」不再需要人工記兩處,是收斂不是分裂。
引句:「子集從 _TRIGGER_WORDS 推,不另抄」

**問三:`rest.split("應", 1)[0]` 這種「切到第一個關鍵字」寫法,本檔有沒有先例——對齊**
`maxsplit=1` 取 `[0]`(或 `[1]`)在本檔是慣用手法,如 scripts/lumos:5798 `state.split(":", 1)[0]`、scripts/lumos:4487 `tg.split("/", 1)[1]`、scripts/lumos:20967 `diff_range.split("..")[0]`,都是同一種「找第一個分隔字元/詞、取前段或後段」的寫法。r3 的 `head = rest.split("應", 1)[0]` 屬於同一族,沒有引入新句法。
引句:「只有「在…應」之間還有分隔才算條件句」

**問四:測試 ⑦⑧ 寫法跟同支測試其他 check 一致嗎——對齊**
⑦⑧ 沿用同函式裡 ①–⑥ 的 `check("<編號+一句話>", <bool 條件>, <證據切片>)` 三參數呼叫慣例,證據都是 `r.stdout[-N:]` 切尾;⑦用 `r7.stdout[-500:]`、⑧用 `r8.stdout[-400:]`,跟旁邊 ⑤ 用 `-500:`、⑥ 用 `-400:` 的長度選擇也對得上(有多個斷言用長一點、單一斷言用短一點)。案例命名 `_sg_plan(kg, "列舉", ...)`、`kg / "Projects" / "別名_計劃.md"` 跟 ③④⑥ 的 `_sg_plan(kg, "字串", ...)`、`p2 = kg / "Projects" / "括號_計劃.md"` 同一套建計劃檔手法。

不對齊共 0 條,其中 major 0 條。
