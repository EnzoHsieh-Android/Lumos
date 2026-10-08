severity: minor

已看過整份 diff(`scripts/lumos` 約 760 行、說明筆記、測試)。沒有 blocker 或 major。下面兩條都是縱深防禦,攻擊路徑照格式列出,但沒有實際重現,所以標推論。

**S1 終端控制字元經檔名印到終端**
severity: minor
blocking: 否 — 推論:沒實際重現,而且舊的違規輸出本來就用同一種印法。
- 攻擊路徑:攻擊者開 PR,在筆記目錄下新增一個檔名含 ESC 或 OSC 序列的 `.md`,內容放一行缺格子的 `RULE:`。維護者本機的 pre-push 或 CI 日誌印出擋下訊息時,檔名裡的控制碼就進了終端。
- 缺口:新的 `_ns_slots_format` 對缺漏描述和核心一句有做 `_esc_clean`,但路徑沒消毒。doctor 新增的那句 `f"{p}:{n}"` 也一樣。舊的 `_note_shape_report` 對路徑也是原樣印,所以這是延續舊缺口,不是新引入。
- 拿到什麼:終端標題或畫面被偽造,例如把擋下訊息畫成別的樣子。
- 修法:印路徑時一律過 `_esc_clean`。
- 引句:「out.append(f"  {p}:{n}  {'; '.join(_esc_clean(x, 200) for x in probs)}")」

**S2 被審分支自己的內容就能關掉格子檢查**
severity: minor
blocking: 否 — 推論:這是設計選擇,同樣的缺口舊的 gate 早就有,不是這次新增的洞。
- 攻擊路徑:攻擊者在自己的分支或 PR 裡做其中一件事。
  - 在 `.lumos/config.json` 加 `note_shape.slots=off`(設定從被檢查的版本讀)。
  - 或在某個提交的掛鉤裡拿掉 `note-shape --staged --slots` 記號,同一提交再寫缺格子的摘要行。
- 結果:`_ns_slots_prepare` 在推送和 CI 都會回 off,或把那些行當成「格子上線前寫的舊帳」放行。
- 拿到什麼:繞過格子檢查。這是內容品質閘,不是權限邊界,而且 `--no-verify` 與 `LUMOS_SKIP_NOTE_SHAPE=1` 本來就能繞,風險有限。
- 緩解:CI 若要當硬閘,設定與掛鉤記號應改從目標分支讀,不從被推送的版本讀。
- 引句:「if _nodehome_golive(root, tip_where, _SLOTS_GOLIVE_MARK) is None:」

**逐類結論**
1. 命令、路徑、模板注入與反序列化:已看,無。
   - git 呼叫都走參數列表(`_ns_git`、`_lens_git`),沒有 shell 插值。
   - `base_where`、`tip_where` 來自 sha 或固定字串,筆記內容沒有流進 git 參數。
   - `-S<mark>` 的記號是常數。
   - 設定用 `json.loads` 解析並限定值域(只認 block/warn/off),沒有 eval 類。
   - 範本用 `str.format`,`core` 在 `_esc_clean` 之後才代入,但範本字串是常數,`{}` 注入打不進去。
2. 登入與權限:已看,無。
3. 密鑰與個資:已看,無。
   - 寫進治理帳的 `slots_lines`、`slots_missing` 只有計數和鍵名,不含筆記內容。
   - 鍵名來自 `re.findall(r"\[([^\[\]:]+):\]")`,只匹配空值格式的訊息;這類訊息用的是 `_SLOT_REQUIRED` 裡的固定鍵,不由筆記決定。
   - `nodes` 是路徑,舊行為已經如此。
4. 加密與傳輸:已看,無。
5. 執行邊界:除 S1、S2 外已看,無。
   - 單次跳過時新增的 `_ns_skip_slot_extra` 整段包在 `try/except` 裡,失敗回 None、照樣放行,不會讓逃生口失效,也不會因此多出可被利用的執行路徑。
   - 沒有寫使用者全域設定,也沒有執行不可信位置的檔。
   - `--slots` 永久保留,避免參數解析失敗造成靜默放行,方向正確。
6. 行動端:已看,無。
7. 新依賴:無(只用既有的 `re`、`json`、`sys`)。

最高嚴重度 minor,blocking 0 條
