# B 席增量標註：batch6

本批獨立判讀 6 題、31 筆，題目皆為搜尋面；只依查詢字串與候選內容判定，未讀其他評審答案。摘要為主要依據，空摘要或關聯不明時補查正文。0 分均明確寫入 JSON。

## 判 2 的理由

- S17｜Issues/健檢技術棧那段撞到多平台設定就整支中斷.md：直接記錄 pitfalls 把工具檔誤算成消費專案風險的事故，並交代精確檔名與內容指紋的排除邊界。
- S18｜Issues/git-hooks路徑指向樹內_checkout即執行分支碼.md：明確指出 anchor 只擋推送、不保護 checkout 與新增 hook，避免把錨點誤當完整執行防線。
- S20｜Issues/共用工作目錄的未追蹤檔讓全套測試假紅.md：提供以同提交的乾淨 worktree 區分真失敗與工作目錄污染的判準，避免改到沒壞的程式。
- S20｜Issues/git-hooks路徑指向樹內_checkout即執行分支碼.md：直接涵蓋 worktree 驗證席的 checkout 執行風險與現有保護不足。
- S20｜Issues/code-loop-pass不能指定分支.md：交代 detached worktree 的留痕分支錯配、推送受阻與可用繞法，是本專案使用 worktree 審查的關鍵前提。
- S21｜Projects/標籤系統精簡_計劃.md：以實驗證明 BM25F 統計取自候選集，刪除鏡像標籤會連留下的節點分數一起改變，直接否定排序不變的錯誤前提。
- S21｜Projects/檢索核心重建_計劃.md：直接交代 BM25F 目前語料口徑、索引改造邊界與保留既有排序的決策，避免混淆候選召回與排序替換。
- S22｜Projects/主session鏡頭利用率_計劃.md：記錄 TTL 在零注入時仍先開冷卻窗的缺陷，以及改成注入後才寫標記的修正前提。

## 開全文與原因

以下「開全文」包含進入正文後定位相關段落；超長篇的工具回傳有截斷，再定向補讀查詢詞所在段落，未將截斷內容視為已完整讀完。

- 開全文：Issues/ci-wait對當日run判no-run.md，原因：摘要只有空欄位，須確認與 pitfalls 是實質關聯或只共用上游節點。
- 開全文：Issues/git-hooks路徑指向樹內_checkout即執行分支碼.md，原因：摘要空白，須確認 anchor 與 worktree 的具體失效邊界。
- 開全文：MOC/index.md，原因：沒有摘要，確認正文是分類導覽而非 anchor 的機制說明。
- 開全文：Projects/全repo審視_計劃.md，原因：沒有摘要，補讀 kill_recipes 與 BM25F 所在正文段落，區分實質裁定與單純索引。
- 開全文：Projects/intake守衛_計劃.md，原因：沒有摘要，確認正文是否交代 TTL；內容實際是前掃宣告與處置閘。
- 開全文：Projects/圖譜進迴圈入口栓_計劃.md，原因：沒有摘要，確認 BM25F 在入口召回的用途與跨查詢分數限制。
- 開全文：Projects/Codex行為精修_計劃.md，原因：摘要未交代 anchor，全文確認只是實作驗收曾核准基線。
- 開全文：Projects/Codex完全支援_計劃.md，原因：摘要未交代 anchor，補查正文驗收段的錨點覆蓋限制。

## 難判與分界

以下記錄本席的判斷邊界，不推測另一席答案。

- S17｜Issues/code-loop-pass不能指定分支.md＝1：是 pitfalls 分級後審查流程的下游障礙，但不直接說明 pitfalls 的掃描或分級規則。
- S18｜Projects/Codex完全支援_計劃.md＝1：正文確有當時的錨點覆蓋範圍，但屬特定整合案的歷史驗收背景，未升為必看。
- S18｜Issues/收工閘漏掉純Bash改碼.md＝1：指出該 hook 納入錨點與修改須核准，有實用背景，但主題仍是收工偵測缺陷。
- S19｜Projects/全repo審視_計劃.md＝1：正文有 kill_recipes 母體太小、不宜每日輪替的具體理由，並非純導覽；但不教欄位或執行協議。
- S20｜Projects/自足性審計閉環_計劃.md＝0：摘要重點是自動審修流程，沒有足以回答 worktree 查詢的操作或限制。
- S21｜Projects/GraphRAG對節點關聯_調研.md＝1、Projects/多路召回與宣告式欄位_調研.md＝1：提供檢索架構與融合的比較背景，沒有 BM25F 本體的必要操作前提。
- S21｜Projects/圖譜進迴圈入口栓_計劃.md＝1：正文交代 BM25F 消費方式及絕對門檻不可比，實用但主要是入口提醒的設計，不是排序本體的權威說明。
- S21｜Projects/全repo審視_計劃.md＝1：有 bigram OR 加 BM25F 的具體提案與翻案條件，超過純索引，但只是整份審視的一個小項。
- S22｜Projects/Codex完全支援_計劃.md＝1、Systems/codex-harness.md＝1：明列 armed token 的十分鐘 TTL 與領席生命週期，可幫助理解一種 TTL 用途，但不足以代表整體 TTL 機制。
- S22｜Projects/執行DAG_調研.md＝1：明確交代領席 TTL 固定且不可續租的重用限制，是背景用途，不是一般 TTL 權威說明。
- S22｜Projects/intake守衛_計劃.md、Projects/OpenSpec_調研.md、Issues/settle路徑席位對帳無輪次可對.md、Projects/roster對帳併入問閘_計劃.md＝0：其核心是審查或規格流程，不能因 settle 等字串或流程相鄰就視為 TTL 答案。
