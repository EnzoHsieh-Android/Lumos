severity: minor

這條是縱深防禦類,攻擊路徑是推論,沒有實測。其餘各類已看,無可利用的洞,逐類結論在最後。

severity: minor
blocking: 否
引句:「return c in "\u200c\u200d\u00ad" or 0xE0020 <= ord(c) <= 0xE007F」
file: `scripts/lumos:6926`
- 攻擊者:陌生 repo 的作者,或能改計劃筆記的協作者。
- 送什麼:在 `pending_questions` 某題的 `text` 裡夾一串 U+E0020–E007F 的標籤字元。這組字元是 ASCII 的隱形鏡像,終端和 diff 裡看不到,但語言模型讀得到。
- 拿到什麼:`lumos pitfalls --stage`、`spec-gate` 的阻塞題清單和推送前提醒,會把題目文字原樣印出。讀輸出的 AI 工作階段(lumos 的主要讀者)可能讀到人看不見的指令,也就是間接提示注入。
- 為什麼放行:`_pq_cf_ok` 為了 emoji 旗幟序列,放行整段 U+E0020–E007F。旗幟序列只用到其中很小一部分,例如 U+E0067 到 U+E007F。
- 限制:攻擊者本來就能寫可見的題目文字,所以多出來的只是對人隱形。因此只算縱深防禦。
- 建議:印到終端前,把題目文字裡所有 U+E00xx 字元換成可見的跳脫寫法。或者只在緊接旗幟 emoji 基底時才放行。ZWJ、ZWNJ、軟連字號同理,會讓人眼比對失準,影響較小。

逐類結果(已看,無):
1. **範圍字串注入**:已看,無。
   - 開頭是 `-` 的範圍在 `_spec_gate_push_check` 被擋掉。
   - 中間帶 `--`、`$(…)`、換行的字串全程用 argv 傳給 git,沒有 shell。
   - `_is_commit` 用 `--end-of-options` 加 `^{commit}` 驗兩端,`HEAD:path`、`--output=` 這類形狀驗不過,就跳過提醒。
   - 範圍中間夾換行時,`_nodehome_cat_blobs` 偵測到 `\n` 會整批回 None,安全失敗。
   - `_range_base` 的 `merge-base` 沒加 `--end-of-options`,但前面的 `git diff … git_range --` 會先把不合法的範圍擋掉,放行回 0。
2. **終端偽造**:已看,無(除上面那條)。
   - `id` 用 ASCII 數字嚴格比對。
   - 格式不對的題號、`{…!r}` 的錯誤訊息都經過 repr 或 `ascii()`。
   - ESC 和雙向覆寫屬於 `_PATH_SPECIAL_CATS`,仍然被擋。
   - 檔名裡的控制字元在 `core.quotePath=false` 下仍被 git 加引號,過不了 `startswith(vrel+"/")`。
3. **寫鎖被符號連結繞過**:已看,無。`_vault_lock_held_for` 對 `path` 做 realpath。指到庫外的連結會讓比對失敗並拒寫,是失敗關閉;`os.replace` 只換連結本身,不會寫到目標。
4. **命令列參數寫進筆記**:已看,無。
   - 換行和控制字元被 `_pq_bad_char` 擋掉,值走 `_yaml_quote`。
   - 寫後用 `_check` 重新解析整份文字並比對,對不上就不寫。
   - `question-set` 的鍵有白名單,`id` 不能改。
5. **規格閘被惡意 repo 繞過**:已看,無。頂格鍵寫錯、清單被切斷、重複鍵、`true # 註解` 這類寫法都走錯誤路徑,規格閘擋下。作者本人能自己把題標成「已決」,但規格閘本來就不是防作者的邊界。
6. **密鑰與個資**:已看,無。
7. **加密與傳輸**:已看,無。
8. **執行邊界**:已看,無。沒有 `shell=True`、`eval`、反序列化。
9. **行動端**:不適用。
10. **新依賴**:已看,無。

總結:整份 diff 只有一條縱深防禦等級的發現(標籤字元可夾帶對人隱形的文字),沒有可直接利用的洞。
