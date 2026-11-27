severity: clean

本輪修補驗收下來沒有發現需要改的問題。

- **正文判法與計劃字面**:`_choice_layer_not_body` 和 `_CHOICE_LAYER_NOT_BODY_RE` 的行為,跟計劃〈用詞〉計劃正文、〈範圍〉8 改寫後的字面一致。含「審計修正紀錄」就排除,〈…〉裡的交叉引用先拿掉再找;「驗收條款」「預期值表」整行比對,可帶一個不含空白的前綴,後面只容括號或冒號說明。「審計修正紀錄外篇」也排除,計劃與測試都寫明這是取捨。
- **語料是否涵蓋 repo 全部同類標題**:我自己 grep 了 `docs/lumos-toolchain-knowledge/Projects` 底下的二級標題,含這三個詞的全部有對應,可歸類的都在 `_CKL_REAL_HEADS`。涵蓋 6 種審計標題寫法、設計標題裡的〈審計修正紀錄〉交叉引用、5 種驗收條款帶說明的寫法(含全形冒號)、純「預期值表」。`Systems` 沒有同類標題;`docs/design` 的「審計修正紀錄」標題不屬於計劃,但規則也涵蓋。
- **旁檔改看加總**:`_choice_layer_plan_sides` 由大到小改旁檔直到內嵌加總不超過上限。`_choice_layer_split_groups` 每組各算一次,旁檔路徑依清單編號加計劃雜湊,同一份計劃在不同組重複寫入沒問題。走旁檔的材料有指路、條款號、段名清單。
- **旁檔內容測試**:`t_choice_layer_side_content` 逐項比對條款原文、預期值表、每段正文,有實質內容。
- **圖譜一致**:筆記 `[test:]` 新增的 `t_choice_plan_sections_real_heads`、`t_choice_layer_plan_sides_total`、`t_choice_layer_side_content` 都存在。`SKILL.md` 新補那句引用的 `cap-retro.json` 在卷證目錄裡。
- **測試與掃描**:
  - `-k t_docs_command_count` 綠(4 passed)。
  - `-k t_choice_plan_sections` 綠(9 passed)。
  - `-k t_choice_layer` 綠(62 passed)。
  - `lumos drift scan` 有列出舊帳(`Issues/code-loop守衛main-direct盲區`、`Systems/autonomous-iteration-loop`、`Systems/verification-rot-eval`、`Systems/回合結束寫法檢查`、`Systems/筆記內容閘`),沒有點到本次改的規格閘或選擇點存活回指條款計劃的筆記。

總結:最高等級是 clean。
