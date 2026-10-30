# r2 收貨紀錄(派工前先寫配對案例)

## 配對案例(待驗範圍,不是作者判定已修好)

固定版本:修前 006c398b82f24827804d3a37893d5c64dcc2026c → 修後 e31302e3842333c50f3d3debc92259b71cec4c07。來源見 r2-repair-binding.json。

| 組 | 角色 | 待驗行為 | 出處 | 案例 |
|---|---|---|---|---|
| G1 | repair | 清單讀可信版本(分叉點),修補輪範圍起點有清單也不讀 | 計劃 S5、用語「起點版」 | t_arch_target_graduate_same_branch 的 I |
| G1 | repair | 清單寫 NFD、改動檔是 NFC 仍認得是舊檔;刪掉 NFD 那行就畢業 | 計劃做法 4「轉 NFC」 | 同一支的 J1、J2 |
| G1 | preserve | 刪行畢業、宣告有改不畢業、頂端讀不懂不畢業、整份刪掉全畢業、頂端多行不影響、改名照目標 | 計劃做法 6、S5 | 同一支的 A、B、C、D、E、G |
| G2 | repair | 起點版沒有宣告時,代碼審判定不印清單說明行 | 計劃做法 7「接在既有目標節點行之後」 | t_arch_target_graduate_check_note 的 K |
| G2 | preserve | 有宣告時少行、多行、宣告有改三種說明照印 | S6 | 同一支的 A、E、B |
| G3 | repair | doctor 兩個計數分得開、none 命中算沒被判給、git 失敗說讀不到、列檔失敗寫算不出 | S9 | t_arch_target_legacy_doctor_lines |
| G3 | preserve | 目標架構宣告那幾行 doctor 提醒照舊 | 架構對齊可宣告目標架構_計劃 S7 | t_arch_target_doctor_soft_warnings |
| G4 | repair | 說明行的「其中幾支」只算這次有改動的;畢業判定只剩一份 | S6 | t_arch_target_graduate_check_note 的 A2 |
| G4 | preserve | 推送前分級、兩條派工鏡頭的分流結果不變 | S5、S11 | t_arch_target_graduate_same_branch、t_arch_target_spec_lens_reads_legacy |
| G5 | repair | 畢業測試跑時下降(r1 量 53 秒,修後量 42 秒;剩下的是 A、B、I 六次子程序,守接線) | 資源席 r1 | 量測 |

修前證據:四支新測試在修前版本的結果沒有另存;G1/G3/G4 的 repair 案例修前是否紅,以 r1 席位的改壞實驗為準,編排者沒另跑,記未判定。

## 出處清單(同一規則的每一處)

- 畢業條件:scripts/lumos 的 _arch_legacy_graduation(唯一一份);呼叫者 _arch_legacy_apply、_arch_legacy_check_lines;說法在計劃做法 6、Systems/arch-alignment-lens、06 那一列。
- 清單讀法:_arch_legacy_at;呼叫者 _arch_legacy_graduation、_arch_legacy_doctor_lines。
- 分流接線:pitfalls(_at_targets 那行)、_dispatch_lens_arch_text、_dispatch_lens_spec_arch_text。
- doctor:_arch_target_doctor_lines(唯一一次 ls-files)→ _arch_legacy_doctor_lines;run_doctor 印法。

## 修補自己的驗證

12 種改壞各自讓對應測試翻紅、還原後全綠(條件反過來、清單改讀範圍起點兩處、拿掉 NFC、設計審沒接、其中幾支改成全部、沒宣告也印、doctor 計數對調、不算 none、列檔失敗當空、git 失敗說成讀不懂、頂端多行取消畢業)。修補輪輸出沒另存原始檔,只留在對話紀錄。

## r2 收貨:修補因果核對(收齊後寫)

| finding | 關係 | 證據 |
|---|---|---|
| C1、B3(沒宣告時 doctor 清單摘要沒測試) | 修補新增的路徑缺測試,行為本身正確,不是回歸 | 修前是獨立函式不看宣告;修後併進有早退的函式,早退仍回傳清單行;兩席的改壞實驗只證沒測試守 |
| C2(說明行讀頂端版清單的參數沒測試) | 修補新增的參數缺測試,行為正確 | 修後直接呼叫 need_head=True 回頂端版清單;改壞實驗只證沒測試守 |
| B1(清單元素必須是字串的檢查沒測試) | 原有漏查 | 修前修後該行相同,測試只有 not-a-list 一種輸入 |
| B2(頂端版宣告有警告不畢業那半條件沒測試) | 原有漏查;經查是多餘條件(宣告有警告時規則變空,比規則已涵蓋),改成拿掉 | 讀宣告的函式有任何警告就回空規則 |
| G1(doctor 列檔名轉 NFC 沒測試) | 修補新增的路徑缺測試,行為正確 | 改壞實驗只證沒測試守 |
| R1(說明行重列一次改動檔) | 原有做法,修補搬位置沒改;改用分級已算好的目標檔 | 兩版都有同一行 |
| A1(測試直接賦值替換內部函式) | 修補新增的測試寫法 | 改成 patch.object |

regression_set=none:八條都完成歸因,沒有一條有證據是上一輪修補改壞了原本正確的行為。

## r2 修補自己的驗證

6 種改壞各自讓對應測試翻紅、還原後全綠:拿掉元素檢查、沒宣告不印清單摘要、說明行不讀頂端版清單、doctor 不轉 NFC、其中幾支改成全部、拿掉宣告相同條件。
