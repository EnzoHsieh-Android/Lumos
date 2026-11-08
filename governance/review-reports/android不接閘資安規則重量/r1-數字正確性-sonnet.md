severity: minor

固定席(Systems/kotlin規則包):這份設計不影響該節點宣稱的行為或合約。它只改型錄文字與圖譜筆記,不動規則檔和 `rules/` 的擋閘範圍,節點掛 0 條合約、0 行 KEY,沒有東西可被破壞。

## 重算結果摘要

數字格我全部重算過,都對得上:
- 〈實驗〉表的檔數等於 corpus tsv 列數:608、511、290、266、509、480、328。
- 命中與 repo 數等於 hits json 的筆數和首段 repo 去重:428(240)、190(153)、111(72)、21(20)、25(11)、14(6)、8(4)。
- 判讀數等於 sample 行數:40、40、40、21、25。
- 誤報與判不準是逐列數 judge 原文:
  - TLS TP 29、FP 11,分項 3+1+4+2+1=11。
  - loadurl TP 32、FP 8,分項是範例碼 6、可信來源 2。
  - cmd TP 8、FP 30、UNSURE 2,分項 22+5+2+1=30。
  - provider TP 12、FP 8、UNSURE 1。
  - db TP 21、FP 4。
- 百分比:27.5%、20%、80%、42.86% 寫成 43%、16%,全對。
- 抽樣的 repo 都沒落在 `excl-repos.txt`(3796 行)。三條「抽 40」的 sample 都是 40 個不同 repo,且全部在 hits 內。
- 我另用 ast-grep 0.51.1 對語料原檔重跑,7 條規則的命中與 repo 數完全重現。重跑命令:`ast-grep scan -c sgconfig-unwired.yml --filter '^&lt;id&gt;$' --json=stream &lt;corpus 目錄&gt;`。結果:TLS 428/240、loadurl 190/153、cmd 111/72、provider 21/20、db 25/11、secret 14/6、cipher 8/4。
- 型錄 7 列補句與表、卷證一致。
- 〈範圍〉2 那 12 條的原數字與型錄和前兩批計劃一致,條數也對得上:第二批 15 條 = 重量 5 + 不重量 10,10 條加 webview-debugging 和 jackson = 12,3+15+1 = 19。
- 前兩批計劃的補註與結案數字(5 條、2 條、20%/80%/43%/16%)和本計劃一致。

## Finding 1
severity: minor
blocking: 否

判準:〈範圍〉2 對 kt-weak-key-size 的誤報原因說法,要和卷證 judge 原文一致。

spec 段落:〈範圍〉2 第二個子項。
引句:「誤報來自測試用假憑證這類形狀分不出的寫法。」

問題:這句與第二批卷證不符。
- 樣本外那 6 處的 4 處誤報,原因是 Minecraft 協定強制 1024 位元 RSA 2 處、區塊鏈教學筆記練習 2 處。
- 「測試用假憑證」那一筆(android__keyattestation 的 testing 目錄)是樣本內的 1 處誤報,不在樣本外 4 處裡。
- 換句話說,樣本外 4 處誤報其實屬於「外部協定強制、範例碼」,與上面 10 條同一型。把它單獨拆出來的理由,應改成「命中只有 6 處,量不夠」,不是「原因不同」。
- 型錄 DATA-91 那列只寫「樣本外 6 處誤報 4」,沒有原因,所以不矛盾。錯只在本計劃這一句。

佐證:
```
file: `governance/review-reports/android資安靜態檢查補齊第二批/experiment/judge-oos.tsv`
grep -P "^kt-weak-key-size" judge-oos.tsv
```
結果:4 筆 FP 是「外部協定強制」×2 加「測試或範例碼;區塊鏈教學筆記練習」×2。含「testing 目錄假憑證」的那筆在 `judge-insample.tsv`。

## Finding 2
severity: minor
blocking: 否

判準:〈範圍〉1 對分組前提的敘述,要與型錄和前兩批計劃的既有數字一致。

spec 段落:〈範圍〉1 標題括號。
引句:「命中不到 20 或沒量過樣本外,形狀本身誤報不高」

問題:這句對 7 條裡的 2 條不成立,而且這個前提正是「為什麼只重量這 7 條」的理由。
- kt-weak-cipher-suite:型錄 API-50 與第二批表寫「樣本內抽判 40 處誤報 33」,即 82%(第二批表:「0%(樣本內 82%)」)。
- kt-command-exec-nonliteral:收窄前樣本外 55 處抽判 40 處誤報 28(70%),這次又量到 80%。
- 這兩條的誤報本來就高。「只因命中不夠才沒升」的因果對它們不成立,而這次實驗的結果也正好證明誤報高。
- 結論(維持不接閘)不受影響。但〈範圍〉1 的前提與〈天花板〉都沒提這點,讀者會以為 cipher-suite 只差命中數。
- 建議把括號改成「(命中不到 20 或沒量過樣本外;cipher-suite、cmd 兩條形狀本身誤報已高,見型錄)」。

佐證:
```
file: `skills/kotlin-idioms/checks-catalog.md:202`
```
該列寫「樣本內抽判 40 處誤報 33(模仿舊版 TLS 指紋這類外部協定強制)」。
```
file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:126`
```
該列寫「kt-command-exec-nonliteral | 55/40/28 | 70.0%(收窄前)」。

## Finding 3
severity: minor
blocking: 否

判準:表中「命中」「全判」的「處」要有一致且可驗的口徑。

spec 段落:〈實驗〉表。
引句:「| kt-provider-openfile-traversal | 266 | 21(20) | 全判 21 | 8,判不準 1(43%) | 不接閘 |」

問題:「處」的口徑不一致,有兩處。
- provider 的 21 筆 hits 裡 `StickerContentProvider.kt:83` 出現兩次,即同檔同行只算 20 個位置。
  - sample 檔因此有兩列相同。
  - judge 也對同一處判了兩次 TP,第二列理由寫「與上一列同一處(重複區塊)」。
  - 去重後是 20 處、誤報加判不準 9,即 9/20 = 45%,不是 43%。
  - 〈天花板〉只提到資料庫那條樣本不獨立,沒提這條。
- TLS 的 428 筆命中中,有 66 組同檔同行重複(共多出 67 筆),獨立的檔加行位置是 361 處。
  - 最多一行被報 3 次(`Dynasty.kt:46`)。
  - 結論都不變(≥20 都成立),但「428 處」是 ast-grep 的比對數,不是 428 個位置。
  - S2 預期值表直接引用「428 處」,應在表頭說明「命中=比對筆數」。

佐證:
```
python3 -c "import json,collections;d=json.load(open('hits-kt-insecure-tls-version.json'));c=collections.Counter(map(tuple,d));print(len(d),len(c),sum(v-1 for v in c.values()))"
```
輸出:`428 361 67`。
```
grep -n Pinterest judge-provider-db.md sample-kt-provider-openfile-traversal.txt
```
輸出:同一檔同行 83 各出現兩列。

## Finding 4
severity: minor
blocking: 否

判準:宣稱「可重現」的步驟,卷證裡要有重現所需的東西。

spec 段落:〈用詞〉「抽 40 處」。
引句:「用固定隨機種子(任意選的固定數,讓抽法可重現)抽 40 處」

問題:卷證 `experiment/` 裡只有 sample 結果檔,沒有抽樣腳本或抽法描述。
- 我用 `random.Random(20261111)` 試了三種常見抽法(先對 repo 抽再每 repo 挑一處、先每 repo 挑一處再抽 repo 等),都無法重現 TLS 那 40 處。
- 所以「讓抽法可重現」目前是空話。第二批計劃把腳本存卷證,本批沒有照做。
- 影響不大,因為 sample 檔本身已列出抽到哪 40 處,判讀可核。但這和 PRIOR-ART 引的 Dwork 保留集精神(抽法不可事後調整)有關,至少要把腳本或一句抽法補進卷證。

佐證:`ls experiment/` 沒有任何 `.py`、`.sh` 或 `.txt` 腳本。我試的三種抽法與 sample-kt-insecure-tls-version.txt 的交集都是 0。

## Finding 5
severity: minor
blocking: 否

判準:分組理由的列舉要涵蓋組內每一條的實際原因。

spec 段落:〈範圍〉2 第一子項。
引句:「誤報來自形狀分不出正當用法(外部協定強制、可信來源、範例碼)」

問題:括號列的三種原因沒涵蓋組內兩條。
- kt-webview-debugging-enabled:型錄寫的原因是「用 FLAG_DEBUGGABLE、別名旗標判除錯版」,是形狀沒認出另一種正當的除錯判法,不屬於這三類。
- kt-hardcoded-secret-name:judge 的 FP 型包含「非秘密」,也不在這三類內。
- 這兩條的結論(要改善得先改形狀)仍成立,甚至更貼切,因為它們根本是形狀要改。
- 建議括號末尾加「等」,或補列「除錯判法沒認出、非秘密」。

佐證:
```
file: `skills/kotlin-idioms/checks-catalog.md`
```
grep 該列「樣本外 42 處誤報 16(用 FLAG_DEBUGGABLE、別名旗標判除錯版)」。
```
file: `docs/lumos-toolchain-knowledge/Projects/Android資安與崩潰靜態檢查補齊_計劃.md:67`
```
該處寫「除錯旗標那條誤報 38% 是形狀問題」。

## 實務隱患(此功能碰的風險類)

- 金流:無。只改型錄文字與筆記,不碰付款。
- 對外送出:無。語料下載只在實驗階段,repo 內沒有對外呼叫。
- 不可逆:無。全是文字檔,退回提交即還原。
- 守衛面:無。規則檔與 `rules/` 沒動,推送前行為不變。我另核對了 `rules-unwired/` 的規則 id,資安類剛好 19 條,與「19 條」吻合,這類規則沒有被誤搬進 `rules/`。
- 併發寫入:無。單人、AI 依序操作,與 spec 自述一致。

## 已讀,無 finding

- 〈用詞〉其餘條目。
- 〈依據來源〉。
- 〈回退〉。
- 〈驗收條款〉S1、S2:S2 的預期值 428 處抽判 40 處誤報 11 與 judge、hits 一致。
- 〈範圍〉3、〈範圍〉4:第二批與第一批的補註數字均與本計劃一致。
- 〈天花板〉:「資料庫那條真問題有 12 處來自同一個 repo」已核實,是 Winnie0408__LocalMusicHelper 12 處;「11 個 repo 裡誤報 3」也已核實,誤報分佈在 jide、JLPT-Mitsuki、UnitTestDemo 三個 repo。

## 我建過的路徑

沒有建任何檔案或目錄,所有重算都用 stdin 腳本或只讀命令完成。

最高等級 minor;blocking 0 條
