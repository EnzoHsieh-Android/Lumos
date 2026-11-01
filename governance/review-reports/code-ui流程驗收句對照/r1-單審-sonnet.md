severity: minor

我逐 hunk 讀完整份 diff,用 `python3.14 scripts/test_lumos.py -k android_e2e` 跑了 850 支,全綠(0 failed)。本案四個特定鏡頭走完都對得上,只剩兩條 minor。

**(a) 放行蓋得過新規則(對照 `_e2e_gate_body` 實際順序)**
- file: `scripts/lumos:42200-42215` 一帶。順序是 `_e2e_gate_load` 的讀不懂、未提交、版本比較新,接著 `_e2e_waiver_ok` 放行,最後才是 `_e2e_gate_full_note`,而新規則 `_e2e_accept_gate` 在它的最後一步。
- 有放行(人或 AI)就在放行那步直接回傳,不會走到新規則,也不印提醒。
- `t_android_e2e_gate_new_rules_order_and_waiver` 把「新規則搶到放行前面」這種改壞抓得住。

**(b) 只在整套紀錄通過那一刻判**
- `runs` 不是 dict 回 `""`,`result` 不是 pass 回「整套結果是…」,`_e2e_runs_missing` 有缺回「沒涵蓋…」,按功能的 fail 較新就先擋。
- 這四條都在 `_e2e_accept_gate` 之前,原本訊息先講。

**(c) 成因與處方**
- file: `scripts/lumos:40456-40466`,`E2E_CHECKS_FIX` 逐字對得上計劃〈成因與處方〉。
- 7 個 judge 代碼加 `no_checks_field` 各一個處方,全是工具類。
- `accept_content` 看的是 `i[2] is None`,同一次有任何內容類就不附放行指令,邏輯正確。

**(d) 既有其他擋下種類**
- `_cl_say_e2e_next` 裡新分支排在 `bad_record`、`merge_main`、`uncommitted` 之後,舊分支的訊息和指令沒動。
- 放行指令的條件只多加 `not accept_content`,舊種類不帶這個旗標,行為不變。
- 外來文字經 `_e2e_gate_out` 的 `clean` 遞迴清過巢狀 list,`accept_items` 也包括在內。

**其他新舊互讀**
- steps.json 維持 `E2E_SCHEMA=1`,範本腳本寫死 `"schema": 1`,不受影響。
- 查證紀錄 1 到 2 都收,舊程式讀 v2 走 `newer_schema`、不覆寫。
- 紀錄資料欄位型別有在 `_e2e_record_err` 驗,壞型別走 `bad_record`,不是內部出錯。

**圖譜鏡頭**
- 固定席節點(`lumos-cli-read`、`guard-kill`、`design-loop`、`lumos-cli-lifecycle`、`bound-tests-gate`、`測試假綠形態`)的 ★INVARIANT★ 都不受影響。
- 理由:diff 只動 E2E 判定與推送檢查一帶(`_e2e_*`、`_cl_say_e2e_*`)和 `_e2e_load_json` 的選填參數,碰不到 search 濾網、guard kill 的 rc 與 JSON、re-inject、設計審處置閘、bound-tests 閘。
- `_e2e_load_json` 預設值(depth=20、不限大小)沒變,其他呼叫端照舊。
- `Systems/android-e2e-acceptance` 這篇家的筆記沒放進 diff,我沒法判它寫回得對不對。
- 角色卡標了 on 但沒附卡,略過。

---

1. 判定預覽與本機總表的 `checks` 欄沒有任何測試守,拿掉也不會紅
severity: minor
blocking: 否 — 這兩處不是計劃 S1–S15 的條款,沒有「測試照綠的具體改壞會做出錯的行為或損壞資料」的證據,只是守衛缺口。
- 位置:
  - file: `scripts/lumos:41259` 與 `41638`,`_e2e_checks_preview` 兩處呼叫。
  - file: `scripts/lumos:41280`,`_e2e_checks_preview` 本體。
  - file: `scripts/lumos:42261`,`_e2e_cap` 的超過 10 條截斷。
  - `_e2e_history_append` 新增的 `**({"checks": x["checks"]["count"]} …)`。
- 引句:「_e2e_checks_preview(e2e, blocks["ui"], notices, sel["cases"])」
- 具體輸入:把按功能那條路的 `sel["cases"]` 換成 `None`,或整行刪掉。
- grep 證據:`scripts/test_lumos.py` 找不到任何斷言碰「這些流程沒有任何檢查:」「預覽;哪些會擋」,也沒有斷言本機總表 `items[].checks`,更沒有超過 `E2E_ACCEPT_SHOW` 條的案例。
- 我沒跑變異,未能重現「改壞測試仍綠」。

2. `accept` 寫在沒有 `flows` 的情境上,設定檢查通過,但推送檢查靜默不對照
severity: minor
blocking: 否 — 只影響「只列截圖的情境寫了 accept」這一種擺法,沒資料損壞,也不放行不該放行的新流程。
- 位置:file: `scripts/lumos:40659`,`_e2e_case_accept_err` 只驗 `accept` 的形狀,不要求有 `flows`。
- 引句:「if c.get("flows") and c.get("accept"):」
- 失敗場景:
  1. 新情境 `{"visual": ["home_visual"], "accept": [{"id":"A1","text":"…"}], "one_way": []}`。
  2. `--check-config` 回 0。
  3. 推送時進 `_e2e_accept_case`,`flows` 為空,`new and c.get("flows") and not c.get("accept")` 與逐句對照兩段都跳過,A1 永遠沒人對照,作者以為驗收句被強制。
- 修法:設定檢查擋「有 accept 沒 flows」,或在訊息提醒這句不會被對照。
- 計劃〈做法〉5 確實只說有 flows 的情境要逐句對照,所以是設計留的縫,不是實作偏離。
- 未能重現(沒跑指令,是讀碼推出的路徑)。

severity: minor
(全份最高)
