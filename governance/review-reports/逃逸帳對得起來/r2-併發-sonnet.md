severity: clean

已看,無:整份 r2 修訂稿逐節讀完,對照 `/Users/enzo/harness/lumos-toolchain` 的 `scripts/lumos` 現況,從資源與併發角度沒找到可以標成 blocker/major/minor 的新洞。逐項記錄查證過程:

- **r1 F1(鎖逾時裸拋例外)已折入且落地可行**:r2 第三節新增「上鎖」一條——「整段『讀帳確認目標→寫入』包在 `_vault_write_lock` 裡(手動記帳今天沒上鎖,這裡要明確加);拿不到鎖時照其他寫入指令一樣印『擋下:…』,不讓例外直接冒出來」,且 S4 條款把這句寫進可驗收條件(「拿不到寫入鎖時應印擋下訊息而不是拋出例外」)。查證:`scripts/lumos:13757-13803` 的 `_vault_write_lock` 逾時仍是 `raise RuntimeError(...)`(第 13791 行),沒變;但 `scripts/lumos:11110/11134/11186/...`、`31734-31761` 這些既有寫入指令已經有 `except (ValueError, RuntimeError) as e: print(f"擋下:{e}")` 這個現成、可直接照抄的模式,r2 這句話對實作者是可執行的指示,不是空話。

- **r1 F2(rule-gap 沒有 env、字面上做不到)已折入且改法自洽**:r2 把原本「rule-gap 改成呼叫 `_escape_rows_for`」的做法整段換掉,改成「保留自己找檔的讀法(它要支援知識庫就在 repo 根的佈局,也排在找到知識庫之前跑);讀到的列套同一支『是不是被撤回』的判斷函式後再數」。查證:`scripts/lumos:20215-20227` 的 `cmd_rule_gap(repo=None, as_json=False)` 現在就是靠 `_anchor_repo_root` 找 git 根、自己在兩個候選路徑(`docs/.escape-log.jsonl` / `.escape-log.jsonl`)裡挑檔讀,完全不碰 `env`/`Env(vault)`;`main()` 裡 `rule-gap` 分支(`scripts/lumos:31400-31401`)排在 `env = Env(vault)` 賦值之前執行,這正是 r1 抓到的落差。r2 的新寫法不再要求 rule-gap 建 env 或改 `_escape_rows_for` 簽名,只要求它在既有的逐行讀取迴圈裡(`scripts/lumos:20224-20231`,現有 `except Exception: continue` 對壞行已經寬容)多套一支共用的撤回判斷,這是同一次讀取、同一個記憶體內的 list 上做過濾,不涉及額外開檔或鎖,沒有新的併發風險。

- **`--withdraw` 本身的 TOCTOU 疑慮已用鎖排除**:「兩個會談同時撤回同一筆」在 r1 的併發席報告裡原本論證「append-only+讀側集合式判斷天然避開資料損壞」,但沒鎖時仍可能兩邊都判斷「還沒被撤」而各自寫入一筆撤回紀錄(不影響資料完整性,但語意上重複)。r2 明確把「讀帳確認目標→寫入」整段包進同一把 `_vault_write_lock`(與 `_auto_escape` 共用同一把,`scripts/lumos:9338` 現況可對照),第二個請求進鎖時會讀到第一個已寫入的撤回紀錄、判定「已經被撤過」而擋下——r2 實務隱患段落也明寫了這個結論,查證後與程式碼機制相符。

- **自動記去重「撤回過的仍算已記過」不會造成鎖序問題**:`include_withdrawn=True` 只是給 `_escape_rows_for` 多一個布林參數、改變回傳的 list 內容,呼叫端(`_auto_escape`)本來就已經在 `with _vault_write_lock(env.vault):` 區塊裡呼叫這支純讀函式(`scripts/lumos:9338-9344`),多一個參數不影響鎖的取得或釋放時機,也不會讓同一把鎖被巢狀請求兩次以上不同的鍵(`_vault_write_lock` 只認一個 vault 路徑,`--withdraw`、手動記帳、自動記帳三條路徑都只對同一個 `env.vault` 上鎖,不存在鎖序交錯的多鎖情境)。

- **escape-stats 讀大帳的耗時**:唯讀指令,不上鎖,讀 `.escape-log.jsonl`(25 列)、`.canary-log.jsonl`(約 1.7MB)、`.governance-log.jsonl`(約 13MB)與計劃筆記;r1 已實測 `cmd_gov`(`scripts/lumos:6871-6904`)用同樣「整檔讀進記憶體」寫法讀同一份治理帳約 0.2 秒,r2 在這支之外新增的只是多讀 `_loop_anchor_tier`/`_plan_for_loop` 這類既有函式,量級沒變,沒有新的效能或鎖風險。

- **手動記帳路徑(`lumos loop escape <id> ...`,非 `--auto`、非 `--list`)本來就沒有上鎖**:查證 `scripts/lumos:9476-9539`,這條路徑今天就是直接呼叫 `_jsonl_append_verified` 寫入,沒有 `_vault_write_lock`。r2 沒有把這條路徑也納入上鎖範圍(第三節「上鎖」那句話字面上只針對 `--withdraw` 新指令),這是既有現況的延續,不是 r2 新引入的落差;`--withdraw` 與手動記帳兩條路徑不會互相搶鎖,也就不構成鎖序(死鎖)問題——只是手動記帳仍然维持「無鎖並發寫入靠單次 `write()` 落在緩衝區內大致不交錯」這個既有假設,這假設在 r1 已被併發席看過且判定可接受(append-only、讀側對壞行寬容),r2 沒有讓它變得更差。

最嚴重 severity: clean;blocking 共 0 條。
