severity: major

## DESIGN-ROLLBACK-1：改名兩側使用不同 Git 語意，真正程式可被當成卷證排除

severity: major

blocking: 是

引句:「程式副檔名、無副檔名腳本與可執行檔保留；無副檔名普通卷證按凍結首行排除」

觀察：

`_review_role_changed_files` 用 `--name-status -M`，改名時只把新路徑放入 `out`；接著 `_impact_diff_modes` 卻用 `--no-renames`，把同一變更拆成舊路徑刪除與新路徑新增。最後的篩選只遍歷前者留下的新路徑，舊程式路徑從未交給 `_impact_diff_seed_ok`。

具體錯行為：把 `src/tool.py` 改名為 `governance/review-reports/case/report.txt`，並由 100755 改成 100644 時：

- raw 模式資料知道 `src/tool.py` 被刪除；
- 角色消費者只評估新 `report.txt`；
- 新路徑被判成已知普通卷證而排除；
- 舊 `.py` 的刪除不會成為種子，真正程式的角色鏡頭、家與事故可能全部漏掉。

`cmd_impact_diff` 的候選清單也未明確關閉改名偵測，因此同樣存在受 Git 設定／預設改名語意影響的落差。既有 code-loop 路徑已明確使用 `--no-renames` 避免這種跨邊界搬移漏判，新的共享入口沒有保持相同邊界。

file: scripts/lumos:24366  
file: scripts/lumos:24370  
file: scripts/lumos:24378  
file: scripts/lumos:24383  
file: scripts/lumos:24386  
file: scripts/lumos:41027  
file: scripts/lumos:41033  
file: scripts/lumos:41045  
file: scripts/lumos:41145  
file: scripts/lumos:41151  
file: scripts/lumos:41156  
file: scripts/lumos:44270  
file: scripts/lumos:44282  
file: scripts/test_lumos.py:23087  
file: scripts/test_lumos.py:23134  
file: scripts/test_lumos.py:38390  
file: scripts/test_lumos.py:38405  

判準：

候選路徑與模式／物件解析必須採相同的改名語意，並加入「程式由普通目錄改名進簿記目錄，同時改副檔名或模式」的控制案例。驗收需證明舊側刪除仍保留種子、家、事故及角色消費者輸入；不限定必須另建新機制。

## 逐節結果

- 標題、背景、兩條 `PRIOR-ART`：無 finding；既有分類、Git 凍結物件及不混入原分支的方向一致。
- 兩條 `RETIRE-IF`：無 finding；正式來源清單與 fixture 改成可控時鐘都是可發生、可判定的撤除事件。
- 「最小改法」：有 DESIGN-ROLLBACK-1；改名跨越簿記邊界時沒有完整兌現保留承諾。
- 「證據與範圍」：無額外 finding；獨立分支、實作後補審及不重設原代碼審輪次的界線一致。
- 「實務隱患」：無額外 finding；守衛面沒有被錯誤排除。
- 「回退」：無 finding；回退明確恢復已知壞行為，不冒稱為通過版本，控制測試名稱存在。
- 「終審揭露的分類例外」：無額外 finding；副檔名、模式、刪檔與 staged 索引案例均有對應實作和測試，但未覆蓋上述跨邊界改名。
- 「第二輪完整例外核對」：無額外 finding；raw parser、物件選擇、大小上限及保守保留語意與程式相符。
- 「修復驗證的時間前提」：無 finding；零預算在任何 Git／選檔前返回；三個正面段使用 30 秒，正式預設仍為 3 秒。

## 已讀材料

- `/private/tmp/lumos-review-artifact-impact-inputs/CLAUDE.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/MOC/index.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-snapshot.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-lens.txt`
- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/lumos`
- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/test_lumos.py`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`

另以 `lumos contracts` 讀取三個 Systems 的合約。未讀其他 `governance/review-reports/` 報告或結果。

臨時 Git 重現因唯讀 sandbox 拒絕建立臨時目錄而未能執行；這不算實驗通過。上述 finding 由兩條明確的程式控制流交叉證成。

最嚴重：major。blocking 總數：1。