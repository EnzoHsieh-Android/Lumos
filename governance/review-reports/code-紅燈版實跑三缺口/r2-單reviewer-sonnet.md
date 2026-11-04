severity: major

## 摘要

我逐 hunk 讀完 723 行修補差異,並用修前 `bcd9a170` 與修後 `06e10168` 兩版實際跑過。修補要修的 G1 到 G7 都有行為證據。找到 1 條 major(`java-junit` 的 DeviceException 判定沒有測試保護)和 2 條 minor。三條都不是這輪修補造成的。

## Findings

### F1 `java-junit` 沒接裝置的判定沒有任何測試保護,拿掉也全綠
severity: major
blocking: 是
- 引句:「`_ENV_MISSING_EVIDENCE = {"kotlin-junit": _AGP_DEVICE_MISSING_RE, "java-junit": _AGP_DEVICE_MISSING_RE}`」
- file: `scripts/lumos:68527` 是新表。
- file: `scripts/test_lumos.py:123318`(`t_spec_gate_device_missing_not_red`)只用 Kotlin fixture,`_mp_repo` 的 profile 全是 `kotlin-junit`。
- 規格 [S6] 寫的是「Kotlin/Java 測試的輸出含 AGP 的 DeviceException」,所以 Java 是必要行為。
- 失敗場景:
  - 把表裡 `"java-junit"` 那一項拿掉,Java 專案沒接裝置會被判成紅並記一筆假逃逸,也就是這案要修的症狀。
  - 測試照綠,因為沒有任何斷言走到 `java-junit` 這個鍵。
- 最小重現(在我自己複製的程式樹裡改,沒動 repo):拿掉該項後跑 `python3.14 scripts/test_lumos.py -k t_spec_gate_device_missing`,輸出 `6 passed, 0 failed`。
- 目前的程式行為是對的:我直接呼叫 `_spec_gate_judge_items`,`java-junit` 回 `weak`,原因是「環境沒跑起來(沒接裝置?)」。缺的只是守衛。
- 歸因:有證據的原有漏查。
  - 修前版本用的是 `TEST_PROFILES["java-junit"]["env_missing_re"]`。我在修前樹刪掉那個欄位後跑同一支測試,也是 `6 passed, 0 failed`。
  - 這輪搬表沒有新增也沒有補這個缺口。
  - `r1-fix-mutation.md` 的 M11 與 N6 改壞的是整個判定或整張表的查詢,沒有逐一拿掉單一格式的項目。
  - `r2-behavior-cases.md` 的 G2 欄已承認「java-junit 沒有獨立案例」。

### F2 整檔重新縮排或換行尾改成 CRLF,檔裡有多行字串且沒斷言的測試會被列成 `tq/no-assertion`
severity: minor
blocking: 否
- 引句:「`isig` 字串原樣保留、字串外空白照 _tg_ident 整理,」
- 引句:「給判本體有沒有變用("a, b" 改 "a,b" 算有變)。同 clone 偵測的分法:只差空白版面的算同一支,內容改了另判」
- file: `scripts/lumos:48999-49000` 與 `scripts/lumos:49722`。
- 失敗場景:
  - 測試 `fun smoke() { render("""\n    {"a": 1}\n""") }` 沒有斷言,內含多行原始字串。
  - 整檔縮排多一層,或換行尾由 LF 轉 CRLF。多行字串的內容跟著變,`isig` 不同,函式被當成「本體有變」,進入 `tq/no-assertion` 判斷。
  - 實測 `_tg_analyze`:修前版與修後版都回 `[('tq/no-assertion', ...)]`。相同的檔案在主線版(`cb14c6fe`,`sig` 是拿掉全部空白)回 `[]`。
  - 這跟筆記宣稱的「只差空白版面的算同一支」「重新縮排照樣不算有變」不符。
- 影響:誤報的候選可以放行,觸發條件窄(要有多行字串、沒斷言)。
- 歸因:有證據的原有漏查,但它是這條分支的 r1 提交 `bcd9a170` 引入的。
  - 修前與修後輸出相同。
  - 這輪把簽名拆兩份保留了這個行為,只修了「找搬家」那條路。

### F3 單平台改回後,懸空的含冒號測試名可能被另一支同名後綴的測試悄悄頂替而判綠
severity: minor
blocking: 否
- 引句:「`elif bare and t not in methods_for(default) and bare in methods_for(default):`」
- file: `scripts/lumos:15999-16001`。這裡只確認「整串找不到、去掉第一個冒號前那段找得到」,沒有檢查那段前綴原本是不是某個平台名。
- 失敗場景:
  - 單平台專案,留痕 tests 是 `["gone:fee_jvm"]`(一支含冒號、現已刪除或改名的測試),同時存在另一支 `fee_jvm`。
  - 修前版:判懸空,回紅,擋下並記逃逸(rc=1,逃逸帳有新增)。
  - 修後版:改跑 `fee_jvm`,綠,放行(rc=0,`ran=['jvm fee_jvm']`,逃逸帳沒有)。
  - 本來該提醒的「綁定的測試不見了」被吃掉。
- 影響:要有含冒號又沒有空白的測試名(去掉前綴後不以空白開頭),才有機會撞到,機率低。
- 歸因:有證據的修復造成的新行為。
  - 修前是紅、修後是綠。
  - 同一支程式的另一半是對的:`jvm:fee: rounds up`、`jvm:fee_jvm` 在修前會紅並記假逃逸,修後綠且不記逃逸。

## 筆記不一致(併入 minor,沒有獨立測試可翻紅)

- file: `docs/lumos-toolchain-knowledge/Projects/紅燈版實跑三缺口_計劃.md:95`
- 回退節還寫「沒接裝置那項拿掉兩個測試格式的 `env_missing_re`」。這個欄位在這輪已經改成 `_ENV_MISSING_EVIDENCE`,照字面找不到。
- 引句:「沒接裝置那項拿掉兩個測試格式的 `env_missing_re` 與逃逸的例外」
  - 這句不在 `r2-repair-review.patch` 內,屬審材外的佐證。
  - 審材內與它相對的是做法 3 與 test-guard 筆記改寫成 `_ENV_MISSING_EVIDENCE`。
- 歸因:有證據的修復造成。r1 寫回退節時對的,這輪只改了做法節,沒同步回退節。

## 三問

### ① 原問題的修復效果

| 組 | claim / input | before | after | 結論 |
|---|---|---|---|---|
| G1 判法只有一支、三處呼叫 | `grep _tg_ledger_ignored`,審材外全庫 | 有 | 程式與筆記都已改成 `_gov_ledger_ignored`,只剩 `governance/review-reports/*patch` 的歷史引用;`t_tq_guard_redbase_ledger_ignored`、`t_spec_gate_redbase_ledger_ignored`、`t_doctor_gov_ledger_ignored`、`t_tq_guard_ledger_ignored_fix_resolves` 共 27 條斷言全過 | 已修復(lens 4d 通過) |
| G2 沒接裝置 | 呼叫 `_spec_gate_judge_items`,rc=1 且 tail 含 DeviceException | kotlin、java 都是 `weak`/環境沒跑起來 | 同左;自訂格式名、`None`、csharp 回 `red`,沒崩 | 行為對,java 無守衛(F1);lens 4c 通過 |
| G3 doctor 接所有例外、規格閘走 stderr | `t_spec_gate_redbase_ledger_ignored`、`t_doctor_gov_ledger_ignored` | — | 全過 | 正向成立;`except Exception` 那條丟例外路徑無測試,我也沒造出會丟例外的輸入 |
| G4 `angle` gating | `_rg_split_args("a<b,c>,d", stripped=…)` | `['a<b','c>','d']` | `['a<b,c>','d']` | 已修復。唯一帶 `stripped` 的呼叫端 `scripts/lumos:49084` 本來就傳 `angle=False`,所以對現有行為無影響 |
| G5 搬進巢狀類別 | 多行字串測試搬進 `inner class` | `tq/test-removed` | `[]` | 已修復;另測斷言內多行字串的搬家與整檔縮排,也是 `[]` |
| G6 改回單平台 | 多平台留痕 `jvm:fee: rounds up`,設定改單平台後跑推送前驗收 | rc=1、`ran=[]`、逃逸帳新增 | rc=0、`ran=['jvm fee: rounds up']`、逃逸帳沒有 | 已修復(附帶 F3) |
| G7 還沒提交那句自帶改法 | `_ig_repo` 的未提交紅燈版 | 「照孤兒那條的改法…」 | 含「到蓋到它的那支忽略設定檔…改完 `git check-ignore -q …` 退出碼是 1」,全文 238 字 | 已修復 |

### ② 修補處的正常、錯誤與相鄰呼叫路徑

- 8 組相關測試(`string`、`record_keeps_platform`、`push_bare`、`device_missing`、`redbase_ledger`、`ledger_ignored`、`spec_gate_redbase_ledger`、`doctor_gov_ledger`)全過,分別是 23、7、3、6、12、9、4、2 條。
- 多平台含冒號名字(`jvm:fee: rounds up`)與舊留痕補平台的路徑仍成立。
- `sig` 只在 `_tg_renames`(`scripts/lumos:49680-49684`)用,`isig` 只在 `_tg_fn_cands`(`scripts/lumos:49722`)用,沒有第三處讀這兩個值(lens 4a)。
- 單平台去前綴的邊界:
  - 名字本身含冒號且存在時(`fee: rounds up`)先走「整串在索引」,不會誤剝。
  - 整串不在索引時的碰撞見 F3。
- 沒驗到的範圍:
  - `LUMOS_TEST_TIMEOUT` 與 256KB 輸出截斷時,DeviceException 那行可能被砍掉(`_kill_cap` 只保護「跑過」證據)。這是修補前就有的設計,我沒造出實例。
  - git 回 128 與逾時只看了程式路徑,沒另外實跑。
  - 全套測試沒跑。

### ③ 新發現在修前、修後各是什麼結果

| 發現 | 修前 `bcd9a170` | 修後 `06e10168` | 歸因 |
|---|---|---|---|
| F1 | `java-junit` 欄位拿掉,測試 6 passed | 表項拿掉,測試 6 passed | 原有漏查 |
| F2 | `tq/no-assertion` | `tq/no-assertion`(主線版 `[]`) | 原有漏查,分支 r1 引入 |
| F3 | 紅、記逃逸 | 綠、放行 | 修復造成 |

## 圖譜鏡頭

- `Systems/lumos-cli-read`(search 預設排除 superseded)與 `Systems/guard-kill`(rc 優先序、`--json` 純度):這份 diff 不碰 `search` 的濾網,也不碰 guard kill 的 rc 與 JSON,不影響。
- `loop-convergence-recording`、`pitfalls-code-loop`:diff 沒動收斂記帳,也沒動 `pitfalls` 的分級與觸發,不影響。
- `reversibility-governance-ledger`:diff 只把 WHY 行裡的函式名改成 `_gov_ledger_ignored` 並註明放在帳檔區,與程式一致。判法本身沒動帳的寫入與合約,不影響。
- `測試假綠形態`(還原翻紅釘須配前置斷言):
  - 新增的 S1 搬巢狀類別斷言是純否定式(`not in got`),沒有前置證明那一支被解析且配對成功。
  - `r1-fix-mutation.md` 的 N1 顯示還原會翻紅,所以現場是實的,但斷言本身仍可能因現場失敗而空綠。這不構成獨立 finding。
  - S3 的單平台案有 `★前置★`,沒問題。
- `test-guard`(Systems 筆記):簽名拆兩份的 WHY 與程式一致,但「重新縮排不算有變」的措辭與 F2 衝突。
- 其餘固定席節點(`bound-tests-gate` 等只列名的):diff 沒碰其函式,我沒有逐篇讀,判不影響的依據只是檔案範圍。

## 暫存

- 我自己的工作目錄 `/private/tmp/lumos-seat-work/code-紅燈版實跑三缺口/單reviewer-sonnet` 已用字面絕對路徑刪除。
- 跑測試時系統暫存目錄 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 裡有 605 個 `gctl-*`,我無法分辨哪些是我這個會談建的,沒有整批刪,留給使用者或原會談處理。
- repo 工作樹 `git status` 乾淨,我沒改任何檔。
