# code-安全證據閘與資安格子 r2 收貨紀錄

preflight-4: ran

## 席位與報告
八席全收齊後一次從逐字稿存檔:正確性、資源、邊界、架構對齊、整合、通才、資安(涵蓋 r2-snapshot.patch 全量與 r2-repair-lumos.patch)、規格對照(opus)。外家未派(預設不派)。report-normalize 八份皆已正規化;quote-check 對 r2-snapshot.patch 八份全數錨定。
各席材料依 r2-dispatch.json 拆包,資安席例外(須涵蓋最後一版完整快照)。架構對齊席報告末行重複一次 severity 宣告,機器數 3、實際 finding 2。

## 編號
- 正確性:K1(payload 遇壞 covers_kinds 崩潰) K2(主線 tip 設定讀失敗靜默當沒設)
- 邊界:E1(確認碼提示指令未加引號) E2(vulndb 時間極端 OverflowError 整道 evaluation_error)
- 資源:Q1(major,快照中符號連結逐一 git ls-tree 不看截止時間)
- 架構對齊:H1(治理帳路徑字面值) H2(共用寫入改文字模式與 docstring 不符)
- 整合:N1(計劃核可鏈上限仍寫 10000) N2(四道/五道沒改完) N3(payload 旗標文件只寫一半) N4(S50、S55 條款沒跟上) N5(Verification 數字是修補前)
- 通才:T1(major,S13 入口 open 格數與全庫相同分不開) T2(major,人機區分只留 stdin 檢查照綠) T3(_sg_pty_run 不守 timeout) T4(主線候選前置斷言太鬆) T5(fixture 重複與慢測試) T6(golden 重產程式無人守、README 不符、無退場條件)
- 資安:V1(major,直接寫核可檔繞過確認碼;主線無鏈時 AI 自釘金鑰) V2(major,gate_detail 原樣印出可注入) V3(核可與背書寫入跟著捷徑走) V4(主線解析失敗時預檢 no_registration 蓋掉 mainline_unknown)
- 規格對照:Y1(major,S9 校準輸出檔綁定無測試守) Y2(讀證據兜底收太寬,程式內部錯誤變單項 report_malformed) Y3(同 T2:and/or 分不出) Y4(S52 但書測試驗不到) Y5(S55 條款與〈三〉不一致) Y6(〈五〉回退節仍寫 iterparse)

## 編排者機械重現與核對(被審版本 7655a12d)
| id | 命令要點 | 結果 |
|---|---|---|
| V1 | 席位在臨時 repo 直接寫入自產金鑰簽的 approvers_init 後 security approvals verify | 採信(席位附指令與輸出 1 ok approvers_init;程式 _secapr_verify 不知寫入途徑,讀碼確認) |
| V2 | `git show 7655a12d:scripts/lumos` 第 63133 行 print gate_detail 未經 _secinv_show | HIT(讀碼確認;席位附 repr 輸出含原始換行與 ESC) |
| Q1 | 席位 fast-import 3000 個符號連結 .md,_secinv_snapshot_tree 給 60 秒截止 | 採信(席位附兩版耗時 80.45s / 76.69s) |
| Y1 | 席位刪掉 calibration_path 加入綁定的兩行後 -k t_secev_s09 | 採信(席位附 12 passed) |
| T1 | 席位拿掉入口過濾後 -k secq_r1_s13 | 採信(席位附 2 passed 與 DBG13 18 18) |
| T2 / Y3 | 席位把 stdin 與 stdout 都要是終端改成只看 stdin(或改 or)後 -k secev_r1_approval_add | 採信(兩席各自實跑皆 4 passed) |
| K1 | r2-repair-lumos.patch 第 92–94 行拿掉登記時 covers_kinds 型別檢查;payload 路徑未補 | HIT(讀修補差異確認) |
| Y2 | r2-repair-lumos.patch 第 1592 行兜底接 KeyError/IndexError/ValueError 等 | HIT(讀修補差異確認) |
| H2 | r2-repair-lumos.patch 第 2491、2559 行原 "ab",共用函式第 2624 行文字模式 | HIT(讀修補差異確認) |

## 修補因果(regression-set)
有證據屬上一輪修補造成:K1(拿掉登記型別檢查)、Y2(新加的兜底)、H2(抽共用函式)、N1(降上限未同步計劃)、N4 與 Y5(改寫〈三〉與 d17 未同步條款)。
有證據屬原有漏查:E2、Q1、V2、V3、Y1、Y6、H1、N2。
未判定(本輪新加的測試或機制,無修前版可比):K2、E1、T1–T6、V1(確認碼是新機制;直接寫檔繞過在修前同樣成立)、V4、Y3、Y4、N3、N5。

## 判讀
- 本輪有 major,依處置閘規則 accepted 必空,所有發現折入;refuted 無。
- V1 涉及使用者裁量(人機區分的根本限制),折入方式另請使用者裁。

refcheck:資安席 missing 3 條、資源席 missing 1 條都是席位自建的重現臨時路徑(docs/a-knowledge/x.md 等),不是審材引用。
