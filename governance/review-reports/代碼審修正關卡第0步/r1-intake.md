preflight-4: ran

# 代碼審修正關卡第0步 r1 收貨紀錄

## 前掃(2026-10-02,sonnet 一席,報告 r1-preflight.md)

①未定義的詞、②壞引用、③範圍矛盾、存在類:全部直接改進計劃,不算 findings。
- 〈名詞〉補「理由夠不夠」(同 `--refuted-set` 理由判法)、「程式檔」(`_nodehome_code_kind` 不是 None 就算)。
- 寫明執行順序(便宜先決條件 → 記修正後 → 清殘骸 → 建樹 → 逐項驗 → 記帳收樹),`--record-template` 不建樹。
- 跳過(`skipped-env`)在 `loop next` 也算處理過;S8 改成五個狀態都印;第 3 項不過的測試不再送第 4 項。
- PRIOR-ART 拿掉 `_lint_copy_configs`(它只複製 lint 設定檔的 glob),設定檔改成直接複製。
- 派工單只讀字面 `<輪>-dispatch.json`、頂層是物件才讀。

④語意類(修改前 → 後):
1. 規格閘共用函式(動到做法):「參數:在哪個根跑、要跑的測試清單;回每支紅綠弱與原因」→「`_spec_gate_judge_items(根, 清單, per_prof, loose_for)` 回 (逐支結果含原始失敗尾巴, 跑不起來的原因);聚合、印出、跑不起來的處理留在呼叫端」。依據:相依回歸的紅字面用原始失敗尾巴、兩個呼叫端對跑不起來處理不同。
2. 第 4 項沒有 `{method}`:「也不過(同規格閘)」→「判不過並說明(規格閘是整批略過)」。
3. 平台根在 repo 外(動到做法):沒寫 →「先決條件:有平台根在 repo 外回 2」。依據:`load_platforms` 允許 `../別的專案`,在樹裡解析不到。
4. 第 5 項:`green` 但有平台沒設 run_cmd 沒跑 → 不過。
5. `loop next` 範本:「載體席記帳範本」→「`disposal_cmd`(只在 --json)」,同步既有測試 `t_loop_next_disposal_cmd_actually_runs`;提醒行文字與 JSON 兩條都接。
6. `--regression-set`:補 `none` 自己認、空字串、沒帶 `--loop`、「第一輪」只看別的輪次。
7. 事件 `head_sha` 先驗 40 碼十六進位再交 `_codeloop_record_valid_ex`(型別不對會丟例外)。
8. `resolve_test_refs` 的 `ValueError` 接住;測試存在判法對齊 `_bound_tests_for_diff`(含 `_KILL_METHOD_OK_RE` 白名單)。
9. 共用工作樹函式契約:兩層目錄、保留時兩層都留、失敗原因照 guard kill 截 120 字。
10. 寫不進治理帳:「照它的行為另加一句」→「回的不是 True 時(含沒有 docs/ 回 None 而且不印)另加一句」,`note` 放結果摘要。
11. 治理帳讀函式:`_drift_jsonl_parse` 吃整份位元組 → 預篩後接起來整批餵。

## r1 席報告收貨(2026-10-02,4 席)

機械收貨:4 份都已是正規化格式;quote-check 三份全數錨定,架構對齊席 #4 引句「只認小寫 `none`」不足 10 字被判錨不到——內容確實出自快照,編排者讀碼核對 `--refuted-set` 那段確實去空白轉小寫後比對(MISS 只是字數,現象 HIT),該條(a4)照折。

id 對照:c=正確性-opus(F1–F8)、i=整合-sonnet(F1–F8)、a=架構對齊-sonnet(F1–F7)、b=邊界-sonnet(F1–F9)。

### 依根因分組

- 樹與主工作目錄不一致(c1 絕對路徑、b1 設定有沒提交改動、b2 平台資料夾沒進版控、b8 實際路徑與壞設定):先決條件改到建樹之後、全部讀樹裡那份設定;三種平台根都回 2。折。
- 依賴資料夾連回主工作目錄載到沒提交的程式(c2):預設不連、`link_deps` 才連並警告。折。
- 多平台與 Path 型別(c3):〈名詞〉明寫樹一律 `Path`;S4 補多平台。折。
- 共用函式漏一份(a1 `_spec_gate_push_one`、i3 per_prof 來源、a2 測試名解析另寫一份):三處一起抽;測試名解析從 `_bound_tests_for_diff` 抽共用;寫明六值解構守衛。折。
- 改名判不過沒出路(b3、c5):改成只提醒。折。
- loop next(i1 escalate 碰不到、i4 範本測試說法錯、i7 JSON 形狀與印的位置、c6 壓提交後內容相同仍響):S8 拿掉 escalate;第 2 輪範本另寫真跑測試;定 `fix_check` 三鍵與印在 `[cap-hint]` 之前;c6 放行(見下)。折。
- 手冊與文件(i2 要背景跑或拉長逾時、i5 漏 reference.md 與 INDEX、SKILL 不加日期):折。
- 其他:c4 `other` 不算同類;c7 失敗細節=結果第 5 個值;c8 補條款(no-config、改名只提醒);i6、a6 清殘骸新寫一支、只借規則;i8 跳過在字元檢查之後、「既有各本帳」;a3 派工單照通配;a4、b7 none 大小寫與空值;a5 用 `_escape_reason_ok`;a7 落點加 reversibility-governance-ledger、bound-tests-gate;b4 `at` 檔案種類與路徑形狀;b5 大小上限;b6 前一輪照 `_disposal_round_groups`;b9 測試名過白名單。折。

### 放行

- c6(壓提交或 amend 之後內容一樣、提醒仍響):沿用代碼審留痕失效的同一套判法,寧多提醒;改成比內容會變成第二套判準(r3 架構席才剛擋過另寫一套)。

### 機械重現不到

無。
