severity: major

我只讀了程式,沒有跑測試。行號指向 `/Users/enzo/orca/workspaces/lumos-toolchain/secev-noexpire` 這份工作樹裡的 `scripts/lumos` 與 `scripts/test_lumos.py`。

## 第 1 問:分層與依賴方向

**對齊。**
- 期限判斷仍分在三處,跟鄰居一樣:形狀層、判定層、核可鏈層。形狀層是 `_secev_ip_review`(8630)與 `_secapr_entry_shape`(9559)。判定層是 `_secev_judge_review`(9322)。核可鏈層是 `_secapr_entry_dates`(9570)與 `_secapr_verify`(9676)。沒有跨層直呼。
- `ctx.na_surfaces` 由 `_secev_stage_judge` 在逐條判定之前填好(11259),護欄層的 `_secev_na_judgments`(10572)再讀它。這跟 `ctx.over_items = _secev_budget_prepass(...)` 的既有做法一樣:階段函式填 ctx,下層只讀。
- 修補把「格子」從判定後挪到判定前(11255)。判不適用的判斷因此直接讀 `_seccell_compute` 驗過核可鏈的結果,沒有另寫一套去讀 considerations。`security list` 那支(8143)用同一個函式,只是不傳 `counted`,所以兩邊是同一個入口。這是上一輪架構席 F1 的收斂,已對齊。
- `_secev_chain_reminders` 本來就用 `ex is not None` 判讀(11085),新增的 null 處理與它一致。

## 第 2 問:命名與錯誤處理

**大致對齊,有一條 minor。**
- null 的表示一致:`expires_on: null` 在形狀層放行,下游統一用 `is not None` 守住。`_secev_ip_review` 的錯誤訊息沿用原句再加括號補充。`cmd_security_approvals` 仍回 rc2,用 `_secinv_say` 印「擋下:」。錯誤代碼沒有新增。
- 測試端的 `review_expires` 與 `hr_expires` 是 `_SgRepo` 既有屬性(104819、104877、104968),直接覆寫它們是既有手法。
- `_secev_kind_verdict` 改成 `base | set(extra_judgments)`,延用了原本 `extra_judgments` 的傳法。

### finding 1:新輔助函式與新常數的位置和命名跟鄰居不一致
severity: minor
blocking: 否
引句:「def _sec_no_expiry(value, kind, allowed):」
佐證 file:
- `scripts/lumos:8495-8503`:函式插在 `_SECEV_CONDITIONAL_JUDGMENTS` 與 `_SECEV_JUDGMENT_FORMATS` 兩個常數之間,打斷了常數群。
- `scripts/lumos:9451`:`_SECAPR_NO_EXPIRY_TYPES` 放在 `_SECEV_` 區,離同族的 `_SECAPR_KEYS`、`_SECAPR_TYPES` 很遠。
- 前綴:鄰居都用 `_secev_`、`_secapr_`、`_secinv_`、`_seccell_`,這支用了沒有層級的 `_sec_`。
- 結構是對的,只是位置和命名偏離慣例。

## 第 3 問:第二種做法

### finding 2:撤銷的判法另起一套
severity: major
blocking: 是
引句:「for ent in res["entries"]:   # 不設期限的核可沒有時間兜底:簽章人後來被撤銷,先前簽的也一併失效」
佐證 file:
- `scripts/lumos:9592-9593`:核可鏈既有的撤銷判定在 `_secapr_entry_status`,規則是 `signer in revoked` 就判 `approval_signer_revoked`。它是依序判的,只管撤銷之後才簽的那些筆。
- `scripts/lumos:9626` 的 docstring 寫「撤銷永久有效」,講的也是這個順序語意。
- `scripts/lumos:9680-9682`:新碼在逐筆迴圈跑完後另開一個迴圈,拿最終的 `revoked` 集合,對 `human_review` 且 `expires_on` 為 null 的筆回頭改狀態。
- 這同一個狀態碼現在有兩套判法:依序判,以及事後回溯並只針對一種型別。新的那套不在 `_secapr_entry_status` 裡,`_secapr_verify` 的規則清單(約 9640 起)也沒記這條。
- 建議收斂:把「null 期限的筆要拿最終撤銷集合重判」併進同一個判定點,或在規則清單與 docstring 明寫這是第二道判定。
- 回溯失效本身的語意可能是使用者有意的設計(r1 F3 的結論)。要不要接受第二套判法,請編排者裁。⚠

### 測試端:沒有另寫一套造核可或判形狀的方式
- 造核可、造撤銷用 `_SgRepo(keys=2)` 加 `add_entry("approvers_revoke", ...)`,跟 105819 和 106884 的既有寫法一樣。
- 判形狀用 `_load_lumos_inproc()` 直接呼叫 `_secapr_entry_shape`,這在測試裡有 749 處先例。
- 驗 CLI 用 `subprocess` 跑 `GRAPHCTL security approvals payload`,跟 109081 一致。
- 狀態判讀用既有的 `_sg_chain_status`、`_sg_codes`、`_sg_kind`。

### 其他
- `_SECEV_CONDITIONAL_JUDGMENTS` 加入 `not_applicable_sound`,沿用既有的條件式判斷機制。`_secev_na_judgments` 的寫法與 `_secev_format_judgments` 平行,沒有第二套。
- null 期限的放行表是 `_sec_no_expiry` 加兩個白名單常數,形狀層與 CLI 層共用。這是單一判法,沒有各寫各的。

不對齊共 2 條,其中 major 1 條
