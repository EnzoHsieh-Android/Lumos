severity: major

## F1 非 main/master 的預設分支在 Actions 缺少 remote HEAD 時會誤算檢查範圍

severity: major  
blocking: 是  
引句:「cands = ([f"refs/remotes/{remote}/HEAD"] if remote else []) + ["main@{upstream}", "master@{upstream}"]」  
file: `scripts/lumos:33128`  
file: `.github/workflows/ci.yml:165`  
file: `scripts/test_lumos.py:51341`  
file: `scripts/test_lumos.py:51489`

1. `_push_mainline()` 只透過 `origin/HEAD`、main/master upstream、以及遠端 main/master 尋找主線。若 GitHub 專案的預設分支是 `develop` 或 `trunk`，而 checkout 沒建立 `origin/HEAD`，即使 `origin/develop` 已存在也完全不會被查詢。

2. 這正是 GitHub Actions 可能出現的形態：`actions/checkout@v4` 搭配 `fetch-depth: 0` 曾被確認不建立 `origin/HEAD`，見 [actions/checkout #2219](https://github.com/actions/checkout/issues/2219)。本批測試輔助函式也明載 Actions 不設定 remote HEAD，但 develop/trunk 測試隨後手動建立該 symbolic ref，因此沒有覆蓋真正的 Actions 前置條件。

3. 已用純函式替身做唯讀重現：

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c 'import runpy; m=runpy.run_path("scripts/lumos"); old,tip,parent,develop="1"*40,"2"*40,"3"*40,"4"*40; seen=[]; refs={old:old,tip:tip,f"{tip}^1":parent,"refs/remotes/origin/develop":develop}; full=lambda _root,rev:(seen.append(rev),refs.get(rev))[1]; m["_push_mainline"].__globals__["_lens_full_sha"]=full; m["_push_range_start"].__globals__["_lens_full_sha"]=full; print("mainline=",m["_push_mainline"](".","origin","refs/heads/feat")); print("looked_up=",",".join(seen)); seen.clear(); print("merge_after_develop=",m["_push_range_start"](".",old,tip,"origin","refs/heads/feat")); print("force_push_old_missing=",m["_push_range_start"](".","f"*40,tip,"origin","refs/heads/feat"))'
```

輸出：

```text
mainline= None
looked_up= refs/remotes/origin/HEAD,main@{upstream},master@{upstream},refs/remotes/origin/main,refs/remotes/origin/master
merge_after_develop= ('1111111111111111111111111111111111111111', '找不到主線(遠端預設分支、main/master 的 upstream、遠端 main/master 都沒有,或就是這次推的分支),用遠端舊值 111111111111 當起點')
force_push_old_missing= ('3333333333333333333333333333333333333333', '找不到主線(遠端預設分支、main/master 的 upstream、遠端 main/master 都沒有,或就是這次推的分支),遠端舊值在本機找不到:從頂端的第一個父提交 333333333333 算,只查最後一個提交')
```

4. 誤擋路徑：功能分支合入最新 `develop` 後，程式仍從遠端舊功能提交開始掃描，`develop` 上別人的轉正會被算成這次推送；block 模式因此可能阻擋正常推送。既有測試在 `scripts/test_lumos.py:51505` 已證明這個較寬範圍會報錯，只因測試手動建立 `origin/HEAD` 才改用正確範圍。

5. 漏擋路徑：force push 的舊 SHA 不在 checkout 中時，由於仍找不到主線，程式退化成只查頂端第一個父提交；多提交推送中較早提交的漂移會被漏掉。`scripts/test_lumos.py:51633` 的既有案例已證明此退化範圍會漏過較早的漂移提交。

6. 放行前應讓 Actions 明確建立 remote HEAD，或從遠端預設分支资料解析主線；並新增「remote HEAD 缺失、預設分支為 develop/trunk」的 CI 形態測試，不能由測試自行補上待驗證環境原本缺少的 symbolic ref。

## 圖譜鏡頭逐條判定

1. `Issues/code-loop守衛main-direct盲區`：未受直接影響；本洞位於 drift push-range 起點，不是 code-loop 的既有 per-ref `_range`。
2. `Systems/存量漂移守衛`：受影響。缺少 remote HEAD 時無法兌現「不把主線上別人的變更算進本次推送」，且 CI 與本機可能得出不同範圍。
3. `Systems/每支檔有家`：未發現本批修改破壞 home range 判定；相關變更集中於中斷訊號處理。
4. `Systems/筆記內容閘`：未發現 note-shape 判定或範圍邏輯的新破壞。
5. `Systems/測試假綠形態`：受影響。測試先手動建立 Actions 實際可能缺少的 `origin/HEAD`，使 develop/trunk 覆蓋形成假綠。
6. `Systems/anchor-integrity`：未受影響；唯讀執行 `lumos anchor verify` 顯示 12 個驗證器均與基準線一致。
7. `Systems/lumos-cli-lifecycle`：未發現 re-inject 或 sentinel 合約變更。
8. `Systems/lumos-cli-read`：未發現 search、stale 或 superseded 行為變更。

最高等級:major