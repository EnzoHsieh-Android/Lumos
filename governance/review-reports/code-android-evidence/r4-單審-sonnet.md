severity: minor

## F1 標頭或 expect 寫歪時噴 Traceback 且回 1,不是承諾的「回 2 並印擋下」
severity: minor
blocking: 否
引句:「print('擋下:收據本身寫錯——' + ';'.join(problems), file=sys.stderr)」
歸因:有證據的原有漏查。
- 標頭解析 `dict(x.split('=', 1) ...)`、`k, v = p.split('=')`、`man['artifacts']` 這幾行都不在 r4 修補差異裡,是上下文原樣。
- 修補只在這些行之後新增了兩道檢查,沒碰到它們。
- 修前沒有獨立跑。判斷依據是這幾行在兩版間相同。
- 修後的輸出見下方重現。

失敗場景:
- 收據標頭多一個沒有 `=` 的字,例如 `-- [Q1] session=a trace=t requires=- expect=a:n=1 oops`。
- 或是 `expect=a:n` 少了 `=1`。
- 或是 manifest 缺 `artifacts`,或 layers 的 `queries` 是 null。
- 這些都是「收據本身寫錯」,但腳本回 1 並噴 Python Traceback。
- 呼叫端依 reference.md 會把 1 讀成「有比對不符」,不是「收據寫錯」。
- 這正是本輪修補想消除的那一類。
- 方向是 fail-closed,不會誤判通過,所以只算 minor。

file: `scripts/templates/android-receipt-rerun.sh:19`、`scripts/templates/android-receipt-rerun.sh:55`、`scripts/templates/android-receipt-rerun.sh:11`

我複製範本跑的實測輸出:
- 標頭多一個無 `=` 的字:`rc=1`,`ValueError: dictionary update sequence element #4 has length 1`。
- `expect=a:n`:`rc=1`,`ValueError: not enough values to unpack`。這發生在 trace_processor 已經跑過之後。
- manifest 缺 `artifacts`:`rc=1`,`KeyError: 'artifacts'`。
- layers 的 `queries` 為 null:`rc=1`,`TypeError`。

新測試 `t_android_evidence_rerun_refuses_empty` 只列了 5 種壞收據,這幾種都沒列。

## F2 新 PITFALL 的根因寫錯,與現行安裝行為相反
severity: minor
blocking: 否
引句:「[根因:複製靠整目錄 rglob,登記清單與檔頭是另外兩件事]」
歸因:有證據的修復引入(新增的筆記文字)。
- 這行是修補新加的。
- 修前沒有這句,所以沒有修前結果可比。

失敗場景:
- 安裝端目前只複製 `_VENDORED_TREE_FILES` 精確清單上的檔。
- 理由寫在 `scripts/lumos:32319`:原本整目錄 rglob 的做法已被第三輪外家否決席改掉。
- 只有 deinit 還用 rglob,見 `scripts/lumos:31774`。
- 所以「沒登記就會被消費專案當自己的程式」不成立。
- 實際是沒登記就不會被複製過去。
- 下一個讀這條筆記的人會被誤導,以為放檔就會被安裝。
- 按專案規則,筆記與程式不符時以程式為準,這條只是線索。

## 已驗主張與未驗範圍

**三問**
- ① 原問題的修復效果,行為證據如下。
  - 指到不存在的 artifact:`trace=zzz` 或缺 `trace` 時,回 2、stderr 以「擋下:」開頭、沒有 Traceback。
  - requires 指到不存在的查詢:`Q7` 與空字串(尾逗號)都回 2。
  - 重複標頭回 2。
  - 以上都是我親手跑出來的結果。
  - 範本已登記進 `scripts/lumos:31928`。
  - 授權檔頭已補上,也是我讀程式確認的。
  - 安裝與更新的複製迴圈會保留執行權限,見 `scripts/lumos:32325`。
  - 我沒有跑 `t_vendored_file_list_matches_what_install_ships`,所以「修前紅、修後綠」我沒有獨立驗。
- ② 修補處的相鄰路徑。
  - 我用假 trace_processor 驗過,四個全對的收據仍走到比對階段。
  - 我沒有做修前版本的逐案對照,這部分標未判定。
  - `expect=-` 的查詢也會被檢查 trace,這是合理行為。
- ③ F1 的同一案例,修前修後結果相同。
  - 這是依程式讀出來的,沒有兩版實跑。
  - F1 因此判為原有漏查。

**本案特定鏡頭(消費專案行為)**
- `lumos update` 只比對 `scripts/templates/` 底下那份。
- 使用者複製進 `.lumos/receipts/<id>/rerun.sh` 的那份不在清單內,不會被覆蓋。
- 但 `_vendored_state` 只按精確路徑跳過。
- 收據目錄那份 rerun.sh 因此會被當專案自己的程式。
  - 我在臨時 git repo 實測:沒設 ignore 時,`lumos pitfalls` 判 tier=high,並指出 `open(` 兩處。
  - 加上 `{"node_home":{"ignore":[".lumos/receipts/*"]}}` 後變 light、0 claims。
- 這個 ignore 設定已寫在 SKILL.md 第 128 行,所以我不另立 finding。
- 這個副作用是「要先設 ignore」的前置條件。

**未驗範圍**
- 整份 skill 的 SKILL.md 內容。
- `lumos macrobench` 的門檻、基準、`_macrobench_num`。
- 圖譜鏡頭的固定席(派工說明範圍算不出來)。
- 全套測試。

總結:這份報告最高嚴重度是 minor
