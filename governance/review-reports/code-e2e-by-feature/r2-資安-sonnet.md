severity: minor

## S1 效能測試方法名的白名單放寬到 `$`,sh 會展開變數
severity: minor
blocking: 否
- 歸因:有證據的修復回歸。修前正則 `[A-Za-z0-9_.#]+` 不收 `$`,修後 `E2E_BENCH_NAME_RE` 收 `$`。
- 攻擊路徑(推論):
  - 誰:打開外來專案的使用者或 AI。
  - 從哪:`.lumos/macrobench.json` 的 `features.*.cases.*.macrobench`。
  - 送什麼:名字如 `Cls$HOME`、`a$IFS.b`。
  - 拿到什麼:`sh -c` 把名字當變數展開,環境變數值會進測試指令的參數,`$IFS` 還能把一個參數切成兩個。
  - 為什麼只封頂在推論:同一份設定裡的 `macrobench_cmd` 本來就是任意 shell,攻擊者用不到這個洞也能執行任意指令,所以沒有多拿到東西。
- 兩版查證(我在 /tmp 臨時目錄,用 `git archive` 取出兩個提交的 scripts 後,對同一組名字比對正則並實際交給 `sh -c`):
  - 修前:`Cls$HOME`、`a$IFS.b` 都被拒絕(old_ok=False)。
  - 修後:兩者通過,`printf '[%s]\n' Cls$HOME` 輸出 `[Cls/Users/enzo]`,`a$IFS.b` 被切成 `[a]` 和 `[.b]`。
  - 修前修後的 `#bad` 結果:修前通過,修後被擋。這個方向(開頭 `#` 被擋)是修對的。
- file: `scripts/lumos:40`(`E2E_BENCH_NAME_RE` 定義處,修後版本);範本腳本 `scripts/templates/android-e2e-run.sh` 有同一條正則。
引句:「E2E_BENCH_NAME_RE = re.compile(r"[A-Za-z0-9_.$][A-Za-z0-9_.$#]*")   # 效能測試方法名:會換進 macrobench_cmd 交給 sh,開頭不准 #(sh 當註解);範本腳本同一條」

## S2 `LUMOS_E2E_COLLECT` 環境變數能整支換掉記憶體收集腳本
severity: minor
blocking: 否
- 歸因:有證據的修復回歸(新引入)。修前 `android-e2e-run.sh` 寫死 `os.path.join(here, "android-stability-collect.sh")`,`grep LUMOS_E2E_COLLECT` 在修前範本腳本是 0 筆。修後多了 `COLLECT = os.environ.get(...)`。
- 攻擊路徑:
  - 誰:使用者本人,或照常操作的 AI。
  - 從哪:shell 裡殘留的 `LUMOS_E2E_COLLECT`,例如測試時 export 過沒清,或 direnv 之類帶進來。
  - 送什麼:平常的整套驗收指令。
  - 拿到什麼:記憶體這一塊改跑別的腳本,它產出的 `stability.json` 被當成真的,整套結果可能被記成 pass 並寫進查證紀錄,沒有任何提示。
- 限制:我沒有跑真機,只讀了程式。這條是靜態確認,修前修後的行為差異只有程式碼層級的證據。同一支腳本裡的 `LUMOS_E2E_LOCK_DIR` 等測試用開關是舊有同類。
- file: `scripts/templates/android-e2e-run.sh:51`、`scripts/templates/android-e2e-run.sh:471`
引句:「COLLECT = os.environ.get("LUMOS_E2E_COLLECT") or os.path.join(here, "android-stability-collect.sh")」

## S3 殘留的 `LUMOS_STABILITY_SCENARIO` 會讓整套跑的 stability 段改用某個情境
severity: minor
blocking: 否
- 歸因:有證據的原有漏查。修前修後的行為相同,不是修復造成的。
- 攻擊路徑:
  - 誰:使用者本人。
  - 從哪:shell 裡殘留 `export LUMOS_STABILITY_SCENARIO=fast`。
  - 送什麼:整套驗收(`senv = env` 是整份 `os.environ`)。
  - 拿到什麼:`scn is None` 那一步本應用 stability 段本身,收集腳本卻改用 `fast` 的 scenario 與 driver,結果仍當成 stability 段的 pass 記錄。修後整套還多跑每個情境,殘留變數會讓同一個情境被跑兩次,而且 None 那一份名稱對不上。
- 兩版查證:我把 `android-stability-collect.sh` 的 `load_config` 抽出來,對同一份設定分別在兩版執行。
  - 修前、修後的結果一致。
  - 變數為空字串時,`scenario` 是 `full`,`driver` 是 `echo FULL`。
  - 變數設為 `fast` 時,`scenario` 是 `fast`,`driver` 是 `echo FAST`。
- 修法方向:整套跑的 `env` 要先拿掉這個變數。
- file: `scripts/templates/android-e2e-run.sh:470`、`scripts/templates/android-stability-collect.sh:124`
引句:「senv = env if scn is None else dict(env, LUMOS_STABILITY_SCENARIO=scn)」

## 三類各一段「已看」
- ①提示注入:已看,無。本次新增的自由文字(情境名、功能名、方法名)都有正則限制。情境名只收 `[A-Za-z0-9_-]+`。`blocked` 原因文字只進本機總表的 JSON 行,不進派工詞或 hook 附加段。
- ②讀寫與執行越界:
  - 記憶體情境名拼進 run-id 與產物路徑:已看。情境名與 run-id 兩邊都有正則,不能帶 `/` 或 `..`,裝置端路徑也有第二道檢查。
  - `features.paths`:只用來做路徑比對,沒有檔案讀寫,也擋了絕對路徑與 `..`。
  - `stability_scenarios` 的 `driver` 是 `sh -c`,但來源跟既有 `stability.driver` 同一份設定檔,信任面沒有變大。修後加了欄位白名單與 cycles 上限。
  - 按功能跑的紀錄寫入點是 `<指紋>.json`,指紋是雜湊,路徑安全。
  - 唯一的新增面是 S1 的 `$`。
- ③非刻意一步繞過:
  - 按功能跑寫進查證紀錄的條件已看。修後要同時滿足三件事才寫:開跑時工作目錄乾淨(`steps.dirty`)、現在也乾淨、HEAD 沒換。這比修前嚴。
  - 同一版已有完整結果時,不完整的結果不會蓋掉它。
  - 沒有任何會判的項目時不再記成通過。
  - 目前沒有任何地方在讀 `feature_runs` 來放行推送。我 grep 整份 `scripts/lumos` 只找到寫入端和格式檢查,所以「沒驗完整的版本被記成驗過」暫時沒有消費者可被騙。這條屬未驗範圍,等下一批接上推送前檢查時要再看。
  - 發現 S2 和 S3。

## 針對三問
1. 原問題修復效果的行為證據:我沒有跑完整測試集,也沒有載入修前版本跑那七支新測試。我只確認了兩件事,都有修前修後對照。
   - `#` 開頭的方法名:修前通過,修後被擋(已驗)。
   - 髒樹開跑不寫 `feature_runs`:靜態讀碼確認,修前沒有 `steps.dirty` 這一條。
   - 其餘修復的行為證據未判定,原因是這是資安席,沒跑一般測試。
2. 修補處相鄰路徑:
   - 整套跑現在多跑每個情境,`_e2e_stab_by_name` 以 `name` 過濾步驟,無名那份不會混進有名的。靜態確認成立。
   - 修前修後都有 S3 的環境殘留問題,見上。
3. 新發現同一案例的修前修後:
   - S1:修前拒絕,修後放行(有實測)。
   - S2:修前沒這個開關,修後有(grep 對照,未實跑)。
   - S3:修前修後相同(有實測)。

我沒有碰 e2e-docs repo。臨時目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/資安-sonnet` 已用字面絕對路徑刪除。

本輪修補沒有帶來可直接利用的洞,只有一處把效能方法名白名單放寬到 `$`、一處新增的收集腳本環境變數覆蓋,另有一處修前就有的環境殘留風險。
