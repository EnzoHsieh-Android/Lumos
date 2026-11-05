severity: minor

**逐類結果**

- ① 提示注入:已看,無。`check.py` 的 `message_problems` 與型錄檢查只讀本機規則檔,輸出是給人看的問題清單,沒有把自由文字塞進派工詞或 hook 附加段。`_cl_say_lint_block` 把訊息從 70 字放寬到 120 字,內容仍只是規則 message(來源是 repo 內規則檔),沒有新增注入面。
- ② 讀寫與執行越界:已看,r2 的第 2 條已修,另有一條新的推論級發現。
  - `scripts/test_lumos.py` 的 `wrap.write_text(...)` 和 `cmd = f"{_shlex.quote(sg)} scan --config {_shlex.quote(str(pack))} ..."` 都改用 `shlex.quote`。路徑含空白或 `;`、`$()` 時不會被拆開執行。新增的逾時包裝腳本是固定內容 `sleep 5`,沒有插值。
  - `check.py` 呼叫 ast-grep 一律用 list 參數的 `subprocess.run`,沒有 `shell=True`。`_TIMED_OUT` 只是模組內旗標,不碰檔案。
  - CI 新增 `pip install ast-grep-cli==0.51.1`,版本已釘,屬依賴供應鏈,依規則不報。
  - 新增內容裡沒有密鑰或信箱(對 snapshot 的新增行掃過金鑰樣式與信箱)。出現 `shell=True` 的字樣全在審查卷證和筆記的敘述裡,不是新程式碼。
- ③ 一步繞過:已看。r2 的第 1 條已修,`node_home.ignore` 現在只認 `samples/*.kt` 和 `samples/*.kts`。`review-fp-` 豁免也收緊了,現在要同時符合三件事:樣本在自己那條規則的目錄(`owner == rule_id`)、檔名以 `review-fp-` 開頭、該規則屬於語意覆核級。測試新增了「會擋的規則的 `review-fp-` 好例照樣報誤報」,所以把 `review-fp-` 檔放進別條規則的好例目錄,或放進會擋的規則的目錄,都不會被放過。`include_test_paths` 經過型別與副檔名檢查,壞值只告警並當沒設,預設為空,等於照舊排除測試路徑。

**發現**

severity: minor
blocking: 否
1. 這條屬推論,我沒有實測。`_RULEPACK_SAMPLE_RE` 中間用 `.*`,所以只要路徑是 `configs/ast-grep/<任一目錄>/samples/…/任何名稱.kt`,就不進風險分級和新增告警閘的掃描。
   - 誰:照常操作的使用者或 AI。
   - 從哪:在 `configs/ast-grep/*/samples/` 底下放一支 `.kt` 或 `.kts`。
   - 送什麼:含真正風險寫法的 Kotlin 檔。
   - 拿到什麼:該檔的新增行不會被風險掃描和 `lint-new` 看到,等於一個不受閘管的目錄。
   - 縮小點:這個目錄本來就是工具鏈放教材樣本的地方,產品碼不放這裡。這個排除是明說的設計,而且只有 Kotlin 副檔名;在別的檔放入口得靠人刻意搬動。另外 `<任一目錄>` 沒鎖定成真實存在的規則包名,要鎖的話可改成只認有 `sgconfig.yml` 的目錄。
   引句:「_RULEPACK_SAMPLE_RE = re.compile(r"configs/ast-grep/[^/]+/samples/.*\.kts?$")」
   file: `scripts/lumos` 的 `_stack_changed_ok`。

**總結**:r2 留下的兩條縱深防禦問題這輪都已處理,沒有可直接利用的洞,只剩一條推論級的樣本目錄排除範圍問題,不擋。
