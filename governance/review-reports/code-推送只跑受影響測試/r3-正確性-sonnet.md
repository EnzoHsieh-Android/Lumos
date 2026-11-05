severity: clean

沒有找到會擋的問題。下面說我驗了什麼、沒驗什麼。

**驗過的**
- **相關測試實跑全綠:** `t_pitfalls_pushed_mainline`(9 項)、`t_pitfalls_suite_computed`(4 項)、六支 `t_prepush_feature_branch_*` 加 `t_prepush_docs_and_light_run_subset`(合計 22 項)都通過。命令是 `python3.14 scripts/test_lumos.py -k <關鍵字>`,在 repo 根跑、沒改任何檔。
- **`_down` 改名沒有殘留:** `scripts/hooks/pre-push` 裡 `_down` 只在兩處被讀:定義與賦值那段,和 `if [[ -n "$_down" ]]` 共用關鍵字那段。兩處都已改成 `spec_light` / `feature_branch`,沒有 `"light"` 或 `"branch"` 舊值的比較。`_SUITE_BRANCH_DOWN` 只在 `feature_branch` 那條設。
- **多 ref 合成:**
  - 混推 main 與功能分支時,main 那個 ref 設 `_SUITE_FULL=1`,整次推送走全套,也不印降級那行。
  - 功能分支加純文件時,走 light 並印一次說明。
  - 原本就判 light 的 ref 不設 `_SUITE_BRANCH_DOWN`,不印降級說明。
  - 執行器不認得 `--suite` 或 `--graph` 時退回全套,此時降級說明不會印出來(只在最終模式為 light 時印)。
- **目的地與本機名不同名:** `--pushed-ref` 傳的是 `$_rref`(遠端 ref)。`feat:main` 判主線,`main:feat` 判功能分支,兩者都有測試。
- **刪除分支:** `_lsha` 全零直接 `continue`,不進判定。
- **標籤與非 `refs/heads/` 的 ref:** `_pitfalls_pushed_mainline` 回 true,走全套(偏安全)。
- **新分支首推:** `_brange` 來自 push-range。push-range 失敗時退回空樹範圍,會碰到守衛檔,最後仍是全套。
- **舊版 lumos:** 掛鉤先讀檔找 `dest="pf_pushed_ref"` 字樣,找不到就不帶旗標,所以不會因 argparse 拒絕而讓 `pf_json` 變空。S8 的測試涵蓋這條。
- **偽造輸入:** 被審分支可控的檔名與訊息進 JSON 後引號會被跳脫成 `\"pushed_mainline\"`,掛鉤的 `grep` 樣式 `"pushed_mainline": *false` 對不上,所以無法偽造降級。
- **變異推演(只讀程式推演,沒有在臨時目錄實際改壞跑測試):**
  - 把 `--pushed-ref` 的參數改成 `$_lref`:feat:main 那條測試會紅。
  - 拿掉 `suite_computed` 檢查:`ppfb-uncomputed` 那條會紅。
  - 讓 `spec_light` 也設 `_SUITE_BRANCH_DOWN`:`t_prepush_feature_branch_already_light` 會紅。
  - 無條件帶旗標、不探測舊版:S8 的純文件那條會紅。
  - 主線集合改成只認 `main`:trunk 那條會紅。

**設計層面的殘留風險(判可接受)**
- `_note_reread_mainline_names` 查候選失敗或逾時,只剩 `main`、`master` 兩個固定名。預設分支若叫別的名字,那次會被當成功能分支而降級。計劃〈實務隱患〉已寫明並接受,本 repo 主線就是 main。
- 掛鉤會被 vendor 到消費專案,但測試套件閘用 `skills/lumos-project-notes` 與 `scripts/test_lumos.py` 是否存在限定,只在源 repo 生效,降級不會外溢。

**未驗範圍**
- 固定席前 8 篇圖譜節點沒有逐篇讀。這份 diff 沒碰 `guard-kill`、`design-loop`、`lumos-cli-read`、`lumos-cli-lifecycle`、`測試假綠形態` 的行為面,所以我判不影響,但沒有逐篇對過合約行。
- `suite_computed` 在有 lint 設定的那條 `pitfalls` 輸出路徑,只靠讀程式確認有帶,測試只走 `--no-lint`。掛鉤永遠帶 `--no-lint`,所以沒有失敗場景,不另列 finding。
- 驗收條款對照:S1 到 S8 都有對應測試且通過。S2 條文裡「`pf_json` 為空」那一格沒有獨立案例,靠 S8 的舊版沒欄位與 `ppfb-uncomputed` 兩條間接覆蓋,行為不會出錯。
- 修補歸因:本輪沒有 finding,所以沒有需要分修前、修後的案例。「已修復」的主張只靠修後版測試通過,修前版沒另外取出比對,這部分標為未判定。

臨時目錄沒有建立,沒有需要刪除的東西,也沒有背景程序殘留。
