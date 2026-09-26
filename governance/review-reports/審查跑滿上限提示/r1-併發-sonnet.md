severity: major

## F1 「沒有彙總帳」判準漏了 vacuous(0 發現)輪,會把乾淨輪誤判成「無法判斷」
severity: major
blocking: 是——照字面實作,「彙總帳」只認「有 findings_set 那一列」;任何 0 發現的乾淨輪都沒有這一列(disposal 閘把它另外標成 vacuous、當合法通過看待),於是這種輪會被這份新功能誤判成「沒記處置」,吐出「判不了,自己看」而不是本該給的「附理由放行」或「折入 0 條、在降」——正是這個功能最該幫上忙的那個情境(輪已經乾淨,只差別的步驟卡住)反而被判成看不懂。
引句:「若有任何一輪沒有彙總帳,則應印那一輪沒記處置並不給建議」
file: `/Users/enzo/harness/lumos-toolchain/scripts/lumos:18340` `carriers = [r for r in latest if "findings_set" in r]`——判斷「這輪有沒有彙總帳」目前的唯一依據是有沒有帶 `findings_set` 的那一列。
file: `/Users/enzo/harness/lumos-toolchain/scripts/lumos:18366-18373`——0 發現的輪(`carrier is None` 但 `all(_fz)`)被 disposal 閘明文標成合法的 `vacuous`,印「這輪 0 條發現,沒有東西要處置(空輪;留痕仍要重驗)」,並不進 fails——即現有機制把它當「已處置」,不是「沒記處置」。
重現場景:一個新開的設計審迴圈(post-2026-09-12,落點閘生效)在最後一輪三席全報 clean/0 findings,但計劃還缺一條 `[SN]` 沒標 `[test:]`——`_disposal_clause_step`(scripts/lumos:18153-18197)判 fail,整體 DISPOSAL GATE FAIL(rc1),於是不會 converged、繼續往下走到 cap-reached。此時「彙總帳」判準(依 findings_set 有無)看到的是「這輪沒有 findings_set 那一列」,依 S6 字面就要印「這輪沒記處置」、整份報告放棄給建議——但實際上這輪的折入數是 0(乾淨),按 S4/S5 的規則本該判「在降+severity≤minor→附理由放行」。這不是罕見邊界:任何「內容已經乾淨、但條款綁定/落點/資安席某一步還沒補齊」的組合都會踩到。
說明:S6 的「彙總帳」一詞在計劃裡從未定義成排除 vacuous,計劃裡也沒有把這個邊界寫進「誠實界線」或條款——屬於未定義詞造成的字面實作缺口,不是措辭問題。

## F2 「併發:只讀帳本」的排除語沒有涵蓋修出口(一)本身的讀寫面
severity: minor
blocking: 否——不會讓實作者做錯決定(S1/S2 條款本身已經寫清楚要委派處置閘,照著做不會漏掉行為),只是「實務隱患」小節用來排除守衛面風險的那句話,對「修出口」這一半並不準確;經實測差量很小,不到需要擋下實作的程度。
引句:「併發:只讀帳本;處置閘讀帳的方式與壞行擋法照舊,這份不另開讀帳路徑。」
file: `/Users/enzo/harness/lumos-toolchain/scripts/lumos:10666-10671`——目前 `cmd_loop_next` 對新迴圈只委派 `panel` 模式的輕量 gate(只做 G3 hash 檢查+帳面欄位比對,不讀 report/snapshot 全文、不掃測試檔);S1 要求改委派 `--disposal`(`_loop_status_disposal`,scripts/lumos:18265),那一支除了讀帳本外,還會讀 `--spec` 檔文字算 sha256、讀判定輪每一席的 `report_path`/`snapshot_path` 全文做 quote-check(scripts/lumos:18398-18466)、對非 code 迴圈跑 `_disposal_clause_step` 掃全部測試檔建索引(scripts/lumos:18153-18197、`discover_test_methods`4475-4497)、跑 `_disposal_landing_step` 讀計劃 frontmatter(scripts/lumos:18214-18262)。這些都不是「帳本」。
file: `/Users/enzo/harness/lumos-toolchain/scripts/lumos:18584`——disposal PASS 時會呼叫 `_loop_gov_mark(..., "converged", "disposal gate PASS")` 寫治理帳,這是「只讀」以外的新增行為(對這批迴圈而言:之前因 panel 閘退役直接 rc2,從沒真的走到這裡)。
已用計時器量過實際成本(複製 `scripts/lumos` 到唯讀實驗目錄跑,不動 repo):對本 repo 47331 行的 `scripts/test_lumos.py` 跑 `discover_test_methods` 約 0.055 秒;對本 repo 現存最大的一份審查報告(2.2MB,`governance/review-reports/推筆記認家/r3-外家codex-transcript-中斷.md`)跑 quote-check 約 0.034 秒。量級都在百毫秒以內,單次呼叫不構成效能瓶頸,所以判 minor 而非 major。

## 已看,無:
- 「2026-08-25 之後開的迴圈」這個切點跟現有 `_panel_retired_for` 的預設 cutoff `"2026-08-26"`(scripts/lumos:8203,`ts[:10] >= cutoff`)是同一天:計劃寫的是「之後」(嚴格大於 8/25),日期是離散值,`> 2026-08-25` 與 `>= 2026-08-26` 等價,兩邊沒有實際落差;S9 的「以前」也同理不會漏接 8/25 當天(當天落在現有 cutoff 的「未退役」那一側,行為與 S9 要求的「照舊」一致)。
- 「一份計劃現在到不了跑滿上限」這個前提我沒有重跑,依派工詞可信任 `governance/review-reports/審查跑滿上限提示/r1-intake.md` 的重現結論(直接取退出碼=2,印「擋下:panel 閘自 2026-08-25 甲裁後僅供舊迴圈回放」),與我讀到的 `_panel_retired_for`(scripts/lumos:8197-8209)、`cmd_loop_next` 步驟②(scripts/lumos:10663-10671)程式碼互相印證,成立。
- `.canary-log.jsonl`(`_jsonl_append_verified`,scripts/lumos:8017-8045)與 `.governance-log.jsonl`(`_append_governance_log`,scripts/lumos:949-971)的寫入都是 `open(path,"a")` 後單次 `f.write()` 再於 `with` 區塊結束時關檔 flush,對這份計劃會用到的短 JSON 單行(遠低於一般檔案系統的原子寫入門檻)不會出現「帳本最後一行寫到一半」的撕裂寫;`canary record` 另外還會落盤自驗(讀回確認鍵值存在),兩個會談同時各記一筆的最壞情況是「先到先寫、後到讀到較舊狀態或稍後才看到對方那筆」,不是寫壞。這份計劃本身也沒有新增任何寫入路徑(自己排除的「已排除:不可逆」條款屬實)。
- disposal PASS 時會內部呼叫 `_loop_gov_mark("converged", ...)`(scripts/lumos:18584),而 `cmd_loop_next` 自己在 rc==0 時也會再呼叫一次 `_loop_gov_mark("converged", ...)`(scripts/lumos:10673)——這會造成同一次收斂在治理帳裡留兩筆 converged 記號。但這不是這份計劃引進的新洞:panel 閘現在(對 2026-08-25 以前的舊迴圈)已經是同樣的雙寫(scripts/lumos:8495/8500 內部寫一次、10673 外層再寫一次),S1 只是讓同一種既有模式在新迴圈上被啟用,不是這份計劃造成的退化,所以不算它的問題。
- 「效能:只數帳本裡這個編號的列」這句話,對「印什麼」(做法二)與「提早熔斷」(做法三)兩節是準確的——`folded_set`/`severity` 都是每輪已經讀進 `rounds` 的欄位,不需要另外開檔;真正會多讀檔的只有「修出口」那一段,已在 F2 拆開講。
- 節點合約檢查:`Systems/loop-convergence-recording` 的 d1–d4 決策(tail-K 滑動窗、severity 自報定位、missed 自然重置、loop next 材料路徑取最後一筆有值)這份計劃都沒有動到,只是在既有出口與既有處置閘之上加印一段建議,不改變 K-streak/severity/hash 鏈任何一項判準,也不改退出碼(S7/S8 綁測試)——不影響該節點宣稱的行為。

最嚴重 severity: major;blocking 共 1 條(F1)。
