---
type: project
status: doing
created: 2026-10-03
updated: 2026-10-03
tags:
  - type/project
  - status/doing
  - scope/evals
lands_in:
  - Systems/codex-harness
---
# 探針讀碼結果證據_計劃

本案接續 [[Projects/代碼審修復穩定性試行_計劃]] 第1案 C1/R2C1/R2C2；代碼審仍為 code-repair-pilot-01 的第3輪，不新增名額。原兩輪失敗證據保持不動。

PRIOR-ART: 借用既有make_sandbox隔離副本和成功工具結果，不造shell parser。Claude tool_result以tool_use_id關聯工具呼叫且有is_error（https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls）；Codex官方SDK的CommandExecutionItem定義aggregated_output/exit_code/status（https://github.com/openai/codex/blob/main/sdk/typescript/src/items.ts，2026-10-03查證）。一次性標記是本案識別「目標片段確曾回傳」的量測方法，不代表程式理解能力或安全邊界。

RETIRE-IF: 工具層提供穩定的實際讀取檔案/範圍證據，或標記導致有效讀取經常被截掉時，改用該證據或停用此題，不能放寬回命令字串猜測。入口為本題回歸及每次runner事件格式升級驗證。

## 根因、改變與保持

命令摘要把檔案參數、搜尋字串、工作目錄混在一起，無法可靠證明取得目標內容。把判準移到結果證據：僅v04啟用source_probe（相對檔名與唯一目標行前綴）；在已建立的隔離副本，對該行加Python行尾註解，含每次嘗試新產生的隨機標記。準備程序不把標記放提示詞或命令；只有與真工具呼叫關聯且成功的回傳文字命中才算取得目標片段。真repo與語法樹不變。每次嘗試以finally還原目標原始內容，不依賴git索引；還原前重驗路徑安全，失敗列儀器例外並停止整批，避免後續污染。既有整場git清理仍保留。

保持成功/錯答案分開、截斷與非零退出優先、不影響其他題、不改結果passed布林形狀、不碰真repo/全域設定。答案仍用既有answer_expect；新證據只補讀取行為，不聲稱答案內容充分。這是可見內容的量測，不聲稱任何合法讀檔命令必能通過：若工具顯示只取檔首而未含目標行，並未建立本題所需的片段證據。

不採：繼續補命令regex（已產生假綠/假紅）；實作通用shell parser（範圍大且仍不知道實際結果）；只看固定程式字串（文件也可能抄同一段）。代價：副本有一段量測註解，舊摘要資料不可按新判準直接重評。

## 驗收條款

- [S1] 當v04進入一場執行時，準備程序應只修改make_sandbox回傳的副本內普通檔案，拒絕絕對/越界/符號連結/多硬連結路徑、找不到或不唯一的目標行及非Python語法；注入前後AST應相同，每場標記應不同，失敗應列儀器例外且不啟動模型。[test: t_probe_source_probe_setup]
- [S2] 當Claude工具結果到達時，判分應只接受可對應到先前Read/Grep/Bash呼叫的成功tool_result文字；Codex應只接受completed且exit_code為0的command_execution輸出。命令、答案、Glob列檔、孤立/失敗/不支援結果不得提供正證據。[test: t_probe_source_probe_results]
- [S3] 當有正證據及正確答案時，v04應通過，直接讀取、先cd後cat、grep與sed相同；README、搜尋路徑字串及find列檔雖可成功退出但無標記，應不通過。完整結束且零呼叫、只有Glob、只有已知失敗工具結果皆為有效失敗；已發出支援呼叫卻缺結果、格式無法識別或未準備標記時應記儀器例外、不進有效分母；已有正證據時不受其他呼叫缺結果影響。不能把缺證據當作模型錯誤。[test: t_probe_source_probe_runners]
- [S4] 當批次main連跑或因用量上限重試時，證據應每次嘗試準備且finally還原、透過兩個runner進共用grade，原判分題及C2/C3排除規則應保持；輸出應留source_evidence狀態供查核，不保存完整原始工具輸出，calls/answer/stderr等全部字串欄位亦遮罩當次標記。新GRADER_VERSION應與舊版不同，舊歷史不改寫。[test: t_probe_source_probe_main]

## 實驗證據與限制

governance/review-reports/code-repair-pilot-01/r3-evidence-experiment.json：真shell在臨時副本跑7種命令，4種正常讀碼回傳標記、3種文件/列檔不回傳；加行尾註解前後AST含位置資訊完全相同。尚未呼叫外部模型；已讀官方結果形狀，新adapter的fixture驗證待實作。舊probe fixture只含命令摘要，不能當作新結果解析已驗證，不宣稱已驗所有CLI版本。

歷史t_probe_code_question_regrade只嵌命令摘要，沒有工具結果；改驗「此歷史樣本在新判準下證據不足」並另以同一命令真跑副本生成結果驗通過，不把人工補的結果冒稱歷史原始證據。這是量測輸入前提改變，需單獨記錄，不能灌入好例綠→綠統計。

## 實務隱患

已排除:金流:本案不處理款項。
已排除:對外送出:只本機mock与隔離shell驗證，不執行模型探針或寄送/推送。
已排除:不可逆:只改可還原程式與臨時副本；既有歷史/入帳報告不改。
守衛面:修改量測判準與副本寫入，需設計審；不改代碼審放行邏輯。

## 回退

回退此實作与source_probe題庫欄位，保留新版證據与已分版歷史；回退後C1仍是已知未解，不可宣告pass。若第3輪仍有存活major，沿原案記達上限未收斂，不開新編號繼續修。
