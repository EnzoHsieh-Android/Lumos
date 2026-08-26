---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:第 2 批接活⑦(v2,r1 五席 18 條全折後重寫)——[S1] doctor 加 [L2] 檢=逐字複用 _lintcheck_validate 四種格式 problem(無 PATH 無必填鍵無新鮮度;服務面=活通路+有 vault 的消費 repo,KDS 凍結通路明文除外)[S2] --no-lint 事實修正:寫死於共用判定函式、pre-push 與 CI 兩側同跳,裁定入 pitfalls-code-loop decisions+回頭條件掛本地觸發詞於 Verification [S3] smoke 責任歸屬明文化(分家後 KDS 自負;Landmark 未宣告=現無義務,宣告日接其 daily-governance)
  DEP:[[Projects/建了沒人跑批次裁定_計劃]]｜[[Systems/pitfalls-code-loop]]
status: doing
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/doing
---

# lint接線收口_計劃

> 白話:v1 被五席 18 條(4 blocker)打掉:PATH 檢兩向誤判且違反既有合約、「必填鍵/新鮮度」是沒有輸入的發明詞、交付通路早已分家凍結讓 KDS 根本收不到、--no-lint 其實兩側都跳、回頭條件綁外部事件不可驗。v2 縮到誠實可達的範圍。

## 條款(v2)

- **[S1] doctor 加 [L2] 檢(複用不重寫)**:repo 有 `.lumos/lint.json` 時,呼叫既有 `_lintcheck_validate` **逐字複用**(四種格式 problem:非 dict/value 非 list/命令空/缺佔位符——不加 PATH、不加必填鍵、不提新鮮度);有 problem=紅(吃 run_doctor 既有 strict 機制)。無宣告=一行「未宣告,跳過」。段名 [L2](守 doctor 單字母+數字慣例);位置=全部既有檢之後、`if ci:` 治理帳寫入之前(案 A 切窗三測位置驗過安全)。服務面明定:走活通路(bootstrap symlink/update)且有 vault 的消費 repo(現=Landmark);KDS 等凍結通路(2026-08-20 分家裁定)明文除外——它們拿不到本 repo 更新,不冒充服務對象;無 vault 消費 repo 的 pre-push 提前退出=已知邊界,現存宣告實例 0,立 Issue 觀察不擋本案。
- **[S2] --no-lint 明文化(事實修正版)**:事實=`--no-lint` 寫死於 `_codeloop_guard_verdict` 共用函式,pre-push 與 CI 的 code-loop gate **兩側同跳**——「CI 兜底」對 lint 發現不成立,這句要原樣寫進裁定。裁定以 `lumos decision-add` 落 [[Systems/pitfalls-code-loop]] decisions 結構化條目;回頭條件掛在本案 Verification 節點的 revalidate_when,觸發詞=**本地事件**(「改 _codeloop_guard_verdict 的 lint 行為」「改 pitfalls 的 lint claim 消費路徑」),不綁外部 repo 事件。
- **[S3] smoke 責任歸屬明文化**:分家(2026-08-20)後 KDS 的 smoke 責任=其 repo 自己的 setup/CI,本 repo 不再背——寫進 [[Systems/lint-declaration-health]];Landmark 現無 lint 宣告=零 smoke 義務;條件性條款:Landmark 若宣告 lint,smoke 接其 daily-governance 排程(有既有基建),屆時另立小案。
- 邊界:lint-check 本體/SARIF 轉換器/pitfalls 消費路徑不動;--no-lint 行為本身不改(明文化非改行為);KDS 通路的任何接線不在本案。

## 行為斷言

fixture:壞 JSON→doctor 紅且訊息=既有 lint-check 白話;非 dict/空命令/缺佔位符→紅;合法宣告→綠;無 lint.json→綠含「未宣告」;[L2] 輸出位置在最後一檢之後(切窗三測照綠);pitfalls-code-loop decisions 查得到新裁定(lumos decisions);本案 Verification 的 revalidate_when 被 stale --candidate --match 掃得到(機械驗)。

## 實務隱患

- 守衛面:[L2] 紅=CI 擋,但判準=既有 _lintcheck_validate 逐字複用(KDS 真宣告驗過不誤紅、{} 合法)——零新判準=零新誤紅面;本 repo 無宣告恆跳過。
- 誠實邊界:本案接線只惠及活通路消費端;KDS 凍結通路的 lint 健康=其自身責任(分家裁定的自然推論),不在此假裝覆蓋。

## 審計修正紀錄

**r1(2026-08-26,五席 18 條全折零放行:ext 3[2b]+s1 4[1b]+s2 4+s3 3[1b]+arch 4;ext 引句格式不合規經機械重現撈回,intake 有檔)**:
- PATH 檢殺除(ext-f2/s1-f1/s1-f2/s2-f1/arch-f1):違反 lint-declaration-health 靜態=格式層合約、CI 必假紅、java -jar 型假綠。
- 「必填鍵」「新鮮度」殺除(s1-f3/s1-f4/s2-f2/s3-f2/s3-f3):無輸入無定義的發明詞;smoke-ts 代理=上線第一天全紅陷阱。
- 可達性(ext-f1/s3-f1):KDS 凍結通路收不到+無 vault repo pre-push 提前退出→服務面明定+除外聲明+觀察 Issue。
- --no-lint 兩側同跳事實(s2-f3)→ [S2] 原樣入裁定;decisions 結構化(arch-f4);revalidate_when 掛 Verification+本地觸發詞(arch-f3/s2-f4)。
- smoke 責任鏈(ext-f3)→ [S3] 分家後歸屬明文化,不再寫不可執行的外部義務。
- [LINT]→[L2] 段名(arch-f2);編排者自首:動筆前沒查圖譜漏掉現成合約筆記,intake 有檔。
