preflight-4: ran

# r1 前掃與處置

審材：`r1-snapshot.md`，100 行，SHA-256 `4f968e49d3d009b04e8644d2d31244fc2ca38da9c12b821a6ac41a836ac40fd2`。`lumos refcheck --json` 驗 2 條引用，missing=0、out_of_range=0；`prose-lint` 無命中；`pitfalls --check` 有實務隱患節。唯讀前掃檢未定義詞、壞引用、範圍矛盾與程式語意，未找到語意錯誤。

前掃提出兩處精度修正，派席前已改真計劃並重凍：

1. 原：「先確保事故後沒有第二個模型在途」→ 新：「先確保同一消融批次內事故後沒有第二個由本批次啟動的模型在途」，避免把保證擴張到其他程序。
2. 原：「當首個工作報事故」→ 新：「當任一工作將批次停止旗標設為 true（探針異常退出、失效或結果不可判）」，讓 S9 的觸發條件可驗。

這兩項是前掃的措辭精度，不是正式 finding；席位仍須獨立檢查設計的行為與邊界。

六席收齊後才改計劃與測試；正確性、架構對齊 clean，其餘四席共九條原 finding，逐字報告保存在同目錄。外家否決席未取得，只以同門視角判讀，不把缺席冒稱外家背書。`quote-check` 全席引句錨定，`refcheck` 所有檔案存在；`seat-check` 對報告沒有逐字提及每份材料的提醒屬觀測。

| ID | 原席與重現 | 處置 |
|---|---|---|
| B1 | 邊界 F1，HIT：舊 parser 讓 workers 0／負值過關才在 executor 崩。 | FOLD：S9 live 僅允許 1；紅測試覆蓋 0／-1。 |
| B2 | 邊界 F2，HIT：舊 merge-only 完全不派模型，不能被 live 限制誤擋。 | FOLD：S9 明定 merge-only 相容；紅綠測試保留 workers 2。 |
| C1 | 併發 F1，HIT：兩進程同 out-dir 的 stop 互不相通，原席以 barrier stub 量到峰值 2。 | FOLD：S10 同目錄本機獨占鎖；雙進程持鎖反例先紅。 |
| C2 | 併發 F2，HIT：舊預設 workers 2，現測試只明寫 1／2。 | FOLD：S9 預設 1；省略參數測試先紅。 |
| D1 | 資料 F1，HIT：缺輸出時只有 summary 記事故，重跑／merge-only 可覆蓋；定向反例先紅。 | FOLD：S8 每次失敗留下逐題 fatal 紀錄，預掃可辨認。 |
| D2 | 資料 F2，HIT：舊 workers 0 在 meta 寫出後才崩，舊 summary 可殘留。 | FOLD：S9 在 out-dir 改寫前驗值；紅測試要求目錄不被建立。 |
| O1 | 運維 F1，HIT：TimeoutExpired stub 先寫出有效結果再丟例外，舊 loader 仍採信。 | FOLD：S8 隔離原結果、用 fatal 紀錄取代；下次純合併仍拒收，反例先紅。 |
| O2 | 運維 F2，HIT：舊例外不留診斷欄，summary 僅泛稱失效。 | FOLD：S8 留例外類型、arm、qid、log 路徑，不抄完整命令／秘密。 |
| O3 | 運維 F3，HIT：舊 usage/default workers 2，merge-only 可帶 workers 2。 | FOLD：S9 改預設與文案、保持 merge-only 相容，回退節明禁恢復預設2。 |

四組去重處置：CLI 邊界 B1/B2/C2/D2/O3、跨進程 C1、持久失敗紀錄 D1/O1、診斷 O2。全部折入 S8–S10，未接受或駁回。`fold-check` 的 reverse-omission 列了舊計劃 body 中多個 CLI 詞而 frontmatter 原本無 summary 欄，逐項核對不是新補丁鏡像矛盾；`spec-gate --no-run` 十條全綁測試。
