severity: clean

已看,無:前兩輪架構席指出的四點,這輪修正都做到、且與 patch 外的既有寫法一致:

1. 標籤只印在段首一行:`_cap_hint_lines` 裡 `P = "  "`(純縮排),只有各段第一行手動接 `"[cap-hint] "` 字面(scripts/lumos:7458、7460、7469 的 `閘:` 行、7480 的 `提示:` 行、7484 的 `熔斷:` 行全用 `P` 不重複標籤)。引句:「標籤只印在段首一行,後面縮排(跟處置閘各段的輸出慣例一樣)」(scripts/lumos:7457 註解,patch 內逐字)。

2. 分輪函式搬到處置閘步驟家族旁:`_disposal_round_groups` 舊址在 `_review_yield_round`(約行 7387)附近、與 `_cap_hint` 系列混在一起;這輪搬到 scripts/lumos:18177,緊鄰 `_gated_seat_rows`(18169)與 `_disposal_security_step`(18199)這組處置閘步驟函式,呼叫端 `_loop_status_disposal`(18425)也在同一區塊,符合「分輪函式在處置閘步驟家族旁」的要求。

3. 不重複定義:用 grep 核對 `_disposal_round_groups`、`_cap_hint_print`、`_cap_hint_lines`、`_cap_hint`、`_gated_seat_rows`、`_disposal_security_step`、`_SEV_ORDER` 在 scripts/lumos 裡各自只有一個 `def`(或一個賦值),没有殘留舊址的第二份定義;patch 呈現的「刪除舊址、新增新址」是搬移不是複製。

4. 裝飾器一支一個:scripts/test_lumos.py 裡新舊測試函式(含新加的 `t_disposal_cap_hint_fail_open`)都只掛一個 `@_cap_real_cutoff`,沒有疊裝飾器,跟既有 16 支同類測試的寫法一致。

另外這輪新加的 `_cap_hint_print`(scripts/lumos:7444)用 `try/except Exception: pass` 吞例外、只印不擋,跟檔內其餘 91 處同款 fail-open 寫法(bare `except Exception:`)一致,不是新引入的風格。`_loop_status_disposal` 兩處呼叫點(scripts/lumos:18695、18705)都已改呼叫 `_cap_hint_print`,沒有殘留直接呼叫 `_cap_hint_lines(_cap_hint(...))` 的舊寫法。

共 0 條。
