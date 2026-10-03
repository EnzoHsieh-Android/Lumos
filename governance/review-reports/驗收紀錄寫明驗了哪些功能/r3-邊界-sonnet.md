severity: minor

審查方式:`git clone --shared` 到臨時目錄,用真零件 `parse_frontmatter`、`as_list`、`build_typed_index` 內聯判法(逐行照抄,`scripts/lumos:740-790`)跑了 50 種寫法。沒有 blocking。上輪我列的 10 種形狀都已被新規則收住,只剩下面 4 個 minor。

## F1 單項判法「原樣抽出」會把兩種項默默跳過,混在有效項旁邊時整欄不報
severity: minor
blocking: 否
引句:「從 `build_typed_index` 裡判單項的那段原樣抽出,`build_typed_index` 改呼叫它、行為不變」
file: `scripts/lumos:759-765`(`if not s: continue`、`if not t: continue` 兩處直接略過,沒進 scalars 也沒進 ghosts)

1. 計劃宣稱的四種不合格(不是單一連結、有路徑沒這篇、沒路徑找不到、沒路徑多篇同名)沒有涵蓋這兩條原碼裡的靜默分支:空字串項、以及 target 抽完是空的項。
2. 實測:`- [[|x]]`、`- [[#x]]` 判成「略過」;`- ''` 解析成 `['']`,同樣略過。
3. 只有整欄都是這種項時,才會被「一項合格的都沒有」接住;`[[Systems/A]]` 加一條 `[[#x]]`,後者默默消失,doctor 3/4 不報。這正是計劃自己要消滅的「默默當成沒驗」,只是範圍很窄(要使用者手誤寫出空 target)。
4. 建議:抽出的 `_typed_link_target` 把這兩種回成第五種不合格(「空項」),`build_typed_index` 呼叫端維持原本略過。S5 的「行為不變」測試照舊能綠。

## F2 「沒有 `system_refs` 這個鍵」的判定是字面比對,鍵名打錯或重複時默默退回從正文推
severity: minor
blocking: 否
引句:「沒有 `system_refs` 這個鍵 → 沒宣告,照舊用現行 `n.targets` 落在 `Systems/` 的。」
file: `scripts/lumos:477-525`(`TOP_KEY_RE` 只認行首、冒號緊貼鍵名;重複鍵後者覆蓋前者)

1. 實測:`System_refs:`、`system-refs:`、` system_refs:`(行首多一格)、`system_refs :` 全部讀成沒有這個鍵,等於「沒宣告」,指路連結誤報照舊,使用者以為已經宣告。
2. 實測:同一層寫兩次 `system_refs:`,後者整個蓋掉前者(第一個清單的項全消失),`parse_frontmatter` 只在 lint 吐「欄位名重複」,doctor 3/4 看不到。
3. 緩解:`_KNOWN_FRONTMATTER_KEYS` 的 lint 會對打錯的鍵唸「不認得的欄位」(`scripts/lumos:5742`),所以不是完全無聲,但 doctor 3/4(會擋推送的那關)沒接這條線。
4. 屬既有行為、風險低;建議至少在〈實務隱患〉寫一句「鍵名打錯由 lint 提醒、doctor 不擋」並附回頭條件,不然 RETIRE-IF 第三條(寫壞率)量不到這類。

## F3 「讀不出任何一項」與「不是單一連結」的訊息對幾種常見寫法會指錯方向
severity: minor
blocking: 否
引句:「一項合格的都沒有(空值、空清單、清單項沒縮排而解析成空)」

1. `system_refs: # 待補`(鍵後面接註解,下面才縮排列項):`parse_frontmatter` 把值讀成字串 `# 待補`,下面縮排的真連結整個不讀,結果報一項「不是單一連結:# 待補」。使用者看不出問題是「鍵後面的註解讓清單失效」。
2. `system_refs: ["[[Systems/A]]", "[[Systems/Sub/B]]"]`(行內清單、兩項以上):整串被當一個值,報「不是單一連結」,而 [S4] 的括號寫的是「多個連結」,改法若只叫人「一個連結一項」不夠,要明講「改成一行一項的縮排清單」。
3. `system_refs: null` / `~` 同樣報「不是單一連結」,而不是「空的」。
4. 以上都有報、不默默放行,只是原因文字要設計成對症;建議改法句在標題後印一次時,列出這三種形狀的白話修法。

## F4 裸檔名大小寫不敏感、路徑式大小寫敏感,同一欄混寫時結果不一致
severity: minor
blocking: 否
引句:「`[[systems/A]]` 大小寫寫錯、`[[sub/B]]` 部分路徑、功能筆記搬資料夾後的舊路徑,在這裡跟在那兩個欄位裡一樣算壞連結」
file: `scripts/lumos:762-776`(路徑式用 `cand in env.notes` 精確比對;裸名用 `by_stem.get(tt.lower())`)

1. 實測:`[[systems/A]]` → 壞(有路徑但沒這篇);`[[foo bar]]` 對 `Systems/Foo Bar.md` → 合格;`[[./Systems/A]]`、`[[/Systems/A]]` → 壞;`[[Systems\A]]`(反斜線)→ 當裸名找不到,報「找不到」而不是「路徑寫法錯」。
2. 計劃已承認與既有欄位一致,算誠實;但〈實務隱患〉只列了大小寫與部分路徑兩種,沒列 `./`、前導 `/`、反斜線,訊息的「改法」要讓人看得出該寫成 `Systems/<檔名>`。

## 看過沒問題(逐項對照上輪我列的形狀)

- 帶引號 `"[[Systems/A]]"`、`'[[Systems/A]]'`:`parse_frontmatter` 先去引號,合格。
- 帶 `.md`、別名 `|別名`、`#段`:都抽到 `Systems/A.md`,合格。
- 子資料夾 `Systems/Sub/B` 合格;`[[B]]` 裸名唯一時合格;`[[Sub/B]]` 部分路徑壞,訊息為「有路徑但沒這篇」,正確。
- 行尾註解 `[[Systems/A]] # 註解`、行尾多一句、全形括號 `【【…】】`、相鄰兩連結:都判「不是單一連結」,有報。
- 單項行內清單 `system_refs: [[Systems/A]]`:`as_list` 包成一項,合格(與計劃「照既有規則」一致)。
- 區塊寫法 `|`:進 `block_keys`,計劃寫「整欄一項寫壞」,對得上。
- 空值、`[]`、`""`、沒縮排、tab 縮排、空項 `-`:全解析成空或只剩空字串,都會落到「讀不出任何一項」。
- 同名多篇 `[[dup]]`、`[[A]]`(Projects/A 與 Systems/A 同名):判不明確,有報,計劃上輪「落在別的資料夾」的特例已拿掉、統一走不明確,更簡單。
- 效能:每項一次字典查表,20 項封頂,沒有二次方問題。

最高等級:minor,blocking 共 0 條
