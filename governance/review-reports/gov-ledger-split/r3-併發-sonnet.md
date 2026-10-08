severity: minor

# r3 併發席驗收(sonnet)

範圍:最壞時序(兩本帳同時寫、同批一本失敗、init 補建/追加 docs/.gitignore 同時有別的行程、兩本合併依時間排序同秒與時區、`_usage_log` 改檔名後新舊版工具並存)。結論:第 2 輪的併發修正都改對了,沒有 blocking;下面 4 條 minor。

## 第 2 輪修正驗收(已改對,不再報)

- 同批兩本各自吞錯:`_append_governance_log` 現況是單一 `open` 包整個迴圈、`except OSError: pass`(`scripts/lumos:1426-1432`);spec 做法 4 改成兩本各自開檔各自吞錯,S4 有測試綁定,方向正確。
- `_gate_event` 一次一筆、只選路徑、回傳值語意不變(`scripts/lumos:1356-1361`),寫不進去回 False,與 spec 一致。
- 判定類讀者清單我用 grep 對過一次:讀 `.governance-log.jsonl` 的位置(`scripts/lumos:1250、2238、2869、3867、8161、10198、11146、12367、25543、43295`)全落在 spec 〈盤點〉列的類別裡(design-loop rewrite/converged、fix-check、code-loop 留痕與表態、lint-new fail-open、帳本成長、spec-gate-run、S18、gov),沒有漏網的判定類讀者讀到本機名單上的閘。
- 白名單項目的寫入端都帶 `hard: False`(`scripts/lumos:2169-2218、2289、3489、7306、36960`),`_gate_event_build` 又用 `bool(hard)` 正規化(`scripts/lumos:1285`),「hard 恰好 False」的規則在現有寫入點不會讓觀察型事件意外落回版控帳。
- 舊使用紀錄帳凍結不停止追蹤:`_usage_log` 只寫不讀(`scripts/lumos:16181-16192`),新舊並存時只是舊版多寫一行到版控檔,不會刪檔或衝突。

## findings

1. 合併讀「依時間排序」沒講排序鍵,三個讀者現況各用一套,同秒與跨時區的結果不確定
severity: minor
blocking: 否(只影響提醒類統計與 doctor 軟段的顯示,不影響任何判定;判準:不會讓閘從擋變放)
引句:「兩本合起來**依時間排序**後再取最後一筆」
佐證:file: `scripts/lumos:2869-2879`(spec-gate 段後半現況是檔案順序、不排序,後寫覆蓋前寫)、`scripts/lumos:8205`(`cmd_gov` 對 `ts` 字串排序)、`scripts/lumos:3831-3841`(`_gov_metric_events` 用 `fromisoformat` 轉成帶時區時間,沒帶時區當本機時間)、`scripts/lumos:10141-10156`(`_loop_ts_key` 的註解自己寫明「字串比大小剛好會對是巧合不是保證」)。
最壞時序:`ts` 只到秒(`scripts/lumos:1282、1427`)。①同一份計劃在同一秒內被兩個行程各跑一次 spec-gate(或舊版工具寫進版控帳、新版寫進本機帳,同一秒),兩本合併後同秒平手,誰是「最後一筆」取決於實作先讀哪本,spec 沒定平手規則;②版控帳是跨機器共用的,雲端工作階段寫 `+00:00`、本機寫 `+08:00`,若 spec-gate 段用字串排序,舊版在 UTC 機器留下的 spec-gate-run 會排在較晚的本機紀錄後面(或相反),取到錯的「最後一筆」。
建議:spec 一句話定死:排序鍵用 `fromisoformat` 轉成帶時區時間(無時區的當本機時間,與 `_gov_metric_events` 同),平手時本機帳排後面(或版控帳排後面,擇一寫明),`cmd_gov` 既有的字串排序在同一句裡也講明是否一起改。S3 的測試也要含「同秒」與「不同時區」兩種資料。

2. S6 的「種類在程式裡真的有人寫」對動態種類的寫入點是空轉的釘子
severity: minor
blocking: 否(防漂移釘失效只是少一道保險,白名單本身仍是預設進版控,判準:不會讓擋人紀錄進本機帳)
引句:「本機名單的每個種類在程式裡真的有人寫」
佐證:file: `scripts/lumos:27367-27372`(nodehome-check 的 `kind` 是變數,`passed`/`warned`/`blocked` 由三元式算出)、`scripts/lumos:34765`(drift-check 同樣用變數 `kind`)、`scripts/lumos:12673`(字面值 `"passed"` 出現在 fix-check 的呼叫上)。
最壞時序:實作者照既有 `t_gov_stats_gate_drift` 的寫法(`scripts/test_lumos.py:6458-6485`,掃全檔字面值)去掃「種類字面值有沒有出現在原始碼」,`passed` 在全檔隨便哪裡都找得到,nodehome-check 與 drift-check 的 `passed` 哪天被改名或刪掉,這條釘子照樣綠,「名單上留著沒人寫的死項」永遠抓不到。
建議:spec 寫明這條釘子要以「閘+種類」成對比對寫入點,動態種類的寫入點要改成列舉(或在寫入點旁登記)才算「有人寫」;做不到成對就把這句降為只釘閘名、種類改由人審。

3. init 追加 docs/.gitignore 的機制沒指定(整檔覆寫還是 append),兩個行程同時跑與要寫哪兩行的字串都有歧義
severity: minor
blocking: 否(結果是多幾行重複或少忽略一行,doctor 軟提醒會唸;判準:不影響判定,也不丟任何已追蹤的檔)
引句:「缺的追加到尾端,原檔最後一行沒換行時先補一個換行」
佐證:file: `scripts/lumos:20885-20907`(`_init_additive_setup` 現況用 `exists()` 先判再 `_write_lf`,兩步之間沒有鎖)、`scripts/lumos:17605-17617`(`_write_lf` 是 tmp 加 `os.replace` 整檔取代,同檔「其他寫入指令仍是 last-write-wins」)、`scripts/lumos:20693、21777`(`_init_additive_setup` 同時掛在 `lumos update` 與 init 兩條路上)。
最壞時序:兩個行程(例如兩個 worktree 共用同一份 docs/ 不成立,但同一個目錄裡 `lumos update` 與 `lumos init` 同時、或使用者正在編輯 docs/.gitignore)同時讀到「缺兩行」。若實作用 `open("a")` 追加,兩邊都先補換行再各寫兩行,結果重複行與多餘空行,S5「已有不重複」在併發下不成立;若實作用 `_write_lf` 整檔重寫,則使用者在兩次讀寫之間手加的一行會被覆蓋掉。另外 spec 在忽略規則同一節先講根 `.gitignore` 要寫 `docs/.governance-local.jsonl`(帶 `docs/` 前綴,根目錄那份才對),下一條說 `docs/.gitignore`「加這兩行」,沒說 docs/.gitignore 裡要寫不帶前綴的 `.governance-local.jsonl`(現況 scaffold 寫的是不帶前綴,`scripts/lumos:20881`)。照字面把帶前綴的字串寫進 docs/.gitignore 會變成匹配 `docs/docs/...`,完全沒忽略,而且「整行相等」的逐行比對也會拿錯字串比。
建議:spec 寫出兩個 .gitignore 各自要出現的確切字串,並指定機制為「讀、算出缺的、`_write_lf` 整檔取代」(沿用 vault 唯一寫入原語,併發下至多是內容相同的重複覆寫);S5 的測試加一個「兩邊先後各跑一次,結果行不重複」的案例。

4. init 補建 docs/.gitignore 會在兩種情況下產生 spec 沒講的副作用
severity: minor
blocking: 否(判準:一次性、可逆;⚠ 我沒有實際在獨立 vault 佈局的 repo 上跑過)
引句:「不存在就照 `governance/.gitignore` 的先例建一份」
佐證:file: `scripts/lumos:20893-20896`(governance/.gitignore 的先例是 `parent.mkdir(parents=True, exist_ok=True)`)、`scripts/lumos:21799-21812`(`_vault_in` 認得獨立 vault:根目錄就是 vault,不一定有 docs/)、`scripts/lumos:1340-1348`(`_gate_event` 以 `docs/` 存不存在決定「這個 repo 有沒有這本帳」,不存在回 None 不寫)、`scripts/lumos:21757-21777`(init 對來源 repo 自己只跳過 vendor,`_init_additive_setup` 照跑)。現況驗證:本 repo `docs/.gitignore` 不存在(`ls docs/.gitignore` 報找不到),且 `git ls-files docs` 裡沒有它。
最壞時序:①獨立 vault 佈局(沒有 docs/)的 repo 跑 `lumos update`,照先例 mkdir 建出一個只有 .gitignore 的 docs/,從此 `_gate_event` 的「結構性不適用」判斷翻成適用,擋人事件開始寫 `docs/.governance-log.jsonl`;spec 〈做法〉3 寫「docs/ 不存在時跟現在一樣不寫」與這個先例互相抵觸。②本 repo 自己跑 `lumos update` 或 init,會建出一份未追蹤的 `docs/.gitignore`(spec 說本 repo 靠根 `.gitignore`),下一次 git status 就髒,恰好是這案要消滅的現象。
建議:spec 加一句「docs/ 不存在時不建 docs/.gitignore(不照 governance/ 的 mkdir 先例)」,並說明本 repo 是否也要有一份 docs/.gitignore(要的話列為提交內容、不要的話 init 對來源 repo 跳過)。

## 總結

總結:併發面沒有 blocking:兩本帳各自吞錯、白名單加 `hard` 恰好 False、判定類讀者不動、舊檔凍結這四條都站得住;剩 4 條 minor(排序鍵與平手規則、S6 對動態種類空轉、docs/.gitignore 的機制與字串歧義、docs/ 不存在或來源 repo 的副作用),可在實作時順手補進 spec。整份最嚴重 severity:minor。
