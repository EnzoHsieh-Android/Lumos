severity: clean

這輪修補跟鄰居的做法一致,沒有新增的不對齊。下面逐問答。

**1. 分層與依賴方向**

`_spec_gate_front` 裡三個子步驟的呼叫形狀現在一樣:`pq_rc = _spec_gate_pending(...)`、`rc, rows_b = _spec_gate_clause_part(...)`、`ex_rc = _spec_gate_expected_part(...)`,都是先取回傳值,非 None 就提早收。

讀帳失敗的備援改用 `_SPEC_GATE_PUSH_LEDGER_TAG`,它是 `scripts/lumos:16544` 既有的常數。同一支檢查的上游讀治理帳失敗處(`scripts/lumos:16498`)也用同一個標籤,標題由 `_spec_gate_push_bad_head`(`scripts/lumos:16585`)統一判讀,所以沒有新增跨層呼叫。

cmd_gov 的 token 條件鏈接在既有的 fix-check 分支之後,位置和寫法都跟 `scripts/lumos:17335` 附近的鄰居分支一致。

引句:「ex_rc = _spec_gate_expected_part(env, rel, text, door)」
對照:`scripts/lumos:15388`(`_spec_gate_pending` 回 1/None)、`scripts/lumos:15210-15226`(`_spec_gate_clause_part`)

**2. 命名與錯誤處理**

- **回傳慣例**:`_spec_gate_expected_part` 從 True/False 改成 1/None,docstring 也寫明「同 _spec_gate_pending」,與 `_spec_gate_pending` 一致。
- **訊息標籤**:新備援訊息「治理帳讀不到(…),判不了 …」與 `scripts/lumos:16498` 同一個「治理帳讀不到」句型,標籤相同。
- **token 條件鏈**:`str(d.get("token") or "") if (d.get("gate"), d.get("kind")) == ("signoff", "expected-signed")` 接在 fix-check 之後當新分支,`origin` 則另用一個條件式欄位,跟其他欄位逐欄 `if` 的寫法一致。
- **CHANGELOG v1.5**:開頭句式「…所以升版,讓還沒更新的專案被提示跑 `lumos update`:」加上粗體條目,與 v1.4 相同,日期格式也沒變。v1.4 多了一句「其餘改動…照常更新即可」,v1.5 沒有。這是內容取捨,不是做法不同,不列。
- **手冊表格列**:`03-寫回圖譜.md` 那一列沿用同檔其他列的 `\|` 跳脫(例如 `05-設計審查迴圈.md` 的 `--tier standard\|high\|light`)和四欄結構。INDEX 與 05 的修改也都是在既有列的原儲存格內延伸。
- **版號**:`LUMOS_VERSION` 改成 v1.5,與 CHANGELOG 標題、各注入區塊的 v1.5 同步。

引句:「return f"{_SPEC_GATE_PUSH_LEDGER_TAG}治理帳讀不到({gerr}),判不了 {prel} 的預期值表簽核;修好帳檔權限或路徑再推"」
對照:`scripts/lumos:16498`、CHANGELOG.md 的 v1.4 條目

**3. 第二種做法**

沒有引入新做法。修補用到的都是專案現成的東西:既有標籤常數、既有的 `check()` 測試風格,以及 `_spec_gate_push_bad_head` 的標題分流。指紋釘值測試跟其他「釘值」測試同類。

引句:「check("S3 指紋算法釘住:範例那一列的指紋是固定值",」
對照:`scripts/lumos` 裡 `t_door_rule_version_pin` 一類的釘值測試

小觀察,不列為 finding(判斷屬純風格):新增的 done 計劃測試掛在 `t_push_check_expected_scope`(S9)裡,檢查標籤卻寫成「S7」,編號與所在函式不一致。

不對齊共 0 條,其中 major 0 條。

總結:全份最高 clean
