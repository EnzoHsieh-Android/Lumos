severity: major

## F1 新開了第二支「計劃連到哪些節點」的函式,沒有重用既有的 _plan_system_links

severity: major
blocking: yes

這批在 `scripts/lumos` 新增 `_plan_all_links`:

引句:「def _plan_all_links(note, text):
    \"\"\"計劃連到的所有節點(lands_in + related + 正文 [[連結]]),去重保序」

它的用途(門判定訊號 2、推送前判定「誰的落點被碰到」)在 patch 裡自己也講了理由:

引句:「也是條款指紋的輸入:留痕後被連結的節點補了合約或標籤,推送閘會判留痕過期、門要重判(r4 回滾席)。」

但這個專案原本就有一支職責幾乎一樣的函式 `_plan_system_links`(file: `scripts/lumos:5256`),文件字面就寫著「計劃連到的 Systems 節點(lands_in + related + DEP 行的 [[連結]])」,而且它的實作註解特別強調「別自己再刻一份剝括號」的紀律:

file: `scripts/lumos:5258`
```
# 字串/清單都收(代碼審 r1);[[…]]/別名/錨點/引號一律交給既有 link_target(代碼審 r2/r3:別自己再刻一份剝括號)
```

`_plan_system_links` 已經被 `_regress_sources`(file: `scripts/lumos:5236`)在用,兩支函式的差異只有二點:①正文連結的抓法(`_plan_system_links` 只認 `DEP:` 那一行的 `[[…]]`;`_plan_all_links` 用 `WIKILINK_RE.findall` 掃整份正文)②要不要過濾成只剩 `Systems/` 開頭。這兩點原本都可以用參數(例如 `scope="dep"|"body"`、`systems_only=True/False`)接在既有函式上,結果這批選擇另開一支平行函式,兩支往後各自維護「計劃連到誰」這件事,以後改連結解析邏輯(例如 alias/錨點的處理)要記得兩處一起改。

這正是題目點名要抓的「自己再刻一份已有的工具函式」——不是風格問題,是同一件事現在有兩套算法、且新的那套明確放寬了既有函式刻意收窄的範圍(只認 DEP 行 → 認全文任何 wikilink),卻沒有把這個放寬的決定寫在既有函式旁邊讓下一個人看到兩套邏輯在打架。

file: `scripts/lumos:5256`(既有)
file: `scripts/lumos:4858-4869`(新開,凍結 patch 內對應段落見引句)

## F2 其餘走查:沒有發現第二種寫法

severity: clean
(僅此段落內的其餘部分)
blocking: no

對照過的既有慣例、確認這批有跟上:
- 審查帳寫入口:沒有另開寫檔函式,`_spec_gate_record` 跟 `_auto_escape`(file: `scripts/lumos:8435`)、`cmd_canary`(file: `scripts/lumos:7104`)、`_ci_write`(file: `scripts/lumos:23106`)一樣,自己組 `rec = {...}` 字典後直接呼叫 `_vault_write_lock` + `_jsonl_append_verified(path, rec, "token", rec["token"])`——這本來就是本專案「各帳本各自組欄位、共用同一支落盤原語」的既有寫法,不是又開一個新寫入口。
- `_rollback_section_chars` 被拆成共用的 `_h2_section_lines`,回退節與新的實務隱患節共用同一套找節邏輯,patch 自己也點名「找節邏輯不准長出第三套」——這是收斂寫法、不是分裂。
- `_run_bound_tests` 的呼叫慣例(`items` 用 `(node, plat, method, "real"/"dangling")` 四元組)在 `_spec_gate_push_check`(file: `scripts/lumos:5591` 附近)裡照抄既有 `_spec_gate_regress`/`_spec_gate_run_clauses` 的形狀,沒有另創格式。
- `_contract_key_matches(summ, with_kind=True)` 呼叫方式跟既有 `_contract_texts`/`cmd_contracts` 用法一致。
- `env.notes.get(lk + ".md") or env.notes.get(lk)` 這個解析連結目標的慣用語,`_door_linked_signals` 跟既有 `_regress_sources`(file: `scripts/lumos:5245`)寫法逐字一樣。
- pre-push 裡 `sg_rc=0; ... || sg_rc=$?; if [[ "$sg_rc" -eq 1 ]]; then ... exit 1; fi` 的錯誤碼處理,跟同檔緊鄰的 `nh_rc`(home check)那段(file: `scripts/hooks/pre-push:186-197`)是同一個寫法,新段落沒有另開一套 rc 慣例。
- argparse:`spec-gate` 的 `node` 改成 `nargs="?"`、靠子旗標(`--push-check`/`--door-rule`)決定要不要吃 node,再在 dispatch 那段手動擋「兩者都沒給」——這跟既有 `dispatch-lens`(file: `scripts/lumos:29220`,`lens_range` 可省略、靠 `--claim/--disarm/--status` 決定)是同一種「node 可省略」慣例,不是新形狀。
- 測試 fixture:`_sg_plan2`/`_sg_commit`/`_sg_records` 都是在既有 `_mk_spec_gate_repo` 之上疊,沒有另起一套 fixture 系統。

沒有找到跨層直呼、繞過既有寫入口、或跟同層對照檔慣例相反的地方。
