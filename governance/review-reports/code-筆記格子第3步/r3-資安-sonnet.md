severity: minor

# 資安審查報告(末輪)

範圍:`/tmp/code3-r3.patch`,在 repo 原樣 checkout 上對照實作。實作位置:`scripts/lumos`,圖譜鏡頭 384f4574..1685194c。審查期間沒有改任何檔,也沒有跑實驗。

## 發現

### R3S1
severity: minor
blocking: 否 — 屬於縱深防禦,而且我找不到能把控制字元塞進例外文字的輸入,所以只能標推論。
引句:「+            ok(f"度量式撤除條件觀測跳過(fail-open:{_e18})")」

推論:S18 的例外兜底原本只印例外型別名,現在改印整段例外訊息 `{_e18}`。這句直接交給 `ok()`,中間沒有經過 `_esc_clean`。`ok()` 的實作是單純 `print`(`scripts/lumos:1329`)。

- 誰:提交筆記、帳檔、設定檔的第三方。
- 從哪裡:clone 或合併進來的 repo。
- 送什麼:要讓 `_doctor_metric_lines` 丟出例外,而且例外訊息帶有他控制的字元,例如 ESC 序列。
- 拿到什麼:doctor 輸出被終端機轉義碼蓋掉或偽造。

我追過這條函式鏈。度量的閘名、種類、比較符、整數都先被 `_SLOT_METRIC_RE` 與 `_slot_retire_err`(`scripts/lumos:3805`)限成安全字元。其餘例外訊息的來源是數字溢位、`json` 錯誤和本機路徑,都不是第三方可控的文字。所以現況沒有可用的路徑。
建議:改回 `type(_e18).__name__`,或包一層 `_esc_clean`。S16 到 S19 其他輸出路徑都已清控制字元,只有這一條漏掉。

### R3S2
severity: minor
blocking: 否 — 沒有人能拿它執行程式碼或外洩資料,只能在終端機上偽造顯示,而且 `_esc_clean` 的這個缺口在這次修正之前就有。
引句:「+                lines.append(_esc_clean(f"{rel}:{why}:{(slot_parse(t[5:])['core'] or t[5:])[:40]}", _DOCTOR_LINE_MAX))」

推論:`_esc_clean`(`scripts/lumos:10453`)只清 `< " "` 和 `\x7f` 到 `\x9f`。雙向文字控制字元(U+202E、U+2066 到 U+2069)和 U+2028、U+2029 會原樣通過。

- 誰:提交惡意筆記的人。
- 從哪裡:筆記裡 RULE、FACT 之類條目的內文。
- 送什麼:帶 U+202E 的句子,讓路徑與提醒行在終端機裡視覺上重排。
- 拿到什麼:`lumos doctor` 的 S16 到 S19 提醒行看起來像在講別的節點或別的行號,誤導使用者的判斷。

這是顯示層的誤導。ESC 與 C1 控制碼已經擋掉,真正能清畫面或改標題的轉義碼進不來。S16 在這次修正已經過 `_esc_clean`,這條只是補強建議。
建議:`_esc_clean` 順手把 U+200E/F、U+202A 到 U+202E、U+2066 到 U+2069、U+2028/9 也換成空格。這是共用函式,一次改好就涵蓋全部呼叫點。

## 逐類

1. 不可信輸入流到危險操作。
   - 命令、模板、反序列化、`eval` 類:已看,無。這次 diff 沒有新增 `subprocess`、`eval`、`pickle` 或字串組命令。`_drift_jsonl_iter` 只做 `json.loads`,解析失敗和 `RecursionError` 都被接住,只留 dict。
   - 輸出路徑逐條核對:
     - S16:`_doctor_stale_rules` 的行過 `_esc_clean`,上限 `_DOCTOR_LINE_MAX`=300。
     - S17、S18 寫法不合那條、S19(兩條)、S18 成立那條:全部過 `_esc_clean`。
     - 單行 summary 那條:它走 `_note_summary_entries`,產出的字串進同樣的 `_esc_clean` 輸出,沒有另開一條不清的路徑。
     - 例外訊息:S18 兜底是唯一漏網(見 R3S1)。
     - 推送掛鉤:`_drift_retire_guarded` 與 `_drift_retire_report` 的 stderr 只印 `type(ex).__name__`,沒有使用者內容。
   - 路徑:只有 `rel` 進輸出,而且在清理之內。沒有拿筆記內容當檔案路徑去開檔。
2. 登入與權限:已看,無。這次 diff 沒有涉及認證或授權。
3. 密鑰與個資:已看,無。新增的輸出是路徑、行號、截斷過的筆記句子和例外型別名,沒有讀取或印出憑證。R3S1 的例外訊息在現況下不含祕密。
4. 加密與傳輸:已看,無。這次沒有網路或加密程式碼。
5. 執行邊界。
   - `_lint_new_config(..., from_snapshot=True)`:`text is None` 時直接回預設,有位元組時只解碼後 `json.loads`,不碰 `p.is_file()` 或 `read_text`,所以 lint-new 在 doctor 路徑上確實不再自己讀磁碟。
   - 唯一入口 `_metric_gate_off` 吃的 `cfg_text` 來自 `_doctor_cfg_bytes`(`scripts/lumos:3487` 附近)。它排除 symlink,並要求 `resolve()` 等於 `root/.lumos/config.json`,所以 `.lumos` 或 `config.json` 當捷徑都不會被跟。
   - 沒有帶 `from_snapshot` 的呼叫(`scripts/lumos:24846`、`scripts/lumos:41319`)是推送時的閘自己讀設定,保留原行為,不在這次 diff 內。`config.json` 是 symlink 時它會跟,但讀到的內容只當 JSON 解析,不會執行,也不會回印內容。
   - 掛鉤與 CI:沒有新增執行外部命令的路徑。
   - 拿掉吞 stderr 的小工具:行為上若 stderr 已關,`print` 可能拋例外。這只影響穩健性,攻擊者控制不到 stderr,不算資安問題。
6. 行動端:已看,無(不適用)。

## 新依賴

已看,無。這次只用標準函式庫(`json`、`re`、`datetime`),沒有新增套件。

## 總結

沒有可直接利用的洞。兩條都是顯示層的縱深防禦建議,而且都是推論。最高嚴重度 minor,blocking 0 條
