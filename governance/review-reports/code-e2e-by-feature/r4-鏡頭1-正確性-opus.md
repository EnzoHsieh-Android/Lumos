severity: major

## F1 記憶體情境改弱以後指紋不變，舊的通過紀錄照樣對得上
severity: major
blocking: 是
file: `scripts/lumos:40544`（`_e2e_fingerprint`）；`scripts/lumos:40509`（`_e2e_thresholds_err` 讀最外層的 stability_scenarios）
失敗場景：指紋只算 e2e 段、app_dirs、驗收素材和門檻檔。stability_scenarios 放在 macrobench.json 最外層，不算進指紋。輸入如下：先提交一份含 `stability_scenarios.player = {scenario: player_cycle, driver: "sh drive.sh", cycles: 50}` 的設定，算一次指紋；再把它改成 `driver: "true", cycles: 1`，提交後重算，指紋一字不差。結果是這一版既有的 runs 與 feature_runs 的通過紀錄（同一個指紋檔）照樣算數。計劃〈查證紀錄長怎樣〉寫的原則是「驗收的範圍或標準變了就該重驗」，這次新加的多情境寫法讓記憶體標準可以在指紋外面改掉。stability 段本身原本就有同一個缺口。
重現（當場就能翻紅）：用 SourceFileLoader 載入 scripts/lumos，在臨時 git repo 提交上面那份設定，呼叫 `_e2e_config_at(d, head)` 和 `_e2e_fingerprint(d, head, full["e2e"])`；把情境改弱、提交，再算一次。兩次都是 `c804680c2dc48714…`，連 stability 段的 driver 與 cycles 一起改弱也不變。
歸因：有證據的原有漏查。兩版查證：`git -C <before 副本> rev-parse HEAD`=4b056532…，`git -C <after 副本> rev-parse HEAD`=7988107c…。兩版跑同一支腳本，都輸出同一個指紋 `c804680c…`，三步都沒變。這不是修補造成的。
引句:「canon = json.dumps(e2e, sort_keys=True, separators=(",", ":"), ensure_ascii=False)」

## F2 整套跑後來沒過，feature_runs 還留著同一版較早的通過
severity: minor
blocking: 否
file: `scripts/lumos:41288`（整套 judge 的 `_put`）、`scripts/lumos`（`_e2e_feature_record` 的 `_put`）
失敗場景：同一個指紋，先用 `--case login.ok` 跑，完整通過，寫進 `feature_runs["login.ok"]` 一筆 pass；之後整套跑，`.maestro/login.yaml` 沒過，`runs.result=fail`。整套的 `_put` 只蓋 runs，所以同一份紀錄裡較新的 runs 說 login.yaml 沒過，feature_runs 卻說用它的情境通過。計劃說下一批推送前檢查會按功能去讀 feature_runs，照現在的資料它會收下這筆過期的通過。這跟計劃的「最近一次的結果才算數、重跑出現的失敗就是真訊號」相反。S27「整套跑不蓋掉 feature_runs」照字面做到了，但兩條規則在這裡打架。建議：整套跑時，把 feature_runs 裡用到沒過項目的情境標成被較新的整套結果推翻，或者在計劃裡明講推送檢查要拿 runs 的時間比。
歸因：未判定。這是設計層的問題，修前修後的程式都只寫 runs（兩版這段一樣）。沒有實跑整套跑後疊按功能跑的場景，靠讀程式判定。
引句:「rec["runs"] = runs」

## F3 拿掉「工作目錄的 e2e 段跟 HEAD 不一樣」那道檢查，測試照綠
severity: minor
blocking: 否
file: `scripts/lumos:41061`
失敗場景：如果 `.lumos/macrobench.json` 被 git 忽略，沒進版控，判讀前檢查會算乾淨。這時 `_e2e_config_at` 回 (None, None)，靠這道檢查擋下不寫紀錄；拿掉它，就會變成拿 None 呼叫 `_e2e_fingerprint`，在 `e2e["app_dirs"]` 那裡丟 TypeError。改壞方式：把 `if why is None and e2e_h != e2e:` 換成 `if False:`，清掉 __pycache__ 後跑 `-k feature_record`（20 過 0 紅）和 `-k by_feature`（22 過 0 紅），全綠。測試裡也搜不到「跟 HEAD 提交的不一樣」這句訊息。對照組：另外三種改壞都翻紅了，見文末。
歸因：未判定（只在修後跑過改壞，修前沒做同樣的改壞）。
引句:「if why is None and e2e_h != e2e:」

## F4 記憶體情境逾時後收手了，效能還是照等一輪上限
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh`（accept 的記憶體迴圈 break 之後）
失敗場景：裝置在記憶體情境中途掉線，收集腳本等滿 `LUMOS_E2E_LONG_TIMEOUT`（預設 3600 秒）後回 None。迴圈 break、印「剩下的情境這次不跑」，可是接著照樣進效能迴圈，第一個效能方法對著一台掉線的裝置再等一次 3600 秒才 break。這次修補的目標是「效能或記憶體卡住就不往下等」，跨塊的那一段沒蓋到。
歸因：有證據的原有漏查。兩版模板 diff 顯示，修後只在各自的迴圈裡加了 break，沒有跨塊旗標；修前連各自的 break 都沒有。沒有在裝置上重現，未能重現。
引句:「say(f"記憶體情境 {scn or 'stability 段本身'} 逾時或跑不起來,剩下的情境這次不跑")」

## F5 run-id 跟「另一次的 run-id.情境」撞名，白跑一次沒判完
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh`（preflight 只查 `history.jsonl` 和 `run_dir/steps.json`；記憶體的 sid 拼法）
失敗場景：整套跑 `r1`，有情境 player，會建出 `.lumos/artifacts/android/r1.player/stability.json`。之後用 run-id `r1.player` 整套跑：preflight 只看那個目錄有沒有 steps.json，沒有，就放行。等 stability 段本身那次收集（sid=`r1.player`）跑到時，收集腳本看到已有結果檔，die 回 2，這一塊判成沒判完。前面的建置、UI 都白跑了，總表的證據目錄也跟上一次的情境資料混在一起。不會誤判成通過。
歸因：未判定（讀程式判定，沒有實跑）。
引句:「sid = run_id if scn is None else f"{run_id}.{scn}"」

### pitfalls manifest 判定
- 「寫總表那段的 open( 有沒有 with 或確定 close」：誤報。`_e2e_history_append` 走 `_local_ledger_append`，用 os.open 拿 fd，finally 裡 os.close；查帳尾的 `_ledger_tail_needs_newline` 也是 try/finally 關 fd；`_e2e_history_cmd` 讀總表走 `_canary_ledger_rows` 的 `with Path.open`，呼叫端會把整個生成器讀完。
- 併發類（鎖、交易）的題目在這個 repo 判範圍外，標誤報。ruff 舊帳不在這次改動的行，略過。

### 圖譜鏡頭
這次沒有附固定席節點（鏡頭計算超時，屬備援段），照派工詞不逐條答。

### 本案特定鏡頭（S22、S24、S27，以及整套 judge 的既有行為）
- 什麼時候寫進查證紀錄：程式要同時滿足六個條件才寫 feature_runs：steps.dirty 明確是 False、沒用替身收集腳本、判讀時工作目錄乾淨、HEAD 跟開跑時一樣、HEAD 的 e2e 段跟工作目錄的一樣、算得出指紋。跟 S27 一致，S22「不寫整套 runs」與 S24 拒寫也一致。例外是 F2 指出的兩條規則打架。
- 整套 judge 的既有行為沒被重構弄壞。實證：用同一支自建腳本（臨時 repo 加手寫 steps.json，呼叫 `lumos android-e2e judge`）兩版各跑一次。兩版 HEAD 用 rev-parse 確認過，修前 4b056532、修後 7988107c。結果：HEAD 換了回 2；髒樹回 2，並點名 app/src/A.kt；乾淨、同 HEAD 回 1（沒判完，有寫紀錄）；有 selection 卻沒帶 --no-record 回 2。兩版回傳碼完全相同，只有最後一條的訊息多了「重判要加 --no-record」。

### 角色卡
- be-api-compat：用具體輸入走過新舊互讀。
  - 舊紀錄沒有 feature_runs：新程式預設當成空物件，可讀。
  - 舊版 lumos 讀新紀錄：整份讀出再寫回，feature_runs 會保留；舊版沒有讀 runs 為 null 的地方（waive 還沒實作）。
  - 新模板配舊 lumos：舊版不認得 `select` 子指令和 `--history` 參數，回 2、不寫紀錄，往安全的方向壞。
  - 舊模板配新 lumos：steps 沒有 selection 和 dirty，走整套那條路；stability 步驟沒有 name，當成 stability 段本身，相容。
  - 跟 F1 無關的相容退步沒看到。不過 app_dirs、flows 裡原本收的 `//`、`/./` 寫法，這次起會被擋（G1 的用意）。
- be-authz：這次沒有網路端點，是單人本機的 CLI，授權題不適用。

### 三問
① 修復效果的行為證據（修前副本換上修後的測試檔，跟修後各跑一次）：
- G1：修前紅 4 條（反斜線回 0、萬用字元回 0、app_dirs 沒共用路徑規則回 0、run-id 叫 history.jsonl 會寫壞總表），修後全綠。保護組 config_strict 兩版都 56 過；features_config 在修前紅 1 條，但只是訊息措辭不同，回傳碼兩版都是 2，行為沒變。
- G2：程式沒改，兩版 `_e2e_keep_old` 逐字相同。修後新加的逐格表在修前就 15 過 0 紅，所以這是補了測試、不是修復，修復效果未判定。保護組 feature_record_trust 兩版都 5 過。
- G3：修前紅（替身收集腳本有設、這次沒收記憶體時也不寫紀錄），修後綠。保護組 full_scenarios_judged 兩版都 4 過。
- G4：修前 run_edges 中途丟例外（紀錄目錄那條），args_and_names 的 run-id 那條也紅，修後綠。保護組 history_edges 7 過、run_script 40 過，兩版相同。
- G5：修前 run_edges 在走到這一條之前就丟例外了，測試層面未判定。兩版模板 diff 證實修後多了 break；修後保護組 perf_per_method 兩版都 1 過。
- G6：`_e2e_scenarios_err` 的改動跟原寫法等價，修前的輪數上限那條沒紅，所以這是重構、不是修復，未判定。保護組 memstab_collect_scenario 兩版都 2 過。
- 修後跑 `-k android_e2e`：376 過 0 紅，6 分 29 秒。

② 修補處的正常、錯誤與相鄰路徑：
- 正常路徑與整套 judge 擋下的路徑都還成立，證據見上一段。
- 捷徑檢查翻得紅：只檢查紀錄檔本身是不是捷徑的改壞版，被 run_edges 抓到。
- 另外兩種改壞也翻紅：情境結果忽略工具問題，feature_record 紅 3 條；拿掉判讀時的乾淨檢查，紅 2 條。
- 相鄰路徑的缺口見 F3 與 F4。

③ 新發現在修前修後的結果：
- F1：修前修後同一個指紋，都失效。
- F2：兩版程式碼相同，都會矛盾，沒有實跑。
- F3：只在修後跑過改壞，修前未判定。
- F4：修前更糟（連各自的 break 都沒有），修後只修了一半。
- F5：沒有實跑，未判定。

未驗範圍：沒在真機跑模板；沒用 git 失敗、改名、主線前進這些情境實測 `--changed`；總表 `history --feature` 篩選時會不會把整套跑的行列進來，沒判。不給整體無回歸的保證。

臨時目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/鏡頭1-正確性-opus` 已經用字面絕對路徑刪掉。跑測試時翻紅留下的 9 份 gctl-run 現場也逐一用字面路徑刪了，只刪了本席建的那幾份。

總結一句：主要問題是記憶體情境放在指紋外面，改弱了舊的通過紀錄照樣算數；其餘是紀錄互相矛盾、一道檢查沒測試守著、逾時後還要等一輪，以及 run-id 撞名幾個小洞。
