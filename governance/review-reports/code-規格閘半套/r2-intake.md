preflight-4: ran

# code-規格閘半套 r2 收貨紀錄

- 審材 r2-delta-snapshot.patch(r1 七條折入的差異,389 行,指紋 109ac89ca4d41384);兩席全新;外家缺席留痕。兩席引句全數錨定、refcheck ok。
- r1 的處置集合被閘擋回(code 迴圈輪內有 major 就不准附理由放行):X4/X7 在 r1 折入提交裡一併折了;本輪 r2 又把 X4 的折法(自建 Setext 判定)打回,改成只認 ATX。

## 編排者重現
- **Y1**:`_clause_grammar("當甲成立,若乙為真系統應回應")` 在 r1 折入版回 True → HIT。
- **Y2**:`_rollback_section_chars("回退\n```python\nfoo = 1\n```\n---\n無關文字…")` 回非 None → HIT(fence 錯配);`回退\n===` 也被當二級 → HIT。
- **Y3**:`_lens_contract_rows` 仍三支 if/elif → HIT。
- **Y4**:`_plan_system_links` 對 `lands_in: "[[Systems/Alpha]]"` 回 [] → HIT。

## 去重對照(Y1–Y4;全折)
| id | 內容 | 席 | 嚴重度 | 型 | 折法 |
|---|---|---|---|---|---|
| Y1 | 複合觸發判準太鬆:第二個觸發詞後沒逗號就放過 | 單F1 | major | code | 第二個 當/若/若啟用 一律複合;「在」要帶分隔才算;測試 ⑤ |
| Y2 | Setext 判定:fence 錯配、H1/H2 不分、跟 KEY 行矛盾、是第二套標題邏輯 | 單F2/F3/F4、架構§3(major+minor) | major | code | 整段拿掉,只認 `## 回退`,擋下訊息提示寫法;測試 ④ 改成不認 |
| Y3 | `_lens_contract_rows` 沒收進 `_contract_key_matches` | 單F5、架構§4 | major | code | 加 with_kind 一起走 |
| Y4 | lands_in 寫成 `[[…]]` 字串被濾掉 | 單F6 | major | code | lands_in/related 一起剝括號;測試 ⑥ |
