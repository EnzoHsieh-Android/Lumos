severity: minor

修補確實達成了主要目標。`_choice_cov_src_pkgs` 與 `_choice_cov_req` 現在共用 `_choice_cov_pkg_of`,帶 BOM 的檔兩邊讀出的值相同。換行、縮排、沒有宣告這幾案我讀程式推論過,沒有實際跑測試。以下是修補沒蓋到的殘留差異與新引入的風險。

severity: minor
blocking: 否
`scripts/lumos:79840` 對 `scripts/lumos:80000`:共用函式,但輸入範圍不同。掃主程式套件只讀檔頭 `_CHOICE_COV_SRC_HEAD`(8192 位元組),壞法行那邊讀整份檔。
失敗場景:檔頭有超過 8KB 的授權或 KDoc 註解、`package` 宣告在 8192 位元組之後,掃描端得 `""`(預設套件),壞法行端得 `a/b`。這跟修補要消除的「兩邊對同一支檔讀出不同值」是同一類不一致。
另一個場景:`package` 剛好跨過 8192 邊界,掃描端會收到被截斷的套件名,例如 `com/exa`。
test 用的檔很短,沒有覆蓋到這一點。
引句:「掃主程式套件與壞法行的套件共用這一支,兩邊對同一支檔讀出的值一定相同」
這句「一定相同」的註解與筆記對輸入範圍不成立。

severity: minor
blocking: 否
`scripts/lumos:79799`:`package` 後的空白放寬成 `[ \t\r\n]+` 之後,誤判面變大了一點。
失敗場景:註解或原始字串裡出現獨占一行的 `package`,下一行是別的字,例如:

```
/*
package
manager notes
*/
```

會把 `manager` 當成套件。
舊的 `[ \t]+` 要求同一行有名字,不會中這一案。
`^[ \t\ufeff]*` 不吃 `*`,所以 KDoc 的 ` * package` 行不受影響。
`packageName` 這類識別字因為要求空白也不受影響。
實際發生機率很低,只是放寬換行確實比修補前多一個誤抓路徑。
引句:「_CHOICE_COV_PKG_RE = re.compile(r"^[ \t\ufeff]*package[ \t\r\n]+([\w.`]+)", re.M)」

severity: minor
blocking: 否
`scripts/lumos:79799`:Kotlin 的 `package a.\n b` 這種在 `.` 後換行、或 `.` 與名字之間有空白的寫法仍然讀不到。
註解宣稱「照 Kotlin 文法」,但只放寬了 `package` 關鍵字後面那一處。
這個寫法極少見,屬措辭精度問題。
引句:「Kotlin 文法 packageHeader」

總結:最高等級是 minor
