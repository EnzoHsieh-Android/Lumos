severity: major

審查範圍是 r5-repair.patch 的每個 hunk,全程在臨時 repo 與 `--depth 1` 淺層 clone 上實測。未碰 e2e-gate 工作樹。實驗目錄已用字面絕對路徑刪除。

1. 淺層 clone 裡拿掉驗收設定的提交被放行(修補處的第三種「查不出上一版」)
severity: major
blocking: 是
引句:「parts = raw.decode().split()」
file: `scripts/lumos:41632`(`_e2e_parent`),呼叫端 `scripts/lumos:41658`。
- 失敗場景:淺層 clone 裡,被推送提交已被截斷,`rev-list --parents` 對它只印出自己,`_e2e_parent` 回 `("", None)`,等於「根提交」。這時主線查不到、提交又刪了 `.lumos/macrobench.json`,呼叫端不擋,判定回 `none`、rc 0。
- 修補只分開了 git 失敗和沒有上一版,「上一版被截斷」仍混在「沒有上一版」裡,跟「判不清就擋」相反。
- 重現:`_e2eg_proj` 建 repo,在 feat 提交刪掉 `.lumos/macrobench.json`。
  - 完整 repo:`blocked`,原因是「這個提交拿掉了 e2e 段」。
  - `git clone --depth 1 --no-local -b feat file://...` 之後跑 `lumos android-e2e check`:`{"status": "none", "reason": ""}`,rc 0。
- 測試為何抓不到:`t_android_e2e_gate_r4_paths` 只用 mock 的 `("", None)` 代表根提交,不涉及淺層。
- 歸因:有證據的原有漏查。修前 `de8a99bc` 的 `rev-parse -q --verify sha^1` 在同一場景也回空,同樣 `{"status": "none"}`。但修補把這一段宣稱成「git 失敗與沒有上一版分開」,這個相鄰情形卻沒顧到。
- 修法方向:`_e2e_parent` 要在 `git rev-parse --is-shallow-repository` 為真,或 sha 在 `.git/shallow` 裡時回錯誤。

2. `waive --list` 沒讀完或全是太大的紀錄時,仍印「沒有任何放行。」
severity: minor
blocking: 否
引句:「print(f"注意:另有 {len(files) - i} 份沒讀(讀超過 {budget:g} 秒);再跑一次會從最新的開始讀", file=sys.stderr)」
file: `scripts/lumos:41935-41960`(`_e2e_waive_list`)。
- 失敗場景一:`budget=0` 且有 3 份帶 AI 放行的紀錄時,stderr 說 3 份沒讀,stdout 卻印「沒有任何放行。」。
- 失敗場景二:唯一一份紀錄是 2MB+1 時,先印「? … 紀錄超過 2MB,沒讀」,再印「沒有任何放行。」。
- 「再跑一次會從最新的開始讀」是錯的:排序固定從新到舊,重跑每次都讀同一批前段,後段永遠讀不到。
- 重現:`_e2e_waive_list(root, budget=0)` 實測確認。2MB+1 的紀錄走真實 `waive --list` 也確認。
- 歸因:時間用完那條路是有證據的修復回歸。修前 `_e2e_records_all` 一次讀完,沒有中途截斷。太大那條是原有漏查。修前太大的給 `(None, "太大")`,結尾一樣印「沒有任何放行。」。

3. 「單一出口」沒收齊:`judge` 的擋下訊息仍是原樣輸出
severity: minor
blocking: 否
引句:「print(f"擋下:{err}" if err else "工作目錄乾淨,可以開跑。", file=sys.stderr if err else sys.stdout)」
file: `scripts/lumos:42182`(precheck),另有 `scripts/lumos:42167`(`_e2e_judge_blocked`)、`41333`、`41349` 同樣沒走 `_e2e_say_block`。
- 失敗場景:工作目錄有檔名帶 ESC 的未追蹤檔,precheck 照原樣印出。這是外來文字直接進終端。
- 重現:建 `app/src/main/x\x1b[31mevil受波及合約的測試沒過.kt`,跑 `judge --precheck`。stderr 為 `'擋下:工作目錄有沒提交的改動…app/src/main/x\x1b[31mevil受波及合約的測試沒過.kt…'`,ESC 與逃逸帳字樣都原樣在。
- 影響較小,因為這條輸出不經過 pre-push 的 `$_cl_out`。
- 歸因:有證據的原有漏查。這幾行修前後都沒動,但 `_e2e_say_block` 的文件字樣是「一律清(單一出口)」。

4. 路徑源頭檢查漏了代理字元(Cs)、私用區(Co)和未指派(Cn),擋下時訊息誤導
severity: minor
blocking: 否
引句:「if any(unicodedata.category(ch) in ("Cc", "Cf", "Zl", "Zp") for ch in p):」
file: `scripts/lumos:40333`。
- 失敗場景:`app_dirs` 含 `"zz/\ud800x"`(JSON 轉義寫法)時,`_e2e_relpath_err` 回 None。
- 結果仍是擋下,所以判定沒放行。但擋下理由是「列不出 15ff0a17 的檔案樹」,像是 git 壞了。`macrobench --check-config` 則說「zz/ x 在專案裡不存在」,把問題指向路徑不存在。
- 另外 `"/".join(["a"]*64) + "/"`(64 層加尾斜線)被判「超過 64 層」,而同一個目錄不帶尾斜線的 63 斜線寫法會過。這是計數少處理 `rstrip("/")` 的小邊界。
- 歸因:都是有證據的原有漏查。修前 `de8a99bc` 的 `_e2e_relpath_err` 在 `p.strip()` 前完全沒有類別檢查,也沒有層數檢查。

未發現問題的邊界(實測):
- 路徑 63 斜線過、64 與 65 擋。
- 全形空白、中文、日文檔名過。
- ZWJ 表情、Tab、U+FEFF、NUL 都擋。
- 清單 1000 過、1001 擋(`app_dirs`、`exclude`、`shared_paths`)。
- flows 不受限。
- 紀錄恰好 2MB 放行、2MB+1 擋且 `bad_record=True`。
- 兩串逃逸帳字樣出現一次、兩次、重疊、夾在路徑裡都被拆開。
- `_cfg(None)` 不會炸。
- 清單 1000 項時,每個改到的檔做範圍比對約 140 微秒。

三問:

① 修復效果的行為證據
- 外來文字:路徑含逃逸帳字樣時,`macrobench --check-config` 印成「受波 及合約的測試沒過」。`/gate` 結果與 `cl` 輸出也都被拆開。
- 控制字元與 ZWJ:設定含 ZWJ 的路徑,在 gate 與 check-config 都被擋,理由清楚。
- 紀錄大小:2MB+1 的提交內紀錄被擋且 `bad_record=True`,2MB 整放行。
- `--list`:太大的紀錄標「?」,不中止。
- cfg_weakened:`t_android_e2e_gate_r4_paths` ③ 的「改回」提示成立。

② 修補處相鄰路徑是否成立
- 不完全成立。`_e2e_parent` 沒處理淺層截斷(finding 1)。`_e2e_say_block` 沒覆蓋 `judge`、`precheck`、`history` 的擋下行(finding 3)。源頭類別檢查沒含 Cs、Co、Cn(finding 4)。`--list` 的收尾訊息跟沒讀完不一致(finding 2)。

③ 新發現修前修後各是什麼
- finding 1:修前 `{"status": "none"}`,修後同。
- finding 2 的時間用完那條:修前沒有這條路徑,修後新出現。
- finding 2 的太大那條:修前修後都印「沒有任何放行。」。
- finding 3:修前修後都是原樣輸出。
- finding 4:修前修後都接受代理字元。

最高等級 major,擋實作的 1 條(finding 1)。
