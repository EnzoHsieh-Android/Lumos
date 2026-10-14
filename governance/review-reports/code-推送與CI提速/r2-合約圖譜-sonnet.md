severity: major

我是三個月後的接手人,逐條核對了計劃、新加的筆記行和程式。我在臨時複本(`/tmp/lumos-seat-work/code-推送與CI提速-r2/合約圖譜-sonnet/repo`,固定版本 22f6e132)裡,對各條條款的實作各改壞一處,再跑綁定的測試。程式本身的行為跟條款都對得上,有問題的是測試偵測力:有幾種壞法,測試照綠。

## 條款改壞對照

| 條款 | 改壞的地方 | 結果 |
|---|---|---|
| S1 | 去掉權重下限、取消「平手比支數」、取消「再取編號小」、改成由小到大、同權重改成名字倒序 | 都翻紅 |
| S1 | 表雜湊從前 8 碼改成前 7 碼 | 照綠 |
| S1 | 表裡沒有的測試,中位數改成只算本次清單裡有的 | 照綠 |
| S2 | 表壞掉每份 rc2、沒有表照名字輪流分 | 有對應斷言(我沒逐條改壞) |
| S3 | 刷新時 run 檔改成只照檔名排序 | 照綠 |
| S3 | 刷新時 run 檔改成最舊的優先 | 翻紅 |
| S3 | 秒數改成存整數(條文寫小數三位) | 照綠 |
| S3 | 不保留舊值、不刪 run 檔、跳過的也記、消費專案也寫 run 檔、跑完不再讀表 | 都翻紅 |
| S4 | 拿掉 `set +e`、改成 PR 與推送都取消、去掉結尾耗時行 | 都翻紅 |
| S4 | 拿掉子殼層結尾的 `exit $rc` | 照綠(finding 1) |
| S4 | 群組鍵拿掉 `github.event_name` | 照綠,無害,PR 編號與提交編號不會撞 |
| S5 | 把耗時表從簿記檔清單拿掉 | 翻紅(`t_test_durations_refresh` 與 `t_codeloop_pass_survives_bookkeeping_commits` 都紅) |

## Findings

severity: major
blocking: 是
子殼層結尾的 `exit $rc` 沒有任何測試守,拿掉後 CI 紅了也會整步綠。
引句:「check("測試紅了也印耗時:子殼層先 set +e(預設 bash -e 會跳過後面)", line.lstrip().startswith("( set +e;"), line)」
- 輸入:把 `ci.yml` 第 123 行附近的 `; exit $rc ) > "/tmp/shard-$i.log"` 改成 ` ) > "/tmp/shard-$i.log"`。
- 現況:`python3.14 scripts/test_lumos.py -k t_ci_yml_speed_shape` 輸出 `7 passed, 0 failed`。
- 實際後果:用同樣結構的小殼層模擬紅的那份(`( set +e; false; rc=$?; echo done ) &` 加外層 `wait || rc=1`),外層得到 `outer rc=0`,應該是 1。真的 CI 就是所有紅的分片被吞成綠,整道全套閘失效。
- 條文與筆記:`bound-tests-gate` 的 PITFALL 寫「離開碼照樣保留,判定不受影響」,並綁 `t_ci_yml_speed_shape`;S4 也綁同一支。這支測試只比兩句 `echo` 字串和 `( set +e;` 開頭,沒驗 `rc=$?` 與 `exit $rc`。
- 應該:斷言這一行含 `rc=$?` 且以 `exit $rc` 結尾,最好在 shell 裡真跑一次紅的子殼層驗離開碼。
- 歸因:未判定(有證據的原有漏查)。修前 0cdfc7cc 的 `ci.yml` 已有 `exit $rc`,修補加的是 `set +e`。修補本身有效:同一個紅分片,修前日誌沒有耗時行、修後有 `第 1 份耗時 0 秒`,兩版外層 rc 都是 1。

severity: major
blocking: 是
[S3] 的「取檔案時間最新的一筆」,測試分辨不出檔案時間與檔名順序。
引句:「older, newer = lum / "test-durations-run-1of2.json", lum / "test-durations-run-2of2.json"」
- 輸入:把 `scripts/lumos` 的排序 `key=lambda p: (p.stat().st_mtime, p.name)` 改成 `key=lambda p: p.name`。
- 現況:`-k t_test_durations_refresh` 輸出 `33 passed, 0 failed`。改成 mtime 反向才翻紅。
- 原因:測試裡舊檔 `1of2`、新檔 `2of2`,檔名順序跟時間順序剛好一樣。真實檔名是 `1of16`、`10of16`、`2of16`,字串排序跟時間無關。
- 後果:改壞後,舊的秒數可能蓋掉新的,耗時表悄悄變舊。影響只是分得不平均,不是漏跑。
- 應該:造一組檔名順序與時間順序相反的 run 檔(例如 `2of2` 比 `1of2` 舊)。
- 歸因:未判定(有證據的原有漏查,r1 就已經有這組檔名)。
- 這條我給 major 是照計劃審計紀錄自己的標準:r1 把「拿掉規則測試照綠」算 blocking。若你們認為這只影響平衡、不影響正確性,可降為 minor。

severity: minor
blocking: 否
[S1] 要求印「表的 SHA-256 前 8 碼」,測試只比三份印的值一樣。
引句:「check("有耗時表:每一份印同一個表雜湊", len(heads) == 1, heads)」
- 把 `hexdigest()[:8]` 改成 `[:7]`,`t_runner_shard_by_duration` 輸出 `29 passed, 0 failed`。
- 寫死成常數也會過,因為沒有對照檔案實際的雜湊。
- 應該:用 `hashlib.sha256` 算一次,比對印出來的字串。
- 歸因:未判定(原有漏查)。

severity: minor
blocking: 否
[S1] 寫的是「表裡沒有的用全表中位數」,測試的表裡每個名字都在清單內,分不出全表和只算清單內的差別。
引句:「med = _sd.median(table.values())」
- 把中位數改成只算本次清單裡有的條目,`t_runner_shard_by_duration` 輸出 `29 passed`。
- 真實的耗時表一定含已刪測試的舊條目,兩種算法會不同。
- 應該:在「中位數」那組輸入裡多放一個清單外的極端值。
- 歸因:未判定(原有漏查)。

severity: minor
blocking: 否
[S5] 寫「代碼審留痕應不失效」,綁的 `t_test_durations_refresh` 只驗成員資格。
引句:「check("耗時表在簿記檔清單裡(刷新不讓代碼審留痕失效)", "governance/test-durations.json" in m._BOOKKEEPING_FILES, "")」
- 真正驗留痕不失效的是 `t_codeloop_pass_survives_bookkeeping_commits`(修補新加了一個耗時表提交),但條款沒綁它。
- 我把耗時表從清單拿掉,兩支測試都翻紅,所以現在偵測得到;只是標註錯位。
- 應該:S5 加綁 `t_codeloop_pass_survives_bookkeeping_commits`。
- 歸因:有證據的原有漏查。

severity: minor
blocking: 否
計劃〈實務隱患〉的一句話已經過期,而且「跑完再讀一次表」沒有任何一條條款涵蓋。
引句:「每份印出的表雜湊不同就看得出來。推送前掛鉤核對各份雜湊一致,放在第二階段一起做(那時要改推送前掛鉤)。」
- 隱患寫「各份可能讀到不同的表,雜湊不同就看得出來」,現在程式在每片結尾再讀一次表,不同就 rc2 擋下(`這一片跑的期間耗時表換了`)。
- 〈做法〉與 [S1]–[S5] 都沒寫這個行為;它的測試在 `t_test_durations_refresh` 裡(S3 名下),跟 S3 無關。
- 這個檢查我驗過:拿掉比對,該測試翻紅。
- 接手人讀計劃會以為還沒有擋,又找不到條款。
- 應該:改寫該隱患,並加一條條款(例如 [S6])綁這個測試。
- 歸因:有證據的修復造成的文件漂移,r1 修補新增了行為但沒回頭改計劃。

severity: minor
blocking: 否
〈做法〉寫「秒數存到小數三位」,沒有測試守。
引句:「table[k] = round(float(v), 3)」
- 改成 `round(float(v), 0)`,測試輸出 `33 passed`,因為測試用的秒數全是整數值。
- 歸因:原有漏查。

severity: minor
blocking: 否
撤除條件量的對象,計劃與 `ci.yml` 註解不一致。
引句:「# 每份記起訖,結尾印“第 i 份耗時 N 秒”:耗時分片的撤除條件要量每份(推送與CI提速 RETIRE-IF)」
- 計劃的 RETIRE-IF 量的是「各台 shards 機器耗時的最大值與最小值之差」,是每台(一台跑兩份),不是每份。
- 每份耗時是診斷用,不是撤除條件的度量。
- 應該:其中一邊改字。

severity: minor
blocking: 否
`測試假綠形態` 的 `lands_in` 登記了,內容只有一條裸連結。
引句:「SEE:[[Projects/推送與CI提速_計劃]]」
- 計劃 `lands_in` 寫了 `Systems/測試假綠形態`,但那篇只多一行 SEE。
- 這輪實際發生的新案例,例如測試靠註解行騙綠、只驗成員資格不驗行為,並沒有記進那篇的形態清單。
- 那篇自己寫「本專案撞最多次的坑=測試存在但沒在驗它宣稱要驗的」。
- 接手人從形態清單找不到這次的案例。
- 歸因:原有漏查。

## 固定席節點(逐條判)

- `Systems/測試假綠形態`(★INVARIANT★,前置斷言證明現場成立):不受影響。新測試的前置斷言多半成立,例如 `★前置★ 現場成立:那支小測試真的寫出了耗時表`、`找得到跑分片的那一行`,我改壞實作都對應翻紅。唯一漏的是上面 finding 1。
- `Systems/pitfalls-code-loop`(★RISK★):不受影響。簿記檔清單只多一項,`-k bookkeeping` 111 條全過。
- `Systems/lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle`、`design-loop`:不受影響。它們綁的合約沒被這次改動碰到,我跑了 `docs_enumeration` 和 `help_when`,13 與 2 條全過。
- `Systems/reversibility-governance-ledger`、`loop-convergence-recording`:不受影響,改動不碰它們的邏輯。
- 清單裡只列名的節點:沒有逐篇核對。
- 摘要格式:`lumos lint` 對 `bound-tests-gate`、推送與CI提速計劃、`測試假綠形態` 都是 0 問題。新的 WHY 與 PITFALL 必有鍵齊全(`[出處:]` `[因:]` `[根因:]` `[修法:]` `[test:]`)。
- 其他文件:指令數 90 的三處(`ARCHITECTURE.md`、`reference.md` 兩處)一致,`INDEX.md` 與 `06-代碼審與推送.md` 的新列,跟 `HELP_WHEN` 一致。
- 小疑慮:`06` 和 `INDEX` 的新列會隨 skill 發給消費專案,但消費專案的執行器不寫 run 檔,在那裡跑 `lumos test-durations refresh` 一律 rc2。這條我沒當 finding。

## 修補鏡頭三問

1. 原問題的修復效果,行為證據如下。
   - 「`set +e`」:用小殼層模擬紅分片,修前外層 rc=1 但日誌沒有耗時行;修後 rc=1 且有 `第 1 份耗時 0 秒`。有效。
   - 「跑完再讀表」:輸入是開頭沒表、結尾有表。預期 rc2;拿掉比對則回 0;現況 rc2。有效。
   - 「消費專案不寫」:把 `_is_src` 改成 `True`,斷言翻紅。有效。
2. 修補處相鄰路徑。
   - `set +e` 對 `exit $rc` 的保留沒有測試(finding 1)。
   - 跑完再讀表只在有分片時執行。表被刪、被換、原本就沒表,三種都有處理:`(None,None)` 對比會擋。
   - `--suite` 子集配合有表時的空片:`t_runner_shard...` 那組沒直接測,但既有的 `--suite keys --keys _range_base --shard 3/4` 在真 repo 有耗時表時走同一路徑,且是綠的。這是順帶覆蓋。
3. 新發現同一案例的修前修後。
   - finding 1、2 在 0cdfc7cc(修前)與 22f6e132(修後)都成立:修前測試也沒驗 `exit $rc`,run 檔排序也一樣。不是修補造成的回歸,是修補沒補到的偵測力缺口。
   - 我沒有逐一在修前版本重跑 finding 2 到 7 的改壞實驗。

## 未驗範圍與殘留

- 沒讀 `r2-repair-binding.json` 與 `r2-intake.md`:固定版本裡不存在,而且指示不讀上輪席報告。「配對案例」是我自己選的,上面三例。
- S2 十種壞表的 stderr 說明文字:只有一個案例斷言了 `耗時表` 字樣,其餘只斷言 rc2。我沒實測拿掉說明的結果。
- 我的改壞實驗讓 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 下留了一批 `gctl-run-*` 現場(測試紅時保留)。裡面混有別的會談的目錄,我分不出哪些是我的,所以沒有刪,請編排者處理。
- `/tmp/lumos-seat-work/code-推送與CI提速-r2/合約圖譜-sonnet/` 是我的臨時目錄,由編排者刪。

總結:最高等級 major,blocking 共 2 條(`exit $rc` 沒測、run 檔時間排序沒測);其餘 7 條為 minor、不阻擋。
