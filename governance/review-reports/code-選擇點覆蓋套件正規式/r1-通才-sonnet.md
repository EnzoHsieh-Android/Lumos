severity: minor

**發現一:package 與名字之間換行,新寫法會讀不到**

severity: minor
blocking: 否
`scripts/lumos:79994`(diff 第 43 行):

引句:「+    m = re.search(r"^[ \t]*package[ \t]+([\w.]+)", text, re.M)」

- 舊的 `\s+` 可以跨行,新的 `[ \t]+` 不行。
- 我用 `package\na.b\n` 實測:舊寫法讀到 `a.b`,新寫法讀到 None,`pkg` 變成 `""`。
- Kotlin 語法允許這種寫法,但實務上極少見。
- 後果:`pkg` 退成預設套件。這個改動檔的套件仍會經由 `scripts/lumos:29146` 的聯集,由 `_choice_cov_src_pkgs` 補進專案類別,所以多半不會判錯。
- 只有這支檔的 `req["pkg"]` 值變成 `""`,沒有其他連動。
- 風險很低,屬措辭層級的行為差異。

**發現二:該不該改用共用的 `_CHOICE_COV_PKG_RE`**

severity: minor
blocking: 否
`scripts/lumos:79799` 有 `_CHOICE_COV_PKG_RE = re.compile(r"^[ \t\ufeff]*package[ \t]+([\w.`]+)", re.M)`,`_choice_cov_src_pkgs` 在用。

- 它能處理檔首 BOM 和反引號套件名。
- `_choice_cov_req` 用 `read_text(encoding="utf-8")` 讀檔,不會去掉 BOM。我實測 `\ufeffpackage a.b` 和 `` package `a.b` `` 在新舊兩種寫法下都是 None,所以這不是這次改動造成的退步。
- 同一個檔在兩處算出不同的 pkg:`_choice_cov_src_pkgs` 得到 `a/b`,`_choice_cov_req` 得到 `""`。
- 後果:`scripts/lumos:29146` 的 `pkgs` 聯集裡多一個 `""`。
- 這會把預設套件的類別也算成專案類別,方向是偏寬鬆,不會漏判。
- 建議直接用 `_CHOICE_COV_PKG_RE.search(text)`,再把反引號去掉。
- 這樣一次解決 BOM、反引號、規則重複三件事,也不會碰到全檔守衛(它已經用 `[ \t]`)。
- 重複定義正則是這次「沒照鄰居」才會被守衛擋紅的同一類疏漏,所以建議共用。

**其他確認**
- 新舊兩種寫法對 `/* ... package x.y ... */` 區塊註解內獨立一行的 `package` 都會誤抓;這是舊有行為,沒有退步。
- 圖譜 PITFALL 那行寫的是 `[test:t_no_multiline_caret_whitespace_star]`,屬全檔守衛。針對 `_choice_cov_req` 本身沒有專屬測試能抓到 BOM、反引號或換行的差異,我只查了讀取程式碼,沒有執行該測試。

總結:最高等級是 minor
