severity: major

## Finding 1 — 實際載入的 skill 未接上試行入口

severity: major

blocking: 是

引句:「本 repo 的 `skills/lumos-code-loop/SKILL.md` 已有入口。第2案啟動前核對實際載入的 skill 版本，未同步時由編排者直接讀本計劃，開工與收尾依本表執行；第五次收尾觸發回顧。」

具體情境：設計閘 PASS 後，新會談接手第2案。Codex 實際從 `~/.agents/skills/` 載入 skill，而目前該副本沒有試行入口，也沒有 reference 的「修復穩定性試行」段。編排者因此只會照普通 code-loop 執行，不會知道自己還必須「核對實際載入版本」，也不會登記序號、開始時間、好例驗證或來源分類。「未同步時直接讀計劃」成為只有讀過計劃的人才看得到的自我指涉指令，無法作為跨會談入口。

同一缺口也影響回退：若日後已同步的使用者層副本沒有隨 repo 回退一起更新，新會談仍可能繼續執行已撤下的試行文字。

證據：

- 圖譜已明載使用者層副本尚未同步：`docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:22`
- Codex 實際 skill 來源是 `~/.agents/skills/`：`docs/lumos-toolchain-knowledge/Systems/codex-harness.md:65`
- 現有載入副本從一般入口直接進入普通輪次，沒有試行入口：`/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md:11`、`/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md:16`
- repo 來源才具有試行入口與修復步驟：`skills/lumos-code-loop/SKILL.md:16`、`skills/lumos-code-loop/SKILL.md:46`
- repo reference 才具有完整試行操作表：`skills/lumos-code-loop/reference.md:122`

最小修正：把「實際 instruction delivery 已生效」納入改道生效條件。在登記第2案前，必須完成並記錄以下其一：

1. 用既有安裝機制同步 `~/.agents/skills/lumos-code-loop/{SKILL.md,reference.md}`，以新會談重新載入，並以試行入口文字或檔案雜湊驗證；或
2. 若不安裝未推送版本，為每個候選新工作提供不可省略的外部入口，明確附本計劃路徑及停止狀態。

回退也須對稱同步實際載入副本。上述驗證未完成時，不得把改道驗證改成 PASS，也不得登記第2案。

## 無 finding 的逐節紀錄

- 開頭、PRIOR-ART、RETIRE-IF：已讀；範圍、五案天花板及到期裁決均清楚。
- S1：除上述入口可達性外，資格、重開同格、中止仍計數、樣本邊界及禁止事後換掉難案均可執行。
- S2：根因分組、保留 finding id、壞例紅綠、好例綠綠、回歸與失敗路徑要求，和 repo reference 一致，未見其他缺口。
- S3：同例前後版的四類來源判定、待查處置及不改嚴重度規則明確。
- S4：原席驗原問題、新席看完整差異與呼叫者、正式輪次及三輪上限均維持。
- S5：intake 只入帳一次、補件去下一份 intake 或計劃、未知值、時間聯集與14日觀測窗均有明確口徑。
- 收斂性診斷與最小調整：有區分「修復引入」和「舊缺口未涵蓋」，沒有把新表宣稱成已驗有效。
- 落點：repo skill、reference、Systems 與本計劃的責任分界清楚。
- 試行登記：五格、首案歷史位置、後四案資格及單一編排者前提已交代；除 Finding 1 外未見其他執行矛盾。
- 待決設計閘：明確要求精簡版另行取得 disposal PASS；圖譜仍維持 pending，未偷移用舊 PASS。見 `docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:16`、`:24`。
- 歷史 FAIL：第1案第四輪 FAIL、樣本外儀器第三輪 FAIL 與後來例外 PASS 均分開保存，沒有改寫原結果。見 `docs/lumos-toolchain-knowledge/Verification/2026-10-04_修復穩定性試行第1案例外續修.md:18`、`:35-39`。
- 實務隱患：金流、外送、不可逆及守衛面均有處置；守衛面保持高風險設計審，合理。
- 證據：intake、版本、時間、來源分類、escape 與補件位置均有可執行規則，且沒有要求覆寫已凍結報告。
- 回退：停止時間、在途案件、既有名額與普通 code-loop 的後續處理均明確；僅實際載入副本的同步問題併入 Finding 1。
- 審計修正紀錄：清楚區分舊正式審、撤回草案與本精簡版，未把診斷材料冒充 PASS。
- 第1案與例外續修：輪次、授權範圍、局部綠測試、未處置缺陷、未知耗時及停止狀態均保留，沒有以局部證據宣稱整案放行。

凍結檔已核對為151行，SHA-256 為 `6a6d89f829b4b0f0c66fed47b9daf76621fc9fb306223e790baacbb4a2afc097`；目前計劃與凍結快照逐位元相同。未讀取其他審查員報告。`refcheck` 為2項通過、`lint` 為0問題；`spec-gate` 在此唯讀環境因無可用暫存目錄而未完成相依測試，因此未據此宣稱 PASS。

最高嚴重度: major；blocking 數: 1