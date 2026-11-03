severity: minor

邊界席第 3 輪報告:零個 major,三條 minor,沒有 blocking。我拿 fe97022(修後)和 6e10ae5(修前)各載成模組,在臨時 git repo 逐案走過。

1. SHA-256 的 repo 上,帳被忽略時整個判綠觀測失效,修前還能用
引句:「+    if head and ignored != "ignored":」
- 輸入與路徑:用 `git init --object-format=sha256` 建 repo,有 origin/main,在 featA 上有提交,帳被忽略且有一筆同分支的 spec-gate-green。修後 `_redbase_branch_rows` 一律走 `_gov_rows_delta(rr, _EMPTY_TREE_SHA, …)`(`scripts/lumos:14417`)。`_EMPTY_TREE_SHA` 是 SHA-1 常數 `4b825dc6…`,在 SHA-256 repo 裡不是有效物件,所以回傳「讀不出起點那一版」。
- 後果:函式直接回 `[]`,判綠過的不存、上一份紅燈版去重兩道都沒作用。
- 這個限制本來就存在於 fork 為 None 的路徑(主線與分離 HEAD)。但修前帳被忽略時還會用 fork 當起點,這條路在 SHA-256 repo 上是通的。修後把這條路也關掉了。
- 為什麼這算有意支援:`_LENS_SHA_RE`(`scripts/lumos:64711`)明列 64 位十六進位。
- 修法:帳被忽略時直接讀工作目錄那份(`_gov_rows_at(rr, None, …)`),不要經過起點版本。
- 兩版查證(同一份帳,同一個 repo):
  - `python3.14` 載入兩版後呼叫 `_redbase_branch_rows(base,"甲",ignored="ignored")`。
  - 修前回 1 筆、stderr 沒有訊息。修後回 0 筆,stderr 印「讀不出起點那一版的治理帳…」。
- 歸因:有證據的修復回歸。
- 重現:沒做成能當場翻紅的測試,只有上面的腳本證據,所以降為 minor。
severity: minor
- blocking: 否

2. 驗收條款 S8 寫「都印一句說明」,但有兩種情形程式什麼都不印
引句:「+- [S8] 當淺複製、部分複製、HEAD 解不出、過了截止時間或超過上限而判不了,或判不了治理帳有沒有被忽略時,過濾應把那幾筆紀錄照舊算進來並印一句說明」
- 這是修補把條款改寫成這樣(修前條款沒有「HEAD 解不出」與「判不了帳有沒有被忽略」)。
- 輸入:`ignored="unknown"`,或還沒有提交的 HEAD 加上沒有 ref 的舊判綠紀錄。
- 結果:兩種都把紀錄照舊算進來,但 stderr 為空。實測 `rows("unknown")` 的輸出是 `([...], '')`,unborn 的輸出是 `([(None,'cdcd')], '')`。
- 原因:`unknown` 時 `ignored == "ignored"` 不成立,不進 `_redbase_on_branch`。HEAD 解不出屬於 b 項(`ok = bool(head) and …`),不計入 `unsure`。這跟做法 e 的「b 以外才計入」一致,所以錯的是條款字面。
- 具體壞處:`git check-ignore` 失敗(例如 docs 是符號連結時回 128)時,過濾靜默退回舊行為,也就是計劃要修的跨分支漏洞,使用者看不到任何提示。
- 測試沒釘住:`t_redbase_branch_rows_fallback_keeps` 對這兩案只驗 `shas`,沒驗輸出。
- 修法:二選一。條款改回實際行為,或 `_redbase_attach` 在 `st == "unknown"` 時印一句。
- 歸因:有證據的修復回歸,指條款文字,程式沒變。
- 重現:`python3.14` 載入 fe97022 的 `scripts/lumos`,以 `pr.py` 腳本實測,修前條款沒有這兩項。
severity: minor
- blocking: 否

3. `_git_partial_clone` 的解析有幾處與 git 實際判定不一致,其中一處修後仍連遠端
引句:「+        if key.endswith(".promisor") and val not in ("true", "yes", "on", "1"):」
- 沒寫等號的 `[remote "origin"] promisor`:
  - `git config --get-regexp` 只印 `remote.origin.promisor`,沒有值。解析把它當 false。
  - git 其實把它當 true,實測 `cat-file -e <不存在的提交>` 仍去連遠端。
  - 我建了乾淨的 repo,遠端抓取腳本會留記號。對 `_redbase_branch_rows(…, ignored="ignored")` 修前與修後都留下記號,沒擋到。
  - 這個 repo 的設定要靠手寫才會有,`git clone --filter` 不會寫成這樣。副作用是 git 第一次連遠端後會自己補上 `partialclonefilter`,之後就認得了。
- `promisor = 2`:git 的布林解析視為 true,白名單沒有 `"2"`,同樣漏判。
- 遠端名含空白:輸出是 `remote.my remote.promisor false`,`partition(" ")` 切出的 key 是 `remote.my`,`endswith(".promisor")` 不成立,落到 `if val:` 回 True。這會把 `promisor = false` 誤判成部分複製。方向偏保守,只是白白關掉過濾。
- 測試缺口:我拿掉 `.promisor` 值檢查整段後,`-k redbase_branch_rows_fallback`、`-k drift_born`、`-k spec_gate_redbase_green` 全綠(19、26、13 條)。也就是 `promisor=false` 這條判斷沒有案例守。
- 修法:`.promisor` 只要出現就回 True(判不了照留本來就是安全方向),或對每個 key 用 `git config --type=bool` 重問。
- 歸因:有證據的原有漏查,修補把三個鍵都收進來,但值的解析仍漏。修前只看 `extensions.partialClone`,對沒寫等號的 promisor 一樣漏。
severity: minor
- blocking: 否

## 回答三問

1. 原問題的修復效果,行為證據(對修後版本逐項改壞):
   - 把 `_GIT_PARTIAL_KEYS` 改成只看 `extensions.partialclone`,「只寫 promisor 的部分複製」那案紅,git 確實去連遠端。
   - 把 `if head and ignored != "ignored"` 改回 `if head`,「帳被忽略:不算分岔點」那案紅,`forks == 1`。
   - 分支名改回 `symbolic-ref --short`,有同名 tag 的 S2 案紅。
   - 把 `_TitleIndex._join` 的快取拿掉,`t_name_collision_scales` 的②紅(515 個不同物件);改成完全不存回 `_joined` 也紅(513 個)。`id()` 重用沒有造成假綠。
   - 修後 `-k spec_gate_redbase_green` 與 `-k redbase_branch_rows_fallback` 共 13 + 19 條全綠。
2. 修補處的正常、錯誤與相鄰路徑:
   - 分離 HEAD、還沒有提交的 HEAD、同名 tag、斜線與中文分支名、淺複製、部分複製、過了截止時間、超過上限,都按計劃判。
   - 分支名在寫入與讀取走同一函式,一致。NFD 與控制字元清洗兩端相同,只可能把「只差零寬字元」的兩個分支名併成一個,偏保守。
   - `_drift_born_env_err` 改用共用函式後,rc 與 None 的處理跟修前同方向。
   - 在 30 萬筆判綠紀錄、帳被忽略的壓力下,截止時間 10 秒有生效(實測 10.0 秒),記憶體約 680MB。這個記憶體用量屬於原有的整本帳讀入,不是這次新增。
   - 相鄰路徑出問題的是上面第 1 條(SHA-256)。
3. 新發現案例在修前、修後各是什麼:
   - SHA-256 + 帳被忽略 + 同分支判綠:修前 1 筆,修後 0 筆加訊息。
   - 沒寫等號的 promisor:修前修後都連遠端。
   - `ignored="unknown"` 與還沒有提交的 HEAD:修前修後都靜默照留,只有條款字面是修補新增的。

## 已驗與未驗

已驗:
- 上面所有行為。
- `ref` 欄位沒有其他讀者會誤讀:`scripts/lumos` 裡讀 `d.get("ref")` 的地方只有 `:14464`(本函式)與 `:24572`(簽核帳)。
- `_TG_LIMITS` 與 `test-quality-standard.md` 新增的句子逐字相同。

圖譜鏡頭:
- 測試假綠形態的 INVARIANT(還原翻紅釘要配前置斷言)。這次新增的案例大多有 ★前置★;分離 HEAD 與還沒有提交的 HEAD 兩案沒有明寫前置,但 `--orphan` 或 `--detach` 失敗時結果會不符預期,等於自帶前置。
- 設計審第五步:S1 到 S9 都綁了存在的測試。
- 其餘 Systems 節點不涉及。

未驗:
- Windows,因為沒有環境。
- CI 上遠端抓取腳本的 `sh` 在 noexec 的暫存區跑不起來時,★前置★ 會誤紅。我沒有驗證新版 git 對 `cat-file -e` 是否仍自動抓取,但失敗時前置會明確紅,不會假綠。
- 真實的 blobless 與 treeless 遠端複製。
- 時鐘倒退。
- 大 repo 沒有 commit-graph。

最嚴重等級是 minor,blocking 共 0 條。

相關檔案:
- `/Users/enzo/harness/lumos-green-scope/scripts/lumos`
- `/Users/enzo/harness/lumos-green-scope/scripts/test_lumos.py`

暫存目錄在 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/邊界-sonnet/`(約 22MB,由編排者收貨後刪)。我另外刪了自己留下的一份 `gctl-run-` 現場。
