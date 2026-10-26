severity: major

這是 CLI 工具、不是 API 服務,所以 be-api-compat 和 be-authz 兩題我只做了有限的判斷。
- **be-api-compat:** 這輪加的結果欄位 `newer_schema`、`mainline_newer` 只是新增。`_e2e_scope_dirs` 從三項改回四項後,所有拆包的呼叫者我都查過(只有 lumos 內部三處加測試一處),沒有漏改。`_e2e_ack_targets` 改成回三項,也只有 lumos 內部的呼叫者。
- **be-authz:** 這輪沒有新增或改動「誰能動哪筆資料」的端點。

我沒有判定到的部分:`lumos impact` 對這個範圍沒有產出「這次新增的殘留」段。pre-push 只改了逃生提示的文字,我讀過差異,沒看到行為變化。你指定的鎖檔 `.warming` 不存在,我沒有動任何鎖。

我實跑了 `python3.14 scripts/test_lumos.py -k android_e2e`,結果 601 通過、0 失敗。

## 發現

### 1. 單份紀錄超過 2MB 時,判定端照樣放行,和條款 S46 不符,AI 放行也從所有看得見的地方消失
severity: major
blocking: 是

- file: `scripts/lumos:41397`(`_e2e_tree_blob` 的上限是 `_SECEV_FILE_MAX`,16MB)對上 `scripts/lumos:40951`(`_e2e_record_update` 的上限是 2MB)。
- 引句:「if p.stat().st_size > E2E_RECORD_FILE_MAX:   # 掃描與判定都不讀這麼大的紀錄,寫回也不整份讀進來(代碼審 r3 資源席)」
- 這行註解說「判定也不讀」,但判定端(`_e2e_gate_load`、`_e2e_tree_json`)沒有這道 2MB 檢查。
- 場景:提交裡放一份合格的 3MB 紀錄,內含一筆還沒人看過的 AI 放行。
  - 判定回 `status=waived`,推送放行。
  - `waive --list` 把它印成「紀錄讀不懂」,doctor 與開場提示都不列它,`--ack` 也標不到它(寫入端拒寫)。
  - 結果是 AI 放行生效了,卻沒有任何一處提示人去看。
- 條款 S46 寫的是「單份超過 2MB→放行不寫、判定擋下叫人修好或刪掉」,判定端這半句沒做到。
- 重現:用 `_e2eg_proj` 建專案,提交改動後取得 fp,寫一份 `{"schema":1,"fingerprint":fp,"runs":null,"waivers":[AI 放行],"pad":"x"*3MB}` 並提交,再跑 `_e2eg_check`。
- 結果:修前 `rc=0 status=waived`,修後 `rc=0 status=waived`,兩版相同。
- 補一個直接證據:`_e2e_tree_json` 讀這份回 dict、`_e2e_record_err` 回 None,同一份用 `_e2e_record_update` 回「超過單份紀錄的大小上限(2MB)」。
- 歸因:有證據的原有漏查。判定端的缺口修前就有,這輪只補了寫入端,卻聲稱兩端同一套。

### 2. S46 的「git 暫時讀不出→不叫人刪」沒有任何測試守,改回舊寫法測試仍全綠
severity: major
blocking: 是

- file: `scripts/lumos:41694`(`_e2e_gate_load` 的 `bad_record="git" not in rerr`)。
- 引句:「_e2e_gate_block(f"查證紀錄 {rerr}", bad_record="git" not in rerr, **info)」
- 條款 S46 把這個行為綁在 `t_android_e2e_record_unreadable`,但該測試只有 `bad_record` 為真的斷言(測試檔裡 `bad_record` 只出現在 19737、20737 兩處,都是真值)。
- 最小重現(我把修後版本複製到暫存目錄做變異):
  - 把 `bad_record="git" not in rerr` 改成 `bad_record=True`。
  - 跑 `-k android_e2e_gate`,116 通過 0 失敗。
  - 再跑 `-k android_e2e_record_unreadable`(8 通過)與 `-k android_e2e_gate_bad_record`(11 通過),全綠。
- 行為證據:刪掉樹裡紀錄那個物件後,修前 `bad_record=True`(叫人修好或刪掉一份其實沒壞的紀錄),修後 `bad_record=False`。所以修補本身有效,只是沒人守它。
- 這個行為是 S46 明列的必要行為,不是覆蓋面可以更完整的那種。
- 歸因:有證據的修復回歸(修補新增的行為缺測試)。前後差異已實測。

### 3. `--ack` 把「紀錄太大」說成「讀超過 60 秒」,叫人再跑也不會有用
severity: minor
blocking: 否

- file: `scripts/lumos:41878`(`_e2e_ai_pending_all` 的 `unread += 1`)與 `scripts/lumos:41919`(`_e2e_ack_targets` 取回 `unread`)。
- 引句:「if path is None:   # 太大的不讀,但算進沒讀的份數(裡面可能有待看的放行;r3 資安席)」
- 這份數同時包含「太大不讀」和「時間到了」,`_e2e_waive_ack` 卻一律印「另有 N 份沒讀(讀超過 60 秒),那幾份這次沒標;再跑一次這個指令」。
- 重現:放一份 >2MB 且有 AI 放行的紀錄,呼叫 `_e2e_ack_targets(root, [], True)`,回 `([], 1, None)`。使用者會看到「讀超過 60 秒、再跑一次」,但再跑永遠一樣。
- 歸因:有證據的修復回歸。修前沒有 `unread += 1`,也沒有這段訊息;這輪新增了計數,訊息卻沒分原因。

### 4. `waive --list` 改成讀全部紀錄後沒有時間上限,和「只留時間上限」的說法不符
severity: minor
blocking: 否

- file: `scripts/lumos:41853`(`_e2e_records_all`)與 `scripts/lumos:41856`。
- 引句:「for fp, path in _e2e_record_files(root, cap=None)[0]:   # waive --list 用:讀全部」
- 這條路徑沒有 budget,而且要整份讀完才開始印。
- 實測:300 份約 1MB 的紀錄花 32.2 秒;同一批用 `_e2e_ai_pending_all(cap=None, budget=60)` 只要 4.0 秒。依此推算,3000 份大紀錄會是五分鐘以上、期間沒有任何輸出。
- 修前最多讀 500 份,所以上限是有的。
- 歸因:有證據的修復回歸。

### 5. 寫入端多驗了結束時間後,舊紀錄壞掉時 judge 重跑也一併被擋
severity: minor
blocking: 否

- file: `scripts/lumos:40965`。
- 引句:「err = err or _e2e_record_err(rec, fp) or _e2e_gate_times_err(rec)」
- 場景:既有紀錄有任一筆 `feature_runs.ended` 讀不懂,`judge` 的 `mutate` 本來會把整份 `runs` 換掉,現在連重跑都拒寫,只能手動修或刪。
- 這和「寫入與判定同一套」一致,而且擋下訊息有說原因。我不判它錯,只標它是行為變化。
- 歸因:未判定。

## 三問

**① 原問題的修復效果有何行為證據?**
- 外來文字統一清:`_e2e_gate_out("blocked","x\ny\x1b[31m", bad_cases=[("k\n1","沒過")], cases=["a\tb"], t=(("a\n",),))` 回 `reason='x y [31m'`、`bad_cases=[('k 1','沒過')]`、`cases=['a b']`、巢狀 tuple 內層也清了。
  - fp、commit、record 路徑、整數、布林、None 都不變。
  - dict 值不清,但目前所有呼叫處都沒有帶 dict。
- `_e2e_prefixes`:
  - `("a/b/c",0)→[]`
  - `1→['a']`
  - `5→['a','a/b','a/b/c']`
  - `("",2)→['']`
  - `("a/b/",3)→['a','a/b','a/b/']`
  - 在 flows 的鍵都已正規化、git 路徑沒有空段的前提下,跟舊的 `_e2e_under` 等價。
- 缺了 git 物件時 `bad_record` 由 True 變 False(修補有效,但無測試,見 2)。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 大部分成立。
  - `_e2e_scope_dirs` 四項的所有拆包處都對。
  - 主線設定不同時多算的兩端指紋,用 `allow_missing=True` 的結果合理:兩端都缺的新模組算相等,分支刪掉或自己新建就會擋。
  - 根提交的上一版檢查會因 `rev-parse` 回空而不擋。
  - `newer_schema` 只在 `schema > E2E_SCHEMA` 時才成立。
- 不成立的相鄰路徑是發現 1(大小上限兩端不一致)和發現 4(`--list` 無上限)。

**③ 新發現的同一案例在修前、修後各是什麼結果?**
- 發現 1:修前 waived,修後 waived,同一個缺口,修補沒碰到判定端。
- 發現 2:修前 `bad_record=True`,修後 `bad_record=False`,無測試守。
- 發現 3:修前沒有這個訊息,修後出現誤導訊息。
- 發現 4:修前最多讀 500 份,修後不設上限。

最高等級 major,擋實作的 2 條(發現 1、2)。

我已用字面絕對路徑刪掉暫存目錄 `/private/tmp/lumos-seat-work/code-e2e-gate/正確性-sonnet`。
