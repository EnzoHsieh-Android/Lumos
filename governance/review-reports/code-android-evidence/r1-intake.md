preflight-4: ran

# code-android-evidence r1 收貨

審材:r1-snapshot.patch(1203 行,從工作樹凍結;工作樹比 HEAD 3461928852b20eb0e216f9b15fa649c982444b48 多一行測試變數改名)。
兩席:單審-sonnet(9 條)、架構對齊-sonnet(3 條)。兩席都交回後才一起存檔與處理。
單審席第 4 條引句內包「」錨不回,請該席自己補正那一行,存成 r1-單審-sonnet-引句更正.md 當載體(原檔保留;除引句外只差一字「第 4 條→第 4 點」)。
圖譜鏡頭:派工時會談專案(Backend_improve)算不出這個工作樹的範圍,hook 附「範圍算不出來」說明、沒有固定席;單審席照備援只就 diff 碰到的節點判定。

## 引句錨不到的兩條(不改席位引句,機械重現)

| id | 錨不到原因 | 重現 | 判定 |
|---|---|---|---|
| S4 | 引句內又包「」被截斷 | 照席位說的兩種改壞(編號一律報最後一條、讀檔時的 stat 檢查拿掉)套到 scripts/lumos 副本,`-k macrobench_threshold_bad_file` 15 passed 0 failed | HIT |
| A1 | 引句跨兩行 | `_macrobench_threshold_item_err` 內有 `import re`,scripts/lumos 第 59 行已在模組層匯入 | HIT |

## 逐條重現與去向

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| S1 | major | 門檻 `max: NaN`、現值 3.6 → `threshold_passed` 1 條、`threshold_failures` 0 條 | HIT | 折:macrobench 讀數字一律只收有限數(門檻、設定容差、基準、結果檔四處同族一起改),新測試 t_macrobench_rejects_nonfinite |
| S2 | major | queries.sql 最後一條漏分號 → 範本 rerun.sh rc=0 | HIT | 折:標頭數與解析條數不同、沒有任何 expect、manifest 列了不存在的 Q 都回 2,新測試 t_android_evidence_rerun_refuses_empty |
| S3 | major | 暫存目錄只放 macrobench.json → `threshold_*` 三欄全空 | HIT | 折:SKILL L0 第 5 步寫明要複製門檻檔 |
| S4 | major | 見上表 | HIT | 折:t_macrobench_threshold_bad_file 補「壞的排第 1 條」與「stat 錯且情境沒跑到仍 rc2」;同兩種改壞重跑已紅 |
| S5 | minor | `decided_at: 2026-13-45` 可載入 | HIT | 折:改驗真的日期,測試補案例 |
| S6 | minor | 摘要行一定印「N 條沒判」,`"沒判" in stdout` 恆真 | HIT | 折:改成數 `[沒判]` 行數並確認沒有 `[沒達驗收門檻]` |
| S7 | minor | `_macrobench_collect` 解析與算雜湊各讀一次檔 | HIT | 折:只讀一次 bytes,同一份解析與算雜湊,讀檔包進 try |
| S8 | minor | reference.md 寫「L0 第 4 步」,實際是第 5 步 | HIT | 折 |
| S9 | minor | expect 的第一欄值含冒號、逗號或是數字會誤判 | HIT | 折:reference.md 寫明限制與取字串別名的做法 |
| A1 | minor | 見上表 | HIT | 折:拿掉函式內的 import re |
| A2 | minor | `_mb_thr_root` 說明寫回三個值、實際四個 | HIT | 折 |
| A3 | minor | skill 的 reference.md 附 rerun.sh 範本,其他 skill 沒有可執行檔 | HIT(⚠ 席位判不準) | 折:同輪有 major,minor 也不得放行;把「範本以文字放在 reference.md、skill 目錄不放可執行檔」寫成 Android逐層診斷_計劃 的 WHY 行(定成這個 skill 的慣例並記不選的理由) |

## 同族掃描

- S1:`_secev_num` 在 macrobench 區塊的四個呼叫點(設定容差、結果檔 metrics 與 sampled、基準 entry_ok、門檻)全部換成 `_macrobench_num`;資安證據閘自己的 `_secev_num` 不動(範圍外,行為不同)。
- 順帶結清 Systems/macrobenchmark-adapter 原有的 NaN 回頭條件(2026-12-21)。

## 修補因果

r1 是首輪,沒有上一輪修補,regression_set 不適用。
