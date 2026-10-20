# code-安全證據閘與資安格子 r1 收貨紀錄

preflight-4: ran

## 席位與報告
九席全收齊後一次存檔:正確性、邊界、資源、整合、通才、架構對齊(引句格式退回該席重交一次,內容未改)、資安、規格對照(opus)、外家finder(codex,截取最終報告段)。quote-check 九份全數錨定;refcheck 九份 missing/out_of_range 皆 0。
圖譜鏡頭:派工時固定席計算逾時、未附節點(多席回報),本輪圖譜一致性由整合席手動核對動到的節點補足。

## 編號
- 正確性:C1(major) C2 C3 C4
- 邊界:B1(major) B2(major) B3
- 資源:R1 R2 R3
- 整合:I1(major) I2 I3 I4 I5 I6 I7 I8
- 通才:G1(major) G2
- 架構對齊:A1(major) A2(major) A3(major) A4 A5 A6 A7
- 資安:S1(major) S2(major) S3 S4 S5 S6
- 規格對照:P1(major) P2(major) P3(major) P4–P22;多做 PX1–PX5
- 外家:X1(major) X2(major)

## 編排者機械重現(被審版本 b99f52c8,python3.14 -B 載入 scripts/lumos 單函式)
| id | 命令要點 | 結果 |
|---|---|---|
| X1 / I1 / S4 | `_secapr_verify(b"", <主線鏈只有一筆 approvers_init,到期 2026-01-31>, "p", 2026-02-01)`,驗章函式固定 True | HIT:2026-01-31 diverged True、2026-02-01 diverged False(整條換掉不擋) |
| B1 | `_secev_target_host("target=http://evil.com#@localhost")`、`("target=http://evil.com?x=@127.0.0.1/")` | HIT:回 localhost、127.0.0.1 |
| B2 | `_secapr_verify(<seq1 type=[] 無 keys 欄>, None, "p", 2026-01-02)` | HIT:TypeError unhashable list;同條帶 keys 欄時判 approval_fields_missing 不丟例外(席位形狀需無 keys 才走到) |
| X2 | 席位附的 `_secev_tool_freeze` 改名 k6→k6-new、min_requests 1000→1 | HIT(採席位實跑輸出,編排者未另跑) |
| S1 | 席位在臨時 clone 改 .lumos/config.json mainline 指向被推分支後 approvals verify rc=0 | 採信(席位附指令與輸出;程式 `_secev_mainline` 讀被推提交的設定,讀碼確認) |
| S2 | 席位以 AI 自產金鑰 payload→ssh-keygen sign→security-approval-add rc=0 | 採信(席位附輸出;程式無互動終端或人機區分,讀碼確認) |
其餘條目為讀碼可驗或文件類,處置時由作者寫先紅測試確認。

## 判讀
- 本輪有 major,依處置閘規則 accepted 必空,所有發現折入;refuted 無。
- 根因分組(派作者時照組寫先紅測試):
  1. 外來 JSON 型別未先驗就用(B2、C1、C3、B3 回傳原因、A4 讀帳)——統一在讀進來的那一層做型別閘,單項壞只讓那一項 invalid,不讓整道 evaluation_error。
  2. 信任基準取自被審的一方或判準過寬(S1、X1/I1/S4、S3、S5、P3)——主線設定只讀主線 tip;到期≠從未有效;approved_on 單調;主線候選全部參與。
  3. 人機區分(S2)——核可寫入要互動終端與使用者手打確認碼;刻意偽造 pty 列工具天花板。
  4. 變弱比對漏洞(X2、P2、P1、PX5)——改名=刪舊加新;清單讀不出不替代;人審綁定涵蓋家節點程式檔;例外缺欄只讓例外不算數。
  5. 解析外部字串(B1)——改用標準 URL 解析。
  6. 第二種做法(A1、A2、A3、A6、A7)——改用既有 helper,git 與 ssh-keygen 逾時跟 deadline 走。
  7. 資源(R1、R2、R3)——迴圈內 tick、鏈長上限對齊預算、便宜預檢先做。
  8. 測試基準(G1、G2)與條款測試缺情境(P13–P22)。
  9. 文件與計劃對不上(I2–I8、P4–P12、PX1–PX4、A5、S6、C2、C4)。
