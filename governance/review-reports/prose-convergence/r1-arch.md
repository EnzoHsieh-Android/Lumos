# 架構對齊審查報告(prose-convergence r1;新紀律:blocking 聲明+三群)

## Q1/[S1] prose_lint 放 scripts/ 獨立腳本 — blocking:是|structural
引句:「design-loop 排乾步驟必跑;派工詞明寫「此掃描可及類別,席位不得報」。」
分界不是 vault-free(fold-check/refcheck 皆 vault-free 仍是子命令),是**角色**:排乾流程逐輪必跑的檢查現行慣例一律 lumos 子命令(SKILL:19 refcheck/pitfalls);[S1] 自認同崗位卻選獨立腳本=同一步驟兩種呼叫語法。命令數守衛不會擋(argparse 之外它是瞎的)——「守衛不擋」不能當理由,慣例指向子命令。

## Q2/d2 末輪驗收 — blocking:否 ⚠|structural
引句:「末輪(標準檔 r3)=**驗收輪**——只驗前輪修復與全量掃 blocking 級,不受理新的 minor 級」
不直接違反「只認機械閘和上限」,但:①與 panel 既有「K=2 第二輪審全量」是同件事還是疊加,沒講;②既有 early-exit(reference:333 實質收斂)明文僅限手動 loop,d2 沒標手動/自主範圍。⚠。

## Q2/d3 重寫出口 — blocking:是|structural
引句:「判定整份重寫而非逐條折補(Gilb:修補式折返=缺陷注入),重寫後重進迴圈。」
沒講重寫計不計上限:同 id 續數=違反「到頂沒過→停」;新 id 重算=無限重開的合法繞過口,正是「別無限燒」要防的。進 skill 前必須補死。

## Q3/d4 審計史外移 — blocking:是|structural
引句:「被審本體只含設計與裁定;審計修正紀錄/收貨紀律逐輪落 `governance/review-reports/<loop>/rN-fold.md`,計劃筆記只留一行指標。」
①規模:52 篇筆記在用(非六案),SKILL:26 流程強制;催生本案的那篇正是最完整範例。②三處機械依賴:_fold_mirror_sections(13453-13462,外移後鏡像段複查靜默沒東西查=假綠型失效)、_FOLD_AUDIT_RECORD_RE 排除域(13492-13494,存在本身證明設計預期內嵌)、_PITFALL_BLACKLIST(10812)。③spec 對「為何改」零對照現行慣例、零遷移成本、零回溯政策——分量不夠打贏慣性。

不對齊共 4 條,blocking 3 條。
