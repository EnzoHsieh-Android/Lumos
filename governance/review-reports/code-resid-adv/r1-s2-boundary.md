# code r1 s2 boundary-sonnet 摘錄
F1 major: bool 是 int 子類,isinstance(int) 守衛擋不住 [true,true,false]→靜默算 67% 假統計(實跑重現)。
F2 major: 同 diff 內另兩個 _estimate 呼叫點(panel 觀測行 3519/K2 obs 3631)無型別守衛→字串 counts 靜默印「估計 0.00+無鑑別力警語」假背書(實跑重現);cluster 3700 同病。
F3 minor: badtype-only 時訊息「不帶 capture_counts;壞型 1 筆」自相矛盾。
Clean: none-only 提前返回一致/kind=second 不可達路徑查證/K2 env pin 確認/既有 27 條實跑綠。
