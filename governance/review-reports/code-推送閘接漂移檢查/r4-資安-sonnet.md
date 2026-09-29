severity: clean

# 資安席 r4(只看第 3 輪修正本身、站攻擊者那邊)

無 finding。逐項查證:

1. CI 補 origin/HEAD 那段:DEFAULT_BRANCH 走 env 傳入、shell 裡一律雙引號展開,沒有拼進命令字串,無 shell 注入。symbolic-ref 目標永遠是 `refs/remotes/origin/` 前綴,不會被當選項;實測含空白或 `..` 的名字被 git 直接拒絕(Refusing to set ... invalid ref),`--x`、`-f`、`main;id` 這類名字只是原樣成為 ref 名,不會指到別處。且該步前面還有 `rev-parse --verify refs/remotes/origin/$DEFAULT_BRANCH` 必須存在才會設。預設分支名由倉庫管理員決定,不是推送者能控的輸入。
2. `merge-base --all 頂端 候選…`:頂端是 `_lens_full_sha` 驗過的 40/64 位十六進位;候選傳進去的是 `_push_rev` 回的、通過 `_LENS_SHA_RE` 的 sha,不是 ref 名;遠端名只出現在 `refs/remotes/<遠端>/…` 前綴內、傳給 symbolic-ref/rev-parse 的第一個字元一定是 `r` 或固定的 `main@{upstream}`,無法被當選項。`--pushed-ref` 在 CI 由 `"$GITHUB_REF"` 帶入(雙引號),只做 `refs/heads/` 前綴比對與字串拼接,不進 git 選項位置。
3. 「判不了」:只有 git 跑不起來或逾時才觸發(OSError/TimeoutExpired),回 _PUSH_START_UNKNOWN 後呼叫端不截上線點、照要處理處理(block 擋、warn 印),沒有退成少查。推送者要製造逾時得讓自己的 repo 巨大,結果是被擋而非放行;要讓「頂端已在主線」誤判成立得控制主線候選 ref 或本機 config(那是本機自己人,且 LUMOS_SKIP_DRIFT_CHECK 本來就是明示逃生口),CI 端候選來自 checkout 的 origin refs,推送者無法把不在主線的提交變成主線祖先。
4. 跳過「被推的那條」的比對是遠端與分支全名相等才跳過;攻擊者改分支名只會讓自己的候選被跳過→走無主線分支,起點退回舊值/空樹,範圍變大(多查),不會變小。

## 圖譜鏡頭逐條判定(資安角度)

- Issues/code-loop守衛main-direct盲區(事故):不影響。事故是守衛被直推主線繞過;這次修正只改 drift 範圍起點的算法,未動 code-loop 守衛,且判不了時 block 擋、不放行,沒有新增繞過面。
- Systems/存量漂移守衛(家):不影響。合約方向(判不了不退成少查)與這次「git 失敗算判不了」一致;候選只用驗過的 sha,無注入面。
- Systems/每支檔有家:不影響。這次沒有新增未歸屬的程式檔,與注入或繞過無關。
- Systems/筆記內容閘:不影響。閘仍用原本的 _lens_push_base;新的起點算法只給 drift 用,兩套並存不互相削弱。
- Systems/測試假綠形態(INVARIANT):不影響。新增測試若走不到被測分支才是風險;資安面上未見能讓閘假綠的輸入(逾時與失敗一律走判不了)。
- Systems/anchor-integrity(RISK):不影響。CI 的 anchor verify 步驟沒動;新步驟只加在其前,不改基線檔。
- Systems/lumos-cli-lifecycle(INVARIANT,re-inject 不動 sentinel 外內容):不影響。這次不碰 CLAUDE.md 注入路徑。
- Systems/lumos-cli-read(INVARIANT,search 排除 superseded):不影響。未動搜尋。
- 只列名的節點(bound-tests-gate、canary-audit、design-loop、guard-kill、slim-*、規格落成可驗收條件、雙向門放行、逃逸自動記、lumos-deinit、cochange-guard、節點範圍與索引守衛、check-r-guard):不影響。這次修正沒有觸及它們的輸入面;從資安角度找不到經由 ref 名、遠端名或判不了處理連到它們的路徑。

最高等級:clean
