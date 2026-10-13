# r1 收貨紀錄(高風險:5 席+架構對齊+資安+規格符合,同門 sonnet;外家未派)

席位與編號:資源 G1–G3、邊界 B1–B2、規格符合 P1–P6、正確性 C1–C2、合約 K1–K2、資安 S1–S4、回滾 R1–R2;架構對齊 clean(0 條)。共 21 條。資安席報 major,依代碼審規則本輪全部折入、不放行。

## 引句錨定狀況

資源、合約、回滾、架構對齊、資安、規格符合六席全數錨定(載體選資安);正確性 4 句、邊界 1 句錨不到——抄的是 patch 裡帶前導空白與大量「」的程式行,內容逐條在下表重現。

## 機械重現表

| 群 | 涵蓋 finding | 重現命令/查證 | 結果 |
|---|---|---|---|
| 比較模式壞路徑與穿越 | S1 G1 B1 | 帳列 `report_path` 填含 NUL、repo 外絕對路徑、不存在檔、非 UTF-8 檔;改後 `t_quote_full_span_compare_and_event` 釘「讀不到 3 組、非 UTF-8 1 組」且無 traceback;scratchpad 變異拿掉「限 repo 內」該條翻紅 | HIT(三席獨立) |
| 事件片段控制字元與欄位偽造 | S2 | 報告引句含 `\x1b[2J\x07report-not-normalized report=/etc/x`;改後 note 無控制字元、`quote=` 排最後、第一個 `report=` 是真路徑;變異拿掉過濾翻紅 | HIT |
| 統計先判開頭順序沒測試守 | K2 | 合約席把 `_rn` 改回 `_rej` 測試全綠;改後同一筆事件只算進引句判準,同一變異翻紅 | HIT |
| 處置閘診斷與資源 | P3 R1 G3 | 讀處置閘新分支:零引句、讀檔失敗不印診斷;路徑未加引號;`except Exception` 接住 MemoryError | HIT |
| 比較模式正規化 2N 次 | G2 | 實跑 `quote-check --compare-rules --repo .`:23.5 秒、尖峰 1.38 GB | HIT(折入:計劃寫明成本,唯讀指令不另做快取) |
| 尾段掃到報告結尾、說明文字打出引號字元 | B2 C2 | 實跑比較模式:舊判過新判不過 21 組中 stray 9 組 | HIT(折入:第一條 REVISIT 另計這一類) |
| 未閉合被別處收尾引號補閉合記成 miss | C1 | 計劃抽取規則第 3 步明定此行為,`t_quote_full_span_v1_pinned` 已釘 | HIT(折入:計劃實務隱患寫明分類後果) |
| 第一階段改了文件 | P1 K1 | `git diff` 見 `skills/lumos-design-loop/SKILL.md`、`templates.md`、Systems 新節、兩篇 Issue | HIT(折入:計劃第一階段登記這三樣) |
| 舊判準說明第一行被動 | P2 | 程式比對改名前 `_quote_rows` 與 `_quote_rows_legacy`:改後說明與本體逐字相同(True) | HIT |
| 量測補行、回放偏離門檻 | P4 | 計劃〈量測〉補實測行;〈推送前驗證〉寫明主線既有漂移的判法 | HIT |
| 略過非零分支無測試 | P5 | 同第一列 | HIT |
| 程式多做規格沒寫的輸出 | P6 | 計劃補「(其中 N 條格式不合)」與 `--rule` 走 argparse choices | HIT |
| 大量短引句耗時 | S3 | 資安席實測 5 萬條引句約 55 秒;舊判準同 | HIT(折入:計劃實務隱患) |
| 第二階段刪章降級 | S4 | 讀 `_quote_rule_of`:缺鍵即 legacy | HIT(折入:第二階段清單加評估項) |
| 還原後舊版統計分錯格 | R2 | 回滾席在改前與改後 clone 各注入兩筆事件實跑 | HIT(折入:計劃實務隱患) |

## 處置

- 折入 21 條(全部)。放行:無。refuted:無。
