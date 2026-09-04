preflight-4: ran

# r1 收貨紀錄(Codex行為精修)

## 前掃(2026-09-05,sonnet)
- ① 1 條:「`--harness codex` 分支」以既有語氣寫,實為新寫(五支 hook 零 argv 解析)→ 修真檔明寫「新增」。
- ② 無。③ 無。
- ④ 2 條:「只差輸出形狀」低估 → 改列要新寫的四件事;「任何例外照舊 rc0」不實(main 只包 JSON 解析)→ 改成「新包一層 blanket try/except」。
- 查證屬實:2026-07-06 撤 Stop nag(commit 7b3aaec,撤的是 code-loop-guard 非本 hook)、探針走真 ~/.codex hook、`-k` 子集存在。

## 外家否決(Codex)9 條(1 blocker 7 major 1 minor;引句 9/9、行號 4/4)
- #1(blocker)逐字稿版本表只有 0.144.1、全域已 0.153.2 → Stop 分支永遠到不了 HIT:重現見上(現況回空);折入:版本表加 0.153.2(格式用今晚真實稿驗過同形),驗收加「版本表含當前 codex --version」。
- #2 stop_hook_active 是同 turn 語意 HIT:措辭修正,session 標記另立為產品政策。#3 標記在輸出前寫、多 hook 覆蓋 HIT:折入 O_EXCL 原子建檔且先印 JSON 再寫標記。#4 24 小時清與「同 session 一次」衝突 HIT:承諾改「同 session 七天內一次」、清 7 天。#5 blanket try/except 改變 Claude 路徑 HIT:折入只包 Codex 新分支。#6 迴圈上限措辭 HIT:改「文件未載、原始碼未見上限」。#7 實驗只量次數與時間 HIT:折入記 turn_id 是否同一、token usage。#8 reason 無長度上限、2500 tokens 後截 HIT:折入 指令行放最前、檔案清單 cap 10、總長 ≤1500 字。#9 驗收缺端到端事件序列 HIT:折入 f02 後組保存逐字稿與 usage,斷言第二次 Stop 的 stop_hook_active。
## 架構對齊 3 條(2 major 1 minor)
- major① 擋停邏輯在 hook 內 vs 薄殼分工 HIT:折入=計劃明寫有意識偏離與理由(check-graph-sync 本就是厚 hook、只服務 Codex、40 行 vs 開新指令要同步五份文件),連結派工鏡頭注入_計劃。major② 2026-07-06「Stop 只注入不擋」裁定未正面回應 HIT:折入=三點結構性差異(條件擋/一次性/Codex Stop 語意)+標明有意識偏離不撤舊裁定+撤回條件(f02 補寫率),related 連上 code-loop必用守衛_計劃。minor 標記目錄 owner 檢查:折入。
## 整合知識同步 8 條(2 blocker 4 major 2 minor;引句/行號 17/17)
- 「hook 從不擋」四處文件(docstring/graph-sync-coverage/圖譜即合約/commands 08)HIT:折入同步點清單。`LUMOS_STOP_BLOCK_OFF` 未列任務、探針沒設 HIT:折入產品碼檢查+探針 `--stop-block` 旗標。env 傳遞未驗 HIT:★實測會傳★(Stop hook 讀到兩個變數)。範本寫死本 repo 指令 HIT:改通用句,具體指令進本 repo 自己段落。
## 邊界可執行 12 條(2 blocker 6 major 4 minor;引句/行號機驗見上)
- blocker① 探針不帶 bypass 旗標 → hook 不 fire:本機已審信任(f01/f02 稿有注入)故 HIT 一半;折入探針 `--codex-bypass-hook-trust` 旗標+結果記 hooks_fired。blocker② 範本寫死本 repo 指令=整合同抓,已折。
- stderr 對 Codex 模型零訊號 HIT:誠實寫進計劃。Stop 對子代理誤 fire?★實測不會★(子代理走 SubagentStop)。blanket try/except 吞掉 stderr 提醒=外家 #5 同題(已改只包 Codex 分支)。minor(session_id 缺/路徑安全/TOCTOU/reason 上限/10 秒 timeout):前四條已折(O_EXCL、cap),timeout:Stop 註冊 10 秒與現況相同、block 分支只多一次寫檔。
- 邊界 #3 引句「新包一層 blanket try/except…」錨不到快照(MISS,不採信);同題外家 #5 已折(只包 Codex 分支)。
## 通才 9 條(1 blocker 2 major 6 minor;引句 9/9 全錨、refcheck 9/9)
- F1 版本表 HIT(=外家 #1,實作項);F2 多一輪計時 HIT:折入(read-only 外家永不擋/環境變數開關/f02 timeout 600/只擋一次);F3 檔名進 prompt HIT:折入 `_safe_path` 消毒+測試⑬;F4–F7 定義/分類/論證補進 spec;F8 已在測試⑦;F9 標題「三條」四條=既有落差,順手改「鐵則」。同輪有 blocker → accepted 空。
