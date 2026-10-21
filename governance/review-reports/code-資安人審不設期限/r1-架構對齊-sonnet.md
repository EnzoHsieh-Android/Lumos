severity: major

## Finding 1:判不適用的入口集合在判定層另寫一套讀 considerations 的方式
severity: major
blocking: 是
引句:「rows = [x.get("raw") for x in (run.reps["push"][0].get("considerations") or []) if isinstance(x, dict)]」
佐證:`scripts/lumos:11243-11245`(新增),對照 `scripts/lumos:7940-7960`(`_seccell_cons_index`)、`scripts/lumos:11258-11261`(同一函式裡既有的 `_seccell_compute` 呼叫)、`scripts/lumos:7998-8029`(`_seccell_compute` 已回傳 `pending`)

專案裡讀 considerations 只有一條路:`_seccell_compute` 先驗列的形狀、outcome 和引用,再交給 `counted=lambda … _secev_consideration_counted(ctx, penv, cid, row)` 驗核可鏈,只認「算數」的列。`_seccell_consideration_content` 的讀法也是先過 `_seccell_cons_problem`。

新碼在同一個 `_secev_stage_judge` 裡,於 `_seccell_compute` 之前自己撈 `["considerations"]` 的 `raw`,只比對 `outcome == "not_applicable"` 和 `surface` 是字串。它沒有這幾道檢查:

- 沒驗形狀和引用。
- 沒驗核可鏈。
- 沒排除 `counted is False` 的列。

沒有核可的 not_applicable 列,或引用壞掉的列,也會把入口算進 `na_surfaces`,進而要求護欄蓋 `not_applicable_sound`。

`_seccell_compute` 的第三個回傳值 `pending`(`applicability_pending_cells`,即 `state.endswith("not_applicable")` 的格子)正是同一個概念,但 `stage_judge` 把它丟給 `_pend`。

另外,這是在 `ctx` 上先填一份衍生狀態,再讓下游的 `_secev_na_judgments` 讀。判定層因此直接依賴盤點的內部列結構(`raw` 包裝),鄰居都經 `_seccell_*`。這同時是第二種做法和跨層直呼。

## Finding 2:不設期限的 null 判讀有兩種寫法
severity: minor
blocking: 否
引句:「exp = _secinv_date(it["expires_on"]) if it["expires_on"] is not None else None」
佐證:新增在 `scripts/lumos:9317`、`scripts/lumos:9565`;對照鄰居 `scripts/lumos:11075-11076`(`_secev_chain_reminders`:`ex = _secinv_date(e.get("expires_on"))` 後直接 `if ex is not None`)

`_secinv_date` 遇到非字串本來就回 None(`scripts/lumos:7379-7382`)。鄰居的既有寫法是「直接呼叫,再判 None」。新碼在 `_secev_judge_review` 和 `_secapr_entry_dates` 多包一層 `if … is not None else None`。

「這條 expires_on 允許 null」的條件在三處各自內嵌了一份,寫法也不同,沒有共用函式:

- `_secev_ip_review`:`it["expires_on"] is None and it.get("kind") in _SECEV_NO_EXPIRY_KINDS`
- `_secapr_entry_shape`:`e.get("expires_on") is None and typ in _SECAPR_NO_EXPIRY_TYPES`
- `cmd_security_approvals`:`expires_on is None and typ in _SECAPR_NO_EXPIRY_TYPES`

結構沒錯,但跟鄰居的寫法不一致。

## 三問

1. **分層與依賴方向:不對齊(Finding 1)。**
   - 其餘改動都對齊:
     - `_secev_na_judgments` 放在 `_secev_control_table` 和 `_secev_format_judgments` 旁(`scripts/lumos:10535-10576`)。
     - 回傳 `set[str]`,在 `_secev_control_layer`(`scripts/lumos:10583`)用 `|` 併入,與兩個鄰居的簽名和合併方式相同。
     - `_SECEV_CONDITIONAL_JUDGMENTS` 加一項,沿用既有機制。
   - 唯一越層的是 `stage_judge` 直接讀 considerations 的原始列。

2. **命名與錯誤處理:大致對齊,有 Finding 2 的 minor。**
   - 命名跟鄰居一致:
     - `ctx.na_surfaces` 的位置和註解跟 `ctx.over_items`、`ctx.tools_broken` 一致(`scripts/lumos:10135-10138`)。
     - `_SECEV_NO_EXPIRY_KINDS` 和 `_SECAPR_NO_EXPIRY_TYPES` 各自沿用 `SECEV`、`SECAPR` 前綴。
   - 沒有新增錯誤代碼:null 的 deployment 照舊走 `evidence_fence_invalid`,例外照舊走 `approval_fields_missing`(`scripts/lumos:9553-9554`)。CLI 的擋下訊息格式沿用原句型。

3. **第二種做法:有一處(Finding 1)。**
   - 讀 considerations 多了一條旁路。
   - 表達「不設期限」用的是 JSON `null` 加允許清單。專案裡沒有既有的「不設期限」寫法可對照,所以我不判它是第二種做法。
   - 測試 `t_secev_s68_review_no_expiry` 和 `t_secev_s69_not_applicable_conditional` 都用既有的 `_SgRepo`、`_sg_eval`、`_sg_codes`、`_sg_chain_status`,對齊。

⚠ 交編排者:`ctx.na_surfaces` 在 `_secev_stage_judge` 填,而 `_SecevCtx(` 目前只在 `scripts/lumos:11157` 建立,`_secev_control_layer` 也只經由 `stage_judge` 到達。現在沒有第二個呼叫點會讀到空集合。不過 `_secev_na_judgments` 讀的是呼叫前才補的屬性,這是隱性順序依賴。`over_items` 也是同樣的模式(`scripts/lumos:11242`),所以我不把它單獨列為不對齊。

不對齊共 2 條,其中 major 1 條
