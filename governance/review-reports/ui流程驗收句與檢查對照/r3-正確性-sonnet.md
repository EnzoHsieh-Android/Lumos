severity: blocker

我讀了 spec 全文、r3-delta.patch 和對照的程式碼。判定邏輯本身(新舊認定、插入點、三類代碼)大致站得住,但 schema 升版這一步會讓整套驗收壞掉。下面 7 條。

**1. `E2E_SCHEMA` 升到 2 會讓範本腳本寫的 steps.json 全部被 judge 拒收**

引句:「紀錄格式版本 `E2E_SCHEMA` 從 1 升到 2:舊版 lumos 讀到新紀錄走既有的」

- file: `scripts/lumos:40433` 的註解寫明 `E2E_SCHEMA` 同時是查證紀錄與 steps.json 的版本。
- file: `scripts/lumos:42640` 的檢查是 `steps.get("schema") != E2E_SCHEMA`,不是「不比它新」。
- file: `scripts/templates/android-e2e-run.sh:427` 把 steps.json 寫死成 `"schema": 1`。
- 重現:照 spec 把常數改成 2,範本腳本跑完呼叫 judge。judge 讀到 steps.json 的 schema 是 1,印「steps.json 的 schema 是 1,這版 lumos 只認 2」。整套路徑不寫紀錄,按功能路徑(`_e2e_judge_selected`,`scripts/lumos:42577`)也直接回 2。
- 後果:所有舊範本腳本跑出來的驗收都回 2、寫不出紀錄,推送檢查就永遠擋在「沒有查證紀錄」。
- spec 沒提 steps.json 要不要拆版本,也沒提範本腳本要改。S4 只寫了紀錄的 schema。
- file: `scripts/test_lumos.py:19908` 現有測試用 `schema=2` 當「steps.json 不認得」的例子,升版後這個測試也會翻。

severity: blocker
blocking: 是,照字面實作會讓判定本體整條壞掉。

**2. 放行路徑在新規則和提醒之前就提早回傳,所以「放行蓋過新規則」之後什麼提醒都不會印**

引句:「接在整套通過、放行之前那一刻;整套沒跑、整套沒過、紀錄讀不懂這些既有情況照舊由原本的路處理」

引句:「而應在整套通過與放行時也印出沒有 `accept` 的舊情境與零檢查的舊流程」

- file: `scripts/lumos:42064`:`_e2e_gate_body` 一看到 `_e2e_waiver_ok` 為真,就直接 `return _e2e_gate_out("waived", **info)`。
- 新規則、舊項目清單、檢查數變少三者,spec 都放在 `_e2e_gate_full_note` 裡、`_e2e_gate_done("pass")` 之前,而 `full_note` 在放行之後才會被呼叫。
- 重現:新流程零檢查 → 新規則擋 → 有人或 AI 放行 → 再推。走 waived 分支,這三者一個都沒算,rep 裡也沒有可印的東西。
- 後果:S10 要求「放行時也印」做不到,新流程零檢查這件事放行後完全消失。
- file: `scripts/lumos:68512` 的 `_cl_say_e2e_notes` 只認 `ci`、`skipped-env`、`pass-by-feature` 和 `pending_ai`。spec 說要「擴到整套通過與放行」,但沒說放行路徑上這些資料由誰算。waiver-only 的紀錄 `runs` 還可能是 null,零檢查舊流程根本列不出來。

severity: major
blocking: 是,spec 自己的條款 S10 和插入點互相矛盾,照字面做不出來。

**3. 舊情境自己補了 `accept` 時,逐句對照要不要判,第 5 條和第 8 條說法相反**

引句:「對新的項目,下面任一成立就擋,擋下代碼分三類」

引句:「舊情境自己補了 `accept`,就照第 5 條判」

- 第 5 條的「新情境」定義是主線與分岔點的 features 都沒有該情境,所以舊情境不在擋下範圍內。第 8 條和決策 d1 卻說補了就照新規則判。
- 重現:主線已有 `list.scroll`,分支幫它加 `accept: [A1]`,但 flow 沒有對應 label。
  - 依第 5 條:舊情境,不擋。
  - 依第 8 條:要判,A1 沒有檢查對到,擋。
- 沒有任何條款(S6 到 S10)測這個輸入。
- 若實作取第 5 條的寫法,「補 accept」就沒有任何效力。若取第 8 條的寫法,要不要同時要求 `accept_review`、`one_way` 也沒定義。

severity: major
blocking: 是,同一個輸入有兩種相反的實作,spec 沒裁。

**4. S1 說按功能跑時同樣記 `checks`,但按功能跑的紀錄裡沒有地方放**

引句:「整套跑與按功能跑都記,`_e2e_judge_ui` 本來就兩條路共用」

- file: `scripts/lumos:41317`:`_e2e_case_results` 把 `blocks.ui` 重組成 `items: [{kind, name, result}]`,只留這三個欄位。
- file: `scripts/lumos:41296` 起的 `_e2e_judge_partial` 把結果寫進 `feature_runs`,這個結構沒有 `blocks`。
- 重現:`--case` 跑完後看 `.lumos/e2e-records/<指紋>.json`,`feature_runs.*.items` 沒有 `checks`。只有記憶體裡的 `runs.blocks.ui` 和本機 history 有。
- 推送檢查只讀整套紀錄,所以不影響擋不擋。但 S1 的「按功能跑時同樣記」測不到持久化結果,spec 也沒說放哪。

severity: minor
blocking: 否,這是條款措辭和資料落點的問題,不會放過該擋的東西。

**5. 「舊版 lumos 不會覆寫新紀錄」的保護只對新建的檔成立**

引句:「不會把新紀錄覆寫成沒有 `checks` 的舊形狀」

- file: `scripts/lumos:41105`(`_e2e_record_update`):檔案已存在時,`rec` 是讀出來的原樣,`schema` 欄不動。只有檔不存在時才用 `E2E_SCHEMA` 新建(`scripts/lumos:41120`)。
- 重現:同一指紋已有舊版 lumos 寫的 schema 1 紀錄。spec 第 5 條的處方正是升級 lumos 後「重跑整套」,指紋不變。新版 judge 把帶 `checks` 的 `runs` 寫進去,schema 仍是 1,舊版 lumos 照樣讀得進、可以整套重寫。
- 實作要在 `_put` 裡明寫 `rec["schema"] = E2E_SCHEMA`,spec 沒寫。
- 後果有限:舊版覆寫後,新版會落到「紀錄裡沒有檢查欄」那條擋下訊息。

severity: minor
blocking: 否,有既有的擋下訊息兜底,只是 spec 的保護說法不準。

**6. 擋下訊息「不附放行指令」的做法放在 `_cl_say_e2e_next`,但放行指令是在它外面印的**

引句:「擋下報告帶一個新旗標,`_cl_say_e2e_next` 照它分派」

- file: `scripts/lumos:68471`:`_cl_say_e2e_block` 在呼叫 `_cl_say_e2e_next` 之後,只要 `fp` 有值且不是 `bad_record`、`newer_schema`,就印「確定是誤擋才放行」和放行指令。
- 新旗標只改 `_cl_say_e2e_next` 擋不住這段,「其他各條不附放行指令」會被實作成照樣附。
- 反過來,「讀不到執行紀錄」那支要附放行指令,多類同時擋下時印哪一個下一步也沒定。

severity: minor
blocking: 否,這是訊息文字問題,不影響擋不擋。

**7. 讀 commands.json 的大小上限沒有對應的做法,決策 d2 裡還留著舊的 `human:` 寫法**

引句:「讀檔沿用 `_e2e_load_json`,給它加一個巢狀層數參數」

- file: `scripts/lumos:40972`:`_e2e_load_json` 先 `read_text` 讀完整檔再 `json.loads`,沒有大小檢查。spec 只加了層數參數,但 S3 和〈實務隱患〉都宣稱有大小上限。
- 實作要在讀檔前加 stat 檢查,spec 沒寫。

引句:「驗收句要人點頭:accept_review.by 必須是 human:;其他情境由另派的代理審即可」

- 決策 d2 的 frontmatter 還是 r1 的 `human:` 前綴寫法,正文已改成 `{"by": "human"}`。照 d2 實作的人可能寫成前綴比對。

severity: minor
blocking: 否,兩項都是補寫就能解的缺漏。

逐項結論:
- `_e2e_judge_ui` 沒有 root 或 run_dir 參數,但 `evidence.dir` 是絕對路徑,取檔不受影響。
- 插入點可行:`_e2e_gate_full_note` 在 `_e2e_gate_done("pass")` 之前可以拿到 `rec`、`sel_full`、`base_full` 和主線版設定。因為 e2e 段有變就一定走整套,新規則在按功能路徑上不會誤觸發。
- 治理帳相容:`_codeloop_e2e_step` 的 `extra` 是攤平合併進事件(`scripts/lumos:1622`),新增 gate_code 值和鍵沒有衝突。`gate_code` 的其他消費者都屬於安全證據閘,不影響。
- `_door_keyword_hits` 回傳中文類名、沒有按類別過濾的參數,spec 的做法(自己篩三類、用 `_DOOR_CLASS_ZH` 反查)可行。

最嚴重 severity: blocker,blocking 共 3 條(第 1、2、3 條)。
