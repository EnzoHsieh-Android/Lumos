severity: major

審查範圍:r1-snapshot.patch 全部 977 行逐 hunk 讀完。我也在 `/Users/enzo/harness/lumos-android-ui-events`(HEAD e7c5a0d55)跑了相關測試,用 detekt 1.23.8 實跑,並用 WebFetch 對照官方頁原文。臨時目錄已用字面絕對路徑刪除。

## 發現

### F1 條款 S4 的測試只擋退出碼 3,YAML 語法錯或型別錯照樣綠
severity: major
blocking: yes

file: `scripts/test_lumos.py:65564`(`t_kotlin_idioms_detekt_snippet_runs`)

引句:「check("S4:照抄範例跑 detekt 不因設定錯誤整次失敗", r.returncode != 3 and "does not exist" not in out」

失敗場景:
- 這支測試要守的是「手冊〈機檢接線〉的範例照抄能跑」,但判準只排除「退出碼 3 加 does not exist」這一種失敗。detekt 1.23.8 的設定壞法不只這一種。
- 我實跑了三種壞設定,結果如下。

| 壞設定 | 退出碼 | detekt 實況 |
|---|---|---|
| 範例少一個 `}`,例如 `GlobalCoroutineUsage: { active: true` 沒收尾 | 1 | `InvalidConfigurationError: Structure must be from type Map<String,Any>!` |
| `active: yes please` | 1 | `IllegalStateException … is not of required type Boolean` |
| 不存在的規則名,或屬性名拼錯 `methdos` | 3 | `is misspelled or does not exist` |

- 前兩種(退出碼 1)整次不檢查任何東西,是「範例照抄跑不起來」的同一類失敗。
- 我把第一種的輸出代進該判準:`r.returncode != 3 and "does not exist" not in out` 為 True,測試照綠。
- 這次 diff 剛改過這段範例(拿掉一行、加了註解掉的 `ForbiddenImport` 區塊)。往後有人取消註解時縮排或括號打錯,這是最容易發生的改壞,而這支測試擋不住。
- 這支測試是 S4 條款的唯一機械驗證,也是這次修補宣稱要擋的錯,所以我判 major。
- 修法:範例在測試的樣本上不該有任何告警,應該直接斷言退出碼為 0,或至少排除 {1,3}。
- 順帶:我把範例放進別的目錄(套件宣告對不上目錄)時,退出碼是 2,同樣會通過。
- 重現指令:`detekt --input <含 src/p/A.kt 的目錄> --build-upon-default-config --config <缺右括號的 yml>`,輸出退出碼 1,上面那個判準算出 True。

### F2 R22 把 Flow 測試頁的範例寫成沒有 `UnconfinedTestDispatcher`,跟官方頁及同次新增的標準自相矛盾
severity: minor
blocking: no

file: `skills/kotlin-idioms/SKILL.md:194`,對照 `skills/lumos-project-notes/commands/test-quality-standard.md:126`

引句:「官方範例用 `backgroundScope.launch { viewModel.score.collect {} }`，測試結束時自動取消」

失敗場景:
- 官方 Flow 測試頁(WebFetch 取回)的範例是 `backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { viewModel.score.collect {} }`。
- 同一個 diff 的 test-quality-standard 也寫了帶 `UnconfinedTestDispatcher(testScheduler)` 的版本,所以兩處互相矛盾。
- 照 R22 字面寫的人,收集協程會用 runTest 預設的 StandardTestDispatcher,先排隊不馬上跑。
- 接著他立刻 `assertEquals(1, viewModel.score.value)`,上游還沒被訂閱,拿到的是初始值,測試莫名其妙紅。
- 這句還標了「官方範例」,屬於把改過的寫法掛上官方名義。
- 沒有 Kotlin/Gradle 環境,我無法實跑,所以降為 minor。
- 修法:R22 改成跟標準同一寫法,或補一句要搭 `advanceUntilIdle()`。

### F3 S4 測試在沒有 detekt 時直接 return,runner 記成通過
severity: minor
blocking: no

file: `scripts/test_lumos.py:65553`

引句:「print("  ⚠ 這台沒有 detekt,照抄設定範例實跑那段沒驗到(只驗到範例存在)")」

失敗場景:
- 專案慣例是用 `raise _SrcOnly(...)` 讓 runner 記成 skip,例如這份 diff 內其他新測試對缺 skills 的處理。
- 這裡改用 print 加 return,CI 或沒裝 detekt 的機器上 runner 會算它通過。
- Verification 筆記有誠實寫「CI 沒有 detekt 時 S4 印沒驗到」,所以是已知取捨,不是隱瞞。
- 但它符合〈測試假綠形態〉的「沒走到被測分支卻綠」。建議改成 `_SrcOnly`,讓 skip 數字可見。

## 逐條判定

**(b) detekt 實測主張(挑了六項在臨時目錄實跑,全部成立):**
- 只給 `--input` 時,只有 `GlobalCoroutineUsage` 報。
- 帶 `--classpath`(coroutines-core-jvm 1.9.0 加 kotlin-stdlib 1.8.20)與 `--jdk-home` 後,以下規則都報:`CouldBeSequence`、`ForbiddenMethodCall`、`InjectDispatcher`、`RedundantSuspendModifier`(3 筆)、`SleepInsteadOfDelay`、`SuspendFunWithFlowReturnType`。
- `SuspendFunSwallowedCancellation` 帶齊型別資訊也只報 `runCatching`(A.kt:11),不報 `try/catch(Exception)`、`catch(Throwable)`。
- 完整套件名 `kotlinx.coroutines.GlobalScope.launch` 不報,import 後的才報。
- `ForbiddenImport` 不需型別資訊;範例取消註解後可跑,import 兩行都報。
- 舊範例加了不存在的規則會退出碼 3,與 Verification 筆記的描述一致。

**(a) 官方事實主張(WebFetch 逐頁對照):**
- 架構建議頁:「不要從 ViewModel 送事件給 UI」是 Strongly recommended。
- 「ViewModel 不持 Context」是 Strongly recommended,「不用 AndroidViewModel」是 Recommended,「假實作優於 mock」是 Strongly recommended。三者的等級和手冊 R19、R20、R22 一致。
- UI 事件頁:原文是「Kotlin Channels 或其他串流」,沒有點名 SharedFlow。
  - 審查題與 R19 寫「Channel/SharedFlow」屬於把「其他串流」具體化,合理但不是官方逐字。
  - 我判不到 minor 以上,因為 R19 並未宣稱官方點名 SharedFlow。
- 其餘條目也都與來源頁一致:`rememberSaveable` 旗標、狀態還原三欄表(設定變更與程序被殺的存活情況、小資料、主執行緒序列化掉幀)、`returnDefaultValues` 的 Groovy 寫法與警語、Robolectric 最後手段、Hilt 單元測試不需要、MainDispatcherRule 屬性順序、Standard 與 Unconfined 的取捨、要測什麼與邊界清單。
- 一個小瑕疵:「`runTest` 整支測試預設 60 秒逾時」在協程測試頁只對應 `dispatchTimeoutMs`,頁面沒有講整支測試逾時。內容大致合理,無法舉出具體失敗,不標。

**(c) 審查題改措辭:**
- `kt-flow`、`kt-leaks` 的 id 與 `when` 兩個欄位在 diff 裡完全沒動。
- `kt-leaks` 的 `when` 還有測試逐字釘住。
- 效能檢核目錄「題(縮)」欄新前綴與 `q` 開頭一致。
- 我跑了 `-k stack_question` 共 120 支,全綠。
- 全 repo 沒有其他地方殘留「事件=SharedFlow」或「單消費=Channel」。
- 已知限制:`AndroidViewModel` 不在觸發字內,只寫 `: AndroidViewModel(app)` 的改動不會亮這題。計劃明寫且有 `REVISIT:2026-12-01`,不另算缺陷。

**(d) 帳本與錨點:**
- `git diff --numstat` 顯示 `.canary-log.jsonl` 為 +2/-0,`.governance-log.jsonl` 為 +4/-0,只有追加。
- 追加的 JSON 行可解析。
- `anchor-baseline.json` 只改 `test_lumos.py` 的雜湊、`approved_at`、`note` 三處。
- `shasum -a 256 scripts/test_lumos.py` 的結果是 `56a111ab…7324`,與基準檔一致。

**測試邊界(鏡頭 1):**
- 新增的 `t_kt_*`、`t_kotlin_idioms_*`、`t_test_quality_standard_android_unit_section` 都對標題或正則做了前置斷言,找不到時是明確紅,不會拋例外或誤判。
- 條號必須從 1 起連續,審查鏡頭的 U+2013 破折號正則找不到會紅。
- 取小節時,檔尾沒有下一個 `### ` 只會多切掉最後一個字元,不影響判斷。
- 臨時目錄:`mkdtemp` 之後在 try/finally 內 `rmtree`,例外時也會清;沒有 detekt 的提早 return 發生在 `mkdtemp` 之前,不會留目錄。
- 弱點:`t_test_quality_standard_android_unit_section` 只查關鍵詞存在於整節。若只把某一段內容挖空、關鍵詞留在別段,測試仍綠,所以它並未做到 docstring 所說的「三段被掏空」。我講不出會破壞必要行為的具體改壞,不標。

**manifest:** 0 條 claims 落在改動行上,無需判定。散文外的 hunk 我都自己看過。

**圖譜鏡頭(固定席節點):**
- `linter精選目錄`(`android.yml` 的家):新增的 FACT 與 REVISIT 行格式齊全,只改註解不改開關,不影響其合約。
- `lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`bound-tests-gate`、`guard-kill`、`授權與歸屬`:這些 ★INVARIANT★ 涉及的行為(search 排除 superseded、re-inject 邊界、處置閘、綁定測試真跑、guard kill 退出碼、授權檔不入 vendored 清單)都沒被觸碰。
  - `scripts/lumos` 只改兩個字串常數,`test_lumos.py` 只新增函式,不改既有判定。
  - 我用 `lumos lint` 檢查六篇受影響筆記,全部 0 問題。
- `測試假綠形態` 的 INVARIANT 要求「還原翻紅釘須配前置斷言證明現場成立」。
  - 新測試大多有前置斷言。
  - 唯獨 S4 的前置斷言只證明範例存在,沒證明 detekt 真的分析成功,這正是 F1 與 F3 的來源。
- 這次沒有「⚠帶殘留」徽章,也沒有「新增殘留」段,殘留題不適用。

**角色鏡頭:** 本次無前端卡,後端卡也不適用(純文件、審查題字串與測試),略過。

總結:最高等級 major(F1)
