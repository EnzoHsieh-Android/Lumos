severity: minor

# 架構對齊審查:summary-line

## 問一:分層與依賴方向
結構對齊。cmd_summary_line 包 `_vault_write_lock` 再進 `_summary_line_locked`,跟 `scripts/lumos:18019`(cmd_set → _cmd_set_locked)同形;讀寫走既有的 `load_raw_for_edit`(`scripts/lumos:17842`)與 `atomic_write_verify`(`scripts/lumos:17893`),找摘要區用既有 `_notelines_regions`、`_ns_summary_logical`,沒有跨層直呼或新依賴。分派段放在 set/append/remove 那一塊之前、自己 return,跟 `cmd_guard_bind`(`scripts/lumos:14539`,在函式內自己 env.find)同一種接法,有前例。
引句:「with _vault_write_lock(env.vault):」

## 問二:命名與錯誤處理
大致對齊(擋下:前綴、rc 2、stderr、ValueError/RuntimeError 轉 擋下)。唯一不一致是節點找不到:見 F1。updated 的更新方式:`scripts/lumos:18715`(supersede)同樣是同一次 atomic 寫裡就地換 updated,所以做法有前例;日期取法 `_dt.datetime.now(_dt.timezone.utc).astimezone().date()` 在 `scripts/lumos:3812`、`scripts/lumos:37604` 有前例(本機日期),對齊。
引句:「print(f"擋下:{ex}", file=sys.stderr)」

## 問三:第二種做法
沒有另寫讀寫或驗證:找摘要行、續行判斷、寫後自驗都重用既有工具;片段比對「多處就擋」是照 `scripts/lumos:14539` cmd_guard_bind 的想法,只多了 --nth,屬功能差異不是第二套機制。取日期見問二,有前例。
引句:「atomic_write_verify(path, new_lines, "summary", check)」

## F1 找不到節點用了 guard bind 的內嵌訊息,沒走 _node_not_found
severity: minor
blocking: 否
set / append / remove 在主程式分派段找不到節點時走 `_node_not_found(env, args.note, write_side=True)`(`scripts/lumos:48355` 起、定義在 `scripts/lumos:12154`):印近名候選、給 lumos search 與 lumos new 的下一步。該函式的 docstring 明講過「複製貼上的內嵌訊息不給近名候選」是被抓過的缺陷。summary-line 抄的是 `scripts/lumos:14539` cmd_guard_bind 的內嵌版本(那邊也沒走 _node_not_found,所以有前例,但屬於較舊、較差的那一種),打錯節點名的人拿不到近名候選。這是訊息品質不一致、結構沒錯;summary-line 是修改既有筆記,不該提「新建」,所以用 write_side=False 版本即可。
引句:「print(f"擋下:圖譜裡找不到叫 {node} 的筆記,先確認名稱或路徑(lumos search <關鍵字> 可以找)", file=sys.stderr)」

不對齊共 1 條,其中 major 0 條
