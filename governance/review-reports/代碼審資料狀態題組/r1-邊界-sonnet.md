severity: blocker

# 審查範圍與方法

外部投稿審查,鏡頭=邊界可執行(立場:為極端輸入——空、單一、超大、剛好卡在界線上——發聲)。逐節讀完 `docs/lumos-toolchain-knowledge/Projects/代碼審資料狀態題組_計劃.md`(與臨時檔 ds-r1.md 逐字比對,`diff` 確認完全相同)。對照程式碼:`scripts/lumos` 的 `_STACK_QUESTION_SPECS`(20018)、`_stack_key_for_file`(20221)、`_stack_applicability`(20281)、`_pitfall_diff_collect`(26030)、`_pitfall_diff_mode`(26218)、`_dispositions_template`(31764)、`_dispositions_verdict`(31649)、`_is_code_file`(6199)。確認 `scripts/test_lumos.py` 目前沒有任何 `t_data_questions_*` 測試(功能尚未實作,純設計審)。另外對本 repo 最近 20 個動到 `scripts/` 的提交做了逐行觸發字掃描(方法與數字見 F4)。

## 現況節

已讀,無 finding。三句程式行為宣稱(棧別題按副檔名分棧且不看分級、風險型樣命中即 high、業務類追問只在 `pitfalls <md>` 印不在 `--diff` 印)逐一在程式碼查證屬實:
- `_pitfall_tier`(25875):`if claims: return "high"`,與 `_STACK_QUESTIONS_GATE_VALUES`/`_dispositions_verdict` 的 gate 判斷各自獨立,分級確實不看 stack_questions。
- `_PITFALL_QUESTIONS`(業務類追問)只在 `cmd_pitfalls` 的 `md is not None` 分支(26522、26529)出現,`--diff` 分支(26496 `return _pitfall_diff_mode(...)`)之前就已經 return,不會印。
- 工具鏈主程式 `scripts/lumos` 本身就是「沒有副檔名、首行 #!」的腳本——這點下面 F2/F3 會指出它反而是本計劃最大的邊界案例來源,不是無關細節。

## 設計節(1–8)

見下方 findings F1–F4、F7。其餘子句(1、3、5 的標籤決定部分已併入 F7 討論)已讀無另外 finding。

## 驗收條款 S1–S7

逐條可否寫成先紅後綠測試的結論併入對應 finding:S1(可寫,但只覆蓋窄案例,見 F3)、S2(可寫,現有 `_stack_changed_ok`/`_PITFALL_DIFF_TEST_PAT` 機制已驗證對其他棧有效,無 finding)、S3(可寫,但字面實作會翻紅,見 F1——這是本次最重的一條)、S4(可寫,且是必要的防呆,現有 `_stack_key_for_file` 的 `ext if ext in _STACK_PERF_QUESTIONS else None` 邏輯若直接加 `data` 鍵就會撞,S4 抓對了,無 finding)、S5(觸發字清單未定義,寫不出來,見 F4)、S6(可寫,`_dispositions_verdict`/`_codeloop_read_dispositions` 是通用機制,無 finding,但要留意 gate=high-only 見 F5)、S7(可寫,但字面重用現有印法會失敗,見 F7)。

## 回退節

已讀,無 finding。退回範圍(拿掉 `data` 鍵、七題、收集段、行數門檻例外)與程式碼裡新增內容的邊界一致,沒有找到會漏拿掉的殘留點。

## 實務隱患節

已排除三類的理由都站得住(不碰付款/外部服務/只加題目與收集邏輯)。自我治理類★命中★的判斷正確,但下方 F5/F6 指出這條僅有的逃生口(`na`/`gate`)在 `high-only` 模式下會變成「目標情境本身就問不到」而不是「答了但被放行」,以及既有死結被放大的程度比一行補注更嚴重。

## 最小實驗、撤除條件節

已讀,無 finding。REVISIT 日期與撤除條件(RETIRE-IF)都寫了可回頭驗的判準,格式符合鐵則四。

## 誠實界線節

已讀,交叉引用 `[[Issues/沒有圖譜的專案答不完表態題]]` 核對存在且內容與 spec 摘述相符(見 F6)。

---

## F1 「data」跨檔彙總行數會撞到既有行數門檻全表適用分支,直接推翻 S3 與設計點 4

severity: blocker
blocking: 是(照字面實作會讓 S3 的測試翻紅,且是設計本身明講要避免的失效模式)
引句:「其他棧超過門檻全表適用的規則照舊,資料狀態題組只看觸發字」

`_stack_applicability(lines_by_stack, threshold)`(scripts/lumos:20281)對每個棧鍵各自檢查 `over = len(raw_lines) > threshold`(20292),`threshold` 是單一數值,來自 `.lumos/config.json` 的 `stack_questions.ask_all_over_lines`(預設 300,`_STACK_ASK_ALL_DEFAULT`,20235)。目前呼叫端(26113–26123)對每個棧鍵是把「屬於那個副檔名的所有檔案的增刪行」彙總後丟進同一次 `_stack_applicability` 呼叫。

設計點 2(`不是測試檔、不是簿記檔的增刪行,不管副檔名是哪一棧`)要求:凡是「需要有家的程式檔」,不論其自身副檔名屬於哪個既有棧,行都要額外算進 `data` 這個跨棧鍵。照現有架構最自然的實作方式,是在 26113–26120 那段迴圈裡,對每個通過 `_stack_changed_ok` 的程式檔,`sk = _stack_key_for_file(...)` 之外再加一行「同時也塞進 `_by_stack["data"]`」,然後仍然用同一次 `_stack_applicability(_by_stack, threshold)` 呼叫。這樣一來,`data` 鍵拿到的是「這次改動裡所有程式檔行的聯集」,天生就比任何單一棧的行數多,幾乎必然先撞到門檻。

具體失敗場景:S3 本身的測試設定就是「當某支程式檔增刪行超過行數門檻卻沒有任何資料狀態觸發字」——例如一支 `.kt` 檔改了 305 行(> 預設門檻 300),內容是變數重新命名等,完全不含任何 ds- 觸發字。若照上面「最自然」的實作,這 305 行既進了 `kt` 桶(既有行為,`over=True`,kt 全表適用,符合設計)也進了 `data` 桶——而 `data` 桶同樣是 305 行 > 300,`_stack_applicability` 對 `data` 鍵也判 `over=True`,於是七題全部被標成 `applicable=True`、`triggered_by=["行數>300"]`。這正是 S3 明文要求「`ds-` 題全部維持不適用」的反面,也正是這份計劃自己的 WHY 段落(`大一點的改動幾乎必過門檻,每次多七題 na 會把表態變成儀式`)明講要避免的失效模式。要避免這個結果,需要讓 `data` 鍵在呼叫 `_stack_applicability` 時拿到「無限大」或另開一次不帶門檻的呼叫再合併結果——這個必要步驟在設計節與七條驗收條款裡完全沒有出現,S3 也沒有測到「多檔彙總後總行數超標」這個更常見的情境,只測了單檔場景,而單檔場景本身就已經足以踩雷。

## F2 `_stack_key_for_file` 是 pitfalls --diff 與 impact/PreToolUse hook 共用的唯一入口,修它去認出無副檔名腳本會連動到設計點 6 明講「本次不動」的那條路

severity: blocker
blocking: 是(會讓一個明確聲明不動的消費端悄悄變了行為,而且沒有任何驗收條款會抓到)
引句:「那條路按單一檔的棧附題,本次不動」

`_stack_key_for_file` 的 docstring 自己講明:「兩個消費者(pitfalls --diff / impact hook)都走這一支,別各自抄副檔名邏輯」(scripts/lumos:20224)。第二個消費者就在 `impact` 指令的 JSON 輸出路徑裡(28831):

```
_sk = _stack_key_for_file(rel_file, repo_root_for_lookup)   # .ts/.js 看 package.json 分前後端
if _sk:
    out_obj["stack_questions"] = {_sk: _STACK_PERF_QUESTIONS[_sk]}
    ...
```

這是單一檔案(`rel_file`)的查詢,正是設計點 6 說「按單一檔的棧附題」「本次不動」的那條路(PreToolUse 動手前提示)。

S1 要求「沒有副檔名、首行是 `#!` 的程式檔」要能命中 `ds-partial-write`,而目前 `_stack_key_for_file`(20221)對無副檔名檔案的處理是 `ext = ""`,不在 `_STACK_PERF_QUESTIONS` 裡,回 `None`——要讓 S1 成立,勢必要修改這支共用函式,讓它對「無副檔名但首行 `#!`」的檔案回傳 `"data"`(或至少某種能查到 `data` 題組的鍵)。

具體失敗場景:工具鏈自己的主程式 `scripts/lumos` 正是這種「無副檔名、首行 `#!`」的檔案(本 repo 幾乎每個功能提交都會改到它)。一旦 `_stack_key_for_file` 被改成能辨識這類檔案,`impact --diff` 或 PreToolUse hook 對 `rel_file="scripts/lumos"` 的單檔查詢(28831)也會自動拿到 `_sk="data"`,把全部七題塞進 `out_obj["stack_questions"]["data"]` 印給使用者看——即使這次改動根本沒有 ds- 觸發字(因為這條路徑目前完全不看觸發字,只看副檔名/棧鍵命中,26113 行那種「觸發式適用性」是給有 `delta_text` 的呼叫用的,28834 開始才有,舊呼叫端會退回印全表)。這直接違反設計點 6 明講的「本次不動」,而且七條驗收條款沒有一條是針對 `impact`/hook 路徑寫的,這個回歸不會被任何測試擋下來。

## F3 七條驗收條款只用「無副檔名腳本」測出適用性,沒有任何一條驗證「有副檔名的程式檔(.py/.kt/…)也會餵進 data 桶」——設計點 2 的核心承諾完全沒有測試覆蓋

severity: major
blocking: 是(核心設計承諾沒有可驗證的判準,實作可以完全繞過它仍然七條全過)
引句:「不是測試檔、不是簿記檔的增刪行,不管副檔名是哪一棧」

設計點 2 的字面要求是「這次改動裡所有『需要有家的程式檔』……不管副檔名是哪一棧」都要餵進 `data` 題組。但七條驗收條款裡唯一會真的觸發 `ds-` 題適用性的是 S1,而 S1 的輸入被限定成「沒有副檔名、首行是 `#!`」的檔案——這恰好是唯一「本來就沒有其他棧可以歸屬」的檔案類型。S5 只要求「每題各給一行命中樣本」,沒有規定這些樣本必須放在有副檔名的檔案裡驗證跨棧收集這件事。

具體失敗場景:一個實作只在 `_stack_key_for_file` 對「無副檔名+`#!`」的檔案回傳 `"data"`(如 F2 所需要的最小修改),對所有其他有副檔名的檔案完全不變(繼續只回它自己的棧,例如 `.py` 回 `"py"`)——這樣的實作可以讓 S1、S2、S4、S6、S7 全部通過(它們都只依賴無副檔名案例或通用機制),S3 只要另外處理好 F1 的門檻問題也能過,S5 只要樣本檔案挑無副檔名的就能過。也就是說,一份完全沒有讓 `.py`/`.kt`/`.cs` 等一般程式檔案的 `os.replace(`/`os.remove(` 之類的行進到 `data` 桶的實作,可以讓全部七條驗收條款亮綠燈——而這正是設計節開宗明義要解決的主要情境(消費專案絕大多數程式檔案都有副檔名),功能名不符實卻沒有測試能抓到。

## F4 七題裡六題的觸發字清單完全沒有定義,S2/S5 現在寫不出測試;用代理詞表估出的日常命中率印證了計劃自己擔心的那個失效模式

severity: major
blocking: 是(驗收條款字面上要求逐題各給命中/不命中樣本,但六題沒有觸發字可依據,無法客觀寫出測試)
引句:「當每題各給一行命中樣本、一行不命中樣本、一行只在註解裡出現觸發字的樣本」

設計點 8 只給了原則(「沿用範式詞加反面詞;要具體到不誤傷」)與一個具體例子(`os.replace(`,用在 S1 裡對應 `ds-partial-write`)。`ds-evolution`、`ds-derived`、`ds-concurrent`、`ds-time`、`ds-irreversible`、`ds-side-effect` 六題,全文找不到任何一條具體 regex 或詞表——只有中文問句本身。S5(`t_data_questions_triggers`)要求每題各給命中/不命中/純註解三種樣本(共 21 行),但沒有觸發字清單,測試作者要先自己發明六題的觸發詞,不同工程師會寫出不同結果,S5 這條驗收條款在今天這份 spec 下沒有唯一答案,無法客觀判斷「照 spec 實作」對不對。

具體失敗場景與實測數據:我用一組保守的代理詞表(每類抓 1-2 個最直覺的關鍵詞,如 `os.replace(`/`os.rename(`/`tempfile` 代表 partial-write,`cache`/`_CACHE`/`snapshot` 代表 derived——刻意排除設計點 8 明講不能用的裸 `index`、`.get(`,也排除同樣過度寬鬆的裸 `.pop(`),套用在本 repo 最近 20 個動到 `scripts/` 的提交上(用 `git -C .../ddia-review-lenses show <sha> -- scripts` 取增行,並套用與 `_stack_changed_ok` 等價的測試檔/文件/簿記檔排除規則),結果:20 個提交裡有 12 個(60%)至少命中一類。若换成較寬鬆但同樣「看起來合理」的詞表(納入裸 `index`/`.pop(`/`.get(`),命中提交數升到 17/20(85%)——這正落在計劃自己 WHY 段落擔心的區間(「大一點的改動幾乎必過門檻,每次多七題 na 會把表態變成儀式」)。这两个数字都还没算进 F1 的行数门槛问题(那会再往上推)。换句话说,S2/S5 能不能守住「只在真的碰到資料狀態風險時才問」這個目標,完全取決於一份 spec 沒有寫出來的詞表怎麼選,而不同合理選擇之間命中率可以差到 25 個百分點。

## F5 `stack_questions.gate=high-only` 是既有、合法的設定值,但會讓 ds- 題組對它設計要抓的目標情境幾乎永遠問不到

severity: major
blocking: 是(在一個既有、被本計劃明講要沿用的逃生口設定下,功能對主要目標情境靜默失效,且此互動全文未討論)
引句:「誤擋的逃生口沿用既有的 `na`(附理由)與設定檔 `stack_questions.gate`(all/high-only/off)」

`_dispositions_verdict`(scripts/lumos:31649)第一行判斷:`if not app or cfg["mode"] == "off" or (cfg["mode"] == "high-only" and tier != "high"): return out`(unblocked,無 problems)。`cmd_pitfalls --diff --disp-tpl` 也有同一條件(26481–26484)。這代表:在 `gate=high-only` 的專案裡,除非這次改動的 `tier` 已經是 `high`,否則即使 `stack_questions_applicable` 裡有適用的 `ds-` 題,也完全不會被要求表態(甚至連樣板都不印)。

而 `tier` 是否為 `high`,只看 `_pitfall_tier`(25875)裡的 `claims`,來源是 `_PITFALL_DIFF_PATTERNS`(scripts/lumos:20323–20330)——六條 regex:HTTP 呼叫、`open(`、`SELECT...FROM`、`time.sleep(`、`threading./Lock(/global`、`INSERT/UPDATE/DELETE`。`os.replace(`、`os.remove(`、`os.rename(`、`json.dump(`、`shutil.rmtree(`、日期時間比較這些正是設計點 7 七題鎖定的核心動作,全部不在這六條 pattern 裡。

具體失敗場景:一個消費專案把 `stack_questions.gate` 設成 `high-only`(合法值,`_STACK_QUESTIONS_GATE_VALUES` 允許)。開發者新增一行 `os.remove(old_snapshot_path)`(刪掉舊快照,典型 `ds-irreversible`/`ds-derived` 情境),沒有伴隨任何一條 `_PITFALL_DIFF_PATTERNS` 命中,`tier` 判定為 `"standard"`。`_dispositions_verdict` 與 `--disp-tpl` 都會直接放行、不印任何 ds- 題目,開發者連「這裡有一題該答」都不會看到,更不用談表態。也就是說,`high-only` 這個既有逃生口對 ds- 題組而言不是「答了但可以晚點答」,而是「這輩子都不會被問」——這個互動在 實務隱患 節與設計節都沒有被討論到。

## F6 已知死結(沒有 docs/ 的專案答不了表態題)被本計劃放大的程度,比 spec 自己「補一行」的處置更嚴重——消費專案的第一個 onboarding 提交正是雙重踩雷點

severity: major
blocking: 是(spec 承認會放大既有死結但沒有評估放大到什麼程度;結合 F1 後,首次推送即可能觸發且無法答題)
引句:「沒有 docs/ 的專案表態指令拒寫、推送閘卻照擋」

`docs/lumos-toolchain-knowledge/Issues/沒有圖譜的專案答不完表態題.md` 記載的死結是真實存在、被測試踩過的(2026-09-12,Python 棧上線後一行 `requests.post` 讓假 repo 六條斷言翻紅)。spec 的誠實界線節正確地引用了它,並承認「資料狀態題觸發面比棧別題廣……撞到的機會變多」,處置是「在那篇 Issue 補一行『受影響面擴大』」——但這只是文件補注,不是功能上的緩解。

具體失敗場景:一個全新消費專案第一次接入(還沒有 `docs/`)。第一個 onboarding 提交通常是把既有程式碼整批帶進來,檔案多、行數大,很容易單一棧就超過 300 行(既有行為),而依 F1 的分析,`data` 跨棧彙總桶幾乎必然也超過同一門檻,導致七題全部 `applicable=True`。`code-loop check`(S6 要求的行為)因此擋下推送;而 `code-loop dispositions <這個檔>` 因為找不到 `docs/` 存治理帳而拒寫(既有死結)。開發者唯一出路是 `--no-verify`——這是死結 Issue 原文就講的結局,差別只在於:原本這個死結要「棧別題剛好命中」才會遇到(相對少見,才會到 2026-09-12 才被測試意外踩到),本計劃上線後,由於 `data` 桶跨越所有程式檔且不吃行數門檻的意圖失敗(F1),幾乎可以肯定在任何消費專案的第一個大型提交就會踩到,而不是「這段期間如果有真的消費專案踩到」(REVISIT 條件字面上假設的「小機率事件、事後觀察」)這種語氣所暗示的機率。

## F7 S7 要求「只列命中的題」且換標籤,但現有人讀輸出迴圈印的是「整棧全部題目」——照設計點 1「全部照舊運作」字面重用會直接違反 S7

severity: major
blocking: 是(現有輸出邏輯與 S7 要求的行為互相矛盾,若不寫新分支必定印錯)
引句:「當有資料狀態題適用,pitfalls 的 diff 模式人讀輸出應印」

`_pitfall_diff_mode`(scripts/lumos:26235)目前的人讀輸出:

```
for stk, qs in data.get("stack_questions", {}).items():
    print(f"  [{stk} 效能檢核]")
    for q in qs:
        print(f"    - {q}")
```

這裡的 `data["stack_questions"]` 來自 26109–26116:`stack_qs[sk] = _STACK_PERF_QUESTIONS[sk]`——只要有任一檔案的副檔名命中某棧,就把該棧「全部題目原文」塞進去,不看個別題目是否觸發(程式碼自己的註解也講明:「stack_questions 語意不變(命中棧整組)」)。這是既有九棧共用的印法。

具體失敗場景:S1 情境成立時(無副檔名 `#!` 腳本 + `os.replace(`),若 `data` 鍵照既有機制也被塞進 `stack_qs`(即 F2/F3 討論的「最小修改」路徑自然會產生的副作用),這段既有迴圈會印出 `[data 效能檢核]`,並列出全部七題——而不是 S7 要求的「資料狀態檢核(跨棧)」標籤,也不是「只列命中的題」(這裡只有 `ds-partial-write` 真正觸發,其餘六題是 `applicable=False`)。要讓 S7 成立,必須新寫一段獨立於這個既有迴圈之外的邏輯,改讀 `stack_questions_applicable.get("data")`(已過濾)而不是 `stack_questions.get("data")`(未過濾),並且用專屬字串取代 `f"[{stk} 效能檢核]"` 這個通用格式。設計點 1 說「表態範本、`code-loop check`、`gov --stats`、`recall-miss` 全部照舊運作,不另寫閘」,但至少人讀輸出這一段確實需要新寫分支——這點只在設計點 5 的結論句帶過,沒有講清楚需要動到哪支函式、以及跟既有印法的衝突在哪裡。

---

# 總結

最嚴重 severity:blocker。blocking 共 7 條(F1–F7 全部 major 或 blocker)。
