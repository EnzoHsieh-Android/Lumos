severity: major

## F1 「只在過關時寫治理帳」低估了實際副作用——每一輪 loop next 都會多寫檔
severity: major
blocking: 是——照這句字面理解,實作者不會替「每輪都寫檔」的新增負載做任何評估或設限,寫出來的東西跟計劃自己講的行為不一致。
引句:「在過關時寫治理帳(這是處置閘既有行為,不是新增)」
file: `scripts/lumos:18488-18502` `_roster_tail()`:`if roster or str(rid).startswith("__"): return`,否則呼叫 `_roster_observe` 並在有異常時把結果 append 進 `governance/review-reports/<loop_id>/roster-alerts.log`——這段掛在 `if not readonly:` 分支(`scripts/lumos:18534-18538`),**不分過不過關,每次呼叫 `_loop_status_disposal` 都會跑**;`_severity_tail()`(`scripts/lumos:18506-18533`)同一份檔案也是同樣「非 readonly 就跑」。
file: `scripts/lumos:9629-9630` `cmd_loop_status` 的 `disposal=True` 分支呼叫 `_loop_status_disposal(...)` 時沒有傳 `readonly`(預設 `False`),所以透過 `loop next` 問處置閘,一樣會落進上面兩段寫檔邏輯。
file: `scripts/lumos:8284-8289` 現況:2026-08-26 之後開的迴圈今天呼叫 `loop next`(帶 --spec)會在 `_panel_retired_for` 直接 `return 2`,**根本不會走到任何寫檔邏輯**(`r1-intake.md` 已實測重現)。本次修出口之後,同一個 loop next 呼叫會改成每輪都問 `--disposal`,於是「每輪」都會執行到 `_roster_tail`/`_severity_tail`,寫檔頻率從 0 變成「每次呼叫 loop next 都可能寫一行」——不是只有「跑滿上限」或「過關」那個時間點,普通的第 1、2、3 輪照樣會寫。
敘述:計劃「實務隱患→併發」那句只講「在過關時寫治理帳」,把寫檔動作限定在收斂那一刻;但程式碼裡真正會被觸發的寫檔路徑(`roster-alerts.log`)是掛在「非 readonly 呼叫」這個粗得多的條件上,跟過不過關無關,也跟本計劃要不要印 cap_report 無關——這是處置閘本來就有的行為,但本計劃第一次讓 `loop next` 的每輪呼叫都摸到它。少寫這句會讓做這份實作的人以為「只有 cap-reached/converged 那一次才有寫入副作用」,因而不會去想「同一個審查編號同時被兩個會談各自敲 loop next」時,兩邊各自觸發一次 `_roster_observe`+append `roster-alerts.log` 是不是要處理(append 單行本身在本機檔案系統上安全,但寫入頻率與內容本計劃完全沒提及、也沒排進「已排除」清單)。

## F2 S9 要 `loop status --disposal` 自己判「輪數已達上限」,但 `_loop_status_disposal` 現在完全不算 tier/cap
severity: major
blocking: 是——字面實作 S9 時,`_loop_status_disposal` 函式裡沒有任何管道知道「上限是幾輪」,不補邏輯就只能不印(S9 沒做到),補邏輯又沒有計劃描述要用哪個既有函式、哪個參數來源,兩個人接這份計劃會做出不同東西。
引句:「輪數已達上限、或觸發熔斷時,在判定之後印同一段」
file: `scripts/lumos:18265` `_loop_status_disposal(rounds, loop_id, spec, n_badlines=0, root=None, bad_linenos=None, env=None, roster=False, repo=None, readonly=False, spec_sha_override=None, result_out=None)`——整支函式(18265–18585 行)裡沒有出現 `tier`、`cap`、`_TIER_PARAMS`、`_loop_anchor_tier` 任一個字(已用 `awk 'NR==18265,NR==18620'`+grep 核對,零命中)。「輪數已達上限」這個判斷目前只存在 `cmd_loop_next` 內部(`scripts/lumos:10398,10416-10417,10676`),靠 `eff_tier = anchor or tier` 與 `_TIER_PARAMS[eff_tier]` 算出 `cap`,而 `eff_tier` 的來源之一是呼叫端傳入的 `--tier`。
file: `scripts/lumos:30771` `ls.add_argument("--disposal", ...)`——`loop status` 子指令的參數清單裡沒有 `--tier`(只有 `loop next` 的 `ln` 在 30804 行才有 `--tier`),所以直接下 `lumos loop status <id> --disposal --spec ... --repo ...`(計劃本身在「二、跑滿時印什麼」與「四、印在哪裡」都預設這條指令可用)時,沒有任何顯式輸入能告訴 `_loop_status_disposal` 這個編號的分級是 standard 還是 high。
敘述:計劃「做法」一/二/三節只描述 `loop next` 怎麼算 cap_report(它本來就有 `eff_tier`/`cap`/`rounds_count` 這些變數),「四、印在哪裡」卻直接假設 `loop status --disposal` 也能印同一段,沒有交代它要怎麼取得 tier/cap——`_loop_anchor_tier(rounds)` 技術上可行(讀 `rounds` 裡第一筆帶 `tier` 的記錄,`scripts/lumos:17905-17908`),但這是要新加進 `_loop_status_disposal` 的邏輯,計劃連一句「復用 `_loop_anchor_tier` 算 cap」都沒寫在「做法」節裡(PRIOR-ART 只籠統提過這個函式名,沒有把它跟 S9 的實作路徑綁在一起)。若實作者只照「做法」一/二/三動手,S9 這條條款會直接漏做。

已看,無:計劃的「一、修出口」把判過不過關改問處置閘、S1/S2 的優先序(少了 --spec 排在跑滿前)這條裁定沒有被推翻,對照 `scripts/lumos:10632-10662` 現況一致,沒有破壞既有 gate-pending 行為;disposal gate 的 rc 語意(0=過/1=沒過/2=用法錯誤,見 `scripts/lumos:18556-18585`)跟 panel gate 一致,loop next 既有的 `if rc==2: return 2 / if rc==0: converged / else: cap 檢查` 這段(`scripts/lumos:10669-10680`)換掉 panel 呼叫成 disposal 呼叫不會破壞這三分支的邏輯;S8 熔斷用「同編號各輪折欄累計」這件事,`_loop_status_disposal` 拿到的 `rounds` 本來就是整個編號的全部記錄(不只當輪 latest),所以累計計算在技術上站得住(`scripts/lumos:9629` 呼叫時傳入完整 `rounds`);`gov --stats` 對 cap-reached/converged 是用 `by = {loop_id: set(kinds)}` 這種去重集合在算(`scripts/lumos:6756-6764`),兩個會談各自寫一筆同 kind 的治理帳記號不會讓統計重複計數,這條路徑本計劃不用額外處理併發去重;「已排除:守衛面」一句(S8、S9 綁測試,不改變過關判定與退出碼)跟程式碼裡 disposal/loop next 現有 rc 語意沒有衝突,判斷「不影響」成立。

最嚴重 severity: major;blocking 共 2 條。
