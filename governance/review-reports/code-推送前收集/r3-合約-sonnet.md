severity: minor

整體判斷:這批的主要修正都對得上程式和測試,我沒找到 blocker 或 major。我在 `prepush-collect` 工作樹重跑了 `t_prepush_cl_reason_table_matches_lumos`、`t_code_loop_keep_going_pass_sites_keep_blocks`、`t_prepush_test_logs_inside_tmp`,全綠;`anchor verify` 與 `lint` 也都過。我另外在 scratchpad 的複本上做了三個翻紅實驗:
- 拿掉主殼的 HUP 陷阱:S10 的測試翻紅。
- 把 `if _stop:` 改成 `if True:`、`if _stop or True:`、`if not _stop:` 或 `if _stop is not None:`:S13 的原始碼守衛翻紅。
- 拿掉子殼的 HUP 陷阱:測試仍全綠(見 finding 3)。

驗證過的重點:
- ref 名字元的說法:本機 git 2.39.2 的 `git check-ref-format` 接受 U+0085、U+2028、U+2029,拒絕 0x0c 與 0x1c,和新文字一致。
- S13 新寫法:緊接 `if <變數>:`、且回傳該變數,與守衛的 AST 判準逐點對得上。
- S18:有綁定測試,`spec-trace` 顯示綁了,18 條裡 12 條綁了、6 條懸空,懸空的 6 條(S5、S8、S9、S11、S16、S17)都是第二批預演條款。
- 輸出契約拿掉 `summary`:計劃、`bound-tests-gate`、`pitfalls-code-loop`、`scripts/lumos`、測試五處一致,`_CODELOOP_BLOCK_KIND_REASONS` 已無殘留,測試 ⑥ 也釘住 `blocks` 每筆只有 `reason_kind` 與 `reason` 兩個鍵。

severity: minor
blocking: 否 — 只是說明文字不一致,不影響行為
引句:「ref 名照 git 規則不含控制字元」
問題:計劃〈做法〉1 沒改的那句仍說 ref 名不含控制字元。這批在 `bound-tests-gate` 新寫的是 git 允許 U+0085(C1 控制字元)、U+2028、U+2029。兩處對「控制字元」的意思不同,後來的人會以為 ref 名一定乾淨。
具體失敗情境:讀計劃的人據此以為不必防 ref 名帶換行類字元,而 `str.splitlines` 實際會在這些字元斷行;所以計劃那句要收窄成「不含 ASCII 控制字元(0x00–0x1f、0x7f)」。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:34` ``(patch 第 9 行的上下文)

severity: minor
blocking: 否 — 只是說明沒跟上,不是行為錯
引句:「2. 先寫第 S1–S17 的紅測試,再改掛鉤與 `scripts/lumos`。」
問題:這批新增 S18 並標成第一批已實作,但實作清單第 2 項仍寫 S1–S17。另外 `pitfalls-code-loop` 的 `_CodeloopKg` 那條 WHY 仍只寫「每個回傳是 `_fin(...)`,或 `hit` 的結果」,漏了新守衛的「緊接在 `if <變數>:` 底下」。原因是這批只改了計劃的 S13,沒改這條。
具體失敗情境:有人照 `pitfalls-code-loop` 的舊說法,寫出無條件的 `return _stop`。帶旗標時 `hit` 回 None,整個判定函式回 None,下游 `.get` 崩;守衛會擋,但文字沒預警。
佐證:``file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:146` ``、``file: `docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:114` ``

severity: minor
blocking: 否 — 子殼的 HUP 陷阱只剩備援作用
引句:「所以子殼(`run_group`)自己接 TERM 與 HUP:收到就把它起的各片收掉再結束」
問題:文件和 PITFALL 的修法都說子殼自己接 HUP,但沒有測試單獨守這件事。我在複本刪掉子殼那行 `trap … HUP`,`t_prepush_interrupt_stops_every_gate` 仍 30 條全綠。原因是只對掛鉤送 HUP 時,主殼陷阱會先對子殼送 TERM,子殼的 TERM 陷阱就把各片收掉了。S10 條款也沒有「掛鉤在閘執行期間收到 HUP」的測試,只有全套測試階段的 ⑨。
具體失敗情境:有人把子殼的 HUP 陷阱當冗餘刪掉,所有測試照綠,條款所說「子殼自己接」就不成立了。這並非現行行為的錯,只是文件宣稱的行為沒有被守住。
佐證:``file: `scripts/hooks/pre-push:815` ``、``file: `scripts/test_lumos.py` ``的 `t_prepush_interrupt_stops_every_gate` ⑨

severity: minor
blocking: 否 — 守衛仍能偵測種類增減與句子被改動
引句:「每種的句子與查不到時的通用句照 _PPC_KIND_SENTENCES / _PPC_KIND_FALLBACK 逐字(計劃與 r1 收貨定稿,不從掛鉤讀)」
問題:`t_prepush_cl_reason_table_matches_lumos` 的 docstring 說句子取自計劃,但計劃〈做法〉5 只給了一句例句(表態那筆)。其餘三句(bound_tests、lint_new、review)圖譜裡沒有任何出處,只存在測試常數與掛鉤兩處。
具體失敗情境:日後想改某句話的人,在圖譜找不到規範,只能同時改掛鉤與測試常數;守衛等於在比兩份同時被人手改的複本。這是變更偵測,不是規範守衛。
佐證:``file: `scripts/test_lumos.py:64611` ``(`_PPC_KIND_SENTENCES`)、``file: `docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:61` ``

最高等級 minor,blocking 0 條。
