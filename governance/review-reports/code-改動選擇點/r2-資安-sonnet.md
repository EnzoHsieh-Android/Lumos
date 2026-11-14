severity: minor

## s1 殘留的 LUMOS_CHOICE_SINCE 讓選擇點推送閘整圈不跑,只印一行、帳上不留痕
severity: minor
blocking: 否 — 要先有殘留的環境變數,平常操作造不出來;而且有印一行提示,與既有的 `LUMOS_HIGH_RISK_EVIDENCE_SINCE`、`LUMOS_KT_SIT_SPEC_SINCE` 同一做法。

- 誰:使用者本人,或照常推送的 AI。shell 裡殘留了 `LUMOS_CHOICE_SINCE=9999-12-31`(例如手動重現測試時 export 過沒清)。
- 從哪:`git push` 觸發 `scripts/hooks/pre-push`,再呼叫 `spec-gate --push-check`,走到 `_choice_push_round`。
- 送什麼:一般的 Kotlin 改動推送。
- 拿到什麼:`_choice_since()` 回 9999-12-31,`since > 今天` 成立,函式直接 `return []`,選擇點那一道整圈不判。stderr 只有一行「選擇點那一道被環境變數關掉」。這一圈沒寫任何治理帳事件,`gov --stats` 與 doctor 事後也看不出來。`.github/workflows/ci.yml` 沒有呼叫 spec-gate 或 choice,CI 也不補這一道。
- 殘留環境變數靠一般操作造不出來:`scripts/test_lumos.py` 只在程序內用 `os.environ.setdefault` 設它,不會漏到 shell,所以我標推論性質的 minor。
- 預期:非刻意殘留時留一筆可查的痕。實際:只有一行終端輸出。
- 若要補,可在被環境變數關掉時用 `_choice_push_event` 記一筆 unverified,讓 `gov --stats` 的「算不出來」計數看得到。

引句:「v = os.environ.get("LUMOS_CHOICE_SINCE", "").strip()」
file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:78453`
歸因:屬於本分支新增的 `_choice_since` 與 `_choice_push_round`,不是修補差異引入的。

## 逐類結論(已看,無)
- ①提示注入:已看,無。`choice-points`、`choice-kill` 與 `_choice_push_show` 印出的原始碼片段、外層宣告、測試失敗摘錄都過 `_kill_esc`。`gov --stats` 的乾節點候選也過 `_kill_esc`。`nores` 原因鍵只取系統固定字串冒號前那段。
- ②讀寫與執行越界:已看,無。
  - 修補把 `_choice_scan` 改成按檔各跑一次 `ast-grep scan`,走參數清單、不開 shell。
  - 設定路徑經 `_lint_wt_cfg_inside` 限在 `configs/ast-grep/` 內,有解 realpath 與 commonpath。
  - 工具經 `_lint_wt_resolve_tool` 解成 PATH 上的絕對路徑,PATH 有空項或相對路徑、落在 repo 內就不跑。
  - 暫存檔名是序號加 `.kt`,不用 repo 路徑;子程序 cwd 是暫存目錄,沒有 `--custom-languages`。
  - `sgconfig.yml` 沒有 customLanguages 或動態函式庫。
  - `check.py --sg` 只在開發者手動跑的自檢裡,沒有被設定檔或 repo 內容間接餵入。
  - pre-push 新增的 `_sg_extra` 用陣列傳參,`$_PP_REMOTE`、`$_rref` 都加了引號。
  - 新測試與新碼裡沒有 `shell=True`、`os.system`、外連下載,也沒有新密鑰或信箱。
  - 帳本與放行檔的寫入沿用既有的原子寫入與不跟符號連結的做法。
  - `cmd_guard_kill` 套壞法前的路徑與符號連結檢查是既有碼,這個分支只改了計數與參數。
- ③非刻意繞過:除 s1 外已看,無。
  - 檔名帶引號、換行這類 git 會加引號的 `.kt`,`_kt_sit_hunks` 會 raise 成算不出來,不會靜默略過。
  - ast-grep 不在、逾時、單檔太大屬於計劃明寫的「只提醒不擋」,不算意外繞過。
  - 新分支首推與合併提交沿用 `_push_range_start` 的既有推導。
- 圖譜鏡頭固定席:這次沒附固定席節點,無可逐條判。

最嚴重:minor;blocking 共 0 條
