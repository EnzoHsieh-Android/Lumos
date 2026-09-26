severity: major

## F1 `cap_report.rounds[].disposed` 欄位完全沒有定義,實作者與寫測試的人各憑猜測
severity: major
blocking: 是——這個欄位在 S3 的 JSON 合約裡是必填(「`--json` 應有 cap_report 物件且欄位如第四節」),但第四節只給了欄位名沒給語意。實作者要嘛猜它是「這輪有沒有彙總帳(has_carrier)」、要嘛猜是「這輪本身有沒有過處置閘判定」、要嘛乾脆塞 `disposal_gate` 的 rc——三種猜法會讓 S3 的機械測試斷言各自不同,寫測試的人跟寫實作的人若各自猜,測試會綁死一種語意,之後任何人想改都得先考古猜測原意,而現在連猜的依據都沒有。
引句:「`rounds`(每輪 `{round, folded, max_severity, disposed}`)」
file: `scripts/lumos:7364`-`scripts/lumos:7385` — `_review_yield_round` 回傳的 dict 是 `{N, M, R, F, A, S, has_carrier}`,並沒有叫 `disposed` 的鍵,也沒有任何欄位語意等同「已處置」;最接近的候選是 `has_carrier`(該輪是否有彙總帳列),但這只是我推測,spec 沒有一句話明講要拿哪個既有欄位對應這個新名字,也沒說它是布林還是別的型別。
敘述(可重現到哪一步):照 spec 字面實作 `cap_report` 序列化函式時,寫到 `rounds` 這個 list 要塞什麼進 `disposed` 鍵——沒有任何一句話可查,只能停在「不知道要填什麼」這一步,無法往下寫。

## F2 熔斷(S8)與跑滿印字(S9)沒有排除「代碼審循序單審」,跟〈適用範圍〉宣稱的「這三種完全照舊」互相矛盾
severity: major
blocking: 是——照 spec 字面實作,S8/S9 兩段新印字都掛在 `_loop_status_disposal`(`loop status --disposal`)身上,而這支函式現行就是 code 循序單審迴圈問閘的唯一入口(`skills/lumos-code-loop` 教操作者一律 `lumos loop status <編號> --disposal --spec <patch> --repo <根>`),不會因為迴圈是不是「多席」而改用別的函式。S8/S9 的條款(第 73-74 行)與〈做法〉第三、四節都沒有寫任何一句「代碼審循序單審不印這段」的排除條件,implementer 若照條款字面實作,會讓 code 循序單審迴圈跑滿 cap 或折入數累計超過 20 時,也印出熔斷段與跑滿建議——這正是〈適用範圍〉明講「不動」、「完全照舊」的那一種迴圈,等於做出跟自己宣稱互相打架的行為。
引句:「、代碼審循序單審(沒有輪次記帳,同理)、2026-08-26 以前的舊迴圈。這三種 loop next 的判定路徑完全照舊」
file: `scripts/lumos:18541` — `_loop_status_disposal` 現行已經有一個同精神的排除先例:`if not readonly and not str(loop_id).startswith("code"):` 只在非 code 迴圈才印「審查有沒有用」那一段觀測行,code 迴圈的問閘尾故意不印;S8/S9 的新印字段落沒有比照這個既有慣例加上同樣的排除,implementer 很可能漏掉。
file: `skills/lumos-code-loop/reference.md:579` — 「code 迴圈問閘尾★不印★「審查有沒有用」那行(它只在設計審印;code 迴圈的數字照樣進 `lumos gov --stats` 那一段)」,證明 code 循序單審跟設計審的處置閘輸出本來就有意分流,S8/S9 沒有沿用這個分流點是遺漏,不是新決定。
敘述(可重現到哪一步):任一 tier=standard 的 code 循序單審迴圈(`seq=True`,cap=3,per `_TIER_PARAMS["standard"]`)跑到第 3 輪還沒過、或某幾輪折入累計超過 20 條,`lumos loop status code-<topic> --disposal --spec … --repo …` 照 spec 字面實作會印出「換做法/由人裁/累計折入已經 N 條」這類多席設計審才有意義的建議語——這段文字假定的是〈做法〉第二節裡「處置閘、輪、席」的多席語境,對只有一個循序 reviewer 的 code 迴圈沒有對應語意,操作者會被指路去做一個範圍外機制沒設計要它做的事。

## F3(minor)〈做法〉第二節第 1 點列舉的「處置以外的步驟」漏了 `quote`(quote-check 引句錨不到)這一種真實會出現的失敗步驟
severity: minor
blocking: 否——S4 條款本身寫的判準是「閘沒過的原因裡有處置以外的步驟」,這句話語意上已經涵蓋所有非「處置集合/無處置帳」的 fails 值(包含 `quote`),不需要靠第二節那句枚舉才能判斷,所以就算枚舉不全,只要實作照 S4 條款字面(「處置以外」= fails 集合減去處置那一項)寫,行為不會錯;風險只在措辭層——如果有人照抄第二節列出的五個中文詞去做字串比對而不是用「非處置」這個邏輯,quote 失敗會被誤判成走勢分支(S5/S6/S12),但這是措辭精度問題不是條款本身有洞。
引句:「只要失敗步驟裡有「處置」以外的(留痕、條款綁定、落點、資安席、材料被改過)」
file: `scripts/lumos:18468`-`scripts/lumos:18471` — `_loop_status_disposal` 的④quote-check 步驟失敗時把 `"quote"` append 進 `fails`,這是第②步「處置集合」之外、真實會獨立出現的第六種 fails 值,第二節的五個例舉詞裡沒有任何一個對應到它。

已看,無:①〈做法〉一「修出口」段要求 loop next 判「過了沒」改問處置閘、不再委派已退役的舊閘——經 `governance/review-reports/審查跑滿上限提示/r1-intake.md` 記載重現屬實(`lumos loop next` 帶 --spec 對新迴圈確實被 `_loop_status_panel` 內的 `_panel_retired_for` 擋在 rc=2),沒有再退化,S1/S2 的優先序描述(「少了 --spec」排在跑滿之前)在程式碼裡(`scripts/lumos:10632`-`10662`)是天然先於 cap 判斷(第③步在第①步之後才會執行到),跟 [[Projects/loop機械脊椎M1包_計劃]] d6 裁定一致——不影響。②S11「loop next 不再自己另寫收斂記號」:現行 `_loop_status_disposal` 過關時已經會在 `scripts/lumos:18584` 寫 `_loop_gov_mark(env, loop_id, "converged", "disposal gate PASS")`,loop next 只要不再重複呼叫自己那筆(`scripts/lumos:10673`)即可達成「只多一筆」,機制上可行,沒有衝突。③熔斷門檻「20」與「只比最後兩輪」兩個數字,spec 自己在〈誠實界線〉已經承認「沒有回測」並排進 REVISIT,不是隱藏的未查證宣稱——不影響。④落點 `Systems/loop-convergence-recording` 現況經讀取確認:掛 0 份計劃、14 行 KEY、decisions d1-d4(跟本案主題不相干,無互相牴觸)、`about_code` 只管 `scripts/lumos` 一支檔,這份計劃改的也只有這支檔,落這篇合理,不需要另開新節點——不影響。⑤〈回退〉段落「拿不回來的是 cap-reached 記號」的描述跟 `_loop_gov_mark` 是 append-only 寫入(`scripts/lumos:549` 起)、`gov --stats` 讀它做計數(`scripts/lumos:6761`)的現況一致,沒有誇大或漏講回退成本——不影響。⑥「已排除」段落宣稱本案不改任何閘的過關判定與退出碼,經檢查〈做法〉全篇(含 F2 指出的範圍缺口)確實都只在既有 rc0/1/2 路徑之外加印字,沒有新增任何會改變 fails 列表判定邏輯的段落——這個宣稱本身成立,F2 的問題是「印字段落跑到不該印的地方」,不是「印字影響了判定」,兩者不衝突。

最嚴重 severity: major;blocking 共 2 條。
