preflight-4: ran

# 設計審第 1 輪收貨紀錄:守檔筆記對照改動

## 前置四項掃描(r1-preflight.md)的處置

前掃 31 條命中(①5、②4 加 1 條驗過屬實清單、③4、④16 加 1 條驗過屬實清單),全部改進計劃真檔;語意類逐條如下(修改前 → 修改後)。標「核心」的動到核心裁定,不由前掃自行定案,交本輪席位審。

| 前掃編號 | 類 | 修改前 → 修改後 | 核心 |
|---|---|---|---|
| ①1 | 未定義 | 「四行來源錨點(provider、model、prepared 等於項目指紋、範本版本)」→ 四行是 seat/provider/model/prepared;範本版本改比項目檔頭 | |
| ①2 | 未定義 | 「同目錄、沒有家的測試檔」→ 同一層、`_nodehome_is_test` 判是測試、沒被任何家的 about_code 列到 | |
| ①3 | 未定義 | 「superseded 或 archived」→ 刪掉,家的定義本來就不含 superseded;沒有 archived 這個狀態 | |
| ①4 | 未定義 | 「同一個逐件檔形狀」→ 同一支寫入函式、自己的檔名正規式 | |
| ①5 | 撞名 | 子指令 home-prepare/record/check、`LUMOS_SKIP_HOME_CHECK` → reread-prepare/record/check、`LUMOS_SKIP_REREAD_CHECK`;資料夾 governance/home-verdicts → governance/reread-verdicts;範本 note-audit-home.md → note-audit-reread.md | |
| ②1 | 壞引用 | 「用筆記內容審找範圍裡碰過的筆記那支」→ 從 `_notes_status_flipped` 抽共用函式、行為不變(新條款 S12) | |
| ②2 | 壞引用 | 「判程式檔的同一支函式(豁免清單一致)」→ `_nodehome_required` 讀頂端快照;簿記檔不算是因為副檔名 | |
| ②3 | 壞引用 | 候選「about_code 列了的節點」→ `_nodehome_homes` 的家定義 | 核心(見③1) |
| ②4 | 壞引用 | 依據的 governance/eval/home-check/ 沒進版控 → 跟實作提交一起進 | |
| ③1 | 矛盾 | 候選從「about_code 列了任一支檔的節點」收窄成程式的家定義(Systems、system、doing/done/stale);〈誠實界線〉補「量準度的母體比產品寬」 | 核心 |
| ③2 | 矛盾 | 「恆回 0」但沿用的範圍解析會回 2 → 一律吞成 0 並印原因;CI 加 continue-on-error 與 `|| true`;S6 補 | 核心 |
| ③3 | 矛盾 | 「V3 逐字」與「加兩樣附加」兩種說法 → 統一成 V3 加兩樣附加,新條款 S10 實作後重跑、真漂移少於八成不接線 | |
| ③4 | 用詞 | CI「一行」→ 一步,S8 釘 continue-on-error | |
| ④1 | 語意 | 起點照 `_lens_push_base` → 照存量漂移檢查帶 --push-remote/--pushed-ref 走 `_push_range_start`;上線點標記傳自己的字串 | 核心 |
| ④2 | 語意 | 掛鉤註解會出現「note-audit check」字串誤觸筆記內容審上線點與 doctor 接線判斷 → 明文禁止並由 S8 測試釘 | |
| ④3 | 語意 | 逐提交碰過 vs 淨改動 → 選逐提交碰過,寫明理由 | |
| ④4 | 語意 | 改名的程式檔 diff 會整支當新增 → pathspec 帶舊路徑 | |
| ④5 | 語意 | 簿記豁免「三個消費者」→ 五個;S7 補純文件測試範圍 | |
| ④6 | 語意 | 新資料夾不會被筆記內容審讀到:屬實,理由措辭改準 | |
| ④7 | 語意 | 項目檔 14 天自動清 → 寫明,抽樣靠紀錄檔 | |
| ④8 | 語意 | 掛鉤位置 → 存量漂移檢查那段之後(逐 ref、帶推送參數);CI 放 drift check 之後 | |
| ④9 | 語意 | `.tmp-wlf` 殘檔 → 自己的檔名正規式排除 | |
| ④10 | 語意 | `_KNOWN_GATES` 不用改:屬實,寫明 | |
| ④11 | 語意 | 來源錨點「逐項丟掉」→ 錨點是整份層級;提醒版照收標 provenance_ok:false | |
| ④12 | 語意 | 單大括號佔位字會跟 JSON 範例衝突、二次替換 → 雙大括號、一次掃描替換;S3 補 | |
| ④13 | 語意 | 「筆記內容審用 opus 是因為判單句」沒出處 → 改成「另一種判斷、另外校準」 | |
| ④14 | 語意 | 範本要登記 `_VENDORED_TREE_FILES` → 新條款 S11 | |
| ④15 | 語意 | record 沒印提交指令 → 補 | |
| ④16 | 語意 | 逐檔讀紀錄檔會隨檔數變慢 → 檔名帶指紋前綴、只列目錄 | |

refcheck 剩 3 條 missing:`scripts/templates/note-audit-reread.md`、`governance/reread-verdicts/` 是本案新建;`governance/note-verdicts/` 是筆記內容審還沒接線、從沒建過的資料夾(程式常數 `_NOTE_AUDIT_VERDICT_DIR`)。三條都不是壞引用。

## 席位報告收貨(6 席全收齊後才動計劃)

四道機械檢查:6 份都已是正規化格式;quote-check 全數錨定;refcheck 只有 `governance/reread-verdicts/` 不存在(本案新建,併發、回滾兩席各 1);seat-check 派工單材料豁免。

finding 編號:c=正確性-opus、b=邊界-sonnet、h=接手-sonnet、k=併發-sonnet、r=回滾-sonnet、a=架構對齊-sonnet,後面接報告裡的 F 編號。

| 編號 | 席 F | 等級 | 處置 | 折在哪 |
|---|---|---|---|---|
| c1 | 正確性 F1 | major | 折 | 做法 1「不經 `_nodehome_required` 過濾」、做法 2 diff 含測試;S1、S2 |
| c2 | 正確性 F2 | major | 折 | 做法 2 補測試檔規則 `tests/<X>`↔`src/<專案>/<X>`;S10 改用 reread-prepare 產材料 |
| c3 | 正確性 F3 | major | 折 | 做法 1 家取起點與頂端兩邊、改到的檔含刪檔;S1 |
| c4 | 正確性 F4 | major | 折 | 做法 2 項目指紋不含範圍;S6 合過主線案例 |
| c5 | 正確性 F5 | minor | 折 | 閘名 `note-reread` 傳給範圍解析;S7 不寫 `note-audit` 事件 |
| c6 | 正確性 F6 | minor | 折 | 做法 1 共用函式只回路徑、不過濾;S12 |
| c7 | 正確性 F7 | minor | 折 | 做法 4 掛鉤交給 `pp_stop_if_signaled`;S9 |
| c8 | 正確性 F8 | minor | 折 | 做法 0 pathspec 用原樣路徑 |
| c9 | 正確性 F9 | minor | 折 | 做法 0 切行口徑;做法 3 行數取項目檔頭、全文從 blob 讀、布林不算;S5 |
| c10 | 正確性 F10 | minor | 折 | 做法 2 填入字串照實驗逐字;S3 |
| c11 | 正確性 F11 | minor | 折 | 做法 4 回 0 清單含推送參數只給一個與例外;S7 |
| c12 | 正確性 F12 | minor | 折 | 指紋不含 diff;diff 固定參數 |
| b1 | 邊界 F1 | major | 折 | 同 c3 |
| b2 | 邊界 F2 | major | 折 | 同 c4 |
| b3 | 邊界 F3 | major | 折 | 同 c6,並寫明路徑形狀(做法 0) |
| b4 | 邊界 F4 | minor | 折 | 做法 0 errors=replace;做法 4 最外層接例外;做法 3 報告非 UTF-8 rc2 |
| b5 | 邊界 F5 | minor | 折 | 做法 0 切行口徑 |
| b6 | 邊界 F6 | minor | 折 | 做法 3 json 區塊抽法與逐項驗證、重複行號;S5 |
| b7 | 邊界 F7 | minor | 折 | 做法 0 與〈誠實界線〉寫明只看一個圖譜 |
| b8 | 邊界 F8 | minor | 折 | 同 c8 |
| b9 | 邊界 F9 | minor | 折 | 做法 2 檔頭與本文用 `---本文---` 分隔、record 只讀檔頭 |
| b10 | 邊界 F10 | minor | 折 | 做法 4 自己先驗範圍與終點、所有事件帶原因、自己的閘名 |
| b11 | 邊界 F11 | minor | 折 | 做法 2 組 diff 失敗那篇不產並印原因;做法 4 時間上限 |
| h1 | 接手 F1 | major | 折 | 做法 6 skill 小節內容與落點;S14 |
| h2 | 接手 F2 | major | 折 | 做法 4 事件 `reminded`(路徑、指紋、來源)、`none`、`covered`;做法 5 量法 |
| h3 | 接手 F3 | minor | 折 | S10 寫明材料來源、重跑規則與推送前順序;做法 6 |
| h4 | 接手 F4 | minor | 折 | 新增 REVISIT 2026-12-02;RETIRE-IF 成本改用項目檔大小 |
| h5 | 接手 F5 | minor | 折 | 同 c7 |
| h6 | 接手 F6 | minor | 折 | 做法 3、4 印「修完會再列、只提醒可照推」 |
| h7 | 接手 F7 | minor | 折 | 做法 6 上線公告;做法 2 紀錄 model 行照報告存 |
| k1 | 併發 F1 | major | 折 | 做法 4 不組 diff、30 秒上限;S7 |
| k2 | 併發 F2 | major | 折 | 同 c7 |
| k3 | 併發 F3 | minor | 折 | 項目檔名帶編排者 |
| r1 | 回滾 F1 | major | 折 | 同 c4 |
| r2 | 回滾 F2 | minor | 折 | 同 c6;S12 補嚴格、截止時間、git 失敗 |
| r3 | 回滾 F3 | minor | 折 | 同 c7;掛鉤標準錯誤丟掉處理版本偏斜;時間上限 |
| r4 | 回滾 F4 | minor | 折 | 〈回退〉revert 時一併刪紀錄資料夾、逃生做法 |
| r5 | 回滾 F5 | minor | 折 | 做法 0 NFC;S1 NFD 案例 |
| a1 | 架構 F1 | major | 折 | 同 c4 |
| a2 | 架構 F2 | major | 折 | 同 c7,並加上線標記註解行 |
| a3 | 架構 F3 | minor | 折 | 同 c5 |
| a4 | 架構 F4 | minor | 折 | 做法 0 路徑形狀;做法 1 前置照 `_nodehome_evaluate` |
| a5 | 架構 F5 | minor | 折 | 做法 4 `note_reread.mode`;S13 |
| a6 | 架構 F6 | minor | 折 | 做法 2 範本載入抽共用、佔位字全大寫、整數版本常數、模型走同一支函式;S3 |

重現不到而沒折的:無(refuted-set none)。放行的:無。
