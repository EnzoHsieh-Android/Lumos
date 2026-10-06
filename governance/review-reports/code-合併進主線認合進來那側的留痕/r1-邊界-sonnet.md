severity: major

鏡頭:邊界與可執行。全部在 scratchpad 臨時 repo 實跑(repo 本身未動;突變實驗在 scripts 的複本上做)。
實跑過、沒問題的極端輸入:SHA-256 物件格式 repo 放行正常;範圍寫三個點、起點全零、起點空樹、第二個母是無關歷史的根提交 → 一律擋;起點是短 sha、終點是短 sha 或 HEAD 字樣、起點寫 `<合併提交>^1` → 都能解析並放行;Windows 換行帳本放行;帳本約 55 MB 約 7.5 秒放行;帳本是空檔、第二個母樹裡沒有帳本 → 擋並講原因;同一 head_sha 同時有 passed 與 skipped → 認最後一筆(跟既有「最後一筆」語意一致);第一母鏈邊界精確(紀錄提交落在窗內第 20 個 → 放行,第 21 個 → 擋);--json 的 reason 含中文與分號,輸出仍是合法單行 JSON。

## F1 _git_is_shallow 逾時沒接,判不了時不是「不認」而是崩潰,且表態關被放行
severity: major
blocking: 是 — 設計明寫「判不了一律不認」,實測逾時時 check 噴 traceback、--json 沒有輸出,而表態那一關被 `except Exception` 吞成 fail-open,把本來會擋的合併提交放過去
引句:「_git_is_shallow(repo_root, timeout=max(1.0, deadline - __import__("time").monotonic()))」
file: `scripts/lumos:6018`(_git_is_shallow 只接 OSError,subprocess.TimeoutExpired 直接往上丟)
最小重現:在 PATH 最前面放一支 git 包裝腳本,遇到 `rev-parse --is-shallow-repository` 就 `sleep 23` 再轉交真 git;用測試的 `_mp_feature` + `_mp_merge` 造出可放行的合併提交,再跑 `lumos code-loop check --json --diff <起點>..<合併> --at-sha <合併> --branch main`。實測:耗時 46 秒(表態關一次、審查關再來一次,各吃滿 20 秒)、rc=1、stdout 空、stderr 是 `subprocess.TimeoutExpired: Command '['git', 'rev-parse', '--is-shallow-repository']' timed out after 19.9 seconds` 的 traceback。表態關那次例外被 `_gate_failopen` 記成「表態核對例外」而放行,審查關那次(沒有 try/except 包住)才崩;tier 不是 high 但有適用效能題的合併提交會因此整個放行。另外這一支的逾時用 max(1.0, …) 不受總預算約束,預算已用完時仍多等 1 秒以上。修法方向:merge_side 內自己接 TimeoutExpired 回 (None, 為什麼),或讓 _merge_side_git 也負責這一支。

## F2 測試的「照舊擋」多格只釘措辭,真正的起點條件沒有行為測試
severity: minor
blocking: 否 — 沒有空殼格(五個突變都被抓到),但起點條件實際擋的那個場景沒被任何一條斷言單獨證明
引句:「check("④未審分支擺第一個母(第一個母不是推送範圍起點)→ 照舊擋、講起點", rc == 1」
引句:「check("⑥還原提交把內容退回主線舊版、只有主線舊紀錄 → 照舊擋", rc == 1 and "合進來那一側(" not in (v.get("reason") or "")」
file: `scripts/test_lumos.py`(新增的 t_codeloop_check_merge_side_pass / t_codeloop_check_merge_side_dispositions)
實測突變(複本上改,各跑 -k merge_side):①拿掉 `p1 != start` → 只有 ④ 紅,而且是因為輸出少了「起點」兩字,不是因為放行了(④ 的 evil 分支即使沒有起點條件也會被「第一個母不是第二個母祖先」擋下);t_..._dispositions ③ 整支照綠。②拿掉紀錄要含第一個母 → ⑥ 紅;③帳本改讀 HEAD → ⑨ 紅;④拿掉合併結果只差簿記檔 → ③ 紅;⑤拿掉祖先檢查 → ⑤ 紅(也是措辭釘:實際仍被別的條件擋)。起點條件真正要防的場景(主線上多一個未推未審的高風險提交 U,分支從 U 之後分出再合進來,範圍起點在 U 之前):實測原版 rc=1 擋在表態關,拿掉 `p1 != start` 的版本 rc=0 放行,但現有測試只靠措辭抓到突變,換個措辭就漏。另外 ⑥ ⑧ 只斷言「reason 不含放行字樣」,check 因任何原因崩潰(v={}、reason 空)時照綠,F1 這種崩潰不會被它們發現。建議:加 U 場景一格,並讓 ⑥⑧ 同時斷言 reason_kind 或 blocked 為 True。

## F3 新測試單支 115.7 秒,離 180 秒上限只有約 1.5 倍
severity: minor
blocking: 否 — 目前綠,但慢機器上的 CI 有逾時風險
引句:「def t_codeloop_check_merge_side_pass():」
實測:`python3.14 scripts/test_lumos.py -k merge_side` 跑完 12 passed,慢測排行印出 `115.7s t_codeloop_check_merge_side_pass (餘裕 2x) ⚠ 餘裕不足 3 倍`;dispositions 那支 37.0 秒。每格都重建一個 repo 並真跑 pass/表態指令,九個場景串在同一支函式裡,拆成數支或共用建好的 repo 可降。

圖譜鏡頭逐條判:
- Systems/pitfalls-code-loop.md(家,RISK):直接相關,本 diff 已在該節點寫了脈絡;沒看到與程式矛盾處,F1 屬程式缺口,不是筆記缺口。
- lumos-cli-read.md(INVARIANT search 排除 superseded):不影響,diff 沒碰 search。
- loop-convergence-recording.md(RISK):不影響,沒動帳本寫入端,只多一條讀帳路徑(讀取端已確認工作樹帳本含非 UTF-8 時舊的 `_codeloop_read_from_ledger` 仍會崩潰,這是既有行為、非本 diff 引入,不計入 finding)。
- guard-kill.md(INVARIANT rc 優先序、--json 純淨):不影響 guard kill;但 --json 純淨精神在 F1 崩潰時被 code-loop check 破壞(stdout 空)。
- lumos-cli-lifecycle.md、測試假綠形態.md、design-loop.md:不影響(測試假綠形態的「還原翻紅釘需前置斷言」精神見 F2:⑥⑧ 缺前置斷言證明現場走到被測分支)。
- reversibility-governance-ledger.md、bound-tests-gate.md 等超出上限只列名者:不影響。
- 表態記錄 py-eventloop na:合理,本 diff 沒有 async def。

總結:邊界輸入大多站得住(SHA-256、三個點、根提交、空/缺/大帳本、窗口 20/21 精確),但 _git_is_shallow 逾時沒接導致「判不了」變崩潰並讓表態關 fail-open(F1,major,附實跑重現),測試另有措辭釘與耗時兩個 minor。
