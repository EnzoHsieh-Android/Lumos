---
type: project
status: doing
created: 2026-10-23
updated: 2026-10-23
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/macrobenchmark-adapter
related:
  - "[[Projects/Android逐層診斷_計劃]]"
  - "[[Projects/Macrobenchmark退步提醒_計劃]]"
  - "[[Projects/併發與效能表態要合約背書_計劃]]"
---
# Macrobenchmark驗收門檻_計劃

白話:Android 的驗收通常是「一整段流程走得通」,Enzo 2026-10-23 要在這段流程上再加效能數字當驗收標準。流程本身照既有做法寫成功能節點的 `★INVARIANT★` 合約行、綁一支跑完整段流程的測試;效能門檻由人裁定(哪台裝置、哪個情境、哪個指標、上限多少),寫進專案的 `.lumos/macrobench-thresholds.json`,每條門檻記它屬於哪條合約。`lumos macrobench` 讀這份檔,在「跟基準比有沒有變慢」之外另報「沒達驗收門檻」,同樣只提醒不擋推送(Enzo 同日裁)。逐層診斷的 L0 拿它當往下查的條件,收據記回對應的合約。

WHY:門檻沒達只提醒、不擋推送 [出處:2026-10-23 Enzo 裁「只提醒、不擋」] [因:沿用 [[Projects/併發與效能表態要合約背書_計劃]] 2026-10-01 的裁定,毫秒隨裝置與溫度浮動,硬擋會隨機誤擋;要擋得先備齊固定裝置、固定資料、環境失敗判無法判定] [不選:人裁門檻沒達就擋推送(要翻 10-01 的決定);只在節點寫一行規則靠人對照(沒有機械檢查,逐層診斷的 L0 觸發條件做不出來)]
WHY:門檻放在專案的設定檔,節點不加新寫法 [出處:2026-10-23 對話,查詢代理逐項核對既有機制] [因:流程驗收已有 `★INVARIANT★`+`[test:]`;效能數字要機器讀,放進節點摘要行得另寫解析器、還會跟合約行的獨立審計混在一起;設定檔裡每條記 `contract` 指回合約,兩邊連得起來] [不選:新增摘要行前綴(要改 lint 與筆記形狀檢查);把門檻寫進 Macrobenchmark 測試裡自己斷言(Macrobenchmark 不提供讀數字的斷言,而且綠燈只代表測試跑完)]
WHY:門檻檢查跟基準比對分開,沒有基準也照判 [出處:2026-10-23 設計] [因:門檻是絕對值,不需要前一次的結果;第一次接上的專案就要能判驗收] [代價:同一個指標可能同時出現在「變慢」與「沒達門檻」兩欄]
PRIOR-ART: 結構仿 `lumos macrobench` 既有的設定檔與比對(見 [[Systems/macrobenchmark-adapter]]);「指標 比較 數字」的門檻判定在 Lumos 已有先例(資安證據閘的 k6 門檻,`_secev_k6_thresholds`);Macrobenchmark 官方文件沒有內建門檻斷言,CI 頁建議用基準追趨勢、門檻由團隊自訂。裁定:自建一個小欄位,不加依賴。
RETIRE-IF: 接上的消費專案連續 8 週沒有任何一條門檻被判「沒達」也沒人改過門檻,或團隊改用雲端測試服務內建的門檻告警,就撤掉門檻檔支援。
REVISIT:2026-12-21 有沒有真實消費專案寫了門檻檔;沒有就判撤案或延後

## 門檻檔格式

```json
{
  "version": 1,
  "thresholds": [
    {"scenario": "com.example.bench.CheckoutBenchmark#checkoutFlow",
     "metric": "frameOverrunMs", "stat": "P90", "max": 0,
     "device_model": "SM-X710",
     "contract": "Systems/結帳流程 ★INVARIANT★ 從主頁進結帳、送單、看到成功畫面",
     "decided_by": "Enzo", "decided_at": "2026-10-23"}
  ]
}
```

- `scenario`:結果檔的情境鍵(`類別#方法`,有參數時跟 `lumos macrobench` 一樣接參數),必填。
- `metric`、`stat`:啟動類用 `median`/`minimum`/`maximum`,滑動類用 `P50`/`P90`/`P95`/`P99`,必填。
- `max` 或 `min`:恰好一個,數字;越小越好的指標寫 `max`。
- `device_model`:選填;寫了就只在這台型號上判,別台列成「換了裝置,沒判」。毫秒只在指定裝置上有意義,建議都寫。
- `contract`:必填,這條門檻屬於哪條合約(節點路徑加合約行片段);印結果時一起印。
- `decided_by`、`decided_at`(`YYYY-MM-DD`):必填,證明是人裁的門檻,不是從某次量測反推的。

## 節點怎麼寫

功能節點(消費專案的圖譜):

```
KEY:★INVARIANT★ 從主頁進結帳、送單、看到成功畫面 [test:bench:checkoutFlow]
SEE:效能驗收門檻在 .lumos/macrobench-thresholds.json,contract 欄指回這一行
```

- 流程走不通 → 綁的測試紅(綁定測試閘照既有規則處理)。
- 流程走得通但數字沒達門檻 → `lumos macrobench` 報「沒達驗收門檻」並印出 `contract`;逐層診斷從 L1 往下查,收據的 `contract_refs` 記這條合約。

## 條款

- [S1] 當門檻檔有一條門檻、這次結果的同情境同指標超過 `max`(或低於 `min`)時,指令應列為沒達驗收門檻,並附現值、門檻值與 `contract` [test:t_macrobench_threshold_fail]
- [S2] 當現值剛好等於門檻或在門檻內時,指令應列為達標,不得列為沒達 [test:t_macrobench_threshold_pass_edge]
- [S3] 當門檻寫了 `device_model` 而這次結果的裝置型號不同時,指令應列為換了裝置沒判,不得判達標或沒達 [test:t_macrobench_threshold_device]
- [S4] 當還沒有基準檔、或基準檔讀不了時,指令仍應照門檻檔判;門檻判定不受基準影響 [test:t_macrobench_threshold_without_baseline]
- [S5] 當門檻檔 JSON 壞掉、或任一條缺必填欄位、`max`/`min` 不是恰好一個有限的數字、`decided_at` 不是真的日期(例如 2026-13-45)、`stat` 不是該類指標會有的統計值時,指令應回 2 並印出第幾條哪裡壞;沒有門檻檔時照舊、不報錯 [test:t_macrobench_threshold_bad_file]
  - 2026-10-24 補充(不改本條的驗收範圍):寫了 `check` 的條目不驗 `max`/`min`,改驗那種檢查自己的欄位;舊寫法條目的 decided_by 寫成 <裁定的人> 這種佔位也回 2(跟 check 條目共用一支署名檢查)。這兩件由 [[Projects/Android記憶體與穩定性驗收_計劃]] 的 S13、S25 驗,綁 t_android_memstab_check_fields_strict
- [S6] 當門檻指的情境或指標這次沒跑到時,指令應列為沒判(並說是哪個缺),不得當成達標 [test:t_macrobench_threshold_missing_scenario]
- [S7] 沒達門檻時指令仍應回 0(只提醒,不擋推送),`--json` 輸出應有 `threshold_failures`、`threshold_passed`、`threshold_skipped` 三欄 [test:t_macrobench_threshold_rc_and_fields]
- [S9] 當帶 `--update-baseline` 時,基準檔的每個情境應記下它來自哪個結果檔(相對 repo 的路徑與 sha256);這次讀不了而沿用的舊項目保留原本的來源;沒有來源欄的舊基準照樣能比 [test:t_macrobench_baseline_records_source]
- [S10] 當門檻、設定檔容差、基準檔或結果檔的數字是 NaN 或 ±Infinity 時,指令應當成格式不對:門檻與設定回 2、基準整份當讀不了、結果檔記成讀不了,不得拿它判達標或不算退步 [test:t_macrobench_rejects_nonfinite]
- [S11] 當收據的 queries.sql 有標頭沒被解析到(漏分號、標頭寫歪)、一條 expect 都沒有、或 manifest 列的查詢不在檔裡時,收據範本的 rerun.sh 應回非 0 並說原因,不得空轉回 0 [test:t_android_evidence_rerun_refuses_empty]
- [S8] 逐層診斷 skill 的 L0 應把「沒達驗收門檻」當往下查的條件,收據 manifest 應有 `contract_refs` 記門檻對應的合約 [manual:讀 skill 與 reference.md 的 L0 與 manifest 段]

## 接線檢查順手修(2026-10-23)

- skill 與逐層診斷計劃原本寫「人裁的門檻檔」,但沒有格式也沒有程式讀;本計劃補上。
- 收據原本沒有欄位指回合約;加 `contract_refs`。
- [[Projects/Android側UI測試綁圖譜工作流_計劃]] 決策 d3 說推送前只擋留痕、不真跑,已過期(綁定測試閘 2026-08-22 起真跑),在那篇加訂正行。
REVISIT:2027-01-31 綁定測試閘還跑不動 Macrobenchmark(只代換方法名不帶類別、單支 180 秒逾時、沒接裝置判紅),要讓流程測試被閘真跑時另開計劃;這次不動

## 不做

- 不擋推送,不接進推送前檢查或 CI 閘。
- 不從任何一次量測自動產生門檻。
- 不驗 `contract` 指的節點是否真的存在(消費專案的圖譜不一定在同一個 repo);只原樣印出。

## 實務隱患

已排除:金流:只讀本機結果檔與設定檔
已排除:對外送出:不發網路請求
已排除:不可逆:只讀不寫,門檻檔由人手寫進版控
已排除:守衛面:只提醒,不改任何閘的判定

## 回退

拿掉門檻檔的讀取與判定函式;消費專案留著的門檻檔會被忽略,其他行為不變。
