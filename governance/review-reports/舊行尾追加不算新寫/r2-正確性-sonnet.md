severity: major

這份修訂稿的查核範圍:逐節讀完,對照 `scripts/lumos` 的 `_notelines_parse_added`、`_ns_diff`、`_notelines_new`、`_note_shape_eval`、`_note_audit_items`、`_notelines_content_id`、`_drift_m1_fit`、`_mainline_ref`、`_lens_push_base`、`_nodehome_clamp_base`。git 行為在我自己 mktemp 的臨時 repo 實跑,沒動 repo。

實跑確認的部分:
- `diff.interHunkContext=3` 搭配 `-U0` 確實會吐出上下文行,舊解析器會因此錯位。
- 加上 `--inter-hunk-context=0` 後區塊會拆開。
- `\ No newline at end of file` 夾在 `-` 與 `+` 之間,與 spec 的讀法一致。

交叉引用都對得上:天花板 1、4、5、7,〈做法〉1 到 6,範本規則 2、5、7,五個 `_note_audit_items` 呼叫端。

**R1 配對起點隨呼叫者的 base 而變,第二層的內容編號因此不穩**
severity: major
blocking: 是 — 同一行在不同呼叫端算出不同編號,已記的「只判尾巴」判定會被當成沒涵蓋,doctor 永遠誤報
引句:「推送與 doctor:起點版本若已在主線上(是主線參照的祖先),配對起點就是它;否則用「終點版本與主線的分岔點」(`git merge-base`)。」
1. 配對起點取「呼叫者給的 base,只要它在主線上」。〈做法〉4 又把配對結果寫進內容編號(`tail_of`)。所以只要各呼叫端的 base 不同,同一行就會有不同編號。
2. doctor 事後掃描(〈做法〉4 把它列為第五個呼叫端):`scripts/lumos:34444` 用 `_note_audit_items(root, gl, ml[1], …)`,base 是上線點。
   - 情境:舊句 O 在上線點之後才進主線(推送 A)。推送 B 在 O 後補括號,當時以 B 的 base(在主線上)配對,記下「尾」編號。
   - doctor 以上線點為起點。上線點版本沒有 O,這行是純新增,不配對,算出整行編號。
   - 結果:`scripts/lumos:34455` 的 `_note_audit_covered(fold.get(it["id"]))` 對不上,doctor 報「已推上遠端卻沒被筆記內容審涵蓋」。這是假警報,而且作者無從消除,只能另判整行。
   - 〈做法〉7 只處理第一層的 doctor,第二層 doctor 沒被提到。驗收條款也沒有任何一條涵蓋(S25 只講第一層)。
3. 手動 `prepare --diff origin/main..HEAD`:fetch 之後 origin/main 領先 HEAD 的分岔點。
   - origin/main 是主線祖先,所以被當成配對起點,但它不是 tip 的祖先。diff 會把主線新增的內容反向算進來。
   - 若主線動過同一行,這行不配對,拿到整行編號。
   - pre-push 的 check 的 base 是遠端分支舊頂端,不在主線上,所以用 merge-base 配對,拿到尾巴編號。兩邊編號不同。
4. 預期:配對起點與呼叫者選的 base 無關,例如一律用 `merge-base(tip, 主線)`,且 base 必須同時是 tip 的祖先。實際:隨 base 變。
5. 第一層同理:推送模式的 base 經 `_nodehome_clamp_base`(`scripts/lumos` 的 `_nodehome_clamp_base`)可能被改成上線點,與提交前用的 merge-base 不同,S24 的「兩邊一致」會破功。

**R2 CI 的 pull_request 或 detached checkout 沒有本地 main,配對整個失效,出現「本機放行、CI 擋」**
severity: major
blocking: 是 — 作者在本機靠放寬過關的提交,到 CI 被擋,而且擋的是舊行本來就有的違規,作者沒法改
引句:「CI 是淺層 clone 時算不出分岔點,這次不配對(比本機嚴、不會比本機鬆);本 repo 的 CI 用完整歷史。」
1. 主線參照走 `_ns_mainline_refs`,背後是 `_mainline_ref(remote_only=True)`,只認 `main@{upstream}` 與 `master@{upstream}`(`scripts/lumos:38736` 起)。
2. 沒有本地 `main` 分支就回 None。常見的 `actions/checkout` 在 pull_request 事件下是 detached 的 merge ref,fetch-depth 0 也只有 `refs/remotes/origin/*`,沒有本地 main。預設分支叫 `trunk` 或 `develop` 的消費專案也一樣。
3. 這時 spec 要求「找不到主線參照就不配對」。本機有 upstream,放寬成功;CI 照今天整行查,就把舊行本來就有的「沒寫來源」算給補括號的人。
4. spec 只討論淺層 clone 的跨環境差異,而且淺層 clone 在 `cmd_note_shape` 已經 early return(`scripts/lumos:28594` 附近)。真正會漏掉的是「CI 沒有本地主線分支」,spec 沒處理。「CI 用的前一版也在主線上,兩邊算出同一個配對起點」只在 push-to-main 事件成立。
5. 預期:CI 與本機行為一致,或 spec 明講 PR 型 CI 不適用並給出替代的主線來源(例如 `origin/HEAD`、`refs/remotes/*/main`)。實際:⚠ 相同提交在兩邊判定不同。我沒實跑 GitHub Actions,依 checkout 慣例與程式現況推得。

**R3 配對失敗的定義含糊,`relaxed-failed` 帳會被「沒有主線參照」灌水,RETIRE-IF ② 失真**
severity: minor
blocking: 否 — 只污染觀測、不影響擋放
引句:「配對失敗(回空表且帶失敗原因)而這次本來有違規時,推送模式記一筆種類 `relaxed-failed`」
1. 〈做法〉1 說任何失敗都回空表加原因字串。「找不到主線參照」「`base_where` 為 None 或空樹」算不算失敗,spec 沒講。S23 只要求「全不配對」,沒說記不記帳。
2. 〈做法〉2 的「用到才算」是只要有違規就呼叫配對,不看有沒有追加候選。
3. 沒有 upstream 的 repo(新 clone 的消費專案、`trunk` 專案),每次有違規的推送都會記一筆 `relaxed-failed`。`base_where` 為 None(`_nodehome_clamp_base` 找不到上線點時 `base_where = None`,見 `scripts/lumos:28583`)若讓 `merge-base --is-ancestor None` 拋 TypeError,也同樣記成「壞了」。
4. 〈做法〉5 把 `relaxed-failed` 定位成「壞了」的訊號(與「沒機會用」區分)。這個定義會讓 RETIRE-IF ② 讀到的「壞了」混進「根本沒有主線」。
5. 預期:明寫「無主線參照」「無起點」屬於「沒機會用」,不記 `relaxed-failed`,並加一條驗收條款。

**風險類逐類(實務隱患鏡頭)**
- 繞過:我試了「插新行搶走舊行」與「刪舊行在遠處重寫」,按位置一對一加「刪加行數相等」的規則擋得住。
  - 追加段的 regex `\s*[(（].*[)）]` 允許「(a) 任意文字 (b)」。但攻擊者自己寫 `(…)` 也能得到同等額度,沒有多放。無 finding。
- 效能:無。配對線性、讀取有 512 KB 上限、只在有違規或有送審項目時才跑 diff。
- 併發:無新增問題。起點釘成 sha,帳走既有寫入器並登記進鎖的 Issue。
- 回滾:無。解析器修洞與配對綁在同一個提交,spec 已寫明。
- 相容:無。新旗標對 `-U0` 呼叫端無害,3.9 語法限制已寫入。
- 跨環境:見 R2 與 R3。

**資料狀態五問**
- 空或不存在:新檔、純新增沒有被刪行,不配對,正確。
- 單筆:無問題。
- 大量:無問題,同上。
- 重複或順序:兩行相同舊句各補不同括號,按位置配對,正確。
- 髒或過期:非 UTF-8 或超過 512 KB 不配對;`-M` 改名不配對,偏嚴,可接受。

**各節結論**
- 〈做法〉2、3、5、6:已讀,除 R3 外無 finding。
- 驗收條款:已讀。缺一條涵蓋 R1 的第二層 doctor 與跨 base 編號一致性,以及 R2 的無本地主線分支情境。
- 固定席:未附。

最高嚴重度 major,blocking 2 條
