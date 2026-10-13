severity: minor

併發與資源鏡頭的結論：沒有會擋合併的問題。八個以上的寫入指令同時跑，資料都在。鎖內沒有再開 lumos 子程序的路徑，持鎖時間也只有一處偏長。

先講我確認過的事。
- `grep sys.executable` 命中的位置，沒有一處落在被 `_vault_locked` 包住的入口。`cmd_decision_supersede` 的連鎖開單（`rel_cascade_create`、`cascade_surface`）和 `_drift_print_backrefs` 都在分派層、鎖已釋放之後才跑，不會卡 60 秒。
- `cmd_rel_cascade_write` 是先寫帳本，再呼叫有鎖的 `_append_decision_ref`。鎖拿不到時只印警告，不會死鎖。
- 我把全部 `atomic_write_verify` 的呼叫點按所屬函式列出。每一處不是自己裝飾了 `_vault_locked`，就是被某個 `with _vault_write_lock` 的呼叫者包著，沒有漏網。
- `decision-reindex --all` 在 600 個節點的庫上整段不到 1 秒，鎖內開銷不是問題。鎖內也沒有重建 Env 或印反向連結，那兩件事都在分派層、鎖外。

**Findings**

1. 鎖等不到時，`decision-amend`、`guard bind`、`guard audit` 會噴 Python 原始錯誤堆疊、結束碼 1，不是「擋下」加結束碼 2。
severity: minor
blocking: 否
引句:「        with _vault_write_lock(env.vault):」
- 原因：裝飾器在函式本體外拿鎖，`RuntimeError` 發生在函式內的 `try/except` 之外。
- 分派層也沒接住：`decision-amend` 只接 `ValueError`（`scripts/lumos:53002`），`guard bind` 和 `guard audit` 完全沒有 `try`（`scripts/lumos:52827`、`52830`）。
- `decision-add`、`decision-refs` 有接，所以只有這三個入口是堆疊。
- 筆記 `lumos-cli-write.md` 寫「鎖殘留時會等 60 秒才回『擋下』」，這三個入口與此不符。
- 最小重現：在 `HOME` 隔離的環境放一個假鎖檔（內容 `999999`），再跑 `lumos decision-amend Systems/A d1 --field content --text zz`，約 60 秒後出 `Traceback ... RuntimeError: 等了 60 秒還輪不到寫入`。
- 歸因：有證據的修復回歸。
- 兩版查證：
  - 修前 `c0265db0`，同樣的假鎖下 amend 與 guard bind 都 rc=0 寫成功，因為當時沒鎖。
  - 修後 `646dc3a8`，amend 和 guard bind 噴堆疊，decision-add 與 decision-refs add-ai 印「擋下」。

2. `decision-amend` 整段包在鎖內，包括 `git fetch --all`（`scripts/lumos:41595` 起），網路慢時會卡住所有其他寫入。
severity: minor
blocking: 否
引句:「def cmd_decision_amend(env, rel, did, field, text):」
- 重現：加一個遠端，用假的 `GIT_SSH_COMMAND`（睡 40 秒）讓 fetch 卡住，再同時跑 `question-add` 和 `set`。amend 持鎖 21 秒後回「git fetch 失敗」，另外兩個各等了 18 秒才寫成功。
- 影響：`fetch` 的逾時是 20 秒。同一把鎖也管治理帳的 append（`scripts/lumos:11818` 等處），所以 pre-commit 掛鉤寫帳會被連帶拖慢。
- 修法方向：fetch 不寫筆記庫，可以移到拿鎖之前。
- 歸因：有證據的修復回歸。修前 amend 沒鎖，同樣設定下 question-add 與 set 立即回（rc=0）。
- 筆記的「代價」那行只提了 60 秒殘留鎖，沒提持鎖時要跑網路。

3. `atomic_write_verify` 只檢查「有沒有任何一把鎖」，不檢查是不是這個檔案所屬筆記庫的鎖。
severity: minor
blocking: 否
引句:「+    if not any(_VAULT_LOCK_HELD.values()):」
- 重現：用 `importlib` 載入 `scripts/lumos`，先對 `Aempty` 目錄拿 `_vault_write_lock`，再對另一個目錄 `B/Systems/Z.md` 呼叫 `atomic_write_verify`，寫成功了，B 沒有被鎖。不拿任何鎖則照規定丟 `RuntimeError`。
- 實際影響：我沒找到會一邊持 A 的鎖、一邊寫 B 的指令，所以目前沒有實害。
- 這是「漏包的在測試裡就紅」這個保證的天花板：同程序內拿錯庫的鎖，守衛看不出來。
- 歸因：有證據的原有漏查（這是此規則一開始就有的設計限制）。
- 兩版查證：修前沒有這道檢查，所以修前寫 B 也不會擋。

另有一處觀察，我沒重現，不列為 finding。`cmd_dref_promote` 在鎖內仍用鎖外載入的 `env.notes` 判斷 `in_ai` 與 `in_main`。併發時依賴的是過時資料，但最後的 `_check` 要求正欄恰好 1 筆，所以會 fail-closed（寫入失敗），不會寫壞。

**三問**

1. 原問題的行為證據：在臨時副本同時跑 12 個 `decision-add`（含 6 個、多輪各 3 次）、2 個 `question-add`、2 個 `guard bind`、1 個 `decision-amend`，三輪結果都是決策 7 條（起始加 6 個新增，amend 另計）、問題 2 題、綁定 2 條、`d1` 被改成「改過」，沒有遺失。但修前 `c0265db0` 在同樣測試下也全數保住（該版本已有 decision-add 的鎖，競爭窗口很小），所以這個測試分辨不出新舊。「沒拿鎖就不寫」本身有直接證據：不拿鎖呼叫 `atomic_write_verify` 丟 `RuntimeError`。
2. 修補處的相鄰呼叫路徑：正常路徑（可重入、巢狀 `reindex --all`、連鎖開單在鎖外）成立。錯誤路徑中，鎖逾時的呈現對 decision-add 和 decision-refs 成立，對 amend、guard bind、guard audit 不成立（finding 1）。持鎖時間的相鄰路徑有 finding 2。
3. 新發現的案例在修前、修後：
   - 案例 1（假鎖）：修前 rc=0 寫成功，修後堆疊 rc=1。
   - 案例 2（慢 fetch）：修前不擋，修後其他寫入等 18 秒。
   - 案例 3（跨庫）：修前不檢查，修後仍放行。

**總結**：鎖規則本身站得住，資料在併發下保得住，沒有死鎖路徑。要處理的是 amend、guard bind、guard audit 逾時時的錯誤呈現，以及 amend 把網路抓取放在鎖內。

臨時目錄在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r3-併發資源-sonnet/`，repo 沒有改動。
