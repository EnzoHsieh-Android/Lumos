severity: minor

回滾鏡頭,凍結審材 r1-snapshot.md 全文已讀。寫入入口逐一對過 `scripts/lumos`,也查了示範專案 order-web 與它的複本 order-web-impl 的實際帳。我沒建任何臨時檔,也沒動任何 repo。

## 寫入入口清單

| 入口 | 新版寫什麼 | 退回舊工具讀不讀得懂 |
|---|---|---|
| 表態 marker 與治理帳 `kind=dispositions` | 題目 id 變成 `react-*` | 讀得懂、不崩;但舊工具要求 `vue-*`,所以仍會擋(見 F1、F2) |
| 統計彙總(`lumos stats`) | 無新欄位 | `_dq.setdefault(_qid, …)` 把 id 當字典鍵,未知 id 照列,不崩 |
| `.lumos/config.json`(init 寫 `node-vitest` 與 vitest 指令、符號 profile) | 值是舊工具已認得的別名 | 讀得懂;但退回後證據樣式又沒了(見 F3) |
| `_RAN_EVIDENCE`、題目表、`_node_flavor_of` | 只在程式裡 | 不進帳,沒有相容問題 |
| 前端範本、react-idioms | 只是檔案 | 刪掉即可 |

## F1 在途分支的舊表態全部作廢,spec 沒有對應的驗收條款與提示

- 對應段落:〈實務隱患〉守衛面第③點與〈驗收條款〉。
- 引句:「在途分支會重新表態(SOP 第 2 步記過的代價),order-web 是唯一受影響的專案。」
- 問題:這裡只承認代價,沒定義怎麼重新表態,也沒有任何一條 S 驗收條款覆蓋。
- 具體例:
  - order-web 與 order-web-impl 的 `feat/order-page` 各有 4 筆表態,全是 `vue-parallel`、`vue-lcp`、`vue-bundle`、`vue-watch`、`vue-reactive`、`vue-extcode` 六題。
  - 它們的留痕座標是 3b31b14,和現在的 HEAD(55719bf)只差簿記檔,所以仍有效(`_codeloop_record_valid_ex` 的豁免)。
  - 工具升級後,`_dispositions_verdict` 只走新的 `stack_questions_meta`,對每個適用的 `react-*` 做 `disp.get(qid)`,得到 None 就回「`react-effect 缺表態`」。舊紀錄仍有效,卻一題也算不上。
  - `_dispositions_template(carry=True)` 只帶 `old.get(qid)`,id 完全相同才帶,所以 `--carry` 一題都帶不過來。
  - 最像的 `vue-extcode` 與新的 `react-extcode` 是同一個問題、同一份 FACT 證據,也要整題重答。
  - 輸出只有一排「缺表態」,看不出是題組換了、舊答案在帳裡還在。
  - 合併進主線時也一樣:`_disp_record_for` 認合進來那側的舊表態,同樣被判缺。
- 照 spec 實作會得到:能運作,但接手的人會以為是帳壞了。
- 建議補一條條款:舊紀錄只含 `vue-*` 而這次適用的是 `react-*` 時,擋下訊息要講明「題組已換、舊 id 不帶過」,並釘一支測試。
- 佐證:`scripts/lumos` 的 `_one` 裡 `if ent is None: return f"{qid} 缺表態"`,以及 `_dispositions_template` 的 `old.get(qid)`。
severity: minor
- blocking: 否(決策已認這個代價,缺的是提示與測試,實作者不會因此做出壞系統)

## F2 〈回退〉說「不碰任何帳本」,但表態帳在退回後會反向失效

- 對應段落:〈回退〉。
- 引句:「已經用了 vitest 骨架的消費專案設定不會被改回,它的 `node-vitest` 仍是合法 profile 名。不碰任何帳本。」
- 問題:
  - 上線後 order-web 重新表態,帳裡就有 `react-*` 的紀錄。
  - `git revert` 之後,舊工具的題表只有 `vue-*`,每題都判「缺表態」。
  - `--carry` 只帶 id 相同的,帶不回來,同一分支要第三次重答。
  - 若有人把 `react-*` 的 JSON 拿去給舊工具寫,`_dispositions_validate` 會回「不是題目表裡的 id」。
  - 〈RETIRE-IF〉撤 react 分支時走同一條路,同樣會讓當時在途的分支重表態。
- 具體例:退回後,order-web 的 pre-push 因表態閘擋下,要先重答一遍才能推。
- 帳的可讀性沒有問題,只是「不碰帳本」這句不精確。〈回退〉要補一句:退回後帶 `react-*` 表態的在途分支要照 `--dispositions-template` 重表態。
severity: minor
- blocking: 否(只是少交代一次重答,不會做出壞系統)

## F3 〈回退〉漏講退回後的證據樣式

- 對應段落:〈回退〉。
- 引句:「跑過證據樣式回到 jest 那條。」
- 問題:
  - init 寫了 `node-vitest` 的專案,退回後 `_RAN_EVIDENCE.get("node-vitest")` 為 None,合約測試閘改走 `_bound_tests_filter_probe`。
  - 〈現況〉附錄已實測:vitest 對不存在的測試名也回 0。
  - 所以該探針判「不可信」,結果快取 14 天,每次推送都被 `unfilterable` 擋下。
  - order-web 設定寫 `node-jest` 的,退回後也回到 `Tests:` 冒號樣式對不上 vitest 摘要的老問題。
- 這就是 F1 要修的那個 bug,退回等於把它放回來。〈回退〉現在只說 profile 名合法,沒說合約測試閘會再擋。
- 建議把這句寫進〈回退〉,讓退回的人知道要同時退或暫關綁定測試閘。
severity: minor
- blocking: 否

## F4 撤除條件在帳上量不到,「退回」那條路不會自己觸發

- 對應段落:〈RETIRE-IF〉。
- 引句:「order-web 在帳上的推送裡 react 題組沒有任何一題被答成「適用並改了程式」」
- 問題:
  - 表態帳每題只有 `satisfied`、`na`、`todo`、`tension` 四值,外加 `carried` 與 `backing`。
  - 沒有「改了程式」這個欄位,`lumos stats` 的彙總也算不出來。
  - 到 2027-04-15 人裁時,這句只能靠人讀卷證判斷,沒有機械數字。
- 具體例:到期日要裁撤時,查統計只看得到各題 `satisfied` 與 `na` 的次數。`satisfied` 是「做到了」,不等於「因此改了程式」,無法判定條件成立與否。
- 建議把條件改成帳上量得到的:例如「react 七題在 order-web 的人答全是 `na`」,即 `lumos stats` 的死題候選同一口徑。
severity: minor
- blocking: 否

## 已讀,無 finding

- 〈做法〉F1 的 `_RAN_EVIDENCE` 放寬、W7、F7、B10:不寫新帳欄位。B10 只讓適用題變少,舊紀錄多出的 `kt-compose` 等 id 在核對時被忽略(`_dispositions_verdict` 只走現行 meta),不會擋。
- 符號 profile 收 `.jsx`:只有放寬,舊工具最壞是把引用 `.jsx` 符號的筆記判成查無,影響極小,不另列。
- 風險類:
  - 守衛面:S5 和 S7 把放寬釘住,此鏡頭下無新增缺口。
  - 舊資料與舊帳相容:見 F1、F2。
  - 已在途分支:見 F1。
  - 與其他會談、其他計劃的交界:吸收《逾期回頭條件立案清單》第 10 節已寫明,無回滾問題。

最嚴重 severity:minor;blocking 共 0 條。

相關路徑:
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-react/scripts/lumos`
- `/Users/enzo/orca/workspaces/order-web/docs/.governance-log.jsonl`
- `/Users/enzo/orca/workspaces/order-web-impl/docs/.governance-log.jsonl`
