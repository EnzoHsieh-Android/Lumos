---
type: verification
status: pass
date: 2026-08-22
valid_under: test_lumos.py runner 失敗時印「✗ FAILED <測試名>」;config test.run_cmd 帶 {method} filter
revalidate_when: 改 _kill_attribute 歸因規則、改 runner 失敗輸出格式、或 _jsonl_append_verified 重寫時
tags:
  - type/verification
  - status/pass
---
# 2026-08-22_guard-kill首次真跑

> 白話:殺傷力驗證這個機制做好兩個月,配方一條都沒人寫過、從沒跑過(gov --stats 零觸發)。今天在本 repo 自己身上跑第一輪:挑一條有綁測試的合約,宣告一個壞法,在隔離副本套進去,綁的測試要翻紅才算守得住。結果:翻紅、歸因成功。

## 怎麼跑
- 合約:Systems/canary-audit「record 回報成功 ⟺ 該行已落盤且可讀回」,綁 `t_canary_record_persist`。
- 壞法(`lumos guard kill-add`):把讀回找不到時的 `return 2` 改成 `return 0`——使用者以為記了,帳上沒有。
- 設定:`.lumos/config.json` 加 `test.run_cmd = python3 scripts/test_lumos.py -k {method}`。
- 跑:`lumos guard kill Systems/canary-audit`。

## 結果
- 第一次:`killed_unattributed`(弱證據)——測試確實紅了,但 runner 的失敗輸出裡沒有測試名,歸因器對不上。修 runner:失敗測試後印「✗ FAILED <名>(N 條斷言)」。
- 第二次:`killed`,「全部 killed(1 配方)——綁定測試咬得住」。docs/.kill-log.jsonl 有帳。
- 順帶:runner 那次改動被 pre-commit「改 code 沒動圖譜」擋下一次,補圖譜決策才過——閘有在做事。

## 限制
- 只有一條配方、只驗一條合約;證明的是機制可用,不是全部合約都守得住。
- 壞法是人宣告的,沒有自動生成;這是設計如此(從業務行為推導,不從實作反轉)。
