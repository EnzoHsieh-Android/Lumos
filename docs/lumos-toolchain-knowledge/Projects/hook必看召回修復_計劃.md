---
type: project
status: done
created: 2026-08-07
updated: 2026-08-07
tags:
  - type/project
  - status/done
summary: |
  KEY:治全系統唯一紅燈(hook P@8 0.639/must recall 0.6)——2026-08-07 驗屍 11 筆必看 miss 歸因:①直連被動態閾砍 6 筆(direct 基底 0.30+L≈0<動態閾 0.65×max_free;v1.1/v1.2 買精度的明碼代價)②裸檔名 1 筆③連結缺失 4 筆(r1 勘誤 E20 改判)
  KEY:兩帖藥(r1 折入後)=R1 直連保底席(最終 free 集零 direct 觸發;準固定席外掛 pins+rescued+free,--top 例外明示;rescued 欄位穿透 ranked schema+hook 顯示跟進)+R2 裸檔名容錯(反查端自建抽取路不動共用 _refcheck_scan;git ls-files 母體唯一才比對;hit provenance 穿透);第三帖(Drift 符號錨/TLR 補連結)deferred 另立
  KEY:r1 panel(2026-08-07):3 caught/s1 missed(a 型連兩日有席漏);15 條全折 max=blocker(R2 修錯層/E20 分類錯→②1 筆③4 筆/R1 名額矛盾→外掛模型/A-B harness knob+top8 對齊/雙庫偏離明示)
  KEY:r2 delta(2026-08-07):2 caught/s3 missed(b 型旗標,引句含針卻未點性質);12 條全折 max=blocker(rescued×pinned 二分桶交互→第三桶明文/gate② split 定 held+R2 held 不可見性聲明/rows 落地 --dump-rows/top8 touchpoint 繼承/多 direct 論證勘誤/母體數字縮尺)
  KEY:裁決=考卷 A/B 沿 PPR 慣例(train 網格→held 確認→±0.02 帶寬→輸刪碼);不動閾/基底/固定席;不為過卷補語料引用(Goodhart)
  FLAG:DECISION
---
# hook必看召回修復_計劃

> 緣起:2026-08-07 全系統掃描——每週考卷唯一連續紅燈=hook P@8 0.639(閘 0.70)、must_in_out_recall 0.6。對 goldset 快照(285d429c)全量重放驗屍,11 筆必看 miss 逐筆歸因,三種死法比例定案,藥按病開。

PRIOR-ART: ① 最小解層級——既有 impact --ranked 管線的謂詞/參數修改+考卷 A/B 裁決,無新治理層、無新依賴(r2 措辭如實:機制面 R2 含反查器內一條新抽取路+一次 git 子行程,非「零新機制」);落點=`cmd_impact` ranked 分支 free/thresh 計算段(scripts/lumos ~11966 起)與 `_impact_reverse_lookup` token 比對(~11429)。裁決模式沿 [[Projects/檢索PPR邊權_計劃]] 慣例(train 網格→held 確認→±0.02 帶寬→輸=刪碼),**帶一處明示偏離**:勝出軸=must recall 非 P@8(本計劃修的是 recall 紅燈,P 是護欄非獎盃),見驗收線。② 內部 prior-art:[[Verification/2026-07-11_hook面v1.1轉正]]——v1.1 調參(閾 0.25→0.55/direct 基底 0.5→0.3)買精度 +20pp、代價 28/30→24/30;v1.2 再調緊(0.55→0.65)+3pp、代價 24/30→19/30——**紅燈=兩輪調參的合計帳單**(r1 勘誤:原文誤把兩刀記成 v1.1 一刀;來源節點的更正註警告過同款「數字沿用進新結論」漂移,又犯一次由 r1 抓回);固定席機制(合約/事故 direct 保送)已存在,本計劃的保底席為其無標記版之延伸。③ 世界解(2026-08-07 調研,列第三帖藥、本計劃不做):Drift(fiberplane)`路徑#符號@sha` 錨定+AST 指紋過期偵測;TLR(LLM 連結恢復,arXiv 2509.05585/2508.12232)——僅離線候選生成+人放行姿勢合法(同證據恆同分家規)。④ 裁定=borrow-design(裁決協定借自家、錨定思路借 Drift 但 deferred)。

## 驗屍證據(2026-08-07,快照 285d429c 全量重放,11 筆必看 miss)

| 死法 | 筆數 | 機轉 | 例 |
|------|------|------|-----|
| ①直連被閾砍 | 6 | 反查 direct 有中;direct 基底 0.30+L(delta code 字串 vs 中文筆記詞彙相似≈0)<動態閾(現行係數 `LUMOS_IMPACT_DYN_COEF`=0.65,閾=0.65×max_free,E14 當場=0.65×max_free 0.72≈0.468(r1 勘誤:pre-flight 的 ≈0.55 亦誤,實測 0.468);⚠ [[Systems/retrieval-ranking]] 節點仍記舊係數 .55,已過期待同步)→ 被砍。E14 全場僅 2 候選、前 8 有空位,唯一 direct 仍出局 | E14 `lint-watch-check.sh`→`lint-version-watch` raw 層 direct 命中、ranked 層消失 |
| ②檔名變體 | 1(r1 勘誤:原 2) | 節點以裸檔名 inline-code 引用(無 `/`),`_refcheck_scan` 抽取層直接濾掉(scripts/lumos:8859 `"/" not in token`)——不是比對層問題,是抽取層(r1 三席一致) | E18 `cross-family-audit`(`` `autonomous-loop.sh` `` 裸檔名) |
| ③連結缺失 | 4(r1 勘誤:E20 自②改判——`convergence-evidence-gate` 對 `cross_audit.py` 的唯一提及無反引號,非 inline-code,抽取機制天生看不見) | 節點壓根無機械可抓引用;hop 可達但衰減+L=0 | E05/E12 三筆+E20 |

> 語意鴻溝的真實老巢:delta=code 字串、節點=中文散文,BM25F 相似分近乎隨機——機制卻以 L 為 direct 的救生索。

## 兩帖藥(本計劃範圍)

### R1 直連保底席(治死法①;r1 重寫——原「名額外加又受 --top 上限」三席一致判自相矛盾)
- **席位模型=第三桶明文**(r2 折入,s3 blocker:現碼只有 pinned 布林二分桶,rescued 落錯桶則「被同一閾再砍」或「污染固定席語意」兩頭死):results 項帶 `rescued: true` **且 `pinned: false`**;`cmd_impact` 組裝順序=threshold/quota **只作用於非 rescued 的 free 項**,rescue 選取發生在截斷之後,`final = pins + free[:min(top, quota)] + rescued(≤N)`(top/quota 皆既有機制);`meta` 加 `rescued` 計數鍵。rescued 不佔 free 名額、不擠掉任何過閾者;明示這是對 `--top` 的例外(同 pins 的 safety_overflow 精神;原「仍受 --top 上限」句作廢)。eval 端沿 pinned 二分讀取不受影響——rescued 天然落 free 桶、**計入 P@8 母體=誠實計噪**(護欄①正是在考這件事);hook 顯示以 `rescued` 鍵分流,不靠 pinned。
- **觸發判定時點=截斷後的最終 free 集**(r1 折入:閾後截斷前判定會漏「過閾但被截」場景):最終 free 集 direct 數=0 且存在被閾砍/截的 direct → 觸發。
- **缺口定義**(r1 折入):=被閾砍或被截的 direct 節點總數;補入數=min(N, 缺口),取分數最高者(同分 tie-break 沿既有 free.sort 慣例 `(-score, hop, node)`,r2 折入);N 由 train 網格定(候選 1/2)。
- 每筆補入項標 `rescued: true`(**新增欄位**,r1 勘誤:原「沿 results 既有 origin 欄」係幽靈欄位——results 現有欄位為 node/kind/pinned/score/L/hop/contract,無 origin;rescued 為 ranked schema 新增,eval 讀 results 全集故自動計入 must_in_out,無需改 eval 碼)。
- **production 顯示跟進**(r1 折入,s3):`scripts/hooks/claude/impact-hook.py` 的 `build_ranked_context` 對 rescued 項加標示(如「⛑ 直連保底」)——不顯示=使用者分不出信心層級,違背設計初衷。
- 刻意保守:僅「最終 free 集零 direct」時觸發。(r2 勘誤:原句「多 direct 場景 free 集必有 direct」論證不成立——動態閾相對混池 max_free,高分 indirect 可把全部低 L direct 一起殺光,此時 rescue 照樣觸發且**應該**觸發;保守性的真實來源=零 direct 觸發條件+N 上限,非「多 direct 必不觸發」。測試補「多 direct 全滅→觸發」案例。)
- 固定席不動(合約/事故保送機制原樣)。

### R2 裸檔名容錯(治死法②;r1 重寫——原落點在比對層,三席一致判 blocker:裸檔名在 `_refcheck_scan` 抽取層就被 `"/" not in token` 濾掉(scripts/lumos:8859),比對層改了也是死碼)
- **落點=反查端自建第二條抽取路**,★不動共用的 `_refcheck_scan`★(它同時餵 refcheck CLI 與 G1 gate,動它=改三個消費者的合約):`_impact_reverse_lookup` 對節點文字另掃 inline-code 中**不含 `/` 的裸 token**,若 == 目標檔 basename 且該 basename 在母體內唯一 → 命中。同節點兩路都中時 provenance 取完整路徑優先(`hit: body-inline-code`),裸檔名僅在無完整路徑命中時記 `basename-match`(r2 折入:單節點單筆去重的合併序明文)。
- **唯一性母體定義**(r1 折入,s2/s4):=`git ls-files` 追蹤檔集(排除 untracked/ignored——r2 勘誤:實測 tracked 529 vs 工作樹 725,原 2426/515 誤把 .git 內部物件算進母體、規模誇大近 10 倍;論證仍成立但如實縮尺:196 檔 ignored/untracked(dist//__pycache__/governance/reports 等)混入即可把唯一誤判歧義;repo 已有 get.sh/install.sh 真實重名例,該兩名天然跳過);大小寫敏感、路徑分隔一律 `/`。
- **provenance 穿透**(r1 折入,Codex):`_impact_reverse_lookup` 回傳型別由節點清單改為 `(node, hit)` 對,`cmd_impact` direct 組裝按實際來源標 `hit: body-inline-code|basename-match`(原無條件寫死 body-inline-code),ranked results 帶出 `hit` 欄——eval 可歸因的宣稱才落地。
- 治療射程如實:死法②經 E20 重分類後僅 1 筆(E18);R2 的 recall 貢獻上限=+1,主力仍是 R1 的 6 筆。

### 刻意不做(記帳防回鍋)
- 死法③(連結缺失)=第三帖藥:Drift 式符號錨/TLR 離線補連結——等 R1+R2 落地後看殘餘 recall 再議,另立計劃。
- 不動動態閾係數(現行 0.65;r1 勘誤:原句誤寫 0.55,照字面實作=改回舊係數=自違範圍刀)、不動 direct 基底(0.30)、不動固定席、不碰 search 面、不動共用抽取器 `_refcheck_scan`。
- 不為過考卷回頭補 goldset 語料的引用(污染考卷=Goodhart)。

## 實務隱患
- **併發/效能/資源**:R1=純排序謂詞無新 I/O;R2=新增一次 `git ls-files` 子行程+basename 索引(O(tracked 檔數) 單次,impact 呼叫內存活;如實承認新 I/O,r1 勘誤原句「無新 I/O」與後半自相矛盾)。git 缺席 → R2 degrade 為不啟用(裸檔名不比對),R1 不受影響。
- **[self-governance]**:排序 advisory+考卷機械裁決;最壞=兩臂皆輸、刪碼零殘留(沿 PPR 前例)。誤救(rescued 進了不相關節點)=P@8 掉,考卷會抓。
- **[prod-irreversible]**:不適用,純讀+git 可逆。

## 審計修正紀錄
- **pre-flight(2026-08-07,機械排乾,不算 loop findings)**:①動態閾數字勘誤——當時記「0.55 是 E14 當場閾值」,現行係數實為 0.65(v1.2 調緊)(r1 再勘誤:0.55 亦誤,實測當場閾=0.468,見驗屍表);連帶發現 [[Systems/retrieval-ranking]] 節點仍記舊係數,列同步義務 ②「既有 ls-files 快取」不存在,改為如實承認新建一次性 basename 索引 ③R1 touchpoint 行段修正+刪 `_reco_fused` 誤指(那是 dormant 的推薦面) ④裁決規則補「平局不轉正」並明示偏離 PPR 慣例之處(勝出軸=recall)。

## 審計修正紀錄(r1)
- **r1(2026-08-07,panel:3 sonnet(通才/正確性/整合)+Codex 外家;canary 3 caught / **s1 missed**(a 型假小節引用,連兩日 a 型有席漏——進型別帳);去重 15 條全數折入,存活 max=blocker,全屬機械證實/多席一致路由免辯方)**:
  - [blocker] R2 修錯層——裸檔名在 `_refcheck_scan` 抽取層被濾(8859 行),比對層加分支=死碼,連自舉的 E18 都治不好(3 席一致)→ R2 重寫:反查端自建第二條抽取路,不動共用抽取器。
  - [blocker→major] E20 死法分類錯——引用無反引號=死法③非②(3 席)→ 驗屍表改 ②1 筆/③4 筆;R2 射程如實=+1 上限。
  - [major] R1「名額外加又受 --top 上限」自相矛盾(4 席全報)→ 重寫為準固定席外掛模型,明示 --top 例外。
  - [major] rescued「沿 origin 欄」=幽靈欄位+hit 在 ranked 路徑丟失(Codex)→ schema 穿透明文。
  - [major] production hook 不顯示 rescued/hit(s3)→ impact-hook.py 顯示跟進入範圍。
  - [major] PPR 慣例第二處偏離(雙庫)未明示(s3+Codex)→ 補明示+單庫理由+措辭降級。
  - [major] A/B 無 harness/knob、eval top50 與 hook top8 不同構(s3+Codex)→ env knob 兩枚+--top 8 對齊。
  - [major] 「+1 筆」與 history rounded 比例不相容(Codex)→ 整數逐題 rows 對帳。
  - [major] v1.1/v1.2 兩刀誤記一刀(s1)→ 歸因拆開。 [major] E14 閾值 pre-flight 勘誤仍錯(s2 實測 0.468)→ 再勘誤。 [major] 範圍刀「不動閾值(0.55)」舊值自違(Codex)→ 改 0.65。 [major] basename 母體未定義(s2+Codex)→ git ls-files+大小寫敏感+degrade。
  - [minor×3] R1 判定時點定截斷後;「缺口」=被閾砍/截 direct 總數;held 刻度 5pp 粗如實記。
- **r2 delta(2026-08-07,panel:3 sonnet(邊界/harness/schema 鏈)+1 全局哨兵;canary 2 caught / **s3 missed**(b 型旗標,引句含針未點性質);12 條全折 max=blocker,全機械證實免辯方)**:
  - [blocker] rescued 與現碼 pinned 二分桶交互未定義(pinned:false 被同閾再砍/pinned:true 污染固定席)(s3)→ 第三桶明文:rescued 鍵分流+threshold/quota 只作用非 rescued+meta 計數鍵。
  - [major] gate② split 漏寫——held 讀法測不到 R2(E18 在 train)、全量讀法=資料洩漏(s1)→ 定 held+R2 held 不可見性如實聲明。
  - [major] 逐題 rows 無落地機制(erows 聚合即棄)(s2)→ eval 加 --dump-rows。
  - [major] top8 對齊未點名 touchpoint(eval:164 硬寫 "50";PPR 同款 blocker 教訓)(s3)→ 繼承修法明文。
  - [major] 「多 direct 必有 direct 存活」論證假(混池 max_free 反例)(s1)→ 勘誤+補測試案例。
  - [major] 回傳型別改動打斷既有 t_impact_reverse_lookup(s3)→ 同步改寫入交付。
  - [major] 母體佐證數字誤把 .git 物件計入、誇大近 10 倍(s1+s2)→ 縮尺 529/725。
  - [minor×5] tie-break 沿慣例、雙路 provenance 優先序、PRIOR-ART「無新機制」措辭如實、pre-flight 0.55 回指再勘誤、summary ②③舊值(哨兵)——全數折入。
- **fold 迷你核對(r1 收尾)**:折入腳本兩段 replace 無 assert 靜默失效(驗收線/審計紀錄一度只在 summary 打勾、body 未落地)——核對員抓回,重補;教訓=程式化折入必帶 assert。

## 合約候選清單(收斂時提名,候選≠已標——蓋章走 guard 流程與「不確定不標」鐵則)
- rescued 恆 pinned:false 且不進固定席統計/顯示(固定席語意=合約/事故機械保證,不可稀釋)。
- threshold/quota 永不作用於 rescued 桶;rescue 僅零 direct 時觸發。
- A/B 敗訴=刪碼零殘留(沿 PPR 墓碑慣例)。

## 驗收線(A/B;r1 重寫——補 harness 機制與兩處明示偏離)
- **A/B 開關=env knob**(沿 PPR 慣例使 history 自動記 knobs):`LUMOS_IMPACT_RESCUE_N`(0=off=A 臂;1/2=B 臂網格,轉正後預設寫死為選定值、knob 留逃生)、`LUMOS_IMPACT_BASENAME_MATCH`(0/1 同款)——均 LUMOS_IMPACT_ 前綴,`retrieval_eval.py` 的 knobs 記錄自動涵蓋。
- **top 對齊**(承接 PPR S4c 教訓):A/B 評測跑 `--top 8`(=production hook 視野)——**touchpoint=retrieval_eval.py:164 的硬寫字面值 `"50"` 改可傳參**(r2 折入:eval 的 k 參數與 --top 現況脫鉤,不改這行「top 對齊」只是敘述;PPR 計劃記過同款 blocker,這次把修法繼承到位)。
- gate(兩條合取,**兩條皆以 held 為準**——r2 折入:②原漏寫 split,held 讀法才是獨立驗收(train 已用於選 N,再計入勝出=資料洩漏)):①護欄=held 上 B 臂 P@8 不劣於 A 超 0.02(口徑如實:rescued 計入 P@8 母體,B 臂天然承壓,護欄考的就是誤救代價) ②勝出=held 上 Σmust_in_out(B)−Σmust_in_out(A)≥1(**整數逐題對帳**——history 只存 rounded 比例不可機械判 +1;**rows 落地機制=eval 新增 `--dump-rows <path>` 把逐題 erows 寫 JSON**(touchpoint retrieval_eval.py:198/223,現碼 erows 聚合後即棄,r2 折入),兩臂各 dump 一份對帳);兩條都過才轉正,只不劣不提升=平局留 baseline。
- **R2 的 held 不可見性如實聲明**(r2 折入):死法②唯一案例 E18 的 split=train——R2 的 recall 貢獻不會出現在 held 勝出帳裡;R2 機制正確性由單元測試證、train 面差異 descriptive 記錄不進 gate。held 勝出實質全靠 R1 的 6 筆(其中 held 佔比依卷面)。
- **兩處明示偏離 PPR 慣例**:①勝出軸=recall 非 P@8(修 recall 紅燈,P 是護欄非獎盃)②單庫 toolchain(PPR 既有裁定「凡動排序雙庫都要過」——Landmark edit 腿 harness(S4a repo 路由)未落地、前案封存;如實記單庫限制,轉正措辭同步降級「單庫視角下」)。
- 刻度如實:held edit 卷有效 9 題/must_total 20,+1 筆=5pp 跳動,勝負可能繫於單一案例——樣本粗,誠實記。
- 轉正=B 過 gate;記 `retrieval-eval-history.jsonl`;輸=刪碼留墓碑。
- 測試:`t_impact_direct_rescue`(最終 free 集零 direct 觸發/有 direct 不觸發/**多 direct 全滅→觸發**/缺口與 N 上限/rescued 欄位與第三桶排列/tie-break)、`t_impact_basename_match`(裸檔名唯一命中/重名跳過/untracked-ignored 不入母體/hit provenance 優先序/git 缺席 degrade);**既有 `t_impact_reverse_lookup` 同步改寫**(r2 折入:回傳型別改 (node,hit) 對會打斷其 `"x" in hits` 斷言,scripts/test_lumos.py:5823-5851,交付範圍內)。
