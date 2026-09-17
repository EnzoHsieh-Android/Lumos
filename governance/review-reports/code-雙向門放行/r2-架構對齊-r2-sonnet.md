severity: major

## F1 推送前反查「被改檔的家」又刻了一份既有的家對照表算法,不是同一份會漂

`_spec_gate_push_check` 為了找出「這次只改了程式檔、沒改筆記」時該查哪些計劃,自己寫了一段迴圈直接掃 `env.notes` 比對 `about_code`:

引句:「for srel, n in env.notes.items():
            if srel.startswith("Systems/") and any(nfc(str(x)) in code for x in as_list(n.fields.get("about_code"))):
                systems.add(srel[:-3] if srel.endswith(".md") else srel)」

但這批本身在 r1 已經確立的規矩是「計劃連到誰」只准有一份算法(`_plan_system_links`,docstring 寫死「★全檔唯一的『計劃連到誰』★……別再開第二支平行函式,兩套算法會各自漂」)。這批犯的是同一類錯誤的另一個座標:「檔屬於哪個家」這件事,repo 裡本來就已經有唯一算法,不是這批第一次要解的問題。

既有的唯一算法在 `_home_map_from_notes`,docstring 原話:

file: `scripts/lumos:20596`
引句:「★家對照表的唯一算法★(推筆記認家 [S1]):輸入 (節點名, type, status, about_code 清單) 的序列,」
引句:「兩套算法一定分岔,而分岔時沒有東西會翻紅。」

而且 repo 裡已經有專門給「已載入的圖譜、不開子行程、只求快」這個確切場景用的封裝:

file: `scripts/lumos:24099`
引句:「這支 hook 是 30 秒外層逾時的熱路徑),同一個圖譜一個行程只算一次。」

`_impact_home_map(env)` 就是拿 `env.notes` 餵 `_home_map_from_notes` 算出 `{檔: [家那幾篇]}`,行程內快取,正是 `_spec_gate_push_check` 這種「已經有 env,不想開子行程」的場景要用的入口(`_impact_mark_about`/`cmd_impact` 等既有呼叫端都是這樣用它,見 `scripts/lumos:24238`)。這批沒有呼叫它,自己在 push-check 裡重新寫了一段結構類似但不同的比對邏輯。

兩邊實際算法有落差,不是純粹重複貼一樣的碼:
1. `_home_map_from_notes` 只認 `typ == "system"` 且 `status in _NODEHOME_HOME_STATUSES`(過濾掉 stale/superseded 等狀態)才算「家」;這批的迴圈只看路徑前綴 `srel.startswith("Systems/")`,不檢查 `type`、也完全不看 `status`——一個標成 superseded 的 Systems 節點在 `_home_map_from_notes` 下不會被當成家,在這批的迴圈裡照樣被當成家,可能把已經作廢的節點反查回一份不該被觸發的計劃。
2. `_home_map_from_notes` 用 `_nodehome_key`(`nfc(_posix_norm(strip_quotes(...)))`)正規化再比對;這批只做 `nfc(str(x))`,沒有 `_posix_norm`、沒有 `strip_quotes`——`about_code` 裡如果寫了帶引號或路徑分隔符不同寫法的值,兩邊比對結果會不一樣。

這正是同一份 docstring 警告的「分岔時沒有東西會翻紅」的情境:兩邊都會綠,只是在邊界輸入(status 過濾、路徑正規化)上悄悄給出不同答案,而 r1 對 `_plan_all_links` 開刀的理由(「別再開第二支平行函式」)原封不動適用在這裡。

severity: major
blocking: yes

## 對照過的既有寫法(沒有發現以外的問題)

- `_regress_sources`/`_door_linked_signals`/push-check 的「誰連到誰」全部改走同一份 `_plan_system_links(note, text=None, systems_only=True)`,三個呼叫點都核對過:`_regress_sources` 沿用舊行為(不帶 text、systems_only=True),`_door_linked_signals`/push-check 用 `text=`+`systems_only=False` 擴權——這個「加選配參數擴既有函式、預設值保留舊行為」的形狀跟 `_contract_key_matches(text, with_kind=False)`(`scripts/lumos:25221`)一致,不是問題。
- `_clause_block_sha` 多加 `exclusions=None` 參數,呼叫端(`_spec_gate_record`、push-check 裡的重算)都同步傳了 `judged["exclusions"]`/`now["exclusions"]`,沒有漏傳導致指紋算不到已排除理由的分支。
- `_h2_section_lines(text, h2_re)` 抽出來給回退節與實務隱患節共用,取代各自維護一份找節迴圈,方向正確,没有引入第三套。
- pre-push 裡新增的 `sg_rc` 判斷跟同檔案原本 `cl_rc`/其餘段落一樣用「先設 0、呼叫失敗才蓋掉、之後判斷 -eq 1 才擋」的寫法,沒有另立一套 rc 慣例。
- `_auto_escape` 在 push-check 裡的呼叫方式(`env, stage, severity, desc, loops, sha, source=`)跟既有 `code-loop`/`CI` 兩處呼叫點參數順序、fail-open try/except 包法一致。
- argparse 的 `spec-gate` 子命令把 `node` 改成 `nargs="?"`,再手動擋「沒給 node 又沒給替代旗標」,跟同檔案 `t_lint`/`waive`/`cascade` 等既有「node 可省略」子命令的擋法(檢查替代旗標、缺了印訊息回 2)同款,不是新寫法。
- `_mk_spec_gate_repo`/新測試沿用既有 fixture 直接擴充 `table` 字典與 `test_x.py` 內容,沒有另開第二套 fixture 產生器。
