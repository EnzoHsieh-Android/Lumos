severity: major

## F31 Kotlin 讀清單的起頭錨點 `^` 被拿掉,測試照綠
severity: major
blocking: 是
歸因:有證據的原有漏查(修前 `Regex("\"files\"\\s*:\\s*\\[").find(text)` 也是在任意位置找 files,而且沒有任何行為測試;修後新測試沒覆蓋起頭錨點)。
引句:「'{"meta": {"files": ["a.kt"]}}', '{"files": ["a\\u0041.kt"]}', '{"files": ["a\x01.kt"]}',」
佐證: file: `scripts/templates/android-arch-target.md`(`val legacyDoc = Regex("""^[ \t\r\n]*\{…`)
失敗場景:
1. 把 `legacyDoc` 的開頭 `^` 刪掉,產出的 Kotlin 就會接受 `x{"files": ["a.kt"]}` 這類前面有雜字的清單。
2. lumos 用標準 JSON 讀同一份檔,會判讀不懂,清單整份不起作用、全部照目標審。架構測試卻照讀並跳過舊檔,兩邊結果相反,正是這次修補宣稱不會再發生的分岔。
3. `must_reject` 與 `must_read` 都沒有「起頭有雜字」的輸入。巢狀那條 `{"meta": {"files": …}}` 被結尾的 `}$` 擋掉,擋不到起頭錨點。

最小重現(在修後提交的臨時工作樹上跑):
- 未改壞:`python3.14 scripts/test_lumos.py -k konsist_legacy_shape` 得 16 passed, 0 failed。
- 改壞:把資料檔 `Regex("""^[ ` 改成 `Regex("""[ `,再跑同一指令,仍是 16 passed, 0 failed。
- 對照:改壞版的正規式對 `x{"files": ["a.kt"]}` 在 Python 回傳有比中。
- 對照:刪掉 `$` 的同類改壞會讓測試翻紅(2 failed)。結尾錨點有被守住,起頭錨點沒有。

同一案例前後:修前沒有行為測試可跑(只比對原文),未判定。修後測試對這個改壞照綠。

## F32 註解宣稱「Java 與 Python 語法同義」,但 `$` 不同義,Kotlin 比 lumos 寬
severity: minor
blocking: 否
歸因:有證據的修復回歸(「只會比 lumos 嚴」是這次修補新寫下的保證)。
引句:「Kotlin 讀得進去的,標準 JSON 也讀得進去而且讀出同一份(只會比 lumos 嚴、不會比它寬)」
佐證: file: `scripts/templates/android-arch-target.md`(`legacyDoc` 結尾 `[ \t\r\n]*$`)
失敗場景:
1. 清單檔尾端是 U+2028、U+0085 或 U+2029,例如 `{"files": ["a.kt"]}` 後面接 `\u2028`。
2. Java 的 `$` 預設會在最後一個行終止符前匹配,Python 的 `$` 只認 `\n`。
3. 在本機 JDK 17 實跑:這三個字元結尾都回 true,Python 回 False,`json.loads` 判讀不懂。
4. 結果是 Kotlin 照讀、lumos 判讀不懂,跟 F31 同一種分岔。因為測試在 Python 裡跑,抓不到這個 Java 與 Python 的差異。
5. 文件〈Systems/android-arch-template〉那句「反過來的『lumos 判讀不懂、架構測試照讀』不會發生」因此不成立。
6. 實際觸發條件很窄(要有人手動在檔尾加這類字元),所以只標 minor。

同一案例前後:修前的手寫讀法對檔尾雜字不檢查,同樣偏寬(未實跑,從原文推讀)。修後仍偏寬,範圍縮小。

## F33 BOM 的「讀得進去」由測試端自己剝掉,Kotlin 的 `removePrefix` 被拿掉也照綠
severity: minor
blocking: 否
歸因:未判定(修前沒有行為測試,無法比較;修後缺口已用改壞實證)。
引句:「m = doc.search(text.removeprefix("\ufeff"))」
佐證: file: `scripts/templates/android-arch-target.md`(`val text = f.readText(Charsets.UTF_8).removePrefix("\uFEFF")`)
失敗場景:
1. 刪掉 Kotlin 的 `.removePrefix("\uFEFF")`:`python3.14 scripts/test_lumos.py -k arch_template_android` 得 88 passed, 0 failed。
2. 檢查標題宣稱 BOM 的清單「Kotlin 都讀得進去」,實際上 BOM 是測試端剝的,同理 NFC 也是測試端的 `unicodedata.normalize`。這兩項不是從 Kotlin 原文抽出來的行為。
3. 帶 BOM 的清單(lumos 容許)在 Kotlin 端會讓架構測試紅。方向是偏嚴、可被看見,所以只標 minor。
4. NFC 那半有 `.map { nfc(it.groupValues[1]) }` 的原文檢查釘著。BOM 那半沒有任何釘住。

## 三問與正向主張證據

**①原問題的修復效果有何行為證據?**
- 案例 H1(Kotlin 比 lumos 寬):
  - claim:尾逗號、前逗號、少逗號、少括號、多欄位、巢狀、跳脫、控制字元、非字串、不換行空白、尾巴多字,Kotlin 都不認。
  - input:`must_reject` 十六條。
  - expected:讀出 None。
  - case_source:r2-intake 的 H1 repair 清單。
  - before:手寫讀法,只比對原文,無行為證據,未判定。
  - after:在 Python 以抽出的正規式跑。我把 `$` 刪掉的改壞版翻紅(2 failed),原版 16 passed。
  - comparison:成立,但有 F31 與 F32 兩個漏洞。
- 案例 H2(清單收檔跟 Konsist 掃描分岔):
  - claim:`src/main/java/mysrc/test/Q.kt` 在清單上,`src/integrationTest/...` 在清單上,`src/test` 與 `.md` 不在。
  - 我沒有另跑修前版,修前紅的證據只有作者在 r2-repro.txt 的說法,未判定。
  - after:`-k arch_template_android` 全跑,88 passed, 0 failed(含 `legacy_modes`)。
  - 我推演的 `_ARCH_TPL_KONSIST_TEST_RE` 變體(只留 `src/test/`)其實與原版等價,因為 `_PITFALL_DIFF_TEST_PAT` 已把其他測試目錄判成程式檔。因此「對照判準獨立」只成立一半:oracle 的正規式是同一條的複本,但差異點被 `_arch_code_file` 吸收,不構成缺口。
- H3(dataSuffixes 斷言):已看到 `dataSuffixes.any { type.endsWith(it) }` 的原文釘住。我沒對它做改壞實驗,未判定。
- H4(文件):S1 與 S3 條款句與 `t_arch_target_android_template_valid`、`t_arch_target_android_template_konsist_names_match` 的實際判準一致:十二條、無過期、無佔位、`defined == bound | 慣例`。技能文件新增「all 改成 new-only」那條操作可行(`--print legacy` 為預覽,存檔路徑在採用步驟已有)。

**②修補處的正常、錯誤與相鄰路徑是否仍成立?**
- 正常路徑:
  - claim:產生器寫出的清單,產出的 Kotlin 讀得進去且讀出同一份。
  - input:`legacy_modes` 內 `reader(out) == set(want)`。
  - after:通過。
- 錯誤路徑:
  - claim:雙引號、反斜線、控制字元檔名被拒絕。
  - after:`legacy_modes` 通過。
- 相鄰路徑:`all` 產出不讀清單,測試通過。
- 未驗範圍:Kotlin 實際編譯與 Gradle 實跑(環境沒有 kotlinc),驗證紀錄的實跑敘述只能引用,無法重現。

**③新發現的同一案例在修前、修後各是什麼結果?**
- F31:修前沒有行為測試,無法比較;修後對這個改壞照綠。
- F32:修前同樣偏寬(推讀),修後偏寬範圍縮小;實跑只在修後。
- F33:修前沒有行為測試;修後對這個改壞照綠。
- 歸因:三條都不是「有證據的修復回歸」中由修補製造的新缺陷,除了 F32 的保證文字是修補新寫的。

## 圖譜鏡頭固定席判定

- `lumos-cli-read`、`lumos-cli-lifecycle`、`guard-kill`、`bound-tests-gate`、`授權與歸屬`、`design-loop`:這份 diff 沒有動這些合約宣稱的行為。
  - 新增的是 `cmd_arch_template`、`_arch_tpl_*` 與測試,不碰 search、re-inject、guard kill、授權白名單。
  - 授權與歸屬那條要求被複製的檔至少有 SPDX 註解行。新增的 `scripts/templates/android-arch-target.md` 是否登記進工具自帶檔清單、是否有 SPDX,屬於主程式與資料檔那席,這席未驗。
- `測試假綠形態` 的 INVARIANT:修 bug 的還原翻紅釘要配前置斷言證明現場成立。
  - 本次的 `前置:產出的 Kotlin 抽得到兩條讀清單的正規式` 與 `前置:預設組十二條規則、九支測試` 符合要求。
  - 但 F31 與 F33 顯示行為釘的輸入集不完整,這條不變量沒被破壞,只是覆蓋面不足。
- `pitfalls-code-loop`、`arch-alignment-lens`、其餘只列名的節點:內容未逐篇展開,未判定是否被破壞。這份 diff 對 `arch-alignment-lens` 的指路句沒有改動。

總結:共 3 條。
