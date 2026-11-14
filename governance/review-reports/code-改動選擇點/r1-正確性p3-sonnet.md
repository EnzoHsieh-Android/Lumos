severity: minor

## c31 gov --stats 的選擇點段吃的是未去重的原始列,與函式說明和新加的去重鍵不符
severity: minor
blocking: 否 這會讓統計數字偏高,但不影響推送閘的判定,屬統計精度問題。

- **輸入:** 治理帳裡有兩行逐字相同的 `choice-kill` 事件,或兩行相同的 `lint-new waived scope=choice-kill` 事件。例如衝突解決時選了「兩邊都留」。
- **路徑:** `cmd_gov` 把 `_raw`(沒去重、沒排序)傳給 `_render_gov_stats`,它再呼叫 `_render_gov_choice(rows)`。
- **實測:** 用 `_stats_fixture` 風格的最小 vault,帳裡放 `[survived, survived, waived, waived]`,同一個 `token:T1`。執行 `lumos gov --since 9999 --stats`,輸出:

```
第一次跑殺掉率 0/2(0.00)
存活處置:寫回規格 0、補測試後殺掉 0、放行 2(不適用 2)
```

預期是 0/1 和 放行 1。
- **牽連:**
  - `_gov_choice_counts` 的說明寫「rows 是去重後的統計列」,實際收到原始列。
  - 這次在 `cmd_gov` 新加的 waived 去重鍵 `f"{file}:{fp}"` 只影響 `ded`(時間軸),對 stats 段無效。
  - 這一段的順序判定(`ever` 要先出現 survived,killed 才算「補測試後殺掉」)也依賴未排序的檔案順序。

引句:「_raw = [r for r in rows if (not node) or stem(node) in r["nodes"]]」

file: `scripts/lumos:18617`(呼叫端傳 `_raw`)、`scripts/lumos:17904`(`_gov_choice_counts` 說明)

## c32 回報上限的種子把放行過的行排除在外,放行一行會讓原本沒抽中的行變成要擋
severity: minor
blocking: 否 不會放過該擋的東西,但「處置一條、仍剩同樣條數要擋」的行為違背穩定回報的意圖,屬使用體驗問題。

- **輸入:** 同一個檔有 8 行曾經存活(都沒處置),上限 7。
- **路徑:** `_choice_push_judge` 對 `waived` 的行先 `continue`,所以放行的行不進 `ever`。`_choice_cap_pick(ever, cap)` 的種子是 `ever` 集合的雜湊,集合一變就整批重抽。
- **實測:** 用 `_choice_push_judge` 單元重現:
  - 放行前:擋第 1、2、3、4、5、6、8 行,第 7 行沒抽中(只提醒)。
  - 放行第 1 行後:擋第 2、3、4、5、6、7、8 行,仍是 7 條。
  - 原本只提醒的第 7 行變成要擋,擋下條數沒有因為處置而減少。
- **對照:** `_choice_cap_pick` 的說明只保證帳本提交、rebase、上限變大不換抽中的行。放行也會改集合,這個保證沒涵蓋。把放行過的鍵也算進種子集合,只對「要不要擋」排除,就不會重抽。

引句:「if key in waived:
            continue」

file: `scripts/lumos`(`_choice_push_judge` 與 `_choice_cap_pick`,在 patch 約 821–849 行與 807–818 行)

## 圖譜鏡頭與其他逐項判定

這次沒附固定席筆記,以下是我自己查 repo 現況後的判定。

- **不影響,新舊互讀:**
  - 新掛鉤配舊 lumos:探針 `grep dest="sg_push_remote"` 與 `dest="sg_pushed_ref"` 兩個都要在才帶參數,舊版不帶,規格閘其他圈照跑。
  - 新 lumos 配舊掛鉤:`push=None`,範圍用推送範圍本身。
  - `${_sg_extra+"${_sg_extra[@]}"}` 與同檔第 47 行既有寫法一致。
- **不影響,被推版本:** 帳走 `_gov_rows_at(rr, at_sha, …)`,放行檔走 `_residual_blob_at`,計劃與檔走 B 版樹,不讀工作目錄。放行檔讀不了不會當成沒有放行或全放行。
- **不影響,生效日:** `_choice_push_round` 先判生效日,晚於今天整圈不跑,既有推送不受影響。日期用本機時間,與 `_choice_requirement` 同一種比法。
- **不影響,帳分流:** `choice-kill` 不在 `_GOV_LOCAL_PAIRS`,blocked 與 unverified 事件進版控帳,去重讀得到。
- **不影響,killing_test 加平台前綴:**
  - 舊紀錄(沒前綴)靠 `plat == default` 另收一份不帶前綴的名字,算預設平台。
  - `_choice_killing_name` 與 `_choice_bound_names` 都走 `_split_test_ref_ex`,兩端口徑一致。
- **不影響,`_gov_event_types_ok`:** 新登記的 `label`、`decl` 欄位只有 `lint-new waived` 帶,沒有別的閘用同名欄位,不會誤丟舊事件。
- **不影響,`_sc_changed_files` 當回報上限的檔數:** 純刪除、純改名(增行 0)不算;二進位算。
- **其他:** 論文的一行一個壞法、乾節點、回報上限 ×7、穩定回報,實作大致照做。回報上限的瑕疵只有 c32。

我沒找到未被接住的例外路徑,也沒找到會讓推送閘做出錯誤擋放的路徑。

臨時目錄已用字面絕對路徑刪除(`/private/tmp/lumos-seat-work/code-改動選擇點/正確性p3-sonnet`)。

最嚴重:minor;blocking 共 0 條
