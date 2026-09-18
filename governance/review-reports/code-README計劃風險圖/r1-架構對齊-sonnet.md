severity: major

## F1 README.en.md 這段丟了「兩段→連結」的收尾,跟其他章節、跟中文版本都對不上

severity: major
blocking: yes

中文版 README.md 這次改動把「不是每份計劃都要設計審」那段的收尾從「兩段文字內就帶連結」改成「兩段文字後另起一行放連結」,結構仍是 小標→圖→兩段→連結,跟①②④其他小節一致:

引句:「[看判準、依據與目前量到的偏差](docs/心智模型.md#規格閘計劃先分風險高低)」

但英文版 README.en.md 同一小節改完之後,兩段文字後面**沒有補對應的連結**,直接接到下一個 `#### Five layers of quality control` 小標:

引句:「The sorting is mechanical and defaults to high risk; authors can only tighten it. It catches missing proof, not wrong proof.」

對照:
- file: `README.en.md:119`(① Notes 收尾連結 `[See note structure and impact-query illustrations](docs/mental-model.md#9-visual-reference)`)
- file: `README.en.md:137`(② Dispatch 收尾連結 `[See the full dispatch, intake, and disposal-gate flow](docs/mental-model.md#7-reading-the-detailed-diagrams)`)
- file: `README.en.md:181`(五層品質防線後段仍保留連結 `[Zoom in on how the review step itself is layered...]`)
- file: `README.md`(中文版同段已補上對應連結)

英文讀者在這個小節少了一個「看判準、依據與偏差」的出口,跟中文版不對等,也跟 README.en.md 自己其餘每個小節「小標→圖→兩段→連結」的結構不一致。實測 `docs/mental-model.md` 目前沒有 `#規格閘計劃先分風險高低` 對應的英文錨點可連,所以這不是漏貼連結那麼小,可能是英文版對應章節/錨點本來就沒補齊。
