severity: minor

## F1 迴圈只接 ValueError/RuntimeError,寫入時的 OSError 仍會中斷整批
severity: minor
blocking: 否
引句:「        except (ValueError, RuntimeError) as ex:」
cmd_set 走原子寫入(暫存、replace),磁碟滿或權限問題會丟 OSError,不在這個 except 內,迴圈仍會中斷、後面幾篇不寫。上一輪要的是「一篇丟例外不影響其他篇」,現在只對兩種例外成立。外層 main 也只接同兩種,OSError 會印堆疊。屬機率極低的邊角,不擋。

驗收結果(臨時副本實跑 `python3.14 scripts/test_lumos.py -k t_updated_sync_nodes`,6 passed):
- 修法①:把迴圈內 try/except 拿掉,⑤紅(EXCEPTION: 測試:寫入失敗);還原後綠。修好了。
  引句:「            print(f"擋下 {rel[:-3]}:{ex}", file=sys.stderr)」
- 修法②:把 `lag = 2` 改成 `lag = 0`,⑥紅;還原後綠。修好了。
  引句:「        except ValueError:      # 形狀像日期但不存在(2026-02-30):當成落後列出,一鍵修會改成今天(代碼審 r2 回歸席 F2)」
- 新問題檢查:在副本造 updated: 2026-02-30 且已提交,實跑 `updated-sync --stale`(非 dry-run),rc=0、該篇真的被改成今天,cmd_set 不因舊值格式失敗;再單篇指定也只印「已是今天」。沒有帶進新問題。

兩條修法都真修好、補的測試拿掉修法即紅,無 blocking;僅一條 minor(OSError 未接)。
