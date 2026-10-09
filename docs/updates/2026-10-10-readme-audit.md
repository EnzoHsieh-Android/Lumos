# Lumos 10/7–10/10 更新與 README 核對（依合併進 main 的時點）

盤點時間：2026-10-10T02:21:40+08:00（Asia/Taipei）。
固定 main 來源：`8e648f3d536220bf7e0ea3c8cd52deed75816595`。範圍取 `20f41c8e..8e648f3d`：上一份清點（[10/1–10/7](2026-10-07-readme-audit.md)）發布的那個提交 20f41c8e 之後，併進 main 的全部提交。這份用「能不能從 main 追溯」篩，不用提交時間篩——PR #48 有一批 10/3–10/4 在分支上寫、10/9 才合併的提交，照合併進 main 的時點算在這份。合併提交、審查帳本和驗證文件都保留，避免把提交數當成功能數。原工作目錄未提交的改動、未合併分支不列。日期是提交時間，不代表部署或發版時間。

共 170 個提交；分類：chore 54, docs 38, feat 10, fix 37, merge 21, test 10。完整清單見文末。

## 依使用者影響分組

| 更新方向 | 代表提交 | 核對入口 | README 處置 |
| --- | --- | --- | --- |
| 測試品質：唯讀掃描可疑測試寫法（Python 四類，其他語言選配本機 Semgrep）、明示執行可信本機測試收證、核對正常→故障→還原證據；各技術棧接入標準（含 PHP／Laravel） | 0d504411、5d8f0ec7、a7ee9fed、25848863、598e41b2、4d17d742、99683f40（#49） | CLI test-quality scan／capabilities／capture／check；skills/lumos-project-notes/commands/test-quality-standard.md | 中文版已有「測試要有用」一節；補英文版對應段落，指令參考補四個子命令 |
| 架構對齊審查可依目錄宣告目標架構：`.lumos/config.json` 的 `arch_targets` 宣告的範圍內，改動照目標架構筆記的 RULE 行審，不再要求跟舊鄰居一致；宣告一律讀跟主線分叉點那一版，被審的分支不能自己放寬 | 30238fbd（#50） | CLI dispatch-lens --arch-target；pitfalls；doctor；code-loop check | README 審查段只講派幾席，不加；留在本盤點 |
| 兩道舊句檢查改成本機推送前擋下：名稱消失檢查（`drift_check.old_sentence`）沒寫子開關時照總開關 `drift_check.gate`，預設擋；回頭重讀改由推送前掛鉤帶 `reread-check --gate`，照 `note_reread.gate`（預設 block）擋兩層——改了程式也改了家筆記卻還沒對照這一版程式的、判定點出的規則類條目還在又沒表態的；CI 與手動跑只提醒；照留用 `lumos drift ack --kind reread`；單次略過 `LUMOS_SKIP_REREAD_CHECK=1`（會留帳） | a7d0e0c4、f80352f6、202da1a4、59f8f92b、40f871bf、5ce8115d（#51） | CLI note-audit reread-check／drift ack／drift check；scripts/hooks/pre-push | 防過期一節原本已寫本機推送擋；補 `drift ack --kind reread`、新增「哪些檢查專案可以調鬆」一段；指令參考補回頭重讀三個指令與專案開關表 |
| 情境探針可靠性：每場從同一份凍結副本重新複製，封住副本的 Git 寫入逸出與工作樹外指；事故（本機全域 skills 連結被動到、副本清不乾淨）整批停下；截斷、撞到用量上限這類壞場次不算分，有效場次不到一半整批不下結論；選配本機用量帳跨批次限制啟動次數；輸出不再卡在沒人讀的管線、不改壞權限 | 2854d961、730b06fe、cfe7a703、8922c3c9、1c91755a、074e91ba、532f5a15、05e87b54、3e149721（#48） | scripts/scenario_probe.py；governance/autonomous-loop.sh 的週跑段 | 評測一節補一段保護說明（README 只留一句，細節在這份清點）；用量帳註明預設不開（週跑沒帶 `--max-per-window`） |
| 只列出、不擋的小提醒：健康檢查列出指向別篇、但那篇已經沒有那條回頭條件的句子；改 `revalidate_when` 時列出別篇引用它的句子；提交時提醒一行綁多支測試要拆開、新寫的數量句要掛標記、更正括號別用位置指清單項目；撤除候選也看只掛 `[manual:]` 的計劃條款；派工鏡頭算不出範圍時在派工詞尾端講一聲 | 68706b1e（#42）、d7a71931（#45）、d85c913e（#41）、07f28120（#39）、2e3d0863（#38）、5cfb4999（#40） | doctor S20／S21；lumos set；note-shape 提交前提醒；dispatch-lens | 指令參考新增「只列出、不擋」一段；README 不逐項寫 |
| 文件與研究：rtb 第三輪提案逐項現況、正文反引號測試名先不查的紀錄、審查席隔離在真 Claude Code 上的實測 | 96a787b3（#47）、cfd54f3f（#34）、14cde462 | 圖譜筆記；docs/ | 不把研究提案或單次實測當已實作 |

純修 bug、使用者看不出差別的（例如凍結判定的暫存檔與同時重凍、強制彩色害測試假紅、`ci-wait` 收短版 sha、測試逾時預算）只在下方完整清單列出，不寫進 README。

## README 本次另修的說法

對照程式重新核對後，修了六處講得比程式更滿的句子：結 Issue 只有 `drift fix --kind c2 --close` 會擋（`lumos set` 只列出）；查詢考卷分數退步只記紀錄、只在沒標過的候選筆記達一成以上時通知；查詢考卷也會順帶考排程腳本指定的另一個專案；3 輪上限與人裁 standard 分級也適用；能調鬆的只有幾類、哪些沒有開關；圖上的金環只是示意、工具沒有「受保護」狀態。

## 發布與核對邊界

遠端 `release` 仍指向 `4a42dede`（9/7；2026-10-10 以 `git ls-remote` 核對）；get.sh 預設 LUMOS_BRANCH=release。README 介紹 main 的能力，不能由本盤點推論 release 安裝已含這些更新。

本盤點確認程式與文件入口；不重跑歷史每一項功能的完整驗證，也不量測真實模型的成效。每筆原驗證、審查與來源可沿下方提交追溯。

## 完整提交清單

| 台北提交時間 | 提交 | 類別 | 更新 |
| --- | --- | --- | --- |
| 10/03 21:11 | [19c55711](https://github.com/EnzoHsieh-Android/Lumos/commit/19c557110b45985a7b3601776d7b41de3c0861a2) | docs | docs: 試行代碼審修復驗證並記錄回顧條件 |
| 10/03 22:01 | [1c91755a](https://github.com/EnzoHsieh-Android/Lumos/commit/1c91755a69616bc1db734b77d3d278337da7460b) | fix | fix: 探針統計排除異常場次 |
| 10/03 22:36 | [9d91cee3](https://github.com/EnzoHsieh-Android/Lumos/commit/9d91cee391ce2f236b97504d7d1d4045bac517a7) | docs | docs: 設計以實際回傳內容驗證探針讀碼 |
| 10/03 22:50 | [4a60b231](https://github.com/EnzoHsieh-Android/Lumos/commit/4a60b231b2a07c8c21ad017764de70572bf2f5b4) | fix | fix: 以成功工具回傳確認探針讀碼 |
| 10/03 23:47 | [637989b1](https://github.com/EnzoHsieh-Android/Lumos/commit/637989b1d16df22512601875f5b8d8ad4bb143ee) | docs | docs: 記錄探針修復三輪未收斂與隔離缺口 |
| 10/04 00:09 | [8922c3c9](https://github.com/EnzoHsieh-Android/Lumos/commit/8922c3c9c11e4234554d94695c31c93973679a99) | fix | fix: 排除不完整讀碼紀錄並封住副本Git寫入逸出 |
| 10/04 01:37 | [13e077c4](https://github.com/EnzoHsieh-Android/Lumos/commit/13e077c45cada7797cc3442a7748e87b806b087c) | docs | docs: 記錄第四輪審查未通過與圖譜驗證 |
| 10/04 02:54 | [88752a29](https://github.com/EnzoHsieh-Android/Lumos/commit/88752a2970f9bb54bdce7df929ef0a6e26b0ff0c) | docs | docs: 訂清探針副本隔離與失敗處置 |
| 10/04 03:21 | [2854d961](https://github.com/EnzoHsieh-Android/Lumos/commit/2854d961675480d44209ff1ad272f560e95b8beb) | fix | fix: 隔離每場探針並在清理失敗時停批 |
| 10/04 04:02 | [730b06fe](https://github.com/EnzoHsieh-Android/Lumos/commit/730b06fe2eb4b159ae0ae2e109e8b3ffa7daea40) | fix | fix: 補齊探針副本邊界與逐場紀錄 |
| 10/04 04:28 | [cfe7a703](https://github.com/EnzoHsieh-Android/Lumos/commit/cfe7a703c7e9687f9bf8aa38ac339a6c31a4cb74) | fix | fix: 擋住工作樹外指與真身分滲入探針 |
| 10/04 04:47 | [87b39887](https://github.com/EnzoHsieh-Android/Lumos/commit/87b398877c21e3e8e9d4294f17936abbb47a231f) | docs | docs: 記錄探針第三輪未收斂與驗證結果 |
| 10/04 11:59 | [d13b52b8](https://github.com/EnzoHsieh-Android/Lumos/commit/d13b52b83d0290f715f395fff609358ddd39aa8a) | fix | fix: 拒收健康不可判的探針批次 |
| 10/04 12:01 | [9f8f39d4](https://github.com/EnzoHsieh-Android/Lumos/commit/9f8f39d47b67651046b32fe8d1ed0a2bced902d5) | docs | docs: 記錄第四輪送審前的邊界驗證 |
| 10/04 12:17 | [1b9d8fe1](https://github.com/EnzoHsieh-Android/Lumos/commit/1b9d8fe15051a2978b4b02a8b5f0cad5fa4abba2) | fix | fix: 舊事故檔與不完整結果都停止探針批次 |
| 10/04 12:28 | [79d3f371](https://github.com/EnzoHsieh-Android/Lumos/commit/79d3f3714236ef1316155019e3d281f168ef31ce) | fix | fix: 不完整探針結果讓整批維持失效 |
| 10/04 12:46 | [70e9ff16](https://github.com/EnzoHsieh-Android/Lumos/commit/70e9ff1647853b2fe8d33947e07f35f24a27494b) | docs | docs: 記錄探針第四輪驗證與外部對照 |
| 10/04 12:48 | [5090d4ff](https://github.com/EnzoHsieh-Android/Lumos/commit/5090d4ff55d150a90b42448aea7a77713d0e9582) | docs | docs: 凍結探針第四輪審查判定 |
| 10/04 12:49 | [e8801749](https://github.com/EnzoHsieh-Android/Lumos/commit/e8801749d2c7b0742537a812fbaf7896535d9c70) | chore | chore(lumos): 記錄代碼審通過 |
| 10/04 13:17 | [5fcdf6ce](https://github.com/EnzoHsieh-Android/Lumos/commit/5fcdf6ce9f3e94ce709b546b81fef9bfa0f286e5) | test | test: 釘住探針事故停派與失敗留痕缺口 |
| 10/04 13:17 | [5ed04382](https://github.com/EnzoHsieh-Android/Lumos/commit/5ed04382897d0cc1579c264cf62ac6e9153011c0) | docs | docs: 凍結探針停派設計審判定 |
| 10/04 14:05 | [074e91ba](https://github.com/EnzoHsieh-Android/Lumos/commit/074e91ba431c0f986bb47d6fc5cbdee1e51ca188) | fix | fix: 探針事故後停止派工並保留失敗紀錄 |
| 10/04 14:05 | [454fa427](https://github.com/EnzoHsieh-Android/Lumos/commit/454fa427531de46f21fa14629df6581c776db6ca) | docs | docs: 補記命令列測試假綠案例 |
| 10/04 14:12 | [86dcb404](https://github.com/EnzoHsieh-Android/Lumos/commit/86dcb4045d7c711d849ec0152595d3b79f8eb939) | docs | docs: 記錄合約檢查與新版表態 |
| 10/07 12:32 | [14cde462](https://github.com/EnzoHsieh-Android/Lumos/commit/14cde4628ea7a507382d5bc557225931ac2f6442) | docs | docs: 記錄審查席隔離在真的 Claude Code 上的實測結果 |
| 10/07 12:55 | [fc0332d5](https://github.com/EnzoHsieh-Android/Lumos/commit/fc0332d58c06d6ac67ecb4e53d3f182cad6751ed) | merge | Merge pull request #37 from EnzoHsieh-Android/guard-realtest |
| 10/07 12:56 | [328d76e9](https://github.com/EnzoHsieh-Android/Lumos/commit/328d76e9e18610b138487bf17a7faffe16b3861a) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 12:56 | [cff5dcca](https://github.com/EnzoHsieh-Android/Lumos/commit/cff5dcca4fb495482ec876cad0cd26baed7f814b) | merge | Merge remote-tracking branch 'origin/main' |
| 10/07 12:57 | [5fb11add](https://github.com/EnzoHsieh-Android/Lumos/commit/5fb11addbf3c81ba02b4adcac1336d60887eed3d) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 13:03 | [cfd54f3f](https://github.com/EnzoHsieh-Android/Lumos/commit/cfd54f3f23a5340291c9011552782944277e5f24) | docs | docs: 記下正文反引號裡的測試名沒人查(實測誤報多,先不做) |
| 10/07 13:03 | [23d05227](https://github.com/EnzoHsieh-Android/Lumos/commit/23d05227af9b098ec9b5e244faf804641ac83559) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 13:03 | [ae3936e1](https://github.com/EnzoHsieh-Android/Lumos/commit/ae3936e160f27c899e78d20cb98b921512b63af8) | fix | fix: ci-wait 給短版 sha 時先換成完整的再查 |
| 10/07 13:03 | [55d3d1fd](https://github.com/EnzoHsieh-Android/Lumos/commit/55d3d1fd6961ab407edf1ed048dd4634eae391c9) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 13:03 | [d4936bb3](https://github.com/EnzoHsieh-Android/Lumos/commit/d4936bb33e89fc9abcdba1b65befb6c40d2e6876) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 14:34 | [53263694](https://github.com/EnzoHsieh-Android/Lumos/commit/53263694cb5061fcf35869318cdd37c142f2db29) | merge | Merge pull request #34 from EnzoHsieh-Android/body-test-names |
| 10/07 14:35 | [2e3d0863](https://github.com/EnzoHsieh-Android/Lumos/commit/2e3d0863089e46e7d3e71cc884b4c3ae49c8e49c) | feat | feat: 撤除候選也看掛 [manual:] 的計劃條款 |
| 10/07 14:36 | [563b60e9](https://github.com/EnzoHsieh-Android/Lumos/commit/563b60e9c9af5496711db316ae247598f1ad5949) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 15:27 | [ac7a8444](https://github.com/EnzoHsieh-Android/Lumos/commit/ac7a8444229c024db4e8c1f01f5ffddfcb691657) | merge | Merge pull request #38 from EnzoHsieh-Android/manual-retire-candidates |
| 10/07 16:41 | [07f28120](https://github.com/EnzoHsieh-Android/Lumos/commit/07f2812098e2f2b01a94f6d076a9ba92efe6279e) | feat | feat: 提交時提醒新寫的數量句掛標記、更正括號別用位置指項目 |
| 10/07 16:41 | [8923eb78](https://github.com/EnzoHsieh-Android/Lumos/commit/8923eb78ab4a62fa0095f2abd7f44e58b37e6838) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 17:39 | [c7b7eb15](https://github.com/EnzoHsieh-Android/Lumos/commit/c7b7eb15ecb42731dca9298b4f325cf3ae4a7812) | merge | Merge pull request #39 from EnzoHsieh-Android/note-nudge |
| 10/07 17:44 | [5cfb4999](https://github.com/EnzoHsieh-Android/Lumos/commit/5cfb4999ee8903fbd6a4b37a94e2b99f00f137d3) | fix | fix: 派工鏡頭在會談專案算不出範圍時講一聲,不再靜默放空 |
| 10/07 17:44 | [beb7c4d5](https://github.com/EnzoHsieh-Android/Lumos/commit/beb7c4d58b44d2eebad1bc937488e8e8b1b09d40) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 18:32 | [95f69031](https://github.com/EnzoHsieh-Android/Lumos/commit/95f690318191f68e32fc6d8afb8c1fbb03b8806c) | merge | Merge pull request #40 from EnzoHsieh-Android/lens-cross-repo |
| 10/07 20:00 | [68706b1e](https://github.com/EnzoHsieh-Android/Lumos/commit/68706b1eebc079027dfbd05b498cc025dd50bff6) | feat | feat: doctor 列出指向別篇、但那篇已經沒有的回頭條件 |
| 10/07 20:00 | [ed207b60](https://github.com/EnzoHsieh-Android/Lumos/commit/ed207b60914260bbbf695d3a1585c699d1d9b420) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 20:34 | [0d504411](https://github.com/EnzoHsieh-Android/Lumos/commit/0d504411e0fb2c12dcfba470c097f6f2af3f83e7) | feat | feat: 掃描測試判準並保留跨語言驗證證據 |
| 10/07 20:57 | [e0642ed0](https://github.com/EnzoHsieh-Android/Lumos/commit/e0642ed0947198aa1fc40d5d6c7619e316c34ef0) | merge | Merge pull request #42 from EnzoHsieh-Android/revisit-ref-dangling |
| 10/07 21:00 | [2c5ab47b](https://github.com/EnzoHsieh-Android/Lumos/commit/2c5ab47bd02cfd5307f87f71547d560b4bfada1b) | test | test: 比較測試手冊措辭並保留無效場次與覆蓋缺口 |
| 10/07 21:08 | [d85c913e](https://github.com/EnzoHsieh-Android/Lumos/commit/d85c913ecb33ff530f22376458ad2f44683c4b91) | feat | feat: 提交時提醒一行綁好幾支測試要拆成一支一行 |
| 10/07 21:08 | [299697cf](https://github.com/EnzoHsieh-Android/Lumos/commit/299697cff147a3faefaae99f332aa308e11f1c2a) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 21:33 | [5d7add9c](https://github.com/EnzoHsieh-Android/Lumos/commit/5d7add9cb21bebe2065e54cb35015af6fec27681) | test | test: 重驗手冊人工推導與原生技能觸發 |
| 10/07 21:52 | [6adb9bf1](https://github.com/EnzoHsieh-Android/Lumos/commit/6adb9bf13c7fad77be59291eb3f4d39fc987d316) | test | test: 重播修復引入回歸卻被弱測試漏掉的歷史案例 |
| 10/07 21:59 | [ba3268f1](https://github.com/EnzoHsieh-Android/Lumos/commit/ba3268f16aa5d94556c74448e6269bf456745b36) | merge | Merge pull request #41 from EnzoHsieh-Android/test-reason |
| 10/07 22:00 | [13bc7227](https://github.com/EnzoHsieh-Android/Lumos/commit/13bc72275a28f4fa7e8d817abd0d948858932b5b) | fix | fix: 殼裡設了強制彩色時測試不再假紅 |
| 10/07 22:00 | [17019a52](https://github.com/EnzoHsieh-Android/Lumos/commit/17019a5285aa9929dd61571b4cb7527b4ae72065) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 22:11 | [3717917e](https://github.com/EnzoHsieh-Android/Lumos/commit/3717917ec0e868976c358b822b612f6df4f76649) | test | test: 用歷史鎖回歸比較手冊前後的首次測試 |
| 10/07 22:45 | [b1af81a9](https://github.com/EnzoHsieh-Android/Lumos/commit/b1af81a98ff0f92b8382f659963b92f2d2f19775) | test | test: 減少歷史鎖案例提示並記錄停止條件 |
| 10/07 22:54 | [0dcc102e](https://github.com/EnzoHsieh-Android/Lumos/commit/0dcc102e753e66e019a24c1ec391e53ff034998f) | merge | Merge pull request #43 from EnzoHsieh-Android/test-no-color |
| 10/07 22:55 | [0ca72480](https://github.com/EnzoHsieh-Android/Lumos/commit/0ca724805e3a2be156a6ad972067d330e3d3f2c1) | fix | fix: 凍結判定被擋下或寫到一半失敗時不再留下暫存檔 |
| 10/07 22:55 | [bab01e8a](https://github.com/EnzoHsieh-Android/Lumos/commit/bab01e8ada8a2e10449b67fce289a8c45be70716) | chore | chore(lumos): 記錄代碼審通過 |
| 10/07 23:09 | [fab5309c](https://github.com/EnzoHsieh-Android/Lumos/commit/fab5309cdde3c14cf0bc821054298205d8b8038a) | test | test: 建立不同失效形態的歷史測試案例集 |
| 10/08 00:03 | [a7ee9fed](https://github.com/EnzoHsieh-Android/Lumos/commit/a7ee9fedc883b513ebdacecd3d992e7b60e74e98) | test | test: 驗證測試證據並建立各技術棧接入標準 |
| 10/08 00:04 | [5de06fa7](https://github.com/EnzoHsieh-Android/Lumos/commit/5de06fa77de0ee949f26f67cf7d60257d1898e2b) | merge | Merge pull request #44 from EnzoHsieh-Android/verdict-tmp |
| 10/08 00:10 | [d7a71931](https://github.com/EnzoHsieh-Android/Lumos/commit/d7a71931288957a2e6e8e3ad311cf0383ad009a4) | feat | feat: 改重驗事件時列出別篇引用它的句子 |
| 10/08 00:15 | [37bd83ec](https://github.com/EnzoHsieh-Android/Lumos/commit/37bd83eccc4fe484a4b052bb0c47cb687306929b) | chore | chore(lumos): 記錄代碼審通過 |
| 10/08 00:36 | [25848863](https://github.com/EnzoHsieh-Android/Lumos/commit/2584886347da0f425b3af6e4221538f174ea8d45) | docs | docs: 補上 PHP 與 Laravel 的測試品質接入要求 |
| 10/08 02:02 | [b960e984](https://github.com/EnzoHsieh-Android/Lumos/commit/b960e984a00f185f12582bee92021d79381ee7f9) | merge | Merge pull request #45 from EnzoHsieh-Android/revalidate-ref-check |
| 10/08 02:03 | [96a787b3](https://github.com/EnzoHsieh-Android/Lumos/commit/96a787b3fc8585904e763fdc4412f17e13b47e73) | docs | docs: 記下 rtb 第三輪提案逐項現況,回傳第 11–14 項先不做 |
| 10/08 02:08 | [dff63d00](https://github.com/EnzoHsieh-Android/Lumos/commit/dff63d00ca41cfb4c1e9bbef83a182a8b3544619) | chore | chore(lumos): 記錄代碼審通過 |
| 10/08 02:59 | [9377d79a](https://github.com/EnzoHsieh-Android/Lumos/commit/9377d79a68c7e073659dab168d3fb0d0a169ef4c) | merge | Merge pull request #47 from EnzoHsieh-Android/rtb-proposal-status |
| 10/08 10:48 | [7e61a0de](https://github.com/EnzoHsieh-Android/Lumos/commit/7e61a0de7dd91e746472ba31517677c82949e4ad) | fix | fix: 兩個凍結同時跑時,寫入端也擋下沒帶理由的重凍 |
| 10/08 10:48 | [ff3f556c](https://github.com/EnzoHsieh-Android/Lumos/commit/ff3f556c86e81a8f6aeaba3563e191aac5943aba) | chore | chore(lumos): 記錄代碼審通過 |
| 10/08 12:55 | [6467401a](https://github.com/EnzoHsieh-Android/Lumos/commit/6467401a7012bb39acb3d5be064bb88758f45818) | merge | Merge pull request #46 from EnzoHsieh-Android/freeze-race |
| 10/08 12:58 | [5d8f0ec7](https://github.com/EnzoHsieh-Android/Lumos/commit/5d8f0ec7045638dcc9c9f21e7fc9e0aff562eca7) | feat | feat: 接通多技術棧測試品質掃描與故障證據驗證 |
| 10/08 13:43 | [598e41b2](https://github.com/EnzoHsieh-Android/Lumos/commit/598e41b23f85285d1f9e4429c5d5314f055fc8bc) | fix | fix: 修正測試收證與部署邊界並保留驗證紀錄 |
| 10/08 14:50 | [4d17d742](https://github.com/EnzoHsieh-Android/Lumos/commit/4d17d74208922e40f7cfd70ca437914a6bfa00bd) | fix | fix: 拒收混裝測試工具並補齊修復回歸控制 |
| 10/08 14:52 | [03a46da6](https://github.com/EnzoHsieh-Android/Lumos/commit/03a46da6b5179cfc5b42ced08e257ee127cc654e) | docs | docs: 補齊修復重验理由與測試入口責任 |
| 10/08 16:12 | [532f5a15](https://github.com/EnzoHsieh-Android/Lumos/commit/532f5a15c05ce547c8305e0d30492e5d3c8845a0) | fix | fix: 保留探針失敗證據並限制批次派工 |
| 10/08 16:23 | [76bb9bad](https://github.com/EnzoHsieh-Android/Lumos/commit/76bb9bad4c14462e0b630c135d1da947cd0cc1fc) | fix | fix: 防止消融結果灌分並補齊事故恢復清單 |
| 10/08 16:29 | [6c833b6e](https://github.com/EnzoHsieh-Android/Lumos/commit/6c833b6e24cf44e90e3fa400396806379fc4f919) | docs | docs: 保留第三輪審查未通過與分席驗證紀錄 |
| 10/08 16:39 | [0f3b89a8](https://github.com/EnzoHsieh-Android/Lumos/commit/0f3b89a8179c46686c896609b46421b7d09eb884) | fix | fix: 保留消融來源證據並轉義報表文字 |
| 10/08 17:08 | [05e87b54](https://github.com/EnzoHsieh-Android/Lumos/commit/05e87b5476cf161a203382a50ef008b374e60a31) | fix | fix: 讓失敗探針與跨日派工共用持久額度 |
| 10/08 19:40 | [7949784a](https://github.com/EnzoHsieh-Android/Lumos/commit/7949784a20a52d967641f432529bb5b17ea02a58) | docs | docs: 記錄持久用量帳第四輪審查停點 |
| 10/08 21:01 | [39dc3ee0](https://github.com/EnzoHsieh-Android/Lumos/commit/39dc3ee09d81e5c5705d9680c20a14dee1d9d4bf) | fix | fix: 封住探針輸出與等待邊界 |
| 10/08 21:10 | [782829d0](https://github.com/EnzoHsieh-Android/Lumos/commit/782829d0a94c56b6e1b458e565e9181faf1410fa) | fix | fix: 補齊測試品質工具的錯誤路徑 |
| 10/08 21:30 | [10d40f30](https://github.com/EnzoHsieh-Android/Lumos/commit/10d40f3009ba136db53b5a071d552395ba2ccbe1) | fix | fix: 統一測試指令的程序清理 |
| 10/08 21:44 | [4d765d5c](https://github.com/EnzoHsieh-Android/Lumos/commit/4d765d5c39a0fbd48b333b25ff32f74710cec01c) | fix | fix: 避免TTY確認讓測試程序收到掛斷 |
| 10/08 22:00 | [c4982cb1](https://github.com/EnzoHsieh-Android/Lumos/commit/c4982cb1bf19f76f162a627d483e0a7ea55f1769) | fix | fix: 收齊測試後端留下的背景程序 |
| 10/08 22:09 | [7d1975e8](https://github.com/EnzoHsieh-Android/Lumos/commit/7d1975e81e49b8af6eb665f7466c831f23f6cc04) | docs | docs: 補上修補前因說明並備妥下一輪審查材料 |
| 10/08 22:37 | [b4cf45a2](https://github.com/EnzoHsieh-Android/Lumos/commit/b4cf45a2996d26b83ab3f14353d7e81d8fdefc90) | fix | fix: 探針輸出不再改壞權限並在開跑前檢查寫入位置 |
| 10/08 22:37 | [483df9fe](https://github.com/EnzoHsieh-Android/Lumos/commit/483df9fe6e363b4078553aea358b8abe4d3ef3e2) | docs | docs: 更正終端確認的防回歸測試說明 |
| 10/08 22:48 | [a2f30b19](https://github.com/EnzoHsieh-Android/Lumos/commit/a2f30b1999b861f48565e79e982490fd72f081ce) | fix | fix: 模型命令與 Semgrep 後端共用同一套程序清理 |
| 10/08 22:58 | [388c4459](https://github.com/EnzoHsieh-Android/Lumos/commit/388c4459db11fcb0d92458fd2979ff576690519f) | docs | docs: 記下第三輪跑滿回顧並備妥加開一輪的審查材料 |
| 10/08 23:34 | [c70b3d6a](https://github.com/EnzoHsieh-Android/Lumos/commit/c70b3d6afc830807d0d61181df448acb3aa1bb81) | fix | fix: 模型輸出過大或清理撞到權限錯誤時不再中止整場評測 |
| 10/09 00:04 | [3e149721](https://github.com/EnzoHsieh-Android/Lumos/commit/3e149721b66f33346385dec40d1ae690a0763402) | fix | fix: 探針輸出不再卡在沒人讀的管線,寫入前檢查與寫入規則一致 |
| 10/09 00:20 | [ec3ef4c1](https://github.com/EnzoHsieh-Android/Lumos/commit/ec3ef4c1109bb82b10e381814022742dc4a57385) | docs | docs: 記錄第六輪處置閘、修正關卡與派工鏡頭測試逾時診斷 |
| 10/09 00:22 | [67b1dea2](https://github.com/EnzoHsieh-Android/Lumos/commit/67b1dea2d1e9dc7ac7a456b862d1ea7e04bc61cf) | merge | chore: 併入遠端主線並解決衝突 |
| 10/09 00:24 | [9a82fd9a](https://github.com/EnzoHsieh-Android/Lumos/commit/9a82fd9aba410b367858be11288a8692cbe4dfb8) | docs | docs: 記下接受剩餘風險的裁定與四輪審查回顧 |
| 10/09 00:31 | [f69ad21e](https://github.com/EnzoHsieh-Android/Lumos/commit/f69ad21e1361522c6407936875219025f71302c4) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 00:36 | [1b862462](https://github.com/EnzoHsieh-Android/Lumos/commit/1b86246212ad1467e534049da7cc427b8b32046c) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 00:55 | [da046ddf](https://github.com/EnzoHsieh-Android/Lumos/commit/da046ddf3596e3e4d78ee2efded558c8366b8d19) | fix | fix: 探針寫進終端不再搶走控制終端,報表控制字元改用主程式同一套寫法 |
| 10/09 00:57 | [e5ce8675](https://github.com/EnzoHsieh-Android/Lumos/commit/e5ce86756ee6b716c40c03e404982f07026b2d9b) | docs | docs: 終端確認的重驗改指向真的抓得到問題的測試 |
| 10/09 01:29 | [6acb5eeb](https://github.com/EnzoHsieh-Android/Lumos/commit/6acb5eeb0b9418aaf25fd2424396d37ebcc4cbf0) | test | test: 報表控制字元改成直接比對主程式的類別集合,並修正幾處說法 |
| 10/09 03:31 | [fc341775](https://github.com/EnzoHsieh-Android/Lumos/commit/fc3417752e7f21700c7f39ccfafc35ec89c7835b) | docs | docs: 記錄探針輸出修補的審查處置、凍結判定與最終全套結果 |
| 10/09 03:32 | [2e2f2efe](https://github.com/EnzoHsieh-Android/Lumos/commit/2e2f2efeb8e91c3fdfc7e87aa92cd00568735d80) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 03:40 | [6de1a0cd](https://github.com/EnzoHsieh-Android/Lumos/commit/6de1a0cd81051d5f4e4dd68a279cad26571fd226) | docs | docs: 記錄探針與消融腳本累積的函式複雜度,附理由放行並開單追蹤拆分 |
| 10/09 03:40 | [df954c8c](https://github.com/EnzoHsieh-Android/Lumos/commit/df954c8c96dcedbe08deec1cdfc1ca9e84d1d65a) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 03:41 | [e9d539fd](https://github.com/EnzoHsieh-Android/Lumos/commit/e9d539fd578aa434de568cb2cd676e328cfd0bf6) | chore | chore: 登記新增探針邊界測試後的測試檔版本 |
| 10/09 03:41 | [c3c2b886](https://github.com/EnzoHsieh-Android/Lumos/commit/c3c2b886a82efeb9cdb9a5bb82c76915cd3dc9ef) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 03:43 | [44928727](https://github.com/EnzoHsieh-Android/Lumos/commit/4492872706878ad83a16e9bb1d9f0c7f46cf6fcd) | docs | docs: 消融腳本筆記兩條防回歸改寫成實際測試所在,不再冒充可自動跑的測試綁定 |
| 10/09 03:43 | [a0020cc7](https://github.com/EnzoHsieh-Android/Lumos/commit/a0020cc76852051ca32f6ff425964ca898768f52) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 03:48 | [fbc170c1](https://github.com/EnzoHsieh-Android/Lumos/commit/fbc170c14905fe7942bdbb26a66d1b8378d9774f) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 03:54 | [ebb34633](https://github.com/EnzoHsieh-Android/Lumos/commit/ebb346336a8e3808511f826a265761bd0289ac9e) | chore | chore: 對改到探針與消融腳本觸發的兩條回頭條件表態照留 |
| 10/09 04:47 | [f605fecb](https://github.com/EnzoHsieh-Android/Lumos/commit/f605fecb60595f111164c744d4a04f9e7e7513ee) | merge | Merge pull request #48 from EnzoHsieh-Android/EnzoHsieh-Android/fix-code-review-convergence-main-sync |
| 10/09 05:00 | [348accc5](https://github.com/EnzoHsieh-Android/Lumos/commit/348accc526911a6acf8b7a3fe433b1fcc2af1222) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 05:01 | [98e92aad](https://github.com/EnzoHsieh-Android/Lumos/commit/98e92aad96bb5d03653d04fb6755a735a0a5ac28) | merge | chore: 併入主線最新改動 |
| 10/09 05:09 | [94e2bb4d](https://github.com/EnzoHsieh-Android/Lumos/commit/94e2bb4d3a8a7d009bb6809d02a4b6a5ab80a071) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 07:23 | [534a73fc](https://github.com/EnzoHsieh-Android/Lumos/commit/534a73fc35aa8555a9750c5877da70cd3a514301) | fix | fix: 讓測試品質指令跟指令說明、文件與掛鉤清單對齊 |
| 10/09 07:26 | [8c60962e](https://github.com/EnzoHsieh-Android/Lumos/commit/8c60962e8fc17bb52a0eedd1dafced48fd6eac11) | docs | docs: 指令全覽與總目錄的測試品質條目跟鄰居寫法一致 |
| 10/09 07:26 | [9ddeec85](https://github.com/EnzoHsieh-Android/Lumos/commit/9ddeec85f01c64e9771235b0699b238a44466f9c) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 08:50 | [1ddc7d4c](https://github.com/EnzoHsieh-Android/Lumos/commit/1ddc7d4c7c4a70444ec3f8ef8e48a17d83d8e290) | docs | docs: 舊句兩道轉擋計劃初稿(設計審前) |
| 10/09 09:07 | [75bfa634](https://github.com/EnzoHsieh-Android/Lumos/commit/75bfa6343e7b14cbb01915d83cff8aede77af674) | docs | docs: 舊句兩道轉擋計劃折入第一輪設計審 |
| 10/09 09:07 | [966ce9c8](https://github.com/EnzoHsieh-Android/Lumos/commit/966ce9c8b04df8a366eddb58c38668a201f57385) | chore | chore: 記錄舊句兩道轉擋第一輪設計審帳 |
| 10/09 09:51 | [9fffa5d5](https://github.com/EnzoHsieh-Android/Lumos/commit/9fffa5d58f007a76d8398f2ed37f8c33dfbabf1c) | test | test: 放寬三支逾時測試的時間預算，避免全套並行時偶發紅 |
| 10/09 09:51 | [125baee1](https://github.com/EnzoHsieh-Android/Lumos/commit/125baee1527b2177eaaa0769a6c2bca2264a0990) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 09:58 | [3993ca76](https://github.com/EnzoHsieh-Android/Lumos/commit/3993ca76c682da1dbf6ce4fbbe5d010247b965cd) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 10:01 | [be4ee23d](https://github.com/EnzoHsieh-Android/Lumos/commit/be4ee23dd94d478f999db6e872c7c35dedbd923d) | docs | docs: 舊句兩道轉擋計劃折入第二輪設計審與人裁 |
| 10/09 10:01 | [b51fef6c](https://github.com/EnzoHsieh-Android/Lumos/commit/b51fef6c7572d7d1eb35d8cb6b5fdcffc7d91c1a) | chore | chore: 記錄舊句兩道轉擋第二輪設計審帳 |
| 10/09 10:16 | [dc3b5e6c](https://github.com/EnzoHsieh-Android/Lumos/commit/dc3b5e6c6f343ab14ddb75587302ab25d6a8113d) | docs | docs: 部署配套校驗計劃改走設計審 |
| 10/09 10:19 | [569257a9](https://github.com/EnzoHsieh-Android/Lumos/commit/569257a9de5e44f38aadf8c35d0ed5d23b311b79) | docs | docs: 舊句兩道轉擋計劃折入第三輪設計審 |
| 10/09 10:19 | [6b30da03](https://github.com/EnzoHsieh-Android/Lumos/commit/6b30da0384a637f93d74fa9666e721ab4ace831b) | chore | chore: 記錄舊句兩道轉擋第三輪設計審帳 |
| 10/09 10:19 | [742c1fc9](https://github.com/EnzoHsieh-Android/Lumos/commit/742c1fc9849e085000cf14b1e8d870623d4a81a9) | docs | docs: 凍結舊句兩道轉擋設計審判定 |
| 10/09 10:52 | [a7d0e0c4](https://github.com/EnzoHsieh-Android/Lumos/commit/a7d0e0c44497727b919b16ab9e23e4941619c785) | feat | feat: 舊句檢查沒寫開關時照總開關,預設擋下 |
| 10/09 10:56 | [99683f40](https://github.com/EnzoHsieh-Android/Lumos/commit/99683f4065ee89eaca589c1c0b6a39dd939645fd) | fix | fix: 測試品質輔助檔一律從驗過的內容載入，不再吃到舊快取 |
| 10/09 10:56 | [60083648](https://github.com/EnzoHsieh-Android/Lumos/commit/600836482707ffbd968488105f599a62d5f23b34) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 11:09 | [16720222](https://github.com/EnzoHsieh-Android/Lumos/commit/16720222452e947941a57f997a7b6c4355dd55fa) | docs | docs: 處理推送時成立的五條回頭條件 |
| 10/09 11:16 | [0f7f8733](https://github.com/EnzoHsieh-Android/Lumos/commit/0f7f8733b86dbc1219d34bd6cfa6510039e9968b) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 11:28 | [fade5a91](https://github.com/EnzoHsieh-Android/Lumos/commit/fade5a9141b06db9a108d74cb66eead8daf3393b) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 11:52 | [f80352f6](https://github.com/EnzoHsieh-Android/Lumos/commit/f80352f6edde4b99057fc930be367616b689aa3f) | feat | feat: 回頭重讀在本機推送前預設擋下,判定點出的規則行要改掉或表態 |
| 10/09 15:18 | [202da1a4](https://github.com/EnzoHsieh-Android/Lumos/commit/202da1a427fb81b42114f5884d2d44d39b3e1225) | fix | fix: 回頭重讀寫得出讀不了的紀錄、測試被單次略過變數弄紅等代碼審發現 |
| 10/09 15:19 | [69ac44b2](https://github.com/EnzoHsieh-Android/Lumos/commit/69ac44b20d6fcd13929203ef0c7e5d567bf777e6) | merge | Merge pull request #49 from EnzoHsieh-Android/audit/implementation-test-quality-oct07 |
| 10/09 15:28 | [5ce8115d](https://github.com/EnzoHsieh-Android/Lumos/commit/5ce8115d46bb84fdc0847bfa513716ed3672f74b) | fix | fix: 舊句檢查的超長行只在名稱整字出現時才算判不了 |
| 10/09 15:30 | [cd1e366b](https://github.com/EnzoHsieh-Android/Lumos/commit/cd1e366b182f55431ecc811b38e2ce02a1debcdd) | chore | chore: 記錄舊句兩道轉擋代碼審第一輪卷證與帳 |
| 10/09 15:31 | [d4fa4c94](https://github.com/EnzoHsieh-Android/Lumos/commit/d4fa4c94f766a4bbbb10649237866f279c9a5174) | chore | chore: 記錄舊句兩道轉擋代碼審第一輪修正紀錄 |
| 10/09 15:31 | [0ddf6583](https://github.com/EnzoHsieh-Android/Lumos/commit/0ddf6583fbe30bf5219035cfa6fa38b1afbc1528) | chore | chore: 補舊句兩道轉擋第一輪修正紀錄的分組說明 |
| 10/09 15:39 | [429d912d](https://github.com/EnzoHsieh-Android/Lumos/commit/429d912d391d0a06bb72073ca13050652769dc0e) | chore | chore: 記錄舊句兩道轉擋實作與代碼審期間的治理帳 |
| 10/09 15:39 | [88322e46](https://github.com/EnzoHsieh-Android/Lumos/commit/88322e464a55b777d78a713a1ff736ad42b5681e) | merge | Merge remote-tracking branch 'Lumos/main' into EnzoHsieh-Android/reread-block |
| 10/09 18:10 | [59f8f92b](https://github.com/EnzoHsieh-Android/Lumos/commit/59f8f92b1446fe7db9e63aa0459027b58800175f) | fix | fix: 回頭重讀的帳真正壓在 4 KB 內、壞紀錄不再讓 prepare 崩潰、提交提示改列具體檔名 |
| 10/09 18:24 | [a4d42fea](https://github.com/EnzoHsieh-Android/Lumos/commit/a4d42feabfae022c5c4cec0f751a4b1364bab665) | chore | chore: 補舊句兩道轉擋修補後的審查卷證與帳 |
| 10/09 20:01 | [40f871bf](https://github.com/EnzoHsieh-Android/Lumos/commit/40f871bfe497fad5d19925cc8b68c5cf41fc78b9) | fix | fix: 回頭重讀不再讀 repo 外的紀錄、深層巢狀設定檔不再讓推送前閘崩潰 |
| 10/09 20:13 | [2b4095aa](https://github.com/EnzoHsieh-Android/Lumos/commit/2b4095aa4def83caff66b4a88ff2ef50295a7e05) | chore | chore: 補舊句兩道轉擋上限輪的審查卷證與帳 |
| 10/09 20:26 | [a36b9633](https://github.com/EnzoHsieh-Android/Lumos/commit/a36b9633a1675052a5eedcc1505c830366802736) | chore | chore: 記錄舊句兩道轉擋代碼審跑滿上限的人裁與回顧 |
| 10/09 20:53 | [fefe4b39](https://github.com/EnzoHsieh-Android/Lumos/commit/fefe4b3914fdcf0df72f5c6497367c0fd53921be) | chore | chore: 補舊句兩道轉擋加開一輪的審查卷證,登記改過的測試檔與掛鉤版本 |
| 10/09 20:54 | [bdfb8f14](https://github.com/EnzoHsieh-Android/Lumos/commit/bdfb8f14f5cc2410420a620e6e41880145b0684b) | chore | chore: 凍結舊句兩道轉擋代碼審的判定 |
| 10/09 20:58 | [30238fbd](https://github.com/EnzoHsieh-Android/Lumos/commit/30238fbd9d98b803285d6d6f7c3f7fd9f25f3744) | feat | feat: 架構對齊審查可依目錄宣告目標架構當基準 |
| 10/09 20:58 | [f4d512ea](https://github.com/EnzoHsieh-Android/Lumos/commit/f4d512ea290bc6c23ea7a1f0efd441a787f21825) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 21:02 | [8c3300b1](https://github.com/EnzoHsieh-Android/Lumos/commit/8c3300b120277419512d66ffbb2a806debee5392) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 21:39 | [56868a24](https://github.com/EnzoHsieh-Android/Lumos/commit/56868a24eade774b030e998042dd36c9070eff08) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 21:39 | [322a6155](https://github.com/EnzoHsieh-Android/Lumos/commit/322a6155959768099ab20dc697806b4f7555cd0c) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 21:41 | [a2c10461](https://github.com/EnzoHsieh-Android/Lumos/commit/a2c104616cf497ed6ccbb9e4e3f1eef6bcef63c0) | docs | docs: 超長行那篇問題筆記的留痕殘行改寫成重現指令,不再留測試待補的佔位字 |
| 10/09 21:50 | [d78e15eb](https://github.com/EnzoHsieh-Android/Lumos/commit/d78e15ebcf6f5a670bc91f22c177c3182ec394a8) | docs | docs: 回頭重讀六篇守檔筆記,改掉被這次改動弄得不成立的舊句 |
| 10/09 21:50 | [22a92c2f](https://github.com/EnzoHsieh-Android/Lumos/commit/22a92c2fec2190279343788f332378573a55ff00) | chore | chore(lumos): 記錄代碼審通過 |
| 10/09 21:56 | [32875a62](https://github.com/EnzoHsieh-Android/Lumos/commit/32875a6244d5600f71a736bea9f8fb1f3411dd90) | merge | Merge pull request #50 from EnzoHsieh-Android/target-arch-lens |
| 10/09 23:27 | [225d1db8](https://github.com/EnzoHsieh-Android/Lumos/commit/225d1db8a63b88fed9466344ce810bd7cb250d1f) | chore | chore(lumos): 記錄代碼審通過 |
| 10/10 00:11 | [a779752a](https://github.com/EnzoHsieh-Android/Lumos/commit/a779752a7e51ebe0426b7512b00fbb7c659e7a88) | chore | chore(lumos): 記錄代碼審通過 |
| 10/10 00:31 | [9850df1c](https://github.com/EnzoHsieh-Android/Lumos/commit/9850df1cfaa973a53118057f5b89ca0beebddf3f) | merge | Merge remote-tracking branch 'Lumos/main' into EnzoHsieh-Android/reread-block |
| 10/10 00:33 | [2396619f](https://github.com/EnzoHsieh-Android/Lumos/commit/2396619f0d584403f68e84e4bc4464ded30d32d0) | chore | chore: 合併主線後回頭重讀五篇守檔筆記,判定都沒有要改的句子 |
| 10/10 00:33 | [41c7c1ae](https://github.com/EnzoHsieh-Android/Lumos/commit/41c7c1ae982596347efd37540eb95076f15f6f13) | chore | chore(lumos): 記錄代碼審通過 |
| 10/10 01:33 | [8e648f3d](https://github.com/EnzoHsieh-Android/Lumos/commit/8e648f3d536220bf7e0ea3c8cd52deed75816595) | merge | Merge pull request #51 from EnzoHsieh-Android/EnzoHsieh-Android/reread-block |
