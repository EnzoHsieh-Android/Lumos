severity: major

## F1 新增測試會讓更新後的消費專案全套測試必紅
severity: major
blocking: 是
引句:「    sk = (root / "skills" / "lumos-project-notes" / "SKILL.md").read_text(encoding="utf-8")」
file: `scripts/test_lumos.py:57915`
file: `scripts/lumos:17766`
file: `scripts/lumos:17877`

1. `scripts/test_lumos.py` 會被 vendor 到消費專案，但 `skills/lumos-project-notes/` 明定只存在於工具鏈來源 repo，不會複製到消費專案。新測試卻直接讀這兩個 skill 檔，且沒有先呼叫 `_need_src(...)`。
2. 測試執行器會把這個 `FileNotFoundError` 記成失敗，因此任何更新到 v1.1 後、需要跑全套測試的消費專案都會被 pre-push／CI 擋住。
3. 唯讀等價重現：以實際 vendored 檔案集合模擬消費專案，執行 `t_graph_discipline_negation_revisit`；前四項範本、注入與版本檢查通過，隨即得到 `FileNotFoundError: skills/lumos-project-notes/SKILL.md`。
4. 修法：在測試開頭以 `_need_src("skills/lumos-project-notes/SKILL.md", "skills/lumos-project-notes/commands/03-寫回圖譜.md")` 標明來源 repo 專用，或把 skill 斷言拆成獨立的 source-only 測試。

最高等級:major