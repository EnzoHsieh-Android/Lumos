# code-新寫句子寫法提醒 r2 收貨

席報告 2 份(正確性 2 條、架構對齊 2 條,其中 1 條 major)。quote-check 全錨、refcheck 全對得上。兩席都沒讀上一輪報告(派工詞禁止,收貨看 git status 沒動 repo)。

彙整 id:正確性 c4–c5、架構對齊 a4–a5。

## 根因分組

- 「定義在不在字串裡」另用 tokenize 判:a4(major,第二種做法)、c4(t-string 沒排除,同族)。
- 註解搬錯行:c5、a5(同一處,兩席各自報)。

## 歸因

- a4:修復回歸——tokenize 是上一輪修 c3 時引入的(修前 83067c94 沒有這支函式)。
- c4:原有漏查——修前、修後都判不出 t-string 裡的假定義(正確性席兩版實測)。
- c5 / a5:修復回歸——上一輪抽 `_COUNT_NUM_EDGE` 時把 `_COUNT_NUM_RE` 的註解接到新行尾(正確性席兩版 diff 實測)。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| a4 | grep `tokenize` 整支 scripts/lumos(去掉 _rank_tokenize) | 只在 `_ns_wd_in_string` 出現;drift 那邊同一件事用 `_drift_py_names`(ast) | HIT |
| c4 | 新測試 t_note_wording_def_shapes ⑤:t-string 裡頂格的 TSTR + 另一支檔的真定義 | 修前沒提醒(⑤紅) | HIT |
| c5 a5 | `sed -n` 看 `_COUNT_NUM_EDGE` 那一行 | 尾端掛著「九位數以內」的舊註解 | HIT |

## 處置

全折(4 條):
- a4、c4:拿掉 `_ns_wd_in_string`(tokenize),改成先只解析定義那一段數成員,數字對上才用 `_drift_py_names` 確認哪幾處是真的模組最上層定義;字串、t-string 裡的假定義自然不算。整支解析只在要提醒時付,大於 4 MB 的檔照 `_DRIFT_M1_PARSE_MAX_BYTES` 不解析;解析時同樣關警告。新增測試 ⑤(t-string)⑥(另一支檔的一般字串)。故意改壞三處(不確認、確認時不關警告、真的不只一處也算)全部翻紅。
- c5、a5:註解放回 `_COUNT_NUM_RE` 那一行,`_COUNT_NUM_EDGE` 自己一段註解。
修後重量:沒候選 1.1 秒、最壞 1.4 秒;要對 3 MB 的檔出提醒時那次多約 2.2 秒、330 MB。
