severity: major

派工尾端沒有附到固定席節點,所以沒有逐條判的對象,以下全是依我這個鏡頭自己找的洞。

先講結論:防放水檢查只比數量,而兩邊的數字都是編排者能動的。分子是自己標的逐條嚴重度,分母可以靠多記報告撐大。所以它擋得住誤標,擋不住想過閘的編排者。

## 1. 把真 major 標成 minor 再放行(沒擋住)

severity: major
blocking: 是

引句:「分子大於分母 → 處置集合判不過」

步驟如下。
1. 報告裡有 1 條 major(X1)和 1 條 minor(X2)。
2. 載體寫 `--finding-severity X1=minor --finding-severity X2=minor`。
3. 折 X2、放行 X1。
4. 分子是 1,分母是 1(報告裡的 minor 宣告行),判過。

我讀了 `cmd_canary`(約 10860 行起)。`finding_severities` 只驗「鍵集合等於 findings_set」和值域,id 與報告裡哪一條發現沒有任何機械對應。輪級的 `severity` 不會幫忙:載體的 severity 本來就只能不低於報告最高值。

設計自己承認「這擋的是數量,不保證每條對應正確」。但設計又把這句話當成防線寫進〈守衛面〉。我的判斷是這道防線形同虛設。

補法(代價合理,擇一):
- 對每個 accepted id,要求收貨紀錄那一列帶出報告原文引句。處置閘用這句引句在該席報告裡找到所屬發現區塊,取那一塊自己的 `severity:` 行。逐條標的值不得低於它,否則判不過。引句檢查和 `_report_severities` 都是現成的,只差「區塊內取值」這一步。
- 便宜的退路是守恆檢查:報告宣告的 major 與 blocker 行數(扣掉降級清單)不得多於 folded 數。重疊發現會誤擋,所以只能當輔助,不能當主防線。

## 2. 灌分母:加一份只含 minor 或 clean 的報告(沒擋住)

severity: major
blocking: 是

引句:「再數 minor 與 clean 的宣告行;同一席同一份報告只算一次(鍵 `(auditor, report_sha256)`)」

這句話同時出了三個洞。

(a) clean 行不是發現,卻被算進分母。`_report_reported_count` 刻意排除 clean,所以報告裡塞再多 `severity: clean` 行,既不會觸發「報告沒正規化」,也不會動到 `reported` 欄。任何一席(包括那份有 major 的報告)多寫 N 行 `severity: clean`,分母就多 N。分母應該只數 minor,單位要跟 `_report_reported_count` 一致。

(b) 同一席換報告也算新的。設計寫「各席最新一筆帳」,去重鍵卻含 `report_sha256`,兩句互相矛盾。照去重鍵實作的話,同一個 auditor 在同一輪再記一筆不帶處置清單的帳,附一份灌水報告(檔首一行 severity,其後一堆 minor 或 clean 行),分母就變大。舊的 major 列還留在輪內,所以 major 規則照樣觸發,但分子跟著過閘。這種同席多筆的形狀在真帳上很常見:646 個 code 輪裡有 55 個輪,同一席有多筆帳。

(c) 派工名單對帳(roster)是純提醒,恆不影響 rc。我讀了 `_roster_observe`,印出來的是 advisory。不在派工快照裡的假席也算數,不需要真派過。非載體席的引句本來就允許錨不到,所以灌水報告不必有真引句。

補法:
1. 分母只數 minor,不數 clean。
2. 每個 auditor 只取最後一筆帳,去重鍵不要含 sha。
3. 只計派工快照(`_roster_dispatch_entries`)裡出現過的席。
4. 計入分母的 minor 行必須帶一句能錨回凍結 snapshot 的引句,沿用 quote-check。
5. 第 4 條不做的話,至少把總量限制成「每席計入上限等於該席報告的非 clean 條數」,這樣席內灌 clean 也沒用。

## 3. 降級清單等於自簽放行章(沒擋住)

severity: major
blocking: 是

引句:「要帶 `--intake` 且 id 在收貨紀錄的重現表同一列出現(整字比對)」

`--downgraded-set` 照抄 refuted-set 的檢查,但兩者的後果不同。

- refuted-set 的 id 在 findings 之外,最多讓「存活數」變少。
- 降級清單的 id 在 findings 之內,而且同時做兩件事:證明 major 可以放行,又替分母加分。

檢查條件只有三樣:id 在 findings_set、標成 minor、理由至少 4 字。收貨紀錄(intake)是編排者自己寫的檔。我讀了 refuted-set 的比對:同一列有整字 id 和 HIT、MISS、重現、採信其中一個字就過。所以寫一列「X1 採信」,再帶 `--downgraded-set X1=辯方證據`,真 major 就合法放行。

另外,降級條數直接加進分母,沒要求降級的 id 必須在 accepted 裡。折掉的 minor 也能掛一筆降級來灌分母,這筆不需要任何真實的 major。

補法:
1. 降級的 id 必須在 accepted 裡。分母只加「同時在降級清單和 accepted 裡的 id」,不加條數。
2. 要求辯方席的報告裡,該 id 對應的發現帶 `file: 路徑:行號` 並宣告 minor。可以搭配既有的 `--refute-verdict id=evidence`,在記帳時機械核對。
3. 降級後仍要留逃逸帳記錄,RETIRE-IF 才查得到。

## 4. 把 major 移進 refuted-set(舊洞,新規則放大它)

severity: major
blocking: 是

引句:「輪內有 major 席、載體帶 `finding_severities`:accepted 裡每個 id 的逐條嚴重度都必須是 minor 或 clean」

步驟如下。
1. 把真 major 登記進 `--refuted-set X1=重現不到(怎麼試的)`,收貨紀錄裡寫一列「X1 MISS」。
2. X1 因此不在 findings_set 裡。
3. 剩下全是 minor,全部放行。

處置閘看的是 `F=findings_set`,X1 不在 F 裡就沒人檢查它。舊規則下,major 輪的 minor 必須全折,這條路的好處不大;新規則下,它變成「消掉 major,其餘 minor 全放」的完整繞法。refuted-set 的現有把關只有 intake 一列整字比對,而 intake 是編排者自己的檔。

補法(代價很低):major 輪裡 `refuted_set` 非空時,退回舊規則(accepted 必須為空),或者要求 refuted 的每個 id 都有辯方 evidence。refuted 本來就少見,這條幾乎不增加正常流程的負擔。

## 5. 拆或合 id(合是沒擋住,拆是設計已承認的誤擋)

severity: minor
blocking: 否

引句:「把多出來的那條改成折入、或補記降級清單就過」

- 合併:把 major 和 minor 併成同一個 id,標 minor 放行,分子只有 1。這是第 1 條的變形,同一個補法(id 對報告區塊)可以一起解決。
- 拆分:拆得越多,分子越大、越容易被擋。這只傷誠實的人。
- 逃生口的措辭不妥:「補記降級清單就過」把第 3 條那個無驗證的路徑寫成誤擋的標準解法,等於教編排者走那條路。逃生口只該寫「改折入」。

## 6. 重記換報告、換新輪(新規則沒多開洞)

severity: minor
blocking: 否

一輪只能有一筆載體(處置閘會擋多筆載體),所以重記載體得換輪。換成只含 minor 的 delta 輪,本來就不會觸發任何 major 規則。這是現行的 delta 輪語意,不是本設計新增的。同輪用同一席補一筆灌水報告的情形,見第 2 條。

## 7. 讓某席報告讀不到(擋得住)

severity: clean
blocking: 否

設計寫「報告讀不到時照處置閘既有的留痕重驗判不過」。現行的留痕重驗對全席、全檔都是 fail-closed。這條沒有繞法,可以不動。

## 附帶:S6 的措辭與事實不符

severity: minor
blocking: 否

引句:「舊帳的載體都沒在 major 輪帶 `finding_severities` 放行 minor」

真帳裡有反例:`code-規格閘半套` r1 帶了逐條嚴重度,而且 major 輪放行了 X4 和 X7(都標 minor)。但處置閘只判該迴圈的最後一輪,那個迴圈的最後一輪是 r3,accepted 為空,所以判定不變。結論 S6 還是成立,只是理由要改成「只有最後一輪參與判定」,不能寫「都沒帶」。S6 的測試要斷言這個理由,不是只斷言結果沒變。

## 摘要

最嚴重等級 major,blocking 條數 4(第 1、2、3、4 條)。第 5、6 條和附帶事項是 minor,第 7 條是 clean。第 1、2、3 條都可以靠「id 綁定到報告區塊的 severity 行」加「只數 minor、只取各席最後一筆」一起解掉,工程量不大。第 4 條只要加一個條件。
