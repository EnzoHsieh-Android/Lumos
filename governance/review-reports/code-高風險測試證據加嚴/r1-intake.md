# r1 收貨紀錄(code-高風險測試證據加嚴)

preflight-4: ran

## 派工與收貨

- 2026-11-05 派三席(正確性、架構對齊、文件一致),材料依 r1-dispatch.json;原派工詞隨 11-05 01:45 當機重開機時 /private/tmp 被清掉,當日重寫後重派,三席都是全新代理。
- 三席報告從子代理逐字稿取出存檔(完成通知會把 < > 轉成跳脫字);存檔前三席都已交回,收齊前沒動工作目錄。
- 收貨三道:quote-check 三份全數錨定;refcheck 三份 missing 0、out_of_range 0;seat-check 只有「派工單另一份材料沒提到」的觀測(各席本來就只派一份材料)。
- 純格式改動(只動總結行,不動任何發現):正確性席第 90 行、文件一致席第 68 行的 `max severity: major`、架構對齊席最後一行的 `severity: minor` 是全份總結句,會被記帳工具當成多一條宣告;改寫成 `總結:全份最高 <值>`。report-normalize 對三份都回「已是正規化格式」。
- 正確性席留了兩個空轉的背景等待迴圈(pgrep 比對到自己的指令列,永遠等不完),編排者收掉;席位報告結論不受影響。
- 席位臨時目錄 /tmp/lumos-seat-work/code-高風險測試證據加嚴/ 收齊後已刪。

## 重現表

| id | 來源 | 重現 | 判定 |
|---|---|---|---|
| c1 | 正確性 #1 | 把 `_live` 改成只認 doing,原測試 -k push_check_expected 照綠(席位實測);補 S9 那支「done 但這次改到計劃檔 → 擋」後,同一改壞跑 -k push_check_expected_scope 翻紅(1 條斷言) | HIT,折入 |
| c2 | 正確性 #2 | 把 `_EXPECTED_PUSH_TAG` 那個分支改成 `if False:`,補斷言後 -k push_check_expected_unsigned 翻紅(標題退回「1 份風險低計劃沒過」) | HIT,折入 |
| c3 | 正確性 #3 | 把指紋的 ensure_ascii 改成 True,原測試照綠(席位實測);補固定值釘子後 -k t_expected_table_fingerprint 翻紅;固定值另用 python3 -c 直接算 hashlib,不經被測函式 | HIT,折入 |
| a1 | 架構對齊 #1 | 讀碼確認:推送前掃描已先讀 spec-gate 閘那份帳,讀不到就先擋;預期值表這段另讀 signoff 閘,兩次是不同閘的篩選。真正的問題是這條備援回的原因帶預期值表標籤,標題會講成「沒過」而不是「帳讀不到」 | HIT,折入:備援改帶帳讀不到的標籤,S11 同程序測試改驗標題 |
| a2 | 架構對齊 #2 | 讀碼確認 `_spec_gate_expected_part` 回 True/False,鄰居 `_spec_gate_pending` 回 rc 或 None | HIT,折入:改成回 1 或 None |
| a3 | 架構對齊 #3 | 讀碼確認 token 先在條件鏈寫一次、再被展開覆寫 | HIT,折入:token 接回條件鏈,origin 照舊另放 |
| a4 | 架構對齊 #4 | 席位標 ⚠ 交編排者:生效日常數給環境變數覆寫,設成 9999 就整道關掉、不留帳 | 放行,理由見下 |
| d1 | 文件一致 #1 | grep 預期值 在注入範本、05 手冊、INDEX、設計審 reference 都是 0 筆;計劃〈做法〉6 明列要同提交改 | HIT,折入:四處補說法、03 手冊補範例與「條款欄不加方括號」、本 repo CLAUDE.md 與 AGENTS.md 用 lumos update 重注、照前例升版號 v1.5 並寫 CHANGELOG(發版照 RELEASING.md 由人裁);設計審 templates.md 沒有講規格閘判風險高的句子,不用改 |
| d2 | 文件一致 #2 | Systems/規格閘 版本行寫 14,程式是 16 | HIT,折入:改 16、標以程式碼為準、補 15 與 16 的沿革 |
| d3 | 文件一致 #3 | responsibility 沒提預期值表、半套那行與流程段沒提 | HIT,折入:三處補上 |

## 放行理由

- a4:計劃決策(生效日判法那一筆,why_chosen)明寫照既有 `LUMOS_PANEL_RETIRE_CUTOFF` 的寫法給環境變數覆寫,測試總開關要靠它;本 repo 威脅模型是單人、AI 依序操作、信賴原則不防刻意繞過;同類常數兩種做法並存是既有狀態,不是這次引入。不修。

## 折入後驗證

- -k expected 115 過 0 紅;-k gov_stats 59 過;-k spec_gate_push 21 過;-k version_pin 5 過;-k discipline 45 過;--suite docs 989 過 0 紅。
- 三道新斷言各改壞一次都翻紅,還原後綠(c1、c2、c3 那三列)。
