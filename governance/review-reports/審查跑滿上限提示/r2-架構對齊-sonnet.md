severity: minor

## F1 cap_report.advice 跟既有 out["advisory"] 同一份 JSON 家族裡近音,容易讀錯
severity: minor
blocking: 否
引句:「`advice`(提示代碼:`fix-gate`/`unknown`/`reshape`/`accept-with-reason`/`human-decides`)」
既有做法:`loop next` 的 emit() 在同一個輸出物件裡已經放了一個固定欄位 `out["advisory"]`(分級由編排者宣告後定死的說明字串),file: `scripts/lumos:10421`。這份計劃在 `--json` 底下新開 `cap_report.advice` 欄位(第四節)。兩個欄位雖然不是同一層級(一個在頂層、一個在 `cap_report` 巢狀物件裡),字面上「advisory」跟「advice」只差幾個字母,且兩者語意都是「工具給的建議/提示」,消費 `--json` 的人或之後維護者容易看錯成同一件事或誤植。屬於命名一致性層級的小摩擦,不影響分層或判定,建議換個更不容易混的詞(例如沿用計劃裡文字段落已經在用的「提示」譯名,如 `suggestion` 或 `hint_code`)。

## 已看,無:
- **分層與依賴方向**:計劃的「報告函式只讀帳本」與 `loop next` 改問處置閘的走法,跟現有 `cmd_loop_next → cmd_loop_status(disposal=True) → _loop_status_disposal` 這條既有委派鏈一致(`scripts/lumos:10336` 呼叫 `cmd_loop_status`;`scripts/lumos:9625-9630` 在 `disposal` 分支轉呼叫 `_loop_status_disposal`,定義在 `scripts/lumos:18265`)。`_loop_status_disposal` 已經有 `readonly` 與 `result_out` 兩個參數專門讓呼叫端唯讀取回判定結果(`scripts/lumos:18265`),回放/凍結/重寫三處呼叫都已經在用 `readonly=True`(`scripts/lumos:634`、`648`、`796`),計劃裡「報告函式在回放/凍結不印」正好接這個既有旗標,沒有新開一條讀帳路徑或跨層直呼內部私有狀態,沒有循環依賴。
- **收斂記號單一入口**:計劃 S11「loop next 改問處置閘之後不再自己另寫一筆收斂記號」跟程式現況吻合——`_loop_status_disposal` PASS 時自己會呼叫 `_loop_gov_mark(env, loop_id, "converged", "disposal gate PASS")`(`scripts/lumos:18584`),而目前 `cmd_loop_next` 委派舊(已退役)panel 閘成功時是自己另外補一筆 `_loop_gov_mark(..., "converged", "loop next 判四關全過")`(`scripts/lumos:10673`)。計劃要求改問處置閘後拿掉 `loop next` 這筆自己補的記號、只留 cap-reached 那筆(`scripts/lumos:10677` 現有),讓收斂記號只剩處置閘一個寫入點——這正是把現有的「兩處都在寫」收斂成「一處寫」,方向對、也確實是沿用既有函式而非另開一套。
- **折入數與空輪計算沿用既有函式**:計劃第二節「每輪折入數用 `_review_yield_round` 的『折』欄」、S7「各席都報 0 條算折 0,有人報了條數卻沒彙總帳才算沒記處置」,跟 `_review_yield_round`(`scripts/lumos:7364`)的既有語意一致:`F = len(carrier.get("folded_set") or [])`(有 carrier 才算得出數字,carrier 存在但 `folded_set` 空即為 0;無 carrier 則 `F=None` 印 `?`)。目前 `_loop_status_disposal` 已經在用它印「審查有沒有用」那一段觀測(`scripts/lumos:18550-18552`,只算最後一輪);計劃要擴成印每一輪,是對同一支函式按輪分組重複呼叫,不是另寫一套折算邏輯,符合「不另寫第二份」的交代。
- **命名風格**:`phase` 既有值是英文連字號小寫(`gate-pending`/`cap-reached`/`plant-canary`,`scripts/lumos:10336` 附近的 docstring),計劃提出的 `advice` 代碼(`fix-gate`/`reshape`/`accept-with-reason`/`human-decides`)沿用同一種「機器代碼英文連字號、人話另外放在 note/文字段」的既有二分,`fail_steps` 打算沿用既有的中文失敗步驟字串(如 `fails.append("條款綁定")`、`"資安席"`、`"落點"`,`scripts/lumos:18568-18578`),沒有另創一套失敗代碼枚舉,一致。
- **落點**:`Systems/loop-convergence-recording` 目前已存在但沒寫負責範圍、只管 1 支檔且未掛合約,計劃把這次的輸出段落與 cap_report 落在這篇是合理的——它本來就是收斂記號/處置閘收斂邏輯這支檔的既有落點,不是另開一篇稀釋波及計算,跟計劃 `lands_in` 欄位所寫一致。

不對齊共 1 條,其中 major 0 條。
