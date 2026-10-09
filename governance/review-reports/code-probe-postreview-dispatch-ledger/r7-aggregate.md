severity: major

# r7 彙整(處置載體)

每條的嚴重度與引句逐字取自原席報告(r7-<席>.md);重現、根因組與修法見 r7-intake.md。

## Finding COR7-01

severity: minor
blocking: 否
引句:「規則跟 _atomic_write_bytes 與歷史檔追加一一對應:取代模式下,字元裝置直接寫、其他非目錄的東西」

- 出處席:正確性7-sonnet
- 根因組:G-CHR
- 去向:折入(見 r7-intake.md)

## Finding COR7-02

severity: minor
blocking: 否
引句:「fd = os.open(path, os.O_WRONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))」

- 出處席:正確性7-sonnet
- 根因組:G-CHR
- 去向:折入(見 r7-intake.md)

## Finding COR7-03

severity: minor
blocking: 否
引句:「標記字元 ⟦ 本身也照寫,原文因此一對一還原得回去,字面反斜線不必加倍」

- 出處席:正確性7-sonnet
- 根因組:G-ESC
- 去向:折入(見 r7-intake.md)

## Finding CON7-01

severity: minor
blocking: 否
引句:「fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o666)」

- 出處席:併發資源7-sonnet
- 根因組:G-TMPMODE
- 去向:折入(見 r7-intake.md)

## Finding CON7-02

severity: minor
blocking: 否
引句:「if stat.S_ISCHR(st.st_mode):」

- 出處席:併發資源7-sonnet
- 根因組:G-CHR
- 去向:折入(見 r7-intake.md)

## Finding CON7-03

severity: minor
blocking: 否
引句:「old_alarm = signal.signal(signal.SIGALRM, _hang); signal.alarm(5)」

- 出處席:併發資源7-sonnet
- 根因組:G-TESTALARM
- 去向:折入(見 r7-intake.md)

## Finding BND7-01

severity: minor
blocking: 否
引句:「os.fchmod(tmp.fileno(), keep_mode)」

- 出處席:邊界7-sonnet
- 根因組:G-TMPMODE
- 去向:折入(見 r7-intake.md)

## Finding BND7-02

severity: minor
blocking: 否
引句:「規則跟 _atomic_write_bytes 與歷史檔追加一一對應:取代模式下,字元裝置直接寫、其他非目錄的東西」

- 出處席:邊界7-sonnet
- 根因組:G-CHR
- 去向:折入(見 r7-intake.md)

## Finding BND7-03

severity: minor
blocking: 否
引句:「# 不可列印字元寫成 ⟦U+XXXX⟧;標記字元 ⟦ 本身也照寫,原文因此一對一還原得回去,字面反斜線不必加倍」

- 出處席:邊界7-sonnet
- 根因組:G-ESC
- 去向:折入(見 r7-intake.md)

## Finding BND7-04

severity: minor
blocking: 否
引句:「# 跑的期間被換成連結或 FIFO 時報錯,不跟過去也不卡住」

- 出處席:邊界7-sonnet
- 根因組:G-HIST
- 去向:折入(見 r7-intake.md)

## Finding CTR7-01

severity: minor
blocking: 否
引句:「if not stat.S_ISCHR(os.fstat(fd).st_mode):」

- 出處席:合約圖譜7-sonnet
- 根因組:G-CHR
- 去向:折入(見 r7-intake.md)

## Finding CTR7-02

severity: minor
blocking: 否
引句:「在有控制終端的開發機上走不到這條路」

- 出處席:合約圖譜7-sonnet
- 根因組:G-NOTE
- 去向:折入(見 r7-intake.md)

## Finding CTR7-03

severity: minor
blocking: 否
引句:「check("原子寫入不碰整個程序的 umask"」

- 出處席:合約圖譜7-sonnet
- 根因組:G-TESTALARM
- 去向:折入(見 r7-intake.md)

## Finding CTR7-04

severity: minor
blocking: 否
引句:「跑的期間被換成連結或 FIFO 時報錯,不跟過去也不卡住」

- 出處席:合約圖譜7-sonnet
- 根因組:G-HIST
- 去向:折入(見 r7-intake.md)

## Finding PLT7-01

severity: minor
blocking: 否
引句:「fd = os.open(path, os.O_WRONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))」

- 出處席:平台程序7-sonnet
- 根因組:G-CHR
- 去向:折入(見 r7-intake.md)

## Finding PLT7-02

severity: minor
blocking: 否
引句:「規則跟 _atomic_write_bytes 與歷史檔追加一一對應:取代模式下,字元裝置直接寫、其他非目錄的東西」

- 出處席:平台程序7-sonnet
- 根因組:G-CHR
- 去向:折入(見 r7-intake.md)

## Finding PLT7-03

severity: minor
blocking: 否
引句:「old_alarm = signal.signal(signal.SIGALRM, _hang); signal.alarm(5)」

- 出處席:平台程序7-sonnet
- 根因組:G-TESTALARM
- 去向:折入(見 r7-intake.md)

## Finding ARCH7-01

severity: major
blocking: 是
引句:「return f"⟦U+{ord(ch):04X}⟧"」

- 出處席:架構對齊7-sonnet
- 根因組:G-ESC
- 去向:折入(見 r7-intake.md)

## Finding ARCH7-02

severity: minor
blocking: 否
引句:「tmp_path = path.with_name(f".probe-out-{os.getpid()}-{secrets.token_hex(4)}.tmp")」

- 出處席:架構對齊7-sonnet
- 根因組:G-MISC
- 去向:折入(見 r7-intake.md)

## Finding ARCH7-03

severity: minor
blocking: 否
引句:「old.st_uid == _euid() and old.st_nlink == 1 else None)」

- 出處席:架構對齊7-sonnet
- 根因組:G-MISC
- 去向:折入(見 r7-intake.md)

## Finding SEC7-01

severity: minor
blocking: 否
引句:「hist_fd = os.open(a.history, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NONBLOCK」

- 出處席:資安-sonnet
- 根因組:G-HIST
- 去向:折入(見 r7-intake.md)

共 21 條,全數折入,無放行、無駁回。
