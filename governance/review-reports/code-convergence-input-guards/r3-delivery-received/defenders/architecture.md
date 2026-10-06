severity: major  
裁決: evidence

現象 HIT：

- staged 確實分別讀起點與捕獲索引的 `cfg/skip`；push-range 的 `_nodehome_group_route_tests` 則接受終點的 `cfg/skip`。見 `scripts/lumos:29470`、`scripts/lumos:29516`、`scripts/lumos:30052-30074`。
- 固定 ref 已核對為指定 HEAD `c09d12037d1f0d5a5ce92bd09ccda1ed048a2319`。

現象 MISS：

- 「這是無意產生的第二種來源政策」不成立。正式入口明載：提交前設定取索引，推送前設定取終點提交，見 `scripts/lumos:29989`。
- 圖譜設計也明確指定 push 分組接收「推送終點快照讀出的同份設定與自裝排除清單」，不是後來偶然接錯參數，見 `docs/lumos-toolchain-knowledge/Projects/已宣告測試家的同次寫回_計劃.md:38`。

判準 HIT：

- staged 的逐來源政策有更窄的適用理由：避免刪除測試時用終點設定把起點、終點兩份各自不合法的來源拼成合法證據。測試名稱與說明直接限定這個案例，見 `scripts/test_lumos.py:49686-49687`。

判準 MISS：

- 沒有證據顯示本案要求 push-range 必須採「每個歷史版本自己的設定」。相反，程式入口與計劃均指定 push 以終點設定作政策權威；歷史版本只各自提供檔案清單、模式與 reader。故目前差異屬明確的適用政策，不是新增缺陷。

未判定：

- 「push 是否應改成逐提交設定」仍可另立設計議題，但那是政策變更，不能由本 finding 當成既有需求回歸。
- 指定 own-temp 不存在且沙盒拒絕建立，因此未跑隔離同輸入實驗；沒有借用其他席目錄。
- 閱讀範圍約 1,680 行；有一次範圍誤取 151 行，故不宣稱逐次 150 行 cap 完全成功。repo 未寫入。