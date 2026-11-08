severity: major

## Finding 1
severity: major
blocking: 是

判準:實作照做會做出沒用的東西(回頭條件的補救手法對不上實測的誤報成因)。
spec 段落:檔尾兩條 REVISIT,以及〈實驗〉的誤報成因。

引句:「REVISIT:2027-05-08 外部網址進 WebView 那條試第二版形狀(同函式有 scheme 或 host 比對就不報)」

問題:
- loadurl 規則現行版本已經有這道排除。
- 規則檔 `kt-loadurl-external` 的 `not: inside function_declaration regex '\.(scheme|host)\b|getScheme\(|getHost\(|Intent\.parseUri'` 就是同函式讀 scheme 或 host 就不報。
- 型錄 API-49 的形狀欄也寫了「同函式有讀 scheme、host 或用 Intent.parseUri 的不報」。
- 這次 8 個誤報裡,範例碼佔 6、可信來源佔 2(twin-te 只拿 Intent 的路徑片段、Jelly 是 App 內部廣播),沒有一個是缺 scheme/host 比對。
- 所以 2027-05-08 的人照這句做「第二版形狀」等於沒改,重量會得到同樣結果。
- 這條回頭條件沒有指向真正的誤報來源。

引句:「REVISIT:2027-05-08 TLS 版本那條試第二版形狀(外層有 Build.VERSION.SDK_INT 小於 21 的判斷就不報)」

問題:
- TLS 的 11 處誤報裡,舊系統相容只有 3 處,其中 owncloud 那處靠 `NoSuchAlgorithmException` 退回,不是 `SDK_INT` 判斷。
- 就算這個形狀完美,誤報也只剩 8/40,即 20%,仍超過 10% 的升級條件。
- 範例碼 4、外部協定 2、函式庫複本 1、已防護 1 都不是這個形狀能處理的。
- 這條 REVISIT 預告了一個不可能過條件的實驗。

佐證:
file: `configs/ast-grep/kotlin-android/rules-unwired/api.yml`(`id: kt-loadurl-external` 段的 `not:` 區塊)
file: `governance/review-reports/android不接閘資安規則重量/experiment/judge-loadurl.md:47`
file: `governance/review-reports/android不接閘資安規則重量/experiment/judge-tls.md`

## Finding 2
severity: minor
blocking: 否

判準:量法有讓結論偏向「不升」的旋鈕,而且沒有在〈天花板〉揭露。
spec 段落:〈用詞〉的判讀代理、〈實驗〉表的 loadurl 列、〈天花板〉。

引句:「誤報率是 40 處以內的點估計。」

問題:
- loadurl 的 8 個誤報裡 6 個是「測試或範例碼」。
- 其中 3 個只靠 repo 名含 demo 或 example 判定(VpnDemo、casdoor-android-example、identity-android-sdk-demo),消費專案的 repo 名不會是這類訊號。
- 把這 6 處排除,誤報是 2/34,約 5.9%,低於 10%;命中 190 處也遠過 20。這時它會過升級條件。
- 「7 條都沒過」對 loadurl 只有在「範例碼算誤報」時成立。
- 這也是第二批樣本外 7% 跳到這次 20% 的主因,是判準改了(第三批才補客觀特徵),不是規則變差。
- 計劃把它寫成純新量測,沒給敏感度。
- 這個選擇偏保守,不升比誤升安全,所以不擋,但天花板該加一行。

佐證:
file: `governance/review-reports/android不接閘資安規則重量/experiment/judge-loadurl.md`(FP 列)
file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:95`

## Finding 3
severity: minor
blocking: 否

判準:說「沿用」的量法其實改了口徑,且追溯改寫了舊結案文字。
spec 段落:PRIOR-ART、〈用詞〉的判讀代理。

引句:「**判不準**不算真問題,誤報率這裡寫成「誤報+判不準」佔判讀數的比例。」

問題:
- 第二批計劃寫的是「誤報比例=誤報÷抽判數(判不準留在分母)」,判不準不進分子。
- 本計劃把判不準併入分子,又說「量法沿用第一、二批」,並且在第二批結案文字裡補了「百分比是誤報加判不準佔判讀數」。
- 這次結論不受影響:provider 是 8/21,約 38%,對 43%;cmd 是 30/40,約 75%,對 80%,都遠超 10%。
- 口徑已經分叉,這段字句要改成承認「與第二批口徑不同」。

佐證:
file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:105`

## Finding 4
severity: minor
blocking: 否

判準:天花板漏掉一個會大幅改變單條數字的判讀爭議。
spec 段落:〈天花板〉第二條、〈實驗〉表的 db 列。

引句:「資料庫那條真問題有 12 處來自同一個 repo,樣本不獨立。」

問題:
- 判讀員自己在 judge-provider-db.md 末尾註明這 12 處的判 TP 有爭議。
- LocalMusicHelper 把 asset 複製到外部目錄再讀寫。若把「轉檔用暫存資料庫」算成匯入外部資料庫,這 12 處改判 FP,誤報變成 16/25,約 64%。
- 計劃只寫了「不獨立」,沒寫「判讀有爭議」。結論(不升)不變,但 16% 這個數字的不穩定度被低估。

佐證:
file: `governance/review-reports/android不接閘資安規則重量/experiment/judge-provider-db.md`(檔尾說明與 `Winnie0408__LocalMusicHelper` 各列)

## Finding 5
severity: minor
blocking: 否

判準:「命中仍不到 20」的結論受語料大小所限,而且語料沒排除資安教材。
spec 段落:〈實驗〉表的 secretkeyspec 與 weak-cipher 兩列、〈用詞〉的樣本外。

引句:「命中仍不到 20,不接閘」

問題:
- 命中數取決於 GitHub 搜尋撈到幾支檔(480、328 支檔),不是規則本身的普遍度。
- secretkeyspec 的 14 處沒判讀,卻是唯一能補樣本外誤報資訊的資料。
- queries.tsv 沒有第二批做過的「排除資安教材與規則樣本 repo」。
- 實際命中已混入掃描器測試語料(`Vulnetix__cli/internal/sast/testdata/...`),以及 SWE-gen 這類基準資料集(`abundant-ai__SWE-gen-Java`)。
- 排除清單只防「前三批見過的 repo」,沒防這類資料集。

佐證:
file: `governance/review-reports/android不接閘資安規則重量/experiment/queries.tsv`
file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:105`

## Finding 6
severity: minor
blocking: 否

判準:內部不一致。
spec 段落:〈範圍〉1 的括號。

引句:「命中不到 20 或沒量過樣本外,形狀本身誤報不高」

問題:
- 這句是挑這 7 條的前提。
- 實測結果是 cmd 80%、provider 43%、TLS 27.5%,明顯不是「形狀本身誤報不高」。
- 型錄 ARCH-90 那列自己就寫「收窄前的寬形狀樣本外 55 處抽判 40 處誤報 28」。
- 前提措辭與結果對不上,會誤導後面的人以為這 7 條原本是接近能升的候選。

佐證:
file: `skills/kotlin-idioms/checks-catalog.md:534`

## Finding 7
severity: minor
blocking: 否

判準:可執行性,回退與驗收條款不完整。
spec 段落:〈回退〉、〈驗收條款〉、〈預期值表〉。

引句:「退回本計劃的提交:型錄 7 列實測狀態的補句、第二批計劃那條回頭條件、本篇。」

問題:
- 〈範圍〉4 另外說要改第一批計劃的補註。
- 收貨紀錄還加了第二批的 RETIRE-IF 更正與 `REVISIT:2026-11-22`,實際提交也動了第三批計劃。
- 〈回退〉清單沒列這些,退回會留下孤兒補註。
- 〈預期值表〉只有 API-45 一列,另外六列的數字(loadurl 8/40、cmd 32/40、provider 9/21、db 4/25、14 和 8 處)只靠 [manual],沒有預期值可核。
- 型錄自檢 S1 也守不到這些數字。

佐證:
file: `docs/lumos-toolchain-knowledge/Projects/Android資安與崩潰靜態檢查補齊_計劃.md:67`
file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:22`

## 已讀,無 finding 的節
- 〈用詞〉其餘條目已讀,交叉引用都存在。
- 〈依據來源〉已讀,無 finding。
- 〈實務隱患〉已讀。碰到的風險類是金流、對外送出、不可逆、守衛面,理由都成立,因為沒改規則也沒改會擋的範圍。
- 「19 條 = 7 + 12」已查證:`rules-unwired/` 共 30 條,扣掉 11 條非資安規則剛好 19。第二批 10 條不重量的算法也對得上。
- 表內數字已查證,與卷證一致:
  - hits 筆數與 repo 數吻合。
  - 抽樣檔 sample-*.txt 的 repo 數吻合(db 的 25 處對 11 個 repo、provider 的 21 處對 20 個 repo)。
  - 7 個 hits 檔和排除清單 `excl-repos.txt` 的 repo 重疊為 0。
  - 各 judge 檔的總計對得上。

## 固定席節點判:Systems/kotlin規則包
不影響。
- 該節點掛 0 份計劃、0 條合約、0 行 KEY。
- 本計劃不改規則與會擋的範圍。
- 節點 RULE 行「誤報超過命中的一成就降提示級、搬 rules-unwired/」與本計劃一致。
- 唯一對不上的是 `lands_in` 列了這個節點,但計劃沒有任何內容要寫進去。這不影響行為。

我沒有在 /tmp/lumos-seat-work/ 底下建任何東西,也沒有修改 repo 裡任何檔案。

最高等級 major;blocking 1 條
