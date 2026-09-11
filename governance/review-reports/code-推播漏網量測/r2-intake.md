# r2 收貨紀錄(code-推播漏網量測)

- 為什麼有這輪:r1 17 條全折後,修正本身(recount.py 四百多行)沒有席位看過(code-loop 手冊步驟 5:收斂前派全新席掃修正差異);推送時 pre-push 以遠端最新版為起點算出 tier high(觸發點是修正加的懶載入全域快取),本輪照 high 編制加派資安席。
- 派四席:單reviewer-sonnet、架構對齊-sonnet、資安-sonnet、外家否決-codex。材料:r2-delta.patch(修正差異,主材料)、r2-snapshot.patch(整個功能的完整 diff)、r1-intake.md(背景)。
- ★外家否決席缺席★:Codex 開跑 4 秒撞到帳號額度上限(「try again at 10:28 PM」),沒有交出報告;原文存 r2-外家否決-codex-缺席紀錄.txt。standard 分級的外家否決是「缺席要註明」(note-if-absent),Enzo 當場裁「跳過外家」;本輪結論只能說「同一家模型的三席看過」。
- 三份報告都已是正規化格式;quote-check 三份全數錨定 r2-snapshot.patch;refcheck 三份 missing 0 / out_of_range 0。資安席六類逐類看過,判 clean。

## 機械重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| D1 | 載入修後 recount.py,`_search_segments('lumos search \\\n  "作廢 收回"')` 並接零命中輸出 | HIT(段 [['\\']]、查詢字串 '\\'、verdict zero) |
| E1 | 讀 recount.py:同檔借模組的既有函式叫 _load_hook_helpers,新函式叫 _lumos_mod | HIT(命名不一致) |
| E2 | 讀 autonomous-loop.sh 的 run_replay 與 run_lens_weekly | HIT(run_replay 先 LOG: 迴圈後原始 JSON,新函式相反) |

## 修法(先紅後綠)

- D1:切段前先把「反斜線接換行(接著的空白)」接回成一個空白,再逐行、再切段。新測試 t_lens_recount_code_review_r2 ① 修前紅(段 [['\\']]、兩個 search 夾續行時 [['a', '\\'], ['b']]),修後綠。
- E1:_lumos_mod 改名 _load_lumos_main,跟同檔 _load_hook_helpers 同一種命名。行為不變,既有測試守。
- E2:run_lens_weekly 改成先逐行記 LOG:、再記原始 JSON。新測試 ② 修前紅、修後綠。
- 修後 -k lens 173 項、-k codex_s3 19 項、-k recount 80 項全綠。

## 處置

- 本輪有 major(D1),依 d2 同輪不得放行:3 條(D1、E1、E2)全折。重現不到 0。
