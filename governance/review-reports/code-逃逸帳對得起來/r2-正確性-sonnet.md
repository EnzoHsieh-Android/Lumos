severity: blocker

## F1 已排除的「plan」逃逸列仍污染共用佐證表,連累真設計逃逸被誤判「歸因不明」
severity: blocker
blocking: yes

引句:「if lid in released:」

file: `scripts/lumos:9877-9890`(`_escape_evidence_keys` / `_escape_shared_evidence`)、對照 `scripts/lumos:9935-9945`(`_escape_row_bucket`)

這輪修正加了「落帳的 `loop_kind` 為準,不因後來才有審查紀錄就事後改類」(`_escape_row_bucket` 第一行:`kind = r.get("loop_kind") if r.get("loop_kind") in ("code", "design", "plan") else _escape_loop_kind(lid, review_ids)`)。這條規則的存在本身就承認:一個迴圈可能先以「plan」身分記過逃逸,後來這個迴圈才進了審查帳、放行(`released`)——這正是 S1 條款要處理的情境,不是我杜撰的邊界。

問題出在:`_escape_row_bucket` 用這個「落帳為準」的判法決定要不要把一列丟進 `plan` 桶(直接跳過、不進任何統計),但建「同佐證對到哪些迴圈」的 `_escape_shared_evidence`(第 9882–9890 行)完全不知道這個判法——它只看 `lid in released`,不看這一列自己記的 `loop_kind` 是不是 `plan`。於是:一列本該被整個排除在統計之外的「plan」逃逸,只要它的迴圈剛好已經 `released`,它的 `sha`/`defect_ref` 照樣會被塞進 `ev_loops`;如果剛好跟另一個**真正的、有效的**設計逃逸撞到同一把佐證鍵,那筆真逃逸就被誤判成「歸因不明」而被踢出分子,漏網率被悄悄壓低。

重現(在 exp2-正確性 的乾淨副本上跑,不動原 repo):
1. 造兩個都已放行的設計迴圈「甲」「乙」(各自有審查紀錄、各自在治理帳有 `converged`)。
2. 甲的逃逸列刻意帶 `loop_kind="plan"`(模擬「記的時候甲還沒有審查紀錄」這個 S1 明講的場景),sha 設成跟乙的逃逸列相同(`SAMESHA`)。
3. 乙的逃逸列是一筆正常的、有效的設計逃逸,同一個 `SAMESHA`。
4. 跑 `lumos loop escape-stats --json`。

實測輸出:
```
{"categories": [{"kind": "design", "tier": "standard", "scope": "未分類",
  "released": 2, "leaked": 0, ...}],
 "totals": {"unattributed": 1, "plan": 1, ...}}
```
甲的那列正確落進 `plan`(1 筆,符合預期,不進任何分子)。但乙那筆**貨真價實、佐證完整**的設計逃逸,本該讓 `design/standard/未分類` 這格的 `leaked` 記 1、`rate` 從 0 變成 0.5——結果因為甲那筆本該被排除的「plan」列還在 `ev_loops["sha:SAMESHA"]` 裡放了自己的迴圈,乙的 `sha:SAMESHA` 一查發現對到兩個迴圈,被判成 `unattributed`,`leaked` 停在 0、`rate` 停在 0.0。

這不是攻擊性輸入,是這輪修正自己新增的規則(記錄優先於推論)造成的副作用——`_escape_row_bucket` 用了新規則排除某一列,但共用的佐證表建構函式沒有同步套用同一條排除規則,兩處對「這一列算不算數」的認定不一致。後果是這個功能存在的核心目的(「各類別放行後漏了多少」算得對不對)被悄悄弄錯,而且是往「看起來比實際安全」的方向錯,不會有任何錯誤訊息或例外。

修法方向:`_escape_shared_evidence` 建 `ev_loops` 時,對每一列先套用跟 `_escape_row_bucket` 同一支判斷(是否該列的落帳 `loop_kind` 或推論值為 `plan`),`plan` 列一律不進 `ev_loops`;或者把「決定桶」這件事整個往前挪一次算好、`_escape_shared_evidence` 直接吃已經排除 plan 列的子集。

我在 `scripts/test_lumos.py`(僅動我的乾淨副本,未動原 repo)加了下面這支探針並實跑驗證,原 repo 完全沒有改動(有跑 `git diff --stat` 核對):

```python
def t_probe_plan_row_pollutes_shared_evidence():
    v = _mk_escape_fixture(review=[("甲", "standard"), ("乙", "standard")], converged=["甲", "乙"],
                           escapes=[_esc_row("甲", token="E1", sha="SAMESHA", loop_kind="plan"),
                                    _esc_row("乙", token="E2", sha="SAMESHA")])
    st = _esc_stats(v)
    # 現況:design/standard 這格 leaked==0、totals.unattributed==1(乙的真逃逸被誤吃掉)
    # 應該:leaked==1(乙那筆是有效逃逸)
```

---

已看,無:`_escape_row_bucket` 對 `sha`/`defect_ref` 各自成鍵的歸因擴大(S8/r1 外家否決席那條)本身邏輯正確,用真實 `.escape-log.jsonl`(28 筆)跑過沒有現存資料觸發;`_escape_released_loops` 的 `gate == "design-loop"` 篩選跟真實治理帳（263 筆 converged 全部是這個 gate 名）核對一致,沒有漏篩代碼審迴圈;`_cat_cache` 只是行程內快取、沒有跨呼叫失效問題；`_review_loop_ids` 改成呼叫 `_escape_review_rows_by_loop` 後在 `_escape_stats` 裡被讀了兩次審查帳(一次直接、一次經 `_review_loop_ids`),同一份檔案重複解析兩次,是效能與極端併發競態上的瑕疵,但單次執行下不改變結果、沒有可重現的輸入能翻紅,不升等為缺陷。
