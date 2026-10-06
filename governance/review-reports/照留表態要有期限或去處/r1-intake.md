preflight-4: ran

# 照留表態要有期限或去處 r1 前掃

前掃一席(sonnet)照固定清單:①未定義的詞 無 ②壞引用 無 ③範圍自相矛盾 1 條 ④機械宣稱驗語意 3 條。都不動「核心裁定」(Enzo 兩題裁定照舊),直接修真檔。

| 類 | 修改前 | 修改後 |
|---|---|---|
| ③ | 舊表態以 11-06 為期限;另寫「寫下時就已成立」的發現只認綁去處的照留——兩句對 rtb 那批舊表態打架(上線即失效) | 舊表態 11-06 前全部有效,含寫下時就已成立的;加 S3 後半句 |
| ④ doctor | 「推送檢查、drift scan、doctor 共用同一支」 | doctor 只數回頭條件條數、不評估不扣表態(`_drift_doctor_lines` 只餵 c1–c6),改寫成推送檢查與 drift scan 共用 |
| ④ 收尾集合 | 綁的那篇狀態在 `_DRIFT_SETTLED` 才算收尾 | `_DRIFT_SETTLED` 不含驗證紀錄的 pass/abandoned、Systems 的 rejected/deferred,沒狀態欄也算開著;改成只認 Issue(open/doing)與計劃(todo/doing),加 S6 |
| ④ 讀檔 | where=None 也用 `_drift_cat` | `_drift_cat` 只吃提交編號、要帶 timeout;None 改讀工作目錄檔 |
| 小 | 沒提 argparse 與 `_drift_ack_args_err`;「--keep 不經過這裡」 | 補 argparse 與參數檢查;--keep 改成「經過但 kind 固定 c2」 |


六席收齊才判讀。三道:引句除邊界席 #4(「綁的那篇還開著」不足 10 字)外全錨;refcheck 無缺檔或越界;報告已正規化。邊界席 F4 由編排者讀碼重現(`cmd_drift_ack` 只 `env.find`,不檢查是不是同一篇):HIT。

| id | 一句 | 重現 | 去向 |
|---|---|---|---|
| c-F1 | scan 的 born 判不了時收緊失效 | HIT:`_drift_born_annotate` 有多種 unknown | 折:scan 不收緊,B2 只在推送 |
| c-F2 | 壞欄位崩潰、批次讀整批判死 | HIT | 折:`_drift_ack_live` 型別防護、改用圖譜物件 |
| c-F3 | 時區方向寫反 | HIT | 折:日期只在 scan,重寫隱患 |
| c-F4 | 固定句仍教裸照留 | HIT:`_drift_fix_hint` probe/retire | 折:做法 8 |
| c-F5 | 舊版工具的裸照留享寬限 | HIT | 放行 |
| b-F1 | 讀不到一律判不在 | HIT | 折:圖譜物件 |
| b-F2 | 同鍵多筆語意未定義 | HIT | 折:任一筆活著就算 |
| b-F3 | 無欄位表態可在寬限內繞推送收緊 | HIT | 折:推送不認寬限 |
| b-F4 | 可綁自己那篇 | HIT:讀碼重現 | 折:擋 |
| b-F5 | 手改壞、成本 | HIT | 折 |
| b-F6 | 到期邊界未定 | HIT | 折:當天有效、ISO、不超過 30 天 |
| b-F7 | NFC/同名/改名 | HIT | 折:記 NFC 路徑、改名不追寫進隱患 |
| b-F8 | 驗收缺邊界 | HIT | 折:S2、S3、S7 |
| i-F1 | 第一次擋下沒有綁去處提示 | HIT | 折:改法提示直接寫 |
| i-F2 | 說明與 skill 沒列 | HIT:04-自檢與健康.md 第 13 行 | 折:做法 8 |
| i-F3 | 既有測試翻紅、日期注入 | HIT:兩支 scan 測試 | 折:scan 不收緊即不翻;today 參數 |
| i-F4 | 印出位置寫錯、與舊理由句衝突 | HIT:`_drift_scan_print` | 折:做法 5、7 |
| i-F5 | 批次失敗、逾時超預算 | HIT | 折:圖譜物件 |
| i-F6 | 晚升級專案沒有緩衝 | HIT | 放行 |
| i-F7 | old 為 None 整批誤標 | HIT | 折:born_now 與擋的條件一致,寫進天花板 4 |
| i-F8 | 時區方向 | HIT | 折 |
| r-F1 | 今天綠明天紅 | HIT | 折:推送不看日期,S7 |
| r-F2 | 寫死日期、日數錯 | HIT:10-06+30=11-05 | 折:改 11-05,REVISIT 撤 |
| r-F3 | 時區方向 | HIT | 折 |
| r-F4 | 退回是放寬 | HIT | 折:回退節 |
| r-F5 | 合併多筆 | HIT | 折:任一筆活著 |
| r-F6 | until 無上限 | HIT | 折:不超過表態日 30 天 |
| s-F1 | 另造 dead_ack | HIT | 折:沿用 prev_ack |
| s-F2 | 舊表態分支死碼 | HIT | 折:REVISIT 撤 |
| s-F3 | 不存 until | HIT | 放行 |
| s-F4 | RETIRE-IF 時間與量法 | HIT | 折 |
| s-F5 | scan 側 born 多餘 | HIT | 折 |
| s-F6 | 開著值手抄 | HIT | 折:由既有常數算 |
| a-F1 | 另造狀態集合 | HIT | 折 |
| a-F2 | 另一套讀狀態 | HIT | 折 |
| a-F3 | 命名與日期注入 | HIT | 折:`_DRIFT_EXPIRING_KINDS`、today 參數 |
