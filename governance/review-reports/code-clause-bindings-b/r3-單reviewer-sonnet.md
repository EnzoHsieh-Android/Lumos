severity: blocker

# code-clause-bindings-b r3(上限輪)— 驗收 j1–j9 + 掃 delta 新洞——單reviewer

被審(凍結):`r3-snapshot.patch`(全量,1416 行)+ `r3-delta.patch`(354 行)。前輪留痕:`r2-intake.md`(j1–j9)、三份 r2 席報告。
方法:工作樹 `scripts/lumos`/`scripts/test_lumos.py` 有另一 session 未提交的改動,一律不碰。`git show HEAD:scripts/lumos`(HEAD=4186e18,與 r3-snapshot.patch 尾狀態一致)另存 `/tmp/lumos_head.py` 做行號核對;另用 `git worktree add --detach /tmp/r3review-worktree HEAD` 建乾淨副本跑測試與獨立 repro(結束後會清掉)。`python3 scripts/test_lumos.py -k clause`(89 passed)、`-k fence`(10 passed)、`-k refcheck`(14 passed)、`-k search`(130 passed)worktree 全綠,與 r2-intake 記的「clause 89、search 130、fence 10、refcheck 14」逐項對上。另用 `_load_lumos_inproc()` 對 `clause_bindings`/`_visible_lines`/`_strip_inline_markup` 純函式餵測試檔外的獨立輸入(一次性 repro,驗完即棄)。

LUMOS-IMPACT: Lumos/main..HEAD

## 九條逐一驗

**j1(三條行內可見規則收成 `_strip_inline_markup`,跟 `_visible_lines` 配對)修了但引入新洞,見 Finding 2**。`clause_bindings` 現在只呼叫這兩份共用實作、不再自己剝一次,`grep _HTML_COMMENT_INLINE_RE|_DOUBLE_BACKTICK_RE|INLINE_CODE_RE` 全檔只有這一處定義、`clause_bindings` 內文再無重複的 `re.sub` 剝碼字樣,收斂確實發生;但這個新函式本身把「先剝 HTML 註解、再剝反引號」寫死成固定順序,見下方 Finding 2。
引句:「def _strip_inline_markup(line):」

**j2(反引號在 [SN] 前面 → 原始行像條款就擋)修好**。獨立餵 `` `[S1] 沒標 `` 給 `clause_bindings`,回傳一筆 `state=untagged`(不再是 rows 空、skip 放行);`cg-r` 沙盒重放亦擋(`不認得的清單寫法` 或 `編號重複`)。ms 為空時才會進 `raw_lead` 這條安全網,`` `x` [S1] 沒標 ``(反引號成對、無截斷)這種常態走 ms 非空的正常路徑,未被誤攔,回歸測過。
引句:「if truncated and raw_lead is not None:」

**j3(字母編號限單字母帶分隔符)修好**。獨立餵 `cf. [S1] 只是引用` 得 `state=undefined, listlike=False`(不再假重複定義),`vs.`/`no.` 同理;`_CLAUSE_ENUM` 現在只吃單一 `[A-Za-z]` 加強制分隔符,兩字母縮寫不再落進枚舉分支。
引句:「★單字母且必帶分隔符★(-b r2:cf./vs. 曾被當編號)」

**j4(listlike 只認符號與帶分隔符短編號,拿掉冒號)修好**。獨立餵 `詳見:[S9] 那段`/`注:[S2] 也是引用` 均得 `listlike=False`(不再誤擋),`cg-q` 沙盒重放 PASS(`沒有條款定義行`);冒號與任意 1–3 字中文詞已從 `_CLAUSE_LISTLIKE_RE` 的分支移除,改成 `_CLAUSE_ENUM` 同款「短編號+強制分隔符」枚舉。
引句:「前面是詞或詞+冒號(規格 [S1]、注:[S1]、cf. [S1])才算散文(-b r2 兩席:冒號與任意短詞曾誤擋)」

**j5(``` 與 ~~~ 圍欄各自配對)修好,但發現同族的 delta 新洞,見 Finding 1**。`fence` 改記「開著的是哪一種」(`s[:3]`),交錯範例 `` ``` \n~~~\n- [S2] 假證據\n``` \n- [S3] 真條款 `` 沙盒重放:S2 仍在圍欄裡看不見、S3 可見且未標被擋(`cg-u` 一致);但 `_visible_lines` 這一輪順手加的「跨行 HTML 註解」偵測有獨立的新洞,見 Finding 1(與圍欄配對本身無關,是同一段程式碼裡另一條分支)。
引句:「只有同一種才能關(-b r2 外家席:兩種共用一個 toggle 會被交錯反轉可見性)」

**j6(① 圈號納入定義行與 listlike)修好**。獨立餵 `① [S1] 圈號 [manual:人看一次]` 得 `state=manual`(不再靜默 skip),`cg-s`(已有合法 `[S1]`、`① [S2]` 沒標)沙盒重放擋於 `S2(第`；`①-⑳⑴-⒇` 已進 `_CLAUSE_ENUM`/`_CLAUSE_LISTLIKE_RE` 兩處。
引句:「a. / 一、/ 十一、/ 甲) / ① 這種短編號也是清單」

**j7(已定義編號再出現在像清單行 → 擋)修好**。獨立餵「`- [S1] 已標 [manual:一次]`\n`→ [S1] 第二次定義沒標`」得 `state=duplicate, dup_lines=[1, 2]`(不再被既有定義遮掉放行),`cg-t` 沙盒重放擋於「編號重複定義」;`listlike_extra` 現在無條件記錄、不看該編號是否已在 `defined` 裡。
引句:「不管這個編號有沒有在別處合法定義,都要擋(-b r2 外家席:被既有定義遮掉而放行)」

**j8(跨行 HTML 註解整段不看)修了但引入新洞,見 Finding 1**。獨立餵 `<!--\n- [S1] 跨行註解裡的\n-->\n沒有條款。\n` 給 `clause_bindings` 回傳 `[]`(S1 不再露出),`cg-w` 沙盒重放 PASS(`opt-in 未啟用`)——這條指定的正向案例本身確實修好;但為了做跨行狀態新增的 `in_comment` 邏輯,在另一種同樣合理的輸入下會把不該隱藏的整行(甚至整份文件其餘部分)吞掉,見 Finding 1。
引句:「跨行 HTML 註解 <!-- … -->:整段不算內容(單行的由 _strip_inline_markup 剝)」

**j9(註解訂正)修好**。`clause_bindings` docstring 已把「反引號裡的內容整段遮掉再掃」改成「反引號/圍欄/HTML 註解裡的內容都不看,未閉合反引號之後不信」,與目前實作(呼叫 `_visible_lines` + `_strip_inline_markup` 兩層)一致,不再只提反引號一種。
引句:「★反引號/圍欄/HTML 註解裡的內容都不看,未閉合反引號之後不信★」

## delta 引入的新洞

### Finding 1
severity: blocker
blocking: 是——一行文字裡先出現字面 `-->`、後面才接一個未閉合的 `<!--`(兩者順序與跨行註解的「先開後關」相反),會被 `_visible_lines` 誤判成「開始一段未閉合的跨行 HTML 註解」,不只吞掉這一行(哪怕它是一條寫好 `[manual:]` 的真條款),`in_comment` 從此卡在 True、之後所有行(直到文件裡某處剛好再出現一個 `-->`)全部消失;`clause_bindings` 對這種輸入回傳 `[]`,而 `_disposal_clause_step` 前置的 `SPEC_CLAUSE_RE.search(text)` 仍在原文找得到 `[SN]` 字面,只有 rows 是空的,於是落進「計劃只在散文/標題裡提到 [SN]……視同 opt-in 未啟用」分支,rc 判 `skip`——整份計劃的條款檢查被靜默關掉,直接違反本輪自己記的「計劃有 [SN] 時任一條款定義行沒有 [test:]/[manual:] 就不得 PASS」★INVARIANT★。
引句:「"<!--" in ln and "-->" not in ln.split("<!--", 1)[1]」
file: `scripts/lumos:2547`(誤判觸發點)、`scripts/lumos:2517`(`_visible_lines` 定義)、`scripts/lumos:13490`(`SPEC_CLAUSE_RE.search` 仍找得到原文 `[SN]`)、`scripts/lumos:13505`(空 rows 落「opt-in 未啟用」分支,靜默 skip)
最小重現(worktree 沙盒已實跑):
```
text = "- [S1] 真條款 [manual:寫好了] --> 尾巴 <!-- 未閉合開始\n- [S9] 下一條也沒標,理論上該擋\n"
clause_bindings(text, {}, "python", lambda p: set(), lambda p: "")
# 回傳 []——S1(已標)與 S9(未標,理論上該擋)全部消失,_visible_lines 對這兩行都不 yield
```

### Finding 2
severity: blocker
blocking: 是——`_strip_inline_markup` 先跑 `_HTML_COMMENT_INLINE_RE.sub`(對整行字面掃 `<!--…-->`,不管反引號邊界),再跑反引號剝除;若一段用單反引號包住的字面文字裡剛好含未閉合的 `<!--`(例如示範「HTML 註解怎麼寫」的行內程式碼),而同一行後面某處(哪怕在反引號範圍之外、甚至是另一段不相干的文字)又出現一個字面 `-->`,這個非 backtick-aware 的正則會把兩者之間的所有文字(含裡面任何 `[SN]`、`[manual:]`)整段吃掉且不留痕跡——不是分類成 `untagged`/`undefined`,是連 `id` 本身都不進 `rows`,不受 j2 加的 `raw_lead` 安全網保護(該安全網只在整行 `ms` 為空時才觸發,這裡同一行還留著別的 `[SN]` 讓 `ms` 非空);若被吞掉的那個 id 原本沒標,`_disposal_clause_step` 完全不知道它存在,PASS 照樣印「✓ 全標」。
引句:「s = _HTML_COMMENT_INLINE_RE.sub("", line)」
file: `scripts/lumos:173`(執行順序:先剝註解)、`scripts/lumos:167`(`_strip_inline_markup` 定義)、`scripts/lumos:4088`(`clause_bindings` 呼叫處,j2 安全網只在 `ms` 為空時觸發)
最小重現(worktree 沙盒已實跑,含「PASS 照樣印全標」的加強版):
```
line = "- [S1] [manual:寫好了一次] 說明 `<!-- 範例` [S9] 未標的真條款 -->結尾"
clause_bindings(line + "\n", {}, "python", lambda p: set(), lambda p: "")
# 回傳 [{'id': 'S1', 'state': 'manual', ...}]——S9 完全不在清單裡(不是 undefined,是不存在)。
# 對到 _disposal_clause_step:clauses=[S1(manual)]、unt=[](S9 未標卻沒被算進去)→ 印「✓ — 1 條全標」、rc PASS。
```

## 其他觀察(minor,不算 blocking)

`_CLAUSE_LISTLIKE_RE` 對「1.[S1]」(無空白)正確走 `_CLAUSE_LEAD_RE` 的通用列表前綴字元類(`\d`/`.` 都在裡面),歸類為 `untagged` 定義行;但「1、[S1]」(數字+頓號、無空白)不同——`_CLAUSE_LEAD_RE` 的通用前綴字元類不含「、」,`_CLAUSE_ENUM` 又要求分隔符前面是字母/中文數字/甲乙,單獨的阿拉伯數字「1」配「、」兩邊都吃不到,結果落進 listlike 分支變成 `undefined, listlike=True`——`_disposal_clause_step` 仍會擋(格式看不懂不放行,方向安全),只是訊息從「未標」變成「不認得的清單寫法」,對「1、」這種中文文件常見的數字編號略顯誤導。獨立測過這個「digit+句點 vs digit+頓號」的不對稱,在 `_CLAUSE_ENUM` 早於本輪就沒收數字分支,不是本輪新增,不列為新 finding。

## 總結

最嚴重 severity:blocker(Finding 1、Finding 2)。blocking 條數:2。
