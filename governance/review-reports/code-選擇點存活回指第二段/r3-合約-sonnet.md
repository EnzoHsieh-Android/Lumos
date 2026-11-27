severity: minor

三項驗收都過:規格閘那條 REVISIT 已改成日期型、`.GIT` 變體擋住了、議題第 14 條已補進進度節。我只找到一個措辭層級的小問題。

**驗收結果**
- **REVISIT 形狀**:`docs/lumos-toolchain-knowledge/Systems/規格閘.md:119` 現在寫成 `REVISIT:2027-03-01 …`,跟同檔第 81、82 行同形。`python3.14 scripts/lumos drift scan` 的輸出裡沒有 規格閘 或 選擇點 的項目,所以不再是寫下就成立的條件。drift scan 列出的其他問題(`Systems/回合結束寫法檢查.md`、`Systems/筆記內容閘.md` 等)都不在這次改動內。
- **`.GIT` 擋法**:`scripts/lumos:29400` 一帶的 `units()` 改成對路徑各段轉小寫再比對,我用 `Path("sub/.GIT/y.kt")` 和 `Path("a/.Git")` 兩種寫法確認都會擋住。`t_choice_compile_units_guards` 新增了 `sub/.GIT/y.kt` 案例,本機跑 1 passed、0 failed。
- **議題筆記**:`lint` 0 問題,摘要的 `[修法:…]` 寫「剩第 8、9 條…與第 13、14 條」,跟進度節第 13、14 條一致。
- **同類位置**:`.git` 擋法確實只做在 `units()`,不在共用路徑判法。這點已被第 14 條自己記為已知、第三段處理,不算新發現。
- **[test:] 名稱**:`t_choice_cov_groovy_dep`、`t_choice_compile_probe`、`t_choice_compile_units_guards` 都在 `scripts/test_lumos.py` 找得到。

severity: minor
blocking: 否
`docs/lumos-toolchain-knowledge/Issues/選擇點存活回指第一段末輪小問題第二段先修.md` 進度節第 13、14 條都寫「第三段收尾前一起處理」,這是會過期的承諾,但沒有 `REVISIT:` 行,也沒有事件綁定。「什麼條件算修好」節仍只列到第 12 條。這是措辭與形狀的精度問題,不會讓照做的人做錯,也不會擋推送。
引句:「第三段收尾前一起處理(還原抽共用、截斷時只留 e: 行、換候選只清這個平台組的列)」

總結:最高等級是 minor。
