C1. 精簡版交付源目錄由 `cp -R skills/lumos-project-notes slim/skills/` 建立副本 | 預期驗證點: repo 內是否存在 `slim/skills/lumos-project-notes/`（SKILL.md + reference.md），且與 `skills/lumos-project-notes` 為同源複製

C2. `slim-scan.py` 初次掃描對複製後的 slim skill 產生 129 條候選懸空引用 | 預期驗證點: scripts/slim-scan.py 執行紀錄／[[Verification/2026-07-31_slim-skill與readme落地]] 是否記載 129 這個初始數字

C3. 經人工逐條裁決（改寫/刪除/判假陽性）後重跑掃描器，候選數收斂至 14 條 | 預期驗證點: 對 slim/skills/lumos-project-notes/{SKILL.md,reference.md} 重跑 scripts/slim-scan.py 的候選計數

C4. SKILL.md 檔案本身最終收斂到 0 候選（懸空引用全部落在 reference.md） | 預期驗證點: scripts/slim-scan.py 單獨對 slim/skills/lumos-project-notes/SKILL.md 執行的候選數

C5. reference.md 的「子命令全覽」段落原列舉 53 支指令，修剪後改寫成僅列 24 支保留指令，並分四類：讀取/導航 12、巡檢/治理 4、寫入 7、合約守衛 1（合計 24） | 預期驗證點: slim/skills/lumos-project-notes/reference.md 中「子命令全覽」該段落的指令清單與分類計數

C6. 修剪過程整段刪除三處內容：① `pitfall_when` 欄位說明 ② 「對抗設計審計的 canary」整節 ③ 「安裝/生命週期」指令表（涵蓋已砍的 install/bootstrap 等四支指令） | 預期驗證點: slim/skills/lumos-project-notes/{SKILL.md,reference.md} 中應不存在 `pitfall_when` 欄位說明段落、canary 對抗設計審計節、安裝/生命週期指令表

C7. reference.md 第 340 行的 `npx playwright install` 是掃描器唯一一條「形態不同」的真假陽性，因裸散文 `install` 字串被誤判為 lumos 指令，與 lumos 指令本身無關 | 預期驗證點: slim/skills/lumos-project-notes/reference.md:340 是否含 `npx playwright install`

C8. reference.md 第 60 行（2026-07-31 終審 C1 修復）新增段落揭露 doctor 建議使用者跑 lumos init/update/self-audit，但這三支指令在精簡版中未交付 | 預期驗證點: slim/skills/lumos-project-notes/reference.md:60 附近的段落內容

C9. reference.md 第 18 行（2026-07-31 終審 C4 修復）將原本「下表指令前綴與全域 lumos 等價」的敘述改寫為「vendored 情境下不等價、不要用 python3 scripts/lumos」 | 預期驗證點: slim/skills/lumos-project-notes/reference.md:18 附近段落文字

C10. C4 修復同時將 reference.md 內共 37 處 `python3 scripts/lumos <cmd>` 指令前綴改為 `lumos` | 預期驗證點: 對比修復前後 reference.md 中 `python3 scripts/lumos ` 與裸 `lumos ` 前綴出現次數（差異應為 37 處變動，且改動只落在保留指令如 append/context/doctor 上）

C11. 終審修復（C1+C4）後候選數從 14 條上升為 21 條（SKILL.md+reference.md 合計） | 預期驗證點: [[Verification/2026-07-31_公開精簡版終審修復]] 記載的候選計數變化 14→21

C12. reference.md 第 679 行（2026-08-01 補修）原指向本包未交付的 `Projects/from-scratch重生守衛_計劃` 與 `governance/golden/fromscratch-m1/`，已改寫為明示「本精簡版沒有交付那些檔案」 | 預期驗證點: slim/skills/lumos-project-notes/reference.md:679 附近段落內容，且 slim/ 目錄下應查無 `governance/golden/fromscratch-m1/`

C13. `slim-scan.py` 只掃描指令名的五種形態（prefixed/bare-token/skill-name/span/prose），無法偵測路徑型懸空引用（如圖譜節點路徑、governance/ 語料目錄） | 預期驗證點: scripts/slim-scan.py 原始碼中比對邏輯是否僅涵蓋上述五種指令名形態、且無路徑字串比對邏輯

C14. `claude-block.md` 與交付版 `SKILL.md` 原本只寫「summary 欄位/summary block」，未明講必須寫在 frontmatter 的 `summary:` 底下（而非 body 的 `## Summary` 標題），2026-08-01 已各補一段含正確 YAML 範例的警告 | 預期驗證點: claude-block.md 與 slim/skills/lumos-project-notes/SKILL.md 是否含針對 summary 欄位位置的 YAML 範例警告段落

C15. 129 條候選最終裁決統計：改寫句子 50 條、整段/整列刪除 78 條、初裁即判假陽性 1 條（合計 129） | 預期驗證點: [[Verification/2026-07-31_slim-skill與readme落地]] 記載的裁決分類統計（50+78+1=129）
