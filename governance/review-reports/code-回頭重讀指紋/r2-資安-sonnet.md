severity: major

這輪修補沒有補到一個洞:同檔另一個結構相同的函式,指紋還是一樣。hunk 標籤只取「頂格那行的名字」加「最近一個縮排的 def 名」,許多語言與寫法下兩個函式會得到同一個標籤。

我沒有用完整推送流程(`git push`)。我 clone 出實驗 repo,載入 reread-fp 的 `scripts/lumos`,直接呼叫真函式 `_note_reread_hunk_tags` 和 `_patch_file_changes(headers=False, lf_only=True, hunk_tag=…)`。diff 用 `_NOTE_REREAD_FP_GIT` 加 `_NOTE_REREAD_FP_DIFF_ARGS` 產生,算出的 16 字指紋與 `_note_reread_fp_file` 同一條路。完整 `fp_info`、紀錄比對那一段(`_note_reread_covered`)沒有跑。

severity: major
blocking: 是 — 攻擊者可把已被對照的改動搬到同檔的另一個函式,指紋不變、提醒被當成已對照而放行;在 Java/TS/Kotlin/C 的檔案上一步就成立,Python 的巢狀函式與巢狀類別也成立。
引句:「名字取 def/class/function/func/fn 後面那個」
- 成因:`_NOTE_REREAD_DEF_RE` 只認 `def|class|function|func|fn`。
  - 頂格行沒有這些關鍵字時,退回「取第一個識別字」。
  - 縮排的方法行沒有這些關鍵字時,內層名為空。
  - 縮排方法行如果自己是巢狀 def,只取離 hunk 最近的那個。
- 攻擊步驟:
  1. 守檔筆記的 about_code 列了 `Svc.java`,裡面有兩個 context 相同的方法 `pub` 與 `adm`,都含 `check(u);`。
  2. 第一次推送把 `pub` 裡的 `check(u)` 改成 `allow(u)`,並對照過(指紋 F)。
  3. 之後改成把 `adm` 裡的 `check(u)` 改成 `allow(u)`,`pub` 還原。
  4. 兩版的改動行與上下三行相同,標籤都是 `Svc`,指紋不變。
- 實驗結果(指紋前 16 字,Java 用 `base.java` 逐字複製兩個方法,其餘語言用同樣結構):

| 案例 | 搬動前標籤 | 搬動後標籤 | 搬動前指紋 | 搬動後指紋 |
|---|---|---|---|---|
| Java 兩個方法 `pub` 與 `adm` | `Svc` | `Svc` | `86f30321ad64fa8c` | `86f30321ad64fa8c` |
| Kotlin(寫成 `fun` 方法) | `Svc` | `Svc` | `86f30321ad64fa8c` | `86f30321ad64fa8c` |
| Kotlin 頂層 `fun pub` 與 `fun adm` | `fun` | `fun` | `10279c19af5872e2` | `10279c19af5872e2` |
| C `int pub(...)` 與 `int adm(...)` | `int` | `int` | `fd3b50b3bb0e07eb` | `fd3b50b3bb0e07eb` |
| TypeScript `export class S { pub(){} adm(){} }` | `S` | `S` | `9cc584d2c437f42b` | `9cc584d2c437f42b` |
| Python 同類別 `A` 的 `m1` 與 `m2`,各含一個巢狀 `def helper` | `A/helper` | `A/helper` | `de9b60180d063cd6` | `de9b60180d063cd6` |
| Python 巢狀類別 `A.X.f` 與 `A.Y.f` | `A/f` | `A/f` | `971739001dd7dd9b` | `971739001dd7dd9b` |

  - Python 那兩列的原因:最近的縮排 def 蓋掉了外層方法名(`m1`/`m2`、`X`/`Y`)。
  - 對照組:`def a(): def h` 與 `def b(): def h` 標籤是 `a/h` 與 `b/h`,指紋不同。
  - 對照組:Swift `extension` 裡的 `func pub`/`func adm` 標籤是 `extension/pub` 與 `extension/adm`,指紋不同。
  - 所以 Python 頂層函式、Swift、Go 這類有關鍵字的寫法有效,沒有關鍵字的語言與巢狀寫法沒有。
- 這個專案會碰到的語言:這個專案的守檔筆記會綁 Java、Kotlin、Swift、Dart、TS 等程式(見 skills 清單),所以這不只是理論。
- 修法方向:標籤不要自己猜名字。改成「hunk 所在的縮排鏈」(每一層往上找到的頂格與縮排定義行),或把「離 hunk 最近的頂格行 + 該行到 hunk 之間的行數」算進去。
- file: `scripts/lumos:36237`(`_NOTE_REREAD_DEF_RE`)、`scripts/lumos:36580`(`_note_reread_hunk_tags`,第 36611 行 `i_new` 只取最近一個)

另外查過、沒找到洞的項目:
- **頂格假定義**:要在 hunk 前面放一行頂格的假定義,那行本身會進 diff 並改變指紋。能用的只有 base 裡原本就有的頂格字串行。
- **截斷**:`_note_reread_v2_cut` 判到截斷或 git 失敗都退回 v1,v1 綁 about_code 在頂端的 blob 編號。
- **查大小失敗再配舊版紀錄**:查大小失敗退回 v1 後,舊版紀錄只認同一份 blob 內容,所以沒有繞過空間。
- **屬性檔**:在 `.git/info/attributes` 寫 `* -diff` 會讓 diff 變成「二進位」。實驗中指紋從 `de9b60180d063cd6` 變成 `b17e6af2b4f6713f`,標籤清單變空,指紋會變,不是繞過。
- **環境變數**:`GIT_DIFF_OPTS=-u0` 在 git 2.39 下會蓋過 `-U3`(指紋 `de9b…` 變 `67d06c…`)。這個差異本身會讓指紋與紀錄對不上,所以只能靠自己用同一個環境去記紀錄,不單獨成洞。`_NOTE_REREAD_FP_GIT` 沒有清掉這個環境變數,屬於 minor 的穩定性風險,這輪沒有另列一條。

實驗暫存已刪。最高等級 major,blocking 1 條。
