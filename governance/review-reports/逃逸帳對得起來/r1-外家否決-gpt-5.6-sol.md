severity: major

## F1 撤回後同一筆自動逃逸會被重新入帳
severity: major
blocking: 是；照規格共用過濾後的讀取結果做去重，已撤回事件會從去重集合消失，重跑同一個 hook 就再次成為有效逃逸。
引句:「所有讀逃逸帳的地方都要走這支」
file: `scripts/lumos:9342` 自動寫入在鎖內用 `_escape_rows_for` 建立 `(loop, stage, sha)` 去重集合，並於第 9360 行據此決定是否重寫。
重現：自動寫入 token T → 撤回 T → 同一 sha 的 CI 或 push-gate 重跑；新 `_escape_rows_for` 隱藏 T 後，`_auto_escape` 會追加 T2，撤回立即失效。去重必須看包含 tombstone 的原始帳，不能看「有效列」視圖；S3 也缺這條案例。

## F2 既有 `push-gate-unreviewed` 會被錯算成漏網
severity: major
blocking: 是；照站名白名單實作，既有推送閘成功接住的事件會被歸為未知站名並算進逃逸率。
引句:「其他站名(CI、prod、使用者回報、消費專案真推送…)算漏網;不認得的站名算漏網並另列」
file: `scripts/lumos:9356` 現行自動路徑明確產生並辨識 `push-gate-unreviewed`。
file: `docs/lumos-toolchain-knowledge/Projects/逃逸自動記_計劃.md:79` 綁定測試 S6 要求該推送閘事件以 `push-gate-unreviewed` 入帳。
規格只把 `push-gate` 列為下一站接住；因此會破壞 `Systems/loop-convergence-recording` 所連到的既有自動逃逸合約。白名單須納入 `push-gate-unreviewed`，或明訂正規化規則。

## F3 `_plan_for_loop` 無法替 `code-` 迴圈找到計劃
severity: major
blocking: 是；照指定函式直接查找，代碼審迴圈即使有對應計劃也會全部落入未分類，分級×範圍統計失真。
引句:「範圍類:用 `_plan_for_loop` 找到的計劃的 `scope/<類>` 標籤」
file: `scripts/lumos:9293` `_plan_for_loop(env, loop_id)` 只嘗試 `<loop_id>_計劃.md` 與 `<loop_id>.md`，不會移除 `code-` 前綴。
例如 `code-筆記欄位關卡補齊` 會查 `Projects/code-筆記欄位關卡補齊_計劃.md`，而實際計劃是 `Projects/筆記欄位關卡補齊_計劃.md`。目前可進分母的 114 個 `code-` 迴圈，直接呼叫此函式沒有一個能命中；至少 7 個移除前綴後確有同名計劃。規格必須定義 code-loop 到計劃的映射，而非宣稱既有函式已能處理。

## F4 撤回缺少目標驗證及撤回者的取得規則
severity: major
blocking: 是；撤回會改善治理數字，若目標拼錯仍成功或操作者身分任意填入，帳面不能證明真正撤回了誰的哪一筆。
引句:「撤回的理由與撤回者照樣留在帳上,可以查。」
規格只給 `--withdraw <token> --reason <理由>`，沒有定義撤回紀錄欄位、撤回者來自 CLI、git identity 還是系統帳號，也沒有要求 token 必須唯一存在、必須指向有效逃逸、不得指向撤回紀錄、重複撤回如何處理。重現：輸入 `--withdraw ESC-拼錯 --reason 誤記`；照字面可追加一筆無作用的撤回並回報成功，原逃逸仍被統計。這些驗證須在同一把寫入鎖內完成並有條款測試。

## F5 真實帳本已有互相矛盾的 tier，規格未定義取哪一筆
severity: major
blocking: 是；同一迴圈可被分到 high 或 standard，分類後的分母與區間會依實作者的遍歷選法改變。
引句:「分級:審查帳裡這個迴圈任何一列記到的 tier」
file: `scripts/lumos:17905` 現行迴圈語意由 `_loop_anchor_tier` 明訂為「第一筆帶 tier 的值」，不能取任意列。
file: `docs/.canary-log.jsonl:434` `code-codex-refine` 的早期帳列定錨為 high；同一迴圈後續另有 standard 帳列。
`any`、最後一筆、最高值與既有定錨函式會得到不同結果。統計必須沿用 `_loop_anchor_tier`，或明訂矛盾帳列獨立列錯且不納入分類。

## F6 共用讀取函式會讓逃逸清單失去既有壞帳容錯
severity: major
blocking: 是；照規格把清單切到現有 helper 後，一行合法 JSON 非物件即可令所有逃逸讀者崩潰。
引句:「讀的一側遇到寫一半的最後一行略過。」
file: `scripts/lumos:7408` `_escape_rows_for` 在 `json.loads` 後直接呼叫 `d.get`，對 `null`、陣列或數字會拋例外。
file: `scripts/lumos:9447` 現行 `loop escape --list` 另外檢查 `isinstance(d, dict)`，把合法 JSON 非物件列為壞行並繼續。
重現：逃逸帳追加一行 `null`；目前 `--list` 會提醒並跳過，改走 `_escape_rows_for` 後會在 `d.get` 當場失敗。S3 要求所有讀者共用 helper 前，必須把語法壞行、非物件行及僅末行截斷的行為一起定義並測試。

已看,無: 投稿與指定的 `Projects/逃逸帳對得起來_計劃` 內容一致，沒有兩版漂移；三個 wikilink/lands_in 目標均存在；intake 已驗過的帳本筆數、無佐證數、自動列數與現行讀者分布未重報；`loop next`、`loop status --disposal`、`canary record`、`quote-check`、`loop escape`、`gov`、`rule-gap` 的現行 help 與既有旗標均已核對，`escape-stats`、`--withdraw` 尚未落地符合計劃狀態。逐節方面，一句話、佐證門檻、另開兩案、S1/S2/S4/S8/S9、回退與誠實界線未另見可重現缺口；S3/S5/S7 的缺口已分別列於 F1/F2/F5。相關節點逐條判定：`Systems/loop-convergence-recording` 會受 F1、F2、F6 影響，因其既有逃逸讀取、去重與自動站名語意會被改壞；`Projects/逃逸自動記_計劃` 會受 F1、F2 影響，因去重合約及 `push-gate-unreviewed` 的 S6 會失真；`Projects/自主審查量尺_計劃` 僅作被取代背景，本案不修改其既有執行路徑。實務隱患逐類：併發有 F1，單純共用寫入鎖不能防撤回後重入帳；效能無，三本現有帳量級可由單次手動唯讀掃描承受；守衛面有 F1、F2、F4、F6，撤回會改好數字且現有自動路徑與讀取容錯會受影響；金流無，沒有付款或計費路徑；對外送出無，未呼叫外部服務；不可逆無，資料採追加式保留，但撤回者與目標稽核缺口已列 F4。

最嚴重 severity: major，blocking 共 6 條。
