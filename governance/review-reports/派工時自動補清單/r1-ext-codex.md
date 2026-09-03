# r1 外家否決席報告(Codex, sandbox=read-only, 前景執行)

---

1. `updatedInput` 的關鍵追測沒有原始證據，現存材料只能證明 hook 看得到 Agent 呼叫，不能獨立證明派工詞確實被改寫。所謂原始 log 僅保存 deny 測試與 `SubagentStart` 輸入，沒有 updatedInput 回傳 JSON、改寫前 prompt、子代理原始回覆或 transcript；追測 commit 也只新增 README 與敘述性 Verification。因此「子代理列出三項」仍可能有共享 transcript/context、人工轉錄錯誤等替代解釋，第三方無法排除。至少應凍結完整 hook 腳本、stdin/stdout、原始 prompt、子代理回覆及 session transcript 的雜湊。
severity: major
blocking: 是；核心可行性宣稱目前只有作者敘述，依現存證物不可重現或反駁。
引句:「回 `hookSpecificOutput.updatedInput` **可以改寫派工詞**——實測子代理原封不動列出只存在於注入文字裡的三個節點名。」
file: `governance/eval/hook-intercept/2026-09-03-raw-hook-log.txt:1` 至 `:13` 只有 deny 與事件輸入，完全沒有 updatedInput 追測輸出。
file: `governance/eval/hook-intercept/README.md:38` 至 `:48` 只給省略成 `{ ...原 tool_input... }` 的示意與結果敘述，不是可直接重跑的完整腳本或原始結果。
file: `docs/lumos-toolchain-knowledge/Verification/2026-09-03_派工攔截點實測.md:58` 至 `:64` 再次敘述結論，但沒有連到新增的原始 artefact。

2. 「碰程式碼就是 20–21 篇，中間沒有級距」被真實 commit diff 直接推翻，而且差異不是小誤差。獨立重跑得到：`67b035e^..67b035e` 為 1 個 code seed、固定席 0；`84d400c^..84d400c` 為 3 個 code seed、固定席 3；`e0730ff^..e0730ff` 為 5 個 seed、固定席 4；`c3b4f3f^..c3b4f3f` 為 11 個 seed、固定席 12；`8466036^..8466036` 為 5 個 seed、固定席 21。中間級距明確存在，小 code diff 也可能是 0。這會改寫清單長度、截斷策略與效能論證。
severity: major
blocking: 是；設計用錯誤的雙峰模型排除了可行的按量分級方案。
引句:「★關鍵形狀:固定席篇數與改動大小幾乎無關——碰到程式碼就是 20-21 篇,只碰文件就是 0 篇。中間沒有級距。★」
file: `scripts/lumos:16318` 至 `:16327` 顯示「code seed」其實是排除少數文件格式後的路徑過濾，不保證每個程式檔都有圖譜覆蓋。
file: `scripts/lumos:16368` 至 `:16413` 顯示固定席是逐檔結果聯集，數量取決於具體檔案和圖譜關聯，不是 code/doc 二值函數。
file: `scripts/lumos:16430` 至 `:16437` 的 JSON `meta.pinned` 是上述重跑採用的機械計數欄。

3. 「歷史 60 份、平均 6.8、九成在 21 內、最大 42」無法從 repo 現存凍結 patch 重現，且 spec 沒交代樣本清單與去重規則。按 `*snapshot*.patch` 排除 `asdispatch` 後得到 62 份：中位 3、平均 5.710、61/62＝98.4% 在 21 內、最大 24；按治理帳 `snapshot_path` 去重且檔案仍存在得到 59 份：中位 3、平均 5.102、58/59＝98.3% 在 21 內、最大 24。兩個合理口徑都對不上 60、6.8、90%、42。雖然重算結果反而更支持「通常很小」，但原宣稱仍屬不可稽核數字。
severity: major
blocking: 是；效能決策依賴的母體定義與統計無法重現，必須先附固定樣本 manifest 和計數程式。
引句:「歷史 60 份凍結 patch 機械數過——★中位 **3 檔**、平均 6.8 檔、九成落在 **21 檔**以內、最大 42 檔★」
file: `governance/replay/code-entry-latch/verdict.json:9` 展示治理帳以 `snapshot_path` 指向凍結 patch 的實際資料形態。
file: `governance/review-reports/code-prose-conv-impl/r1-snapshot.patch:1` 是現存樣本中依 diff header 重算為 24 檔的最大值之一；現存樣本找不到 42 檔。
file: `scripts/lumos:16354` 至 `:16367` 顯示工具本身以 `git diff --name-only` 再過濾計算檔數；spec 未說歷史統計是否採同一口徑。

4. 錨點保護不了真正執行中的全域 hook，安全主張打錯資產。`anchor verify` 只雜湊 repo 內固定五檔；目前沒有任何 Claude hook 在名單內。即使日後把 repo 內 hook source 加進去，Claude 實際執行的是 `~/.claude/hooks/...` 的安裝副本，攻擊者竄改該副本或 `~/.claude/settings.json` 不會改變 repo baseline。pre-push 還可用 `--no-verify` 跳過；CI 只 checkout repo，自然也看不到本機全域副本。
severity: blocker
blocking: 是；spec 把「repo 原始碼防無痕變更」誤當成「執行中 prompt 改寫器完整性」，後門風險沒有被所提控制覆蓋。
引句:「這個 hook 本身必須進錨點保護清單。此機制與提示注入技術上是同一件事,差別只在善意」
file: `scripts/lumos:11404` 至 `:11410` 的 `ANCHOR_FILES` 只有兩支測試與三支 git hook。
file: `scripts/lumos:12252` 至 `:12259` 只讀 `repo_root / rel` 算 SHA-256，不檢查 `~/.claude/hooks` 或 settings。
file: `scripts/hooks/pre-push:45` 至 `:60` 只在本機 push 前呼叫 anchor，且 `:57` 明列 `--no-verify` 逃生。
file: `.github/workflows/ci.yml:56` 至 `:59` 的 CI 也只驗 repository baseline。
file: `~/.claude/settings.json:19` 至 `:27` 證明實際執行目標是 `${HOME}/.claude/hooks/impact-hook.py`。

5. 規定永遠回 `permissionDecision:"allow"` 不只是第二種做法，還把「改 prompt」不必要地耦合成「替 Agent 工具作權限決定」。既有 hook 明文只用 `additionalContext`、永不改 permissionDecision；本案卻要求 allow。若宿主原本需要詢問、政策判定或其他 hook 拒絕，這個 allow 的合併語意尚未實測，可能造成權限旁路。`updatedInput` 與 permission decision 是兩個獨立能力；要改 input 不應順手授權。
severity: blocker
blocking: 是；在未證明多 hook 合併與權限語意前，主動 allow 可能擴張 Agent 呼叫權限。
引句:「本案唯一允許的回傳是 `permissionDecision:"allow"` 加 `updatedInput`;★任何情況都不得回 `deny`★。」
file: `~/.claude/hooks/impact-hook.py:384` 至 `:391` 的既有做法只回 `additionalContext`。
file: `~/.claude/hooks/impact-hook.py:394` 至 `:415` 明文「永不 block、永不改 permissionDecision」並展示輸出結構。
file: `governance/eval/hook-intercept/README.md:40` 至 `:43` 把 allow 與 updatedInput 綁在同一追測，沒有 allow 缺席時的對照組，也沒有多 hook/既有權限衝突測試。

6. `additionalContext` 不能視為已證明可達成同一目的，但 spec 也不能把本案淡寫成既有 hook 的「第二個消費者」。現有註解說 PreToolUse additionalContext 出現在 tool result 旁；對 Agent 而言，工具輸入已形成，甚至可能在 child 執行後才回到 parent，因此沒有證據會進入該次 child prompt。若採 updatedInput，這就是新的 prompt-rewrite trust primitive，應有獨立合約、測試、安裝與安全模型，而非沿用 additionalContext 的風險結論。
severity: major
blocking: 是；現有機制無等價證據，新機制又尚未被當成獨立安全邊界設計。
引句:「本 repo 已有一支同位置的 hook(改檔前注入合約提示),本案是它的第二個消費者。」
file: `~/.claude/hooks/impact-hook.py:397` 至 `:401` 明記 additionalContext 注在 tool result 旁，且要求版本實測。
file: `~/.claude/hooks/impact-hook.py:425` 至 `:432` 顯示既有 hook 只處理 Edit/Write/MultiEdit，沒有 Agent 路徑。
file: `governance/eval/hook-intercept/README.md:36` 至 `:48` 顯示本案真正依賴的是另一個欄位 `updatedInput`。

7. spec 只保護 hook 程式，卻沒保護被塞進 prompt 的資料；這是更直接的提示注入面。固定席節點名、摘要、合約內容都來自待審 repo/分支，而該分支正可能是攻擊者控制的輸入。只要求「中性框架」無法阻止節點內容本身包含「忽略前文、洩漏秘密、執行命令」等文字；若依 spec 要「貼內容不能只貼路徑」，攻擊面更大。錨點即使完善，也只證明載具沒變，完全不證明載荷可信。
severity: blocker
blocking: 是；本案建立了從不受信任 repository 文字到子代理指令面的自動通道，卻沒有資料消毒、引用隔離或信任分級。
引句:「本案注入必須貼內容,不能貼路徑;會加劇未解 3 的長度問題」
file: `~/.claude/hooks/impact-hook.py:332` 至 `:380` 顯示既有格式化器會把節點、trigger 與指令句組成自然語言 context，沒有把內容標成不可執行資料的結構化隔離。
file: `scripts/lumos:16374` 至 `:16383` 顯示 impact 查詢直接取待審 diff hunk 與 repo 圖譜計算，輸入信任邊界就在被審分支。
file: `scripts/lumos:16442` 至 `:16447` 顯示輸出包含圖譜節點名稱與關聯來源，未做 prompt-oriented escaping。

8. 鄰案六死因的「二不適用、四適用」分類本身大致成立，但 spec 隨後又重新開放已判適用的 top-N 路線，論證只是把負擔換人，沒有消滅步驟。要取得未貼出的完整內容，仍有人必須再次呼叫工具；而審查員比編排者更缺 diff-range 真相，還可能每席重複計算。這不但把步驟裝回來，還從一次中央計算放大成 N 席重算。角色不同不改變流程成本與資訊缺失。
severity: major
blocking: 是；在固定席可能超長時，完整貼會爆 prompt，截斷又重現前案死因，spec 尚無可執行的第三條路。
引句:「而是變成**審查員的可選動作**:它拿到 20 篇的名單 + 前 N 篇的內容,要不要自己展開是它的判斷」
file: `docs/lumos-toolchain-knowledge/Projects/impact鏡頭機械化_計劃.md:69` 至 `:74` 記錄截斷、證物污染與範圍口徑等獨立死因。
file: `docs/lumos-toolchain-knowledge/Projects/code席爆炸半徑供糧_計劃.md:28` 至 `:36` 明確裁定 top-N 是把已消滅步驟裝回來，且固定席無上限。
file: `scripts/lumos:16410` 至 `:16413` 顯示固定席 `pins` 全保、只有 free 席受 top 限制；底層原語本來就沒有固定席 top-N 語意。

最嚴重 severity: blocker；blocking 共 8 條。
tokens used
191,359