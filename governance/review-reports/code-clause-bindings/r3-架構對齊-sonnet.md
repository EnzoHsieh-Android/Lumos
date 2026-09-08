severity: major

# 架構對齊審查——code-clause-bindings(r3,上限輪,sonnet)

被審(凍結):全量 `governance/review-reports/code-clause-bindings/r3-snapshot.patch`;delta `governance/review-reports/code-clause-bindings/r3-delta.patch`。
只判第 2 輪折入(delta)有沒有引入「跟這個專案既有做法不一樣」的寫法,以及前輪(r2)兩條 minor 折入後對不對齊。不找 bug、不評風格。前輪本席:同目錄 `r2-架構對齊-sonnet.md`。

LUMOS-IMPACT: Lumos/main..HEAD

---

## 1. 分層與依賴方向

**判定:對齊(r2 minor#1 已折平,未發現新的分層違規)。**

檢查點①——對照 `_loop_status_disposal` 既有「擋下…return 2」用法錯誤路徑(file: `scripts/lumos:13559-13563`):G3 那條 rc2 短路是「攔例外的地方」跟「真的 return 2 的地方」在同一層(`_loop_status_disposal` 自己 try/except 後直接 print+return 2)。折入後計劃讀不到這條,走的是「helper 印訊息、回傳 sentinel;呼叫端把 sentinel 翻成 return 2」:

> 引句:「print(f"擋下:--spec 指的文件讀不成文字({e.__class__.__name__}),確認路徑對不對:\n    {spec}", file=sys.stderr)」

呼叫端:

> 引句:「if _cl == "abort":」

這不是新的跨層違規——`_disposal_clause_step` 折入前就已經是「回傳字串狀態、呼叫端決定下一步」的 helper 形狀(原本回 "skip"/"fail"/"ok" 三種,由 `_loop_status_disposal` 逐一判斷處置),這裡只是多一種 "abort" 值,helper 沒有自己 `return 2`、沒有繞過呼叫端動 process exit,真正決定 rc 的仍是最外層那一行 `return 2`。訊息措辭(「擋下:」開頭、走 stderr、「確認路徑對不對:\n    {spec}」句型)跟 G3 那條(file: `scripts/lumos:13562`)幾乎逐字相同,差別只在「讀不到」→「讀不成文字」與多帶 `UnicodeDecodeError`——這個雙例外組合不是新發明,同一函式的 quote-check 步驟(file: `scripts/lumos:13684-13688`)本來就用 `except (OSError, UnicodeDecodeError)` 讀文字檔,是既有慣例的延伸,不是另立一套。★r2 兩條 minor 之一「計劃讀不到的處置跟 G3 不一致」——已對齊。★

檢查點②——對照 `_roster_kind` 三值語意(code/design/None)與既有消費端怎麼處理 None:本專案既有兩種既有處理方式並存——`_roster_observe`/`_roster_next_payload`(advisory 情境)對 None 顯式分支、當「無法判定,跳過對帳」處理;`_roster_kind(loop_id) == "code"` 直接比較(file: `scripts/lumos:7489`、`scripts/lumos:7558`),None 不特別處理、自然落進「非 code」分支。折入前的 `_disposal_clause_step` 仿第一種(`if kind is None: ... return "skip"`),這正是 r2 finding#2 指出「docstring 沒算進去的第五種 skip」的來源。折入後改採第二種既有寫法:

> 引句:「if _roster_kind(loop_id or "") == "code":」

None 不再走獨立分支,直接落進「當設計審繼續往下判」,並附註解說明理由:

> 引句:「# _roster_kind 回 None(code 開頭但不是 code-)一律當設計審:fail-closed,免得取個 codeX 的編號就繞過(r2 外家席實跑抓到)」

這是本專案原本就有的兩種既有分岔之一(advisory 用顯式 None 分支跳過;enforcement 用直接比較讓 None 落進預設分支),不是自造第三種——`_disposal_clause_step` 是閘(enforcement)不是觀測(advisory),選 enforcement 那一種既有寫法是對的層級選擇,也跟 Q2 的 docstring 核對一致(見下)。

- severity: minor(r2 原評級,現已折平)
- blocking: 否(已解決)

---

## 2. 命名與錯誤處理

**判定:仍不對齊(1 條本輪新增,minor)。**

r2 minor「docstring 跳過種數」:

> 引句:「skip 四種:①凍結/回放模式(spec_sha_override 有值,對凍結 sha 判、不重讀活檔)②迴圈類型是 code(loop id 前綴 code-,同 _roster_kind;」

跟實作核對(file: `scripts/lumos:13446-13448`):現在真的只有四條 skip 路徑(凍結回放/code 迴圈/cutoff 不回溯/無 [SN])——原本被點名「沒編號進去」的第五種 `kind is None` skip,已經在 Q1 檢查點②被整支拿掉(不再是獨立 skip,併入②繼續往下判)。不是靠補一句文字把 docstring 湊到五種,而是讓程式碼行為回到跟 docstring 講的一致(四種)。**已對齊。**

- severity: minor(r2 原評級,現已折平)
- blocking: 否(已解決)

本輪新增(minor,同一類「自我文件跟不上新分支」問題,這次出現在另一段列舉):折入時為了修 Codex 挑出的「勾選框零條款照過」洞,新增了一個 fail 分支——

> 引句:「計劃裡有 [SN] 字樣但沒有一條在行首定義({len(undef)} 個只在行內/範例出現);看不懂的寫法不放行——條款要寫成 `- [S1] …`/`### [S1] …`/表格列/`- [ ] [S1] …`」

但同一函式 docstring 那句列 fail 理由的地方(file: `scripts/lumos:13449`,「設計審審材不是 .md、首筆帳 ts 讀不動、測試索引建不起來 → fail(驗不了≠通過)」)沒有把這第四種 fail 理由算進去——跟 r2 finding#2 是同一種病(新增分支,docstring 枚舉沒跟上),只是這次出現在 fail 的列舉而不是 skip 的列舉,且是這一輪折入本身新產生的,不延續 r2 舊帳,所以不算「r2 兩條折入未對齊」的一部分,是本輪新增的第三條。

- severity: minor
- blocking: 否

`cmd_handoff` 其他錯誤訊息三段式核對:函式已有明文慣例——

> 引句:「# 人讀三段式:發生什麼 → 為何在意 → 下一步指令獨立一行」

新增的 index_error 訊息:

> 引句:「print(f"驗收條款:測試索引建不起來({_cc['index_error']}),算不出各條狀態;先修 .lumos/config.json 的 test 設定,再 lumos spec-trace {plan_name.split('/')[-1]}")」

沒有拆成三行獨立列印,但這條插在檔案狀態清單之後、通用「為什麼在意:」總結之前,屬於函式體裡的一則獨立觀測訊息(跟旁邊「提醒:逐字稿有 {…} 行讀不動,已跳過」同一類單行寫法,而不是函式開頭那種「找不到節點/不在 git 裡」的硬擋錯誤),跟同函式裡其他非阻斷性單行提示的既有寫法一致。且句型直接沿用同一錯誤(索引建不起來)在 `cmd_spec_trace` 的既有訊息(file: `scripts/lumos:4242`,「提醒:測試索引建不起來({berr}),綁定欄全印「索引不可得」;先修 .lumos/config.json 的 test 設定」),只是多補一句指路指令——不是另立新句型。**已對齊。**

- severity: minor
- blocking: 否

---

## 3. 第二種做法

**判定:不對齊(1 條本輪新增,major)。**

本專案對「反引號/程式碼圍欄內容不算」這件事有明確的單一實作與反覆審計歷史:`_visible_lines`(file: `scripts/lumos:2504-2520`)是「全檔唯一的 fenced-code 判定實作」,`INLINE_CODE_RE`(file: `scripts/lumos:162`)是全檔唯一的 inline-code 正則,`_search_visible_lines`(file: `scripts/lumos:2536-2550`)用 `INLINE_CODE_RE.sub("", ln)` 把行內反引號內容剝掉——檔案自己的註解明講過為什麼所有呼叫端都必須共用這一份(file: `scripts/lumos:7380`,「候選收集與 cmd_search 主迴圈同用 _search_visible_lines/nfc 原語,不另寫剝碼/切詞第二份」),歷史上就是因為各處自己寫一份反引號/圍欄正則才踩過「幽靈圖譜邊」「整段散文被吞」等真事故。

折入後,`clause_bindings` 為了修 r2 單reviewer 抓到的「同一行『真條款 + `[S9] 範例`』讓閘 FAIL」這個 blocker,新寫了一個獨立正則自己剝反引號:

> 引句:「line = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), raw)   # 反引號裡的一律是範例:整段遮掉(長度不變,行號/位置照舊)」

這支 `r"`[^`]*`"` 跟 `INLINE_CODE_RE = re.compile(r"`[^`\n]*`")`(file: `scripts/lumos:162`)是同一件事的第二份正則(逐行處理時 `\n` 排除與否沒有實質差異),而且完全沒有經過 `_visible_lines`/`_search_visible_lines`/`INLINE_CODE_RE` 任何一個既有原語,是這一輪折入自己新造的一套。就算堅持要「遮蔽保留長度」而非「剝除改變長度」,`INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), raw)` 一行就能重用既有正則達到同樣效果,不需要重寫比對規則本身。這正是本檔案史上已經反覆栽過的那個坑,也是這次三問清單裡點名要對照的既有慣例——新碼確實是第二套。

- severity: major
- blocking: 是

---

## 小結

不對齊共 2 條,其中 major 1 條。
