---
type: project
status: doing
created: 2026-08-24
updated: 2026-08-24
summary: |-
  FLAG:DECISION
  KEY:立案(2026-08-24 Enzo「好」)——Check S 是「喊了等人看」:兩篇樞紐筆記被喊 44/40 天(546/499 次)沒人理,終於派乾淨 agent 審=2/2 全站不住、11 處真漂移(兩處「照做出錯」級)。抽檢命中率 100%,問題不在閘在「沒人看」;backlog 的「腐化偵測延遲」gap 與這題同主題(★s3 r1 訂正:該 gap 從未被 loop 試過——兩次啃不動的是寫閘與治理帳,立案理由改為 44 天實證而非 loop 敗績★;落地時該 gap 標 covered)
  KEY:方案(★d1 裁定版:全自動閉環★)=每週派乾淨 agent 審「從未確認+過期」功能筆記(N=2/週,PR 高者先)——PASS→自動戳(auto/ 前綴留痕);FAIL→★另一 agent 修筆記→第三個乾淨 agent 複審(maker/checker 分離)→PASS 自動戳+commit★;連續兩輪 FAIL 才落 pending 喊人(Enzo:都靠人工閘難免疏漏,人=兜底非主閘)
  KEY:成本錨——乾淨 agent 一篇 ~10 分鐘/1-2 美金(今天實測),對照 orchestrator 一輪 34-68 美金;零新演算法,全現成零件(gov --nags 資料同源、claude -p 派工、self-audit 戳)
  DEP:[[Systems/autonomous-iteration-loop]]｜governance/autonomous-loop.sh
plan_refs: []
related:
  - "[[Systems/autonomous-iteration-loop]]"
tags:
  - type/project
  - status/doing
decisions:
  - content: FAIL 路徑改全自動:審→修(另一 agent)→複審(第三個乾淨 agent,maker/checker 分離)→PASS 自動戳+commit;連續兩輪 FAIL 才落 pending 喊人(人=兜底非主閘)
    id: d1
    context: v1 設計 FAIL→pending 等人放行;Enzo 裁:都靠人工閘難免疏漏——pending 匣一樣會躺(44 天空轉正是人工閘失效的實證),偵測到不足就該自己審自己放行
    why_chosen: 機械不靠自覺(設計原則 2);自動放行的誠實線=修者不自驗+乾淨複審;人保留在連續失敗的逃生梯
    decided: 2026-08-24
    valid: true
---
# 自足性審計閉環_計劃

> 白話:體檢每天喊「這篇筆記該找沒背景的人重新確認」,喊了一個半月沒人動——今天真的派人去看,
> 兩篇全是爛的。所以把「派沒背景的 agent 去看」變成每週自動的事:站得住自動蓋章,站不住把
> 修正建議放進待放行匣等人。機器修筆記有三道韁繩(修者不自驗、乾淨複審、範圍刀);蓋的章寫明是 agent 看過。(v1「機器不改筆記」已被 d1 取代)

## 症狀(會翻紅的指令)

```
python3 scripts/lumos gov --nags 14 --since 120
```
2026-08-24 前:兩組 44/40 天空轉(546/499 次)。本案成功=同款空轉結構性不再累積(≥14 天即有審計紀錄)。
佐證:2026-08-24 手動派審 2/2 站不住(governance/review-reports/self-audit/ 兩份報告,11 處漂移)。

## 設計(v4;r2 五席 37 條折入後版)

**架構**:全邏輯在 `governance/autonomous_loop/selfaudit.py`(subprocess timeout;test_autonomous_loop 直接 import 測);
autonomous-loop.sh 每日進場呼叫 3 行(配額按週,見 §4)。

1. **選目標——CLI 唯讀出口(r2 arch major:Env 跨層 import 是治理模組第一例,收掉)**:
   前置重構:Check S 判定抽純函式 `_self_audit_lists(notes) -> (missing: [rel], stale: [(rel, sa_date, upd)])`
   (★不碰 gov_events——落帳與顯示字串留在 run_doctor 端用原始元組重建,r2 s1f3/s2f1/Codex f3★);
   新唯讀子指令 `lumos self-audit --candidates --json` 輸出 PR 排序候選(rel、stem、repo_rel 三欄——檔名用 stem、
   CLI 呼叫用 rel、範圍刀用 repo_rel,三個口徑各給各的,s2f2/s2f3);selfaudit.py ★subprocess 拿 JSON,零 import★
   (治理模組全 subprocess 慣例)。測試:①CLI 出口與 doctor 同集+★doctor --ci 後 governance-log 仍有 check-s 事件★。
2. **審計/複審派工——探針式沙盒(r2 s2f7:唯讀工具面砍掉手動版最強的實測手段;Codex f1:唯讀 agent 寫不了報告)**:
   照 `scenario_probe.make_sandbox` 三層隔離先例建**沙盒副本**(無 remote/假身份/pre-push 擋),agent 在沙盒內
   `--allowedTools "Read,Grep,Glob,Bash"`(Bash 可實測 CLI 行為——手動版 export 那條就是跑出來的;主樹零風險);
   ★報告由 selfaudit.py 落盤★(agent 只回文字;`--output-format json` 的 result 原子寫入
   `governance/review-reports/self-audit/<日期>-<stem>.md`;逾時/is_error=無檔=FAIL);
   認證 env 照 orchestrator 兩行 export;`subprocess.run(timeout=900)`。
3. **VERDICT**:真相源=selfaudit.py 落盤的報告檔;文法=最後一個非空行 `^VERDICT: (PASS|FAIL)$`;
   正常結束判定=json `is_error` 欄(s2 minor 補);半寫/矛盾/多 VERDICT→FAIL+log 死因。
4. **處置(d1;★「連續兩輪」=同次派工內審+複審兩關,s1f1 講死★)**:
   - PASS → `lumos self-audit <rel> --model auto-<model>`(★連字號前綴,保住 `<model>/<date>` 單斜線文法;
     auto- 前綴既有慣例——arch r2/s2f8 收掉 auto/ 斜線版★)。
   - FAIL → 修復鏈:★修 agent 在 `git worktree`(從 HEAD 建)★內修該篇(allowedTools 加 Edit;
     範圍刀=`git -C <wt> diff --name-only` 與候選的 repo_rel ★同空間嚴格相等★,越界=丟 worktree 主樹零污染,
     r2 Codex f2/s2f2 的「事後刀砍不回」由 worktree 結構性解);
     → ★複審 agent 也在該 worktree★(從 HEAD 建=結構性看不到主樹未提交的報告/pending,s1f2 的隔離變機械)
     → 複審 PASS=檔案 copy 回主樹+蓋章+commit(照既有自動 commit 格式,訊息 trailer 記 audited/fixed/reverified 三 model,arch minor)
     → 複審 FAIL=報告落 `governance/pending/selfaudit/<日期>-<stem>.md`(★stem 不含斜線,s2f3;selfaudit.py 開頭
     `os.makedirs(exist_ok=True)`,s2f4★)。
   - ★跳過判定=pending/selfaudit/ 內該 stem 有未歸檔檔案★(天然可逆:人歸檔即恢復;不建 skip jsonl——
     arch r2 ⚠「可逆 vs covered 永久」由此消解)。
   - ★週帳 `governance/selfaudit-week.jsonl`(r2 s2f6/Codex f4 定形)★:每行 `{"week","stem","verdict","ts"}`;
     配額=`N - 本週行數`(N=2 寫死)——每日進場只補殘額,兩篇做完同週選零(★真正鎖 2/週;不設 run_nags 式整段週戳★);
     喊人=每日進場檢查 pending/selfaudit/ mtime>3 天,★每檔每週最多喊一次★(同 jsonl 記 `{"week","stem","nagged":true}`,Codex f6)
     ——SLA 真實 3-4 天(s1f6/s2f5 的「週頻=10 天」由每日進場消解)。
5. **成本**:每篇 log 一行白話「本篇審計成本:US$x | y 分鐘 | z tokens」(同 orchestrator log 慣例)+
   `canary record --tokens/--wallclock-min` 落帳;★美元重驗來源=log grep,不宣稱 ledger 存 USD★(Codex f7)。
6. **執行模式白名單(d1 授權)**:selfaudit.py 只准寫:報告檔/`pending/selfaudit/`/週帳 jsonl/self_audit 戳/
   修復 copy 回的那一篇;loop 頭部裁定註解加例外行,★帶重驗條件★(arch minor):「三個月內範圍刀曾觸發或
   人抽查發現自動 PASS 誤放 → 回審本例外」。
7. **doctor 文案**:Check S 標題「被不知道背景的人重新確認」→「被不知道背景的人或乾淨 agent 重新確認」。
8. **觀測條款(r1 Codex f9 補折——2/2 樣本撐不起誤放率宣稱,s1f4 抓到漏折)**:首月自動 PASS 的報告全留檔,
   人抽查;抽到誤放 → N 改 0 關自動、回人工模式,該例寫進本計劃。
## 不做什麼(邊界)

- 自動修僅限被審那篇筆記正文/frontmatter(範圍刀機械擋);不動 code、不動其他筆記;不動 Check S 本身;不碰 design/code-loop;不審 Systems 以外 type(Check S 口徑);★Landmark repo 不在本案(30 篇 system 另議)★。
- 不新增評測尺——成功看 nags 清單與 pending 產出,兩者都既有。

## 連動(s3 r1)

- `Systems/autonomous-iteration-loop` 筆記加本機制一節;doctor Check S 文案改(§7);DRYRUN-OBSERVE.md 記首輪實跑;
  backlog「腐化偵測延遲」條標 covered;★Landmark repo 不在本案★(邊界節已留句);
  pending 檔處置=歸檔到 `pending/archive/`(既有慣例),v1「可直接刪」作廢;PASS/FAIL 記 governance-log 事件(gate=selfaudit)。

## PRIOR-ART

`PRIOR-ART: borrow-design`——派工/週戳/LINE 全抄 run_nags/run_probe 既有慣例;判定同源 Check S(不另立);
「agent 審+人放行修正」= design-loop 收貨模式的單席簡化。零新依賴。

## 測試(草)

(全部走 `test_autonomous_loop.py` 直接 import selfaudit.py;CLI 出口部分走 subprocess)
①`_self_audit_lists` 純函式:與 doctor 同集+★doctor --ci 後 governance-log 仍有 check-s 事件(落帳回歸)★
②CLI `--candidates --json`:missing/stale/PR 序/三欄口徑(rel/stem/repo_rel)③選目標:配額=N-本週行數、pending 存在跳過、兩篇完成同週選零
④VERDICT 文法:PASS/FAIL/缺行/半寫/多行/is_error(全 fail-closed)⑤PASS→戳 auto-<model> ⑥FAIL 鏈:worktree 修→複審 PASS→copy+戳+commit;複審 FAIL→pending+主樹零污染
⑦範圍刀:worktree diff 越界→丟 worktree、主樹無變化(正案例:合法修不誤判——repo_rel 同空間)⑧gap_select 不連坐(子目錄 glob 非遞迴)
⑨週帳:中斷後補殘、喊人每檔每週一次 ⑩成本落帳一筆 ⑪翻紅釘:fail-closed 反轉→④紅;範圍刀拿掉→⑦紅;gap_select glob 改遞迴→⑧紅。

## 實務隱患

- **守衛面**:自動蓋章會不會洗掉真問題?→ PASS 才蓋,prompt 是「找站不住」框架(2/2 抓到證明有牙);auto/ 前綴留追溯。
  ★自動修會不會把筆記改壞?★→ 三層:修者不自驗(乾淨複審)、範圍刀(只准動該篇,diff 越界作廢)、lint 必綠;
  最壞情況=修錯但複審也漏 → 筆記錯法換一種,但有 git 史+commit 訊息三 model 署名可回溯,且下輪 Check S 過期會再抓。
  人工閘的對照組不是「零錯」——是 44 天沒人看(實證):自動鏈的錯誤率要跟「根本沒人處理」比,不是跟完美比。
- **成本**:N=2/週×~2 美金,月 ~16 美金,可忽略;timeout 護欄。
- **回滾**:N=0 寫死值改 0 即整段關;pending 檔歸檔 pending/archive/(既有慣例;v1「可直接刪」作廢)。
- **併發**:週戳+循序派工,無共享寫。

## 審計修正紀錄

### r1(2026-08-24;s1/s2/s3 + arch + Codex 五席,審 v2)
s1 7(3 blocker)/ s2 10(3 blocker)/ s3 10(1 blocker)/ arch 5(1 major)+3⚠ / Codex ★9★(1 blocker+8 major;r1 帳誤記 6——r2 s3f1 抓到,同款計數錯第三犯,帳只追加、以此為準)。全折、零放行,v3 重寫設計節:
**A 判定 import 不可行**(五席同抓:Check S 在 950 行閉包內)→ 前置重構抽 `_self_audit_lists` 頂層函式+翻紅釘;
**B pending 連坐凍結自主 loop**(s1/s2/s3 三席 blocker:pending_exists glob 任何 .md 就停選 gap——38 天病灶的新觸發源)→ 子目錄+不連坐測試+自帶喊人;
**C 執行模式無合法路徑**(Codex blocker:loop 鎖 dry-run、PASS 要寫檔)→ 白名單例外授權=d1 人裁,範圍刀機械驗,不解整體禁令;
**D bash 不可測+timeout 無落地**(s2 f2 blocker+f9 major:macOS 無 timeout、claude -p 無旗標、母版零測試)→ 全邏輯進 python 模組;
**E 語意偷換**(s1f4 blocker:doctor 說「人確認」、-auto 是 agent)→ 文案改「人或乾淨 agent」+安全論證訂正;
**F 工具面未定**(arch major/s2f3:照 orchestrator 模板抄會把 Edit 給唯讀審計員,confused-deputy 裁定在同檔沒被引用)→ 審/複審唯讀、修 agent 才有 Edit;
**G VERDICT 文法與真相源**(Codex f3/s2f6)→ 報告檔尾行嚴格正則;**H 重派抑制**(s2f5/s1f6)→ skip 檔照 covered.jsonl;
**I 成本落帳**(s2f4)、**J per-篇週戳**(s2f10)、**K 立案宣稱錯**(s3f4:「loop 兩次啃不動」不實,改 44 天實證)、
auto/ 前綴(arch)、knob 改寫死(arch)、認證 env 兩行(s2f3)、連動清單(s3 七項)、mkdir(s2f8)。
★教訓:v1「全現成零件拼裝」的自評,被五席拆出 38 條(7+10+10+5+9 逐份數;初記 31 同款抄摘要錯)——「拼裝」最大的坑不在零件在接縫(pending 連坐/dry-run 合約/閉包 import),
拼之前要把每個零件的「隔壁是誰」看一遍。★

### r2(2026-08-24;s1/s2/s3 + arch + Codex,審 v3)
逐檔數:s1 7(2 blocker)/ s2 8(3 blocker)/ s3 9(0 blocker 5 major)/ arch 6+1⚠(2 major)/ Codex 7(4 blocker)=37 條。全折、零放行,v4 重寫設計節:
**A Env 跨層 import 治理模組第一例**(arch)→ CLI 唯讀出口 `--candidates --json`,subprocess 慣例歸位;
**B 唯讀工具面自相矛盾**(Codex f1 寫不了報告+s2f7 砍掉實測手段)→ 報告由 wrapper 落盤;審計/複審進探針式沙盒,Bash 解禁而主樹零風險;
**C 範圍刀砍不回+路徑空間錯位**(Codex f2+s2f2)→ 修復進 worktree,刀驗 worktree diff、repo_rel 同空間,越界=丟 worktree;
**D 複審隔離只是嘴上**(s1f2)→ 複審同 worktree(HEAD 建,結構性看不到報告);
**E 配額與週戳**(Codex f4 每日跑會 14 篇/週+s2f6 無 schema+s1f6/s2f5 SLA 10 天)→ 週帳 jsonl 定形、每日進場補殘、喊人每檔每週一次;
**F 抽函式切口**(s1f3/s2f1/Codex f3 gov_events+形狀互斥)→ 純函式回原始元組、落帳留 doctor、測試①加落帳回歸;
**G d1「連續兩輪」語意**(s1f1)→ 講死=審+複審;skip jsonl 刪除,pending 檔存在即跳過(可逆,arch ⚠ 消解);
**H auto/ 斜線破文法**(arch/s2f8)→ auto- 連字號;pending 檔名用 stem(s2f3);mkdir(s2f4);成本重驗=log grep(Codex f7);
**I r1 漏折補**(s1f4:Codex r1 f9「2/2 撐不起誤放率」)→ 觀測條款首月抽查;例外註解帶重驗條件(arch);三 model 署名走 trailer(arch);
s3 九條(帳面/殘句)已於輪中先折。★教訓:v3 的「隔離」「範圍刀」都是宣稱層——r2 全部換成結構層(沙盒/worktree/同空間比對),
「寫著安全」和「構造上安全」的差距就是這 37 條。★

## 下一步

r3(上限輪):五席審 v4 delta。過了實作;沒過攤人裁。
