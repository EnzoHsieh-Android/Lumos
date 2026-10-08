severity: blocker

# 第 3 輪通才席報告(code-only-test-tag-not-write-back)

審查方式:全份 diff 逐 hunk 讀過,用 test_lumos.py 的夾具 `_nh_tag_repo` 在臨時目錄(`tempfile.mkdtemp`)造專案,repo 本身沒動。每條重現都實跑兩道檢查:`home check --diff A..B` 與 `note-shape --diff A..B`。實驗腳本在 scratchpad 的 x1.py。

## F1:真測試名前面接一段英文說明加一個點,整段被當成真測試名,兩道檢查都過

severity: blocker
blocking: 是。判準:把程式改動的說明寫進不是家的筆記而不被擋,正是這個案子要守的底線,而且是第 1、2 輪同一類「英文句子包成 [test:]」的繞法,這輪只是換個形狀。
file: `scripts/lumos:14564`(`_KILL_METHOD_OK_RE` 的第二個分支 `^[\w .]+$` 容許空白與點)
file: `scripts/lumos:43481`(`real = method in mset or ("." in method and method.rsplit(".", 1)[-1] in mset)`:只要最後一個點之後是真測試名就判 real,點前面的任何字都不看)
引句:「_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")」
引句:「if j is None or j(nm)[0] != "yes":」

失敗場景:新增的 [test:] 名稱要「指得到真測試」,但判定把「任意文字.真測試名」(Class.Method 寫法)當成指得到。值的字元白名單同時放行空白與 `.`,所以一段不含逗號的英文說明,最後接 `.test_alive`,就同時過了值判準與真測試判定。說明可以到 200 字,不必新增任何測試,也不必說明剛好是測試名,比〈天花板〉1 寫的「剛好寫成一個真的測試名」嚴重得多:天花板假設攻擊者得有一支名字是句子的測試,這裡任何既有的真測試都能當尾巴。

最小重現(夾具 `_nh_tag_repo`,B 的合約行原本只有 `[test:test_alive]`,同一個提交改 `src/a.py`、B 的摘要加一個綁定):
- 新增綁定值:`From now on the retry count is three and every failure is logged with the request id and the cache is dropped on save.test_alive`
- 寫在合約行(`KEY:★INVARIANT★ b 不變 [test:test_alive] [test:<上面那串>]`):`home check --diff` rc=0、`note-shape --diff` rc=0 且無輸出。
- 同一串單獨成行寫在正文:`home check --diff` rc=0、`note-shape` rc=0。
- 對照:同樣位置改寫成 `[test:a now retries three times]`(沒有 `.test_alive` 尾巴)→ `home check` rc=1 點名 Systems/B,是正確被擋。
- 兩道檢查都過的原因:第二道 note-shape 也走 `_classify_test_refs`,同樣把這串判 real,沒有獨立把關。

修法方向(查證過的事實,不是建議的措辭):值要先 fullmatch 識別字或 `識別字(.識別字)*`(不含空白)再進真測試判定;空白只准出現在 Jest 風格句子測試名那一支,且那一支要求整串逐字出現在測試索引裡,不走 `rsplit(".")` 取尾。

## F2:[test-gone:] 的 @ 後面整段是自由文字,只要上一版綁著同名 [test:]

severity: major
blocking: 是。判準:同 F1,不被擋的前提是上一版綁過那個名稱,但那是舊筆記常態,攻擊者只需要挑一個本來就綁著的名稱。
file: `scripts/lumos:29730`(`_test_names_of` 對 test-gone 做 `nm.split("@", 1)[0]`,@ 後面整段丟掉不核對)
引句:「新的 [test-gone:] 名稱要是上一版就綁著的 [test:](只認「測試刪了、」」

失敗場景:名稱切掉 @ 之後只剩 `test_drop`,符合「上一版綁過」;@ 後面的內容沒有任何格式要求(不必是提交編號),值判準的字元白名單又含 `@`、空白,於是整段英文說明躲進去。

最小重現(`_nh_tag_repo`,上一版 B 合約行 `[test:test_drop]`,同一個提交改 `src/a.py`、把測試檔裡的 test_drop 改名成 test_zzz、B 改成 `[test-gone:test_drop@<上面那串 114 字英文>]`):`home check --diff` rc=0、`note-shape --diff` rc=0 無輸出。對照 `[test-gone:test_drop@abc1234]` 同樣 rc=0(合法寫法),所以 @ 後面是不是提交編號完全沒人看。
備註:要先有上一版的 `[test:同名]` 才能用,所以每個名稱只能用一次;但一個筆記可以先綁一堆真測試名(單獨成行的綁定本來就被豁免),之後逐個轉成 test-gone 帶說明。

## 已試、被擋住或屬天花板的路徑

- 在同一個提交新增一支名字是 snake_case 句子的測試再綁它(`test_cache_dropped_on_every_save_so_stale_reads_cannot_happen`):兩道都過(rc=0)。屬〈天花板〉1(說明寫成真的測試名),F1 修掉之後這條仍在,不重報。
- 英文句子直接當名稱、反引號英文句子、新寫沒綁過的 test-gone:`home check` rc=1,擋得住(夾具既有 ①②③④⑤ 與我的對照組)。
- test-gone 對應的測試其實還在(沒刪):note-shape 只給提醒(rc=0,說「測試還在」);這條不是新問題,模式預設是 warn,屬既有行為。
- 把綁定從一篇搬到另一篇:接收方的新名稱要自己指得到真測試,搬進去的內容就是真測試名,沒有額外新洞(F1 的尾巴手法除外)。
- 新筆記(上一版為 None)或 sig_t 不同:`_nodehome_tag_only_change` 直接回 False,沒找到繞法。

總結:全份最高等級 blocker
