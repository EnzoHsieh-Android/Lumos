# r3 收貨紀錄(派工前先寫配對案例)

固定版本:修前 44b0044da2eaa72938fe0a97835bf80f55730cf5 → 修後 525d773ac242ce5a8b121fe45be44cd624f0d58e。來源見 r3-repair-binding.json。

## 配對案例(待驗範圍,不是作者判定已修好)

| 組 | 角色 | 待驗行為 | 出處 | 案例 |
|---|---|---|---|---|
| G1 | repair | 沒宣告只有清單時 doctor 照印摘要;git 列出 NFD 檔名時認得清單上的 NFC 寫法 | S9 | t_arch_target_legacy_doctor_lines |
| G1 | preserve | 有宣告時的計數、讀不懂、讀不到、算不出照舊 | S9 | 同一支 |
| G2 | repair | 起點沒清單、分支新增清單時說明行印多了幾行;其中幾支改用分級已算好的目標檔 | S6 | t_arch_target_graduate_check_note 的 L、A2 |
| G2 | preserve | 少行、多行、宣告有改、沒宣告四種說明照舊 | S6 | 同一支的 A、E、B、K |
| G3 | repair | 清單混非字串元素判讀不懂、推送前分級不崩 | S5 | t_arch_target_graduate_same_branch 的 H2 |
| G3 | preserve | 拿掉多餘的警告條件後,宣告有改仍不畢業 | S5 | 同一支的 B |
| G4 | repair | 測試替換內部函式改用 patch.object | 架構對齊 | t_arch_target_legacy_doctor_lines |

修前證據:沒另存,記未判定。修補自己的驗證見 r2-intake.md〈r2 修補自己的驗證〉。

## r3 收貨

- 五席 clean(資安、架構對齊、資源、正確性、邊界);兩條 minor,沒有 major。
- 接手 H1(測試 L 名稱寫修補理由、修前也綠):放行。r2 的改壞實驗「說明行不讀頂端版清單」讓 L 翻紅,L 守的是那個參數;名稱寫它守什麼,不宣稱修前紅。
- 通才 G1(說明行後備分支沒測試):放行。邊界席與正確性席各自查證:分級只在目標檔非空時寫 targets 鍵,畢業的改動檔一定在裡面,正常流程走不到後備分支;改成空字典輸出也不變。
- regression_set=none:兩條都是原有或測試措辭問題,沒有修補改壞原本正確行為的證據。
