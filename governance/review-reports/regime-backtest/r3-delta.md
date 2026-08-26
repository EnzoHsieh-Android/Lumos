# 審查報告:改制回測 r3(delta 席,r2 折入回歸鏡頭)

sha256 已核對 = 7c670c9fabc49078a6c1751b74a566cd5c38bf90d24d8852d2a38fa7ff769e02。

## d-f1
severity: major
引句:「哪類差異(邏輯漂移/帳被動/golden 過期)」
佐證:file: `governance/review-reports/regime-backtest/r3-snapshot.md:29`(同段「回放讀凍結檔前先 sha 對帳...不符或佚失=分類凍結檔被動/佚失(紅,資料完整性)」是獨立於下文「分三類」之外、且比三類判斷更早執行的第四種結果);file: `governance/review-reports/regime-backtest/r3-snapshot.md:32`(週跑通知 MSG 規格只列三類)
說明:S1 為解 r2 的 ext-f4(閉包無內容位址,凍結檔被動時誤報邏輯漂移)新增了「sha 先驗,不符/佚失就分類凍結檔被動/佚失(紅,資料完整性)」這條判定路徑——這是獨立於原本「分三類」之外、且優先於三類判斷的第四種結果。但 S4 的週跑通知規格白紙黑字只列了三類(邏輯漂移/帳被動/golden 過期),沒有把這個新分類算進去——S4 這段文字在 r2 折入時沒有被同步更新。照字面實作,週跑真的抓到「凍結檔被動/佚失」時,組訊息的程式碼要嘛沒有對應分支可用(漏發這條本來最該喊人的資料完整性警訊),要嘛實作者會把它硬塞進名字相近的「帳被動」分支——但這兩者代表完全不同的問題(canary 帳列被改 vs report/snapshot 檔案被改/遺失),誤標會讓收到通知的人查錯方向、修錯東西。

## d-f2
severity: major
引句:「verdict 另記各檔 git blob id,內容可從版控史回復」
佐證:file: `governance/review-reports/regime-backtest/r3-snapshot.md:29`;現場實測(scratchpad 建空 repo):`git hash-object f.txt` 只回傳雜湊、隨即 `git cat-file -t <該雜湊>` rc=128 讀不到物件;改用 `git hash-object -w f.txt` 才會建物件,但 `git fsck --unreachable` 立刻回報該物件是 `dangling blob`(未被任何 commit/tree 引用)
說明:這條是為解 r2 的 ext-f4(閉包無內容位址)新增的——sha 對不上時不硬算,改記 git blob id 讓內容日後可從版控史回復。但 S2 把「收斂即凍」定義成「gate PASS 後操作者當場 --freeze」,這個時間點通常早於 report/snapshot 檔案真正被 `git commit` 進版控(本專案現有慣例是收工時才把報告與快照一起 commit 進卷)。如果 --freeze 當下只是計算 `git hash-object`(不寫入)拿到的雜湊,那個雜湊在 `.git/objects` 裡根本不存在,日後讀不到;就算改用 `-w` 強制寫入,寫進去的也只是一個沒有任何 commit/tree 指向它的「懸空 blob」,git 的自動垃圾回收(`gc.pruneExpire` 預設 2 週)之後照樣可能清掉。條款沒有交代「先確保檔案已進了某個 commit 才記 blob id」這個前提,照字面實作,verdict 裡記下的 git blob id 有相當機率日後根本回復不了內容,卻讓人誤以為多了一條可靠的復原路徑。

## d-f3
severity: major
引句:「比照 run_nags 的 nags-last-week.txt 慣例」
佐證:file: `governance/review-reports/regime-backtest/r3-snapshot.md:32`;file: `governance/autonomous-loop.sh:225-233`(`run_nags` 的 `nags-last-week.txt` 只存一個 `$(date +%G-W%V)` 週戳記,拿來跟本週比對「本週跑過沒」,不記任何位置/索引,也不記候選清單)
說明:r2 的 d-f4 點名的洞是「S1~S4 沒有一條講輪替游標要存在哪裡、用什麼格式」——這條折入只補了「存在哪裡」(`governance/replay/.rotation-cursor`),沒有補「用什麼格式」,而且拿來當範本的 `nags-last-week.txt` 剛好是結構完全不同的機制:它是「這週跑過沒有」的去重戳記,不是「輪流抽 5 包、記得上次抽到哪、輪完一圈重來」需要的位置指標。照字面「比照 nags-last-week.txt 慣例」實作,最自然的寫法就是複製同一套讀寫模式——存一個當週戳記、本週跑過就跳過——這種寫法完全兜不出「輪完一圈重來」:它防得住「同一週重跑兩次」,但答不出「這一圈跑到第幾包、下次該從哪包接著抽」,存量抽樣還是會退化成 r2 d-f4 原本點名的「無狀態抽樣,有些包永遠抽不到」。

## 掃過但乾淨的面

- 卷證完整性:sha256 與題目給定值相符。
- r2 六條折入逐條對照,確認全部落進 S1~S4 條款本文(不是只停在審計修正紀錄):spec_path 三段式(技術上可行,`scripts/lumos:3655-3677` 已有 --report/--snapshot 存 path+sha256 的現成模式,且 D 案恰在改同一寫側區塊,「順同一刀」與現場一致)、閉包雙集合(多輪 loop 凍完不再恆報長大,r2 d-f2 已解)、readonly 不含觀測尾巴(對照 `scripts/lumos:10101`/`10297-10317`,結構上堵住第三個寫入點)、重凍檔名+拒寫(--note 必填+留痕與 `scripts/lumos:10661-10700` anchor approve 邏輯一致;歸檔改名是明講的新機制非誤引先例)。
- 未發現 r2 折入之間互相矛盾,亦未發現 r2 折入與 r1 折入打架(engine_rev 分流、S3 產物歸圖譜驗證紀錄、spec sha 用窗末 result_sha256 等銜接處逐一核過,語意一致)。
- G3 hash 鏈在 replay 模式下比對「永遠為真」的設計在 r3 未被任何改動觸碰,維持原判——非漏洞。
