# 審查跑滿回顧 r2 收貨紀錄(2026-10-05)

編排者:claude(接手自 Hook Refactor 會談,Enzo 2026-10-05 指派)。凍結快照 `r2-snapshot.md`(sha256 23132647…)。四席:正確性、邊界、整合、架構對齊;外家否決席依 Enzo 指示不派。

## 收貨三道

- 四份報告 `quote-check` 對 `r2-snapshot.md`:全數錨定(正確性 8 句、架構對齊 4 句、整合 7 句、邊界 12 句)。
- 報告引的 file:line 由編排者抽查重現(見下表),跟 `scripts/lumos`(本分支 HEAD 7e96fc89)一致。

## 編排者重現(佐證通道)

| id | 命令 | 結果 |
|---|---|---|
| c1/i1/b2 | `sed -n 13246,13249p scripts/lumos`(loop next 在 rounds_count>=cap 寫 cap-reached)、`grep -n '"cap-reached" in k' scripts/lumos` | HIT:每問一次寫一筆、不會抹掉;gov --stats 有排除 converged/rewrite 的口徑 |
| c3/a3/b5 | `sed -n 971,980p scripts/lumos`(`_loop_gov_mark` except 全吞)、`sed -n 1445,1470p`(`_gate_event` 回傳值要被看) | HIT |
| c4 | 讀 `_gov_row` 去重鍵(本輪改成直接讀原始 jsonl,不再依賴) | HIT(採信席位所述,設計已避開) |
| c6/b7 | `sed -n 22477,22495p scripts/lumos`(`_disposal_round_groups` 錯誤分支)、`sed -n 12943p`(loop next 集合計數) | HIT |
| a1 | `sed -n 1300,1340p scripts/lumos` 中 `ev.update(extra)` | HIT:extra 併進事件頂層,可放結構化欄位 |
| a2 | `sed -n 9500,9516p scripts/lumos`(canary 寫側擋下都落 blocked 加隨機碼) | HIT |
| a4 | `sed -n 7938,7960p scripts/lumos`(`_KNOWN_GATES` 有 `fix-check` 自成一閘的先例)、`t_gov_stats_gate_drift` | HIT |
| i5/b9 | `sed -n 1053,1075p scripts/lumos`(凍結第一趟 readonly=True 無 override;第二趟帶 override) | HIT |
| i6 | `grep -n "def _intake_dir_status" scripts/lumos` | HIT |
| b6 | `sed -n 12258p scripts/lumos`(`_FIX_ID_BAD_RE`)、`sed -n 1040,1042p`(replay 只擋三種) | HIT |

## 逐條去向(26 條,全部折入;放行 0;重現不到 0)

觸發改成人裁紀錄(決策 d6,Enzo 2026-10-05)之後,多數發現的前提消失,折入方式是改寫〈名詞〉〈適用範圍〉〈三〉〈條款〉,並記決策 d7(取代 d5)。

| id | 席 | 嚴重度 | 一句 | 去向 |
|---|---|---|---|---|
| c1 | 正確性 F1 | major | cap-reached 後又 converged 被算跑滿 | 折入:觸發不再看 cap-reached |
| c2 | 正確性 F2 | major | 3 輪不開第四輪的人裁沒有擋點 | 折入:accept-risk 記人裁,擋不到的寫進〈三〉與〈誠實界線〉,doctor 列出 |
| c3 | 正確性 F3 | minor | `_loop_gov_mark` 寫不進去仍回成功 | 折入:改 `_gate_event`,寫不進去回 1 |
| c4 | 正確性 F4 | minor | gov 載入器去重會取到舊筆 | 折入:直接讀原始 jsonl、檔內順序 |
| c5 | 正確性 F5 | minor | 跳過永久有效 | 折入:跳過綁最新人裁紀錄 |
| c6 | 正確性 F6 | minor | 共用函式遇亂序帳回錯而放行 | 折入:輪數改集合計數;帳壞時有人裁紀錄的迴圈 fail-closed |
| a1 | 架構 F1 | major | 指紋塞 note 字串 | 折入:結構化欄位 `retro_sha256` |
| a2 | 架構 F2 | minor | 寫側擋下沒落 blocked | 折入:落 `canary blocked` |
| a3 | 架構 F3 | minor | 同 c3 | 折入:同 c3 |
| a4 | 架構 F4 | minor | 事件名與閘名歸屬不齊 | 折入:新閘名 `loop-retro`(照 fix-check),kinds `cap-decision`/`recorded`/`skipped` |
| i1 | 整合 F1 | major | 同 c1,另 cap-reached 九十月零筆 | 折入:同 c1;零筆的事實寫進〈為什麼要做〉 |
| i2 | 整合 F2 | minor | 閘、doctor、統計對「有回顧」定義不同 | 折入:單一合格回顧判定,統計另列過期 |
| i3 | 整合 F3 | minor | 每多一輪要重寫回顧、跳過卻永久 | 折入:回顧與跳過都綁人裁紀錄,破例輪不使回顧失效;懸空引用一併改寫 |
| i4 | 整合 F4 | minor | 沒有現成條號辨識可抽 | 折入:拿掉條號與原 S13 |
| i5 | 整合 F5 | minor | 凍結第一趟會印 FAIL | 折入:凍結第一趟帶參數略過第八步 |
| i6 | 整合 F6 | minor | 為暫存迴圈建資料夾改變既有判斷 | 折入:沒有卷證資料夾不適用、不代建 |
| i7 | 整合 F7 | minor | `_cap_hint_scope` 已存在 | 折入:敘述更正,不再說「抽出」 |
| b1 | 邊界 F1 | major | r3b 例行複核輪被誤擋 | 折入:觸發不再看輪數 |
| b2 | 邊界 F2 | major | 同 c1+c2 | 折入:同 c1、c2 |
| b3 | 邊界 F3 | major | 上線時刻時區比較 | 折入:觸發是新事件,不需上線時刻、不比時間戳 |
| b4 | 邊界 F4 | major | 合格回顧與 S3 矛盾、跳過永久免疫 | 折入:合格回顧改成「最新人裁之後最新一筆」 |
| b5 | 邊界 F5 | major | 寫帳失敗無聲、指紋無處放 | 折入:同 c3、a1 |
| b6 | 邊界 F6 | minor | 編號檢查太弱 | 折入:`_FIX_ID_BAD_RE` 加空字串與 `.`;大小寫碰撞寫進實務隱患(已排除理由) |
| b7 | 邊界 F7 | minor | 壞帳三呼叫端怎麼辦 | 折入:新路徑接住;有人裁紀錄才 fail-closed |
| b8 | 邊界 F8 | minor | 證據路徑正規化與不存在的報告 | 折入:正規化、檔要存在、拿掉條號 |
| b9 | 邊界 F9 | minor | 凍結判定不涵蓋第八步 | 折入:〈三〉2 與〈誠實界線〉明寫 |

另:b4 內文指出退場條件②「跳過次數多過回顧次數」沒定義單位、i1 內文指出③要重量——併入 b4、i1 的折入:②改成以迴圈計、只算已記回顧(不含跳過),③改成三個月內零筆人裁紀錄。

finding-kind:全部 `spec`(被審文件缺陷)。

## 本輪結論

r2:26 條/blocking 9(正確性 2、架構 1、整合 1、邊界 5)/全部折入。觸發改人裁紀錄後擋點與合格回顧重做,見計劃〈審計修正紀錄〉r2 與決策 d7。

## 折入後鏡像核對

派一個 sonnet 只看本輪 diff 與席報告目錄,找到 15 處前後不一致,14 處已改:blocking 數改 9(邊界 5,編排者原本數錯);退場條件②③的折入補進上面「另」那段;「共用函式遇亂序帳」從自然消失改列折入;守衛面寫明 accept-risk 擋下的出口是改記 extra-round;帳壞 fail-closed 補條款 S17;狀態分「已記回顧/已跳過/過期/沒有」,統計與退場條件講已記回顧不含跳過;REVISIT 的對照基準改成輪數 ≥ 上限的迴圈數;事件帳樣本寫明不進治理帳;代碼審看不到 loop next 提示補一句;r1 段加「已被 r2 取代」說明;回退補手冊還原;效能句改正;S7、S10 補缺分支;兩種擋下分原因碼。
沒改的 1 處:決策 d2 代價寫「每次跑滿多派一個代理」,用詞是舊的,但意思(要回顧時多派一個起草代理)仍對;有效決策內文只能翻案改,為用詞翻案不值得。
