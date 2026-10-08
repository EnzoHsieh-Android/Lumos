severity: minor

## F1 改名進工具自裝檔路徑,能讓被刪的名稱逃過刪除守衛
severity: minor
blocking: 否
引句:「parsed = _delguard_parse_diff(r.stdout, gr_rel, frozenset() if _is_toolchain_repo(root) else _VENDORED_ALL)」
佐證行:file: `scripts/lumos:17750`(_VENDORED_ALL 是精確路徑集合)
佐證行:file: `scripts/lumos:29537` 附近 cmd_delguard_check 對 git diff 帶 `-M`(改名偵測開啟)

1. 輸入:消費專案(沒有 skills/lumos-project-notes/SKILL.md)裡,把 `src/app.py` 用 `git mv` 改名成 `scripts/lumos`(或 `scripts/hooks/pre-commit` 等清單內任一路徑),同時把內容裡的函式(例:compute_secret_thing_0..2)整個刪掉,再 staged 跑刪除守衛。
2. 走到:`git diff --cached -M` 產出 `diff --git a/src/app.py b/scripts/lumos`。`_delguard_path_flags` 只看 b/ 側路徑,`cur in vendored_skip` 成立,`is_excl=True`,該檔所有 `-` 行都不抽 token。
3. 壞在:原本屬於自己程式碼的被刪名稱被當成工具檔的刪除跳過。
4. 重現(在 clone 的臨時目錄跑,呼叫 `_delguard_parse_diff(diff, "docs/kg", _VENDORED_ALL)`):
   plain 刪除 -> tokens 含 compute_secret_thing_0/1/2,vendored_skipped=[]
   改名進 scripts/lumos 並刪掉那些函式 -> tokens=[](沒有 compute_secret_thing_*),vendored_skipped=['scripts/lumos']
5. 影響有限:守衛本來只提醒、不擋,且計劃已明寫「消費專案自己改工具檔就不提醒」為刻意取捨;但這條是「不用改工具檔本身、改名就能繞」的路徑,計劃沒寫到。治理事件 note 會記 vendored-skip=1,事後可查。

## 其他攻擊面判定(無可利用洞,不列 finding)
- c4 預填 lumos set 指令:每一項走 `_drift_sh`(非白名單字元一律 shlex.quote,節點以 - 開頭補 ./),整行再過 `_esc_clean`(控制字元、C1 換成空格)。卷證目錄名只在清單裡印、過 `_esc_clean`,不進可貼指令;範本句只含佔位字與 hex sha。特製目錄名/檔名無法讓貼上的指令多執行任何東西。(_esc_clean 2000 字截斷可能切掉結尾引號,只會讓 shell 等輸入,不執行東西。)
- git 子行程參數:同提交查詢的 sha 來自 `_plan_first_commit`(hex),目錄名不進 git 參數,路徑以 `-z` 讀入;沒有 `-` 開頭路徑被當選項的路徑。
- `--reason`(c3):`_drift_fix_reason_ok` 限單行(splitlines)4 到 200 字,只接在正文最後一行的「;理由:」之後,不進 frontmatter,不能起新行;不會注入欄位。與 c2 同口徑。
- c1 新句子(`_guard_settle_missing_say(say=False)`)只含固定字串,沒有把 rel 帶進 msg,沒有新增未過濾的終端輸出。
- 治理事件 note `vendored-skip=... files=`:檔名只來自 `_VENDORED_ALL` 固定集合,攻擊者不能自訂內容。
- 消費專案自己在清單內路徑(如 scripts/hooks/pre-commit)放真程式,刪除名稱不會提醒:計劃已明列為刻意取捨,不重複報。

## 圖譜鏡頭
- 存量漂移守衛、guard-kill、lumos-cli-write、delguard:本席只看資安面,改動不破壞其合約;delguard 行為變更即 F1 所述取捨。
- bound-tests-gate、授權與歸屬、測試假綠形態、lumos-cli-read、lumos-cli-lifecycle、design-loop 的 INVARIANT:改動不碰授權檔白名單、search 濾網、re-inject、處置閘,判不影響。

最高等級:minor
