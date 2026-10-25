preflight-4: ran

# android端到端驗收 r1 收貨

## 前掃(首輪,派審查員之前)

前掃員(sonnet,沒參與設計)照固定清單掃:①未定義的詞 5 條 ②壞引用 2 條 ③範圍矛盾 4 條 ④機械宣稱驗語意不對 4 條。①②③與存在類直接修真檔;語意類逐條記下修改前後。前掃動到的「做法」與「條款」不改任何 WHY 行的裁定(擋合併、人可留理由放行、本機跑 CI 驗紀錄、做法 A、綁內容指紋、毫秒類只提醒、失敗重跑一次),只改機制寫法去兌現這些裁定;改動由本輪席位審。修改前的全文存在 scratchpad,沒進卷證。

語意類修改(修改前 → 修改後):

| # | 前掃查到的事實 | 修改前 | 修改後 |
|---|---|---|---|
| P1(③1) | pre-push 傳 --diff 本次推送範圍、CI 傳 BEFORE..SHA;「合併前必須通過」只看最後一次檢查 | 「這次推送改到設定裡的 App 程式目錄時」才要求紀錄 | 範圍改成「分支跟主線的分岔點到被推送提交」;新增條款 S8(先推改程式、再推只改文件,照樣要求) |
| P2(③2) | waive 只能對已存在的紀錄放行,沒跑驗收時沒有出口 | 「指紋找不到紀錄時回 2」 | 沒有紀錄就新建一份 result=waived 的紀錄;條款 S9 改寫 |
| P3(③3) | 本計劃第 4 塊與實驗室驗收現在就要用 Maestro 驅動,repeat 吃不吃變數沒實測 | REVISIT:2027-01-31 再驗 | 刪掉那條 REVISIT,改成〈資料怎麼流〉第 0 步前置實測(連同 toolkit 狀態列固定)與條款 S13 |
| P4(③4) | pre-push 與 CI 都用 --at-sha,工作目錄可能有未提交改動 | 「算目前那一版的指紋」 | 指紋從被推送提交的檔案樹算(git ls-tree),工作目錄改動不影響;S2 改寫 |
| P5(④1) | code-loop check 既有六道(含安全證據);各自出訊息只在 --keep-going(pre-push);CI 第一道擋下就停;新判定要排在放行早退之前 | 「跟既有的合約測試、表態、新增告警、審查留痕並列」 | 寫明排在放行早退之前、pre-push 與 CI 的差異;新增條款 S11 |
| P6(④2) | pre-push 對 rc1 擋、其餘非零 fail-open | 沒寫 | 寫明判定回 1 才擋、出錯回 2 時 pre-push 照舊放行(既有行為,本計劃不改),列入實務隱患與不做 |
| P7(④4) | --stability 只判寫了 check 的門檻條目;結果有 failures、passed、skipped 三種;沒門檻時只印 stability_unjudged | 只處理沒過與工具沒跑成 | 新增 result=unjudged:會擋的那幾類列在 skipped 或整段 unjudged 都算沒判到、不算通過(可人放行);凍結幀沒判到只提醒;設定節寫明要有 check 門檻條目;S5 改寫 |
| P8(④7) | visual-check.sh 通過時不印相符率、只有不相符才印;回傳碼 0 過、1 不符或環境問題、2 缺基準或參數錯;門檻不准低於 99.5;第二個參數才把差異圖複製到指定處;只在模擬器驗過 | 「相符率不低於門檻」「每個畫面的相符率」「寫出差異圖路徑」 | 改成看回傳碼、只在不相符時記相符率、第二個參數指 run 目錄;設定的 visual_threshold 不得低於 99.5(S1);S4 改寫;狀態列固定列入前置實測 |

存在與定義類(直接修):補〈設定〉一節定義 app_dirs、package、apk、flows、visual、visual_threshold、adb_serial 與既有設定的關係;定義 notices、result 四種值、run-id 預設格式、治理帳事件名 android-e2e-waive;寫明用截圖前要先照 toolkit 的 install.sh 裝好、畫面名對應 flow 與基準圖檔名;「Maestro 驅動範例」改指 skills/lumos-android-evidence/reference.md(那裡已有範例、沒實測),不是 Systems/android-stability-collector;toolkit 腳本路徑改寫成裝進專案後的 `.maestro/visual-check.sh`。另查證 Maestro 2.10.0 的 `--device`/`--udid` 旗標存在。

## 六席收貨

- 六席報告都已正規化(只搬等級宣告的位置),引句對凍結快照全部錨得到。
- 編號:c 正確性、g 守衛、e 邊界、i 整合、n 通才、a 架構對齊,後接各席報告裡的條號(a 席用它自己的 A 號)。
- 兩題超出計劃能自己裁的,拿去問 Enzo:放行權 → 「AI 能放行,但要通知你」;CI 擋合併 → 「第一版只擋本機推送」。兩條都寫成計劃的 WHY。

## 編排者重現表

| id | 宣稱 | 重現 | 結果 | 處置 |
|---|---|---|---|---|
| g1 / i1 | CI 的 code-loop check 在 PR 上不跑;推到主線時範圍為空 | 讀 ci.yml:那一步 `if: github.event_name == 'push'`,推送事件只在 main;判定傳 BEFORE..SHA | HIT | 折(第一版只擋本機推送,Enzo 裁;CI 列不做附 REVISIT) |
| g3 / c14 | tag 與非分支 ref 不跑這道 | 讀 pre-push:只對 refs/heads/* 叫 check;ci.yml 的 tag 工作只跑安全證據 | HIT | 折(列不做,併進同一條 REVISIT) |
| g2 | 設定從被推送提交讀,同提交能關掉判定 | 讀安全證據閘:設定只讀主線版,同一個理由 | HIT | 折(e2e 段只讀主線版;S9) |
| n4 / g4 | 放行太便宜,AI 會自己放行;紀錄檔名沒跟內容比對 | 計劃原文只要 10 字理由;讀 `_confirm_tty`:非互動回 None,分得出人與 AI | HIT | 折(AI 放行標記並在 doctor 列出,Enzo 裁;指紋欄位要等於檔名與重算值;S10、S13、S14) |
| n2 / c4 / i10 | 沒綁「驗的 APK 是這份程式建的」 | 計劃原文沒有建置步驟,APK 路徑由人給 | HIT | 折(範本照 build 指令在乾淨樹上建、記建出與裝置上的 sha、前後比;judge 要求沒有未提交改動;S6、S7) |
| c5 / i5 / n9 | 紀錄從哪讀沒定;放在 app_dirs 底下對不上 | 計劃原文只說「找紀錄」 | HIT | 折(從被推送提交的樹讀;app_dirs 不得包住 .lumos;S1、S10) |
| e1 / c10 | judge 覆蓋會蓋掉放行 | 計劃原文「同指紋覆蓋」 | HIT | 折(runs 與 waivers 分開,waivers 只增不刪;S13) |
| e2 | 紀錄沒有版本欄 | 計劃原文欄位清單沒有 | HIT | 折(schema 欄,新版就擋;S10) |
| e5 | 紀錄壞掉時會變成放行 | 讀 code-loop check 的內部錯誤路徑:接住後 fail-open | HIT | 折(紀錄讀不懂一律回 1,不走 fail-open;S10) |
| e3 / c13 / g6 | 指紋沒定義符號連結、子模組、權限、分隔;目錄外 gradle 檔與驗收素材不算 | 計劃原文只說「目錄內容的雜湊」 | HIT | 折(ls-tree 的 mode、物件編號、路徑,NUL 分隔、位元組排序、整段路徑比對;驗收素材納入;漏列模組由 check-config --env 提醒;S2) |
| g7 | 只改單元測試也要重跑實機 | 計劃原文以 app_dirs 全目錄算 | HIT | 折(預設排除 src/test、src/androidTest,另有 exclude) |
| g8 / c9 | 主線分岔點算不出來時範圍未定 | 讀既有推送範圍算法:新分支首推走 push-range | HIT | 折(用既有算法;算不出走 fail-open 記帳,另附 REVISIT 回頭看次數) |
| i2 / g5 | 「出錯回 2」不是 code-loop check 的既有做法 | 讀 `_gate_failopen`:內部錯誤接住、記帳、放行 | HIT | 折(改寫成照既有做法;只有紀錄讀不懂才擋) |
| i3 / a6 / c11 | 接線漏了種類、擋下訊息、明細、pre-push 對照表與測試 | 讀 `_cl_say_block`、`_codeloop_kg_finish`、pre-push 的 pp_cl_reason 與比對測試 | HIT | 折(〈資料怎麼流〉第 4 步列全;S12) |
| i4 / n9 | 紀錄進版控會讓留痕失效 | 讀 `_BOOKKEEPING_DIRS`:不含 .lumos/e2e-records/ | HIT | 折(加進簿記目錄清單) |
| i8 / a3 | 治理帳數不出放行;新閘名要登記 | 讀 `_KNOWN_GATES` 的清單 | HIT | 折(閘名 android-e2e、種類 waived,登記已知閘名) |
| c1 / i6 | stability 子目錄收集腳本做不到 | 讀收集腳本:輸出固定寫在 run 目錄最上層 stability.json | HIT | 折(照收集腳本放最上層) |
| c2 | macrobench 會吃到上次的舊結果 | 讀 macrobench 設定:結果從 results_dirs 全讀 | HIT | 折(新旗標 --results-dir,只複製這次的結果檔;S15) |
| c3 | judge 的輸入格式沒定 | 計劃原文只說「原始輸出」 | HIT | 折(steps.json:每步回傳碼、時間、每次嘗試的報告路徑;S16) |
| c6 / i9 / n1 | 工具失敗、沒設定的塊、只提醒的塊沒跑成,result 打架 | 計劃原文三處寫法互相矛盾 | HIT | 折(沒設定=未設定不影響;會擋的塊沒跑成→非 pass;只提醒的塊沒跑成→notice;S4–S6) |
| c7 | threshold_failures 混兩類;只設部分 check 會靜默 pass | 讀 `--stability` 判定:只判寫了 check 的門檻條目,其餘不出現 | HIT | 折(只看在 stability_checks 裡的 check;沒出現在任何清單算沒判到;S5) |
| c8 / i7 | toolkit 介面對不上:門檻、裝置、鎖、畫面名 | 讀 visual-check.sh:THRESHOLD 環境變數、DEVICE 由 MAESTRO_DEVICE 覆蓋、`.maestro/.lock-<裝置>`、回傳碼 0/1/2、畫面名帶 _visual | HIT | 折(照實寫;清殘留鎖要先確認沒人在跑) |
| n3 | 沒有取消、裝置占用、併發處理 | 計劃原文範本腳本只有依序步驟 | HIT | 折(開跑前檢查、.e2e-lock、中斷寫「中斷」再 judge;S16) |
| n5 | 紅了看哪裡沒規格 | 計劃原文沒寫輸出內容 | HIT | 折(judge 與擋下訊息印哪一塊沒過、證據或紀錄路徑、要跑的指令) |
| n6 | 人工條款沒有失敗標準 | 計劃原文 S13–S15 只寫要跑 | HIT | 折(S17–S20 各寫什麼算沒過、怎麼分支) |
| n7 | 第一次接入沒有順序 | 計劃原文沒有 | HIT | 折(新增〈第一次接入的順序〉,含 check-config --env) |
| n8 | 效能塊第一版沒驗收力、擋的範圍卻寬 | 對照 Enzo 10-25 選「毫秒類先只提醒」 | HIT | 折(〈實務隱患〉寫明一次驗收的時間代價;RETIRE-IF 改成量得到的放行率與 AI 放行佔比) |
| e4 | 改 app_dirs 讓舊紀錄全失效 | 指紋涵蓋設定本身,改了必變 | HIT | 折(寫明是刻意的、不做遷移) |
| e6 | 時間欄位時區沒定 | 計劃原文只寫「時間」 | HIT | 折(本機時區、帶時差的 ISO 格式) |
| e7 | 紀錄與 run 目錄無限增長、大 repo 指紋成本 | 指紋改用 ls-tree 物件編號,不讀檔 | HIT | 折(寫明大小與成本;清理照產物目錄既有做法) |
| c12 | 10 個字與「誰」沒定義 | 計劃原文只寫「理由至少 10 字」 | HIT | 折(去掉空白後算;誰取 git user.name,沒設取登入帳號) |
| a1 | 綁內容指紋是第二種留痕算法 | 讀安全證據閘:收據逐檔列出比對 | HIT | 折(WHY 寫明為什麼不能逐檔:目錄上萬檔) |
| a2 | 跟收據目錄重疊 | 讀 skill:收據是逐層診斷證據,一次診斷一份 | HIT | 折(WHY 寫明分開的理由) |
| a4 | 另開設定檔、package 與序號重複 | 讀 macrobench.json 已有 stability 段 | HIT | 折(改成同檔 e2e 段,跟 stability 段比對一致) |
| a5 | 範本腳本反過來呼叫 lumos | 讀收集腳本:不呼叫 lumos | HIT | 折(WHY 的代價寫明這點差異與要裝相容 lumos) |
| a7 | lands_in 落點沒對應改動、細節塞大節點 | 計劃原文把 android-stability-collector 列為落點但沒改它 | HIT | 折(拿掉;判定細節寫新家,pitfalls-code-loop 只加連結;補 bound-tests-gate) |

修補對照:修改前的全文存在 scratchpad(未進卷證);修改後就是本次提交的計劃。
