# B 席第 1 批標註筆記

本批 14 個編輯案例、57 筆候選；只標待標清單列出的配對。依改動檔案職責與題目 diff 判斷，直接約束該檔的機制優先，一般測試方法或間接消費關係不自動升為必看。

讀取紀錄：初次讀題庫時誤將整份 JSON 輸出，工具結果包含部分其他案例的既有 labels；未讀取另一席本批答案，亦未以既有標籤作為本批判準。此項揭露供評測主持人判斷盲評程序是否需要重做。

## 判 2 的理由

- E05 → Projects/固定席降噪A層_計劃.md：直接規定評測器的參考道排除、固定席指標與逐 split 棘輪口徑，改計分時漏讀會換掉驗收標準。
- E06 → Systems/每支檔有家.md：明定 pre-commit 的索引快照、Gate H 與新增違規阻擋語意，是修改提交掛鉤必須保留的邊界。
- E08 → Systems/測試假綠形態.md：本次修改測試，節點記錄現場未成立及鄰近斷言代打等實際假綠，直接約束測試能否證明所宣稱的行為。
- E08 → Systems/autonomous-iteration-loop.md：說明此測試檔驗證的自動迴圈流程、風險分級重驗與放行邊界，避免把錯誤預設寫成正確期望。
- E10 → Systems/每支檔有家.md：直接說明 pre-push 的逐提交寫回檢查、上線點與新分支範圍，並明令不要與其他掃描範圍合併。
- E10 → Systems/bound-tests-gate.md：直接規定推送時合約測試的執行證據、高低風險分流及失敗訊息，調整測試閘不可漏掉。
- E10 → Projects/enforcement可觀測性_計劃.md：記錄 pre-push 跳閘會連帶繞過合約測試的問題，以及完成事件、跳過與失敗落帳的限制。
- E11 → Projects/code-loop必用守衛_計劃.md：交代 code-loop 留痕綁 HEAD 的有效性模型，是題目忽略本機收斂台帳的直接設計背景。
- E11 → Projects/消費專案接入靜默失效_計劃.md：明記 governance/.gitignore 的正確分工為本機 marker 不版控、治理帳提供 CI 權威，並有初始化弄反的實際缺陷。
- E11 → Issues/code-loop-pass自失效追尾.md：記錄追蹤帳本提交後讓 pass 自失效的事故與簿記豁免，直接影響忽略規則的取捨。
- E11 → Systems/pitfalls-code-loop.md：說明本機留痕、簿記白名單與自我餵食誤觸發，修改 code-loop 目錄的追蹤政策須保留這些前提。
- E13 → Projects/intake守衛_計劃.md：全文 T4 明定 daily-governance 必須呼叫 doctor，這條排程線是提醒升級能運作的必要前提。
- E16 → Systems/授權與歸屬.md：直接點名 3d-force-graph 上游壓縮碼沒有版權 banner，匯出再散布必須另補聲明。

## 開全文的節點與原因

- 開全文：Projects/intake守衛_計劃.md（E13），沒有 summary，需確認日常治理腳本的接線要求。
- 開全文：MOC/index.md（E14），沒有 summary，確認正文是導覽索引而非 lint-watch runner 的行為說明。
- 開全文：Projects/全repo審視_計劃.md（E16），沒有 summary，正文的漏看項、授權主題與結案紀錄提供第三方圖形函式庫的具體背景。
- 開全文：Projects/Codex行為精修_計劃.md（E09），摘要談 Stop hook，需確認實作與同步點是否涉及 settings 合併器；正文顯示註冊命令列不變，核心改在 hook 與探針，判 0。

## 難判與可能分歧的配對

- E02 → 三篇候選均判 1：都對同一支大型主程式有真實約束，但題目是 prospective 內容查找，未直接修改測試閘、doctor 範圍或授權機制；不因共用巨檔就全升 2。
- E03 → Systems/節點範圍與索引守衛.md、Systems/guard-kill.md、Systems/bound-tests-gate.md 均判 1：有測試與合約背景，但融合權重的手算斷言不是這三個機制本身的修改。
- E05 → Projects/推播miss量測_計劃.md 判 0：雖同屬檢索量測，摘要明言本案只交 miss 清單、不做評測題，主體是 recount 儀器。
- E07 → Systems/autonomous-iteration-loop.md 判 1：wrapper 會消費 difficulty 的結果，值得了解上下游；maxr 與 panel 的直接權威不在這篇。
- E08 → Projects/自足性審計閉環_計劃.md 判 1：同一自動化測試領域的背景有用，但不是本題 panel_width 的分級規則。
- E09 → Projects/Codex完全支援_計劃.md 判 1：多平台 hook 合併與註冊架構有用，但題目是 Claude hooks 目錄定位，不直接要求改 Codex 接頭。
- E09 → Issues/探針沙盒改動真全域機器狀態.md 判 1：真 HOME 被沙盒安裝污染是操作全域 settings 時有用的事故背景，但直接事故是 skills 重連，不是合併器本身。
- E09 → Systems/anchor-integrity.md、Systems/canary-audit.md、Systems/design-loop.md、Systems/測試假綠形態.md 均判 0：它們的驗證器或審查背景不足以直接指導 settings 合併器的目錄定位。
- E10 → Systems/design-loop.md、Systems/guard-kill.md 均判 1：分別提供收斂原語與測試 runner 的背景，推送接線的直接規範在其他候選。
- E11 → Projects/棧別提問表態閘_計劃.md、Projects/兩席相反時端出張力_計劃.md、Systems/棧別提問表態閘.md 均判 1：表態 marker 共用 code-loop 目錄，忽略政策有關，但題目聚焦 pass 收斂台帳，表態細節不是必看。
- E11 → Verification/2026-07-05_code-loop必用守衛.md 判 1：提供留痕座標與守衛驗證背景，但含舊 Stop nag 與嚴格 HEAD 等值描述，不能當現行完整規則。
- E12 → Systems/bound-tests-gate.md 判 1：impact 固定席是下游合約測試來源，但本次 incidents 讀取與呈現不直接修改測試判定。
- E13 → Issues/收工閘漏掉純Bash改碼.md 判 0：純 Bash 是修改檔案的工具方式，事故屬 Stop hook 的逐字稿辨識，不能因日常治理腳本也是 Bash 就判相關。
- E16 → Projects/全repo審視_計劃.md 判 1：不是只有連結的樞紐，正文確實分析並記錄圖形函式庫再散布問題；現行必要要求已由授權節點集中說明，故不升 2。
- E16 → Systems/lint-version-watch.md、Systems/linter精選目錄.md 均判 0：版本相同詞不足以建立關係，這兩篇處理 linter 偵測或選型，圖形函式庫是執行期第三方碼。
