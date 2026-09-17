preflight-4: ran

# code-規格閘半套 r3 收貨紀錄(standard 上限第 3 輪)

- 審材 r3-delta-snapshot.patch(r2 四條折入的差異,257 行,指紋 0db645c099678398);兩席全新;外家缺席留痕。引句全數錨定、refcheck ok。

## 編排者重現
- **W1**:`_clause_grammar("當甲成立,在三秒內系統應回應,並記錄")` 在 r2 折入版回 (False, 複合觸發) → HIT。
- **W2**:`_plan_system_links` 用自寫正則+split 剝括號,`link_target()`(scripts/lumos:216)既有且做同一件事 → HIT。
- **W3**:`("若啟用", "當", "若")` 字面子集與 `_TRIGGER_WORDS` 常數並存 → HIT。

## 去重對照(W1–W3;全折)
| id | 內容 | 席 | 嚴重度 | 型 | 折法 |
|---|---|---|---|---|---|
| W1 | 「在」子句的分隔掃整個回應段,列兩件事的逗號被當複合 | 單F1 | major | code | 分隔只看「在…應」之前;測試 ⑦ |
| W2 | 剝 [[…]] 自己刻正則+split,既有 link_target 沒用 | 架構§4 | major | code | 改走 link_target;測試 ⑧ |
| W3 | 觸發詞子集另抄一份,不從 _TRIGGER_WORDS 推 | 架構§3 | minor | code | `tuple(w for w in _TRIGGER_WORDS if w != "在")` |
- 折入後又有新 delta(三處小修+兩條測試),但 standard 上限 3 輪已到:照手冊「到頂沒過→停,攤給人裁」——r3 本身的處置閘照記、照問;delta 要不要再開新迴圈由 Enzo 裁。
