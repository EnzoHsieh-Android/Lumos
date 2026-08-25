---
type: project
status: doing
created: 2026-08-25
updated: 2026-08-25
summary: |-
  FLAG:DECISION
  KEY:立案(2026-08-25 Enzo「好」)——散文 spec 設計審六輪未機械收斂的病根=「零缺陷退出」判準(世界四傳統零一家用它審散文;2026 受控實驗:多輪重審散文全劣於單輪,FP+62%)。第一版解法全在「判準+前處理」層,**閘程式碼一行不動**(現行閘判「該輪 max≤minor=乾淨」本來就對,壞在審查員把精度級通膨成 major)
  KEY:五件=[S1] prose-lint 腳本(中文 weak-word/歧義掃描,席位不得再報該類)/[S2] design-loop skill 判詞(blocking 錨死+全 minor=乾淨明句+末輪驗收紀律+重寫出口)/[S3] 派工模板(每條 finding 聲明 blocking 是/否)/[S4] spec 紀律(行為斷言配例+瘦身:審計史外移)
  DEP:[[Systems/design-loop]]
plan_refs: []
related:
  - "[[Systems/design-loop]]"
tags:
  - type/project
  - status/doing
---
# 設計審收斂重定義_計劃

> 白話:設計審查迴圈對散文 spec 幾乎收斂不了(本 repo 六輪實測)。查了世界:五十年審查學派、期刊、IETF、Google 全都不用「乾淨才過」審散文——他們用的是密度門檻、非阻塞標籤、人裁。病根不在閘的程式,在審查員的判準與材料的形狀。本計劃五件(四件交付+一件實測驗收),全是文件/腳本層。

## 症狀(會翻紅的證據)

節點還原案兩迴圈共 6 輪、153 條全折仍未機械收斂;後期輪發現多為簿記精度級但被判 major 擋閘;每折一輪平均新生 1-2 處措辭問題(「半改句」單日五發)。世界解與實驗證據:`governance/review-reports/prose-convergence/web-research.md`(密度門檻/false positive pressure/二值判準一致性最高)。本案成功=下一個真實設計迴圈在上限內機械收斂,或以「新發現全 non-blocking」正常出場。

## PRIOR-ART(問世界)

已完成(2026-08-25 調研歸檔,見症狀節路徑):Fagan/Gilb 密度門檻與重寫出口、PBR(分視角閱讀)/EARS(受限句型)/ARM(NASA 弱詞掃描器)機器前移、AWS 與「以例為規」(Specification by Example)配例造 oracle、Google Nit 不擋、期刊兩輪上限+IETF 粗共識、CriticGPT(OpenAI 批評者模型)與 More-Rounds(2026 多輪重審受控實驗)。裁定=借用既有設計:全部收成判準文字與小腳本,不引外部工具(零依賴)。

## 核心裁定

- d1(候選):**第一版不動閘碼**。現行 panel/disposal 閘判「該輪存活 max ≤ minor=乾淨輪」語意本來正確;收斂失敗源於 major 通膨。解法=把「blocking」判準錨死在派工詞與 skill(「不改,實作者會做錯決定/做出壞系統嗎?不會→minor」),精度類由 prose-lint 前置絕育。回頭條件:落地後下一個真實設計迴圈若仍 3 輪不收斂、且人裁認定後期 major 半數以上實為精度級→升級為記帳層改法(blocking-set 欄位+閘讀殘餘密度)。
- d2(候選):末輪(標準檔 r3)=**驗收輪**——只驗前輪修復與全量掃 blocking 級,不受理新的 minor 級(實驗依據:多輪重審 +0.08 召回/+62% 假陽性)。
- d3(候選):**重寫出口**——估計殘餘 blocking(capture-recapture 或 找到×3 粗估)超過門檻(暫定 >5 條/千字)→判定整份重寫而非逐條折補(Gilb:修補式折返=缺陷注入),重寫後重進迴圈。
- d4(候選):**spec 瘦身鐵則**——被審本體只含設計與裁定;審計修正紀錄/收貨紀律逐輪落 `governance/review-reports/<loop>/rN-fold.md`,計劃筆記只留一行指標。行為斷言必配具體例(輸入→預期;寫不出例=該斷言自己是 major)。

## 落地件

1. [S1] `scripts/prose_lint.py`(新檔,現在不存在,本案交付物):零依賴掃描器——中文弱詞表(適當/必要時/原則上/盡量/相關/等等/視情況…)、未定義代詞密度、超長句;輸出行號+類別,恆 rc0(advisory)。design-loop 排乾步驟必跑;派工詞明寫「此掃描可及類別,席位不得報」。
2. [S2] `skills/lumos-design-loop/SKILL.md`+`reference.md`:blocking 判準錨句、「新發現全 minor=乾淨輪(照現行閘語意,明寫防通膨)」、末輪驗收紀律、重寫出口與粗估法、spec 瘦身鐵則。
3. [S3] `skills/lumos-design-loop/templates.md` §1:finding 格式加「blocking: 是/否+一句判準」;§7 panel 派工同步。
4. [S4] `skills/lumos-project-notes` 計劃筆記規範:行為斷言配例;審計史外移規則。
5. [S5] 實測驗收:下一個真實設計迴圈(非本案自審)按新制跑,收斂或正常出場→Verification 認領;若觸發 d1 回頭條件→立記帳層改法案。

## 實務隱患

- **判準靠 prompt 錨,審查員仍可能通膨**:無機械擋。回頭條件=d1 內建(下個迴圈實測裁)。
- **prose-lint 誤殺**(弱詞在引句/程式碼區塊內):掃描排除 code fence 與「引句:」行;首版詞表保守,寬鬆度由實測調。
- **末輪不受理新 minor 可能漏真問題**:漏的上限=minor 級(定義上不影響實作正確性);blocking 級末輪照收。
- **金流/對外/不可逆**:不涉及——純文件+advisory 腳本,可整體 revert。
- **本案自審的自指**:本 spec 用舊制審(新制未生效),但實踐新紀律(薄 spec/首輪分群/派工要求 blocking 聲明)——新舊並存一輪,留痕說明。

## 下一步

design-loop(編號 prose-convergence,tier standard——動審查紀律屬守衛面)→ 收斂或攤人 → 實作 [S1]–[S5]。
