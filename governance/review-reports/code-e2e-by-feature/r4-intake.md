# code-e2e-by-feature r4 收貨紀錄

第四輪是使用者裁「加開一輪」後的那一輪。七席全交回(2026-10-26),git reflog 核過席位沒動 repo(HEAD 仍在 7988107c)。正確性、邊界、合約三席原派 sonnet,因 Sonnet 每週額度用完中途停止、沒有交報告,改派 opus 全新代理(r4-dispatch.json 的 note 有記)。引句七席對各自審材與完整快照全數錨定。架構對齊席自述清理自己臨時目錄時用了萬用字元刪檔(違反派工詞),目錄在它的 /tmp/lumos-seat-work 底下、已不存在。

編號:正確性 C1–C5、資源 R1、邊界 B1–B4、合約 K1–K6、通才 G1–G2、資安 S1–S2、架構 A1–A4,共 24 條,blocking 4 條(C1、B1、G1、A1)。

## 修補因果(regression)

上一輪修補造成、有兩版證據的:G1、B2(功能 paths 寫 ./. 修前擋、修後放行)、A1(捷徑檢查在原地另寫一套,沒用共用守衛;行為正確、做法不一致)。
原有漏查:C1 B1 B3 S1 S2 G2 R1 C4 K1 K2 K3 K4 A2 A3;未判定:C2 C3 C5 B4 K5 K6 A4。

## 根因分組與去向

| 組 | 編號 | 重現 | 去向 |
|---|---|---|---|
| 記憶體設定不在指紋裡 | C1 | HIT:席位兩版同一指紋;新測試在修後拿掉那段就紅 | 折:e2e 段開了記憶體時,stability 段與 stability_scenarios 接進指紋;改 S2 條文、記決策 d1 |
| 主線上開發 --changed 漏挑 | B1 | HIT:新測試在拿掉 fallback 後紅 | 折:分岔點等於 HEAD 且在 main/master 上時改拿 upstream(沒設就 origin/<分支>) |
| ./. 漏過根本身檢查 | G1 B2 | HIT:新測試在拿掉 _e2e_norm 判斷後紅 | 折:_e2e_relpath_err 根本身也看 _e2e_norm 之後的值 |
| 捷徑檢查另寫一套、總表沒擋中間層捷徑 | A1 A2 S1 | HIT:新測試在拿掉總表守衛後紅 | 折:紀錄與總表寫入都走 _repo_path_unsafe 與 _repo_path_unsafe_why |
| run-id 大小寫、跟情境目錄撞名、多出來的參數 | B3 S2 G2 R1 C5 B4 | HIT:新測試各自在拿掉對應檢查後紅 | 折:不分大小寫擋 history.jsonl;run 目錄或「run-id.情境」目錄已存在就擋;多出來的位置參數擋 |
| 記憶體逾時後效能還等一輪 | C4 | HIT:新測試在拿掉 device_stuck 後紅 | 折:記憶體那段逾時就連效能也不跑 |
| 工作目錄設定跟提交不同沒有測試 | C3 | HIT:讀碼 | 折:t_android_e2e_r4_edges 用 assume-unchanged 造出這種狀態 |
| 整套跑沒過、feature_runs 還留著較早的通過 | C2 | HIT:讀碼 | 折:計劃〈查證紀錄長怎樣〉寫明推送前檢查要比兩邊結束時間取較新的 |
| stability_scenarios 併入做法不同 | A4 | HIT:讀碼 | 折:跟 stability、e2e 一樣在 _macrobench_config 直接放進 cfg |
| 分派函式的理由 | A3 | HIT:讀碼 | 折:guard 分派說明裡改寫成實際的理由 |
| 文件 | K1 K2 K3 K4 K5 K6 | HIT:讀文件對照程式 | 折:README 與 skill 的覆蓋規則、計劃 runs/history/feature_runs 欄、回傳碼補齊、S26 條文、stability_scenarios 位置、終端最後一行 |

重現方式:對修後版本逐條拿掉這輪加的七道檢查,t_android_e2e_r4_edges 各自翻紅(./.、主線 fallback、總表守衛、run-id 大小寫、情境目錄撞名、多出來的參數、記憶體逾時);拿掉指紋的記憶體設定也翻紅。修補前版本跑新測試時一開頭就因指紋函式少一個參數丟例外,後面的斷言沒跑到,所以修補前對照不算數,以逐條改壞為準。另在實驗室實機跑六種分塊組合,全部照預期。

沒有機械重現不到的條目(refuted 為 none)。同輪有 major,minor 全折、沒有放行。使用者裁「修完就推」,不再開第五輪。
