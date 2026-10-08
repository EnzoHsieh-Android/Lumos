severity: major

接手-sonnet 席(設計審第 1 輪)。立場:三個月後照 spec 與它印出的訊息做事的人。查證對象是 clone-ns 的 `scripts/lumos`、`scripts/test_lumos.py`、`skills/lumos-project-notes/commands/`、Systems 三個家節點加 delguard。

## F1 c4 帶 --values 先寫檔、事後才發現 c4 沒消失,而且證據頁會鼓勵這種輸入
severity: major
blocking: 是
引句:「驗證磁碟內容等於算出的內容且 c4 消失 → 修復帳」
file: `scripts/lumos:28105`(`_drift_fix_verify` 用 `_drift_no_kind("c4")` 判已處理,在 `_drift_fix_write` 寫完之後才跑)
file: `scripts/lumos:26376`(c4 的判定是 valid_under 全部項目串起來,任一項含「未提交/還沒提交/uncommitted」就成立)
file: `scripts/test_lumos.py:53476`(現有測試就造了兩項都命中的筆記,證據頁標出兩個「← 要改的這項」)
1. 輸入 A:一篇 valid_under 有兩項命中(現有測試 E.md 的第 1、2 項),接手的人照 spec 第 2 節「要改的那項放 `<整項新內容>`」只改一項、另一項照抄。工具算出改後內容、通過乾淨檢查、鎖內寫入成功,驗證時 c4 仍在,印「寫入後內容跟預期不同……工具不自動還原」,不寫修復帳。結果是筆記已被改、帳上沒有、下一項 drift fix 因指紋對不上而被擋。
2. 輸入 B:人把「本工作樹(未提交)」改寫成「原本未提交,已於提交 abc 進主線」。這是最自然的改法,新句子仍含「未提交」,同樣寫完才紅。
3. 那句訊息叫人 `git checkout --` 退回,連同這一篇之前 drift fix 改過、還沒提交的內容一起退掉(`_drift_fix_verify` 自己寫了這一點)。也就是這條新路徑的常見失敗,會讓人丟掉前面已修好的東西。
4. `--dry-run` 只印改前改後,也看不出 c4 會不會留下。
5. spec 第 2 節寫「要改的那項」單數,但證據頁真實會標出多項。要求:算出改後內容之後、寫檔之前,用同一套判定(`_DRIFT_UNCOMMITTED_WORDS`)檢查新的整欄;還有命中就擋下、檔案不動,並且 `--dry-run` 也要報。這是新增行為,要列進條款與測試(現在 S2 沒有)。

## F2 範本句的佔位字 <sha>、<卷證> 沒被擋,會被寫進筆記
severity: major
blocking: 是
引句:「`--values` 各項已由 `_conditions_rewrite` 擋空值、多行、佔位字」
file: `scripts/lumos:15134`(`_set_conditions_locked` 只擋 `_SET_COND_SLOT`=`<整項新內容>`)
file: `scripts/lumos:27622`(`_drift_placeholder_err` 才認 `<sha>`、`<卷證>`,c2 的 --reason 在用,c4 沒接)
file: `scripts/lumos:27951`(範本句在找不到 sha 或卷證時會印成「提交 <sha>;代碼審見 <卷證>」)
1. spec 的「佔位字」指的是 set 現有那一道,只認 `<整項新內容>`。
2. 輸入:reports_via 為 none(spec 自己預期會發生的情形,RETIRE-IF 就在量它)時,範本句含 `<卷證>`。接手的人照 spec「範本句照舊用找到的目錄」把整句貼進 `--values`。
3. 這一項通過空值、多行、佔位字三道,寫進 valid_under;c4 消失,修復帳記 `template_used: true`。筆記裡從此留著字面的「<卷證>」。這正是 `_drift_placeholder_err` 當初為 c2 擋下的同一類事故(存量漂移守衛 WHY 行有記)。
4. 要求:`--values` 每一項另外過 `_drift_placeholder_err`(不能塞進 `_conditions_rewrite`,否則 `lumos set` 行為變了,違反 [S3]);列進 S2 條款。

## F3 c3 --reason 的必改處 spec 沒列全,照字面做 S5 過不了
severity: major
blocking: 是
引句:「`--kind c3` 收選填的 `--reason`(規則同 c2:一行、4 到 200 字、擋提示佔位字」
file: `scripts/lumos:27679`(`_DRIFT_FIX_ALLOWED["c3"]` 是 `{"status","by"}`)
file: `scripts/lumos:27725`(不在允許集合的選項一律回「--kind c3 不收 --reason」)
1. spec 第 2 節為 c4 明寫了要改 `_DRIFT_FIX_OPTS` 與 `_DRIFT_FIX_ALLOWED`,第 4 節 c3 卻只說「收」。
2. 照字面只改 `_drift_fix_c3` 與抽出佔位字檢查,執行 `drift fix ... --kind c3 --status pass --reason "..."` 會先被 `_drift_fix_args_err` 擋成「不收 --reason」,t_drift_fix_c3_reason 第一步就紅。
3. 同類漏列:`cmd_drift_fix` 的參數組裝(`scripts/lumos:38097` 那個 dict 要加 values)、argparse 兩處(`--values` 與 `--reason` 的說明現在寫「c2:」,`scripts/lumos:37595`)、`_drift_fix_load` 裡「c4 不做乾淨檢查」的判斷(`scripts/lumos:27792`,帶 `--values` 時要改成做)。spec 只寫「照慣例」而沒指到這支函式,實作者漏掉的話 --values 會跳過乾淨檢查直接寫檔,違反 spec 第 2 節的話,而且會蓋掉別人未提交的改動。
4. 要求:第 4 節與第 2 節各補一行「改哪個表、哪支函式」。

## F4 lands_in 缺刪除守衛的家,指令文件與舊筆記要同步改哪些沒列
severity: major
blocking: 是
引句:「lands_in:
  - Systems/存量漂移守衛
  - Systems/lumos-cli-write
  - Systems/guard-kill」
file: `docs/lumos-toolchain-knowledge/Systems/delguard.md:34`(about_code 列了 scripts/lumos,cmd_delguard_check 與 `_delguard_parse_diff` 的家是它)
file: `skills/lumos-project-notes/commands/04-自檢與健康.md:11`(寫著 c4 只列證據與 lumos set 指令、「c4 不自己寫檔」,c3 只有 `--status [--by]`)
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:44`(PITFALL 寫「drift fix --kind c4 只列證據……以程式為準」,第 77 行同)
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:41`(WHY 寫「c4 只給證據由人給要換的片段」)
1. 第五條(刪除守衛)改的函式家在 Systems/delguard,不在三個 lands_in 裡。CLAUDE.md 鐵則 5:改到哪支檔、寫進那支檔的家。實作者按 lands_in 寫回,delguard 節點不會被更新,而它的 KEY 行寫著「vendored 白名單源 repo 反轉語意」屬已知殘項,這次的跳過行為正好落在這裡。
2. 指令文件 `commands/04`(第 11 行)與那三處舊句,實作後會直接說謊:接手的人讀到「c4 不自己寫檔」會去手貼 `lumos set`,走進不記帳的那條路(見 F7)。spec〈範圍〉〈回退〉都沒有列這些檔。reference.md 查過沒有 drift fix 段,不用改。
3. 這也翻掉 Enzo 2026-09-30 才裁的「c4 只列證據、改走 lumos set」。spec 的依據只引「照順序做」,沒有記這條翻案。應該 `lumos decision-add` 一筆,並把存量漂移守衛第 44 行標成被取代,否則之後的 session 讀到兩句互相矛盾的筆記。
4. 回退節只講 `_drift_c4_print` 與 `--values` 一起拿掉。實際要跟著還原的還有 F3 那幾個表、`_drift_fix_hint` 的 c4 文字、上述文件。

## F5 使用者看得到的舊文字與既有測試會跟新行為打架
severity: minor
blocking: 否
引句:「證據頁印的指令改成這一條;」
file: `scripts/lumos:27652`(`_drift_fix_hint` 對 c4 印「列證據、範本與預填好的 lumos set 整欄指令(c4 不自己寫檔)」,推送閘、scan、doctor Z 段都從這裡拿)
file: `scripts/test_lumos.py:53497`(t_drift_fix_c4_evidence_then_replace 斷言證據頁的預填指令就是 `lumos set ...`)
file: `scripts/lumos:36736`(drift fix 的說明寫「c4 換掉還沒提交的前提」)
1. spec 只提證據頁的指令改掉。三個入口(擋下訊息、scan 清單、doctor)印的是 `_drift_fix_hint` 的括號說明,實作後會寫「c4 不自己寫檔」,與行為相反。
2. 上述既有測試在指令改成 drift fix --values 後會紅,spec 條款只列了新測試,沒說這條要改寫還是保留(它同時在釘 lumos set 擋佔位字,那一段要留)。
3. 要求:spec 列出這兩處要改,或註明測試拆成兩支。

## F6 RETIRE-IF ① 的指標分不出它要撤的東西,REVISIT 也沒人有辦法去量
severity: minor
blocking: 否
引句:「修復帳裡 c4 的 `reports_via` 在工具鏈與 rtb 合計有一半以上是 `none`(兩種找法都查不到)→ 撤掉同提交找法」
file: `scripts/lumos:28122`(修復帳只在 --values 寫成功時才記一筆)
1. `none` 表示兩種找法都沒找到,撤掉同提交找法不會讓它變好。要判同提交找法值不值得留,得比 same-commit 與 name 的占比,以及 same-commit 找到的目錄後來有沒有被人採用。現在的門檻在「兩者都零」時才觸發,卻叫人撤其中一個。
2. 母體偏誤:證據頁找不到目錄的人最可能放棄走 drift fix、改用 `lumos set` 或手改,這些不進帳,none 的比例被低估;`name` 找到錯誤目錄也算成功。
3. 沒有工具能彙整帳。「工具鏈與 rtb 合計」需要讀 rtb repo 的 governance/drift-fixes.jsonl,spec 沒寫誰在 2026-11-30 去取、用什麼指令算(接手的人拿到 REVISIT 那行,只知道要「量」)。RETIRE-IF ② 是「有人回報」,沒有機制看到「跳過而漏掉」(見 F9)。
4. 要求:寫出量法指令(例如一行 jq 或 `lumos drift stats`)、指標改成 same-commit 與 name 的採用比,並說明誰去 rtb 拿帳。

## F7 lumos set 與 drift fix --values 兩條路並存,沒有任何一邊會提醒走錯
severity: minor
blocking: 否
引句:「`lumos set <節點> valid_under …` 照舊可用,但不記修復帳;證據頁只印 drift fix 那條。」
file: `skills/lumos-project-notes/commands/04-自檢與健康.md:11`
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:18`(寫著 c4 證據頁預填的是 set 指令)
1. 三個月後的接手者面對的是舊文件(F4)、舊筆記、rtb 記憶裡的 lumos set 流程。走 set 那條:c4 消失、修復帳沒有、也不會有任何訊息。
2. 更實際的後果:同一篇驗證紀錄常同時有 c3 與 c4。先用 set 修 c4(檔案跟 HEAD 不同、也不是帳上最後一筆的指紋),再修 c3 會被乾淨檢查擋成「有未提交的改動(不是 drift fix 自己留下的)」,得先提交才能繼續;反過來則不會。方向不對稱,接手者不知道要調順序。
3. `lumos set` 改 valid_under 時,若那一篇現在有 c4 且改完後 c4 消失,可以多印一行「這一筆漂移也可以走 drift fix --kind c4 --values 記進修復帳」,但這會動到 set 的輸出,與 [S3]「訊息一字不變」衝突,所以只能靠文件。建議把這個限制寫進 `commands/04` 與存量漂移守衛〈誠實界線〉。

## F8 --values 帶頭尾空白時 check 與寫入內容不一致
severity: minor
blocking: 否
引句:「`check=lambda f: _conds(f.get("valid_under")) == vals`」
file: `scripts/lumos:15129`(`_set_conditions_locked` 的 vals 是先 strip 過的)
1. spec 對 `_conditions_rewrite` 的回傳只有(改後行, 錯誤訊息),沒有 strip 後的 vals;`res["check"]` 用的 `vals` 卻是呼叫端手上的 `--values` 原字串。
2. 輸入:`--values "本項 " "另一項"`(shell 複製貼上常帶尾空白)。檔案寫的是 strip 後的,check 用的是原字串,`atomic_write_verify` 與後面的驗證判不一致,印「寫入後內容跟預期不同」,筆記已寫、帳沒記。
3. ⚠ 判不準實作者會怎麼取 vals,但 spec 沒說,兩種都可能。要求:呼叫端先 strip 再傳,或 `_conditions_rewrite` 多回一個 vals。

## F9 c1 訊息的「已經是轉正後的說法」漏了手補段落刪掉 settle 句之後的狀態
severity: minor
blocking: 否
引句:「settle:正文有「(日期 已轉正)」那一行,或既有 `settle-del` 已判出下一行是手補的「已轉正」段。」
file: `scripts/lumos:12115`(`settle-del` 只在 settle 句還在時才產生)
file: `scripts/lumos:12146`(改寫時 `seen.add("settle")`,之後那一句已被刪掉)
1. 輸入:先前某次 c1 已經因手補的「2026-09-20 已轉正」段刪掉 settle 句;之後這篇又因別的預告句(例如 TEST)被 c1 列出。此時正文沒有 settle 句,也沒有「(日期 已轉正)」那一行,只有手補段落。
2. `_guard_prose_settled(lines, "settle")` 依 spec 回 False,訊息又講「找不到 settle 句,可能被手改過」,正是 rtb 抱怨的誤導。
3. 要求:settle 這一種也認 `_GUARD_MANUAL_SETTLED_RE` 在正文任何位置出現;TEST 的辨認若要涵蓋手改過的「TEST:預告已轉正」(沒有 [日期])要寫明認不認。WHY 那一種 spec 寫「沿用 why-done」,但 `_guard_settle_rewrite` 已把 why-done 算進 seen,WHY 本來就不會進 missing,那一句是多餘的,不影響。

## F10 刪除守衛跳過工具檔:額外 git 呼叫沒算進預算,跳過了多少也看不到
severity: minor
blocking: 否
引句:「`cmd_delguard_check` 先判 `_is_toolchain_repo(root)`:是工具鏈本身就不跳」
file: `scripts/lumos:17765`(`_vendored_state(root, "")` 對 17 支工具檔各跑一次 `git show`,每次逾時 20 秒)
file: `scripts/lumos:29423`(delguard 的 15 秒預算在 `git diff` 之後才開始計 `_over()`)
1. 消費專案每次提交都會多 18 次 subprocess,而且是無條件的,不管這次 diff 有沒有碰到工具檔。spec〈效能〉只寫 c4 的那次 git show,漏了這條,也沒說要不要在 diff 完全沒碰工具檔路徑時短路。
2. 最壞情形(git 卡住):17 次逾時,遠超 15 秒預算,這是 advisory 守衛,不能讓 pre-commit 卡住。要求:先看 diff 有沒有碰到 `_VENDORED_ALL` 的路徑再讀索引,或把這步放進 `_over()` 的判定。
3. 量測:RETIRE-IF ② 說「漏掉真的過期句(有人回報)」,但被跳過的符號不會出現在任何輸出。要能在 2026-11-30 回頭,應該在 delguard 的治理帳記一筆「因工具檔跳過而少抽的檔數」。

## 各節與合約結論(非 finding)
- 已讀,無 finding:〈範圍〉〈不做〉、〈做法〉第 1 節(卷證目錄:`git show -z --name-only --diff-filter=A --format=` 與 `core.quotePath=false` 的用法、退回路徑、`_esc_clean` 都對得上現有函式)、〈誠實界線〉。
- 合約判定:Systems/guard-kill 兩條 ★INVARIANT★(guard kill rc 優先序、--json stdout 恰一行 JSON)不受影響,這份設計只動 settle 與 c1 的提示句,不碰 guard kill 的 rc 與 JSON 路徑。Systems/lumos-cli-write 與 存量漂移守衛、delguard 沒有 ★INVARIANT★ 行;但 lumos-cli-write 第 18 行的 WHY 綁 `t_drift_fix_c4_evidence_then_replace`(set 擋佔位字),抽 `_conditions_rewrite` 時必須把佔位字檢查連同搬過去並保持在 set 的執行順序第一位,否則那條 WHY 的綁定測試翻紅。
- rtb 五條對照(依據只有跨會談訊息,repo 內沒有 rtb 的原話與案例,只能對照 spec 的白話段,⚠ 無法逐字核對):
  1. c4 卷證目錄找不到:同提交找法在「筆記與卷證同一提交」成立時解得掉;分開提交時仍退回猜名字,spec 已承認。解。
  2. c4 改完帳上沒紀錄:走 --values 才解;走 set 仍不記(F7)。條件式解,依賴文件把人導過去(F4)。
  3. c1 訊息把已改好講得像出錯:TEST、whynot 解;settle 在手補段落的狀態沒解(F9);手改過但字樣不同的 TEST 句仍會講「找不到」。部分解。
  4. c3 沒法寫理由:設計解,照字面實作會被「不收 --reason」擋(F3)。
  5. 刪除守衛誤報工具檔:消費專案且清單一致時解;更新工具的提交若沒把 `.lumos/vendored.json` 一起 stage,索引裡的清單是舊指紋,一律判不一致、不跳過,spec 沒提這個前提。⚠ 未實測(需要真的做一次工具更新提交)。
- 實務隱患逐類:併發(c4 寫入走既有鎖與指紋比對,無新洞,除 F1 的寫後才驗);資安(卷證目錄名印出前過 `_esc_clean`,貼進筆記的範本句沒消毒,但目錄名來自 git 檔名,含控制字元時 `_drift_one_line` 會擋,無新洞);不可逆(F1 的還原訊息會連帶退掉同篇先前的修復,列入 F1);效能見 F10;金流、對外送出:無,純本機工具。

最高等級:major;blocking 共 4 條
