severity: major

圖譜固定席:這次沒附固定席節點(鏡頭計算超時),我也沒補算,所以沒有逐條判定可給。

**Finding 1**
severity: major
blocking: 是
`scripts/lumos:79930` 附近的 `_choice_cov_robo`(diff 第 912 行起)。「是不是 Robolectric 測試」只看檔案裡有沒有 `RobolectricTestRunner` 這個字串。
引句:「hit = [x for x in texts if re.search(r"(?<![\w$])" + re.escape(t) + r"(?![\w$])", x)]」
失敗場景:
- 測試用 `@RunWith(AndroidJUnit4::class)` 加 Robolectric 依賴(現在最常見的寫法),或繼承帶 `@RunWith(RobolectricTestRunner::class)` 的基底類別。這兩種檔案本身都不含那個字串,於是被判成「一般 JUnit」。
- 覆蓋設定沒生效時(例如 `includeNoLocationClasses` 沒套上),這些測試的專案類別有紀錄數是 0。`_CovBase.take` 只對 robo 測試標「覆蓋接不起來」,`breaker` 也只累計 robo 測試。
- 結果是斷路器永遠不跳,每個壞法行都算出「沒有測試經過」,記成存活(`via cov`),一支測試都沒跑。這正是計劃要防的情況,用的是計劃自己的判準。
最小重現:我在暫存 repo 放兩支測試,`ChildTest` 繼承帶 `RobolectricTestRunner` 的基底類別,`ModernTest` 用 AndroidJUnit4。呼叫 `_choice_cov_robo(wt, ["childCase","modernCase"])` 回 `{'childCase': False, 'modernCase': False}`。我沒有真跑 Gradle,所以「設定失效時整批記存活」這段是從程式碼推出來的。

**Finding 2**
severity: major
blocking: 是
`_choice_kill_pick` 的 via cov 帶過去分支(diff 第 701 到 704 行)。
引句:「if cov_sha_of is not None and evs[-1].get("cov_sha") == cov_sha_of(x):」
失敗場景:
- 舊路徑明確要求 `_CHOICE_TESTS_UNKNOWN not in str(tests_sha)` 才帶過去(守的測試所在檔查不完或找不到就當成變了,r2 H1)。新路徑沒有這個守衛。
- `_choice_cov_sha` 把 UNKNOWN 當一般字串雜湊進去。兩次的守的測試雜湊或所在檔 blob 都是 UNKNOWN 時,cov_sha 必然相等。
- 例如守的測試找不到所在檔,或第一次時限內沒查完。之後人補了一支經過這行的測試或改了測試檔,cov_sha 仍相同,舊的「沒有條款經過」存活被一直帶過去,不重跑。
- `_choice_cov_sha` 若拿到 UNKNOWN 的 `tests_sha` 或 `blob` 應回「不可比」,或在帶過去前加同一道 UNKNOWN 檢查。
最小重現:`_choice_kill_pick({"lines":[x]}, {key:[{"via":"cov","cov_sha":csha,...}]}, set(), None, "t", None, cov_sha_of=lambda x: csha)`,其中 `csha=_choice_cov_sha("t|"+UNKNOWN, UNKNOWN, "n")`。回傳的 carried 是 `{('a.kt','f'): 'survived'}`,應該要重跑。`t_choice_cov_carry` 若沒蓋 UNKNOWN 案例,就是抓不到的缺口。

**Finding 3**
severity: minor
blocking: 否
`_CovBase.cached` 與 `_choice_cov_pkg_dirs`(diff 第 1215 到 1224 行、第 942 到 953 行)。
引句:「if cp and os.path.isfile(cp):」
失敗場景:
- 續跑快取的 exec 檔存在但讀不出來(例如超過 8MB 上限、版本不同、內容壞),`take` 記「覆蓋資料沒產出」。這支測試不進 `todo`,同一個 at_sha 下永遠不會重量。
- 結果是含它的每個壞法都退成 unknown,全跑守的測試,是退化而不是誤判。
- 這個快取檔在存檔時是通過 `take` 才算有效的,卻沒有把「讀不出來」的快取檔刪掉重量。

**Finding 4**
severity: minor
blocking: 否
`_choice_cov_pkg_dirs` 的正規式(diff 第 950 行)。
引句:「m = re.search(r"(?:^|/)src/([^/]+)/(?:java|kotlin)/(.+)/[^/]+\.(?:kt|java)$", f)」
失敗場景:
- 沒有 package 的檔(預設套件)路徑是 `src/main/kotlin/Foo.kt`,`(.+)/` 配不到,`pkgs` 不含 `""`。
- 檔案所在資料夾和 package 宣告不一致時,`_choice_cov_proj_hits` 用類別名的套件算,同樣對不上。
- Robolectric 的真實覆蓋會被數成 0,前 5 支就誤跳斷路器,整個平台退成全跑。方向安全,但覆蓋功能會靜默失效。

**Finding 5**
severity: minor
blocking: 否
`_CovBase.cmd_of` 與 `wrap`(diff 第 1186 到 1189 行、第 1226 到 1240 行)。
引句:「self._cmd = {n: _run_cmd_expand(self.c.run_cmd, self.meth[n], name_filter=self.nf) for n in todo}」
失敗場景:
- 準備物件在跑任何配方之前就用測試名組指令並執行,沒有走 `_test_name_ok`。逐支流程是 `scripts/lumos:28522`,合併道是 `scripts/lumos:29074`,兩處都檢查名稱,後者還查 `_name_collision_reason`。
- 名稱超長、以 `-` 開頭、含控制字元的測試名會被當成基準去跑。`{method}` 有 shell 引號,所以不是注入,但名稱檢查被繞過。
- 撞名時,測試 A 的 exec 混進測試 B 的覆蓋,命中被高估。方向是多跑,不是漏。

**Finding 6**
severity: minor
blocking: 否
`_CovBase.red_rerun`(diff 第 1273 行)。
引句:「plain = _kill_run(self._cmd[n], self.c.run_dir, cap)」
失敗場景:
- 掛覆蓋的那支逾時,而且 `cap == full`(剩下時限 ≥ 600 秒)時,會再用同樣的 `cap` 不掛覆蓋重跑一次。
- 一支真的卡住的測試最多吃 2 倍的 `full`(約 1200 秒),可能超出總時限最多 600 秒。`cap` 沒有扣掉剛花掉的時間。

**沒有找到問題的項目**
- exec 解析器(`_choice_cov_exec_classes`、`_jacoco_block`、`_jacoco_varint`)對空檔、截斷、magic 或版本不對、varint 過大都回 `None`,不會丟例外。
- 續跑快取只留 2 個 at_sha 的邏輯,在第 2 與第 3 個 at_sha 的界線上正確。
- 其餘讀完沒有挑出界線錯誤,包括 `_choice_reach_only_clash` 的 `max_mutants` 預設改成 `None`、合併快篩的子集判讀、gov 的欄位登記。

總結:最高等級是 major(2 條:finding 1、2;minor 4 條)
