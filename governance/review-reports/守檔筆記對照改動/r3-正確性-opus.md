severity: major

# 設計審第 3 輪:正確性-opus

席名:正確性-opus(第 3 輪,全新席)。審材:r3-snapshot.md。對照程式:negguard 的 clone(b3680d44),實驗目錄 rr-r3-work-正確性-opus/。
逐節讀過並對程式查證。實驗與查證:
- `git ls-tree tip:<不存在的資料夾>` 回 128;`ls-tree -r tip -- <資料夾>/` 在資料夾不存在時回 0 且沒有輸出(第 4 節「先確認資料夾在不在」做得到)。
- Python 3.14 碰到沒被接住的 KeyboardInterrupt,bash 看到的回傳碼是 130(第 4 節「只在回傳碼 130 停下」接得上)。
- rtb 驗證組 17 行真漂移全部落在「同一提交也改過、而且當時 type: system、status: doing」的 Systems 筆記上(拿 `line_judgments.tsv` 對 rtb 逐一 `git show --name-only` 核對過)→ 產品的候選定義不會先把 S10 的門檻吃掉,S10 量得出來。
- `_note_audit_resolve` 的截斷上線點:標記不在頂端歷史時 `_nodehome_clamp_base` 回原本的起點(rtb 沒有這個標記,所以 S10 的單一提交範圍不會被截空)。
- `_nodehome_name_status` 只負責解析、norm=False 會回原樣路徑;`_notes_status_flipped` 的 git log 呼叫與測試假造 `_ns_git` 的方式(只看 `"log" in args`),抽出共用函式後照樣能用。

## F1 項目檔名與 `prepared:` 來源錨點還在用「只看程式那一半」的指紋:同樣程式、筆記不同的兩份材料會互蓋,record 會把舊報告配到新的檔頭
severity: major
blocking: 是
引句:「`.lumos/note-audit/reread-<項目指紋>-<編排者>.md`,用筆記內容審的工作目錄」
file: `scripts/lumos:26326`
1. 第 2 輪把項目指紋改成不含筆記 blob,目的是讓「有沒有對照過」跟筆記內容脫鉤。但同一個指紋還拿去當兩種身分用:項目檔的檔名(第 2 節)與報告的 `prepared:` 錨點(第 3 節:「`prepared:` 填項目指紋」)。這兩處要認的是「判定者當時讀的是哪一份材料」,而那份材料包含筆記全文、筆記 blob、筆記行數與範圍終點。這些東西都不在指紋裡。
2. 失敗場景(一般流程就會走到):作者照提醒跑 reread-prepare(頂端 T1,筆記 blob n1,120 行),產出 `reread-<fp>-claude.md` 並派出判定者 A。判定者還在跑的時候,作者自己先改掉明顯過時的幾行、刪了一段,提交成 T2(筆記 blob n2,95 行,程式沒動),再用新的終點重跑 prepare,想讓判定看新版。程式那一半沒變,所以指紋一樣,檔名一樣,項目檔被覆寫成 n2/95 行/T2。
3. 判定者 A 的報告回來後,`reread-record --prepared reread-<fp>-claude.md`:`prepared:` 等於指紋,錨點檢查通過,provenance_ok 是 true;行號拿 95 行去驗,A 點出的第 100、110 行被當成「超出行數」丟掉;留下的行,「那一行當時的全文」是從 n2 讀的,跟 A 的原句、理由對不上。紀錄檔帶著錯的文字提交進版控,沒有任何一道能發現。
4. 影響:第 5 節抽 30 行人工判、RETIRE-IF 第一條「點出的行在之後的版本還一字不差留著的比例」都拿紀錄檔裡「當時全文」的欄位來比,資料會被污染;〈實務隱患〉「併發」那條宣稱「項目檔名帶編排者,不互蓋」,在同一種編排者的兩個會談(兩個 claude 會談各自 prepare 同一篇、筆記版本不同)下也不成立。
5. 建議折法:把「材料身分」跟「覆蓋指紋」拆開。項目檔名與 `prepared:` 改用材料指紋(覆蓋指紋加筆記 blob 加範圍終點,或整份本文的雜湊,比照筆記內容審清單指紋的做法);record 用材料指紋驗錨點,寫紀錄檔時檔名前綴照樣用覆蓋指紋(check 只認這個)。S5 補一句:「覆蓋指紋相同、筆記 blob 不同的兩份項目檔不互蓋;用舊材料的報告配新項目檔時 provenance_ok 是 false」。

## F2 〈誠實界線〉對指紋盲區的「影響小」理由,是第 2 輪改指紋之前的說法,現在不成立
severity: minor
blocking: 否
引句:「實際影響小:候選要求筆記這次被碰過,筆記內容一變指紋就變」
file: `governance/review-reports/守檔筆記對照改動/r3-snapshot.md:156`
1. 第 2 節現在明寫「★不含筆記自己的 blob★」,所以「筆記內容一變指紋就變」是錯的。這是第 2 輪的折法沒有同步到這一節。
2. 盲區因此比這句講的寬:被舊紀錄蓋過的條件不再需要「筆記改了又改回」,只要「頂端 about_code 列的那幾支檔的 blob 跟某次紀錄時一樣」,再加上這次動的是沒被列的補測試檔,或是從 about_code 移出/刪掉的檔,就會被當成已對照。例:第 1 次推送 about_code=[F],記錄了 h(N,[F@b1]);之後把 H 加進 about_code;第 3 次推送刪掉 H、從 about_code 移出 H,並在 N 追加一段,F 沒動 → 頂端指紋回到 h(N,[F@b1]),check 判成已對照,但刪掉 H 這個改動從沒被對照過。
3. 提醒版不會因此擋錯東西,所以是 minor;但這句是在替盲區找理由,要照現在的指紋定義重寫(例:「只有頂端 about_code 各檔 blob 與某次紀錄完全相同、這次只動了這兩類檔時會被舊紀錄蓋過」)。

## F3 「從紀錄看得到別名解析到哪個版本」跟報告錨點照抄檔頭的做法互相矛盾
severity: minor
blocking: 否
引句:「報告的 `model:` 行照判定者自己寫的存進紀錄;別名在不同環境解析到不同版本時,REVISIT 那天從紀錄看得到」
file: `scripts/templates/note-audit-judge.md:27`
1. 範本的附加說明是「報告開頭四行來源錨點的照抄說明」,沿用筆記內容審的做法:`model: <copy 判定者模型 from the list header>`。record 則拿 `model` 去跟檔頭比(`scripts/lumos:26444` 的 provenance 比法;第 3 節也規定不同就標 false)。照這樣做,判定者寫的是檔頭的別名 `sonnet`,紀錄裡永遠是 `sonnet`,看不到實際解析成哪個版本。
2. 反過來,如果要判定者自己報實際版本,每一份的 `model` 都會跟檔頭的 `sonnet` 不同,provenance_ok 恆為 false,每次都印警告。
3. 〈誠實界線〉把這一行當成「換模型沒有機械偵測」唯一的事後補救(「REVISIT 那天從紀錄檔的 `model:` 行看有沒有混用」),這條補救照字面做不到。這是第 1 輪鏡像核對補的東西,折法本身沒落實。建議:錨點照抄不變,另加一行判定者自報的 `judge_model:` 只存不比;或者直接在〈誠實界線〉承認看不到,並附 REVISIT 條件。

## 各節核對結果
- 開頭、依據、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding(S10 門檻對產品的候選定義量得出來,見上面的實驗)。
- 〈範圍〉:已讀,無 finding。
- 〈做法〉0:已讀,無 finding(`--literal-pathspecs` 加在 ls-tree/log 的資料夾 pathspec 上實測可用)。
- 〈做法〉1:已讀,無 finding(範圍解析的選配參數、起點算不出當提早結束、候選交集,都跟 `_note_audit_resolve`、`_push_range_start`、`_nodehome_homes` 現在的回傳形狀對得上;手動 prepare 跟帶推送參數的 check 起點不同,但指紋不含範圍,S6 那個「合過主線」的情境照字面會變綠)。
- 〈做法〉2:F1。其餘(截斷與填入字串照實驗、補測試檔規則對 rtb 佈局)已讀,無 blocking。
- 〈做法〉3:F1、F3。
- 〈做法〉4:已讀,無 blocking(資料夾不存在的判法可以做到;130 那條跟 Python 的 SIGINT 回傳碼接得上;掛鉤與 CI 現在都沒有 `note-audit check` 這串,S9 可以照字面驗)。
- 〈做法〉5、6:已讀,無 finding。
- 〈條款〉S1–S14:都寫得成會翻紅的測試;F1 建議 S5 補一句。
- 〈回退〉〈實務隱患〉:「併發」那條受 F1 影響,其餘無 finding。
- 〈誠實界線〉:F2、F3。
- 〈附錄〉:已讀,無 finding。

最高等級:major;blocking 共 1 條
