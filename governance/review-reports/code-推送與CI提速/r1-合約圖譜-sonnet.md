severity: major

核對的版本是 0cdfc7cc。有兩條 major 和三條 minor。計劃的 [S1]–[S3]、[S5] 都有綁定測試沒驗到的項目,[S4] 的測試形同空殼。

## 發現

severity: major
blocking: 是
**[S4] 的 `t_ci_yml_speed_shape` 驗不到「每份耗時真的有印」。**
- 測試只檢查 shards 區段內有沒有子字串 `份耗時`。
- 同一段的註解 `# 每份記起訖,結尾印「第 i 份耗時 N 秒」` 本身就含這個子字串。
- 重現:把 `echo "第 $i 份耗時 ..."` 刪掉、註解留著,`"份耗時" in shards` 仍為 True(輸出 `echo removed; '份耗時' in shards: True`)。
- 此測試沒有前置斷言證明「現場成立」,與 `Systems/測試假綠形態` 的 INVARIANT 精神相反。
- 應該:比對實際的 `echo` 敘述,或比對含 `date +%s` 的那一行。
引句:「+            ( s=$(date +%s); python scripts/test_lumos.py --shard "$i/$SHARD_TOTAL"; rc=$?; echo "第 $i 份耗時 $(( $(date +%s) - s )) 秒"; exit $rc ) > "/tmp/shard-$i.log" 2>&1 &」

severity: major
blocking: 是
**[S1] 的核心規則沒有被 `t_runner_shard_by_duration` 驗到,而且四種變異都存活。**
- 我在 `_shard_by_duration` 分別做了四種變異:權重下限改 0、中位數改 0、拿掉「同總權重比支數」、拿掉「同權重照名字排序」。
- 用測試的輸入直接呼叫,四種的分配結果都跟原版完全相同:`[1,13,13,13]`,有缺表的測試也都是 `[5,5,5,5]`。
- 測試實跑也是 `17 passed, 0 failed`。這一輪的實跑沒檢查變異是否真的套用,套用與否以上面的直接呼叫為準。
- 各項問題:
  - **權重下限 0.05:** 測試 ② 的 `holders >= 3` 在沒有下限時也成立,因為平手比支數也會把 0 秒的測試攤開。
  - **全表中位數:** 測試 ③ 只驗聯集和 `med > 0`,沒驗缺表的測試拿到的是中位數。
  - **同總權重取支數少的、再取編號小的:** 兩項都沒有專門的斷言。
  - **每份印「總支數」:** 條款寫了,測試只比對雜湊,沒驗 `共 N 支`。
引句:「+    check("耗時分片:0 秒的測試不會全擠進同一份(有下限、平手比支數)", len(holders) >= 3, [len(b) for b in zb])」

severity: minor
blocking: 否
**[S3] 寫了「過、紅、逾時、例外都算,跳過的不算」,測試只驗了「過」。**
- `t_test_durations_refresh` 的執行器子跑只選 `t_runner_exitfirst_and_failfirst` 這一支,而且是綠的。
- 紅、`TestTimeout`、`EXCEPTION` 各自記不記、跳過的不記,都沒有測試。
- 把 `if t.__name__ not in SKIPPED_NAMES:` 改成無條件記錄,測試照綠。
- 「只在來源 repo 寫」也沒有反向測試:消費專案不該有 `.lumos/test-durations-run*.json`。
引句:「+        check("執行器跑完把各支秒數寫進 .lumos/test-durations-run.json", "t_runner_exitfirst_and_failfirst" in names, (sorted(p.name for p in after - before), list(names)[:5]))」

severity: minor
blocking: 否
**[S2] 的格式不對情形沒有測全。**
- 條款寫的情形是:不是物件、`tests` 不是物件或是空的、秒數不是非負有限數字。
- 測試的壞表有 6 種,缺的是 `tests` 為非物件(例如 `{"tests": []}`)和 `Infinity`。
- 「帶 `--suite` 的空片照舊算過」在這支測試裡也沒驗,只驗了不帶 `--suite` 的 rc1。
- 程式的判斷本身是對的,只是沒有測試守。
引句:「+        for label, bad in (("不是 JSON", "{nope"), ("不是物件", "[]"), ("tests 是空的", '{"version": 1, "tests": {}}'),」

severity: minor
blocking: 否
**[S5] 只驗了清單成員資格,沒驗「代碼審留痕不失效」。**
- 測試檢查 `"governance/test-durations.json" in m._BOOKKEEPING_FILES`,另外檢查 `pitfalls` 判成 docs。
- 沒有測試跑 `code-loop` 的留痕判定,看只改耗時表的提交是否真的不讓已過的留痕失效。
引句:「+        check("耗時表在簿記檔清單裡(刷新不讓代碼審留痕失效)", "governance/test-durations.json" in m._BOOKKEEPING_FILES, "")」

severity: minor
blocking: 否
**計劃與 `ci.yml` 對不上,紅的那份還會少印耗時。**
- 計劃〈做法〉寫「shards 工作在每一份的日誌開頭與結尾印時間」。`ci.yml` 只在結尾印,開頭沒有印。
- GitHub Actions 的 `run` 預設是 `bash -e`,專案自己的註解也寫著這步是 bash -e。子殼層裡 `python` 失敗時 errexit 會直接結束子殼層,後面的 `rc=$?; echo "第 i 份耗時…"` 不會執行。
- 重現:`bash -e -c 'set -u; ( s=$(date +%s); python3 -c "import sys;sys.exit(1)"; rc=$?; echo "第 1 份耗時…"; exit $rc ); echo outer_rc=$?'` 沒有印任何東西。綠的那份會正常印出。
- 退出碼本身還在,CI 判定不受影響。
- 紅的那份缺耗時行,只影響 RETIRE-IF 的量測。
- 應該:改成 `python …; rc=$?` 前面先 `set +e`,或用 `|| rc=$?`,並補上開頭那行時間,或把計劃的「開頭」兩字拿掉。
引句:「+            # 每份記起訖,結尾印「第 i 份耗時 N 秒」:耗時分片的撤除條件要量每份(推送與CI提速 RETIRE-IF)」

severity: minor
blocking: 否
**`commands/INDEX.md` 夾帶了跟本主題無關的資訊刪除。**
- 本次改動在 guard 列的 `guard list·scaffold·bind·audit·trace·kill-add(--covers、--try)·kill-rm(不帶 --id 列出)·kill(--id)` 把括號內的用法提示全部拿掉。
- 這跟 test-durations 無關,也不在計劃的範圍裡。
- 查 `1b83927e` 的 `INDEX.md` 確認那些括號在原版存在,所以是這次改動帶來的刪除。
- 九類子檔的索引是接手人找指令的依據,少了 `--covers`、`--try`、`--id` 的提示。
- 應該:還原這段括號。
引句:「+| 代碼要推、要過高風險審 | `commands/06-代碼審與推送.md` | pitfalls --diff / loop fix-check / code-loop pass·skip·check / note-audit prepare·record·check·skip(筆記內容審) / note-audit reread-prepare·reread-record·reread-check(推送前回頭重讀) / guard list·scaffold·bind·audit·trace·kill-add·kill-rm·kill / ci-wait」

## 其他核對(判為沒問題或不影響)

- **計劃內部前後說法:**
  - 範圍、做法、條款、回退、實務隱患互相一致。
  - 「不做」清單沒有被程式碼違反。
  - RETIRE-IF 的量測(各台最大最小差)依賴 CI 日誌的耗時行,見上面第六條。
  - `REVISIT:YYYY-MM-DD` 的格式正確。
- **`lumos test-durations refresh` 的行為:**
  - 取檔案時間最新的一筆、保留舊值、讀完刪檔、不在 git 專案或沒有 run 檔回 rc2,這幾項跟〈做法〉一致。
  - 〈做法〉沒寫、程式碼實作的行為:舊表格式不對就從空表開始,新表會整個覆蓋它。這會悄悄丟掉舊值,屬於計劃之外的行為。
- **`Systems/bound-tests-gate` 新加的 WHY 行:**
  - 有 `[出處:]`、`[因:]`、`[不選:]`、`[test:]`,摘要行格式與必有鍵齊全。
  - 內容跟程式一致:沒表輪流分、表壞每份擋、下限 0.05、平手比支數。
  - 它綁的兩支測試的驗證缺口見第一、二條。
- **`Systems/測試假綠形態`:**
  - 只新增一行 `SEE:[[Projects/推送與CI提速_計劃]]`,格式合規。
  - 計劃的 `lands_in` 把它列為落點,但它沒有實質內容。對應的內容其實是第一條的假綠形態:子字串落在註解裡。
  - 該節點的 ★INVARIANT★ 要求「前置斷言證明現場成立」。`t_runner_shard_by_duration` 和 `t_test_durations_refresh` 有前置;`t_ci_yml_speed_shape` 沒有,所以沒擋住第一條。
- **其他文件:**
  - `ARCHITECTURE.md`、`reference.md` 的 89→90 與 `INDEX.md` 的「88→90」跟 `HELP_WHEN` 新增的 `test-durations` 一致。
  - `reference.md` 的 INDEX 句子本來寫 88,89 這個數字沒有出現在那句,所以「88→90」是順帶補正。
  - `.gitignore` 加了 `.lumos/test-durations-run*.json`。
  - `--ff` 讀的 glob 是 `test-cache*.json`,不會讀到新的 run 檔。
- **固定席節點(INVARIANT 與 RISK):**
  - 對 `lumos-cli-lifecycle`、`lumos-cli-read`、`guard-kill`、`design-loop` 的合約:
    - 它們牽連的是 `scripts/lumos`、`scripts/test_lumos.py`、`ci.yml`,但合約內容(re-inject、search 排除、guard kill 的 rc、設計審處置閘)都不在這次改動的路徑上。
    - 新增的只是 `test-durations` 子指令、測試執行器的分片與計時、`_BOOKKEEPING_FILES` 多一項。
    - 判不影響。唯一碰到邊界的是 `_BOOKKEEPING_FILES` 多一項,效果見第五條的 [S5]。
  - `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger` 是 ★RISK★ 且牽連 `scripts/lumos`,但內容沒有被這次改動違反,判不影響。

最嚴重等級:major;blocking 共 2 條。
