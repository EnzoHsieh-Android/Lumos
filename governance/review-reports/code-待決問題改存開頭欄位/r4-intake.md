# code-待決問題改存開頭欄位 r4 收貨與處置(人裁加開的第一輪)

- 審的是第三輪修補:修前 646dc3a8 → 修後 d6bb423f(來源 r4-repair-binding.json、配對案例 r4-behavior-cases.json)。修補差異 r4-repair-review.patch(1042 行)給五席與架構對齊;資安兩席分讀 r4-review-甲.patch(主程式)、r4-review-乙.patch(測試、筆記、技能)。
- 八席同門 sonnet,沒派外家席。全部交回後才一次寫進卷證,從逐字稿原文存檔;正規化與引句全過。
- 臨時目錄:收齊存檔後刪掉 /tmp/lumos-seat-work/code-待決問題改存開頭欄位/(14GB,刪前確認沒有程序開著)。
- 結果:19 條,blocker 1(C1=E1,兩席獨立)、major 2(K1、A1)。使用者裁再加開一輪(cap-decision extra-round,第二次)。

## 重現表(對被審版本 d6bb423f;HIT=編排者重現得出)

| id | 席 | 現象 | 重現 | 結果 | 去向 |
|---|---|---|---|---|---|
| C1 | 正確性 | 清單後面接任何有項目的欄位(工具自己加的 decisions:)就判清單被切斷,合法筆記整份讀不懂 | 程式內 pq_parse:pending_questions 後接 decisions 清單 → 報第 10 行被切斷 | HIT | 折 |
| E1 | 邊界輸入 | 同 C1(lands_in、related、tags、summary 區塊都中) | 同 C1 | HIT | 折 |
| C2 | 正確性 | 筆記檔是指向庫外的符號連結時,寫入被當成沒拿鎖 | 讀碼(realpath 順著連結到庫外) | HIT | 折 |
| G1 | 通才回歸 | 同 C2 | 同 C2 | HIT | 折 |
| C3 | 正確性 | 標籤字元整段放行,可藏看不見的 ASCII 指令 | 讀碼(U+E0020–E007F 全放) | HIT | 折 |
| S1 | 資安-甲 | 同 C3 | 同 C3 | HIT | 折 |
| E2 | 邊界輸入 | 只有放行格式字元的題目文字讀得懂,畫面上空白 | 讀碼(空值判斷沒排除放行字元) | HIT | 折 |
| C4 | 正確性 | 同時寫入測試在負載下偶發紅 | 席位負載下兩次各紅一次、單跑全綠;原因未判定 | HIT | 折(安靜環境重跑並加診斷) |
| N1 | 併發資源 | 寫入篇一行仍寫已撤掉的 _vault_locked | grep | HIT | 折 |
| G2 | 通才回歸 | 同 N1 | 同 N1 | HIT | 折 |
| K1 | 合約圖譜 | S2、S3 條款寫格式字元一律擋,跟放行 emoji 用字元的程式相反 | 讀計劃與程式 | HIT | 折 |
| K2 | 合約圖譜 | t_qfm_r3_folds 綁的條款跟它守的行為對不上 | 讀計劃與測試 | HIT | 折 |
| K3 | 合約圖譜 | guard plan、abandon、kill-add 鎖逾時仍噴追蹤,「一律擋下」說太滿 | 讀分派段(沒接 RuntimeError) | HIT | 折 |
| K4 | 合約圖譜 | 三個新斷言抓不到錯(⑦ CLI 被指令列先拒、⑥ amend 沒走到拿鎖、⑤ 缺兄弟目錄前綴反例) | 讀測試(席位拆道實驗仍綠) | HIT | 折 |
| K5 | 合約圖譜 | 寫入篇第 150 行、情境出題第 6 行過期句 | grep | HIT | 折 |
| A1 | 架構對齊 | _is_commit 另寫一支,專案已有 _lens_full_sha | 讀碼 | HIT | 折 |
| A2 | 架構對齊 | guard bind/audit 分派只接 RuntimeError,鄰居三種一起接 | 讀碼 | HIT | 折 |
| A3 | 架構對齊 | _decision_amend_locked 第一個參數不是 env | 讀碼 | HIT | 折 |
| A4 | 架構對齊 | _pq_cf_ok 字元級例外是新形狀(⚠ 判不準) | 讀碼 | HIT | 折(理由寫明,收窄成只放行旗幟序列) |

refuted-set:none。

regression-set(有兩版證據支持由第三輪修補造成):C1、E1、C2、G1、C3、S1、E2、N1、G2、K1、K2、K4、A1、A2、A3、A4。K3 為原有漏查(三個守衛指令修前也噴追蹤,但「一律」這句是第三輪新寫的);C4 未判定。
