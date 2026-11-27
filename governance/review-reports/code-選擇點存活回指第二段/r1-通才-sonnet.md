severity: major

這份改動有一個會直接當掉的缺口:`situation-rule --point` 碰到新行狀態 `exhausted` 會 KeyError。另有兩條 minor。其餘我追過的路徑沒找到問題。

**追過沒問題的部分**
- `_choice_pick` 不帶 skip 時挑到的跟原本相同。
- `_choice_compute`、`_choice_file_points`、`_choice_push_read` 加參數後的所有呼叫者,參數都傳到了。
- `_KillPrep.run` 在 compile 與 cov 都沒開時,行為跟第一段一樣。
- `_secev_junit_facts` 與 `test_quality.junit` 的空殼判定,跟被刪掉的 `_choice_merge_ghost_suite` 等價,只差一點:根外的 `skipped` 元素現在算非空殼,這點可忽略。
- `_TEST_QUALITY_BUNDLE_DIGESTS` 裡 `test_quality.py` 的雜湊跟實際檔案一致(`75c4ac79…`)。
- `_GOV_FIELD_TYPES` 新鍵(`killed`、`compile`、`blob` 等)沒有撞到既有欄位。
- 第一段測試改帶 `--cov-audit 0`,抽查預設開的路徑另有 `t_choice_cov_audit` 蓋住。
- 我在複製目錄把推送閘 `_choice_compute(... skip=skip)` 的 skip 拿掉:`t_choice_compile_batch` 的「推送閘不擋沒有可用壞法的行」斷言轉紅,推送閘的 skip 有測試護著。

**finding 1**
severity: major
blocking: 是
`scripts/lumos:81636-81638`(`_situation_rule_point_target`);`situation-rule --point <檔>:<行>` 指到 `exhausted` 的行(候選都編不過、帳上 blob 沒變)會當掉。
場景:`_choice_kill_scan` 現在會把跳過集合算進去,於是回傳的行可能是 `status == "exhausted"`。但該處的錯誤字典只有 `None`、`arid`、`none`、`not_unique` 四個鍵,取 `["exhausted"]` 直接 KeyError,人看到 traceback 而不是「沒有可用壞法」的提示,計劃沒動。這條路的 `_CHOICE_STATUS_TEXT` 已加 `exhausted`,但這個字典漏改。
最小重現(猴子補丁 `_choice_kill_scan` 回一行 `status=exhausted`,呼叫 `_situation_rule_point_target(None, "a.kt:3", None, None)`):已當場重現,輸出 `KeyError: 'exhausted'`。
測試缺口:`t_choice_compile_batch` 只驗到 `situation-rule` 挑同一個候選,沒走 `exhausted` 的分支。
引句:「        ent["status"] = "exhausted"」

**finding 2**
severity: minor
blocking: 否
`scripts/lumos:80350` 附近(`_CHOICE_COV_BLOCK_COMMENT_RE`);區塊註解的正規式不分行註解。
場景:檔首有 `// 見 src/main/*` 這類行註解時,`/*` 被當成區塊註解開頭,一路蓋空到檔尾,`package` 被吃掉。實測 `_choice_cov_pkg_of("// 見 src/main/*\npackage com.example.app\n…")` 回 `''`,拿掉 `/*` 就回 `'com/example/app'`。
影響:掃主程式套件與壞法行用同一支函式,兩邊同錯,只會讓覆蓋判成不明、方向是多跑,不會誤判存活。
引句:「_CHOICE_COV_BLOCK_COMMENT_RE = re.compile(r"/\*.*?(?:\*/|\Z)", re.S)」

**finding 3**
severity: minor
blocking: 否
`scripts/lumos`,`audit_done` 的 `killed = verdict == "killed"`。
場景:抽到的 none 行照跑全部測試後是 `no_result`(逾時、編不過、基準不綠),`killed` 為 False、`wrong` 為 False,記成「一致」,`_resolve` 就把其餘 deferred 的 none 行照覆蓋記存活(via cov)。一次沒有結論的抽查被當成覆蓋判斷的佐證。
建議:`no_result` 時不算抽查完成,或不放行 deferred 的行;計劃條款有沒有規定這點我沒去核。
引句:「        killed = verdict == "killed"」

**圖譜鏡頭**
- 這次沒附固定席節點,我沒有逐篇核對筆記內容。
- 這包也改了 `_choice_cov_src_pkgs`、`_CHOICE_COV_SRC_HEAD`、`_CHOICE_COV_BLOCK_COMMENT_RE` 這些套件掃描,屬於第一段放行後的實測補修,不在審查主題上,我沒有單獨審。
- `Systems/guard-kill.md` 與 `規格閘.md` 的職責描述已隨 diff 更新,看起來一致。

**清理**
我的臨時目錄 `/private/tmp/lumos-seat-work/code-選擇點存活回指第二段/r1-通才-sonnet` 已刪。`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 下有一份拿掉 skip 的紅燈跑法可能留下的 `gctl-run-*` 現場,同目錄下有很多別人的,我認不出哪份是我的,所以沒動。

總結:最高等級是 major(`situation-rule --point` 碰到 `exhausted` 行會 KeyError,已重現);另有 2 條 minor。
