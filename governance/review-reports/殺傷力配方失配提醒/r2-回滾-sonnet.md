severity: major

# r2 回滾與相容席(sonnet)

## F1 新增 kill-rm 子指令會踩到兩條既有測試,實務隱患「既有測試」一節沒列
severity: major
blocking: 是
引句:「kill-add 只多印一行、不擋,既有 `t_guard_kill`、`t_guard_kill_rc_precedence`、`t_guard_kill_log_new_fields` 用失配或逃逸配方宣告的 8 處照舊能寫;沒有逐字比對 kill-add 標準錯誤的既有測試(回滾席查過)。」
file: `scripts/test_lumos.py:28370`
1. 該節對既有測試的相容宣稱只查了「kill-add 輸出」,漏掉「加一支 guard 子指令」本身會動到的釘。實測 `lumos guard -h` 目前的 choices 是 `{list,scaffold,plan,settle,abandon,required,bind,audit,trace,kill-add,kill}`,而 `scripts/test_lumos.py:28370` 的 S6-3 子斷言(在 `t_slim_skill_reference_scan_assertions` 區段內)逐字釘這串;新增 `kill-rm` 子解析器後這條必紅(該處註解寫「加子指令時照實更新這一行」)。
2. `scripts/test_lumos.py:8181` 起的測試要求每個二層子指令的 `--help` 第一段都有「什麼時候用:」,資料來源是 `scripts/lumos` 的 `HELP_WHEN` 表(約 39645 行,已有 `kill-add`、`kill` 兩列)。kill-rm 沒補 `HELP_WHEN` 一列這條也會紅。
3. 照 spec 字面實作(落點只列 Systems/guard-kill、skill 指令表、`--file` 字串)不會有人去改這兩處,第一次跑 `-k` 子集就紅,而且 spec 還白紙黑字寫「既有測試照舊」。折法:在〈實務隱患·既有測試〉與〈落點〉明列「要同步更新 test_lumos.py 的 guard choices 釘(28370)與 `HELP_WHEN` 加 `kill-rm`」,並把這兩條納入實作要跑的測試子集(`-k slim_skill_reference`、`-k help_when` 一類)。
4. 另外 `scripts/lumos` 的 subparser 順序決定 choices 字串;spec 沒說 kill-rm 排在 kill-add 與 kill 之間或之後,更新釘時要跟著寫對。

## F2 配方身分用的「節點」字串形式沒指定,P2 印出的短身分可能跟 kill-rm 算的對不上
severity: minor
blocking: 否
引句:「配方身分**:用既有 `_kill_recipe_key(節點、invariant、file、old)` 算,印出時取前 12 個字元當短身分;kill-rm 收短身分(見做法 4)。」
file: `scripts/lumos:12955`
1. kill-add 與 kill-log 都用 `str(rel)`(帶資料夾與 .md 的相對路徑,如 `Systems/Limit.md`)當 node 算身分(12955、13334 行);doctor 其他段落的事件與顯示常用 `n.stem`。spec 沒指定 P2 與 kill-rm 該用哪一種;若 P2 用 stem 算,印出的「可直接貼的修法」會讓 kill-rm 對到零條。S6 測 kill-rm、S3 測 P2 各測各的,不會互相驗身分。放行理由:實作者照既有 `rel` 走即可,且測試貼修法指令一跑就現形;建議實作時加一條「P2 印的短身分餵給 kill-rm 能對到」的斷言。

## 其餘各節
- 原子寫入與 frontmatter 單行 JSON:kill-rm 沿用 `atomic_write_verify`(其 check 回呼要自己寫成「該配方不在了、標記狀態符合」,spec 說「同 kill-add 的寫法」已足夠):已讀,無 finding。
- 背書計算 `_backing_note_recipes` 與 kill-log:只認筆記現有配方,kill-rm 後舊紀錄自然略過;rm 再同鍵重加時,舊紀錄靠 head_sha 有效版本判斷(筆記非簿記檔)收掉:已讀,無 finding。
- guard list `[kill✓]`:來自 KEY 行有無 `[kill:recipes]`(`classify_invariants`);kill-rm 拿標記與此一致;lint 沒有反向孤兒標記檢查(查過 scripts/lumos 無對應碼):已讀,無 finding。
- `check-p2` 閘名:`t_gov_stats_gate_drift` 掃字面 `"gate": "check-p2"` 要在 `_KNOWN_GATES`,spec 已登記;revert 後帳裡殘留的 check-p2 事件在 gov 統計仍會被列出、不出錯:已讀,無 finding。
- `--file` 說明字串:全 repo 無測試或文件逐字釘「相對配方平台 root」(僅 `scripts/lumos:40131`):已讀,無 finding。
- P2 段標題標籤:`_section_of(out,"P")` 找 `[P]` 不會誤中 `[P2]`:已讀,無 finding。

最高等級:major;blocking 共 1 條
