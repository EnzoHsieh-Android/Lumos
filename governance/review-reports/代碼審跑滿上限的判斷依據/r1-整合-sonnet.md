severity: major

## F1 loop_next 的 cap-reached 出口對 panel 格式迴圈(design-loop、high 代碼審)已經是死路
severity: major
blocking: 是——照 S1 字面把報告函式接在 loop_next 的 emit("cap-reached", …) 後面,design-loop 和 high 代碼審(佔迴圈用量最大宗、也最容易撞上限)全部看不到這段輸出,做出一個「大多數目標使用者永遠碰不到」的功能
引句:「當代碼審迴圈的輪數達到該分級上限且閘未過,`loop next` 的輸出應在交給人的那句底下列出每輪折入數、修正引起的條數與同類重複狀態,並給出一個建議」

實測(讀 repo 真帳,唯讀):對一個真實存在、目前還開著的 panel 格式迴圈直接問 `loop next`:
```
$ python3 scripts/lumos loop next "design-筆記欄位關卡補齊" --spec "docs/lumos-toolchain-knowledge/Projects/筆記欄位關卡補齊_計劃.md"
擋下:panel 閘自 2026-08-25 甲裁後僅供舊迴圈回放,這個編號是之後才開的新迴圈——
  多席審查改用彙總記帳(處置清單只掛一席,其餘席只留痕),然後問處置閘:
    lumos loop status <編號> --disposal --spec … --repo …
```
再用合成帳本(自建 vault,不動 repo)重現同一形狀(`--tier high`、兩輪 panel 格式帳、ts 在 2026-08-26 之後),結果一致。

file: `scripts/lumos:10664-10671` —— `cmd_loop_next` 的「② full-basis gate 委派」呼叫 `cmd_loop_status(..., gate=True, panel=(panel_fmt and not light), ...)`,**沒有帶 `disposal=True`**;`rc == 2` 時直接 `return 2`,函式在這裡就結束,永遠走不到後面「③ cap(資訊充分且未 PASS)」那一步(`scripts/lumos:10675-10678` 的 `if rounds_count >= cap: … emit("cap-reached", …)`)。
file: `scripts/lumos:8284-8289` —— `_loop_status_panel`(`gate=True, panel=True` 時走的分支)第一步就是 `_panel_retired_for(rounds)`:任一 panel 格式迴圈首筆 ts ≥ 2026-08-26 就直接印「panel 閘自 2026-08-25 甲裁後僅供舊迴圈回放」並 `return 2`。design-loop 一律 panel 格式;代碼審 high tier 的多席編制也是 panel 格式(`scripts/lumos:10402` `seq = (eff_tier == "standard" and _roster_kind(loop_id) == "code" and not panel_fmt)`——只有 code+standard+無 round 才叫 seq,high 恆是 panel_fmt)。
若不帶 `--spec` 呼叫,則卡在「① gate-pending」(`scripts/lumos:10633-10662`),同樣到不了 step③。

換句話說:2026-08-25 之後開的迴圈,只要是 design-loop 或 high 代碼審,`loop next` 這個函式裡「② full-basis gate 委派」這一步**對這兩種迴圈恆傳回 2 或卡在 gate-pending**,`emit("cap-reached", …)` 這行 code 對它們是不可達的死碼。真正能觸發 cap-reached 判定、走完整條閘邏輯的只剩 standard+代碼審的循序(`seq`)迴圈與 light 迴圈——這兩種的上限本來就低(2、3 輪)、也不是計劃摘要裡舉的那些「跑到 4 輪以上還沒收斂」的例子(那些是 code-relmainnet/記憶過期清掃…全是 panel 格式或已越過上限很多輪的舊迴圈)。

這解釋了計劃自己的 FACT(「136 個迴圈裡 11 個(現重跑是 12 個,見下方誠實揭露)跑到 4 輪以上,但治理帳裡『跑滿上限』只記過 3 次,都在 08-24」)——3 次全部發生在 `_panel_retired_for` 的 cutoff(2026-08-26)**之前**。計劃把「幾乎不觸發」完全歸因於「編排者跑滿後常直接記下一輪,沒再問 loop next」(行為面),但至少對 panel 格式迴圈而言還有一個機械面的原因:就算真的去問了,也問不到。計劃的「印在哪裡」段兩個出口(loop next 的 S1、`loop status --disposal` 的 S6)寫得像是互為備援的兩個入口,但對 design-loop/high 代碼審來說 S1 這個入口目前是打不通的——S6(`loop status --disposal`)才是唯一會被實際跑到的出口。建議：spec 明講這個落差,把 S1 的實作重點放在「loop_next 的訊息裡指路去 `--disposal`」而不是自己列出三個數字(反正列了也印不出來),或者先把「② full-basis gate 委派」改成对 panel 格式迴圈改問 disposal(那是另一個更大的變更,不在本案範圍但要註記依賴)。

## F2 「沿用 quote-check 的引句定位」對「新增行」判斷是名不副實——quote-check 本來就不記行號
severity: major
blocking: 是——照 spec 字面只重用 `_quote_rows`/`_quote_norm`,實作者拿不到「這條引句落在快照的第幾行、是不是新增行」這個資訊,S2/S7 沒東西可比,會被逼著另開一套字串比對邏輯,但 spec 完全沒描述這套邏輯要怎麼做、跟既有 quote-check 的關係是什麼
引句:「拿它的第一句引句去最後一輪的凍結審材定位(沿用 quote-check 的比對);定位到的那行是新增行」

file: `scripts/lumos:17849-17859` —— `_quote_norm` 的正規化是 `unicodedata.normalize("NFC", s)` 之後 `" ".join(s.split())`:`s.split()` 對整份文字(不分行)切詞再用單一空格接回去,**換行資訊在這一步就已經被摺掉**,輸出是一整條攤平的字串,不是逐行結構。
file: `scripts/lumos:17881-17892` —— `_quote_rows` 對每條引句只做 `nq in hay`(整份攤平文字裡的子字串存在性檢查),回傳只有 `{"quote":…, "ok": True/False}`,**沒有任何位置或行號欄位**。這支函式從設計上就只回答「這句話有沒有出現在這份文件裡」,答不了「出現在哪一行、那一行是不是上一輪沒有的新增行」。

代碼審的凍結審材(`--snapshot`)實務上多半是 `git diff -U10` 產生的 `.patch`/`.diff`(本 repo 實際卷證裡 247 個 `.patch`+4 個 `.diff` vs 213 個純 `.md`),unified diff 本身有 `+`/`-`/行號可用,「新增行」在那種格式下是有意義的概念;但 quote-check 現有實作完全不利用這個結構,只把整份 patch 當成一坨文字找子字串。要做到 S2/S7,實作者勢必要另外寫一套「逐行/逐 hunk 比對」的新邏輯(讀 patch 的 `+` 行、或直接對兩輪快照做行級 diff),而不是像 spec 「不加新依賴」「沿用既有」的用詞暗示的那樣直接呼叫現成函式。這不是不能做,但 spec 的「做法」一節該把這段新邏輯明講出來,而不是含糊地說「沿用 quote-check 的比對」——現在的寫法會讓實作者以為 `_quote_rows` 已經替他做好行定位,一讀程式碼就會發現落空。

## F3 loop_status_disposal 目前不知道自己在哪個 tier、上限是多少——S6 得另開一套 cap 判斷,跟 loop_next 那套分家
severity: major
blocking: 是——兩處各自重算「有沒有到上限」,依 2026-08-02 那次 quote-check 預檢/主迴圈兩份實作漂移的前例,分開寫最後大概率兜不起來,S6 承諾的「與 S1 相同的一段」會變成兩份可能不一致的邏輯
引句:「`loop status --disposal`(每一輪都會跑)在輪數已達上限時也印同一段」

file: `scripts/lumos:18265-18277`(`_loop_status_disposal` 函式簽名與 docstring)——七步合取裡完全沒有 tier/cap 的概念,不讀 `_TIER_PARAMS`。
file: `scripts/lumos:10398`(`width, cap = _TIER_PARAMS[eff_tier]`)與 `scripts/lumos:9801`(`_TIER_PARAMS = {...}`)——tier→cap 的查表邏輯目前只存在 `cmd_loop_next` 一處,靠 `_loop_anchor_tier(rounds)`(`scripts/lumos:9905-9908` 附近,取帳上第一筆帶 tier 的值)定錨。

要讓 `loop status --disposal` 也能判斷「輪數已達上限」,實作者必須在 `_loop_status_disposal` 裡重新呼叫 `_loop_anchor_tier` 拿 tier、再查一次 `_TIER_PARAMS` 算 cap——這是完全可以做但 spec 沒有指名要共用同一支查表/判斷函式。本專案自己的 quote-check 開發史已經踩過這個坑並留了警告(`scripts/lumos:17850-17852` 註解明講「★抽取與比對共用這一份——嚴禁第二份實作★(2026-08-02 教訓:預檢與主迴圈兩份實作當場漂移)」),spec 卻沒有把同一條紀律用在這裡:沒有一句話要求「cap 判斷只寫一份,loop_next 跟 disposal 共用」。萬一 disposal 那份 cap 判斷漏抄了 `_loop_anchor_tier` 的某個邊界(例如 seq 的 width/cap 覆寫、legacy fallback),S1 跟 S6 就會在同一個迴圈上給出不一致的「有沒有到上限」結論。

## 逐類實務隱患檢查(F1/F2/F3 之外,獨立過一次)

- 併發:計劃已寫「報告函式只讀帳、不寫帳」,讀到寫一半最後一行的處理沒有另外新起爐灶——`_loop_status_disposal` 現有壞行處理(`scripts/lumos:18279-18285` fail-closed 整段拒判)是既有機制,計劃若照它的既有慣例沿用沒有新增風險;只是計劃沒有明講新報告函式遇到壞行時是要 fail-closed(拒印建議)還是跳過那一行,這點留白但不到 major(不影響閘的判定,只影響建議印不印得出來)。
- 效能:計劃承諾「只在輪數達上限或觸發熔斷條件時才算」——`_loop_status_disposal` 每輪都跑一次,若沒先判斷 `rounds_count >= cap` 再決定要不要進報告函式,等於每輪都去讀整本審查帳跟凍結審材;這點計劃文字上有承諾但沒有寫進條款([S6] 只講「應印出」,沒講「僅在達上限時才計算」),算是條款對「做法」段落的覆蓋不完整,但不足以構成 blocking(頂多是效能上的浪費,不是錯誤行為)。
- 金流/對外送出/不可逆:計劃自己的「已排除」三項核對過真實機制皆成立——報告函式只讀本機帳本檔(`.canary-log.jsonl`)與凍結審材(本機檔案),沒有任何網路呼叫路徑;新增輸出段落與 `--finding-class` 選填欄位確實可以透過拔掉呼叫點回退,舊帳沒有這個欄位、讀側對缺欄位一律容忍(參照 `scripts/lumos` 全篇多處「缺欄視為未填,不當作有值」的既有慣例,如 `_findings_zero` 對 `findings` 缺欄的處理),這條回退主張站得住。
- 守衛面:計劃承諾「只印不擋」,S6/S9 也各自綁了「不改變過關判定與退出碼」的條款([S6][S9])——照現有 disposal 函式結構(印一段文字、不影響 `fails` 清單),要做到「只印不改 rc」是自然的(其他步驟如①②③④⑤⑥⑦都各自印一段再各自決定要不要進 `fails`,加一段不進 `fails` 的純觀察段落是既有模式的直接延伸),沒有看到會意外污染既有 rc 判定的路徑。

已看,無:計劃摘要裡的三處 WHY 引用(VRR-Stop/arXiv 2607.17641v1、Google eng-practices「拆小改動、談不攏往上找人裁」、Claude Code auto 模式拒絕熔斷器)裡,第一項已查證——arXiv 2607.17641 真實存在,標題是「Verify, Repair, Repeat, or Stop? Robust Stopping for Noisy Verify-Repair Loops in LLM Agents」,內容確實談「repair 會把對的東西改壞」「用預期邊際收益判斷要不要繼續修」,跟計劃的轉述一致,不是編造或斷章取義。計劃自己已經誠實標註第四項出處(Claude Code auto 模式拒絕熔斷器)「編排者沒有對照原始碼核實」,符合 PRIOR-ART 紀律對不確定出處的誠實揭露,沒有再加驗的必要(第三方對閉源工具的原始碼分析本來就查不了)。record_cmd 的 `caught|missed`→`canary record none` 這處歷史修正,對照 `Systems/design-loop.md` 的 PITFALL 記錄與程式碼現況(`scripts/lumos:10461`),三方一致,計劃這句「已於 2026-09-25 修掉」屬實。`_TIER_PARAMS` 的 light/standard/high cap(2/3/3)與 skill 文件(`skills/lumos-design-loop/SKILL.md:65`「light 2 筆、standard / high 3 筆」)對得上,計劃沒有另外重述這個數字但也沒有講錯的地方。落點 `Systems/loop-convergence-recording` 核對過現況(該節點已管 `scripts/lumos` 的 loop 系列函式,DEP 行與大量 KEY 都在講同一支 loop next/disposal 機制),掛進這篇不會撞到別的家。條款 S3–S5、S8 讀起來邏輯自洽,對照既有帳本欄位(`folded_set`/`accepted_set` 每輪可加總)可行,沒有另外的懸空引用或矛盾。計劃自己在「順帶看到、不在本案範圍」段落標記的舊帳已修正項目與程式碼現況一致,沒有過期。三個機械數字(136 個迴圈、11 個跑到 4 輪以上、3 次跑滿上限)裡,跑滿上限的「3 次都在 08-24」重跑結果一致;但「136 個迴圈」「11 個跑到 4 輪以上」重跑分別得到 141 與 12(帳本在 2026-09-25 到今天 2026-09-26 之間自然長大,計劃的 FACT 行已按 CLAUDE.md 規範標了可重跑指令與日期,這是活資料的預期漂移不是計劃寫錯,不列為 finding)。

最後一行總結:最嚴重 severity 為 major,blocking 共 3 條(F1、F2、F3)。
