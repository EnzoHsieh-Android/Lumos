severity: minor

資源鏡頭的結論:這輪修補照既有判法加了淺複製與部分複製的保護,並把撞名測試改成數次數,兩處都站得住。我另找到三條小問題,都不擋推送。沒有 major 以上。

## 修補差異的結論

- **原問題的行為證據**:`t_redbase_branch_rows_fallback_keeps` 的淺複製、部分複製、過了截止時間、超過上限四組全綠(我在 r2 版本實跑)。
- **相鄰路徑**:
  - 治理帳進版控的分支(`t_spec_gate_redbase_green_tracked_unfiltered`)仍綠。
  - `t_spec_gate_redbase_green_other_branch` 十條斷言全綠。
  - `t_name_collision_scales` 四條全綠,0.4 秒。
- **子程序收拾**:`merge-base`、`cat-file`、`config --get`、`rev-parse --is-shallow-repository` 都走 `subprocess.run(timeout=…)`。逾時與 Ctrl-C 都會殺掉 git 本身。這四個指令在完整 repo 裡不會再叫起子程序,沒有殘留。

## 逐條 finding

1. 部分複製的 fork 點讀帳在過濾之前就會去遠端抓,60 秒卡住,抓取子程序殘留
   - 引句:「repo 種類照回頭條件那支 _drift_born_env_err 的判法:淺層用既有的 _git_is_shallow(逾時當判不了),部分複製看 extensions.partialClone——」
   - 失敗場景:
     - 部分複製(例如 treeless)的 fork 那一版 tree 在本機沒有。
     - `_redbase_branch_rows` 在到達新的部分複製保護之前,就會先跑 `_lens_fork_point` 與 `_gov_rows_delta`。後者內部的 `git show <fork>:docs/.governance-log.jsonl` 會觸發 lazy fetch。
   - 重現:
     - 我手工做了一個 `extensions.partialClone=origin` 的 clone,刪掉 fork 的 root tree 與 docs tree,`remote.origin.uploadpack` 指到 `sleep 45` 的假腳本。
     - 呼叫 `m._redbase_branch_rows(cl,"甲",ignored="ignored")`,量到 elapsed 60.2 秒、回傳 0 列,並印「讀不出起點那一版的治理帳」,所以這次過濾與去重整個沒作用。
     - 回傳後 `ps` 還看得到 `sleep 45` 孤兒(ppid 已被重新指派),也就是 git show 逾時被殺、它叫起的抓取子程序沒被收。
     - 觸發的 git 指令是 `('show','--no-textconv','b68304…:docs/.governance-log.jsonl') -> None 60.0`。
   - 範圍:只有 fork tree 不在本機的 treeless clone 才會走到。一般 blobless clone 的 tree 在本機,帳又被忽略、路徑不存在,不會抓。
   - 歸因:有證據的原有漏查。修前 7d029f46、409ab14f、修後 6e10ae5b 三版結果相同(同樣 60 秒、同樣孤兒)。計劃說的「部分複製整批不問」只覆蓋祖先那一步,沒有覆蓋同一函式前面的兩個讀取。
   - 建議:把部分複製判斷提前,在 `_lens_fork_point` 與 `_gov_rows_delta` 之前先判,判成部分複製就當作判不了。
severity: minor
   - blocking: 否

2. 部分複製只認 `extensions.partialClone`,漏掉只設 `remote.<名>.promisor` 的複製
   - 引句:「部分複製看 extensions.partialClone——」
   - 失敗場景:
     - 在這台機器(Apple git 2.39.2)上對 `git clone --filter=blob:none file://…`,伺服器沒認出 filter,結果 `remote.origin.promisor=true`、`remote.origin.partialclonefilter=blob:none`,但沒有 `extensions.partialClone`。
     - 這種 repo 被判成 `full`。我實測 `git merge-base --is-ancestor ab…ab HEAD` 與 `git cat-file -e ab…ab^{commit}` 對本機沒有的提交,都會去連遠端(記號腳本被觸發,git 提示無法讀遠端、`cat-file -e` rc 128)。
     - 這種情況下 `_redbase_on_branch` 對每個舊的、不存在的提交會連兩次遠端。
   - 範圍:鄰居 `_drift_born_env_err` 也只認 extension,repo 內 grep 不到 promisor,屬於既有慣例。伺服器不支援 filter 才會出現,而且不是單人本機常見配置。
   - 歸因:有證據的原有漏查(判法照抄鄰居)。
severity: minor
   - blocking: 否

3. 10 秒預算在大 repo 且沒有 commit-graph 時,幾個陳年舊紀錄就會用完,過濾退回「全留」
   - 引句:「截止時間在問祖先前一刻才起算,讀帳與算分岔點不吃這份預算。」
   - 重現一:
     - 30 萬提交的線性 repo、沒有 commit-graph,`git merge-base --is-ancestor <非祖先> HEAD` 每次 1.15 秒。
     - 15 個不同的非祖先 head_sha 呼叫 `_redbase_on_branch`,elapsed 10.01 秒,只判了 8 個、留了 7 個,印「7 筆紀錄判不了…照舊算進來」。
     - 寫了 commit-graph 之後同一個查詢 0.019 秒。
   - 重現二:
     - 6 萬列、87MB 的帳,每列隨機 head_sha(不存在),帳被忽略。過濾前 1.08 秒,過濾後 11.1 秒,在預算上限停下,只問了約 170 個 sha(每個 2 次 git,約 58ms),其餘 59810 筆照留。
     - 記憶體 387MB 對 393MB,過濾沒有多吃。
   - 行為:退回舊行為並印提示,沒有擋人,最壞多等 10 秒,有界。
   - 現實性:一份計劃要有近十個以上同分支名或沒有 ref 的陳年 head_sha,才會碰到。
   - 附帶:87MB 帳讀進來要 387MB 記憶體,是 `_gov_rows_at` 既有的整檔讀取,修補前就如此。
   - 歸因:未判定,偏有證據的原有漏查。
severity: minor
   - blocking: 否

4. 圖譜鏡頭附帶發現:S6「同名重開」案例缺前置斷言,不符《測試假綠形態》的 ★INVARIANT★
   - 引句:「check("S6 同名重開、判綠那時的提交不是祖先:照存", "redbase" in rec, (rec.get("redbase_skipped"), out[-500:]))」
   - 失敗場景:
     - 那段先寫判綠紀錄再刪分支重開,卻沒有斷言判綠紀錄真的寫進帳了。
     - 我在 /tmp 的副本把 `write_text("")` 與 `unlink()` 兩行換成 `pass`(整個測試不再造出判綠),`t_spec_gate_redbase_green_other_branch` 仍 10 passed。
   - 影響:判綠寫入端若壞掉,S6 會空轉不會紅。祖先過濾本身壞掉仍會紅。
   - 歸因:有證據的原有漏查,409ab14f 就有這段,修補沒碰。
severity: minor
   - blocking: 否

## 三問回答

1. **哪個子程序在逾時、Ctrl-C、例外時沒被收掉**
   - 本輪新增的呼叫:完整 repo 與有 extension 的部分複製都沒有殘留。部分複製整批不問,我用 `uploadpack` 記號腳本驗過。
   - 沒被收的有兩條:finding 1(部分複製 fork 點讀帳,60 秒加孤兒)與 finding 2(只有 promisor、沒有 extension)。
2. **哪個時間預算在大輸入或慢機器上擋下正常操作或讓過濾被跳過**
   - 只有 finding 3,是有界的退回,最壞多 10 秒。
   - `_lens_fork_point` 與 `_gov_rows_delta` 沒有 deadline,屬既有。
3. **哪段整本讀進記憶體或做二次方工作**
   - 本輪新增部分(`dict.fromkeys(reversed(order))`、候選清單、`verdict.get`)都是線性,過濾沒有額外記憶體。
   - 整檔讀帳放大 4.5 倍是既有。
   - 新的 `_TG_CONST_PAT` 三引號那段是佔有式,對 500 萬字元的各種病態輸入(未收尾的三引號、大量引號、大段三引號)都在 0.08 秒內,舊的 0.00 秒。

## 新測試在 CI 上的時間與記憶體

| 測試 | 本機時間 | 備註 |
|---|---|---|
| `t_name_collision_scales` | 0.4 秒 | 前一版本機約 5.8 秒 |
| `t_redbase_branch_rows_fallback_keeps` | 4.8 秒 | |
| `t_spec_gate_redbase_green_tracked_unfiltered` | 3.2 秒 | |
| `t_spec_gate_redbase_green_other_branch` | 16.9 至 17.8 秒 | 跑 10 次規格閘;同族測試約 4 至 5 秒 |

- `t_spec_gate_redbase_green_other_branch`:若 CI 慢約 3 倍,約 50 秒,仍低於測試超時上限 180 秒(餘裕 10 倍)。
- 假部分複製的 `uploadpack` 腳本是立刻 `exit 1`,不會卡住。
- 臨時目錄走 `mkvault()` 的 mkdtemp 慣例。

## 固定席節點對照(圖譜鏡頭)

- `lumos-cli-read`、`design-loop`、`guard-kill`、`lumos-cli-lifecycle` 的 ★INVARIANT★:這份 diff 沒有動搜尋濾網、處置閘、`guard kill`、re-inject 的行為,看不出破壞。
- `測試假綠形態`:新測試多數有 ★前置★ 斷言,只有 finding 4 那一處缺。
- `規格閘` 與 `pitfalls-code-loop`、`loop-convergence-recording` 等 ★RISK★ 節點:diff 只讓規格閘事件多一個 `ref` 欄位。我查過 `scripts/lumos` 裡讀 `ref` 的幾處,都是別本帳(簽核帳、retro),沒有讀 spec-gate 事件,沒有誤讀。

## 未驗範圍

- 沒有實測過真正的 blobless 與 treeless 遠端 clone。此機器 Apple git 2.39.2 的 file:// 伺服器不認 filter,我用手工刪 tree 加設 `extensions.partialClone` 模擬。
- Windows 上 git 起程序較慢,10 秒預算可能更早用完,沒實測。
- 時鐘倒退沒實測。

我自己的臨時 repo(大 repo、大帳、部分複製、突變副本)已用字面絕對路徑刪除。留在 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/資源-sonnet/` 的只有幾支小的 probe 腳本與兩份 lumos 舊版副本,由編排者收貨後刪。

最嚴重等級是 minor,blocking 共 0 條。
