# r1 收貨與去向(2026-10-27)

材料:r1-snapshot.patch(0701350..0aecbf90,扣掉 governance/ 與帳本,2968 行;七席都拿整份,派工各給重點範圍)。7 席:正確性(C)、邊界(B)、資源(P)、合約與文件(K)、通才(G)、架構對齊(A)、資安(S)。三席(C、P、K)總結句含等級字樣被當成宣告,退回只改那幾句,內容不變。

這輪有 major,照代碼審規則 accepted 必須為空:35 條全折(修正前 0aecbf90 → 修正後 a1ba52bf)。

## 重現(觀察與判準分開驗)

| id | 重現 | 結果 |
|---|---|---|
| C1、S1 | 只改設定(拿掉 flow、整段刪 e2e、調小記憶體輪數)、App 沒動 → 原版 check 回 not-required;補成 t_android_e2e_gate_reads_mainline_config 四組 | HIT |
| C2、B1、K1、G1 | 提交壞掉的 macrobench.json,原版帶 LUMOS_SKIP_ANDROID_E2E=1 與 CI=true 照樣 blocked;補成 t_android_e2e_gate_unclear_blocks 三條 | HIT |
| C3、K3 | 按功能那條路把 >= 改成 >、涵蓋只留 flow,原版測試照綠;補同一秒、截圖、記憶體三條 | HIT |
| B2 | 捷徑指到 /dev/zero,掛鉤卡住(席位實測 5GB);補 t_android_e2e_ai_count_copies_agree 的捷徑案例 | HIT(讀碼對上 stat 跟著捷徑走) |
| B3、C4 | 只改只列效能的功能、沒紀錄 → 原版擋、情境清單空白;補 S31 一條 | HIT |
| A1 | _E2eRecordLock 靠鎖裡程序編號接手,_excl_lock_try 註解明文不這樣做 | HIT(讀碼) |
| S2 | waive --list 原樣印 who 與 note;補控制字元案例 | HIT |
| K2 | 拿掉畫面與記憶體 check 的改壞測試照綠;補兩條 | HIT |
| K4 | doctor --ci 沒驗回傳碼;補一條 | HIT |
| K5 | 佔位字「<為什麼放行,至少 10 個字>」去空白 14 字過得了;改成「<理由>」並補照抄過不了的測試 | HIT |
| K6 | main 上已提交沒推,不帶 --range-start 誤報;補 t_android_e2e_check_on_main | HIT |

## 去向(根因分組,一條規則補一組)

1. 出口排得太後面:C2、B1、K1、G1 → 折。判定結果是擋下時最後再看 CI 與 LUMOS_SKIP_ANDROID_E2E(_e2e_gate_escape)。
2. 只改設定就放行:C1、S1 → 折。指紋相同時另比分岔點與被推送提交自己的 e2e 段、記憶體設定;拿掉 e2e 段就擋。
3. 只列效能的功能:B3、C4 → 折。沒有要驗的情境就按功能放行、列出沒驗的,不要求紀錄。
4. 測試沒守住:C3、K2、K3、K4、K11 → 折。補同一秒、截圖與記憶體涵蓋、拿掉畫面與記憶體、doctor --ci、答 n、看過後推送行;K11 的句子一致由 t_prepush_cl_reason_* 兩支守,S12 條款保持現狀並在條款旁不另加測試(兩支守衛已綁在 bound-tests-gate)。
5. 讀紀錄檔:B2、B4、G2、C5、P2、P3、A3 → 折。_e2e_record_files:lstat 只讀一般檔、最新的 500 份、單份 2MB;掛鉤是同一組數字的複本、逐份容錯;補兩邊算出一樣的測試。
6. 外來文字進輸出:S2 → 折。--list 的 at、who、note 過 _esc_clean。
7. 鎖:A1 → 折。改回 _vault_write_lock,不自動接手;計劃 S34 改寫並記一行 WHY(推翻設計審 r3 的折法)。
8. 輸入防呆:B5、K5、K6 → 折。LUMOS_TTY_TIMEOUT 負數或 NaN 用預設;佔位字改短;main 上 check 自動用 upstream。
9. 效能:P1、P4、P5 → 折。歸屬先建索引、每 1000 支查截止時間;pathspec 不重複列素材目錄底下的 flow;讀檔前先問大小;治理帳事件過 _gate_event_fit;--case 建議最多 10 個。
10. 跟鄰居對齊:A2、A4 → 折。取不到要推的提交也交給判定(工作目錄有 e2e 段才擋);代碼改成 evaluation_timeout、evaluation_error。
11. 文件:K7、K8、K9、K10、S3 → 折。計劃接線說明、waivers 的 commit 欄、開場提示只在有圖譜的專案印;驗證紀錄補 REVISIT 重跑探針;S3(AI 放行與人放行效力相同)是計劃已裁的設計,計劃 WHY 已寫,這輪補 SKILL「放行前先跟使用者講」那句已在,折入=確認文件寫明。

refuted:none。
