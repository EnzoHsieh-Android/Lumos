severity: major

審查結論:一般 guard kill 的行為沒有被改壞,但有一條 major(計劃正文分段沒有排除實際計劃裡的審計修正紀錄),另有三條 minor。實際跑了 `-k choice_layer` 和 `t_choice_compile_swap_keeps_other_plat`,37 支加 2 支全綠,所以現有測試沒有覆蓋下面這幾條。

**追過的呼叫端,沒有發現回歸**
- `_kill_target`、`_kill_revert` 取代逐支 guard kill 的還原與路徑檢查:順序、錯誤字樣、revert 失敗後 `break` 都跟原本相同。唯一的行為差異是一般 guard kill 也開始擋 `.git` 底下的檔,這是刻意的。
- `_CHOICE_COMPILE_UNVERIFIED` 改成 `object()`:所有使用處(`scripts/lumos:29504`、`29523`、`29558`、`29571`)都先做 `is` 判斷才拆 tuple,沒有漏。
- `_kill_cap` 的 `keep_max` 預設仍是 20,舊呼叫端(合約測試閘)只多一行 `[kept lines cut]` 標記。
- 推送閘子原因拆開:擋不擋、rc、回報上限(只有抽中的才進原因)、`_CHOICE_PUSH_REASONS` 的順序都沒變。`scripts/lumos` 裡沒有其他地方依賴字面 `"存活"` 原因。`_choice_push_verdict` 只有一個呼叫端,且有帶 `aux`。

**圖譜鏡頭**
- 固定席(guard-kill、bound-tests-gate 等)的 `★INVARIANT★` 是 rc 優先序與 `--json` 純度。`_kill_run`、`_kill_cap` 的簽名只是多了帶預設值的參數,這些不變量沒被碰到。
- 一般 guard kill 現在也擋 `.git` 底下的檔,這個行為變動沒寫進 `guard-kill` 節點,但方向正確。

---

severity: major
blocking: 是
`scripts/lumos`:`_CHOICE_LAYER_NOT_BODY`(patch 的 `_choice_plan_sections` 附近)。計劃正文排除審計修正紀錄,但判斷是整段標題逐字相等,不是前綴比對。repo 裡實際有 `## 審計修正紀錄(lumos-design-loop)` 6 份、`## 審計修正紀錄(r1)` 5 份、`## 審計修正紀錄（design-loop，…）` 1 份(全形括號)。這些段落會被收進「計劃正文」,後果有兩個:
- 第 2 層判讀可以引審計員的批評句當「計劃寫了」的依據。
- 第 1、4 層的 `deps_sha` 含這段,每次審計折入都讓判讀變「待複核」。

專案自己的 `_FOLD_AUDIT_RECORD_RE` 用 `審計修正紀錄.*` 前綴比對(`scripts/lumos:69147`),這裡沒共用。
最小重現:

```
t="---\na: 1\n---\n# T\n## 範圍\n正文A\n## 審計修正紀錄(r1)\n審計說: 會誤判\n## 驗收條款\n[S1] x\n"
m._choice_plan_sections(t)
```

回傳裡含 `('〈審計修正紀錄(r1)〉','審計說: 會誤判')`,但 `〈驗收條款〉` 被排除。測試只用了剛好叫 `## 審計修正紀錄` 的計劃,所以抓不到。
引句:「_CHOICE_LAYER_NOT_BODY = ("驗收條款", "預期值表", "審計修正紀錄")   # 計劃正文不含的二級節(〈用詞〉計劃正文)」

severity: minor
blocking: 否
`scripts/lumos`:`_choice_push_fix`。待複核提示是用 `any(...pending...)` 套在所有原因上,不只存活子原因。上一輪有判讀、現在變成「跑不出結果」「缺紀錄」「過期」的行,只要判讀的依據變了,就會在那些處置句後面多出「計劃改過,處置完這一批後重跑 choice-layer --template 複核」。我拿 `pending=True` 的 seg 直接呼叫 `_choice_push_fix("跑不出結果", …)` 和 `("缺紀錄", …)`,兩者都帶出這句,是錯誤指引。
引句:「fix += ";計劃改過,處置完這一批後重跑 choice-layer --template 複核」

severity: minor
blocking: 否
`scripts/lumos`:`_choice_plan_sections`。第一個標題前有文字、而且接著出現一級標題時,兩段都叫 `〈前言〉`:一級標題把 `stack` 清空後 `seen["〈前言〉"]` 才記到 1,初始名稱沒有登記。我用「導言文字 / `# 標題` / 標題下一句」跑,回傳兩筆同名 `〈前言〉`。`dict(sections)` 會吃掉前一筆,於是引前一段的 quote 被誤判「引句不在 〈前言〉 裡」,`deps_sha` 也漏算那一段。
引句:「stack, name, buf, out, seen = [], "〈前言〉", [], [], {}」

severity: minor
blocking: 否
`scripts/lumos`:`_choice_kill_survivor_list` 用跑之前算好的 `res`。run 中途因合批編譯 `on_swap` 換過候選的行,`res["lines"]` 裡還是舊壞法。清單會印舊的型錄列號,而且 `_choice_nsha` 給的是舊 `new_sha`。這樣讀判讀(`ev["new_sha"] != new_sha`)和覆蓋分類(cov_sha 含 `new_sha`)都對不上,剛判存活的那一行顯示「未分類」。只影響 choice-kill 收尾那份清單,不影響擋不擋。這條沒有實際跑出來,是讀 `on_swap` 只複製 `x`、沒回寫 `res` 得出的。
引句:「xs = _choice_layer_survivors(sc)」

**議題 13 換候選後保留其他平台的列(可能是設計取捨,沒有標等級)**
`on_swap` 現在保留前面平台組的舊列。那些列是舊壞法在平台 A 跑出的結果,卻會跟新壞法在平台 B 的列合起來判。`killed` 一定是決定性的,舊列不會造成假殺掉。但「survived」可能是新壞法從未在 A 跑過的結果;偏保守,只會多要處置。現有測試只斷言「列留著」,沒覆蓋這個語意。

**效率:沒有問題**
`_choice_push_segs` 對所有有壞法的行都算 `_choice_seg_fill`。我讀了 `_choice_cov_sha_fn`,它只是雜湊加一次樹查詢,沒有昂貴的 I/O,所以不構成上一輪點名過的「只算存活行」問題。

總結:最高等級是 major。
