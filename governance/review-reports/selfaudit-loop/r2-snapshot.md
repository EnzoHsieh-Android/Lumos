---
type: project
status: doing
created: 2026-08-24
updated: 2026-08-24
summary: |-
  FLAG:DECISION
  KEY:立案(2026-08-24 Enzo「好」)——Check S 是「喊了等人看」:兩篇樞紐筆記被喊 44/40 天(546/499 次)沒人理,終於派乾淨 agent 審=2/2 全站不住、11 處真漂移(兩處「照做出錯」級)。抽檢命中率 100%,問題不在閘在「沒人看」;backlog 的「腐化偵測延遲」gap 與這題同主題(★s3 r1 訂正:該 gap 從未被 loop 試過——兩次啃不動的是寫閘與治理帳,立案理由改為 44 天實證而非 loop 敗績★;落地時該 gap 標 covered)
  KEY:方案(★d1 裁定版:全自動閉環★)=每週派乾淨 agent 審「從未確認+過期」功能筆記(N=2/週,PR 高者先)——PASS→自動戳(-auto 留痕);FAIL→★另一 agent 修筆記→第三個乾淨 agent 複審(maker/checker 分離)→PASS 自動戳+commit★;連續兩輪 FAIL 才落 pending 喊人(Enzo:都靠人工閘難免疏漏,人=兜底非主閘)
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
> 修正建議放進待放行匣等人。機器不改筆記,只蓋「我看過還行」的章。

## 症狀(會翻紅的指令)

```
python3 scripts/lumos gov --nags 14 --since 120
```
2026-08-24 前:兩組 44/40 天空轉(546/499 次)。本案成功=同款空轉結構性不再累積(≥14 天即有審計紀錄)。
佐證:2026-08-24 手動派審 2/2 站不住(governance/review-reports/self-audit/ 兩份報告,11 處漂移)。

## 設計(v3;r1 五席 31 條折入後版)

**架構裁定(s2 blocker×2 定調)**:派工與處置全部在 ★python 模組★ `governance/autonomous_loop/selfaudit.py`
(macOS 無 timeout 指令、claude -p 無 --timeout 旗標——全 repo 唯一真 timeout 先例是 `scenario_probe.py` 的
`subprocess.run(timeout=)`;bash 函式也無法單元測,run_exam/probe/nags 三個母版全零測試);
autonomous-loop.sh 只加 3 行呼叫(週戳同 run_nags)。

1. **選目標**:★前置重構(五席同抓)★——把 Check S 判定從 `run_doctor` 閉包抽成頂層函式
   `_self_audit_lists(env) -> (sa_missing, sa_stale)`(照 `about_code_expired` 先例:抽出後 run_doctor 與外部共用,
   翻紅釘:兩邊算出不同集→紅);selfaudit.py 用 `SourceFileLoader` 載入呼叫(canary_calibration/k1_stop_replay 既有先例)。
   PR 排序沿 `_graph_pagerank`;配額 `N=2` 寫死+註解(loop shell 慣例,不開 env knob——arch);
   ★重派抑制(s2f5/s1f6)★:照 `covered.jsonl` 同款結構開 `selfaudit-skip.jsonl`——已有未結案 pending 檔的篇跳過,
   人清 pending 後自動恢復;測試釘「連續 FAIL 不重選」。
2. **派工**(selfaudit.py 內 subprocess):`claude -p --output-format json`;
   ★工具面(arch major/s2f3)★:審計與複審 agent `--allowedTools "Read,Grep,Glob"`(唯讀,照 ai-governance-research.sh
   唯讀模板精神;不給 Edit/Bash/Agent——「不動筆記」是工具層擋不是 prompt 口頭);修 agent 加 `Edit`(仍無 Bash/Agent);
   ★認證 env 照 orchestrator 兩行 export 同款★(走 Max 訂閱;成本錨的量測情境一致);
   `timeout=900` + `except TimeoutExpired` → 當 FAIL(fail-closed)。
   prompt=今天手動版的**方法論**+★新增★機械判定行(s1f3/s3f3 訂正:「同款」指方法論;VERDICT 是本案新規格,
   今天兩份報告沒有它——實據誠實標)。
3. **VERDICT 規格(Codex f3/s2f6 釘死)**:★真相源=報告檔★(留痕稽核物;stdout 只判斷是否正常結束);
   文法=報告檔最後一個非空行完全匹配 `^VERDICT: (PASS|FAIL)$`;半寫檔/兩來源矛盾/正文出現多個 VERDICT→FAIL+log 死因。
4. **處置(d1:全自動,人是兜底)**:
   - PASS → `lumos self-audit <篇> --model auto/<model>`(★前綴 auto/,repo 既有 auto- 前綴慣例;arch:-auto 後綴無先例★)。
   - FAIL → 修復鏈:修 agent(帶報告,Edit 只該篇;修完 selfaudit.py 跑 `lumos lint` 必綠+★範圍刀:`git diff --name-only`
     只准含該篇,越界=整輪作廢★)→ 第三個乾淨複審 agent(不給報告與修法)→ PASS=蓋章+commit(訊息三 model 署名)
     → 複審仍 FAIL=落 pending、記 skip 檔、本篇不再自動重試。
   - ★pending 位置(三席 blocker)★:`governance/pending/selfaudit/<日期>-<篇>.md`(子目錄——`gap_select.pending_exists`
     只 glob `pending/*.md` 非遞迴,實測不連坐;★測試釘「selfaudit pending 存在時 gap_select 照常選」★);
     >3 天喊人:★selfaudit.py 每次跑自帶檢查+LINE★(s2f7:既有喊人只在 backlog 空時觸發,不穩定——本案不依賴它)。
   - 每篇處置完即記週戳分錄(★per-篇完成戳,非整輪頭尾★——s2f10:N=2 中途死掉,下次只補沒做完的那篇,不重派已完成的)。
5. **成本落帳(s2f4)**:每篇跑完照 orchestrator 慣例 `lumos canary record` 帶 `--tokens/--wallclock-min`
   (loop 帳既有欄);成本錨 $1-2/篇 由帳目持續重驗(鐵則:承認風險附回頭看條件)。
6. **執行模式(Codex f1 blocker)**:autonomous-loop.sh 現鎖 dry-run(2026-07-29 confused-deputy 裁定)、PASS 要寫檔——
   ★白名單例外,授權=d1 人裁(「自己審自己放行」)★:selfaudit.py 只准寫三類(self_audit 戳/被審那篇/`pending/selfaudit/`+skip 檔),
   範圍刀機械驗;loop 頭部裁定註解加一行引用 d1 與白名單。不解除整體禁令。
7. **doctor 文案(s1f4 blocker)**:Check S 訊息「被不知道背景的人重新確認」改「被不知道背景的人或乾淨 agent 重新確認」;
   本計劃安全論證同步訂正:PASS-auto=「乾淨 agent 看過」,不是「人看過」——Check S 的保證層級本來就是這層,措辭不得偷換。
## 不做什麼(邊界)

- 自動修僅限被審那篇筆記正文/frontmatter(範圍刀機械擋);不動 code、不動其他筆記;不動 Check S 本身;不碰 design/code-loop;不審 Systems 以外 type(Check S 口徑)。
- 不新增評測尺——成功看 nags 清單與 pending 產出,兩者都既有。

## 連動(s3 r1)

- `Systems/autonomous-iteration-loop` 筆記加本機制一節;doctor Check S 文案改(§7);DRYRUN-OBSERVE.md 記首輪實跑;
  backlog「腐化偵測延遲」條標 covered;★Landmark repo 不在本案(它 30 篇 system 另議,留一句)★;
  pending 檔處置=歸檔到 `pending/archive/`(既有慣例),v1「可直接刪」作廢;PASS/FAIL 記 governance-log 事件(gate=selfaudit)。

## PRIOR-ART

`PRIOR-ART: borrow-design`——派工/週戳/LINE 全抄 run_nags/run_probe 既有慣例;判定同源 Check S(不另立);
「agent 審+人放行修正」= design-loop 收貨模式的單席簡化。零新依賴。

## 測試(草)

(全部走 `test_autonomous_loop.py` 直接 import selfaudit.py 的既有模式——s2f9:bash 層無可測先例,故邏輯全在 python)
①`_self_audit_lists` 抽出後與 run_doctor 同集(翻紅釘:改一邊→紅)②選目標:missing/stale/PR 序/配額/skip 檔跳過
③VERDICT 文法:PASS/FAIL/缺行/半寫/多 VERDICT/兩源矛盾(全 fail-closed)④PASS→戳 auto/<model> ⑤FAIL 鏈:修→複審 PASS→戳+commit;複審 FAIL→pending/selfaudit/+skip
⑥範圍刀:diff 越界→整輪作廢 ⑦★selfaudit pending 存在時 gap_select 照常選(不連坐)★ ⑧per-篇週戳:中斷後只補殘篇
⑨成本落帳一筆 ⑩翻紅釘:fail-closed 改 fail-open→③翻紅;範圍刀拿掉→⑥翻紅;gap_select glob 改遞迴→⑦翻紅。
shell 段落照 t_install_global_hook_sync 模式(bash -n+函式抽測)。

## 實務隱患

- **守衛面**:自動蓋章會不會洗掉真問題?→ PASS 才蓋,prompt 是「找站不住」框架(2/2 抓到證明有牙);-auto 留追溯。
  ★自動修會不會把筆記改壞?★→ 三層:修者不自驗(乾淨複審)、範圍刀(只准動該篇,diff 越界作廢)、lint 必綠;
  最壞情況=修錯但複審也漏 → 筆記錯法換一種,但有 git 史+commit 訊息三 model 署名可回溯,且下輪 Check S 過期會再抓。
  人工閘的對照組不是「零錯」——是 44 天沒人看(實證):自動鏈的錯誤率要跟「根本沒人處理」比,不是跟完美比。
- **成本**:N=2/週×~2 美金,月 ~16 美金,可忽略;timeout 護欄。
- **回滾**:knob=0 整段關;pending 檔可直接刪。
- **併發**:週戳+循序派工,無共享寫。

## 審計修正紀錄

### r1(2026-08-24;s1/s2/s3 + arch + Codex 五席,審 v2)
s1 7(3 blocker)/ s2 10(3 blocker)/ s3 10(1 blocker)/ arch 5(1 major)+3⚠ / Codex 6(1 blocker)。全折、零放行,v3 重寫設計節:
**A 判定 import 不可行**(五席同抓:Check S 在 950 行閉包內)→ 前置重構抽 `_self_audit_lists` 頂層函式+翻紅釘;
**B pending 連坐凍結自主 loop**(s1/s2/s3 三席 blocker:pending_exists glob 任何 .md 就停選 gap——38 天病灶的新觸發源)→ 子目錄+不連坐測試+自帶喊人;
**C 執行模式無合法路徑**(Codex blocker:loop 鎖 dry-run、PASS 要寫檔)→ 白名單例外授權=d1 人裁,範圍刀機械驗,不解整體禁令;
**D bash 不可測+timeout 無落地**(s2 兩 blocker:macOS 無 timeout、claude -p 無旗標、母版零測試)→ 全邏輯進 python 模組;
**E 語意偷換**(s1f4 blocker:doctor 說「人確認」、-auto 是 agent)→ 文案改「人或乾淨 agent」+安全論證訂正;
**F 工具面未定**(arch major/s2f3:照 orchestrator 模板抄會把 Edit 給唯讀審計員,confused-deputy 裁定在同檔沒被引用)→ 審/複審唯讀、修 agent 才有 Edit;
**G VERDICT 文法與真相源**(Codex f3/s2f6)→ 報告檔尾行嚴格正則;**H 重派抑制**(s2f5/s1f6)→ skip 檔照 covered.jsonl;
**I 成本落帳**(s2f4)、**J per-篇週戳**(s2f10)、**K 立案宣稱錯**(s3f4:「loop 兩次啃不動」不實,改 44 天實證)、
auto/ 前綴(arch)、knob 改寫死(arch)、認證 env 兩行(s2f3)、連動清單(s3 六條)、mkdir(s2f8)。
★教訓:v1「全現成零件拼裝」的自評,被五席拆出 31 條——「拼裝」最大的坑不在零件在接縫(pending 連坐/dry-run 合約/閉包 import),
拼之前要把每個零件的「隔壁是誰」看一遍。★

## 下一步

r2:五席審 v3(delta=設計節全重寫/連動/測試)。過了實作。
