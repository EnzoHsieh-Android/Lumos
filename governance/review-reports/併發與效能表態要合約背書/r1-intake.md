preflight-4: ran

# r1 收貨紀錄(併發與效能表態要合約背書)

## 首輪前掃(sonnet,固定清單四項)

①②③:詞未定義三處(強證據、推送版本、次數型)→ 在〈做法〉開頭補用詞定義;壞引用 0;範圍矛盾 0。

④ 語意類命中,已修真檔(修改前 → 修改後),均不在核心裁定節:

1. 緣起「併發那一席不是必到席,缺席只提醒」未驗證 → 改寫成 `_TIER_ROSTER` 註解的原意:只有資安席必派且處置閘會擋,其他鏡頭席缺席只提醒(已對 `_TIER_ROSTER` 註解原文)。
2. 做法 1「每條配方判完」寫治理帳 → 現行 `.kill-log.jsonl` 是迴圈外批次寫;改成「在同一處為每條配方各寫一筆」,並指名用 `_gate_event_or_warn`。
3. 「鍵名不用 gate」的理由錯:既有註解指的是回傳 dict 的 mode 鍵,磁碟上 JSON 鍵本來就叫 `stack_questions.gate` → 刪掉錯誤理由,改寫成新鍵與 `stack_questions.gate` 並列;「印一句」改成照慣例放進 warnings、由 code-loop check 印。
4. 「閘內部錯誤走 `_gate_failopen`」過度簡化:`_dispositions_verdict` 單題錯誤現行是擋下,只有外層例外與超時 fail-open → 改寫成分層處理。
5. 派工鏡頭「只改附加文字」不成立:`_lens_dispositions_lines` 只讀表態標記不讀治理帳,`_lens_cache_path` 快取鍵不含背書狀態 → 補寫要多讀治理帳、共用判定函式、快取鍵納入背書狀態。
6. tension 選 suggested 時的 evidence 走同一條驗法,文中沒交代 → 明寫 v1 不要求背書。

未驗證但保留:「guard kill --json 恰一行」的既有合約文字 —— spec-gate 相依回歸已從 [[Systems/guard-kill]] 抽出該 ★INVARIANT★ 並跑綠 t_guard_kill_json_purity,視為已驗。

## 收貨三道(六席)

- report-normalize:六份皆已是正規化格式。
- quote-check(對 r1-snapshot.md):六份全數錨定(正確性 15、邊界 16、整合 24、資源併發 17、簡化 4、架構對齊 16 條引句與佐證)。
- refcheck:六份報告引的 file:line 全部存在。
- seat-check:五份報告「unreported r1.md」——報告大量逐字引用 r1.md 但沒寫出路徑字串,屬字串比對假陽性;out_of_scope 皆 0。只觀測不擋。

## 編排者重現(採信前自己查過)

| 群 | 席位 id | 重現 | 結果 |
|---|---|---|---|
| 閘名不在名單 | C7 B1 R3 I1 A3 | `_KNOWN_GATES` 名單有 kill、code-loop,無 guard-kill/contract-evidence | HIT 採信 |
| gate=off 提早結束 | B8 A5 | `_dispositions_verdict` 開頭 mode==off 或 high-only 非 high 即 return | HIT 採信 |
| kill-log commit 只記最後一組、test 為原始配方值 | C5 B2 R2 | `cmd_guard_kill` 寫 kill-log 處 commit 為迴圈外單一變數、test 取 res.get("test") | HIT 採信 |
| meta 沒有 evidence 欄 | I7 | `_stack_applicability` rows 只有 id/question/applicable/triggered_by;另有 `_stack_spec_by_id` | HIT 採信 |
| 鏡頭只讀 marker 的既有決策 | A1 | Systems/棧別提問表態閘 FLOW/KEY 行;`_lens_dispositions_lines(lines, rec)` | HIT 採信 |
| 表態失效沿用 `_codeloop_record_valid` | A2 | 函式存在,表態與 pass 共用 | HIT 採信 |
| gov 已按題目 id 統計表態狀態 | P1(量法) | gov 讀 kind=dispositions 事件逐題累加 satisfied/na/todo/tension | HIT 採信 |
| 本 repo 八題觸發 0 次 | P1 | 席位實數,未另外重數,改寫進計劃時標明出處 | 採信 |

refuted-set:none。
