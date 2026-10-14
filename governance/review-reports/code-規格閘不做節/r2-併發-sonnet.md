severity: minor

我在 `_nogo_skip_lines`、`_door_judge`、`_h2_section_lines` 上用 python3.14 跑了病態輸入,耗時都隨輸入大小線性增長,沒有 finding。只有 `_NOGO_NEG_RE` 的否定字樣太寬這一條 minor,不在併發與資源的重點範圍內,是順帶看到的。

**實測結果**(實驗檔已刪)
- 20 萬個項目(約 2.9MB):`_nogo_skip_lines` 0.72 秒,整個 `_door_judge` 3.4 秒。
- 20 萬組重複的 `## 不做` 標題:`_nogo_skip_lines` 0.91 秒,`_door_judge` 3.5 秒。
- 單行 200 萬個 tab、空白或全形空白,以及 `- - - …` 這類像分隔線的行:`_nogo_skip_lines` 最多 0.21 秒,`_door_judge` 最多 0.86 秒。
- 20 萬行縮排參差的續行:`_nogo_skip_lines` 0.32 秒。
- 20 萬個空行:`_nogo_skip_lines` 0.08 秒。
- 200 萬字元的超長單行(`_NOGO_NEG_RE`、`_NOGO_ITEM_RE`、分隔線正規式):沒有退化成指數時間。

severity: minor
blocking: 否 — 只是讓風險判定偏鬆,有一點風險但留痕仍綁被跳過的詞,不是效能或資源問題
引句:「_NOGO_NEG_RE = re.compile(r"不|沒有|無|排除|暫緩|非本期|\bout of scope\b|\bnot\b", re.I)」
問題:中文否定字樣是子字串比對,「不」「無」出現在任何詞裡都算。「無縫」「不僅」「不間斷」等詞,和「不做」的語意無關。
具體失敗情境:我實測 `## 不做` 下的 `- 本版無縫串接 Stripe 扣款` 和 `- 不僅實作退款也實作扣款` 都被跳過,實際在做的金流項目判成風險低。只有 `- 實作 Stripe 扣款` 這種完全沒有「不」「無」的行不會被跳過。留痕會記下被跳過的詞,推送前仍會重判,所以影響有限。
佐證:``file: `scripts/lumos:8012` ``(`_NOGO_NEG_RE.search` 呼叫處)

已讀,無 finding:
- 新的否定字樣正規式在病態輸入下的時間。
- `_nogo_width` 與續行、子項目的計算。
- 空行後只准接項目的狀態轉換。
- `_h2_section_lines` 之後每份計劃多掃幾次:`_door_judge` 在推送前流程裡跑兩次,每次多一趟線性掃描,可忽略。
- 雜湊前去掉全部空白,以及指紋改用版本號、不再取原始碼。

最高等級 minor,blocking 0 條。
