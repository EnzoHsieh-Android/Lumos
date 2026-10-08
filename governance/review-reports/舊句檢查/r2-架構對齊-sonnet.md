severity: minor

## F1 治理帳「沿用既有結果詞」但 skipped-no-base 是新字串
severity: minor
blocking: 否
引句:「gate `drift-check`;kind 用既有結果詞:要處理 0(只列出幾筆都一樣)→ `passed`」
file: `scripts/lumos:25788`
file: `scripts/lumos:7120`
1. 既有 drift-check 沒起點時由 `_note_audit_resolve` 記 kind=`skipped`(25788),沒有任何 `skipped-no-base`;全檔 grep 該字串 0 筆。spec 同一段把它列在「既有結果詞」裡,字面自相矛盾。
2. 不會做錯行為:閘的動作統計用 `startswith("skipped")`(7120)認得,spec 也寫了這點。但「kind 用既有值」的宣稱要改成「kind 用 skipped 開頭的既有家族、新增 skipped-no-base 這個後綴」,或直接沿用 `skipped` 並把區別放 `extra.state=no-base`(spec 的 extra 本來就有 state)。建議後者,少一個新值。
3. 其餘四值 passed/warned/blocked(hard=True)與 nodehome-check 的做法(24638-24640)一致,`extra` 帶 dict 也有先例;`extra.check` 這個鍵全檔沒有別的閘用,但只是新鍵、不是第二種做法,不算違反。

## F2 同一次推送同一個 gate 會落兩筆事件,既有 core 不記 passed
severity: minor
blocking: 否
引句:「有候選名稱的每次 drift check 都記一筆 `m1` 帳(含零筆;沒有起點也記一筆)」
file: `scripts/lumos:28271`
file: `scripts/lumos:28296`
1. 既有 `cmd_drift_check` 沒要處理時直接 `return 0`(28271),不記 passed;有要處理才在 `_drift_report_must` 記一筆 blocked/warned(28296、28299)。也就是「這個 gate 每次推送至多一筆」。
2. 照 spec,`m1` 另外記一筆同 gate 事件:c1–c5 擋下 + `m1` 擋下 → 同一次推送兩筆 blocked(hard);`m1` 零筆也記 passed,其他閘沒有這種「通過也記」的先例(nodehome-check 有 passed,但那是該閘自己一致地每次都記)。「閘的動作」統計(7120 一帶)按事件數算,擋下次數會雙計。
3. spec 用 `extra.check` 區分,但 core 那邊的事件沒有 `extra.check`,消費端要寫「沒有 check 鍵 = 舊的 core」的隱含判讀。建議在計劃寫一句:統計端以 `extra.check` 分流、core 事件視為 check 缺省;或 `m1` 的 blocked 在 core 也 blocked 時併成一筆。此為記帳口徑,不影響閘判定。

## F3 快取淘汰把兩套做法各取一半,但沒點出「~/.cache 下目前沒有清舊檔的先例」
severity: minor
blocking: 否
引句:「每次 `m1` 開跑前刪掉目錄裡 mtime 超過 14 天的檔(照 `_note_audit_work_dir` 清舊檔的做法)」
file: `scripts/lumos:25975`
file: `scripts/lumos:34624`
file: `scripts/lumos:34746`
1. `_note_audit_work_dir` 清的是專案內 `_NOTE_AUDIT_WORK_DIR`(帶 .gitignore、只掃 `*.md`),不是 ~/.cache;而 ~/.cache/lumos 下的既有快取(dispatch-lens 的 `_lens_cache_read` 33130 附近、bound-filter 34746 附近)都只在讀取時比 mtime(TTL),從不刪檔。所以 spec 這條是把「TTL 用 mtime、讀不更新」(bound-filter)與「開跑前 unlink 舊檔」(note_audit)拼起來,~/.cache 下第一個會刪檔的快取。方向合理、不算第二種做法,但引用的既有做法只對得上一半。
2. 刪檔前的信任順序 spec 已寫(過 `_trusted_private_dir` 才碰),與 `_trusted_private_dir` docstring「不過關一律不信、不碰(不擋、不寫、不刪)」一致;無問題。
3. 14 天在既有碼是常數(`_FILTER_PROBE_TTL = 14 * 86400`,34624),`_note_audit_work_dir` 則是內嵌魔術數。spec 該指名一個常數(例:`_DRIFT_M1_DEFS_TTL`),不要再內嵌第三份 `14 * 86400`。

## F4 寫入配方會出現第三份手抄,且沒提檔案層的 uid/權限檢查
severity: minor
blocking: 否
引句:「每剖完一支就寫(同目錄 `mkstemp` 唯一暫存名、chmod 0600、`os.replace`,照 `_lens_cache_write`)」
file: `scripts/lumos:33142`
file: `scripts/lumos:34772`
file: `scripts/lumos:33130`
1. `_lens_cache_write` 把 `".cache","lumos","dispatch-lens"` 寫死在函式內(33150、33152),無法直接給 drift-defs 用;bound-filter 那邊(34772)則是手抄同一套 mkdir+trusted 檢查再用 `_write_lf`。spec 說「照」它,實作時等於第三份手抄。此檔註解多次寫過「別再各自漂」(33475 一帶、bound-filter 註解),同一個漂移在這裡再開一處。建議計劃寫明:把 `_lens_cache_write` 抽成收目錄段落參數的共用函式(dispatch-lens 呼叫端不變),或明說接受第三份並釘一條一致性測試。
2. 既有兩個讀取端除了目錄檢查,還逐檔驗 `st_uid == getuid` 且無 group/other 寫位(33130 附近、34752 附近)。spec 只寫「讀寫兩端都過 `_trusted_private_dir`」。目錄 0700 且是自己的時,檔案層檢查多半冗餘,但既有兩處都做了,spec 沒寫就會被實作者省略,造成第二種讀法。這份快取決定名稱「還在」與否,spec 自己也說被改動等於繞過,建議寫進去。
3. 不影響判定行為。

## F5 程式檔範圍的排除清單:docs/、governance/ 是字面重列,而既有常數就叫 `_DELGUARD_PROSE_DIRS`
severity: minor
blocking: 否
引句:「路徑開頭是 `docs/`、`governance/`;開頭或任何 `/` 之後出現 `node_modules/`」
file: `scripts/lumos:29206`
file: `scripts/lumos:29245`
1. spec 引用了 `_DELGUARD_EXCLUDE_DIRS`、`_DELGUARD_EXCLUDE_LOCKFILES`,卻對 docs/、governance/ 用字面寫,沒點名同一處的 `_DELGUARD_PROSE_DIRS`(29206,值正好是 governance/、docs/,語意是「只認 repo 根」,與 spec 一致)。實作若照字面抄清單就是第三份(delguard、參考實作 `_excluded`、m1)。
2. 排除判斷本身在 delguard 是巢狀函式內的運算式(29245-29252)、無法直接呼叫;參考實作 `_excluded` 也是自己組。所以 m1 需要一支自己的小述詞是合理的,但應該在述詞裡引用三個既有常數,而不是字面重列,並補一條「與 delguard 的排除語意一致」的釘住測試(delguard 那段註解已說明 pre-commit 那份與它語意刻意不同,漂移風險是真的)。
3. 另外 spec 排除 `.md` 而 delguard 是另靠 vault/.md 判斷(29240 一帶),兩者在 spec 的範圍句裡合併成一條,實作時要留意 `.md` 不在常數裡。行為結果與驗收數字不受影響(spec 說 P4r3 已量)。

## F6 副檔名清單改用 `_nodehome_code_kind` 後,與參考實作差在大小寫與清單成員,計劃沒明寫
severity: minor
blocking: 否
引句:「其他程式檔 = `_nodehome_code_kind` 回 ext(副檔名在既有程式檔清單裡)或沒副檔名、首行是 `#!`」
file: `scripts/lumos:23603`
file: `scripts/lumos:23387`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:535`
1. `_nodehome_code_kind` 大小寫敏感(23609),`_NODEHOME_CODE_EXTS`(23387)沒有 .json/.toml/.yml 等;參考實作 `TEXT_EXTS` 含它們並且 `.lower()`(535)。spec 前文已說重跑數字逐筆相同,所以驗收不受影響,但新的「其他程式檔」語意(如 `foo.PY`、`x.yml` 被當非程式檔)與參考實作已不同,〈做法〉沒寫這個差異也沒寫理由。這是合理的沿用既有模組(不引第二份清單),只差一句話。
2. `_NODEHOME_CODE_EXTS` 上方註解說該清單是「第五份副本」並由 `t_code_exts_lists_agree` 釘一致;m1 直接呼叫 `_nodehome_code_kind` 不新增副本,與那條紀律相容,無問題。

## 逐項對照(你點名的檢查點)
- 快取位置 `~/.cache/lumos/drift-defs/` 與 `_mkdir_trusted_under_home` + `_trusted_private_dir` 兩端檢查:與 dispatch-lens(33150)、bound-filter(34752、34772)一致,無第二種做法(細節見 F3、F4)。
- 表態取聯集 vs c2/c3:spec 已寫理由(「c2/c3 綁的是當時連著哪些已收尾計劃…m1 的名稱一旦為這一句原文表態過就不會變」),`m1` 不進 `_DRIFT_BOUND_KINDS`(26258)、另開分支,與 `_drift_split_acked`(27404)的既有分流形狀一致;既有 else 分支(`keys.add`)會把 m1 當「任何表態即已表態」,所以另開分支是必要的,spec 已寫。`_drift_load_acks`(27385)以 `_DRIFT_KINDS` 濾未知種類、其餘欄位原樣通過,`names` 欄可存活;舊版遇 m1 行被濾掉,與 spec 的相容宣稱相符。已讀,無 finding。
- 名稱「還在不在」:沿用 `_drift_py_names`(擴參數)、`_drift_py_def_re`(26816)、`_DriftNames` 的先篩做法;不共用 `_DriftProbeTree`(26943)的理由(語料不同、要整份定義集合才能進快取)寫得清楚,且該類別逐檔懶讀的設計確實不適合。改 ASCII 切詞的理由(`\w+` 含中文)與 `_DriftNames` 的 26919 實作相符。已讀,無 finding。
- 不放進 `_drift_check_core`、另開判定函式:與 cmd_drift_check(28236)組裝方式相容,理由(考試與歷史重放共用)成立。已讀,無 finding。
- `_DRIFT_SCAN_KINDS` 子集常數照 `_DRIFT_FIX_KINDS`(26257)先例,無問題。

最高等級:minor;blocking 共 0 條
