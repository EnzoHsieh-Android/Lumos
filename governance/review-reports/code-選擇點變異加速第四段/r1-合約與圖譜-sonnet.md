severity: major

我是接手的人,照計劃、筆記、註解逐條對過一遍程式與測試。S1、S2、S3、S6 的預期值大致都有對應的斷言。「只在找不到 JUnit 結果檔時重試」這個收窄,程式、S6 測試、做法節第 62 行都跟上了,但白話、PRIOR-ART、不做、依據來源、回退和 guard-kill 的 WHY 還停在舊說法。manifest 那 1 條是 `with open(...)` 寫法,沒問題。

1. 斷路器恢復後 `hang_streak` 不歸零,恢復後只要再逾時一次就又跳開。
severity: major
blocking: 是
引句:「    if kind in ("pass", "fail"):   # 跑到測試後逾時的連續次數:通過或有失敗歸零(第四段計劃做法 3)」
- 這段歸零寫在斷路器啟用中的路徑。停用中收到試探快篩通過或失敗時,程式先走恢復分支就 return,從頭到尾沒碰 `hang_streak`。
- 跳開時 `hang_streak` 也沒歸零,只歸零了 `cool`。
- 計劃寫的是「連續 15 次才跳開」,而且「通過或有失敗 → hang_streak 歸零」,恢復後的第一次通過就該算。
- 最小重現(已用 python3.14 載入 `scripts/lumos` 跑過):
  - 對 `_kill_merge_breaker` 餵 15 次 `(kind="unclean", why=_CHOICE_MERGE_HANG_WHY)`,斷路器跳開,`hang_streak` 為 15。
  - 再餵一次 `kind="pass"`,恢復,`hang_streak` 仍是 15。
  - 再餵 1 次逾時,斷路器立刻又跳開,`hang_streak` 變 16。
- 測試 `t_choice_kill_merge_hang_breaker` 的「停用中試探逾時有事件行 → 不恢復」案例只驗證不恢復,沒有「跳開、恢復、再逾時一次」這一案,所以抓不到。
- 這會讓 S5 實測時,試探恢復後的下一個掛住壞法就把合併關掉,偏離計劃的預期。

2. `Systems/guard-kill.md` 的 WHY 沒有跟上收窄,仍寫「任何不通過都重試」。
severity: major
blocking: 是
引句:「帶腳本的合併基準不通過就不帶再跑一次、通過就照常合併並記 merge_init_off」
- file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:68`
- 程式只在原因等於「找不到 JUnit 結果檔」時重試。
- 有失敗、rc 不是 0 但有寫結果檔、編不過,都不重試。
- 這是守檔筆記,下個 session 會先讀它。照它判斷會以為腳本沒拒收、基準照樣會重跑。

3. 計劃檔裡還有四處留著收窄前的說法。
severity: minor
blocking: 否
引句:「腳本讓合併基準不通過時,不帶腳本重試一次。」
- file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第四段_計劃.md:26`(白話)
- 同樣留著舊說法的還有:
  - 第 35 行 PRIOR-ART ⑥:「帶腳本的合併基準不通過就不帶腳本重試一次」
  - 第 90 行〈不做〉:「帶腳本不通過就不帶重試」
  - 第 139 行〈依據來源〉:「帶腳本不通過就不帶重試」
  - 第 115 行〈回退〉:「腳本被 Gradle 拒收時工具自己不帶重試」
- 〈做法〉第 62 行與審計修正紀錄第 151 行是新的,同一份檔案內前後不一致。

4. 做法節說重試通過後 `sh["init"]` 改 None,程式沒做。
severity: minor
blocking: 否
引句:「                mg.init_off[c.plat] = first   # 之後快篩用回傳的 mcmd(不帶腳本那次組的)」
- file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第四段_計劃.md:62`
- 計劃寫「`sh["init"]` 改 None」,程式只記 `init_off`,靠回傳的 `mcmd` 讓快篩不帶腳本,`sh["init"]` 維持原值。
- 我查了 `scripts/lumos` 裡所有用到 `sh["init"]` 的地方,目前沒有後續讀者,行為無誤。但接手的人若以為改成 None 而在下游判斷 `sh["init"]`,會判錯。

5. S1 測試對「不帶、照常合併」只斷言 `init is None`,沒有斷言之後真的照常合併。
severity: minor
blocking: 否
引句:「check("S1 ★對照★ 現場沒有 scratch → init 是 None", r0 is not None and r0.get("init") is None, str(r0))」
- 「寫不進去」那案同樣只斷言 `init` 變 None 與印出提示,沒走到合併。
- S1 條款有寫「照常合併」。真跑案例只涵蓋有 scratch 的一般情況。

最高 major,blocking 2 條

**圖譜鏡頭**
- 固定席節點(`bound-tests-gate`、`lumos-cli-read`、`測試假綠形態`、`lumos-cli-lifecycle`、`reversibility-governance-ledger`、`loop-convergence-recording`):這份 diff 都不影響。diff 只動 choice-kill 合併快篩與治理帳新欄位,沒碰它們宣稱的行為或合約。
- `guard-kill` 的兩條 INVARIANT:
  - rc 優先序:diff 沒動逐支判定與 rc 規則,不受影響。
  - `--json` 純度:新增的提示只印到 stderr,不受影響。
- `pitfalls-code-loop`:`pitfalls-builtin` 那 1 條 `open(` 是 `with open`,資源會關。
- 其餘「超出上限只列名」的節點只列名,我沒逐篇讀,不判。
- 沒有「這次新增的殘留」段,殘留決策那題不適用。

**表態記錄**
- 我這邊沒有反駁。程式裡沒有 async 或並行,外部呼叫只有本機 Gradle 子程序,逾時後不再重試。
