severity: minor

## F1 r2 審計修正紀錄的條數對不起來,也沒寫放行落在哪份 intake
severity: minor
blocking: 否
引句:「5 條/blocking 0/折 1 條說明(報告不含驗收素材)、放行 3 條;卷證同上。」
file: docs/lumos-toolchain-knowledge/Projects/端到端驗收對照表涵蓋報告_計劃.md:72

1. 這行寫 5 條,但折 1 加放行 3 只有 4 條,少交代 1 條。
2. 鄰居的寫法是折與放行加起來等於總數。例如 Android端到端驗收_計劃.md:345 的「52 條……折 47 條、放行 5 條 minor(見 r3-intake.md)」。
3. 鄰居有放行時會附 intake 出處。這行只寫「卷證同上」,沒指到哪份 intake。

## F2 r2 的「例」沒有綁測試或手動驗證標記
severity: minor
blocking: 否
引句:「只改 `.maestro/baseline/home_visual.png` 與門檻檔 → coverage --changed 列 0 支,check 要整套;說明改成「程式檔部分」並講明素材另計。」
file: docs/lumos-toolchain-knowledge/Projects/端到端驗收對照表涵蓋報告_計劃.md:73

同一份筆記 r1 的兩條「例」都帶 `[test:t_android_e2e_coverage_…]`(67–69 行)。這條例子描述了可重現的行為,卻沒有 `[test:]` 或 `[manual:]`,跟 r1 的寫法不一致。

## 三問

1. **分層與依賴方向**:沒有改到。修補只動了 `_e2e_coverage_report` 的 docstring(scripts/lumos 約 42140 行)和計劃筆記的三處文字,沒有新的呼叫或 import,函式簽名也沒變。依賴方向跟 r3 完整改動一樣,仍沿用 `_e2e_scope_hit`、`_e2e_file_owner`、`_e2e_owner_ctx`。

2. **命名與錯誤處理**:docstring 的出處標註「(代碼審 code-e2e-coverage r2 兩席)」跟鄰居同格式,例如 scripts/lumos:1279 的「(代碼審 code-凍結暫存檔清理 r3 正確性席)」。差別是鄰居點的是具體席名,這裡只寫「兩席」,我判為 minor 以內。docstring 開頭仍是單源指向計劃筆記,跟 `_e2e_*` 群一致。審計紀錄的問題見 F1、F2。計劃筆記本文裡「程式檔裡」「驗收素材不列」的措辭,跟同檔第 1 項及 `--changed` 的說明互相呼應,沒有新增說法。

3. **第二種做法**:沒有。沒有新的函式、旗標、錯誤出口或輸出路徑,只是修改說明文字。

不對齊共 2 條,其中 major 0 條
