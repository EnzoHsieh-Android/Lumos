# 合併進主線認合進來那側的留痕 r3 收貨

席報告 1 份(繞過r3 3 條)。quote-check 全錨;refcheck 一處 missing 是 `governance/code-loop`(gitignore 的留痕資料夾,本來就不在版控),非錯引。

彙整 id:繞過r3 h1–h3。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| h1 | 席位臨時 repo 實跑:母 (P1, R),R 把 guard.py 還原成主線較早版本 X,`_codeloop_record_valid_ex(X, R)` | (True, 祖先+簿記豁免, False),合併結果退掉 P1 的修補 | HIT |
| — | 編排者:新規則「第一個母是紀錄提交的祖先」對 #28:`git merge-base --is-ancestor d0b24391 afb7115c` | rc0(認) | 新規則不擋正常流程 |
| — | 同上對主線舊紀錄 eeaa6162 | rc1(不認) | 新規則擋舊紀錄 |

## 處置

全折(3 條):h1 紀錄提交必須包含第一個母;h2 推送前掛鉤新分支首推已改寫起點,寫明安全性不靠起點條件;h3 條件 4 加 `-z`。
