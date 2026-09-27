severity: blocker

# 審稿記錄(鏡頭:回滾)

## frontmatter / 白話 / 依據 / PRIOR-ART / RETIRE-IF / REVISIT(第1–25行)

三個計劃連結節點逐條判(是否破壞其宣稱行為或合約):

- 「Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋」:不是合約節點(無 `[test:]`/`[audit:]` 綁定),是這份 spec 直接執行的決策來源(d1–d6)。本 spec 是在落實它記下的決策,不構成破壞。
- 「Systems/pitfalls-code-loop」:這是有 ★INVARIANT★/`[test:]` 綁定的合約節點(例如 d4→d7「擋推鏈恆以 --no-lint 跑 pitfalls」「新增告警閘」等)。本 spec 沒有修改 `cmd_pitfalls`/`cmd_code_loop`,是另開一條 `note-audit` 指令族,不觸及它已宣稱的行為,不構成破壞——但它抄的是「代碼審留痕閘」這個機制殼,沒有抄到同一份文件裡緊鄰記載的「個別專案關閉開關」慣例(細節見下方 F4)。
- 「Systems/外部對照-code衍生wiki」:它的論點是「lumos 的價值在程式碼推不出來的那半,圖譜不該是 code 的衍生投影」。本 spec 進一步收窄「現況描述」的允許範圍,方向與它一致,不構成破壞。

本節其餘文字(判定者小實驗摘要、RETIRE-IF/REVISIT 日期)已讀,無 finding。

## 判定者能不能用:小實驗(第27–38行)

已讀,無 finding(小實驗本身的可信度不在回滾鏡頭範圍內)。

## 做法·第一層(第42–49行)、條款 S1–S3(第65–67行)

## F1 「已排除:不可逆」這句安全網對第一層不成立

severity: major
blocking: 是 —— 不改,實作者會誤信「刪掉的內容都能從 git 找回」而不去做任何真正的救回機制,遇到需要救回時才發現救不回來。

引句:「已排除:不可逆:筆記內容刪了可以從提交紀錄找回,閘拿掉即恢復原狀」

逐條說明:
1. 第一層(S1/S3)是 pre-commit hook,擋下時用 `exit 1` 中止,git 的標準行為是**在 pre-commit 回非零時完全不建立 commit 物件**(githooks(5) 定義的行為,現有 hook 也是靠這個機制運作)。file: `scripts/hooks/pre-commit:200` 是既有 Gate 2(改碼沒動圖譜)擋下時的 `exit 1`;file: `scripts/hooks/pre-commit:64` 起的 Gate 1、`:91` 起的 Gate L 是同一種擋法。新的 S1/S3 檢查會加在同一支腳本裡,擋法必然一樣。
2. 因為沒有 commit 物件,就沒有對應的 git 提交紀錄、也沒有 reflog 項目可尋——「從提交紀錄找回」這句話對第一層的擋下場景在字面上不成立:那段文字從頭到尾只存在於作者的工作目錄裡,還沒進版控。
3. 這句安全網只對第二層(S8,推送前查核)成立,因為第二層作用時 commit 早就已經存在於本機分支——那時真的能「從提交紀錄找回」。spec 把兩層的安全網寫成同一句話,沒有區分「commit 建立前被擋」與「commit 已存在但推送被擋」是兩種不同的可救回程度。
4. 具體會出錯的輸入:作者寫了一段命中 S1(含 `檔名:行號`)的新句子,`git commit -a` 被 pre-commit 擋下;作者接著跑 `git checkout -- <該筆記檔>`(以為是在還原剛才某個不小心的改動,或用了會清工作目錄的腳本/IDE 動作)——那段文字這時候真的永久消失,沒有任何提交紀錄可找。

## 做法·第二層、規範文字跟著改(第51–61行)、條款 S4–S10(第68–74行)

已讀,無 finding(判定者派工詞、申訴機制、指紋綁定的機械驗證邏輯本身不在回滾鏡頭範圍;規範文字改法見下方 F4 的延伸討論)。

## 回退(第76–80行)

## F2 回退清單漏列 `lumos set` 裡的第三個檢查點

severity: major
blocking: 是 —— 不改,回退後 `lumos set <計劃> status done` 仍會照 S2 擋人,跟「回退」的字面承諾矛盾,也沒人知道該去哪裡關掉。

引句:「拿掉提交前與推送前那兩處呼叫即可,不留狀態」

逐條說明:
1. S2 條款(計劃第46行)明講:「`lumos set <計劃> status done` 也先檢查一次,早一步講」——這是**第三個**接線點,獨立於「提交前」與「推送前」的 hook 呼叫之外,直接嵌進 `lumos set` 這支指令本身的邏輯。
2. file: `scripts/lumos:14283` 的 `_cmd_set_locked` 目前對 `status` 這個 key 只有「同步 `status/*` 標籤」的邏輯(見 `:14309-14320`),沒有任何跟「done 且現況段沒收窄」相關的分支——S2 要求的檢查必須是新插進這支函式裡的程式碼,不是掛在 hook 上的一次呼叫。
3. 回退段只講「拿掉提交前與推送前那兩處呼叫」,完全沒提到要同時拿掉 `_cmd_set_locked` 裡新增的這段邏輯。字面上照做回退清單走的人,會留下一個沒人知道還在運作的第三個擋點:整個機制的「回退」在文件層級上宣告完成,但 `lumos set` 這個入口實際上還在擋。

## F3 CI 接線不隨 `lumos update` 走,回退清單完全沒提到它

severity: blocker
blocking: 是 —— 漏改 CI 這一步,輕則 CI 永遠對「動到筆記的推送」誤擋(找不到已撤掉指令的通過紀錄),重則 CI 直接崩潰(呼叫一個已經被移除的子指令),擋住所有人的推送,而且沒有本機訊號能提醒維護者去查 CI 檔本身。

引句:「推送前與 CI 用同一支指令對整段範圍再跑一次」

file: `.github/workflows/ci.yml:98` 目前的「code-loop gate」步驟是手寫在 workflow 檔裡直接呼叫 `python scripts/lumos code-loop check`(同檔 `:113`),不是靠 vendored 檔案同步過去的。
file: `scripts/lumos:16888`(`_VENDORED_TOOLKIT`)與 `scripts/lumos:16896`(`_VENDORED_TREE_FILES`)是 `lumos update` 唯一會同步的檔案清單(見 `scripts/lumos:17158-17169` 的 `_vendor_toolchain` diff 自癒迴圈),兩份清單都不含 `.github/workflows/ci.yml`。

逐條說明:
1. S4(範圍重跑第一層)與 S8(指紋通過紀錄)都明講「CI」要跑同一套查核,而 CI 的接線方式——照這個 repo 自己現有的 `code-loop gate` 那步——是人工寫進 `.github/workflows/ci.yml` 的一個 step,不是被 `lumos update` 自動安裝或撤回的檔案。
2. 這代表:第一層/第二層要真正在 CI 生效,需要有人手動編輯 `.github/workflows/ci.yml` 加一步;而回退時,如果只做了「拿掉提交前與推送前那兩處呼叫」(第一層)、「拿掉推送前與 CI 的查核」(第二層字面上有提到「CI」,但沒講怎麼拿掉、也沒講這件事跟 `lumos update` 無關),很容易漏掉這一步——因為維護者的直覺會是「跑一次 `lumos update` 就會把工具鏈同步回舊版」,但 CI workflow 檔不在同步範圍內,必須另外手動改。
3. 具體會出錯的輸入:團隊決定回退,改回舊版 `scripts/lumos`(移除 `note-audit` 子指令)並要求所有消費專案 `lumos update`;`lumos-toolchain` 自己的 `.github/workflows/ci.yml:98` 那步如果沒人同步手動改掉、且原本已經按 S4/S8 加了呼叫 `note-audit check`(或範圍重跑第一層)的 CI 步驟,下一次 push 到 CI 時,`python scripts/lumos note-audit check ...`(或等價指令)會因為子指令已經被移除而回傳非零甚至直接是「invalid choice」的 argparse 錯誤——CI 對*任何*推送(不限是否動到筆記)全部變紅,而且錯誤訊息不會指向「這是回退沒做完」,只會像是工具鏈本身壞掉。

## 實務隱患(第82–93行)

## F4 消費專案沒有個別關閉開關,回退對它們是被動的、有時間差的

severity: major
blocking: 是 —— 不給出獨立開關,單一消費專案想在中心倉庫決定回退之前(或之後暫時)關掉這道閘,唯一手段是逐次 `git commit/push --no-verify`,而 spec 自己在別處把 `--no-verify` 定位成「留痕例外」而非正常操作模式,兩者矛盾,會實際卡住那些專案的日常推送直到有人手動介入。

引句:「那支指令是從工具鏈原始 repo 拉進本專案,不是由這裡推出去」

逐條說明:
1. file: `scripts/lumos:17164`(`_vendor_toolchain` 的 filecmp 自癒迴圈)確認散布方向是單向、單次觸發的「pull」——只有消費專案自己主動跑 `lumos update` 才會拿到新版(不論是上線新版還是回退舊版),工具鏈這邊沒有任何推播或通知機制。
2. `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md` 這份 spec 自己列為 PRIOR-ART 的「代碼審留痕閘」家族,裡面緊鄰的「新增告警閘」子機制明文有個別關閉開關:環境變數 `LUMOS_SKIP_LINT_NEW`(整道關)與 `.lumos/config.json` 的 `lint_new` 三態(擋／只報告／關閉),讓單一專案不必等中心倉庫改變主意就能自己降級。本 spec 全文(做法、條款、回退)沒有任何等價設計——沒有環境變數、沒有 `.lumos/config.json` 的對應區塊。
3. 具體後果:如果某個消費專案在推行兩週後遇到高申訴率或誤擋率(spec 自己在 RETIRE-IF ① 設的門檻),要等到「工具組決定撤掉」(中心裁定)且該專案自己再跑一次 `lumos update` 才會真正解除——這段等待期裡,該專案只能靠 `--no-verify` 苦撐每一次推送,而 CI 端(見 F3)若已經接了查核,`--no-verify` 在本機繞得過、在 CI 端繞不過,會被留痕標紅但推送實際上仍然過得去(這點跟既有 code-loop 機制一致,但 spec 沒有明講,讀者容易誤以為「本機不留痕」等於「CI 也放行」)。

## F5 「治理帳裡已寫的通過紀錄留著無害」跟既有的泛用讀取器矛盾

severity: minor
blocking: 否 —— 不影響是否擋得住推送或是否做出壞系統,只是讓一句「無害」的斷言不準確,頂多讓報表多出一行不會被誤認成新問題的舊資料。

引句:「治理帳裡已寫的通過紀錄留著無害(沒有讀者就不會被用到)」

file: `scripts/lumos:6635` 的 `_render_gov_stats`(`lumos gov --stats` 的實作,呼叫點在 `scripts/lumos:7084`)對 `docs/.governance-log.jsonl` 裡出現過的**任何** `gate` 值都會聚合列出(`agg.setdefault(r["gate"], ...)`),不受限於 `scripts/lumos:6586` 的 `_KNOWN_GATES` 白名單——白名單只用來算「完全沒觸發過的閘」那一段(`scripts/lumos:6657`),不會把不在名單上的既有紀錄濾掉。

逐條說明:
1. 這代表如果第二層真的上線過、寫過 `gate: "note-audit"` 這類事件到 `docs/.governance-log.jsonl`,回退之後這些歷史事件不會從報表消失——下一次有人跑 `lumos gov --stats`,還是會看到一行 `note-audit` 的去重筆數/原始筆數/首見末見日,跟其他仍在運作的閘並列在同一張表裡。
2. 這不等於「被誤用去做決定」(該行不會被拿來擋任何東西),但確實不是「沒有讀者」——`_render_gov_stats` 本身就是個不挑 gate 名稱的通用讀者,一定會撿到它。spec 這句話的字面意思(沒有任何東西會去讀它)不成立,只是後果溫和(多一行舊資料,不會誤導擋推送的判斷)。

## 誠實界線(第89–93行)

已讀,無 finding(「上線頭兩週逐筆看申訴」「花費」兩點已經誠實揭露,跟回滾鏡頭沒有新增衝突)。

---

總結:整份文件最嚴重 severity 為 blocker(F3:CI 接線不受 `lumos update` 同步、回退清單未提及,漏改會讓 CI 對整個 repo 的推送持續擋下甚至崩潰);blocking 的 finding 共 4 條(F1、F2、F3、F4),non-blocking 的 finding 共 1 條(F5)。
