# 判讀準則 v2:kt-loadurl-external(外部網址沒驗就丟進 WebView)

凍結於 2026-11-08,看第二份語料之前寫定;雜湊在 judge-loadurl-v2.sha.txt。跟 v1(judge-criteria.md)的差別只有下面四點,其餘照 v1。

依據:Android 官方 unsafe URI loading 風險頁(https://developer.android.com/privacy-and-security/risks/unsafe-uri-loading):從外部 Intent 拿到的網址沒驗 scheme、host 就載入,攻擊者能讓 WebView 開任意網頁。

每處看前後文(必要時打開原檔),並看同目錄的 manifest-<序號>.txt(這個 repo 所有 AndroidManifest.xml 的內容,抓不到就寫「無」)。判 TP / FP / UNSURE:

- TP:正式碼,Intent 帶進來的網址(getStringExtra、intent.data、dataString 等)沒驗 scheme、host 就 loadUrl,而且那個畫面**對外開放**:manifest 裡這個 Activity 有 `android:exported="true"`,或帶 intent-filter 且沒寫 exported="false"。
- FP,理由欄開頭寫「FP型:<型>;」:
  - 不對外開放:manifest 找得到這個 Activity,而且 exported="false"、或沒有 intent-filter 也沒寫 exported(Android 預設不開放)。網址只能從 App 自己的畫面傳進來。
  - 已防護:別處驗了 scheme、host 或白名單。
  - 可信來源:網址不是外部 Intent 帶的整條網址(例:只帶路徑片段、App 內部廣播)。
  - 測試或範例碼:**只看檔案路徑**有 test、sample、demo、example、tutorial 這類目錄或模組名;repo 名不算(消費專案是正式 App,repo 名不會是這種訊號)。
- UNSURE:manifest 抓不到、或找不到這個 Activity 的宣告(例如 Activity 名對不上、用了別名),看不出開不開放;寫明缺什麼。

另外兩條由編排者在抽樣前做,判讀員不用管:①repo 名或路徑帶 insecure、vulnerab、vuln、goat、damn、ctf、owasp、testdata、sast 的(刻意寫弱的資安教材、掃描器測試語料)不進抽樣;②同一份程式複製到不同 repo 的(同檔名、前後文去掉空白後相同)只抽一處。

輸出:TSV,每處一列:序號<TAB>檔:行<TAB>TP|FP|UNSURE<TAB>理由(一句;TP 要寫 manifest 哪一行證明對外開放)。最後一列總計(TP、FP、UNSURE 各幾,FP 各型各幾)。
