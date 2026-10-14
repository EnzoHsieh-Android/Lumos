severity: major

severity: major
blocking: 是 — `_h2_section_lines` 的說明已明文裁定只認 ATX 標題、不准自建 Setext 判定,計劃的過濾器正好是被否決過的那套
引句:「Setext 標題的底線(前一行不是空行、這一行只有 `=` 或 `-`)、HTML 標題標籤(`<h1>`–`<h6>`)」
對照:`scripts/lumos:7823-7826` 的 `_h2_section_lines` 說明寫「找節邏輯不准長出第三套」,以及「只認 ATX 標題(代碼審 r2:自建 Setext 判定是第二套標題邏輯,還有 fence 錯配與 H1/H2 不分兩個洞)」。節的邊界規則是「到下一個 `## `/`# ` 為止、三級標題不切節」。
判定理由:計劃在 `_h2_section_lines(text, _NOGO_H2_RE)` 的結果上再過濾一遍,遇到 `###`、Setext 底線、`<h1>`–`<h6>` 就收節。這等於把這個函式的節邊界換成另一種,做法是疊一個後置過濾,而不是改函式本身。結果是不做節用一套切法,回退節和實務隱患節用另一套,同一個函式回傳的「節」有兩種定義。Setext 判定正是 r2 否決過的設計,計劃沒有提出理由說明為何現在可以翻案。照既有慣例,要嘛不做節也照 ATX「三級不切節」的規則,再靠清單項目限制擋住子標題裡的散文;要嘛給 `_h2_section_lines` 加選配參數,讓所有呼叫者共用同一個切法,並更新那段說明。

severity: major
blocking: 是 — 計劃新增跨行註解計數,而 `_visible_lines` 對註解的處理是刻意不做,並且有 blocker 紀錄
引句:「從檔頭數到這一行,`<!--` 比 `-->` 多(標題落在沒收尾的註解裡),就不當成不做節」
對照:`scripts/lumos:4927` 寫「★不偵測 HTML 註解★(-b r3 單reviewer 兩條 blocker:`-->  <!--` 先關再開會把後面整份藏掉)」。行內註解由 `_strip_inline_markup` 處理(`scripts/lumos:376` 起),其餘註解計數(`scripts/lumos:3652`、`19680`)是各自針對特定語法的小正規式。
判定理由:專案裡跨行註解狀態只有一種處理方式,就是不處理。計劃在判門的路徑上加了第二種做法:從檔頭累計 `<!--` 與 `-->` 的數量差。這個數量差有兩個問題。第一,它會把圍欄內的 `<!--` 也算進去,而 `_visible_lines` 不看圍欄內的內容,所以兩邊對「看得見」的定義不一致。第二,`-->  <!--` 同一行先關再開時數量相抵,正是 r3 blocker 的形狀。計劃應改為:不碰註解,讓不做節標題在註解裡時照舊被認成節,再靠「其他訊號照掃」兜底;或把註解處理做進 `_visible_lines` 並重新通過它那邊的 blocker 檢驗。不能在判門處自建一份。

severity: minor
blocking: 否 — 重用機會,不是第二套邏輯
引句:「以 `-`、`*`、`+` 或 `數字.`、`數字)` 開頭的行,與它底下比它縮排更深的續行」
對照:`scripts/lumos:7910` 的 `_EXCL_LEAD_RE`,以及 `scripts/lumos:7753` 的 `_CLAUSE_LEAD_RE` / `_CLAUSE_ENUM`。這兩個是「前綴剝除」用的,不是「判斷是不是清單項」用的。標題正規式另有 `scripts/lumos:32531` 的 `_NOTELINES_HEADING_RE` 和 `scripts/lumos:41002` 的 `_DRIFT_M1_HEAD_RE`。
判定理由:專案沒有現成的「這行是不是清單項」判斷,所以新增 `_NOGO_ITEM_RE` 站得住腳。但清單符號的集合(`- * + 數字. 數字)`)與 `_EXCL_LEAD_RE`、`_CLAUSE_LEAD_RE` 各有一份,三處會漂移。建議在計劃裡寫明新正規式的符號集與前兩者的差異和理由,或在 `_NOGO_ITEM_RE` 旁註明「與 `_EXCL_LEAD_RE` 同一組符號」並加一個守衛測試。`_NOGO_STOP_RE` 的 ATX 部分也是已有的第三份 `#{1,6}\s` 變體(其中 `_DRIFT_M1_HEAD_RE` 不認 tab 和空標題),計劃已說明理由(tab、空標題),可以接受。

severity: minor
blocking: 否 — 與既有留痕比對方式不同,但不構成第二種做法
引句:「推送前重判(`_spec_gate_push_stale`)多比一件事:現在算出的 `nogo_skipped` 跟留痕記的不同,就判留痕過期」
對照:`scripts/lumos:8999` 和 `scripts/lumos:8136`:既有做法是把門的附加輸入(`linked`、`exclusions`)作為 `_clause_block_sha(text, rows_b, linked, exclusions)` 的參數併進同一個 `clause_sha`,推送前只比這一個值。
判定理由:計劃改用另一個留痕欄位加單獨比對,而不是把 `nogo_skipped` 併進 `_clause_block_sha`。這會讓「留痕還成不成立」變成兩處比對,日後再有新的門輸入時,還要判斷該用哪一種。計劃的理由(舊留痕沒有該欄位時視為空清單、維持成立)是對的:併進 `clause_sha` 會讓所有舊留痕的指紋都變。折衷是在 `_clause_block_sha` 加選配參數,只在清單非空時才納入雜湊,這樣舊留痕不受影響,又保持單一比對點。這不是 blocking,但計劃應註明為何不這樣做。

不對齊共 4 條,其中 major 2 條(其中 Setext/ATX 切節與註解計數兩條都標 blocking)。
