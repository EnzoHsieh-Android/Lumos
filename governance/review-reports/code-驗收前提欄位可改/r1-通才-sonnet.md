severity: major

## F1 值裡的「空白+#」會被真 YAML 讀成註解,悄悄截斷整條前提
severity: major
blocking: yes
引句:「if fmt_scalar(key, v) == v and not re.match(r"-(\s|$)", v):」

重現步驟:
1. 在暫存圖譜建一篇 Verification 筆記,`valid_under: 舊前提`。
2. 執行 `python3 scripts/lumos --vault <暫存圖譜> set V valid_under '含 # 井字號的條件 #not-a-comment'`,rc=0,寫入成功,`lumos lint` 也是 0 error。
3. 用真正的 YAML 解析器讀同一段 frontmatter(`pip install pyyaml`):
   ```
   yaml.safe_load(...) == {'valid_under': '含', ...}
   ```
   整條前提在第一個「空白+#」處被截斷成「含」,後面全部消失。

原因:`_fmt_cond` 判斷要不要加引號,直接沿用 `fmt_scalar` 的規則——只檢查「開頭」是不是 `[{>|*&!#@`」,不檢查值「中間」有沒有「空白+#」。可是標準 YAML(含 Obsidian 用的 js-yaml)規定:純量裡「空白後接 #」就是註解起點,不管在字串中間還是開頭。lumos 自己的 `parse_frontmatter` 是自製的極簡 parser,不認得這條規則,所以 `atomic_write_verify` 的「寫完讀回來比對」自驗完全抓不到——它拿同一支不合規的 parser 驗自己,兩邊一起錯,才會兩手一攤放行。

為什麼算數:valid_under/revalidate_when 就是設計來給人寫長篇前提用的散文欄位(spec 開頭就寫「另一個代理複製 lumos 到 /tmp 繞過規則」,顯然是常態使用),而中文/技術寫作提到「issue #123」「井字號」「hashtag」的機率遠高於既有那批純量欄位(status/type 這種短列舉字)。一旦命中,Obsidian 開起來看到的前提是被腰斬過的殘句,而且沒有任何 lint/doctor 警訊——這正是任務指名要查的「寫出來的東西標準 YAML(例如 Obsidian)讀不讀得了」。

建議修法:`_fmt_cond` 的加引號判斷再補一條「值中間含 `\s#`(前面有空白的 #)就要加引號」,和目前已經有的「開頭是 `-` 」判斷同一個位置補。

## F2 值裡有反斜線接常見字母(如 \n、\t)被雙引號包住卻沒轉義,真 YAML 會解讀成換行,悄悄把單行前提拆成多行
severity: major
blocking: yes
引句:「return '"' + v + '"'」

重現步驟:
1. 同一篇筆記,執行(bash `$''` 語法,值裡是字面上的一個反斜線加英文字母 n,不是真的換行):
   ```
   python3 scripts/lumos --vault <暫存圖譜> set V valid_under $'路徑: C:\\\\Users\\\\test\\n檢查點'
   ```
   rc=0,`lumos lint`/自驗都過,寫出來的檔是:
   ```
   valid_under: "路徑: C:\\Users\\test\n檢查點"
   ```
2. 用 PyYAML 讀回:
   ```python
   yaml.safe_load(...)['valid_under'] == '路徑: C:\\Users\\test\n檢查點'
   ```
   (Python repr 裡單一 `\n` 代表真正的換行字元)——也就是說,真的 YAML 讀出來這條前提被硬生生插入一個換行,變成兩行文字。

原因:`_fmt_cond` 需要加雙引號時只把值原封不動包進 `"..."`(`'"' + v + '"'`),沒有把值裡既有的反斜線(`\`)先跳脫成 `\\`。標準 YAML 的雙引號純量會解讀反斜線跳脫(`\n`→換行、`\t`→tab、`\"`→引號…),lumos 自己的 `parse_frontmatter`/`strip_quotes` 完全不解跳脫,所以自驗讀回來字串沒變、覺得沒事,但 Obsidian 或任何標準 YAML 工具讀到的是「多行」。這直接違反本計劃自己定的合約([S3]「一條條件只能一行」)——只是違反的是「別人怎麼讀」而不是「lumos 自己怎麼讀」,自驗機制天生看不到。

為什麼算數:valid_under/revalidate_when 是自由散文,提到 Windows 路徑、regex、或單純打「請看 \n 這個逸出字元」都會踩到;而且這是任務明講要測的「值裡有引號」情境延伸(加引號分支本身就沒做完整)。

備註:這兩個 bug 的根因(`fmt_scalar` 的引號規則本身)在其他既有純量欄位(如 `responsibility`)理論上也存在同樣缺口,不是這次 diff 新引入的通病;但這次新增的 `set valid_under/revalidate_when` 明確鼓勵寫長篇散文,把原本很少被踩到的邊界變成常態可觸發,而且是這次審查明確要求驗的「標準 YAML 讀不讀得了」項目,所以列為本次審查的真發現。

---

已看,無:
- S1–S5 五條條款各自的專屬測試(`t_set_condition_fields_replace_any_shape`/`multi_values`/`reject_bad_values`/`t_set_other_keys_single_value_only`/`keep_other_lines`)全部實際執行過,29+3 案例皆綠;用「拆修法」的方式驗過兩顆 mutation(拿掉 `_fmt_cond` 的破折號判斷、把 `_set_conditions_locked` 的整段替換改成插入不刪舊區塊),兩次都讓對應測試翻紅,證明測試真的接得住這兩類 bug。
- 四種原本寫法(單行、清單、空的、多行區塊)以及「完全沒這欄」共五種起始狀態,整欄替換後開頭其他欄位與正文都逐字保留,已用內建測試 + 手動建構「沒有 tags/沒有其他清單欄位」「valid_under 是 frontmatter 最後一行、緊接 `---`」等額外案例覆蓋,皆正確。
- 給多個值時清單縮排、順序、含冒號/方括號開頭/wikilink/破折號開頭的值都能正確加引號並讀回原字;wikilink 夾在散文中間(非整值)不會被誤判成邊,跟既有的 `_SINGLE_WIKILINK_RE.fullmatch` 索引規則行為一致,沒有因為新寫法而多長出 ghost 邊。
- 值同時含單引號與雙引號、又需要加引號時,正確擋下且訊息講清楚、檔案不動;只含其中一種引號時能正確挑另一種包住並讀回原字。
- 空值、只有空白、含換行(含「多個值裡有一個空的」)都被擋下且檔案不變,錯誤訊息分辨「不能是空的」跟「只能一行」兩種原因。
- 其他欄位(以 `status` 為例)給兩個以上值會被擋、檔案不動;只給一個值行為與改動前完全一致——讀了 `main()` 裡 `set`/`append`/`remove` 三個子命令的 argparse 設定,確認只有 `set` 的 `value` 改成 `nargs="+"`,`append`/`remove` 沒被牽動;也讀了程式裡所有直接呼叫 `cmd_set(...)` 的既有呼叫點(signed_off、status pass/abandoned、self_audit、about_code_stamp、responsibility 共 7 處),全部都傳單一字串(非 list),進到 `_cmd_set_locked` 時 `isinstance(value, list)` 為 False,直接跳過新加的「給多個值就擋」那段,行為與改動前一致,沒有被誤傷。
- `cmd_remove`/`_cmd_remove_scalar` 對 `valid_under`/`revalidate_when` 的行為改動前後一致(兩者都不在 `LIST_KEYS`,`_cmd_remove_scalar` 檢查的是 `SCALAR_KEYS` 而非新的 `COND_KEYS`,所以「不給 append/remove 動這兩欄」這條「不做的」清單真的守住了,沒有意外開後門)。
- 另外測了「參數本身是 `---`/`-a`/`-x` 這類容易被 argparse 誤判成選項的值」——確認會在 argparse 層直接失敗;但用同一份 argparse 設定比對 `nargs=None`(改動前的單值寫法)一樣會失敗,證明這是 argparse 既有共通行為(只要值裡沒有空白、開頭是連續破折號就會踩到),不是這次把 `value` 改成 `nargs="+"` 新引入的問題,故不列為本次發現。
- `COND_KEYS` 沒有被併進 `SCALAR_KEYS`,沒有影響到唯一依賴 `SCALAR_KEYS` 數量做斷言的測試(`t_...⑤純量白名單有 responsibility`,只斷言成員存在,不斷言總數)。
