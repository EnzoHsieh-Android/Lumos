severity: major

# r6 彙整(處置載體)

每條的嚴重度與引句逐字取自原席報告(r6-<席>.md);重現、根因組與修法見 r6-intake.md。

## Finding COR6-01

severity: minor
blocking: 否
引句:「if replace and not os.access(path.parent, os.W_OK | os.X_OK):」

- 出處席:正確性6-sonnet
- 根因組:G-PRE
- 去向:折入(見 r6-intake.md)

## Finding COR6-02

severity: minor
blocking: 否
引句:「if old is not None and (stat.S_ISCHR(old.st_mode) or stat.S_ISFIFO(old.st_mode)):」

- 出處席:正確性6-sonnet
- 根因組:G-FIFO
- 去向:折入(見 r6-intake.md)

## Finding CON6-01

severity: major
blocking: 是
引句:「fd = os.open(path, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0))」

- 出處席:併發資源6-sonnet
- 根因組:G-FIFO
- 去向:折入(見 r6-intake.md)

## Finding CON6-02

severity: minor
blocking: 否
引句:「if replace and not os.access(path.parent, os.W_OK | os.X_OK):」

- 出處席:併發資源6-sonnet
- 根因組:G-PRE
- 去向:折入(見 r6-intake.md)

## Finding BND6-01

severity: minor
blocking: 否
引句:「fd = os.open(path, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0))」

- 出處席:邊界6-sonnet
- 根因組:G-FIFO
- 去向:折入(見 r6-intake.md)

## Finding BND6-02

severity: minor
blocking: 否
引句:「if replace and not os.access(path.parent, os.W_OK | os.X_OK):」

- 出處席:邊界6-sonnet
- 根因組:G-PRE
- 去向:折入(見 r6-intake.md)

## Finding CTR6-01

severity: minor
blocking: 否
引句:「hist_fd = os.open(a.history, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o666)」

- 出處席:合約圖譜6-sonnet
- 根因組:G-HISTSWAP
- 去向:折入(見 r6-intake.md)

## Finding CTR6-02

severity: minor
blocking: 否
引句:「from scenario_probe import _atomic_write_bytes  # 原子寫入同樣只留探針那一份」

- 出處席:合約圖譜6-sonnet
- 根因組:G-IMPORT
- 去向:折入(見 r6-intake.md)

## Finding CTR6-03

severity: minor
blocking: 否
引句:「raw = str(x).replace("\r", " ").replace("\n", " ").replace("\\", "\\\\")」

- 出處席:合約圖譜6-sonnet
- 根因組:G-MD
- 去向:折入(見 r6-intake.md)

## Finding CTR6-04

severity: minor
blocking: 否
引句:「problem = target and _output_target_problem(target, replace=replace)」

- 出處席:合約圖譜6-sonnet
- 根因組:G-PRE
- 去向:折入(見 r6-intake.md)

## Finding PLT6-01

severity: minor
blocking: 否
引句:「fd = os.open(path, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0))」

- 出處席:平台終端6-sonnet
- 根因組:G-FIFO
- 去向:折入(見 r6-intake.md)

## Finding PLT6-02

severity: minor
blocking: 否
引句:「if replace and not os.access(path.parent, os.W_OK | os.X_OK):」

- 出處席:平台終端6-sonnet
- 根因組:G-PRE
- 去向:折入(見 r6-intake.md)

## Finding PLT6-03

severity: minor
blocking: 否
引句:「check("既有唯讀檔照舊拒絕寫入且內容不變", refused and ro.read_text() == "keep")」

- 出處席:平台終端6-sonnet
- 根因組:G-ROOT
- 去向:折入(見 r6-intake.md)

## Finding ARCH6-01

severity: major
blocking: 是
引句:「mode = 0o666 & ~umask」

- 出處席:架構對齊6-sonnet
- 根因組:G-UMASK
- 去向:折入(見 r6-intake.md)

## Finding ARCH6-02

severity: minor
blocking: 否
引句:「if old is not None and stat.S_ISREG(old.st_mode) and old.st_uid == os.geteuid():」

- 出處席:架構對齊6-sonnet
- 根因組:G-OWNER
- 去向:折入(見 r6-intake.md)

## Finding ARCH6-03

severity: minor
blocking: 否
引句:「with patch.object(mod.os, "geteuid", return_value=wide.stat().st_uid + 1):」

- 出處席:架構對齊6-sonnet
- 根因組:G-TESTPATCH
- 去向:折入(見 r6-intake.md)

## Finding ARCH6-04

severity: minor
blocking: 否
引句:「from scenario_probe import _atomic_write_bytes  # 原子寫入同樣只留探針那一份」

- 出處席:架構對齊6-sonnet
- 根因組:G-IMPORT
- 去向:折入(見 r6-intake.md)

## Finding SEC6-01

severity: minor
blocking: 否
引句:「既有目標是裝置或 FIFO」

- 出處席:資安-sonnet
- 根因組:G-FIFO
- 去向:折入(見 r6-intake.md)

## Finding SEC6-02

severity: minor
blocking: 否
引句:「if old is not None and stat.S_ISREG(old.st_mode) and old.st_uid == os.geteuid():」

- 出處席:資安-sonnet
- 根因組:G-OWNER
- 去向:折入(見 r6-intake.md)

共 19 條,全數折入,無放行、無駁回。
