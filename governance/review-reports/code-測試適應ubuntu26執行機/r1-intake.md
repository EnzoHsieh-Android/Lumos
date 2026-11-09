# r1 收貨紀錄(code-測試適應ubuntu26執行機,light)

- 一席架構對齊(sonnet)交回後從逐字稿存檔。報 2 條 major、1 條 minor → light 判定失效,照規則升級開 code-測試適應ubuntu26執行機-std(standard)審修正後的版本。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| A1 | 恢復子程序 SIGINT 另寫內嵌 lambda,同檔已有具名函式 _ppc_sigint_default(三處在用,說明寫明就是為分片繼承忽略 SIGINT) | HIT | 折:改呼叫 _ppc_sigint_default |
| A2 | 新寫 _py314_old_python,同檔已有 _py314_old_interpreter(三支測試在用,契約相同) | HIT | 折:刪掉新函式,改呼叫既有的;把既有函式的候選補上 GitHub 執行機預裝的 /opt/hostedtoolcache 3.10 到 3.13,讓另外三支用到它的測試在 Ubuntu 26 也恢復有驗 |
| A3 | 「沒驗到」措辭跟鄰居不同 | HIT | 折:改成「3.14 以前的直譯器」 |

- 根因:修補前沒先在被改的檔搜同類既有函式(記憶「防護工具先找既有」的同一型)。
- 驗證:六支相關測試在一般與父程序忽略 SIGINT 兩種條件都綠;改壞三種:拿掉恢復預設→忽略條件下紅、找舊版改回 3.14→①紅、找不到舊版→綠並印沒驗到。

## 先查世界

- PRIOR-ART:A1——Python 文件寫明 SIGINT 只在父程序沒改過時才轉成 KeyboardInterrupt(https://docs.python.org/3/library/signal.html),所以測 Ctrl-C 的子程序要先裝回預設;專案已有 _ppc_sigint_default,重用。
- PRIOR-ART:A2——GitHub runner-images 的 Ubuntu 26 映像說明列系統 Python 3.14.4、預裝 3.11 到 3.15 於 hostedtoolcache(https://github.com/actions/runner-images 的 ubuntu26/20261101.186 發行說明);擴充既有函式的候選即可。
