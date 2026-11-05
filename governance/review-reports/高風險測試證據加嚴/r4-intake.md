# r4 收貨紀錄

## 派審前:借用函式前提核對(跑滿回顧 avoid 的第二條,2026-11-04)

派一個 sonnet 代理只讀、逐一打開計劃第一批說要借用的約 30 支既有函式,列出寫死的前提並對照計劃。它列出 8 件計劃沒處理或只處理一部分、照字面實作會判錯或跑不起來的,派審前直接修進計劃(不算本輪發現):

| # | 前提 | 修進計劃的地方 |
|---|---|---|
| p1 | `_push_mainlines` 要遠端名與被推 ref,推送前檢查現在拿不到 | 第 2 點:`--push-check` 加 `--push-remote`、`--pushed-ref`,掛鉤傳入;分岔點用 `_push_range_start`(遠端舊值當全零),沒傳就跳過 |
| p2 | 修正關卡的樹準備是行內碼、出錯 return 2,樹內設定用該版 | 第 4 點:抽出後回傳狀態由呼叫端決定;兩棵都用推送版設定 |
| p3 | `_run_bound_tests` 沒有逾時、環境、子程序登記參數,串行不收子程序 | 第 5 點:加三個選填參數,串行也登記 |
| p4 | `_spec_gate_run_clauses` 一條多支時任一非綠蓋過綠;`_spec_gate_twoway_static` 前綴寫死「風險低」 | 第 5 點:判定逐支、自寫回原因代碼;兩支既有函式加選填前綴參數 |
| p5 | `_plan_first_commit` 回提交編號不是日期、沿 HEAD 找 | 第 6 點:取日期、加起點參數、淺複製只看 created;天花板七 |
| p6 | 讀推送版文字要去 BOM、門判定吃筆記物件 | 第 3 點:`_note_text_at_rev` 加組筆記物件;條款綁定對推送版那棵判 |
| p7 | `_h2_section_lines` 丟掉 `#` 行與圍欄,清單相鄰不等於行號相連;`_out_clean` 會壓換行、截 4000 字 | 第 7 點:回傳行號、用行號判連續;第 8 點:逐格清理 |
| p8 | `_gov_vc_gate_events` 讀工作目錄的帳,未提交的簽核也算 | 第 9 點:讀推送版裡的治理帳;讀不到就擋 |

驗收條款 S4、S6、S22 跟著改字。

## 席位收貨

四席報告從逐字稿存,四份全數錨定。編號:正確性 1–12 記 c1–c12、邊界 1–12 記 b1–b12、整合 1–15 記 i1–i15、架構對齊依出現順序 1–12 記 a1–a12(a1 開關形狀、a2 擋下事件 hard、a3 簽核逾時旋鈕、a4 參數穿透與預算、a5 讀推送版治理帳第三種讀法、a6 推送版計劃筆記物件、a7 逐支判定不借既有真值表、a8 分岔點已有 `_rg_fork_point`、a9 `_h2_section_lines` 本來就回行號、a10 借 `_spec_gate_twoway_static` 的兩處細節、a11 樹準備抽出的差異、a12 改檔清單解析器)。

## 世界查證(Enzo 2026-11-04 新定:同類 major 連兩輪、準備換形狀時先查方向)

r3、r4 同一類(基準重播接上推送前流程的接縫)連兩輪有 major。查了「fail-to-pass check GitHub Actions pull_request base branch merge-base」「pre-push hook vs CI pull request check tradeoffs」:
- devops-cli 的 `ci fail-to-pass` 在 pull_request 事件跑(https://github.com/dan-petty/devops-cli/pull/1596);PRProof 提供 GitHub Actions 整合(https://github.com/pedronav1310/prproof)。
- 社群共識:CI 才是最終依據、昂貴檢查放 CI、推送前掛鉤當方便;有推送前掛鉤跑好幾分鐘結果每次都被跳過的實例(https://github.com/uutils/shadow/issues/231、https://dev.to/tildalice/pre-commit-hooks-vs-ci-3-cases-to-skip-local-checks-2o5h)。
- GitHub Actions 在 PR 上有 base 提交可拿來當分岔點(NixOS 的工作流程,https://tangled.org/tjh.dev/nixpkgs/tree/master/.github/workflows)。
方向:對,但要換位置。Enzo 裁「換位置到 PR 檢查(推薦)」。

## 依根因分組與去向

| 組 | 根因 | 發現 | 去向 |
|---|---|---|---|
| G1 | 放在推送前帶來的接縫(掛鉤與 lumos 版本錯開、範圍增量或累計、直推主線、標籤與空樹、插入點被提早 return 跳過、多批合併、掛鉤重查指令) | c1 c3 c6 c7 b3 b7 i1 i2 i4 i6 i14 a8 | 折:整類拿掉——改成獨立指令 `lumos pr-evidence --base --head`,CI 的 pull_request 事件呼叫,推送前掛鉤不動;只重播這次改到的測試檔裡的測試(d7) |
| G2 | 判定與失效方向(對照組在編譯型語言必不綠、平台根不存在丟例外、工具例外變擋、環境變數與預算、證實不留帳、兩棵同缺被 gitignore 的檔、擋下事件 hard) | c5 c10 c12 b1 b2 i3 a2 | 折:唯一會擋的是「新行為測試在舊程式上就綠」,其他記成判不了不擋;整支包一層例外即放行;環境變數壞值用預設、不設總預算;加 `base-replay-proven` 事件;擋下事件 hard |
| G3 | 借用既有函式的細節(`_spec_gate_twoway_static` 沿 HEAD、改檔清單解析、`_spec_gate_judge_items` 參數穿透、樹準備抽出的差異與既有測試、讀推送版治理帳與組筆記物件要用單一來源、改名刪到正式程式、帳壞行) | c2 c8 b8 b12 i5 i8 i9 i13 a4 a5 a6 a10 a11 a12 | 折:`_spec_gate_twoway_static` 加起點參數;`_nodehome_name_status`;一路加選填參數到 `_kill_run`;樹準備回傳狀態、設定用 head 版覆蓋、照 `fix_check.link_deps`;`_gov_rows_at`(有期限、壞行跳過);`_note_from_text`;舊路徑是測試檔才刪 |
| G4 | 預期值表與簽核(簽核資格看不到推送上下文、全標 keeps 死鎖、外側空格、格長與列數、提示逾時參數與環境變數優先、行號已有) | c4 c11 b9 b10 b11 i10 a3 a9 | 折:簽核資格不看 status;全標 keeps 不要求表;外側格去空白後判空;每格 2000 字、500 列上限;`_waive_origin_tty` 與 `_confirm_tty` 加選填逾時、環境變數優先;只加標題計數參數 |
| G5 | 生效日與開關(淺複製、改名、時區、當天、開關讀哪一版與壞值、開關涵蓋範圍) | c9 b4 b5 i11 a1 | 折:常數取合併日隔天、「不早於」含當天、淺複製只看 created;開關改成 `pr_evidence.gate` 區塊、讀 head 版、head 放寬照分岔點判、壞值當 block、off 含規格閘表格檢查 |
| G6 | 文件與測試清單(更多測試產生器、本 repo CLAUDE.md 與 AGENTS.md 重新注入、templates.md、決策正文、事件原因列舉、殘骸清除時限) | i7 i12 i15 | 折:第 10、11 點補齊;d1 重寫;殘骸時限照實寫 |
| — | 理由不夠長時當成沒寫,沒有提示(b6) | b6 | 放行:當成沒寫的結果是照常重播,不會漏擋;要提示另開 |
| — | 自寫逐支判定,沒借 `_spec_gate_twoway_run_verdict` 的真值表(a7) | a7 | 放行:這裡只有「新行為在舊程式上就綠」一種擋、其餘判不了,跟它「新行為要紅、keeps 要綠、合條款」的真值表不是同一張表;逐支判是為了不被同條款另一支的紅蓋掉 |

51 條:折入 49、放行 2(都是 minor)、0 條重現不到。
