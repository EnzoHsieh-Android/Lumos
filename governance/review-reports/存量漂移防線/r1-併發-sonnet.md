severity: blocker

# 存量漂移防線_計劃 審查報告(鏡頭:資源與併發)

審查範圍:凍結快照全文(`r1-snapshot.md`,161 行,frontmatter + 正文全部段落)逐節讀完;對照程式碼倉 `clone-ns`(`scripts/lumos` 34289 行、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`)與圖譜節點(`Issues/治理帳多個寫入者都沒上鎖.md` 等)實際查證。前掃已改的四類(`r1-intake.md`)不重報。

## 逐節讀完紀錄

- frontmatter / 白話 / 依據:已讀,無 finding。
- PRIOR-ART / RETIRE-IF / REVISIT:已讀。與 `Projects/code側刪除傳播守衛_計劃` d0(delguard 只提醒)的關係、與 `Projects/先問世界_存量掃描裁定` 的關係,文字內部一致,判「不影響」——丙的三處窄化(只收整檔消失的名稱/只看這次推送帶進來的/只有家筆記與摘要行擋)確實比 delguard 窄,沒有翻案。
- 範圍(做/不做):已讀,無 finding。
- 做法 0(共用/`lumos drift`/推送閘):見 F1、F2、F3、F5、F6。
- 做法 1(甲,guard settle / lumos set / 狀態一致檢查):見 F2。
- 做法 2(乙,`[when:]` 條件):已讀,無 finding(併發面上,`[when:]` 只是讀取判斷,不寫入,沒有寫入競態)。
- 做法 3(丙,推送前列出舊句):已讀,無 finding(併發面上是純讀取 + 一次性判定,見 F5/F6 的效能面)。
- 做法 4(健檢:scan 的兩種現況檢查):見 F1(4.2 的 `git log -G`)。
- 做法 5(考卷與考法):已讀,無 finding。
- 做法 6(掃全圖譜與修復):已讀,無 finding(rtb 那份交給 rtb 會談,工具鏈自己逐條處理,沒有描述到跨會談同時改同一批筆記的情境,但這步驟本來就是人工序列執行,不構成併發風險)。
- 條款 S1–S18:見 F1、F2、F3、F5、F6(逐條對應見各 finding)。
- 回退:已讀,無 finding。
- 實務隱患:見〈本鏡頭隱患逐類作答〉,含對現有「併發」段落的具體挑戰(F2 的落差、F5/F6 的效能落差)。
- 誠實界線:已讀,無 finding。
- 考試結果 / 修復結果(空節,前掃已補位):已讀,無 finding。

---

## F1 doctor 每次推送都會跑的 Z 段,`git log -G` 沒有時間上限,實測單次約 14 秒

severity: blocker
blocking: 是 — 不改的話,`lumos doctor`(已經無條件掛在每次 push 與每次 CI 上)一旦跑到 4.2 的候選符號檢查,會把單次 push/CI 拖到數分鐘甚至數小時,不是「風險」而是會直接把推送流程做壞。

引句:「doctor 開一段(字母 `Z`)印筆數與前幾筆」

引句:「在 git 歷史上曾經是某支程式檔裡的定義(`git log -G` 找過去版本」

引句:「每次 scan 最多查 500 個候選名,超過就印出截斷並給 `--limit` 旗標」

file: `scripts/hooks/pre-push:179-181`(`_DOCTOR_ARGS=(doctor --ci)` 且 `if [[ $have_vault -eq 1 ]] && ! "$PY" "$GRAPHCTL" "${_DOCTOR_ARGS[@]}"; then ... exit 1`——doctor 是每次 push 都無條件跑、非零就擋的閘)
file: `.github/workflows/ci.yml:97`(`run: python scripts/lumos doctor --ci`,CI 同樣無條件跑)

1. [S15] 與〈做法〉第 4 節第 2 點合起來要求:doctor 的 Z 段要印出 scan 的「筆記點名的程式符號已經不存在」檢查結果,而那項檢查的判準明文是「在 git 歷史上曾經是某支程式檔裡的定義」,做法是 `git log -G` 找過去版本;候選名上限只設「500 個」,沒有設時間上限(時間上限的 60 秒只出現在〈實務隱患〉段,文字明講是給 `check` 用的,見 F5)。
2. doctor 已經無條件掛在 `scripts/hooks/pre-push:181` 與 `.github/workflows/ci.yml:97`,兩處都是「非零就擋 / 紅」的同步呼叫,不是背景任務。
3. 實測(在本工具鏈自己的複本 `clone-ns` 跑,2264 個提交、`.git` 70M):
   ```
   time git log -G"SomeRandomSymbolNameThatMightExist" --oneline -- . > /dev/null
   # 13.64s user 0.84s system 92% cpu 15.690 total
   time git log -G"AnotherRandomSymbolXYZ" --oneline -- . > /dev/null
   # 13.44s user 0.61s system 99% cpu 14.165 total
   time git log -G"YetAnotherSymbolABC" --oneline > /dev/null
   # 13.31s user 0.54s system 99% cpu 13.859 total
   ```
   三次獨立跑,穩定落在 13.3–15.7 秒/次。
4. 照這個實測值外推:只要一次 push 帶進來 10–20 個「形狀像程式符號、反引號包住」的候選名(一篇筆記的 `RULE:`/`FACT:` 行提到十幾個函式名很常見),Z 段就會加 2–5 分鐘;做法 4.2 自己承認的上限是 500 個,外推約 2 小時。這比 pre-push 現有「便宜的先跑、貴的最後」註解裡列的基準(所有閘加起來約 13 秒,全套測試 8 分鐘)高一到兩個數量級。
5. `LUMOS_SKIP_DRIFT_CHECK=1` 這個逃生閥(〈做法〉第 0 節)只對 `drift check` 有效,doctor 本身不是 `drift check`,S15 也沒有給 doctor 的 Z 段獨立的略過旗標——一旦這段變慢,使用者連現成的逃生路都沒有,只能 `--no-verify` 整支 hook 一起跳過(連同 anchor verify、home check 等其他閘一起放棄)。
6. 對照組:同一份〈做法〉第 0 節對 `check` 明講「淺層 clone 跳過並記帳(同兩層筆記閘)」,但 doctor 的 Z 段沒有對應的淺層/大 repo 降級敘述。

## F2 guard settle 改寫家筆記沿用既有無鎖的 read-modify-write,S4 在同一條路上加寫更多內容,〈實務隱患〉的「併發」段沒提到這條路

severity: major
blocking: 是 — 兩個會談(同一個工作目錄,例如同時開兩個 Claude session)一個在 `guard settle`、另一個在對同一篇家筆記做 `lumos set`,後寫的會整段蓋掉先寫的,而且不會有任何錯誤或警告——這正是專案自己在 `_lint_waivers_add` 的註解裡點名要避免的那種靜默流失。

引句:「工具應把守衛紀錄裡 guard plan 寫的 TEST、WHY、正文三種預告句改成歷史說法、其他行一字不動」

引句:「寫後自驗照既有 `atomic_write_verify`」

1. 現有 `cmd_guard_settle`(`scripts/lumos:11792-11830`)已經在做一次 read-modify-write:讀家筆記(`env.vault / home_rel`)、算出要換的那一行、呼叫 `atomic_write_verify(env.vault / home_rel, ...)`(`scripts/lumos:11821`)——呼叫端**沒有**包 `with _vault_write_lock(env.vault):`。呼叫鏈一路到 dispatcher(`scripts/lumos:34092`,`return cmd_guard_settle(env, args.ref, args.gs_test)`)也沒有外層鎖。
2. 對照 `cmd_set`(`scripts/lumos:14300-14302`):`def cmd_set(env, rel, key, value): with _vault_write_lock(env.vault): return _cmd_set_locked(...)`——同一個筆記庫的欄位寫入是有鎖的。
3. `_write_lf` 自己的說明白紙黑字寫著這個分野(`scripts/lumos:14153-14158`):「read-modify-write 的併發:set/append/remove 由呼叫端上鎖(`_vault_write_lock`),其他寫入指令仍是 last-write-wins(單機 CLI,accepted)」——`guard settle` 對家筆記的改寫落在「其他寫入指令」那一類,是專案自己已經標明接受 last-write-wins 的路。
4. S4 要求在**同一個 `guard settle` 呼叫**裡再多改守衛紀錄本身(`rel`,不是家筆記)的 TEST/WHY/正文三種句型,而且〈做法〉第 1 節第 1 點明講「寫後自驗照既有 `atomic_write_verify`」——即沿用同一支沒有鎖保護的寫入原語,對象換成守衛紀錄那篇筆記。這篇筆記緊接著又會被同一次呼叫裡的 `cmd_set(env, rel, "status", "pass")`(有鎖)改一次——同一篇筆記在同一次 `guard settle` 內先後被無鎖寫一次、有鎖寫一次,中間那個空檔正是另一個會談可以插進來改同一篇(例如 `lumos guard abandon` 需要簽核、正在走簽核流程的另一個會談,或直接手動 `lumos set` 那篇守衛紀錄的欄位)的視窗。
5. 〈實務隱患〉的「併發」段只寫了表態檔(`governance/drift-acks.jsonl`)分支合併的情境,完全沒有提到 `guard settle` 這條既有、且被 S4 加重使用的無鎖寫入路——而這正是本鏡頭派工詞明講要查的「guard settle 改寫守衛紀錄…跟其他寫入者(共用工作目錄的其他會談)同時改同一篇」。

## F3 `drift ack` 綁的內容編號不耐筆記改名,改名會讓既有表態全部靜默失效、舊句重新被擋

severity: major
blocking: 是 — 作者已經 `drift ack` 過的句子,只因為那篇筆記被改名(`git mv`,本專案常見操作,CLAUDE.md 與圖譜多處談到「推筆記認家」「搬節」)就會被當成沒表態過重新擋下,會讓 RETIRE-IF 的第一條指標(「照留」表態比例)失真,也會讓使用者誤以為工具在無中生有地重新翻案。

引句:「工具應綁那一行的內容編號:那行沒改時同一句不再擋、改過就失效照擋」

引句:「借 `_notelines_content_id`:路徑、區塊、小標題、去空白的行文字」

file: `scripts/lumos:23819-23825`
```
def _notelines_content_id(path, region, heading, line, done=False):
    """內容編號=(NFC 路徑、區塊、所屬小標題、去頭尾空白的行文字)的短雜湊..."""
    raw = "\0".join([nfc(path), region, heading, line.strip()] + (["完成審"] if done else []))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
```

1. 內容編號的四個輸入之一是 `nfc(path)`——筆記檔案的路徑。
2. 筆記被改名(`git mv A.md B.md`,內容與小標題一字不動)時,`path` 這個輸入變了,雜湊必然變成另一個值,哪怕同一句話、同一個小標題、同一個區塊完全沒動過。
3. `drift ack` 綁的是舊路徑算出的舊雜湊;改名後 `drift check`/`drift scan` 用新路徑重算,得到新雜湊,在表態檔裡查不到 → 判定成「沒表態過」→ 那一行重新落入丙的「要處理」或「只列出」層,即使那行文字連同它所指的程式符號都完全沒變。
4. 本鏡頭派工詞明講要查「表態綁的內容編號在筆記改名…時的行為」,這是直接命中且有具體重現路徑的落差:①`drift ack` 某篇某行 ②該篇改名(不改內容) ③下次 `drift check`/`drift scan`,那一行重新出現在清單裡。
5. 做法 3 第 1 點有處理「檔案:被刪或改名的舊路徑算消失」,但那是指**被改動的程式檔**(丙偵測的對象),不是**筆記檔**本身改名對已存 ack 記錄的影響——兩者是不同的物件,спec 沒有涵蓋後者。

## F4 內容編號不含行號,同一小標題下逐字重複的句子共用同一個編號,一次 ack 會靜默連坐蓋過另一處

severity: minor
blocking: 否 — 觸發面窄(要求同一區塊、同一小標題、文字逐字重複),但一旦發生是靜默的假陰性,值得記下來讓實作者知道這是既有機制的已知取捨、不是這次新引入的 bug。

引句:「工具應綁那一行的內容編號:那行沒改時同一句不再擋、改過就失效照擋」

file: `scripts/lumos:23819-23825`(同 F3 引用的函式定義,雜湊的四個欄位裡沒有行號)

1. `_notelines_content_id` 的雜湊輸入是 `(路徑, 區塊, 小標題, 去空白後的行文字)`,不含行號——這件事本身是 `Systems/筆記內容閘` 既有機制的設計,借用時沒有問題(它原本的用途是標記「這行審過了」,同一句重複審一次也審過沒差)。
2. 但 `drift ack` 的語意是「這句沒過期,照留」,語意比「審過」更強——如果同一個小標題下逐字出現兩次同一句(例如複製貼上留下的重複行,或刻意在兩個情境各寫一次同樣的描述),對其中一行 `drift ack`,雜湊相同的另一行會被判成「已表態、那行沒改過」而一起跳過,即使那一行實際上指的是另一個已經漂移、真的該擋的情境。
3. 重現路徑:同一篇筆記同一小標題下寫兩行一字不差的 `FACT:` 或 `RULE:` 句(各自跟著不同上下文),`drift ack` 其中一行,`drift check`/`drift scan` 對另一行也判成已表態。
4. spec 的〈不做〉第 2 點明講「跨篇重複句偵測…另排,本計劃不動」——那是指**跨篇**;本項是**同篇同小標題內**逐字重複,是既有雜湊函式在新用途(ack)下才會浮現的邊界,沒有被那條排除涵蓋。

## F5 `check` 的效能煞車(名稱數 300、耗時 60 秒、`degraded` 帳)只寫在〈實務隱患〉的敘述裡,沒有對應條款或 `[test:]` 釘住

severity: major
blocking: 是 — 沒有條款與測試釘住的機制,實作時很容易被漏掉或做成「差不多」的版本;而這正是整份 spec 唯一回答「check 會不會把推送拖慢」這個問題的機制,一旦沒被落實,F1 的問題(見上)在 `check` 這條路上會重演,而且沒有測試能抓到迴歸。

引句:「設上限(名稱數 300、耗時 60 秒),超過就印截斷並記 `degraded` 帳,不靜默放行也不無限跑」

file: `scripts/lumos:6604-6614`(`_KNOWN_GATES` 是固定名單,`_gate_event` 對不在名單上的 `gate` 值直接拒寫並只印一行警告——`scripts/lumos:898-901`——如果 `degraded` 要走的是 `kind` 而不是 `gate`,不受這道名單擋,但下一步同樣缺條款去釘死它一定會被寫出來)

1. 對照 S1 全文:只講 `block`/`warn`/`off`/`LUMOS_SKIP_DRIFT_CHECK`/淺層 clone 五種模式與對應事件(`blocked`/`warned`/`skipped-env`/`skipped`),完全沒有提到名稱數上限、耗時上限、或 `degraded` 事件——[test:t_drift_check_gate_modes_and_range] 這條綁定測試因此也不會涵蓋這個上限。
2. 〈做法〉第 0 節第 6 點明講事件種類只有「`blocked`、`warned`、`skipped-env`、`skipped`、`acked`」五種,`degraded` 不在這份正式清單裡——這是內部不一致:〈實務隱患〉段落使用了一個沒有在〈做法〉正式事件清單裡宣告、也沒有條款保證一定會被寫出的事件名。
3. S13(對應 scan)倒是把它的 500 個候選名上限綁進了條款與測試:「候選超過上限時應印截斷 [test:t_drift_scan_dangling_tests_and_symbols]」。同一份 spec 對 scan 的上限有條款、對 check 的上限沒有,是可觀察的內部不一致,而 check 正是掛在每次推送上、影響最直接的那一條路。
4. 實作者若只照 S1–S18 做(這是 spec 唯一列出「必須做」的清單),很可能不會做出名稱數/耗時上限,因為那兩個數字目前只活在一段風險敘述裡,不是驗收條件。

## F6 多 ref 一次推送時,`check` 的效能上限沒有講清楚是「每個 ref 各自」還是「整次推送共用」

severity: minor
blocking: 否 — 需要「同時推多個分支」這個不算罕見但也不算多數情境的操作才會放大,而且已經是 F5(上限本身沒有條款釘住)的下游影響,單獨看衝擊面較小。

引句:「工具應只看這次推送帶進來的觸發、讀被推送頂端提交的樹」

file: `scripts/hooks/pre-push:214-292`(逐 ref 迴圈:`for _ppl in ${_PP_LINES+"${_PP_LINES[@]}"}; do ... done`,home check、note-shape check、pitfalls、spec-gate push-check、code-loop check 都在這個迴圈裡各自對每個 ref 的 `_range` 跑一次)

1. `lumos drift check --diff <起點>..<終點>` 的介面只收一組 diff range,跟同一個迴圈裡的 `home check --diff` `note-shape --diff` 是同一種簽名——照現有 hook 的結構,合理推斷 `drift check` 也是掛在這個逐 ref 迴圈裡,每個 ref 各跑一次。
2. `git push` 一次可以帶多個 ref(例如 `git push origin branch-a branch-b`),`_PP_LINES` 這個陣列本來就是為了處理這種情況而設計(見 `scripts/hooks/pre-push` 開頭的 stdin 讀取註解)。
3. 如果 F5 提到的 60 秒/300 名上限確實是「每次呼叫」的上限(spec 沒有明講是每次呼叫還是整次推送共用一個預算),多 ref 推送會讓這個上限乘上 ref 數——三個分支一次推,理論上限就從 60 秒變成 180 秒,而目前 S1 與〈做法〉都沒有一句話講這件事怎麼算。

---

## 本鏡頭隱患逐類作答(資源與併發)

- **表態檔多寫入者**:已排除單純的並發位元組交錯(append 單一 `write()` 呼叫在本機檔案系統上是安全的既有慣例,`_jsonl_append_verified` 這條路本身沒有問題)。真正的落差是 F3(改名讓既有表態失效)與 F4(同句重複造成連坐)——都是「綁的鍵不夠穩定」而不是「寫入本身不安全」。
- **治理帳寫入頻率**:spec 自己在〈實務隱患〉只把 `Issues/治理帳多個寫入者都沒上鎖` 這篇跟表態檔的「分支合併衝突行」連在一起,但那篇 Issue 講的其實是「同一時刻兩個行程都在寫同一本帳,沒有鎖」這種執行期競態,跟「兩個分支各自 commit 後合併衝突」是不同層次的問題;而 `check` 每次擋下/放行/略過都會呼叫同一支 `_gate_event`(`scripts/lumos:856`)寫治理帳,這正是那篇 Issue 點名的「至少四支寫入器,都沒鎖」裡會多出來的第五支——spec 沒有把這條算進去,也沒有提到那篇 Issue 訂的 2026-10-11 覆核點(`docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md:52`)。但因為 `_gate_event` 目前的失敗策略是「寫不進去也不改變閘的判定,只在 stderr 講一句」(`scripts/lumos:876-879` 的說明),即使真的競態出現,後果是「這筆帳沒留下」而不是「閘判錯」,衝擊面比 F1/F2/F3 小,列在這裡當背景脈絡,不獨立開 finding。
- **推送閘掛鉤先後與互相影響**:見 F1(doctor 的 Z 段沒有掛在既有「便宜先跑」的分級裡,直接繞過那套設計原則)、F5/F6(check 的順序與上限沒有講清楚)。中途被中斷(Ctrl-C、機器睡眠、CI 逾時砍掉)這件事:`_write_lf` 走 tmp→`os.replace` 的單一寫入者原子交換(`scripts/lumos:14164-14178`),中斷在寫暫存檔或换名前都不會動到原檔,單一寫入者這條路是安全的;真正的風險是 F2 講的「多寫入者」而不是「單一寫入者中途被砍」。
- **效能**:見 F1、F5、F6,已用實測數字(`git log -G` 單次 13.3–15.7 秒)證明 F1 不是假想風險。
- **超時策略是否清楚**:不清楚——`check` 的上限只活在敘述裡(F5),`scan`/doctor 的 Z 段完全沒有時間上限(F1),兩條路對「超時要怎麼辦」給出的答案深淺不一,而且都沒有被條款或測試釘住。

---

## 相關既有節點:是否被本設計破壞

- `Projects/code側刪除傳播守衛_計劃`(d0,delguard 只提醒不擋):不影響——丙明講不翻案,而且範圍窄化(只收整檔消失的名稱/只看這次推送帶進來的/只有家筆記與摘要行擋),比 d0 判定過的 delguard 更保守,沒有牴觸。
- `Projects/先問世界_存量掃描裁定`:不影響——PRIOR-ART 段落已經引用並說明沒有採用 Doorstop/Swimm 式錨點的理由(改造成本大於收益),跟該篇的裁定方向一致。
- `Projects/筆記形狀擋_計劃` / `Projects/筆記內容審_計劃` / `Systems/筆記內容閘` / `Systems/筆記內容審`:不影響設計方向,但 F3、F4 指出借用 `Systems/筆記內容閘` 的 `_notelines_content_id` 時,原本在「審過標記」語意下可接受的取捨(不含行號、綁路徑),搬到「表態沒過期」這個更強的語意下會產生新的失效模式——這不是破壞既有決策,是既有機制被新用途放大了原本較小的邊界問題,值得補進本計劃或那兩篇既有節點的〈誠實界線〉。
- `Issues/存量筆記漂移三種機制_rtb根因回饋`:不影響,本計劃就是照它裁的順序在做。
- `Issues/治理帳多個寫入者都沒上鎖`:見上面「治理帳寫入頻率」段——本計劃沒有破壞它的決策(那篇本來就還沒裁定怎麼修),但本計劃是它 REVISIT 時該算進去的下一個受影響對象,而本計劃自己的〈實務隱患〉沒有提到這一點。

---

最嚴重等級 blocker,blocking 共 4 條(F1、F2、F3、F5)。
