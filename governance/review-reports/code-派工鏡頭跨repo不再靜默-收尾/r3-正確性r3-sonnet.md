severity: minor

我看到「lumos 自動附加」段,共列 8 篇有內容的節點(pitfalls-code-loop、lumos-cli-read、lumos-cli-lifecycle、測試假綠形態、reversibility-governance-ledger、guard-kill、loop-convergence-recording、design-loop),另有 21 篇超出上限只列名。

固定席必答(依根因分組):
- lumos-cli-read、lumos-cli-lifecycle、guard-kill、測試假綠形態、design-loop 這幾條合約:這次修補只動 `codex_s1_lens_arm_claim` 的武裝範圍與計劃筆記一段。search 排除 superseded、re-inject sentinel、guard kill 的 rc 與 JSON 純度、處置閘第五步,都沒有碰到。不破壞。
- 測試假綠形態「還原翻紅釘要有前置斷言」:本案還原翻紅是真的。修前版跑該測試會在 `armed/.../meta.json` 處丟出 EXCEPTION,修後綠。前置斷言「arm 2 席 rc0 且印席數」也在。成立。
- pitfalls-code-loop、reversibility-governance-ledger、loop-convergence-recording 這三條是風險類,沒有可綁的合約行。本次修補不牽涉。

## F1 測試頭部註解與新註解互相矛盾
severity: minor
blocking: 否
引句:「其餘三次用 <upstream>..<upstream> 這個空 diff——一樣過 base」
佐證:file: `scripts/test_lumos.py:39670-39677`(f177602e)
失敗場景:`t_codex_s1_lens_arm_claim` 的「★便宜範圍★」大段註解仍寫「其餘三次用空 diff、實測 1.4 秒」。緊接著新增的註解卻說空範圍不能武裝了,改用 `cheap = rng`,並說「一樣便宜」。實際計時是 35.3 秒(修前 12 秒左右)。下一個讀者會同時看到兩套說法,而且「1.4 秒、空 diff」已經是假的。
歸因:有證據的修復回歸。舊註解是修前就有的,修補只在後面追加,沒有改掉舊段。
查證命令:
- `grep -n "空 diff" scripts/test_lumos.py`:修前 dfb79d27 與修後 f177602e 都命中同一段舊註解。
- 修後 `python3.14 scripts/test_lumos.py -k codex_s1_lens_arm_claim`:`35.3s ... 餘裕 5x`。

## 已驗主張(正向,有證據)
1. **原問題修好。**
   - 修前 dfb79d27 在我的臨時 clone 跑 `-k codex_s1_lens_arm_claim`:EXCEPTION,找不到 `armed/b0456.../meta.json`。
   - 修後 f177602e:12 項斷言全綠。
   - 前置:臨時 clone 沒有本機 `main`,測試會 skip。我建了 `main`(指到 ac7a8444,upstream 設為 origin/main)才跑得起來。
2. **各段斷言意圖不變。**
   - TTL 過期、disarm/status 的剩席數、5 個並發認領 3 席(席次 1,2,3 不重複)、hook SubagentStart 的 LUMOS-LENS 首行,都照舊通過。
   - 並發段不受重算影響:`cmd_dispatch_lens_claim` 只讀 meta 與 token,不重算鏡頭,所以 NO_CACHE 與真實範圍不會讓並發互相干擾。
   - 重算只發生在 `--arm`,共 5 次(2 席、1 席、3 席、3 席、1 席)。
3. **耗時有餘裕。** 單支 35.3 秒,對 180 秒上限約 5 倍餘裕。就算機器慢 3 倍也約 106 秒。計劃筆記寫的「12 秒變 35 秒」與實測相符。
4. **產品端空範圍行為沒變。** `scripts/lumos:45636` 仍有 `empty_range` 且回 rc2。
5. **別處沒有依賴「空範圍可武裝」。**
   - grep `--arm`:測試裡只有 `rng` 與 `cheap`。`t_codex_s1_r1_fixes` 本來就用 rng。
   - 手冊與掛鉤文字裡的 `--arm <base>..HEAD` 在正常情況下 HEAD 不等於 base。
   - 其餘空範圍寫法(`HEAD..HEAD`)都是在驗 empty_range 本身。
6. **相關測試全綠。** `-k lens` 全跑 327 passed、0 failed。

## 未驗範圍
- Codex 編排者手動 `--arm` 遇到空範圍時,只有 stderr 一行「擋下:範圍 X 是空的(起點等於終點)」,手冊沒有對應說明。我沒找到失敗場景,所以不列 finding。
- 真實 pre-push 環境(`Lumos/main` upstream、本機多出很多提交)我沒有重現。
- 並發段在機器忙時的席次穩定性,我只在閒置機器上跑過。

總結:這次修補確實讓那支測試重新通過,各段驗的東西都沒變,產品端的空範圍擋法也沒動;唯一的毛病是測試檔裡舊註解還在說「空範圍、1.4 秒」,跟新改法矛盾。
