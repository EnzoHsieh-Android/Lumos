severity: major

**1. 分層與依賴方向**
輔助函式和筆記的放置位置大致對。`_py314_old_python` 放在 `_py314_sysbin` 和 `_py314_hook_repo` 之間,靠近它唯一的使用者 `t_hooks_block_without_python314`,和 py314 系列輔助函式同區(file: `scripts/test_lumos.py:88335`)。PITFALL 寫進家節點 `Systems/測試執行器.md`,節點的 `about_code` 本來就列了 `scripts/test_lumos.py`。

但這支輔助函式的職責和同檔既有的 `_py314_old_interpreter`(file: `scripts/test_lumos.py:88228`)重疊,下面 A2 詳述。

**2. 命名與寫法**
- 輔助函式名 `_py314_old_python` 的前綴和鄰居一致,但和 `_py314_old_interpreter` 只差一個詞,容易混淆。
- 輔助函式內用 `import glob as _gl, subprocess as _sp, os as _os` 的函式內別名匯入,和鄰居寫法一致(file: `scripts/test_lumos.py:88229`)。
- 子程序恢復 SIGINT 這處,鄰居的寫法是具名函式 `_ppc_sigint_default` 配 `preexec_fn=`(file: `scripts/test_lumos.py:85371`、`scripts/test_lumos.py:31136`、`scripts/test_lumos.py:86195`)。這次改用內嵌 lambda,和鄰居不同。
- PITFALL 行帶了 `[出處:]` `[根因:]` `[test:]` `[修法:]`,鍵齊全,符合 CLAUDE.md 的表。位置上,同檔既有的 SIGINT 那條 PITFALL 把 `[修法:]` 放在 `[test:]` 前面,新行相反。這只是欄位順序,CLAUDE.md 寫明欄位前後都行,不列。

**3. 第二種做法**
有兩處。專案原本就有「SIGINT 恢復預設」的共用寫法,也有「找舊版直譯器」的共用輔助,這次各另起一種。

A1(子程序 SIGINT 恢復)
severity: major
blocking: 否
引句:「                          preexec_fn=lambda: _sig.signal(_sig.SIGINT, _sig.SIG_DFL))」
file: `scripts/test_lumos.py:85371`
同檔已有具名函式 `_ppc_sigint_default`,做的事一模一樣。它的 docstring 還記了「推送前閘分片裡繼承忽略 SIGINT」的出身。三處呼叫(`scripts/test_lumos.py:31136`、`scripts/test_lumos.py:85386`、`scripts/test_lumos.py:86195`)都直接傳這個函式。新程式碼另寫了一個內嵌 lambda,等於同一個問題有兩種寫法。

A2(找舊版 Python)
severity: major
blocking: 否
引句:「def _py314_old_python():」
file: `scripts/test_lumos.py:88228`
同檔已有 `_py314_old_interpreter`,職責是「找一支真的 3.14 以前的直譯器,找不到回 None」,而且已有三處呼叫(`scripts/test_lumos.py:88249`、`scripts/test_lumos.py:88580`、`scripts/test_lumos.py:88892`)。新函式回傳契約相同,只是候選路徑清單更長,再加上 hostedtoolcache 和 Framework 的 glob。做法上等於多了一個平行的版本探測器。比較自然的結構是擴充既有函式的候選清單,而不是新增第二支。我不確定既有函式的候選清單是否刻意收窄,所以 A2 的判定帶 ⚠。

A3(測試內的註解與提示字串)
severity: minor
blocking: 否
引句:「        print("  (沒驗到①:這台機器找不到低於 3.14 的 python)")」
file: `scripts/test_lumos.py:88249`
鄰居 `t_lumos_old_python_reexec_or_explain` 的「沒驗到」訊息用「3.14 以前的直譯器」的措辭。新訊息改成「低於 3.14 的 python」,用詞不一致,但結構相同。

不對齊共 3 條,其中 major 2 條
