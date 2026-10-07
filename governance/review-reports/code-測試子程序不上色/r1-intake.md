# code-測試子程序不上色 r1 收貨

分級 light,一席架構對齊(新席),從逐字稿抽原始最後回覆存檔;report-normalize --write 只把 A2 嚴重度行尾的 ⚠ 搬到下一行(純格式搬移)。quote-check 全錨。

彙整 id:架構對齊 a1–a2。載體:架構對齊席。最高 minor。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| a1 | 讀碼:鄰居守衛(t_runner_isolates_real_home_and_tmp 等)訊息帶領域前綴、有「★前置★ 現場成立」;新測試只有 ①②③ | 不一致;Systems/測試假綠形態 的合約要翻紅釘配前置斷言 | HIT |
| a2 | `grep -n 'NO_COLOR="1"' scripts/test_lumos.py` | search -h 那支仍自帶 NO_COLOR | HIT |

## 處置(全折)

- a1:補前置斷言——不中和時 FORCE_COLOR=3 子程序 traceback 真的帶顏色碼(現場成立);訊息加「不上色:」前綴。無環境變數與 FORCE_COLOR=3 兩種跑法都 4 條全過。
- a2:search -h 那支拿掉自帶的 NO_COLOR(顏色在進入點已關,它本身也會剝顏色碼);FORCE_COLOR=3 下 t_lens_recount_search_multi_r1_codex 6 條全過。

## 修補因果(regression-set)

首輪。
