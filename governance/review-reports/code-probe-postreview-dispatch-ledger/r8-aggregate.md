severity: minor

# r8 彙整(處置載體)

每條的嚴重度與引句逐字取自原席報告(r8-<席>.md);重現、處置與放行理由見 r8-intake.md。

## Finding COR8-01

severity: minor
blocking: 否
引句:「sample = "\u202e\ufeff\U000e0001\u3000\u00a0x"」

- 出處席:正確性8-sonnet
- 去向:折入(G-CATS)

## Finding COR8-02

severity: minor
blocking: 否
引句:「return f"\\u{ord(ch):04x}" if unicodedata.category(ch) in _SPECIAL_CATS else ch」

- 出處席:正確性8-sonnet
- 去向:折入(G-NOTE)

## Finding CON8-01

severity: minor
blocking: 否
引句:「這裡不為一組常數載入整支,改由測試核對兩邊寫法一致(t_probe_boundary_fourth_round_report_and_provenance)。」

- 出處席:併發資源8-sonnet
- 去向:折入(G-CATS)

## Finding CON8-02

severity: minor
blocking: 否
引句:「raise FileExistsError(errno.EEXIST, "連續 100 次都撞到既有的暫存檔名", str(path.parent))」

- 出處席:併發資源8-sonnet
- 去向:折入(G-CAP)

## Finding CON8-03

severity: minor
blocking: 否
引句:「規則由第七輪收斂，見下一條。證據 [[Verification/持久用量帳第六輪審查修補驗證]]。」

- 出處席:併發資源8-sonnet
- 去向:折入(G-NOTE)

## Finding CON8-04

severity: minor
blocking: 否
引句:「且換行與空白類仍會折成空白」

- 出處席:併發資源8-sonnet
- 去向:折入(G-NOTE)

## Finding BND8-01

severity: minor
blocking: 否
引句:「單檔 CLI,這裡不為一組常數載入整支,改由測試核對兩邊寫法一致(t_probe_boundary_fourth_round_report_and_provenance)。」

- 出處席:邊界8-sonnet
- 去向:折入(G-CATS)

## Finding BND8-02

severity: minor
blocking: 否
引句:「raw = str(x).replace("\r", " ").replace("\n", " ")」

- 出處席:邊界8-sonnet
- 去向:折入(G-NOTE)

## Finding CTR8-01

severity: minor
blocking: 否
引句:「改由測試核對兩邊寫法一致(t_probe_boundary_fourth_round_report_and_provenance)。」

- 出處席:合約圖譜8-sonnet
- 去向:折入(G-CATS)

## Finding CTR8-02

severity: minor
blocking: 否
引句:「報表裡的外部文字只把控制、格式（雙向覆寫、零寬）、行段分隔、代理這幾類字元寫成看得見的 `\uXXXX`」

- 出處席:合約圖譜8-sonnet
- 去向:折入(G-NOTE)

## Finding CTR8-03

severity: minor
blocking: 否
引句:「不像主程式清理注入內容的 `_esc_clean` 那樣換成空白」

- 出處席:合約圖譜8-sonnet
- 去向:折入(G-NOTE)

## Finding PLT8-01

severity: minor
blocking: 否
引句:「check("沒有控制終端時 --out /dev/tty 開跑前就擋下", "PRE_TTY True" in out, out)」

- 出處席:平台程序8-sonnet
- 去向:放行(理由見 r8-intake.md)

## Finding PLT8-02

severity: minor
blocking: 否
引句:「check("終端讀得慢時大量輸出照樣寫完", pty_err is None and len(got) >= 300_000, (pty_err, len(got)))」

- 出處席:平台程序8-sonnet
- 去向:放行(理由見 r8-intake.md)

## Finding ARCH8-01

severity: minor
blocking: 否
引句:「_SPECIAL_CATS = frozenset(("Cc", "Cf", "Zl", "Zp", "Cs"))」

- 出處席:架構對齊8-sonnet
- 去向:折入(G-CATS)

## Finding ARCH8-02

severity: minor
blocking: 否
引句:「暫時借 SIGALRM 抓卡住的呼叫;結束時把測試執行器原本的逾時鬧鐘還回去」

- 出處席:架構對齊8-sonnet
- 去向:放行(理由見 r8-intake.md)

## Finding ARCH8-03

severity: minor
blocking: 否
引句:「raise FileExistsError(errno.EEXIST, "連續 100 次都撞到既有的暫存檔名", str(path.parent))」

- 出處席:架構對齊8-sonnet
- 去向:折入(G-NOTE)

## Finding ARCH8-04

severity: minor
blocking: 否
引句:「_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)」

- 出處席:架構對齊8-sonnet
- 去向:放行(理由見 r8-intake.md)

## Finding SEC8-01

severity: minor
blocking: 否
引句:「hist_fd = os.open(a.history, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NONBLOCK」

- 出處席:資安-sonnet
- 去向:放行(理由見 r8-intake.md)

共 18 條:折入 13、放行 5、駁回 0。
