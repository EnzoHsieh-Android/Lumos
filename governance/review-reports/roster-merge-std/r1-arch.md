### arch-f1 「復用邏輯但限定當輪」沒指名參數化寫法,留給實作=抄一份改的第二種做法風險
severity: major
引句:「復用 _roster_observe 邏輯但限定當輪 rid」
佐證:file: `scripts/lumos:5021`
佐證:file: `scripts/lumos:3880`
說明:_roster_observe 組 rids 含 dispatch glob 補漏,限定當輪要動函式內部;專案先例=_panel_round_conjuncts 的 quiet= 參數化。條款應寫死「新增參數限定,不另寫」。

### arch-f2 disposal 自動尾端=不受旗標管轄的第二條觸發路徑,--disposal --roster 同帶重複輸出未裁
severity: major
引句:「保留現行為(全輪、四模式可用)」
佐證:file: `scripts/lumos:4707`
佐證:file: `scripts/lumos:4656`
說明:互斥清單沒擋 --roster=同帶合法;入口全輪版+尾端當輪版兩套並存,spec 沒裁誰吃掉誰。

### arch-f3 「全面對齊先例」措辭失實:panel=拒新留舊機械擋,[S2]=原地全留——結構不同件事
severity: minor
引句:「panel 先例有祖父條款→[S2] 全面對齊先例改」
佐證:file: `scripts/lumos:3866`
說明:不加擋對 advisory 是對的,但審計紀錄的援引措辭會讓讀者誤以為 roster 也有新舊分界;正確理由=advisory 不該比照會動 rc 的閘。

## 對齊良好的面
不對 advisory 硬加機械擋的判斷正確;「恆 advisory」同 canary 觀測段慣例;[S3] 三處行號逐一核對命中真實;邊界聲明與改動範圍一致。
