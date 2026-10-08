# code-ci-wait短sha r1 收貨

席報告 2 份(正確性 2 條 minor、架構對齊 2 條 major)。quote-check 全錨。

彙整 id:正確性 c1–c2、架構對齊 a1–a2。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| a1 a2 | Grep:`_lens_full_sha` 同一條 rev-parse、`_LENS_SHA_RE` 同一個 40/64 正規式 | 重複 | HIT |
| c1 | 計時:新測試修前 32.5 秒(沒帶 --grace 0),修後 4.2 秒 | — | HIT |
| c2 | 讀碼:git 缺席、逾時、短碼歧義都回空,一律講成本機找不到 | 修後列三種可能 | HIT |

## 處置

全折(4 條):改用 `_lens_full_sha` 與 `_LENS_SHA_RE`、刪掉自寫的那份(a1 a2);測試帶 `--grace 0`(c1);報錯列出本機沒有、短碼對到不只一個、git 跑不起來三種(c2)。
