severity: major

**Finding 1**
severity: major
blocking: 是 — 筆記寫的行為跟程式現況不符,而且綁的測試測不到這個落差
引句:「也印成「(名字含不收的字元)」,這是取捨:只影響那一行顯示,內容照讀(計劃照讀、連結節點照附、程式檔照跑 impact)」
問題:這句話(計劃做法 6、Systems/派工鏡頭的 WHY、S32)說白名單外的標點(`&`、`+`、`,`、全形冒號)只影響顯示,連結節點照附。程式不是這樣。會談目錄裡真的存在、但名字帶這些標點的節點,連內容都不讀。
- 連結段和落點段進讀取前,先過 `_lens_spec_name_ok`。節點名不合白名單就只計數、不讀、不附。
- 我實跑:`Systems/Q&A設計`、`Systems/a+b`、`Systems/設計：舊` 都回 False。
- 測試 `t_dispatch_lens_spec_fullwidth_paren_node_attached` 也釘住這個行為:全形冒號節點的 `LR3-COLON-BODY` 不在輸出,只計數「1 篇連結的節點名含不收的字元」。
- 所謂「連結節點照附」,實際只成立在「計劃檔名帶標點、被連結的節點名合規」。S32 綁的 `t_dispatch_lens_spec_punct_name_shown_as_bad_content_read` 只測了這一種。
- `[代價:]` 欄只寫了「來源行對不上 spec-freeze 那行」,沒寫「節點整篇沒附」。這是一個沒承認的代價,也沒有回頭條件。
具體失敗情境:計劃寫 `[[Systems/Q&A規則]]`,這篇節點真的在會談目錄且帶合約行。席位的派工詞裡只有「另有 1 篇連結的節點名含不收的字元」,合約行沒附。讀了這份筆記的人會以為已經附了,也不會去補。
修法方向:把「連結節點照附」限縮成「連結節點名合規時才附」。S32 補一條節點名帶 `&`、`+` 的條款和測試(只計數、不附)。`[代價:]` 補上這一項,並讓 REVISIT 一併涵蓋「合法節點名帶這些標點會整篇漏附」。
佐證:
- file: `scripts/lumos:49226`(`_lens_spec_name_ok`)
- file: `scripts/lumos:49535`(落點段 `if not _lens_spec_name_ok(it)` 就 `continue`)
- file: `scripts/test_lumos.py:44513`(S32 綁的測試只覆蓋計劃檔名與程式檔名)

**Finding 2**
severity: minor
blocking: 否 — 計劃裡一句過時的做法,S35 和 Systems 已寫對
引句:「`{what}` 用 `_clean_field(spec)`,不用範圍專用的 `_SAFE_RANGE_RE`」
問題:計劃做法 8 這句沒有標「被取代」。掛鉤現在的實作是:
- `{what}` 走 `_spec_what`(計劃值)和 `_range_what`(範圍值)。
- `_spec_what` 會先切冒號,檢查冒號前是不是 7 到 64 碼十六進位,再決定顯示。
同一節的「掛鉤不解析值的形狀」也不完全成立。程式註解說只決定顯示,寫法仍由 lumos 判,但計劃本文沒反映。
具體失敗情境:下一個 session 照做法 8 實作或審查,會把 `_clean_field` 當成對的做法。這正是 r4 才修掉的洞(整句指令從說明行進派工詞)。
修法方向:在這一句標明「2026-10-14 r4 起改為 `_spec_what`,見 S35」,並把「不解析形狀」改成「不依形狀分流,只在顯示時切冒號前的十六進位」。
佐證:
- file: `scripts/hooks/claude/dispatch-lens-hook.py:269`
- file: `scripts/hooks/claude/dispatch-lens-hook.py:323`

**Finding 3**
severity: minor
blocking: 否 — 條款說得比測試強,屬於寫法過滿
引句:「本計劃、[[Systems/派工鏡頭]] 與 [[Systems/codex-harness]] 應有該有的守則行(各帶綁定測試)與回頭條件、條款綁這兩輪新加的測試、不留輪次流水帳;拿掉任一項時文件守衛應紅」
問題:S27 比它綁的 `t_lens_repo_notes_r4_clauses_and_limits` 強。
- 測試的變異只做四種:拿掉一條條款行、拿掉 lens 的 REVISIT、加回一句承認句、拿掉 codex 的 `_spec_what` 行。「任一項」沒有逐項證明。例如 S13 的齊全度、做法 5 的「取代」和做法 6 的措辭,都沒有變異。
- 「不留輪次流水帳」只靠三個字面字串判(`代碼審 r1 修正(`、`### 代碼審 r1 修正`、`四個分支`)。本計劃的「審計修正紀錄」r1、r2 兩段和實作紀錄裡「r3 併發席實測」這類輪次敘述,條款字面上算流水帳,守衛卻是綠的。
- 守衛只確認 S25 起的行帶了指定的 `[test:]` 名字,不看條款文字跟測試斷言對不對得上。
具體失敗情境:有人把 S13 的「不帶 `--out`」改回舊寫法,守衛只在字串消失時才紅,語意被改寫成別句就照綠。
修法方向:把 S27 的「任一項」改成實際守的清單,或補齊變異。「不留輪次流水帳」改成「不留 `代碼審 rN 修正(` 這類標題」。
佐證:
- file: `scripts/test_lumos.py:44921`
- file: `scripts/test_lumos.py:44909`(`_lr4_notes_problems`)

**Finding 4**
severity: minor
blocking: 否 — 只是條款少寫,測試比條款嚴
引句:「外面那篇的內容不應進派工詞,只計數。」
問題:S30 綁的 `t_dispatch_lens_spec_vault_dir_symlink_pinned_not_read` 還斷言了兩件條款沒寫的事:說明行要講「圖譜資料夾本身或上層是符號連結」,工作樹寫法要回 `no_knowledge` 並在 stderr 講明符號連結。條款沒寫這兩個行為。
具體失敗情境:有人讀條款後改了說明行措辭,測試紅,但他看不出是哪條規格要求這一句。
修法方向:S30 補這兩個行為,或另開一條。
佐證:
- file: `scripts/test_lumos.py:44700` 附近(`t_dispatch_lens_spec_vault_dir_symlink_pinned_not_read`)

**已讀,無 finding 的部分**
- 條款與綁定:`spec-trace` 35 條款、綁了 35、懸空 0、壞名 0。S25–S35 的 `[test:]` 名字在測試索引裡都找得到。
- 其他條款與測試內容一一對得上:S25(40 碼不存在、附註標籤、替身解回縮寫)、S28(5000 與 5001 邊界、`scan_truncated`/`cands_truncated`)、S29(NFD 存放、NFC/NFD 去重)、S31(整句檔名、單一出口、守衛變異)、S33、S34、S35。S34 的 U+F900 與 U+8C48 我用碼位確認是兩個不同字元,字元集、長度邊界與程式一致。
- S13 的新措辭跟 `SPEC_FREEZE_HINT` 一致。六處手冊與說明字串(五份手冊加 `HELP_WHEN`)由 `t_design_loop_manuals_spec_freeze_old_step_any_placeholder` 守。
- 做法 5 的批次寫法跟 `_spec_commit_present` 一致(`_nodehome_cat_sizes` 加每批 200 個路徑的 `ls-tree`、5000 候選)。也標明了「取代」,不再有「不一次帶多個路徑」。
- 白名單字元集與長度(80、300、不收 U+F900–FAFF、Cn/Co)在計劃、Systems/派工鏡頭、程式三處一致。
- 回頭條件:兩條 `REVISIT:2026-12-15` 都是「日期 加 一句要做什麼」,`lumos lint` 對計劃與派工鏡頭節點都是 0 問題。「無標點整句仍印得出」這個承認有獨立的 REVISIT 行,原句沒有再帶承認。
- `lint Systems/codex-harness` 的兩條 FACT 警告是舊行,不在這次差異裡。
- `governance/anchor-baseline.json` 的 `test_lumos.py` 與掛鉤雜湊,跟 lens-repo 現有檔案的 sha256 一致。

最高等級 major,blocking 1 條。
