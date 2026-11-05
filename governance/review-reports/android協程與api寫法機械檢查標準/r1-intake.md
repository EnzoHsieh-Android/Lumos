preflight-4: ran

# r1 前掃收貨(2026-11-05,sonnet 一席,只讀)

前掃四類命中:①未定義詞 6 ②壞引用 2 ③範圍矛盾 5 ④機械宣稱 21 句(屬實 11、不屬實 4、查不到 2、部分屬實 1、未重驗 2)。①②③與存在類直接修真檔;語意類逐條如下(修改前→後)。沒有動到「裁決紀錄」節,不升級為正式 finding。

## 語意類命中(修改前 → 修改後)

1. 回合結束鉤子防無限擋:前「同一批告警指紋已經擋過兩次就改成只提醒」→ 後「stop_hook_active 時一律不擋;同一會談同一批只擋一次,用自己的會談標記檔(檔名含那批的雜湊)」。依據:check-graph-sync.py 的 stop_block_decision 遇 stop_hook_active 回 False、名額標記檔一個會談只建一次,「擋兩次」照字面做不到。
2. 兩道擋停合成訊息:前「各自判、各自擋,兩道都要擋時合成一則訊息」(暗示現狀已分道)→ 後寫明「既有鉤子現在只有一道、一則訊息;改成兩道各自判、各自佔名額」。條款 S6 同步加「兩道各自的名額各自記」。
3. 改檔前推列冷卻:前「同一列同一會談只推一次」(未說機制)→ 後寫明既有冷卻是每檔 20 分鐘、語意不同,改借既有「同會談只講一次」標記函式、以列編號為鍵。
4. 代碼審手冊第一步:前「先跑 lumos code-loop check,機械判定乾淨才派審查席」→ 後「先跑 lumos lint-new --worktree」。依據:code-loop check 在 tier high 派席前必因沒有審查留痕而 rc1,看不出機械乾不乾淨;輸出也沒有機器可讀的擋下原因行(grep LUMOS_BLOCKS 無)。
5. 整道關閉「會留帳」:前「整道關閉走既有環境變數(會留帳)」→ 後只寫變數名 LUMOS_SKIP_LINT_NEW,拿掉「會留帳」(前掃查不到 off 分支寫治理帳)。
6. 表態「本來就放行」:前「沒有宣告的專案那兩道本來就放行」→ 後「新增告警那道沒宣告就放行;表態那道不看宣告、看有沒有碰到棧別題」。
7. 推送前閘判定不變:前「不改推送前閘本身的判定」→ 後補「判定函式多收工作樹終點,但終點是提交時走原路徑、結果一字不變」。
8. 預算截斷:前只在實務隱患寫「截斷只提醒不擋」→ 後寫進範圍 4:工作樹檢查對預算沒跑到的命令只列出不擋,推送前閘照舊擋;條款 S5 同步。
9. 設定檔位置:前「.lumos/lint-new.json 的 stop_budget_sec」→ 後「.lumos/config.json 的 lint_new 區塊新加 stop_budget_sec」。依據:既有新增告警設定在 config.json 的 lint_new 區塊,程式註解明說設定不放 lint.json。
10. 開場防護報告加一項:前在實務隱患寫「開場防護報告要列出(批二範圍內)」但範圍與條款都沒有 → 後拿掉這句,改成一行 REVISIT 回頭條件(看消費專案印「沒裝 ast-grep」的次數再決定)。

## 其他直接修的

- 壞連結:批三計劃還沒建,改成純文字暫定名。
- 未定義詞:補「表態」「正向約束」「告警身分(指紋)」「light 等級、盲判席」四條用詞;放行帳改寫成 lint-waivers.json 那份;「這一輪有動作」拿掉(既有鉤子也不再宣稱切得出「這一輪」);sgconfig-hints.yml 補進規則包用詞。
- LUMOS_STOP_LINT_OFF、lint-new --worktree 標「(新增)」。
- 型錄欄數:前掃數到 1 列 14 欄,實為反引號裡的直線;扣掉後 491 列全是 11 欄。S3 補「反引號裡的直線不算欄位分隔」。
- 本機沒裝 ast-grep 與 semgrep(前掃提醒):規則包已在 /Users/enzo/lumos-scratch/android-checks/venv 裝 0.51.1 驗過;實作時 S1、S4 的測試在沒裝時印略過,推送前要在裝好的環境跑一次。

# r1 席報告收貨(2026-11-05,四席 sonnet:通才、正確性、接手、架構對齊)

收貨三道:四份引句 quote-check 三份全錨;架構對齊席 #6 引句裡又包了「」被截短成「型錄是「標準寫法」」(<10 字),機械重現見下表(HIT),不改席位原文。refcheck 的 missing 只有計劃標新增的 configs 路徑與型錄統計行號(席位寫 845,型錄 844 行),不影響判讀。seat-check 對本輪派工單判 vacuous(派工單寫成 seats 陣列),材料涵蓋另由下表人工核。通才席最後一行總結句以「severity:」開頭,改成「總結:」開頭(只改格式,report-normalize 原本會把它拆成多一條發現)。

## 編排者機械重現

| id | 命令 | 結果 | 判 |
|---|---|---|---|
| 正1/通1/接1 | `sed -n 38497,38498p scripts/lumos` | `"per_cmd_floor_sec": 30` 與預算 20 秒 → 第一條就記成預算不足 | HIT 採信 |
| 通3/接4 | `sed -n 38434p scripts/lumos` | `message_text = (...)[:120]` | HIT 採信 |
| 正2/通2/接2 | `grep -n 'if graph_touched' scripts/hooks/claude/check-graph-sync.py` | 1029 行 `if graph_touched:` 之後 return 0 | HIT 採信 |
| 正12/通11 | `grep -n '_PITFALL_DIFF_TEST_PAT = ' scripts/lumos` | 37574 行含 `(?:^|/)tests?/` | HIT 採信 |
| 通13/接7 | `grep -n 'if not chunks' scripts/hooks/claude/impact-hook.py` | 893 行既有輸出空就 return 0 | HIT 採信 |
| 正3 | 暫存區 git 實驗:`mv Foo.kt Bar.kt` 後 `git diff --name-status HEAD` 只見 D、`git status` 見 ?? | 照既有做法改名會變成整檔新增;換暫時索引後得 R100 | HIT 採信 |
| 架6 | `grep -c '型錄是「標準寫法」的單一來源' r1-snapshot.md` | 1 | HIT 採信(原句存在,截短是巢狀引號造成) |

## 先查世界

- PRIOR-ART: 規則誤報上限——Google Tricorder 與後續 MEAN 論文:分析器「沒用」比例要壓在一成以下,壓不下就停用(https://www.cs.umd.edu/class/spring2019/cmsc414/papers/tricorder-building-a-program-analysis-ecosystem.pdf、https://lup.lub.lu.se/search/files/91080778/ICSE_SEIP_2021_MEAN_final.pdf)。採用:範圍 3 落地前在兩個真專案量,超過一成降 hint。一成是 MEAN 論文的數字,原 Tricorder 論文片段沒寫數字,所以出處標 MEAN。
- PRIOR-ART: 工作樹對 HEAD 的改名配對——git 自己的 stash 用暫時索引(GIT_INDEX_FILE)做暫時操作(https://github.com/git/git/pull/2306)。網上沒找到「暫時索引上 add -A 再 diff --cached 配對未追蹤改名」的現成說明,改在暫存區實驗:得 R100、真索引不變。採用。
- PRIOR-ART: 規則訊息長度——ast-grep 規則有 message(短)與 note(長、可帶修法)與 url 三欄(https://ast-grep.github.io/reference/yaml.html);ESLint、Clippy 慣例是短訊息加規則文件。SARIF 輸出是否帶 note 查不到(只看到印出器用 message),所以不靠 note:訊息自己放最短修法,完整寫法靠型錄編號。不採「放寬 120 字截斷」:那會改到所有棧的告警輸出。
- 排除:「回合結束鉤子另訂一個預算設定鍵」——鉤子天花板只能有一個來源(merge-claude-settings 的註冊表),改從內層預算切。

## 去向(r1 全部 50 條)

全部折入計劃(folded),沒有放行、沒有駁回。對照:
- 預算與保底、鉤子總預算(正1、通1、接1、接3、正8、通15、架2):範圍 7(工作樹模式保底 1 秒)、範圍 8(切內層預算一半、上限 15 秒、不另訂設定鍵)。
- 鉤子插入位置與提早離開(正2、通2、接2):範圍 8 寫明插在所有提早離開之前。
- 訊息截斷與格式(通3、接4、接10):範圍 2 訊息 ≤120 字、含修法;S2。
- 共用工作目錄與快照被撿(通4、通5、正9):範圍 8 只掃這一輪寫過的檔;範圍 7 不掃 `.lumos/`;輸出帶檔:行與指紋。
- 工作樹終點語意(正3、正6、正11、通6):範圍 7 暫時索引配改名、衝突檔不掃、明示參數、全沒跑印「不算乾淨」。
- 代碼審通過的範圍與抽函式(正4、通8、架4):範圍 10 抽共用函式、範圍取分岔點到 HEAD,並在實務隱患寫明比推送前寬。
- 手冊步驟與指令(正5、通7、接6、接12):範圍 6 加 `lint-new --diff`;範圍 11 改用提交範圍、表態時機照手冊。
- 測試檔被排除(正12、通11):範圍 5 加 `include_test_paths` 開關;S11。
- 每列都接電的實況(通9、接5):範圍 1 加「通電批次」欄;天花板 3 寫明數字;用詞說明哪些批才生效。
- S3 與型錄打架(通10、接8):S3 改成人裁列免盲判席。
- 規則包樣本與 CI(接9、通18 的 API-1/STATE-1 部分):範圍 2 API-1 只放 semgrep;S1 每條至少兩壞兩好、CI 裝 ast-grep。
- 改檔前推列(架1、正10、通13、接7、接11):範圍 9 比對移進 lumos 本體、強弱字門檻、只看新內容去註解字串、取前三的順序、只記印出的列、空輸出照推、列編號欄、Codex 這版不推。
- warning 規則只在樣本驗過(通12):範圍 3 真專案量測;S10。
- 放行灌帳(通14):範圍 6 `lint-new` 不寫治理帳。
- 擋停上限與續做(通16):範圍 8 一會談最多三次;天花板 4。
- 範本路徑與 CI(通17):範圍 4 改成 `$HOME/harness/lumos-toolchain`、寫明 CI 要裝。
- 用詞錯(通18 light 定義、35 條):用詞與舊版初稿節修正。
- 型錄統計與暫存路徑(接13):範圍 1、S2。
- 沒裝工具的偵測(接14):範圍 6 第一個詞找不到執行檔就明說。
- 同一批的定義(正7):用詞改成多重集合。
- 標記檔位置(架3):範圍 8 放既有擋停名額目錄、過同一個信任檢查。
- 規則包的家、新增告警閘本體的家(架5、架6):用詞改成另開 Systems/kotlin規則包、新增告警閘指向 pitfalls-code-loop;lands_in 加 Systems/kotlin規則包。
