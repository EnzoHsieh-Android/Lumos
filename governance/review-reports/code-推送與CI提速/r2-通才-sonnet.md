severity: minor

審的範圍是固定版本 22f6e132 對主線 1b83927e 的完整改動,加修補差異(0cdfc7cc 到 22f6e132)。我沒找到會讓測試漏跑或把壞結果放行的缺陷。下面兩條都只是成本或極端輸入的問題。

## Findings

severity: minor
blocking: 否
- 條目:新測試 `t_runner_shard_by_duration` 太慢,離逾時上限只剩約 3 倍(⚠ 會不會在 CI 變假紅判不準)
引句:「rcs = [run("--shard", f"{i}/3", "--list").returncode for i in (1, 2, 3)]」
- 場景:這支測試每次檢查壞表都對 3 片各開一個子行程,10 種壞表共 30 次,加上其他情境約 36 次。每次要重新匯入整個 2MB 的測試檔,單次約 1.1 秒。
- 實測:我在固定版本的複製品裡跑 `python3.14 scripts/test_lumos.py -k t_runner_shard_by_duration`,印出 `58.8s t_runner_shard_by_duration (餘裕 3x)`,上限是 180 秒。
- 風險:專案自己的註解說 CI 機器慢約一倍,而且一台機器同時跑 2 份。PR #7、#8 就曾因為本機 105 秒的測試在 CI 超過 180 秒被砍。分到這支的那一份可能被判 TIMEOUT 而整次 CI 紅;一旦出現,常見的下一步是有人調高全域上限,削弱逾時偵測。
- 這支測試也讓拿到它的那一份多跑約 1 分鐘,和「縮短 CI 時間」的目標相反。
- 應該:壞表情境直接在行程內呼叫 `_load_durations_table`,只留 1 到 2 次真正的子行程驗 rc2;或在 `TIMEOUT_OVERRIDE` 給它單獨的上限。
- 歸因:未判定。我沒有修前版本的測試耗時數據。查證命令與結果如上。
- 它也寫了「一片跑完耗時表被換掉」的測試,同一類做法,但那支只有 25 秒(餘裕 7 倍),不用處理。

severity: minor
blocking: 否
- 條目:`--shard 1/N` 的 N 很大時,記憶體隨 N 線性成長(⚠ 極端輸入,單人使用下機率低)
引句:「loads, counts, buckets = [0.0] * live, [0] * live, [[] for _ in range(n)]」
- 場景:`_shard_by_duration` 只需要第 `_i - 1` 份,卻先建出 n 個空串列。上一輪只把「比較次數」改成 `live`,配置沒跟著改。
- 實測:同樣形狀的配置,n=10^6 約 90MB、0.09 秒;n=10^7 約 750MB、1.4 秒;外推 n=10^9 約 75GB,會被系統砍掉。舊的輪流分是 O(1)。
- 應該:只建 `live` 份,回傳時 `buckets[i-1] if i <= live else []`。測試 ⑥ 現在鎖死「回傳長度等於 n」,要一併改。
- 歸因:未判定。程式碼確實是修後版本才有這個形狀,但我沒對照修前版本。

## 三問

1. **原問題的修復效果,有什麼行為證據?** 修補只動了 CI 子殼層加 `set +e`,我獨立驗證了。
   - 輸入:`bash -e -c '( s=...; false; rc=$?; echo "耗時"; exit $rc ) > log & wait $! || echo red'`
   - 預期:測試紅時仍要印出耗時。
   - 修前(沒有 `set +e`):log 是空的,印不出耗時,只有 `red`。
   - 修後(有 `set +e`):log 有「耗時」,離開碼照樣回傳,也有 `red`。
   - 文件裡其他幾項修補(刷新刪檔前核對、耗時表換掉時擋下)我讀過邏輯,也跑過 `t_test_durations_refresh`,33 項全過。其中「表被換掉」那項用臨時 repo 實際寫入表,檢查結果是 rc2,確認真的會翻紅。

2. **修補處的正常、錯誤、相鄰路徑是否仍成立?**
   - 正常:`t_runner_shard_by_duration` 29 項全過,`t_test_durations_refresh` 33 項全過,都在固定版本複製品上跑。
   - 錯誤:壞表(10 種)每片都回 rc2;結尾再讀一次表,不同就回 rc2。
   - 相鄰:沒有表就照名字輪流分;空片的 rc1 和帶 `--suite` 的子集空片 rc0 都照舊;`--suite` 先篩、再分片、再 `--ff` 重排、最後 `-k`,各片算出的分法一致。
   - `ci-wait` 是按 sha 篩 run,PR 舊提交被 `cancel-in-progress` 取消,不影響新提交的判定。我讀了 `cmd_ci_wait`,cancelled 會落在 undetermined、不會誤判綠或紅。

3. **新發現的同一案例,修前、修後各是什麼結果?** 兩條都是原有的設計或配置形狀,我沒有逐條對修前版本做對照,所以歸因都標「未判定」。

零回歸的主張只對我驗過的路徑成立。

## 固定席節點

- `pitfalls-code-loop`(RISK)、`reversibility-governance-ledger`、`loop-convergence-recording`:牽連檔是 `scripts/lumos`。本次只新增子指令 `test-durations`,改了簿記檔清單(多一個 `governance/test-durations.json`),沒動 pitfalls 的風險分級或留痕邏輯。`t_codeloop_pass_survives_bookkeeping_commits` 補了前置斷言和「真的改到耗時表」,不影響這些節點。
- 測試假綠形態(INVARIANT:還原翻紅釘必須配前置斷言):新測試大多附了 `★前置★` 斷言,例如「找得到跑分片的那一行」、「那支小測試真的寫出了耗時表」、「探針裡合法與不合法的都有」、「現場成立:刷新本身成功」。四條分片規則也各給一組拿掉就會變的輸入。我沒發現還原後仍全綠的新測試。
- `lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle`、`design-loop`:不影響。這次沒碰 search、guard kill 的 rc 與 JSON、re-inject、處置閘。
- 超出上限、只列名的節點(`bound-tests-gate`、`check-r-guard` 等):不影響。我只讀了 `bound-tests-gate` 的新增 WHY 與 PITFALL 行,內容和程式一致,沒有對不上的地方。

## 未驗範圍

- 沒在真實的 GitHub Actions 跑 `concurrency` 與 `cancel-in-progress`,只讀了設定和 `ci-wait` 的程式。
- 沒跑全套,也沒量 CI 每份耗時的前後差。
- 只核對了耗時表的格式(2029 筆、合法),沒有逐項核對它和實際測試的對應。

最嚴重等級:minor;blocking 共 0 條。
