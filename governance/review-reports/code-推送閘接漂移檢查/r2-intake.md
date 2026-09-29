# r2 收貨紀錄(code-推送閘接漂移檢查)

凍結材料:5a496daa..dca86f7d 的 git diff -U10(不含治理帳),833 行,不拆;`r2-snapshot.patch`。第 2 輪審第 1 輪修正本身,全新席位。
5 席:正確性 opus、邊界 sonnet 5.5、架構對齊 sonnet 5.5、資安 sonnet 5.5、外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。派工鏡頭沿用第 1 輪編排者算好的檔。

## 席位收貨

- 5 席全交,等完成通知、ls 確認後才讀;正確性席在它自己的 --shared 複製(r2op)做實驗,clone-hook 的 reflog 只有編排者與實作代理人的提交。
- report-normalize:5 份都已是正規化格式。quote-check:4 份全數錨定;資安席 clean、沒有引句(無 finding,不適用)。
- 發現 10 條(機器數):正確性 3、邊界 2、架構對齊 3、外家否決 2、資安 0;major 4 條(正確性 F1、架構對齊 F1、外家否決 F1 F2)。

## 判讀

- 同一類第二次(第 1 輪就是起點算錯):正確性 F1 F2 F3、邊界 F1 F2、外家否決 F2、架構對齊 F1 F2 都是「起點在掛鉤 bash、CI shell、健檢範本、工具端四處各算一份,各有洞」。換形狀:起點只在工具裡算一處(新函式,主線候選遠端預設分支優先、跳過被推的那條、看全部合併基底),掛鉤與 CI 只把原始範圍連同遠端名與被推的 ref 交進去;bash 與 shell 的補法整段刪掉。筆記形狀擋與每支檔有家仍走舊的共用判法,已記在 Issue「推送前其他閘的範圍在合過主線時會多算」,那兩道該改用新函式。
- 架構對齊 F1 席位自標「未能重現、結構性」仍維持 major:編排者讀掛鉤確認 bash 另有一份主線與起點算法,且正確性 F2、邊界 F1 實測兩份行為不同(工具端與掛鉤端對同一次推送算出不同起點)——採信。
- 外家否決 F1(健檢範本貼上不是合法 YAML):說明改成 YAML 註解;另兩處共用 `_CI_PY314_NOTE` 的範本有同形狀問題,不在這批,開 Issue「健檢CI範本說明貼進workflow不是合法YAML」。
- 架構對齊 F3(只有漂移這道被 Ctrl-C 中斷時停下):同輪有 major 不能放行,折入——其他閘被中斷也停下。

## 機械重現(在審的那一版 dca86f7d 上;方法:折入後的新測試格,把修法還原就翻紅,先證明舊行為)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性-F1 | 舊 CI/範本補法跑合過主線、首推頂端是合併提交 | HIT:`t_ci_drift_start_shapes` ①② 先證明舊補法 rc1;拿掉推送參數 ① 紅 |
| 正確性-F2 | 候選改回 upstream 優先 | HIT:`t_prepush_drift_start_mainline_shapes` ① 紅 |
| 正確性-F3 | 只看一個合併基底 | HIT:同上 ③ 兩種先後都紅 |
| 邊界-F1 | 候選改回 upstream 優先 | HIT:同上 ② 紅 |
| 邊界-F2 | 首推多提交、轉正在第一個 | HIT:`t_ci_drift_start_shapes` ③⑤ 先證明舊補法 rc0;舊值找不到改回空樹 ⑤ 紅 |
| 外家否決-F2 | 同邊界-F2 | HIT:同上 |
| 架構對齊-F1 | 掛鉤不帶推送參數 | HIT:`t_prepush_drift_range_ref_shapes` 12 條紅 |
| 架構對齊-F2 | CI/範本回到自己補起點 | HIT:`t_doctor_drift_ci_template_start_fallback` ②③ 紅 |
| 外家否決-F1 | 說明改回不帶 # | HIT:同上 ⑤ 紅(先證明舊範本讓斷言紅;另用 ruby YAML 解析器實際解析) |
| 架構對齊-F3 | 拿上一版(dc89b491)的掛鉤跑新測試 / 逐道拿掉停下那行 | HIT:`t_prepush_gates_stop_on_signal` 每支檔有家、筆記形狀擋、spec-gate、code-loop 四道紅(被殺掉照跑全套 rc0);逐道拿掉各自紅 |

## 處置

- 10 條全折(folded),accepted 空、refuted 空。修正在 dc89b491(起點統一、掛鉤、CI、範本、測試、筆記、兩篇 Issue)與 fc25e1e4(推送前五道「rc1 擋、其他放行」的閘被中斷時都停下)。
