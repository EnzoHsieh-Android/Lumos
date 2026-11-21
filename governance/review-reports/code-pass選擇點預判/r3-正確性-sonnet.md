severity: minor

## c1 修補讓 `t_codeloop_pass_choice_skips` 變慢,安全餘裕從 4 倍掉到 2 倍
severity: minor
blocking: 否

引句:「+        _cpc_git(r3, "remote", "remove", "origin")
+        r = _cpc_pass(r3, f3)」

file: `scripts/test_lumos.py`(該測試函式的 S12 新增段,r3 repo 上多跑兩次 `_cpc_pass`)

失敗場景:新增的「沒有遠端」和「兩個遠端」兩案各多跑一次完整 pass 子程序。測試跑的是同一支函式 `t_codeloop_pass_choice_skips`。慢的 CI 機器若比本機再慢約 2.5 倍,就會撞上 180 秒上限而誤紅。工具自己印出 `⚠ 餘裕不足 3 倍`。計劃的代碼審 r1 才把這組測試拆成四支來降低耗時,這次的修補又把它加回去。

歸因:有證據的修復回歸(耗時增加來自修補新增的兩次 pass 呼叫)。

兩版證據:
- 同一個關鍵字 `-k codeloop_pass_choice_skips` 在兩版各跑一次。
- 修前 826ce8451:最慢 50.7s,餘裕 4x,8 項斷言全過。
- 修後 4fa28747:最慢 72.8s,餘裕 2x,帶 ⚠。
- 只各量一次,有機器雜訊的可能,但增加約 22 秒與多兩次呼叫相符。

證據表:
- claim:修補沒有讓測試時間逼近上限。
- input:`python3.14 scripts/test_lumos.py -k codeloop_pass_choice`。
- expected:餘裕至少 3 倍。
- case_source:測試工具自己的耗時摘要。
- before:50.7s(4x)。
- after:72.8s(2x,⚠)。
- comparison:耗時變多,修補造成。

## 已驗的修復與保留行為

**G1 沒有遠端(repair)**
- claim:沒有遠端時放行、印「沒有遠端」、rc 0,且測試守得住。
- input:Kotlin 專案,執行 `remote remove origin` 後跑 pass。
- expected:rc 0,輸出含「沒有遠端,選擇點留給推送前判」。
- case_source:新增的 S12 斷言。
- before:修前測試沒有這一案,把放行改成擋下測試也不會紅(case 為新增)。
- after:測試通過。
- comparison:保護是新增的,未實際變異驗 G1。

**G2 多個遠端都不是 origin(repair)**
- claim:這種情況講判不出哪個遠端,並教 `git config branch.<分支>.remote`,不說「沒有遠端」。
- input:加 `fork`、`upstream` 兩個遠端,沒有 origin,分支沒設上游。
- expected:輸出含「判不出要比對哪個遠端」與 `branch.`,不含「沒有遠端」,rc 0。
- case_source:新增的 S12 斷言。
- before:修前 `if not remote` 一律印「沒有遠端」,所以會誤印;修前版沒另外重跑這個輸入。
- after:測試通過。
- comparison:我把修後版的 `if not n:` 改成 `if True:`(一律印「沒有遠端」,即修前行為)。`-k codeloop_pass_choice_skips` 變成 9 passed、1 failed,S12 兩個遠端那條斷言紅,所以新斷言抓得到這個錯。
- 救法有效:`_lens_default_remote` 讀 `branch.<分支>.remote`,值在遠端清單內就回傳,所以教的救法接得上。這點是讀程式碼確認,沒另外實跑。

**preserve**
- claim:有 origin、設了上游、detached HEAD、非 Kotlin 專案的路徑不變。
- case_source:`-k codeloop_pass_choice` 全跑。
- before/after:26 passed、0 failed(只跑了修後版)。
- comparison:修補只動 `if not remote:` 內部,有 remote 的路徑沒被碰到。
- 未判定:修前版整組 26 項沒跑,只跑了其中的 skips 那支。

**其他確認**
- `_lens_git(rr, "remote")` 失敗回 None 時,`n` 設為 0,走「沒有遠端」分支,沒有例外。
- 本席沒起子程序,也沒動不可逆操作,所有臨時目錄與 worktree 都已清掉。

## 三問回答
1. 原問題修復效果:多遠端誤印「沒有遠端」已修,證據是上面的變異紅。
2. 修補處的相鄰路徑:正常路徑、錯誤路徑(git 失敗)、有 remote 的路徑都沒有壞掉。
3. 新發現 c1 在修前 4x、修後 2x。

## 未驗範圍
- pass 的預判用本機追蹤的遠端分支當舊值,推送前拿到的是遠端實際舊值。兩者可能不同(未 fetch、或推到非預設遠端),但這是設計審已定的範圍,不是這次修補引入的。我沒有找到能讓 pass 放行、推送前反而擋下的具體合理輸入,所以不當 finding 交。
- 本席沒逐 hunk 重查計劃筆記、手冊與 `gov --stats` 的統計改動,那些不在修補差異內。
- 沒有對 G1 放行做變異驗證。

總結:最高嚴重度 minor
