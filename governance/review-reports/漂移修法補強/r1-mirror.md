# 折入核對(漂移修法補強_計劃 r1)

統計:已處理 47、部分 4、未處理 0、相反 0(共 51 條);新矛盾 5 條(另 2 條覆蓋缺口);審計紀錄引錯 1 處(另 1 處引得寬鬆)。
節名縮寫:§1~§5=〈做法〉1~5 節;誠實=〈誠實界線〉;回退=〈回退〉;依據=〈依據〉段。

## 1. 逐席逐條

### 正確性-opus
- F1 交集濾掉代碼審目錄 → 已處理 → §1 全列標來源、排序、範本只填兩者;S1
- F2 範本佔位字 `<卷證>`/`<sha>` → 已處理 → §2 擋 ②(`_drift_placeholder_err`),S2
- F3 寫後才驗 c4 消失 → 已處理 → §2 擋 ③(三個詞點名第幾項),S2
- F4 `fmt_scalar` ValueError 噴 traceback → 已處理 → §2 `_conditions_rewrite` 轉成錯誤訊息,S2 舉單雙引號例
- F5 讀檔提前改變 set 訊息順序 → 已處理 → §2 拆 `_conditions_vals_err`(先驗值、再讀檔),S3 獨立測試+黃金字串
- F6 check 與 strip 口徑 → 已處理 → §2 `_conditions_vals_err` 回去空白 vals,check/template_used 用它
- F7 接線點漏列(參數組裝、c3 允許表、hint) → 已處理 → §2 接線清單、§4 c3 ALLOWED、回退列 hint
- F8 區塊寫法被併成一項、截斷 → 已處理 → §2 用 `_conds`、不截斷、超 2000 字改逐項
- F9 lands_in 缺 delguard → 已處理 → frontmatter lands_in、§5 `skip` 與 `_DELGUARD_*` 分開

### 邊界-sonnet
- F1 佔位字 → 已處理 → §2 ②,S2
- F2 未提交字寫後才報 → 已處理 → §2 ③,S2
- F3 traceback → 已處理 → §2 `_conditions_rewrite` 轉錯誤,S2
- F4 無交集列 1~3 個不相干目錄、不再試計劃名 → 部分 → §1/S1 兩份都列標來源、範本只填兩者(主建議已做);缺:`_plan_first_commit` 遇計劃檔改名會回到改名提交,計劃與誠實都沒提;子字串太短的 key 多命中沒說
- F5 預填指令 2000 字截斷 → 已處理 → §2 不截斷、超長/控制字元不印可貼指令
- F6 多行區塊壓成一項 → 已處理 → §2 `_conds`
- F7 卷證目錄邊界(頂層檔、巢狀、控制字元、範本句 shell 元字元) → 部分 → §1 四段路徑、`_esc_clean`、指令參數走 `_drift_sh`;缺:範本句(人會整句貼進 `--values`)沒走 `_drift_sh`,目錄名含換行時 template_used 用未消毒版比對永遠不等
- F8 check 未去空白 → 已處理 → §2
- F9 S3 檢查/讀檔順序 → 已處理 → §2 拆函式、S3
- F10 c1 辨認式太鬆 → 已處理 → §3 whynot 認完整「預告當時為什麼還不做:」、TEST 限摘要區、settle 限正文(日期格式驗證沒提,原報告列為附帶)
- F11 c3 理由去空白/連結 → 已處理 → §4
- F12 argparse 與分派字典接線 → 已處理 → §2 接線清單、`_drift_fix_load` 條件、`--values=-x` 寫進誠實
- F13 lands_in → 已處理 → frontmatter

### 接手-sonnet
- F1 寫後才發現 c4 沒消失、單數「那項」 → 已處理 → §2 ③、④(「含三詞的項」複數皆需改寫)、S2、dry-run 也擋
- F2 佔位字 → 已處理 → §2 ②
- F3 c3 必改處、接線 → 已處理 → §4 ALLOWED、§2 接線
- F4 lands_in、指令文件與舊筆記同步、翻案決策 → 部分 → lands_in 補 delguard、依據段寫翻案並要 `decision-add`、PITFALL 標被取代;缺:`commands/04` c4/c3 那列、存量漂移守衛 WHY(c4 只給證據)沒有「正向」要改的條目,只在回退節被順帶列出
- F5 舊文字與既有測試 → 部分 → §2 接線列 `_drift_fix_hint`;缺:`t_drift_fix_c4_evidence_then_replace` 要改寫只在回退節以「改回」出現,條款/做法沒寫上線時怎麼改(哪段保留)
- F6 RETIRE-IF ① 指標與量法 → 已處理 → RETIRE-IF 改成 reports_same 減 reports_name、附一行指令、寫明 rtb 帳由跨會談訊息取(未處理母體偏誤,屬原報告次要點)
- F7 set 與 drift fix 並存 → 已處理 → §2 證據頁末行、誠實(set 不記帳、順序不對稱);未寫進 commands/04
- F8 空白 → 已處理 → §2
- F9 settle 手補段落 → 已處理 → §3 settle 認正文任一行符合 `_GUARD_MANUAL_SETTLED_RE`
- F10 delguard 額外 git、跳過數 → 已處理 → §5 有碰到才做、`_over()`、detail 記數

### 併發-sonnet
- F1 整欄覆蓋 → 已處理 → §2 ④,併發隱患行
- F2 空白 → 已處理 → §2
- F3 git 查詢在鎖外 → 已處理 → §1 末段
- F4 乾淨檢查條件 → 已處理 → §2 接線(`_drift_fix_load` 改「c4 且沒帶 --values」);所建議的「髒檔案帶 --values 被擋」測試未列進條款
- F5 delguard 序列 git 與期限 → 已處理 → §5
- F6 清單沒暫存 → 已處理 → §5 末條、誠實、S6

### 回滾-sonnet
- F1 → 已處理 → §2 ③、S2
- F2 回退漏列 → 已處理 → 回退 c4/測試/文件/decision-supersede 都列了
- F3 混版與退路 → 已處理 → §2 證據頁末行、誠實
- F4 RETIRE-IF 量法 → 已處理 → RETIRE-IF、REVISIT(帶最小 N=5、20)
- F5 c1 判定與訊息同源 → 已處理 → §3 擴充 `_guard_settle_rewrite` 的 seen、WHY/settle-del 不重寫、組字函式一處
- F6 清單沒暫存與回退 → 已處理 → 誠實、S6、回退

### 架構對齊-sonnet
- F1 lands_in → 已處理
- F2 c3 佔位字「抽成共用」措辭 → 已處理 → §4 改成 c3 也呼叫既有 `_drift_placeholder_err`(但「現在只有 c2 呼叫」不準,見新矛盾 N5)
- F3 辨認式重用既有常數、「找不到」字樣一處 → 已處理 → §3
- F4 訊息雙重前綴與 set 專屬指示 → 已處理 → §2 前綴由呼叫端印、`how` 參數
- F5 用既有 git 包裝與 `-z` 寫法 → 已處理 → §1(`_nodehome_git` + `-z`,不加 -c);`_nodehome_commit_groups` 合併提交的次要問題沒回應
- F6 第五份內嵌 → 已處理 → §5 抽 `_vendored_intact`、三處一起改

### 外家否決-codex
- F1 無交集把別案卷證寫成依據 → 已處理 → §1/S1 標來源、範本只填兩者、>3 另標

## 2. 新矛盾

- N1(§2 vs 既有行為與前置掃描決定):§2 尾段寫「乾淨檢查 → `--dry-run` 到此」,但程式現況 `_drift_fix_load` 是 `not dry_run and kind != "c4"` 才做乾淨檢查(dry-run 不做),前置掃描 r1-intake ③-2 也裁「--dry-run 照慣例不做乾淨檢查」。同一節前面又說 dry-run 也照擋值檢查。要寫清:值檢查 dry-run 也做、乾淨檢查 dry-run 不做,並改掉「乾淨檢查 → dry-run 到此」的順序。
- N2(RETIRE-IF ②/REVISIT ② vs §5):RETIRE-IF ② 與 REVISIT ② 要「抽樣 5 次被跳過的名稱」再 `lumos search`,但 §5 與 S6 只記「跳過幾支、少抽幾個名稱」(數量),事件裡沒有被跳過的名稱清單,抽樣做不出來。要嘛事件 detail 記名稱(有上限),要嘛量法改成別的。
- N3(§3 內部):第一條首句「WHY 與 settle 重用既有 `_GUARD_SETTLED_TAIL_RE`、`_GUARD_MANUAL_SETTLED_RE`」,同一條後段又說「WHY 與 settle-del 既有判定已算 seen,不重寫」。WHY 到底重用辨認式還是完全不動,措辭打架(實作上以後者為準,首句應刪 WHY)。
- N4(回退 vs §5):§5 新增 `_vendored_intact` 並把三處既有內嵌改成呼叫它,回退節只列 `skip` 參數與 detail 欄位,沒列這支新函式與三處改呼叫(行為不變,可留,但該明寫「可留」)。
- N5(§4 vs 程式):§4 寫「`_drift_placeholder_err` 現在只有 c2 呼叫」,架構對齊報告指出 c2 與 ack 兩處都在用;事實敘述不準(不影響做法)。
- 覆蓋缺口(非矛盾):(a)〈實務隱患〉效能寫「多一次 git show」,實際是 `_plan_first_commit` 的 git log 加 git show 兩次(併發 F3);(b)條款沒有覆蓋證據頁 `_conds` 展開/不截斷/超 2000 字改逐項、「髒檔案帶 --values 被乾淨檢查擋」、`_drift_fix_load` 接線(只有 `--values` 漏接的測試會靜默過),這些在做法有寫、條款沒綁測試。

## 3. 〈審計修正紀錄〉r1 引用核對

逐一對過七份報告的 F 號:除下列外都對得上。
- 引錯 1:「c3 理由去空白、連結不驗(邊界 F11、架構對齊 F2)」——架構對齊 F2 講的是「佔位字檢查早已是獨立函式 `_drift_placeholder_err`,不用再『抽成共用』」,不是去空白或連結不驗;去空白/連結不驗只對應邊界 F11。應改為「(邊界 F11;佔位字措辭:架構對齊 F2)」。
- 引得寬鬆(不算錯):「目錄名進照貼指令走 `_drift_sh`(邊界 F7)」——邊界 F7 實際指的是「範本句」沒走 `_drift_sh`,計劃只做了指令參數那半(見上 邊界 F7 部分)。
- 其餘核過:正確性 F2 F3 F4 F6、邊界 F1 F2 F3 F8、接手 F1 F2 F8、併發 F1 F2、回滾 F1(寫入前擋);正確性 F1、外家否決 F1、邊界 F4(卷證);正確性 F5、邊界 F9、架構對齊 F4(set 拆函式);正確性 F7、接手 F3、邊界 F12、併發 F4(接線);正確性 F8、邊界 F5 F6;回滾 F5、接手 F9、邊界 F10、架構對齊 F3(c1);併發 F5 F6、接手 F10、回滾 F6(delguard);lands_in 四席;回滾 F2、接手 F5;回滾 F4、接手 F6;回滾 F3、接手 F7;邊界 F7;併發 F3;架構對齊 F5 F6——編號與內容皆對。
- 附註:紀錄說 r1 是「7 席」,報告確為 7 份,無誤。
