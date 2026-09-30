severity: major

# 架構對齊-sonnet 第 2 輪報告

審材:r2-snapshot-code.patch、r2-rebase-rangediff.txt。repo 根為 m1impl(佐證行行號取自該工作樹,scripts/lumos)。

## F1 快取與留痕目錄的信任判準被放寬成只有舊句檢查用的第二套
severity: major
blocking: 是
引句:「+        if st.st_mode & (_stat.S_IWOTH if group_ok else (_stat.S_IWGRP | _stat.S_IWOTH)):」
file: `scripts/lumos:34785`(_trusted_private_dir 本體,docstring 仍寫「檢查四件事,少一件都不算過」「④ group / other 不可寫」,這次沒改 docstring)
file: `scripts/lumos:34450`(_home_cache_write,鄰居 dispatch-lens 走預設嚴格判準)
file: `scripts/lumos:36064`(bound-filter 也走嚴格判準)、`scripts/lumos:15053`(vault-lock 也是)
file: `scripts/lumos:34446`(註解寫「舊句檢查的定義快取共用同一支,不手抄第三份」——但共用的是函式,判準已分成兩種)

1. 既有做法:家目錄底下的私有目錄一律走 `_trusted_private_dir` / `_mkdir_trusted_under_home` 的同一條門檻(group 與 other 都不可寫);該函式 docstring「出身」一節記錄了上一次「兩邊各自漂」的事故,家規是單一來源、不放寬。
2. 這次修正:為了 umask 002 機器上目錄被建成 0775,加了 `group_ok` 旗標,只給 drift-defs 與 drift-m1 兩個目錄開放 group 可寫。且不只新建的層:`_trusted_private_dir` 對整條相對路徑的每一層都套 group_ok,所以 `~/.cache`、`~/.cache/lumos` 已經是 0775(別的工具建的)時也放行。
3. 結果是同一台機器上兩套標準並存。最小重現(暫存 HOME,`~/.cache` 與 `~/.cache/lumos` 設 0775):
   `m._mkdir_trusted_under_home(".cache","lumos","bound-filter")` → False
   `m._mkdir_trusted_under_home(".cache","lumos","drift-defs",group_ok=True)` → True
   輸出:`strict: False group_ok: True`。鄰居(bound-filter、dispatch-lens、vault-lock)在這種機器上快取整個靜默關掉,舊句檢查的照開。
4. 同一個缺陷家族沒掃完:patch 自己承認的病因是「umask 002 建出 0775 被自己的檢查判不可信」,但 `mode=0o700` 只加在 group_ok 分支(`cur.mkdir(mode=0o700, exist_ok=True) if group_ok else cur.mkdir(exist_ok=True)`),三個鄰居的 mkdir 仍吃 umask,同一個病沒修。要嘛全家改成新建層明給 0700(判準不動),要嘛承認放寬並全家一致;現在是「只有新來的人拿到豁免」。
5. 放寬的方向也跟 docstring 的邊界宣告相反:docstring 說擋的是「不是同一個 uid 的人動目錄」、不過關「不信、不碰」;group_ok 讓 group 成員可寫的 `~/.cache/lumos` 被信任,同群組的別人能換掉 drift-defs 子目錄。快取讀取端另有檔案 owner 與 group/other 不可寫檢查(`_lens_cache_read`,`scripts/lumos:34431`)頂著,所以不是資料污染洞,這裡只報「判準分岔」這件事。

## F2 doctor 開頭提醒用子字串過濾把合併後的提醒再拆開,gate 自己的提醒會被誤吞
severity: minor
blocking: 否
引句:「+    cfg_warns = [w for w in cfg_warns if "old_sentence" not in w]」
file: `scripts/lumos:28448`(_drift_config:把 gate 提醒與 old_sentence 提醒 `warns + osw` 併成一個清單回傳)
file: `scripts/lumos:29545`(doctor 端拆回去)

1. 既有做法:`_drift_config` 的 docstring 自己宣稱「從同一次解析來,不另開第二支讀同一個鍵」,提醒清單是 gate 一種語意;鄰居 `_note_audit_doctor_lines` 同樣只取 `cfg_warns[0]` 直接用。這次合併衝突解法是在呼叫端用文字比對把 old_sentence 的提醒濾掉——第二種做法(靠訊息內容而不是結構分開)。
2. 失敗場景(已跑):`.lumos/config.json` 寫 `{"drift_check":{"gate":"old_sentence"}}`。
   `_drift_config` 回 `('block', ["drift_check.gate 只能是 block/warn/off,你寫的是 'old_sentence',照預設 block"], True, 'warn')`;
   `_drift_gate_doctor_lines(repo)` 回 `[]`——gate 自己的「設定寫錯」提醒被濾掉,doctor 沒講。
3. 輸入很偏(gate 值恰好等於 old_sentence),所以只標 minor;根因是合併靠字串,任何日後含這個字的 gate 提醒都會被吞。

## 逐項對照(判為一致、不報)

- 兜底 `error` 狀態:既有 drift 兄弟閘對判不了一律走「判不了 → block 擋、warn 印」(`_drift_report_must`,`scripts/lumos:28578`),m1 的 `_DRIFT_M1_UNKNOWN` 加 `error` 同一條路。唯一不同的鄰居是 delguard(`scripts/lumos:30563` 內部錯誤 fail-open、帳記 degraded),那是恆 rc0 的 advisory 閘,m1 有 block 模式,照 drift 家族不照 delguard 是對的。`_drift_m1_guarded` 二層 try 之後最後一層「帳也沒記」有印一行,不吞。
- 轉義:`_drift_m1_show` 是 `_nodehome_show`(`scripts/lumos:23681`,drift 內 `scripts/lumos:28186` 也用)加 `_esc_clean`(`scripts/lumos:9783`)的薄包,不是第二套轉義;多的 UnicodeError 退路是防衛,不算分岔。
- 名稱正規化位置:`_drift_m1_name_canon` 放在 m1 區、被 ack 區(`_drift_ack_names_err`、`_drift_m1_split_acked`、`cmd_drift_ack`)呼叫,跟原本 `_DRIFT_M1_NAME_MAX` 與 `_drift_ack_names_err` 的跨區用法同向;`_drift_one_line`、`_drift_placeholder_err` 也是同樣被 ack 區與別區共用,沒有新形式。
- gov 去重鍵加 `check`:讀端有照該處註解的「必須用 .get」慣例;既有作法是 token 欄擔鑑別,這次另開 `check` 一軸,但我給不出會漏或誤折的輸入,不標。
- `range-unavailable` 結果詞:綁定測試閘沿用同一個詞(`scripts/lumos:36236`);gov 端沒有任何地方按這個詞特判(`scripts/lumos:7136` 只認 skipped 前綴),所以「不再被算進被跳過」成立。drift-check 的 c 側起點算不出走 unknown/warned 路(`scripts/lumos:28557`),m1 的 no-base 是另一種情境(沒有起點版可比),兩者不同種,不算不一致。
- `_DriftM1Clauses` 與舊 `_drift_m1_clause_hist` 並存:舊函式在正式流程已無人呼叫,只剩測試當基準(`scripts/test_lumos.py:56977` 逐位置比對兩者);給不出失敗場景,不標。
- 合併的其他衝突解法(`_drift_config` 多回值、預設 gate=block 與 old_sentence=warn 各管各的、`_drift_old_sentence_config(cfg, bad)` 補壞檔分支):跟 `_drift_gate_config` 的形狀對稱,沒有分岔。

## 圖譜鏡頭逐條判定(架構對齊角度,鏡頭檔前 8 篇)

1. lumos-cli-read(search 預設排除 superseded 不排除 stale):不影響。patch 沒碰 search 濾網,只動 drift 檢查、gov 去重鍵、私有目錄判準與 doctor 提醒。
2. bound-tests-gate(固定席合約綁測試逐支真跑,算不出範圍不擋只記帳):不影響。m1 沿用 `range-unavailable` 這個詞只在 drift-check 這道閘寫帳,沒改 bound-tests 的判定或帳;F1 的 `group_ok` 預設 False,bound-filter 那條路行為不變(但見 F1:它與 m1 的判準已分岔)。
3. guard-kill(rc 優先序、--json 純度):不影響。沒碰 guard kill 的 rc 或 stdout。
4. 授權與歸屬(授權檔不進 _VENDORED_TOOLKIT、主程式檔頭 SPDX 與 MIT):不影響。patch 沒動 _VENDORED_TOOLKIT 與 scripts/lumos 檔頭。
5. 測試假綠形態(還原翻紅釘要配前置斷言):不影響。本席只讀 code patch,沒審測試 patch;該合約歸測試鏡頭席。
6. lumos-cli-lifecycle(re-inject 只覆蓋 sentinel 內):不影響。沒碰注入流程。
7. design-loop(處置閘第五步):不影響。沒碰設計審迴圈的閘。
8. pitfalls-code-loop(RISK,無 INVARIANT):不影響。沒改風險分級;`gov` 去重鍵多一軸 `check` 只讓同一 commit 的 drift-check c 類與 m1 兩筆不被折成一筆,不影響 code-loop 事件(它們的 check 為空,鍵行為同前)。

最高等級:major
