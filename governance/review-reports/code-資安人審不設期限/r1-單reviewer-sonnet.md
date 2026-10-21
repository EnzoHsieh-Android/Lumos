severity: major

## F1 測試 ② 抓不到「不設期限的審查紀錄不再綁版本」
severity: major
blocking: 是
引句:「合成 repo 提交時會照新 blob 重算綁定,所以這裡看到的是「人審核可的內容對不上」;真實 repo 沿用舊綁定時是 binding_changed。兩種都是失效」

失敗場景:
- `t_secev_s68_review_no_expiry` 的 ② 改了 `src/app.py` 之後重新 commit。合成 repo 會用新的 blob 重算 `bindings`。人審核可的內容雜湊因此對不上,review 退成 ai,判 `missing:human_review_missing`。
- ② 的斷言接受 `{"stale:binding_changed","missing:human_review_missing"}` 任一個。所以它從沒走到 `scripts/lumos:10287` 的 `binding_changed` 判定。
- 條款 S68 的「綁定的檔一改照樣判 stale:binding_changed」,也就是 d21 說的「只靠綁版本失效」,實際上沒有測試守住。

最小重現(在我自己的 clone):
- 改壞:在 `_secev_bindings_problems` 的 `for b in it["bindings"]:` 迴圈裡加 `if it.get("expires_on", 1) is None: continue`。結果是不設期限的紀錄永遠不判 binding 變動。
- 結果:`python3.14 scripts/test_lumos.py -k t_secev_s68` 仍然 `8 passed, 0 failed`,② 打 ✓。
- 修法:② 要用明確的舊 `bindings`(不用 `@auto`),並斷言 `stale:binding_changed`。

file: `scripts/test_lumos.py:106474`(`t_secev_s68_review_no_expiry` 的 ②),`scripts/lumos:10287`

## F2 「其他核可型別寫 null 照舊看不懂」只測了 exception,放寬到別的型別測試照綠
severity: major
blocking: 是
引句:「deployment 審查紀錄與其他核可型別寫 null 應照舊判看不懂(審查紀錄 evidence_fence_invalid、核可鏈 approval_fields_missing)」

失敗場景:
- 測試 ④ 只用 `exception` 驗了 null 會被擋。
- 清單 `_SECAPR_NO_EXPIRY_TYPES` 是唯一的放行點(`scripts/lumos:9554`、`11692`)。
- 把它改成 `("human_review","gate_setting","revision")`,`gate_setting` 與 `revision` 的 null 就漏進來。這兩型本來上限 30 天,現在會變成永不過期。
- CLI 端也一樣:`security approvals payload gate_setting …` 不帶 `--expires-on` 也會放行,測試只試了 exception。
- 實測這個改壞後 `-k t_secev_s68` 仍然 `8 passed, 0 failed`。
- 這正是題目要求的「不准順手放寬」的守衛。它沒有逐型別的測試,守衛就是空的。
- 修法:對 `_SECAPR_TYPES` 其餘每個型別(`approvers_*`、`revision`、`gate_setting`、`tool_list_change`、`threat_table_change`、`consideration`、`suppression`)各測一次 null 被擋。payload 的 rc2 也同樣逐型別測。

file: `scripts/test_lumos.py:106474`(S68 ④、①'),`scripts/lumos:9554`

## F3 撤銷金鑰收不回「不設期限的人審」,d21 沒講這個代價
severity: major
blocking: 是
引句:「綁定沒涵蓋到的東西改了(作者漏寫進 fixture_globs 的夾具、執行環境沒寫進描述檔的差異)不再有時間兜底,舊人審會一直有效」

失敗場景:
- 核可鏈的撤銷只往後生效。`scripts/lumos:9657` 只擋「撤銷之後」用被撤金鑰簽的筆,先簽的筆照舊 `ok`。計劃 `Projects/安全主張驗收閘_計劃.md` 的金鑰遺失流程(第 757 行)就是撤舊金鑰、加新金鑰。
- 以前被外洩金鑰簽下的 `human_review` 最多活 90 天。現在簽成 `expires_on: null`,撤銷金鑰也收不回來,只能改動被綁定的程式。
- d21 的 trade_offs 只講了夾具漏綁和外部威脅,沒提「金鑰外洩後已簽的人審永遠有效」,也沒補回頭條件。

最小重現:
- 在我 clone 的 `scripts/test_lumos.py` 加了一支探針測試 `t_zz_probe_revoked_signer_null_hr`。
- 做法:`_SgRepo(keys=2)`,審查紀錄與人審都設 `None`,commit 後用 key1 追加 `approvers_revoke` 撤掉簽人 key0,`today=2027-06-01` 判定。
- 輸出:`review verdict after signer revoked  qualified [(1,'approvers_init','ok'), (2,'human_review','ok'), (3,'approvers_revoke','ok')]`。簽人已被撤,人審仍 ok,review 仍 qualified。
- 建議:在 d21 trade_offs 明寫這個代價,並補一條回頭條件。或讓撤銷對該簽人先前的 null `human_review` 追溯生效。

file: `scripts/lumos:9657`(迴圈逐筆驗)、`scripts/lumos:9671`

## F4 計劃正文仍有照做會用錯的舊句,d21 也沒宣告取代 d10
severity: minor
blocking: 否
引句:「| `reviewer`、`author`、`reviewer_kind`、`judgments`、`expires_on` | review_record 必填 | 審查人、被審內容的作者(字串或字串陣列)、`ai` 或 `human`、這筆紀錄審了哪幾項判斷(id 見〈機械做不到的判斷〉)、到期日 |」

失敗場景:
- 圍欄欄位表(`安全主張驗收閘_計劃.md:417`)只寫 `YYYY-MM-DD` 的「到期日」,沒說 review 可以寫 null。
- 核可鏈欄位說明「`expires_on`:到期日,每筆都有」(第 726 行)沒補 null。
- 「怎麼加一筆」(第 755 行)的指令列只有 `--expires-on YYYY-MM-DD`,沒說 human_review 可以不帶。
- d10 content(第 149 行)仍寫「人審 90 天」。d21 只宣告取代 d8 與 d20,沒宣告取代 d10 裡這句。照決策清單讀,d10 與 d21 會打架。

file: `docs/lumos-toolchain-knowledge/Projects/安全主張驗收閘_計劃.md:417,726,755,149`

## F5 舊版 lumos 讀到 null 會把整塊證據圍欄判成讀不出來,沒有任何相容提示
severity: minor
blocking: 否
引句:「expires_on 是 review_record 必填、要是 YYYY-MM-DD(review 種類可寫 null:不看時間、只靠綁版本失效)」

失敗場景:
- 舊版 lumos 讀到 `expires_on: null` 的審查紀錄,會回「expires_on 是 review_record 必填、要是 YYYY-MM-DD」。
- `scripts/lumos:8625` 是圍欄層級的檢查,同一篇 Verification 的圍欄會整塊判 `evidence_fence_invalid`,連其他證據項一起擋。
- 核可鏈那一筆則會被舊版判 `approval_fields_missing`。
- 結果是擋下(fail-closed),不會漏放,但訊息誤導。d21 與 `Systems/安全證據閘.md` 都沒提「先升工具再寫 null」。圍欄標記仍是 `lumos-evidence-v1`,沒有版本區分。

file: `scripts/lumos:8625`、`scripts/lumos:9554`

---

## 逐點走過、判無問題

**讀 `expires_on` 的地方(含提醒、輸出、JSON、核可查詢、verify、寫入前驗證):**
- 審查紀錄的判定與提醒:`scripts/lumos:9317-9324`。null 時 `exp=None`,三處比較都有 `exp is not None` 守衛。
- 核可鏈:
  - `_secapr_entry_shape`(`9554`):缺鍵仍判 `approval_fields_missing`,因為前面的鍵集合檢查已先擋。
  - `_secapr_entry_dates`(`9565`):null 只對 `human_review` 放行。
  - `9581` 的 `ex` 只用在 `approvers_init` 金鑰池,不影響 `human_review`。
  - `9671` 有守衛。
- 提醒與輸出:`11075` 有 `ex is not None` 守衛。`_secev_chain_view` 與 `verify` 的輸出不碰 `human_review` 的 `expires_on`。
- 其他讀取點:`11305` 的 consideration、`10506` 的 exception 是別的型別,不受影響。
- 寫入端:`security approvals payload` 的 `--expires-on ""` 與缺鍵都會擋。`security-approval-add` 走同一支驗證函式,沒有另一條路。

**邊界值:**
- `expires_on` 缺鍵、空字串、數字或 True 都判看不懂。只有 JSON null 加上 `kind=review` 才放行。
- `expires_on` 為 null 且 `kind=deployment` 判看不懂,測試 ③ 有覆蓋。

**同護欄同種類多筆紀錄:**
- 有日期的與 null 的並存時,仍取最差。有日期且過期的那筆會讓整類壞掉,沒有行為改變。
- `_secapr_lookup` 取最新的 ok 筆,沒動。

**判不適用條件(S69):**
- `ctx.na_surfaces` 取自推送版 `considerations` 的 `raw` 底下,`isinstance` 守衛足夠。`surfaces` 非字串的元素被過濾,缺或壞的 `considerations` 退成空集合。
- 不看 NA 格子有沒有核可,只要存在就要蓋。會多擋,不會漏放。
- 主線凍結下來的護欄(推送版刪掉)用主線的 `reported_status`,但格子用推送版。作者可以在推送版刪格子,少要求一項。這是 d21 trade_offs 已寫的取捨。刪除護欄本身另需要 revision 核可,我想不出額外失控的具體場景,所以不另列 finding。
- 我試了幾種改壞,S69 的測試都會翻紅:忽略 surface、少認 `reported_status`、AI 不算數。

**日期正確性:**
- 有日期的紀錄當天有效、隔天過期。測試 ★前置★ 證實半年後有日期的仍判 `review_expired`。

## 圖譜鏡頭(固定席節點)
- 不受影響:`lumos-cli-read`(search 濾網)、`lumos-cli-lifecycle`(re-inject sentinel)、`guard-kill`(rc 與 JSON 純度)、`loop-convergence-recording`、`pitfalls-code-loop`(此 diff 只動安全證據閘)。
- `bound-tests-gate`:新條款 S68、S69 的綁定測試名稱都存在,且實跑 `8 passed`、`5 passed`。但 F1、F2 顯示綁定測試擋不住上述改壞。
- `design-loop`(處置閘):S68、S69 有 `[test:]` 綁定,形式符合。
- `測試假綠形態` 的 INVARIANT(還原翻紅釘要配前置斷言,證明被測那條路真的被走到):S68 ② 沒有這種前置,F1 就是這條 INVARIANT 描述的第④型現象。

## 清理
我在 `/tmp/lumos-seat-work/code-資安人審不設期限/單reviewer-sonnet/repo` 留了一份 clone,裡面有被我加過探針的測試檔。`lsof +D` 顯示有一個不是我開的程序(pid 20684,`git push Lumos HEAD:refs/heads/EnzoHsieh-Android/sec-guide`,看來是別的會談)正開著這個目錄下的檔案。依「只刪自己的、有程序開著先不刪」的規則,我沒有刪。請收貨後,等那個程序結束再刪這份 clone。

severity: major
(最高:F1、F2、F3)
