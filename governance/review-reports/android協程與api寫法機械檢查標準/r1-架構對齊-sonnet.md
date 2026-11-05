severity: major

判讀前提:快照第 6 點寫「在目標是 `.kt` 檔、而且要寫進去的內容含〈情境決策表〉某列的觸發字時」,沒寫由誰比對。我照字面讀成由鉤子比對。

## 問 1:分層與依賴方向

**大半對齊,有一處跨層(第 6 點)。**

對齊的部分:
- 回合結束那道(第 5 點)。既有擋停鉤子自己不判圖譜,而是用子程序叫「可信來源」的 lumos 去算(`_impact_missing`,`scripts/hooks/claude/check-graph-sync.py:739-750`)。本案把判定放進 `lumos lint-new --worktree`,鉤子只收結果,同一個形狀。
- 工作樹終點(第 4 點)。判定函式 `_lint_new_verdict`(`scripts/lumos:39031`)多收一種終點,不另寫一套,沒有分層問題。
- 代碼審通過前先查(第 7 點)。重用 `_lint_new_verdict` 與表態判定,不另寫判定。

不對齊的部分:
- 既有的棧別題,「哪題適用」是 lumos 算的。鉤子只取 `stack_questions_applicable` 來印,不自己比對詞(`scripts/hooks/claude/impact-hook.py:705-709`、`scripts/lumos:59024-59070`)。
- 觸發詞的定義也在 lumos 本體,不在鉤子。規格表是 `_STACK_QUESTION_SPECS`,詞用 `when` / `when_raw` 寫(見 `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:35-38`)。
- 本案第 6 點相反。「觸發字」是型錄(Markdown)〈情境決策表〉新增的一欄,由改檔前鉤子看寫入內容決定推哪幾列。這等於鉤子自己做比對,還多出一張放在 `skills/` 的觸發詞表。

severity: major
blocking: 是
引句:「在目標是 `.kt` 檔、而且要寫進去的內容(既有那支取 Edit/MultiEdit/Write 寫入內容的函式)含〈情境決策表〉某列的觸發字時」
file: `scripts/hooks/claude/impact-hook.py:705-709`
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:35`
⚠ 如果本意是讓 `lumos impact` 回傳決策表命中列、鉤子只印出來,就對齊了。快照沒寫,請編排者向作者確認。

## 問 2:命名與錯誤處理

**大致對齊,有兩處小不一致。**

對齊的部分:
- `LUMOS_STOP_LINT_OFF` 對應既有的 `LUMOS_STOP_BLOCK_OFF`(`scripts/hooks/claude/check-graph-sync.py:893`)。
- 沿用 `LUMOS_SKIP_LINT_NEW`(`scripts/lumos:39050`)。
- `--budget 秒` 對應 `drift scan` 的同名旗標(`scripts/lumos:70713`)。
- `lint_new` 設定區塊加 `stop_budget_sec`,跟 `budget_sec` 放同一處(`scripts/lumos:38493-38497`)。
- `lint-new` 這個指令名落在 `lint-waive` / `lint-check` 的同一族。

不對齊的部分:

**(a) 預算有第二個來源。** 鉤子的時間天花板只有一個來源,就是註冊表 `HOOK_BUDGET`。`check-graph-sync.py` 現為 40 秒,內層只拿 0.7 倍,也就是 28 秒(`scripts/merge-claude-settings.py:110-121`、`scripts/hooks/claude/check-graph-sync.py:712-738`)。`merge-claude-settings.py` 內的註解還寫著「天花板與旗標都只能有一個來源」。快照在 `.lumos/config.json` 另訂 20 秒的 `stop_budget_sec`,也沒說它怎麼跟 28 秒的內層上限相加。既有那道圖譜同步檢查實測要 25 秒,兩道合起來會超過上限。

severity: minor
blocking: 否
引句:「預算預設 20 秒,可用 `.lumos/config.json` 的 `lint_new` 區塊新加的 `stop_budget_sec` 調」

**(b) 標記檔放哪裡沒指定。** 既有擋停名額標記放 `~/.cache/lumos/<name>`,而且要過 `_stop_dir_ok` 信任檢查(`scripts/hooks/claude/check-graph-sync.py:768-900`)。`_voice_once` 放系統暫存區 `lumos-impact-<會談>/voice-<代碼>`(`scripts/hooks/claude/impact-hook.py:825-838`)。快照寫「檔名含那批的雜湊」的標記檔,沒說用哪一套的目錄、信任檢查與清理。放錯就多一種放法。

severity: minor
blocking: 否
引句:「用它自己的會談標記檔(檔名含那批的雜湊,跟既有「改 code 沒動圖譜」那道的名額標記分開)」

另有一個沒擋的觀察:既有擋停寫明「兩家一致」(Claude 與 Codex 共用同一份邏輯,`scripts/hooks/claude/check-graph-sync.py:889-891`)。快照只提 Claude 的回合結束鉤子,沒說 Codex 那邊要不要同步。

## 問 3:第二種做法

**沒有新的放行機制或新的設定檔位置,有三處值得標。**

對齊的部分:
- 放行沿用 `lumos lint-waive`(`scripts/lumos:38064`)與 `LUMOS_SKIP_LINT_NEW`。
- 設定放 `.lumos/config.json` 的 `lint_new` 區塊。
- 規則包分發用 `configs/<工具>/…`,跟 `configs/detekt/android.yml` 同一種,隨 clone 分發。
- ast-grep 與 semgrep 走 `.lumos/lint.json` 的 SARIF 橋。`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:27` 已寫明這「不碰零依賴家規」。倉裡也已有 `scripts/test_quality_semgrep.py`。所以外部工具依賴本身不算第二種做法。

不對齊的部分:

**(a) 第 7 點讓 `code-loop pass` 去跑機械閘。** 現況 `pass`/`skip` 只寫留痕,不跑任何閘(`scripts/lumos:68594-68603`)。閘由 `check` 與推送前的 `_codeloop_guard_verdict` 跑(`scripts/lumos:68605-68611`、`scripts/lumos:67865`)。快照刻意不用 `check`,另在 `pass` 內加一道,所以閘多了一個呼叫點。判定函式是同一支,但要留意「pass 寫留痕」跟 `Issues/code-loop-pass自失效追尾` 那段既有慣例的互動。

severity: minor
blocking: 否
引句:「`lumos code-loop pass` 寫留痕前,對同一版本跑新增告警與表態兩道判定」
⚠ 這是新增放行點還是等價的提前檢查,我判不準。

**(b) 工具鏈第一次自寫整包規則。** `configs/detekt/android.yml` 只開第三方工具既有的規則。本案是在 toolchain 內自寫 `kt-*` 規則,附壞例好例樣本與樣本測試。這不算第二種做法,只是首例。`linter精選目錄` 自己寫「事故固化走 ast-grep」,方向一致,但承載它的專家頁面需要確認(見問 4)。

severity: minor
blocking: 否
引句:「`configs/ast-grep/kotlin-android/`(新增):`sgconfig.yml`、`rules/<主題>.yml`、每條規則的壞例好例樣本」

**(c) 型錄檔放在 `skills/kotlin-idioms/` 內。** 其他語言的 idioms skill 只有 `SKILL.md`,規則與機檢對照寫在同一檔。本案另放一份 473 列、約 24 萬字元的 `checks-catalog.md`,再讓 `SKILL.md` 改成指向編號。其他棧不是這種結構。這屬於「規則放哪」的新慣例,若別的棧日後比照,要先立標準,現在先不擋。

severity: minor
blocking: 否
引句:「型錄是「標準寫法」的單一來源;kotlin-idioms 本文的每條規則改成指向型錄編號,不重抄。」

## 問 4:落點合不合理

**部分不合理,沒有主人的檔會很多。**

- **規則包的家。** 快照把家指給 `Systems/linter精選目錄`(用詞段「家是 [[Systems/linter精選目錄]]」)。但該節點自己定位為「各專案該裝哪些 linter」的菜單,「不是某專案已裝什麼的清單」(`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:39`)。它目前只管 `configs/detekt/android.yml` 一支檔(同檔 `:31-32`)。要放進去的 `configs/ast-grep/kotlin-android/` 整包規則與樣本、`configs/semgrep/kotlin-android.yml`,是 toolchain 自己的程式碼,性質不同。依專案鐵則第 5 點(每支程式檔要有家),建議另開一篇,例如 `Systems/kotlin規則包`,用 `lumos new system … --code` 登記這些檔。`linter精選目錄` 只加 `.lumos/lint.json` 範本與指向它的連結。

severity: minor
blocking: 否
引句:「家是 [[Systems/linter精選目錄]]。」

- **型錄檔 `skills/kotlin-idioms/checks-catalog.md`。** `lands_in` 沒列任何 skill 相關節點。要確認它的家是誰(同樣依鐵則第 5 點)。這點可併入上一條處理。

- **工作樹檢查與 `lint-new --worktree`。** 判定函式 `_lint_new_verdict` 在 `scripts/lumos:39031`,但五個 `lands_in` 沒有一個以「新增告警閘本體」為責任。`linter精選目錄` 與 `棧別提問表態閘` 只是牽連。我找過 `Systems/` 下提到 `新增告警閘` 的節點,最可能的主人是 `lint-declaration-health`,不在 `lands_in` 裡。要補這一篇,或明講新終點寫進哪一篇。

severity: minor
blocking: 否
引句:「新增告警閘的判定函式多收一種終點「工作樹」」

- **擋停鉤子兩道。** 落點 `Systems/graph-sync-coverage` 合理,它管 `check-graph-sync.py`(提到該檔的節點之一,見 `Systems/graph-sync-coverage`)。改檔前推列落 `Systems/改檔前推播` 也合理,它管 `impact-hook.py`。
- **表態與審查迴圈。** `Systems/棧別提問表態閘` 與 `Systems/pitfalls-code-loop` 對應批二的第 7、8 點,合理。

## 統計

不對齊共 6 條,其中 major 1 條。

1. major:鉤子比對決策表觸發字(問 1)。
2. minor:`stop_budget_sec` 與 `HOOK_BUDGET` 並存(問 2a)。
3. minor:標記檔位置未指定(問 2b)。
4. minor:`code-loop pass` 內加閘(問 3a)。
5. minor:規則包的家(問 4)。
6. minor:新增告警閘本體沒有落點節點(問 4)。

問 3b、3c 是觀察,已寫在上面,沒算進不對齊的條數。

**臨時目錄**:本席沒有建任何暫存檔或實驗 repo,不需清理。
