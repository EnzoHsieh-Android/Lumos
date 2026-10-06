severity: major

## 先讀的結論

**用真帳算過一輪。** 在審查帳和治理帳(`docs/.canary-log.jsonl`、`docs/.governance-log.jsonl`)裡,2026-08-26 之後開的非 light、帶輪次迴圈共 267 個。
- 輪數超過上限的有 19 個,其中 17 個最後是 converged。
- 判法①(`cap-reached` 事件):全帳只有 3 筆,都是 2026-08-24 以前的。
- 結論:實際會觸發的幾乎只有判法②,而且多數是「破例多一輪後過閘」的迴圈,不是「跑滿沒過」。

---

### F1 「跑滿未過」的實際觸發面是破例再一輪,和 d4 的語意對不上
severity: major
blocking: 是 — 日常的「全折後派新席複核差異」流程會被硬擋,並被迫多寫一份回顧

- spec 段落:〈名詞〉「跑滿未過」、〈三〉擋點 1 與 2、決策 d4。
- 問題:判法②(帳上輪數超過上限)只數相異輪次 id,不看最後有沒有過閘。
  - 輪數統計用 `len({r["round"] ...})`,見 `scripts/lumos:12943`。
  - 輪次 id 可以是 `r3b`、`r3-dref`、`r4-dref-delta` 這類複核輪。
- 具體輸入→結果:
  - `code-純文件子集` 的輪次是 `r1,r2,r3,r3b`,`code-文件子集收緊` 也是。
  - 這兩個迴圈 r3 折完後派新席複核,帳上就成了「第 4 輪」。
  - 上線後同形狀的迴圈:記 `r3b` 的第一席被 S1 回 2,gate 第八步 ✗,要派乾淨代理起草回顧、補寫、`--record` 才能繼續。
  - 但 d4 明說「剛好在最後一輪過閘的不算」;這種迴圈本質上就是在 r3 過閘。
- 「破例再一輪後過閘」的迴圈在 d4 的取捨裡沒被算進成本,d4 的「近期約六成」估算也沒重算。
- 真帳旁證:
  - 上述 19 個超上限迴圈中 17 個 converged,只有 2 個沒有 converged 事件。
  - 退場條件③「三個月內零次跑滿未過」對判法①成立得很快,但判法②不會零。退場條件沒有拆開兩種判法。

引句:「帳上輪數已超過上限(到上限沒過才會破例再開一輪)」
引句:「剛好在最後一輪過閘的不算(Enzo 2026-10-05 裁,見決策 d4)」

file: `scripts/lumos:12943`

---

### F2 判法①把「cap-reached 後又 converged」的迴圈算成跑滿未過,且擋點對「剛好到上限」的實例完全不擋
severity: major
blocking: 是 — 分母與提醒清單永遠含已過閘的迴圈,且動機實例(3 輪折完、不開第 4 輪)沒有任何機械擋

- spec 段落:〈名詞〉判法①、〈三〉擋點、〈四〉doctor、S10、S11。
- 問題一:`cap-reached` 事件由 `loop next` 在 `rounds_count >= cap` 且閘沒過時寫(`scripts/lumos:13248-13249`)。
  - 同一個 3 輪迴圈,閘因引句錨定、spec 被改或其他可修原因暫時 FAIL,被寫了 `cap-reached`。
  - 修完再問閘,過了,又寫 `converged`。
  - 此時「治理帳有這個編號的 cap-reached 事件」成立,但這個迴圈是剛好在最後一輪過閘的。
  - 既有統計 `scripts/lumos:8145` 的口徑是「cap-reached 且沒有 converged、沒有 rewrite」。
  - spec 沒沿用這個口徑,所以 doctor、retro-stats 的「兩者都沒有」清單會永遠列著它,只有 `--skip` 能清掉。
  - 被 `rewrite` 收尾的舊編號同理,會一直被唸。
- 問題二:真正卡在剛好 3 輪的迴圈,三個擋點都不擋。
  - S1 只擋「第 4 輪」。
  - 第八步只管「輪數已超過上限」。
  - `loop next` 只多印一行。
  - 〈為什麼要做〉的實例 `code-lumos事件帳`(三輪、Enzo 裁全修不開第四輪)上線後不會被擋,只剩 doctor 唸。
  - 這跟〈一句話〉「要先留…才能繼續」的承諾不一致,〈誠實界線〉只承認「人裁直接放行」沒擋,沒提這一格。

引句:「治理帳有這個編號的 `cap-reached` 事件」
引句:「要先留一份固定格式的「跑滿回顧」才能繼續」

file: `scripts/lumos:13248`、`scripts/lumos:8145`

---

### F3 上線時刻比較沒指定時區處理,真帳已有 +00:00 的列
severity: major
blocking: 是 — 界線附近的迴圈會被誤判為「上線前」而不擋不唸,或反向誤擋

- spec 段落:〈適用範圍〉「只管上線之後」、S4。
- 問題:spec 只說「精確到秒的程式常數」與「看迴圈首筆帳的時間」,沒說怎麼比。
- 真帳數據:審查帳 3028 列裡有 95 列是 `+00:00`,其餘 2933 列是 `+08:00`。
  - 最新一筆 `+00:00` 是 2026-10-05T08:15:48,離今天很近。
  - 這些列來自 `code-結案連帶掃描`、`code-鎖身份含內容`。
- 具體輸入→結果:
  - 常數若寫成 `2026-10-05T23:00:00+08:00`,首列 `2026-10-05T16:00:00+00:00`(實際 00:00 +08,已在上線後)。
  - 用字串比,`"…T16…" < "…T23…"` 成立,被判為上線前。
  - 該迴圈跑滿也不擋不唸。
- 既有慣例就在隔壁:`_loop_ts_key`(`scripts/lumos:10320` 附近)專門處理這件事,落點步驟 `_disposal_landing_step`(`scripts/lumos:22646`)已拿它比時間。spec 沒要求沿用。
- 「首筆」也有歧義:3 個迴圈的列不是依時間遞增。落點步驟取 `min(keys)`,spec 寫的是「首筆」。
- 另外 `_loop_ts_key` 對沒帶時區的 ts 回 None。spec 沒說 None 時往哪邊判,S4 也沒有對應測資。

引句:「判斷看迴圈首筆帳的時間,首筆早於上線時刻的不擋也不唸」

file: `scripts/lumos:22646`

---

### F4 「合格回顧」定義與 S3 互相矛盾,跳過事件一筆就永久免疫
severity: major
blocking: 是 — 條款 S3 在有跳過事件時不可能成立,擋點可被一筆 10 字的跳過永久關掉

- spec 段落:〈名詞〉合格回顧、S3、〈二〉`--skip`、〈四〉。
- 問題:合格回顧是「(回顧檔合格且最新 `cap-retro` 指紋相符) 或 (治理帳有一筆 `cap-retro-skipped`)」,「有一筆」不限新舊。
- 具體輸入→結果:
  - r4 前先 `--skip --note "xxxxxxxxxx"`(10 字)。
  - 之後不論開到 r5、r8,都不再需要回顧。
  - 也沒有任何輪次變動會讓它失效;回顧檔反而會因 `rounds` 不一致失效(〈一〉)。
  - 同一編號先 `--record` 後檔被改,指紋不符,但只要曾有 skip 事件,閘就判合格。S3 要的「應 ✗ 並叫人重新 `--record`」就不成立。
- 順序語意也沒寫:skip 在 record 之後、或 record 在 skip 之後,「最新一筆」是 `cap-retro` 還是兩種事件混合比較,spec 沒說。
- 退場條件②「跳過次數多過寫了回顧的次數」也沒定義單位。同一編號每多一輪就 `--record` 一次,事件數會比迴圈數多,比較會偏向「回顧多」。

引句:「或治理帳有一筆 `cap-retro-skipped` 事件」
引句:「指紋不符(記帳後被改)應 ✗ 並叫人重新 `--record`」

---

### F5 寫治理帳照 `_loop_gov_mark`,失敗無聲,`--record` 與 `--skip` 會回 0 卻沒寫進去
severity: major
blocking: 是 — 擋點全部建在一筆可能沒寫進去的事件上,使用者得不到任何失敗訊號

- spec 段落:〈名詞〉合格回顧、〈二〉`--record`、`--skip`、〈實務隱患〉併發。
- 問題:`_loop_gov_mark` 把所有例外吞掉(`scripts/lumos:971-980`)。其底層 `_append_governance_log` 還有兩個無聲出口:
  - 取不到 `git rev-parse --short HEAD`(空 commit)就 `return`(`scripts/lumos:1564-1565`)。
  - 寫檔 `except OSError: pass`(`scripts/lumos:1580-1583`)。
- 具體輸入→結果:
  - 在非 git 目錄、剛 `git init` 無 HEAD、或帳檔唯讀時,`lumos loop retro X --skip --note "…十字以上"` 印成功、回 0。
  - 帳上沒有事件,`canary record` 仍被 S1 擋,閘仍 ✗。
  - 使用者重跑 skip 也一樣,沒有診斷訊息。
- repo 內已有現成的有回傳值寫入器:`_gate_event`(`scripts/lumos:1445`)的註解寫明「回傳值要被看」,因為吞錯會留下假紀錄。spec 沒採用,反而指定 fail-open 的那支。
- 指紋欄位無處放:`_loop_gov_mark(env, loop_id, kind, note)` 只收 `note`,spec 要的「路徑與 sha256」只能塞進 `note` 文字再解析回來。
  - 編號含空白、或 `note` 含 `sha256` 字樣時解析會錯。
  - spec 沒定義 `note` 的格式。

引句:「治理帳寫入照 `_loop_gov_mark` 既有做法(失敗不擋)」

file: `scripts/lumos:971`、`scripts/lumos:1564`、`scripts/lumos:1580`、`scripts/lumos:1445`

---

### F6 編號檢查指定的是較弱那一支,`.`、空字串、控制字元、NUL 都漏
severity: minor
blocking: 否 — 有現成更嚴的正則可換,且不影響主流程

- spec 段落:〈一〉位置。
- 問題:`cmd_loop_replay` 的檢查只擋 `/`、`\`、`..`(`scripts/lumos:1041`)。同檔另有較嚴的 `_FIX_ID_BAD_RE`(`scripts/lumos:12258`),多擋控制字元與 DEL。
- 具體輸入→結果:
  - 編號 `.`:路徑成了 `governance/review-reports/./cap-retro.json`,回顧檔落在 `review-reports/` 根,跨編號共用一份。
  - 編號 `""` 或純空白:同樣沒被擋(replay 檢查沒有 `strip`)。
  - 編號含 NUL:後續 `Path`/`open` 丟 `ValueError`,違反 S7「不丟錯誤堆疊」。
  - macOS APFS 預設不分大小寫:`Code-X` 與 `code-x` 是兩個編號,卻落同一個資料夾。「`-v2`、`-std`…各自一份,不會互相覆蓋」的保證,在大小寫與 NFC/NFD 變體上不成立。
- 回顧檔裡的 `loop` 欄雖然要等於指令給的編號,只會讓第二份被判不合格,不會避免被覆寫。

引句:「編號含 `/`、`\`、`..` 一律拒絕(照 `cmd_loop_replay` 既有的編號檢查)」

file: `scripts/lumos:1041`、`scripts/lumos:12258`

---

### F7 共用函式遇到壞帳(亂序、非字串 round)時三個呼叫端怎麼辦,spec 沒寫
severity: minor
blocking: 否 — 只在手改帳或損壞帳時出現,但 S1 的兩種失敗方向都有害

- spec 段落:〈適用範圍〉、〈三〉擋點 1、S1、S7、〈四〉。
- 問題:共用判定要靠 `_disposal_round_groups`。它在以下情況回錯,不是回輪數:
  - 輪次被別輪隔開後重現,例如 `r1,r2,r1`。
  - 輪次以 `__` 開頭。
  - `round` 若是非字串,`rid_.startswith` 直接 `AttributeError`(`scripts/lumos:22490`)。`_cap_hint_print` 用 try 包住,spec 的新呼叫端沒說也包。
- 具體輸入→結果:
  - 帳上有 `round: 3`(int)的手改列時,`canary record` 在 S1 檢查處丟堆疊。
  - 若回錯就「照常寫帳」,則壞帳可繞過擋點。
  - 若回錯就「擋」,則只剩 `--skip` 出口,而 F5 又讓 skip 可能沒寫進去。
- doctor 段「一個帳列壞了只略過那一個」有寫,但 S1 與 `--check` 的 `rounds` 比對沒寫。
- 順帶:`_loop_records` 用 `read_text(encoding="utf-8")`(沒有 `errors=`),非 UTF-8 的帳在 `UnicodeDecodeError`(不是 `OSError`)處炸出堆疊(`scripts/lumos:11815`)。S1 新增的檢查會把這個既有洞帶進 `canary record` 的新路徑。

引句:「若帶輪次的迴圈要記的新一輪會讓輪數超過分級上限、而且沒有合格回顧,則 `canary record` 應回 2 且不寫帳」

file: `scripts/lumos:22490`、`scripts/lumos:11815`

---

### F8 證據路徑檢查有三個沒寫的邊角
severity: minor
blocking: 否 — 只影響回顧檔可信度,不影響閘的主流程

- spec 段落:〈一〉`evidence`、S6。
- 問題:
  - 比對方式只寫「要是帳上某一列的 `report_path`」,沒說字串正規化。真帳 `report_path` 有 2 列絕對路徑。
    - 一列是 `/Users/enzo/.claude/projects/.../agent-….jsonl`,一列是 `/private/var/folders/.../report.md`。
    - 若檢查是逐字相等,`./governance/...`、重複斜線、反斜線都過不了;若有正規化,spec 沒寫。
  - 真帳另有 17 列 `report_path` 指向不存在的檔,例如 `visual-baseline-sop` 那批。只寫路徑不加條號即可通過,等於可以引用已不存在的報告;加了 `#F<n>` 才會因讀不到而失敗。
  - `#F<n>` 的拆法沒寫:路徑含 `#` 時用 `split` 還是 `rsplit`。
  - 共用條號辨識函式會略過標題含「已驗過／沒問題／已看,無」等字樣的 `F` 段(`scripts/lumos:8706`)。起草者引用「F3 已驗過…」那種標題時會被判成找不到。
- 與 S13「共用函式取代原寫法」的行為不變,並不衝突,但 `--check` 的錯誤訊息應告知這點,spec 沒要求。

引句:「路徑要是這個編號帳上某一列的 `report_path`(不接受其他檔)」

file: `scripts/lumos:8706`

---

### F9 凍結第二趟跳過第八步,凍結判定可以存成 PASS,而即時閘是 FAIL ⚠
severity: minor
blocking: 否 — 判不準有沒有人信任凍結判定當放行依據,標 ⚠

- spec 段落:〈三〉擋點 2、d5。
- 問題:凍結流程第二趟帶 `spec_sha_override`,第八步印「—」不重判,`verdict.json` 的 `rc` 取自這一趟(`scripts/lumos:1068-1073`、`scripts/lumos:1102`)。
- 具體輸入→結果:
  - 沒有回顧的第 4 輪迴圈,即時閘第八步 ✗(FAIL)。
  - 凍結存下的 `verdict.rc` 卻是 0。
  - spec 只說「凍結本來就容許存 FAIL 判定」,沒處理這個相反方向:凍結產出的 PASS 並不代表第八步看過。
- 我在 `scripts/lumos` 裡沒找到會把 `verdict.json` 當放行依據的呼叫端(`governance/replay/` 只出現在凍結寫入與 bookkeeping 目錄清單),所以標 ⚠。若手冊或 pre-push 拿凍結判定當證據,才會變成實際繞過;建議 spec 明寫凍結的 verdict 不涵蓋第八步。

引句:「凍結的第二趟與回放(帶 `spec_sha_override`)印 — 不重判」

file: `scripts/lumos:1068`、`scripts/lumos:1102`

---

## 各節核對

- 名詞、做法〈一〉〈二〉:見 F1 至 F8。
- 〈三〉擋點 3(loop next):已讀,無獨立 finding。`loop next` 以 `readonly=True` 問處置閘,第八步會跑,沒有越權。
- 〈五〉誰來寫:已讀,無 finding。五處到頂句與指令速查確實存在。我查到的行號:
  - `skills/lumos-code-loop/SKILL.md:59`
  - `skills/lumos-code-loop/reference.md:211` 與 `:586`
  - `skills/lumos-design-loop/SKILL.md:65`
  - `skills/lumos-design-loop/reference.md:332` 與 `:542`
  - `skills/lumos-project-notes/commands/05-設計審查迴圈.md:29`
- 〈實務隱患〉效能:已讀,無 finding。治理帳 119,919 行(19MB),全掃一次約 0.3 秒,可接受。
- 〈回退〉:已讀,無 finding。

總結:最嚴重 major,blocking 4 條
