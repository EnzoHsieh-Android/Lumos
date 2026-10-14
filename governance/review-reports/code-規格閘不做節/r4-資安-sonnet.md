severity: major

這輪外層看門有兩個洞,各能讓真要做危險事的計劃不經真正的輕量審就推上去。第一個是輕量審沒綁到這份計劃的內容,第二個是計劃可以不被推送前檢查挑中。「留痕之後才審」和「略過的詞進指紋」這兩道我試了都擋得住,其餘攻擊面見最後的未成立清單。

我在 `git clone` 出來的實驗 repo 裡跑,用 `python3.14` 呼叫測試檔裡的 `_mk_spec_gate_repo`、`_sg_plan2`、`run`,指令都是真的 `lumos`。實驗目錄和 `gctl-test-*` 暫存已刪。

---

severity: major
blocking: 是 — 輕量審沒綁到這份計劃的內容,假審一行指令就過,推送前的唯一看門形同虛設
引句:「verdict, fails = _light_gate_fails(rounds, env.vault / prel, cur_sha_override=(rounds[-1].get("result_sha256") if rounds else None))」

這是「借別份計劃的審」「手寫假審」「同名迴圈借審」三條攻擊共用的洞。`cur_sha_override` 傳的是那筆審查自己的 `result_sha256`,所以「窗末 result 等於當前檔」的比對變成自己比自己,永遠成立。整個推送前檢查也沒有比對帳上的 `spec_path`,所以那筆審查審的是哪個檔都不影響結果。

攻擊步驟(輸入到結果):
1. 計劃「## 不做」寫 `- 不做:先實作扣款`,同時真的要做扣款。跑 `lumos spec-gate Projects/甲_計劃`。
2. 規格閘判風險低,留痕 `nogo_skipped_n=1`,輸出說推送前要輕量設計審。
3. `spec-gate --push-check HEAD~1..HEAD` 回 rc1,講「帳上沒有這個編號的輕量審」。
4. 不派任何審查席、不敲 `loop next`,直接審一個無關檔 `tests/run.py`:
   `canary record caught --loop 甲 --severity clean --findings 0 --reviewed <run.py 的 sha256> --spec tests/run.py`
5. 回 rc0,「憑證 CANARY-6eac624b」。
6. 再跑 `--push-check`,回 rc0:`✓ 甲_計劃:留痕裡的 1 支測試全綠`。
7. 帳上那筆審查的 `auditor` 是空字串、`spec_path` 是 `tests/run.py`,和計劃毫無關係。
8. 對照同一份帳:`lumos loop status 甲 --light --spec <計劃>` 回 rc1,「spec 於審計後被改動(窗末 result ≠ 當前檔)」。同一支 `_light_gate_fails`,既有路徑拿真計劃檔比 sha 會擋下這筆假審,新的推送前路徑把 sha 比對關掉了。

手寫假帳比既有留痕多給了什麼權力:
- 在既有 `loop status --light` 路徑,偽造審查至少得指向計劃的當前內容。
- 這輪的推送前路徑不用指向計劃,連審查的是不是這份計劃都不驗,也沒有席數、`auditor`、`loop next` 派工的要求。
- 結果是 AI 編排者一行指令就能替自己簽一張「放行票」。比起「沒有輕量審」,實質只多了一道不需要審查席的儀式。
- 憑證綁定的前提是 sha 比對,這輪把它拿掉,等於把計劃內容的綁定讓出去。
- 同樣能過的做法還有:拿真審過的舊版計劃的帳改 loop 編號、拿別份計劃的審借來用、手寫一行 jsonl。只要排在規格閘留痕之後,都能過。

建議修法:把 `cur_sha_override` 換成當前計劃檔的 sha256,並要求最後一筆審查的 `spec_path` 指向這份計劃。「只改空白不必重審」的需求用「去空白後的雜湊」處理,不要用「完全不比」。

佐證:`scripts/lumos:9157`(`_spec_gate_push_light`)、`scripts/lumos:11841`(`_light_gate_fails`)、`scripts/lumos:11835`(`_hash_chain_check`,有 override 就不讀檔)。

---

severity: major
blocking: 是 — 把計劃狀態改掉,或讓計劃沒有規格閘留痕,整個推送前檢查(含這道看門)就不看它
引句:「rec = latest.get(nfc(_loop_id_for_plan(prel)))」

`_spec_gate_push_scan` 只挑 `status == doing`、而且「這個迴圈編號最後一筆規格閘留痕是 low」的計劃。其餘一律不查,連提醒都沒有。這個挑選機制是本分支之前就有的。但這輪把「危險詞要輕量審」的全部權責放在這個入口之後,所以入口一關,新看門等於沒有。

攻擊步驟與結果:
1. 同上的夾帶計劃(不做清單寫「不做:先實作扣款」)跑過 `spec-gate`,這時推送前檢查會擋(rc1)。
2. 把計劃開頭欄位 `status: doing` 改成 `status: done`,提交。`--push-check HEAD~1..HEAD` 回 rc0,什麼都沒印,連測試也不跑。
3. 另一條路:`git mv` 把計劃改名(`甲_計劃.md` 改 `乙_計劃.md`),迴圈編號變了,新編號帳上沒有留痕。`--push-check` 回 rc0。
4. 這兩種做法不產生任何治理事件,也不留逃逸帳。

說明:
- 這是既有的挑選規則,「用 `spec-gate` 跑過才有留痕」的前提本來就在。但本題目標正是「讓計劃不被推送前檢查挑中」,而這輪正好把唯一的防線放在這個入口後面。
- 我沒查到其他閘會要求「有 `## 不做` 清單略過危險詞的計劃一定要有規格閘留痕或維持 doing」,所以按 major 報。若另有閘擋改名或改狀態,可降級。
- 建議修法有兩個方向:一是 `status` 不是 `doing` 但範圍內改了該計劃時至少比對一次;二是對範圍內新出現(包含改名)的 `Projects/*_計劃.md` 要求有留痕。

佐證:`scripts/lumos:8903`(`_spec_gate_push_candidates`)、`scripts/lumos`(`_spec_gate_push_scan` 內 `if n is None or str(n.fields.get("status")) != "doing"`)。

---

我另外試了這些,沒有成立(不計入 finding):
- **讓帳讀不到而放行**:把 `.canary-log.jsonl` 設成 `chmod 000`,或換成目錄,`_spec_gate_latest_records` 沒有 try/except,拋出 traceback、rc1,結果是擋下(fail-closed),不是放行。
- **帳裡混壞行**:塞一行非 UTF-8 的壞資料,檢查照常運作,仍然擋下。
- **竄改留痕再洗掉略過詞**:手改留痕的 `door_rule` 為 1、`nogo_skipped` 清空、`needs_light_review` 改 False,沒有用。推送前讀現況重算 `nogo_skipped` 再和 `clause_sha` 比,仍擋下。
- **留痕之前先審再改清單**:順序規則靠帳的 append 序,舊審排在新的規格閘留痕前面時,回「帳上的輕量審都早於這筆規格閘留痕」。要過只能重新記一筆假審,那是第一條。
- **改門規則版本跳過**:`_spec_gate_push_stale` 不看留痕的 `door_rule`,但 `clause_sha` 已把略過的詞併進來。舊版留痕遇到新的略過詞會過期,這條走不通。
- **同名迴圈互借**:`甲.md` 與 `甲_計劃.md` 共用迴圈編號 `甲`。兩份計劃的條款指紋不同,拿另一份的留痕會被判過期而擋。借審這條路實際上會被第一條涵蓋。
- **鄰近的繞法,不算新增**:合格的「已排除」理由行裡塞危險詞會整行被跳過、完全不進 `nogo_skipped`。這是本分支之前就有的路徑。另外,關鍵字表沒涵蓋的說法(例如 wire money)根本不會被抓到。

兩條 finding 都是 major,blocking 兩條(0 blocker,第一條優先處理)。
