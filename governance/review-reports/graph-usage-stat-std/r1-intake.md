# graph-usage-stat-std r1 前掃留痕

preflight-4: ran

- 本迴圈=light graph-usage-stat 出 1 blocker+4 major 後的 ratchet 升級;被審=v2(L-1..L-8 全折後)
- refcheck v2:0 壞引用;pitfalls --check:實務隱患節六類(含 r1 補的讀取穩定性/可攜性)
- 前掃教訓已折:v1 的「已修不實」係 replace 靜默沒中——本輪凍結前逐關鍵詞 assert 過(NFC/ts 前綴比較/值域守衛/中位數/排除自引/std 升級 全在)
- 近案裁定遵循:兩前案裁死派工端強制,本切片讀側純觀測
