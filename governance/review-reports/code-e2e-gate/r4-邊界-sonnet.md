severity: major

我的臨時目錄已用字面絕對路徑刪掉。審查途中我把 e2e-gate 的工作目錄暫時切成 detached HEAD,隨即切回 `EnzoHsieh-Android/e2e-gate`,指到 de8a99bc,沒有改任何檔。

## Findings

1. 讀不懂紀錄的錯誤訊息把外來的功能鍵名原樣帶出,寫入路徑沒清

severity: major
blocking: 是

引句:「return f"feature_runs 的 {k}:skipped 要是字串清單、items 要是 {{kind, name, result}} 清單"」

file: `scripts/lumos:40741`(新增訊息)、`scripts/lumos:40966`(`_e2e_record_update` 原樣包進回傳)、`scripts/lumos:42021`(waive)、`scripts/lumos:41955`(--ack)、`scripts/lumos:41236`(跑完寫紀錄)

- 失敗場景:
  - 被推送提交帶一份紀錄,`feature_runs` 的鍵名含 ESC、OSC 序列或 U+202E,而且 `items` 不是清單。
  - 開發者或 AI 在本機跑 `waive`、`waive --ack` 或跑驗收寫紀錄,訊息 `擋下:…讀不懂(feature_runs 的 <原樣鍵名>:…)` 會原樣印到終端,也進 AI 視野。
  - 判定那條路走 `_e2e_gate_out` 已清掉;寫入這條路沒有。本輪宣稱的「外來文字在出口統一清」在這裡不成立。
- 重現:
  - 在臨時 git repo 放 `.lumos/e2e-records/<64 個 a>.json`,內容是 `feature_runs: {"f\x1b]0;PWNED\x07.c\u202e": {"result":"pass","items":"x"}}`。
  - 呼叫 `_e2e_record_update(root, fp, lambda r: None)`,回傳的錯誤字串裡 `\x1b]0;PWNED\x07` 與 U+202E 都原樣保留。
  - 同一段文字經 `_e2e_gate_block("查證紀錄讀不懂:"+err)` 時,控制字元已換成空格。
- 歸因:有證據的修復回歸。修前 `_e2e_record_err` 的訊息不含 `{k}`(`git show bf9dac49:scripts/lumos` 的同一函式),修後新增鍵名外洩。

2. 紀錄大小上限在判定與寫入兩邊不一樣(2MB 對 16MB)

severity: minor
blocking: 否

引句:「if p.stat().st_size > E2E_RECORD_FILE_MAX:   # 掃描與判定都不讀這麼大的紀錄,寫回也不整份讀進來」

file: `scripts/lumos:40960`、`scripts/lumos:41408`、`scripts/lumos:8524`

- 失敗場景:
  - 提交樹裡 2MB 到 16MB 的紀錄,判定端照讀、照放行或照擋(上限是 `_SECEV_FILE_MAX`,16MB)。
  - 寫入端(waive、--ack、跑完寫紀錄)一律以「超過單份紀錄的大小上限」拒寫。
  - 一份被擋、又大於 2MB 的紀錄,放行與重跑都寫不進去,只能刪檔。這是失敗即擋的安全方向,但註解說的「判定與寫入同一套」不成立。`history` 每跑一次追加一筆且沒有上限,所以長期用同一指紋也會慢慢碰到。
- 重現:未能當場翻紅。這是從兩個常數與兩處程式讀出的差異,我沒有造 2MB 以上的紀錄實跑。
- 歸因:有證據的修復回歸(寫入端的大小檢查是本輪新加,修前寫入端沒有這道)。

3. 超過單份上限的紀錄永遠算「沒讀到」,提示每次開場都出現

severity: minor
blocking: 否

引句:「if path is None:   # 太大的不讀,但算進沒讀的份數(同 lumos 的 _e2e_ai_pending_all)」

file: `scripts/hooks/claude/lumos-entry-hook.py:322`、`scripts/lumos:41889`

- 失敗場景:
  - 一份超過 2MB 的紀錄會讓開場掛鉤與 doctor 永遠報「另有 N 份沒讀」。
  - `waive --list` 對它只印「紀錄讀不懂」,`--ack` 也標不了它,使用者無法用任何指令讓提示消失,只能刪檔。
  - `--ack` 的提示文字還寫成「(讀超過 60 秒)」,但實際可能是檔案太大。
- 重現:未能當場翻紅(同上,沒造大檔)。
- 歸因:有證據的修復回歸(`unread += 1` 是本輪新加)。

## 邊界逐項

照程式走的結果如下,除上面三條外都成立。

- 結構與路徑:
  - `_e2e_prefixes`:maxd=0 回空;`paths` 寫 "." 在前面的路徑檢查就被擋;app 路徑剛好等於 maxd 層或多一層、flows 是目錄或空,都正確。
  - 對舊版 `_e2e_scope_hit` 與 `_e2e_owners` 做了 20000 組隨機對照(含 `./` 開頭、結尾斜線、flows 為目錄、有無 exclude),新舊零差異。
  - `shared_paths` 等於 `app_dirs`、`./app`、app_dirs 帶 `./` 或結尾斜線都放行;`.//x`、`app/./x`、`.`、空字串、`APP/x`、`app` 對 `app/src`、`lib` 都擋下。
- 紀錄欄位:
  - schema 為 0、負數、字串、True、1.0 都被擋,訊息一致。
  - `skipped` 或 `items` 為 null、`ran` 為清單或 `ran.flows` 為 null 都被擋;三個欄位缺漏則放行。
  - schema 為 0 時訊息寫「比較新就更新 lumos」,措辭誤導,但仍判擋。
- `--commit` 與查主線失敗:
  - 大寫十六進位以 `.lower()` 比對,正確。
  - 十六進位剛好等於分支或 tag 名時,若沒有以它開頭就拒絕。縮寫此時不能用,屬於判不清就擋。
  - 查主線失敗且上一版為根提交時,`sha^1` 為空,不擋、走 `none`。上一版沒有設定檔時 `_e2e_tree_json` 回 `(None, None)`,不誤擋。
- 不處理的字元:
  - U+2028 和零寬字不清,這是 `_esc_clean` 文件註明的設計取捨,不是本輪新增,不判。
  - 雙向覆寫字元在判定出口確實被清,錯誤出在 finding 1 的寫入路徑。
- 沒有實跑,結論只靠讀程式:
  - `ended` 有毫秒或 Z:`_e2e_gate_times_err` 本輪沒改,只是被寫入端接上。
  - 上一版是合併提交:只看 `^1`,我讀了程式但沒造案例。
  - 紀錄超過 2MB 正好在邊界:判定端與寫入端的 `<=`、`>` 方向一致。
  - `--ack` 時有 0 份紀錄:走「沒有還沒人看過的 AI 放行」,rc 0。
  - 紀錄目錄不存在:我讀了程式,沒造案例。

## 三問

① 修復效果的行為證據:
- 前綴查表只查到 maxd 層,結果與舊版逐層查表在隨機對照中零差異。
- `shared_paths` 不在 `app_dirs` 底下現在被擋,`.//x` 被擋。
- 紀錄欄位型別不對時,現在由 `_e2e_record_err` 擋成「讀不懂」,不再走進判定內部出錯。
- 判定端的外來文字已清:鍵名中的 ESC 與 U+202E 在 `_e2e_gate_block` 輸出裡換成空格。

② 修補處相鄰路徑是否成立:
- 不全成立。統一清只做在判定出口,寫入路徑(`_e2e_record_update` 與它的三個呼叫端)不經過它,即 finding 1。
- 「寫入與判定同一套」只成立在 `_e2e_record_err` 加 `_e2e_gate_times_err`,不成立在大小上限,即 finding 2。

③ 新發現修前修後各是什麼:

| 項目 | 修前 | 修後 |
|---|---|---|
| finding 1 | 訊息不含鍵名,沒有外洩 | 訊息帶原樣鍵名,寫入路徑外洩 |
| finding 2 | 寫入端沒有大小檢查 | 寫入端 2MB 拒寫,判定端 16MB 放行 |
| finding 3 | 超大紀錄在掃描時被略過,不計入沒讀的份數 | 計入,而且永遠算沒讀 |

最高等級 major,擋實作的 1 條(finding 1)。
