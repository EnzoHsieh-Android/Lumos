severity: major

1. 新增第三套主線候選枚舉,沒走既有兩套之一
severity: major
blocking: 是
引句:「cands = ["main@{upstream}", "master@{upstream}"]」
file: `scripts/lumos:50941-50966`(新函式 `_codeloop_default_base`)
- 這個函式自己列了一份主線候選:`main/master@{upstream}`、用 `for-each-ref refs/remotes` 掃出來的每個遠端 main/master,再加本機 main/master。專案裡早有兩套:
  - `_mainline_ref`(`scripts/lumos:47391`),要本機 main/master 時用 `remote_only=False`。
  - `_push_mainlines`(`scripts/lumos:47226`),候選是 `refs/remotes/<遠端>/HEAD`、`main@{upstream}`、`master@{upstream}`、`<遠端>/main`、`<遠端>/master`。
  - 新函式的候選跟兩套都對不上。它多了「掃整個 refs/remotes」和「本機 main/master」,少了遠端 HEAD、「跳過被推的那條」,也沒有 git 失敗時回 `_PUSH_START_UNKNOWN` 的處理。
- `_lens_push_base`(`scripts/lumos:47163`)和 `_push_range_start`(`scripts/lumos:47255`)的說明文字,都明講「兩套並存」,收斂路記在 Issues/推送前其他閘的範圍在合過主線時會多算。這份 diff 沒碰那兩段說明,現在實際是三套並存,而且沒有紀錄寫收斂路。
- 專案有過前例:`_ns_mainline_refs`(`scripts/lumos:32098`)的說明寫著「代碼審 r2 架構對齊席:原本另寫一套找主線」,後來改成沿用 `_mainline_ref`。這次是同一類問題。
- 新函式的說明講「推送閘的起點早就因同一個理由改成全部候選一起算」,但推送閘的候選枚舉(`_push_mainlines`)和 merge-base 算法(`_push_range_start` 內部)新函式都沒重用,只重用了最後一步 `_push_pick_base`。知識筆記寫「重用同一支挑法」,說的只是這一步,不是整套。
- 建議:
  - 候選枚舉抽成 `_push_mainlines`(或 `_mainline_ref`)與新函式共用的一處,新函式只多加本機 main/master 這一差異。
  - 或直接呼叫 `_push_range_start(root, 全零, head, remote, None)`。
  - 不然就在兩處「並存」說明與 Issues 筆記補上第三套與收斂路。

2. loop next 人數:有重用名冊來源,但還留著第二條路
severity: minor
blocking: 否
引句:「width = sum(1 for _s in _roster0["seats"] if _s.get("occupies_w") and _s.get("requirement") != "conditional") or width」
file: `scripts/lumos:15382-15384`(`cmd_loop_next`)
- 好的一面:名冊來源直接用既有的 `_roster_next_payload`(`scripts/lumos:13520`),沒有另寫一份查表。專案裡數 `occupies_w` 的地方只有 `scripts/lumos:15581` 的顯示,沒有現成的計數函式,所以這裡內嵌 sum 不算第二種做法。
- 殘留兩點:
  - 上面 `width, cap = _TIER_PARAMS[eff_tier]` 和 `if seq: width = 1` 還在。尾端的 `or width` 讓名冊算出 0 或名冊為空時,又落回 `_TIER_PARAMS`。這跟新 WHY 筆記寫的「不再另查 _TIER_PARAMS」不一致,筆記言過其實。
  - 同一支函式裡 `_roster_next_payload(loop_id, eff_tier)` 在 15382 和 `emit` 內(`scripts/lumos:15402`)各呼叫一次,名冊拿兩次。
- 建議:算好名冊後共用,或在筆記補一句「名冊為空時才退回 `_TIER_PARAMS`」。

3. ⚠ 手冊新增段落放的位置
severity: minor
blocking: 否
引句:「**首輪派審前先自己變異**:新功能第一次凍結材料之前,編排者對這次新寫的判斷函式逐條分支在複本上改壞一處」
file: `skills/lumos-code-loop/SKILL.md:40`(插在第 5 步「修與釘」內)
- 格式上跟同層的 `**修正關卡**`(粗體開頭、3 格縮排)一致,沒問題。
- 內容是「第一次凍結材料之前」的派審前動作,放在「修與釘」(審後修補)裡,時序對不上。這一步比較像第 1、2 步(派審)之前的準備。
- 這段跟本 diff 的功能(預設起點、名冊人數)無關,是搭便車的流程規則。
- 判不準它在 skill 結構裡該放哪,所以標 ⚠,不算 major。

總結:最高等級 major,blocking 共 1 條

我只讀了 patch 和 `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-small` 裡的 `scripts/lumos`,沒有改任何檔案,也沒有建實驗目錄,所以沒有東西要刪。
