# 問世界:散文審查收斂的世界解(2026-08-25,Enzo 指示網搜)

總綱:世界主流解不是「把迴圈跑到乾淨」,是**改掉「乾淨才放行」判準本身**。四個互不相識的傳統(審查學派/需求工程/期刊+IETF/Google)全部用密度門檻或人裁,零一家用「連續兩輪乾淨」審散文。

## 六路要點
1. **審查學派**(Fagan 1976/Gilb 1993·2009/capture-recapture Petersson-Wohlin 2004):退出=殘餘 major 密度≤門檻(IBM 0.25/頁、NASA 0.1/頁;起步線可寬至 1/頁);檢出率約 1/3→估總量≈找到×3;速率上限實測(50→200 行/時,檢出率 1.6%→0.6%);密度太高=整份重寫而非逐條修(「修補式折返=缺陷注入」);Gilb 原文:重寫決定本身是合法退出。Fagan「返工>5% 才整份重審」出自二手,未核原文。
2. **需求工程**(PBR Basili-Shull 2000/EARS Mavin RE'09/NASA ARM·QuARS):措辭級缺陷機器前移(weak-word/歧義掃描);行為需求用受限句型;席位帶固定視角減撞題。工具本體不引,抄思路自建(零依賴)。
3. **給散文造 oracle**(AWS TLA+ CACM 2015/Specification by Example Adzic 2011):只對「人腦推不動的核心協議」上形式化;可舉例的主張轉輸入→預期例,例子即 oracle;寫不出例子的行為斷言=作者沒想清楚(major)。TLA+ 本體不採。
4. **非阻塞紀律**(Google eng-practices/Conventional Comments):放行鐵則=「比現狀好就准」;Nit: 前綴不擋;發言時就聲明 blocking/non-blocking。
5. **期刊+IETF**(MDPI 兩輪上限/RFC 7282):major 回原審、minor 編輯自驗;上限後 reject=判定重寫;粗共識=異議被考慮過即可,不必採納;running code 是終審。
6. **LLM 實證**(CriticGPT 2024/Huang 2023/More Rounds More Noise arXiv 2603.16244/judge 可靠性系 2026):批評者精度-召回不可兼得;多輪辯論期望不改善(martingale);受控實驗單輪 F1 0.376>所有多輪(最佳 0.303,FP+62%,召回僅+0.08)——機制:false positive pressure(真錯耗盡後捏造)+Review Target Drift;二值判準評分一致性最高。〈More Rounds〉單作者小樣本,證據中等但與本案六輪實測同構。

## 折入排序(前 3)
1. 閘=殘餘 blocking 密度門檻+non-blocking 不擋(病根:零缺陷退出在散文上數學不可達)。
2. 「新發現全是 non-blocking」=收斂成功(現制判「沒過」方向相反);後期輪只驗收不報新;超線→判定重寫。
3. 措辭級前移機器 lint(席位不得再報該類)+行為斷言強制配例。

## 來源
Gilb Agile Spec QC 2009 PDF(數字逐字核)/Software Inspection 1993/Petersson-Wohlin JSS 2004/Shull-Basili IEEE Computer 2000(J79)/EARS alistairmavin.com/NASA ARM 重建 SIVOE 2013/Newcombe CACM 2015/Adzic gojko.net/Google eng-practices standard/conventionalcomments.org/RFC 7282/MDPI editorial_process/OpenAI CriticGPT+LLM Critics PDF/arXiv 2603.16244·2310.01798·2601.02854·2606.19544·2606.00093
