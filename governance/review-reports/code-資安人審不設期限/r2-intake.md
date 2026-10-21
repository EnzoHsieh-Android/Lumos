# r2 收貨紀錄

## 機械驗證

- 單reviewer-sonnet:第一次交回的 F1 標 severity major、blocking 否,兩欄矛盾,退回該席只就 F1 重判;它維持 major、blocking 改是,整份重交。quote-check 全數錨定、格式不用改。
- 架構對齊-sonnet:quote-check 全數錨定、格式不用改。

## 修補因果

- 兩席的四條都不是上一輪修補造成的行為退化:s-F1 是上一輪新加的判不適用條件少一個反例(條件本身對),a-F1 是上一輪新加的撤銷回溯寫成第二道判法(行為對、寫法不一致),s-F2 與 a-F2 是文件與命名。regression_set:none(判過)。

## 重現表

| id | 席 | 怎麼重現 | 結果 |
|---|---|---|---|
| s-F1 | 單reviewer | 把判不適用的入口集合改成連 risk_accepted 也算,跑 t_secev_s69_not_applicable_conditional | HIT:修前照綠;修後新增的 ③' 翻紅 |
| s-F2 | 單reviewer | 讀計劃第 751 行核可鏈逐筆驗證步驟 | HIT:漏寫 null 不比上限與回溯撤銷;已補 |
| a-F1 | 架構對齊 | 讀 _secapr_entry_status 與 _secapr_verify 尾端回溯迴圈 | HIT:兩處各判一次 signer in revoked;修後收成 _secapr_signer_revoked 一支,docstring 寫明兩道 |
| a-F2 | 架構對齊 | grep _sec_no_expiry 位置與前綴 | HIT:放在常數群中間、前綴不屬任何一族;修後改名 _secev_expiry_null_ok、移到核可型別常數之後 |

## 處置

全部折入,沒有放行、沒有駁回。
