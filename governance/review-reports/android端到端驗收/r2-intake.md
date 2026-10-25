# android端到端驗收 r2 收貨

## 六席收貨

- 六席都是沒參與過的新代理,鏡頭同 r1。報告從完整逐字稿存檔(完成通知會把角括號轉成跳脫字)。
- 守衛席引句沒包「」、通才席沒有引句行、整合席有一行列表項以「嚴重度」開頭被機器當成等級宣告:三席都退回自己重交,只改格式,內容與判定沒動;重交後六席都已正規化、引句全錨。
- 編號:c 正確性、g 守衛、e 邊界、i 整合、n 通才、a 架構對齊,後接各席報告裡的條號(a 席用它自己的 A 號)。
- 修補因果:r2 的發現裡,回退指錯檔(a5、e1、g6、c15、i1、n3)是 r1 把設定併進 macrobench.json 時沒改到回退節;指紋選檔設定(c1、g2、i3、n2、n7、e2)、照抄成「既有做法 fail-open」(i6)是 r1 補段時帶進的未查證宣稱;其餘是 r1 版本就有、r1 沒被點到的洞。

## 編排者重現表

| id | 宣稱 | 重現 | 結果 | 處置 |
|---|---|---|---|---|
| a5 / e1 / g6 / c15 / i1 / n3 | 回退指向不存在的 `.lumos/android-e2e.json`;刪段的提交會被這道自己擋 | grep 計劃全文:這個檔名只出現在回退節;設定節寫明不另開設定檔 | HIT | 折(回退改成環境變數關一次、主線刪段) |
| c1 / g2 / i3 / n2 / n7 / e2 | judge 與判定用哪份設定選檔沒定;「e2e 段本身」不是 ls-tree 的項目 | 讀〈查證紀錄〉指紋公式只有 ls-tree 三欄;讀 macrobench 設定讀取:整份一個檔 | HIT | 折(選檔用被推送提交自己的段;另接 e2e 段正規化雜湊一行;WHY 新增一條) |
| g3 | 同一提交關掉 stability 只跑 UI 也會 pass | 指紋只看檔,旗標改動不改檔案集合 | HIT | 折(判定核對紀錄跑過的塊涵蓋主線版要求的;S9) |
| g1 / c14 / i2 | 「既有推送範圍算法」有多套,增量推送起點是遠端舊頂端;CI 說法矛盾 | 讀 pre-push 的 `_brange` 註解與 `_push_range_start`;讀 ci.yml 傳 BEFORE..SHA;讀 `_secev_mainline_pushed`、`_secev_mainline_pick` | HIT | 折(分岔點=跟主線的 merge-base,主線照安全證據那套;在 CI 用 `_in_ci` 不跑;S8) |
| i6 / e3 / c13 | 安全證據閘判不清就擋,不是 fail-open;主線設定壞掉會靜默放行 | 讀 `Systems/安全證據閘` 那行「判不清就擋」;讀 `_secev_evaluate` 例外轉擋下 | HIT | 折(判不清一律擋,出口是 LUMOS_SKIP_ANDROID_E2E;WHY 新增、S17 新增;刪掉 fail-open 的 REVISIT) |
| e4 / c2 | 驗收中途提交會讓紀錄綁到沒驗過的程式 | 計劃原文只在開跑前檢查一次、judge 結束時算 HEAD | HIT | 折(steps.json 記開跑 HEAD,judge 比對不同就回 2;S7) |
| e5 / g4 | 髒樹檢查只看 app_dirs,建置吃整個工作目錄與沒追蹤的檔 | 讀 `_dirty_non_bookkeeping`:有 untracked 參數、扣簿記檔 | HIT | 折(開跑前與 judge 都用它、連沒追蹤的檔) |
| e6 / c8 / g5 | `.e2e-lock` 殘留沒清法;只鎖工作目錄不鎖裝置 | 讀 visual-check.sh:mkdir 鎖、只 trap EXIT;計劃原文鎖在專案目錄 | HIT | 折(鎖改放 `~/.cache/lumos/android-e2e-lock/<序號>`、寫程序編號、程序不在就接手;加 HUP) |
| a1 / e7 / c9 | 暫存檔放系統暫存目錄跟 `_write_lf` 不同,跨磁碟會失敗 | 讀 `_write_bytes_atomic`:暫存檔同目錄、帶 .tmp-wlf | HIT | 折(直接用 `_write_lf`;判定只讀 `<指紋>.json`,殘留暫存檔不影響) |
| a2 | 讀改寫沒鎖、沒有 --list、重複放行沒定 | 讀 lint-waive:讀改寫包鎖、有 --list | HIT | 折(包鎖、加 --list、重複放行多一筆) |
| c5 / i8 | `_confirm_tty` 答 n 的情況沒定;等 30 秒沒提 | 讀 `_confirm_tty` docstring:True/False/None、LUMOS_TTY_TIMEOUT 預設 30 | HIT | 折(答別的=不放行回 1;--ack 只有 y 才算;寫明等待) |
| c4 / i9 | 只有放行的紀錄沒有 result,跟「result 不認得就擋」衝突 | 計劃原文兩條規則對這種紀錄給相反答案 | HIT | 折(runs=null;判定先驗 schema 與指紋,有放行就過;S10) |
| n4 / i10 | 「主動通知」其實是被動;開場提示沒有承載列、doctor --ci 會不會紅沒寫 | 讀開場掛鉤:沒有知識目錄就不印、只印 enforcement 的列 | HIT | 折(每次推送那道都印一行待看;doctor 列成提醒不讓 --ci 紅;enforcement 多一列;WHY 改寫成「列出」並寫代價;S14) |
| n5 / e11 / c10 / i11 | RETIRE-IF 的 pass 沒有資料來源;failopen 拼錯 | 讀 `_gate_failopen` 記的是 fail-open;計劃原文 runs 每次覆蓋 | HIT | 折(紀錄加只增不刪的 history;RETIRE-IF 改成掃紀錄;fail-open 那條 REVISIT 刪掉) |
| n6 | 紀錄產生了沒提交,擋下訊息叫人重跑或放行 | 計劃原文沒分這兩種 | HIT | 折(工作目錄有這個指紋的紀錄時,訊息改成「提交這支紀錄」;judge 最後一行也印) |
| n1 / c12 / i4 | 只有 e2e 段的 macrobench.json 會被讀設定那支擋;--results-dir 在沒有 results_dirs 時不生效 | 讀 `_macrobench_config`:沒有 results_dirs 也沒有 stability 段就回錯誤;`_macrobench_mode` 沒有 results_dirs 就不收結果 | HIT | 折(改到的地方列這兩處;S1、S15) |
| a3 / i13 | check-config 另開一個入口;--env 要碰裝置跟「lumos 不碰裝置」衝突 | 讀 `lumos macrobench --check-config`、stability 段的檢查掛在同一支 | HIT | 折(格式檢查併進 macrobench --check-config;環境檢查搬到範本腳本 --preflight) |
| i5 | 擋下原因句子的正本在另一篇計劃,測試會逐字比 | 讀 `t_prepush_cl_reason_sentences_match_plan` 與那篇計劃〈做法〉5 | HIT | 折(改到的地方與第 4 步列出三處同步、要 Enzo 簽章) |
| a4 / i7 | WHY 說收集腳本不呼叫 lumos,不實 | 讀收集腳本 load_config:用 `../lumos` 跑 macrobench --check-config | HIT | 折(改寫代價;找 lumos 照收集腳本) |
| a6 | failopen 拼法跟既有 fail-open 不同 | 讀 `_gate_failopen` 傳 "fail-open" | HIT | 折(那條 REVISIT 已刪,本案不再用 fail-open) |
| c3 | 共用子 flow、toolkit 腳本不在指紋裡 | 讀 visual-check.sh 的門檻底線與跑 flow 那行 | HIT | 折(驗收素材改成整個 .maestro/ 目錄) |
| c6 | Macrobenchmark 的 Gradle 指令會裝上、移除 App | 我沒實跑 AGP 驗證(席位自己也標 ⚠);常見的 connected 測試任務會裝卸測試 App | HIT | 折(效能排最後、sha256 在它之前讀第二次;實驗室驗收會實際碰到) |
| c7 | 截圖腳本的輸出沒存,judge 讀不到相符率 | 讀 visual-check.sh:相符率只印在終端 | HIT | 折(每步的標準輸出與錯誤輸出存檔、路徑寫進 steps.json) |
| c11 | steps.json 沒版本欄;舊版 lumos 沒這道判定不會發現 | steps.json 那半:計劃原文沒有 schema | HIT | steps.json 那半折(加 schema、不認得回 2);舊版 lumos 那半放行(lumos 經符號連結更新,一台機器只有一份;寫進〈不做〉) |
| e8 | visual_threshold 沒上限、科學記號會被 toolkit 拒 | 讀 visual-check.sh 的數字格式檢查 | HIT | 折(99.5 到 100、寫成一般小數) |
| e9 | 重跑沒過會蓋掉先前的 pass | 計劃原文 runs 每次覆蓋 | HIT | 折(寫明最近一次才算數的理由;先前結果留在 history) |
| e10 | flow 的「名」沒定義,同名會互蓋 | 計劃原文只寫 `<名>` | HIT | 折(名=相對路徑去副檔名、`/` 換 `__`,同名回 2) |
| i12 | 門檻條目情境名不符會讓記憶體塊永遠沒判到 | 讀 `_macrobench_stab_skip_reason`:情境或型號不符就跳過 | HIT | 折(check-config 要求條目情境等於 stability 段的情境) |
| i14 | REVISIT 綁整份統計化計劃 done,不是第 1、3、4 條 | 讀那份計劃自己的 REVISIT 列的是條目 | HIT | 折(改成 2027-03-31 查那三條) |

修補對照:修改前的全文存在 scratchpad(未進卷證);修改後就是本次提交的計劃。
