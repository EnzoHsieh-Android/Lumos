# about-code-impl-std r3(即 std-r2)架構對齊審查

審查範圍:`/tmp/about-code-impl-std-r3.md`,只審標「std-r2」的 delta——「過期守衛」節末 std-r2 段(新 helper
`note_body_hash`、三段式 stamp、`lumos about-code restamp` 子命令、83 篇存量遷移)、「#4」「#6」(std-r2 折入後版,
即目前該兩節全文)、「#10」先例條(`fusion_p` 校正)、「本案新增/修改工具清單」11 列。

判準:只判「跟本專案既有做法一不一致」,不判 bug、不判風格。major = 引入第二種做法或跨層直呼;minor = 命名/錯誤
處理不一致但結構對。（比對基準:`scripts/lumos`、`governance/eval/retrieval_eval.py`、`scripts/hooks/claude/impact-hook.py`、
既有 Projects 計劃筆記,實際 grep 現況,非讀 spec 自證。）

---

## Q1:分層依賴——有沒有跨層直呼、繞過既有邊界?

**結論:沒發現不對齊。**

- `note_body_hash(vault, rel)` 被 `cmd_impact`(#4)與 `run_doctor`(#6)兩邊共用,是模組層級自由函式,跟
  `split_frontmatter`(`scripts/lumos:101`)、`_impact_about_counts` 這類「共用工具函式被多個呼叫端使用」是
  同一種形狀,不是誰伸手進誰的內部。`_impact_about_counts(env)` 切成獨立頂層函式、不 inline 進 `cmd_impact`,
  對齊 `_impact_reverse_lookup`(`:13605`)/`_impact_contract`(`:13681`)/`_impact_bfs`(`:13719`)的既有分工——
  這點 std-r1 就已對齊(見 `r2-arch.md` Q3),std-r2 沒有改動它。
- git 完全退場後,`#6` 不再需要 `repo_root`——這跟 `Check S` 本身(`scripts/lumos:823-869`)本來就不吃
  `repo_root`、只讀 `n.fields` 是同一形狀,是收斂不是分裂。對照 `r2-arch.md` 對 std-r1 版「`repo_root` 該複用
  哪一種既有找法」的疑慮,std-r2 直接繞開了整個問題(不需要 `repo_root` 就不必挑「四種既有寫法」裡的哪一種),
  不是新增第五種找法,是把依賴整個拿掉。
- `#10` 的接線(row → `_macro()`(`governance/eval/retrieval_eval.py:266-268`)→ `verdict["pin_top3_must"]` →
  `_history_record` 的 `"verdicts": {r["split"]: r["verdict"] for r in reports}`,`governance/eval/retrieval_eval.py:499`)
  沿用既有 `fusion_p`(`:384`)/`must_pinned_count`(`:410`,raw sum 非 macro,經核對屬實)已經在走的管線;
  `gates` 字典(`governance/eval/retrieval_eval.py:570-575`)明確不碰,核對現碼位置與內容皆準確,沒有另開一條
  路徑把新指標送進 gate 或 history。這條先例引用是準確的,不算不對齊。
- hook / eval 呼叫 CLI 走 `subprocess.run([sys.executable, str(LUMOS), ...])` 吃 JSON(非 import
  `scripts/lumos` 內部函式),「hook/CLI/eval 共用單一實作」這句話因此自動成立,std-r2 沒有改變這個既有的
  process 邊界。

## Q2:命名與錯誤處理——命名、fail-open/fail-closed、訊息組裝跟既有慣例一不一致?

**結論:1 條不對齊(minor)。**

對齊的部分:
- 三段式 stamp `<誰>/<日期>/<正文 sha256 前 12 碼>` 沿用 `self_audit` 既有的 slash 分隔慣例
  (`cmd_self_audit`,`scripts/lumos:7543-7558`,寫 `<model>/<date>`),只是多加一段,分隔符與欄位語意風格一致。
- `about_hit` 只在 `True` 時才出鍵、讀側一律 `r.get("about_hit", False)`,對齊既有 `rescued`
  (`scripts/lumos:14279`)、`query_gated`(`:14288-14289`)「不同來源路徑帶不同鍵集合、消費端用 `.get()` 讀」的
  既有慣例,以及 `r.get("hop", 0)`(`:14246`/`:14276`)、hook 的 `x.get("hit")`(`impact-hook.py:358`)—— 三處
  precedent 皆核對屬實。這條 std-r1 就已對齊,std-r2 沒有改動。

不對齊(minor):`#6` 的 `warn_soft` 訊息把「怎麼辦」焊進 `head` 字串,沒有走既有的 `head`/`advice` 兩參數分工。

引句:「有 {N} 篇筆記的 about_code 標了之後正文又改過,標記可能過期(`lumos about-code restamp <節點>` 重標)」

`warn_soft(lines, head, advice=None)`(`scripts/lumos:486-497`)本身把「發生什麼」跟「怎麼辦」拆成兩個獨立參數:
分開印成兩行(`⚠ {head}` 一行,`建議: {advice}` 另一行)。本專案目前每一個既有呼叫點都遵守這個切法——`Check S`
自己(`scripts/lumos:866-869`,`head` 只講「有 N 篇……需要再確認一次:」,`advice` 另傳「重派乾淨 agent 還原審後
`lumos self-audit <node>` 重新留痕」)、`valid_under` 過期檢查(`:1116-1118`)、程式路徑存在性檢查
(`:1163-1165`)、工具鏈版本 nudge(`:1351`)皆是同款「`head` 只描述現況、`advice` 單獨給下一步指令」的兩段式。
std-r2 描述的 `#6` head 直接把 `` `lumos about-code restamp <節點>` `` 這條操作指令焊進 head 句子裡,`advice`
參數等於沒用——功能上仍會印出來,但跟五個既有呼叫點的兩段式切法不一致,接手的人看到的訊息形狀跟其他 Check
不同。

## Q3:第二種做法——有沒有跟既有機制並存的平行實作,或悄悄漏掉既有防線?

**結論:2 條不對齊(1 major、1 minor)。**

對齊的部分(先講清楚哪些不算違規,避免誤讀):
- `note_body_hash` 只雜湊 `split_frontmatter(text)[1]`(正文,不含 frontmatter),跟本專案既有 3 處 sha256
  用法(`_sha256_file` 整檔位元組 `scripts/lumos:3319`;`anchor verify`/`anchor approve` 同為整檔位元組
  `:10468`/`:10500`)不同形——經 grep 確認,**本專案目前沒有「只雜湊 frontmatter 之外」的先例**,這是全新形狀。
  但 spec 有明講理由並留痕:「跟 Check S(日期制)不同形——r1 架構席『第三套機制』那條在這裡再次被推翻,理由是
  兩輪五席實證日期制表達不了順序;留痕,不再折回」(line 333-334),也解釋了為什麼要排除 frontmatter(「about_code
  自己就在 frontmatter 裡,重標不會自我過期」)。這是「有記在案的例外」,不算不對齊,不列為 finding。

不對齊(major):`note_body_hash` 沒有指名沿用既有「用 vault+rel 重讀一篇筆記原文一律 `utf-8-sig`」的慣例。

引句:「新 helper `note_body_hash(vault, rel)`(讀檔→split→hash;★無快取,無 git,無子行程★)」

本專案「用 `vault`+`rel` 重讀一篇筆記原文」目前至少 15 處呼叫點(如 `scripts/lumos:1137`、`1230`、`1268`、
`1435`、`1760`、`2864`、`6249`、`7161`、`8417`),全部走 `(env.vault / rel).read_text(encoding="utf-8-sig")`;
其中 `:6218` 甚至留了註解「-sig: 同 load_vault 慣例,BOM 不外洩進輸出」;`load_vault` 自身(`scripts/lumos:201`)
也是同款讀法,明講理由「-sig: BOM 檔也偵測得到 frontmatter」。BOM 在這個 repo 是踩過的真坑——`utf-8-sig`
全檔出現 29 次,且有 `reinject_bom_crlf` 等既有測試專門測 BOM 場景(`scripts/test_lumos.py:10806` 起)。
spec 只寫「讀檔→split→hash」,沒指名編碼——若字面實作用預設 `utf-8`(或 `open()` 不帶 `-sig`)讀檔,帶 BOM 的
筆記 `text.startswith("---")` 會判 `False`,`split_frontmatter`(`scripts/lumos:101-108`)回傳 `(None, text)`,
`body` 會變成「整份原始檔內容(含 frontmatter)」——正文雜湊就會把 frontmatter 也算進去,直接打穿這一節自己
宣稱的設計保證「about_code 自己就在 frontmatter 裡,重標不會自我過期」(spec line 327)。一旦某篇筆記帶 BOM,
任何合法的 frontmatter 改動(包含 `lumos set`/`append`)都會讓正文雜湊跟著「看起來變了」或反過來讓真正的正文
改動被 frontmatter 差異蓋掉,產生靜默誤判。這不是風格問題,是把本專案自己踩過、寫進 29 處程式碼的 BOM 防線,
在這條新讀檔路徑上悄悄漏掉,等於是給「讀一篇筆記原文」立了第二套不保證跟既有讀法同結果的做法。

不對齊(minor):`#6` 的過期掃描沒有比照既有「跳過 `status: stale/superseded` 節點」的慣例。

引句:「掃全部 type(不只 system),有 `about_code_stamp` 的節點算 `note_body_hash` 比對 stamp 第三段」

`#6` 明講訊息格式「照 Check S 實際逐行寫法」,但 Check S 本身在掃描迴圈一開始就先排除
`status in ("stale", "superseded")` 的節點(`scripts/lumos:832`)才往下判過期。這不是 Check S 獨有的個案:
同一份 `scripts/lumos` 裡至少還有 4 處同款過濾(`:588`、`:884`、`:1476`、`:6043`,皆排除
`stale`/`fail`/`superseded` 狀態的節點才繼續做「這篇是不是該重新確認」一類的軟提醒),是本專案「已經被取代/
判定失效的筆記,不再對它做新鮮度提醒」的既有共識。std-r2 這節只說「掃全部 type」,完全沒提要不要排除
`stale`/`superseded` 狀態——如果字面實作,`doctor` 會對已標記為過時、作廢的筆記照樣喊「about_code 過期,請
restamp」,對照既有 5 處慣例是不一致的行為,也違背了「照 Check S 逐行寫法」這句話本身隱含的「連判準一起抄」
的預期(目前只抄了訊息格式,沒抄過濾條件)。

---

## 統計

不對齊共 3 條,其中 major 1 條(Q3:`note_body_hash` 未指名 `utf-8-sig` 讀檔慣例)。無 ⚠ 項——三條找到的不對齊
在本專案既有 code 裡都有明確、可重現的對照證據,不屬於「判不準」。
