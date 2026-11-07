# 規則包語意覆核級命中走盲判 r1 收貨(2026-11-07)

preflight-4: ran

## 首輪前掃(r1-preflight.md)

固定清單四項:① 未定義的詞 6、② 壞引用 3、③ 範圍自相矛盾 5、④ 機械宣稱驗語意 11 條不符(5 條相符)。①②③與存在類直接修真檔;④ 語意類逐條修並記改前→改後如下。沒有動到〈核心裁定〉:三題使用者裁定(d1 判 real 擋、d2 還沒判擋、d3 判 false 進 AI 放行複查清單)照舊。

## 語意類修正(改前 → 改後)

- B1 落點:改前「`_lint_new_verdict` 在跑完一般段之後跑 review 段」→ 改後分流點在 `_lint_new_tools` 組命令清單那一層,一般段與 review 段各組一份、各自比對新增。
- B2 時間預算:改前「同一個時間預算」,預算耗盡會被既有邏輯歸成擋 → 改後 review 段吃一般段剩下的預算,沒跑到記 `review_undone`,只講出來、不擋(S7 加一列)。
- B3 結果另放:改前一句「另跑、結果另放」→ 改後寫明各自呼叫 `_lint_new_diff_claims`、覆核命中放 `review_new`、`_lint_new_classify` 的擋只看一般段。
- B4 寫放行檔的位置:改前判 false 自動記放行、沒講在哪寫 → 改後只在 `lumos code-loop blind-judge <結果檔>` 記帳那一步寫,判定函式不寫檔(S4 加「判定函式不寫放行檔」、預期值表加一列)。
- B5 材料來源:改前「多印一節」→ 改後 `--template` 當下用同一範圍重跑覆核命令,另成一份 `rule_hits`、跟情境段分份。
- B6 結果檔格式:改前 `{"type": "rule-hit", "judgments": …}`(舊驗證器整份拒收)→ 改後頂層新鍵 `rule_hits`,`_kt_bj_validate` 擴充認它,沿用同一格只認第一筆。
- B7 仲裁:改前「沿用 `--arbiter`」(現有挑格靠作者與第一盲判分歧,規則命中沒有作者)→ 改後新增 `--template --unsure` 挑第一判 unsure 的筆、結果照 `--arbiter` 記。
- B8 治理帳:改前「多一個 type 欄」→ 改後判定放新欄 `rule_hits`,不放進舊的 `blind_judge` 欄,舊版讀帳略過。
- B9 準確率資料:改前統計「人複查後判錯幾筆」但 `lint-waive --ack` 只記看過 → 改後新增 `lint-waive --ack <鍵> --verdict agree|overturn`(用詞照 `canary second`);real 判定的人工覆蓋用 origin human 的放行數;門檻寫明哪些是本案自訂。
- B10 等級:兩份 sgconfig 的內容與等級相符;新增告警閘解 SARIF 不看等級,所以靠 review 段分流,不靠等級。
- B11 型錄主表:改前假設 lumos 讀得到「對應列、出處不全」→ 改後 lumos 用 importlib 借 check.py 的 `main_rows`(主表唯一讀法),規則對列用訊息開頭的型錄編號;四欄改成主表真的有的「壞寫法形狀、標準寫法、後果、情境怎麼認」(原寫的「不適用時」只在決策表)。

## 其他直接修

- 壞連結:「Android端到端驗收計劃」→ `Projects/Android端到端驗收_計劃`。
- 數字:AI 放行沒人看過 41 筆 → 2026-11-07 本 repo 實數 62 筆。
- 殘句:nowinandroid 那句改成「上線前要先量兩份 sgconfig 的命中」。
- 範圍矛盾:身分不再加序號(跟放行指紋同一把);門檻不再寫「照情境題同一組」;回退節補消費專案的處置;工作樹模式不跑 review 寫進範圍 2 並加 S9。
- 天花板補第 5 條:判 real 時 AI 也能自己放行。

## 六席收貨

- 正規化:六份皆已是正規化格式。quote-check:六份全數錨定。
- 發現編號照席位前綴:正1–正11、邊1–邊10、整1–整11、資1–資9、回1–回8、架1–架6(照各席報告的條目順序),共 55 條,major 33 條。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 架1、正1、整1、回4 | 讀 scripts/lumos:41888、42010:依賴層與新增告警閘設定兩次為同一理由不放進 lint.json;現行驗證器對每個頂層鍵當副檔名驗 | HIT |
| 回1、回2、回3、資5、邊1、邊2、正4 | 讀 _lint_waivers_add(已放行的鍵回失敗、沒有撤銷)、_lint_waive_ack(只記 acked)、記帳整份已有就回 2:判誤報寫放行撤不回、推翻無效、兩處寫一半補不上 | HIT |
| 正3、邊3、資6、回5、整3 | 讀 _lint_new_key 只用片段、_lint_new_diff_claims 同指紋計次:同片段多處共用判定、新增的那一處沒被判過 | HIT |
| 資1、整6、架3 | 讀 _codeloop_disp_range 與 _codeloop_lint_new_step 傳的範圍不同:template 與 check 範圍會對不上 | HIT |
| 資2、整5、架2 | _lint_new_verdict 與 _codeloop_lint_new_step 都沒有分支與合併側參數 | HIT |
| 資3、正2、邊 minor | _codeloop_lint_new_step 整段 except Exception 會讓一般段一起放行 | HIT |
| 資7、邊5、正 template、整6、架4、架5 | _kt_bj_validate 只認 segments 且要非空;_cmd_codeloop_blind_judge 開頭被情境型錄卡住 | HIT |
| 正 seg 偽造 | _kt_bj_validate 擋不在材料裡的段,spec 沒要求 rule_hits 對照當次命中 | HIT |
| 正 測試目錄 8 條 | rules-review/testing.yml 與 rules-hints/testing.yml 的 files: 限測試目錄,新增告警閘預設濾掉測試路徑 | HIT |
| 邊4 | 出處不全 7 條在還沒判時會擋,與 d1 理由矛盾 | HIT |
| 整2、回7、正 帳欄 | rule_hits 沒存規則代號、沒登記 _GOV_FIELD_TYPES | HIT |
| 資4、整7 | 覆核沒跑不留帳,跟一般段自動放行要記帳的做法相反 | HIT |
| 其餘 minor | 讀碼 | HIT |

## 世界查證(同一類 major 在五席獨立出現,換形狀前先查)

- Semgrep Assistant:AI 判誤報不自動關,藏起來集中給人批次複查;人同意才關、不同意就重新打開(https://ai.semgrep.dev/blog/2025/announcing-ai-noise-filtering-and-triage-memories 、https://semgrep.dev/docs/semgrep-assistant/best-practices-for-memories )。
- SonarQube:問題身分是規則加命中行內容雜湊(去空白),誤報標記跟著身分走,人可以手動重新打開(https://docs.sonarsource.com/sonarqube-server/latest/user-guide/issues/solution-overview/ )。
- 結論:要換方向——身分用指紋是業界標準(照留,寫進天花板);錯的是「把 AI 判誤報寫成放行」,改成只留治理帳、另列待人看、人推翻就重新擋。這一條改到使用者裁定 d3,先問人:使用者 2026-11-07 原話「照建議」,記成 d4、d3 標被取代。

## 分組與去向(輪內有 major;55 條全折)

- G1 宣告放哪:架1、正1、整1、回4 → 另開 .lumos/lint-review.json(範圍 1)。
- G2 判誤報寫放行:回1、回2、回3、資5、邊1、邊2、正4、正5、整4、架6 → d4:只留治理帳、rule-review 單筆或整批推翻(範圍 5、6)。
- G3 身分與同片段:正3、邊3、資6、回5、整3 → 材料列每一處、記處數、處數變多重判;語境變了寫進天花板(範圍 4、6)。
- G4 擋停接線:資2、資3、整5、架2、正2、正8 → 放在 _codeloop_lint_new_step、自己接例外、mode 與合併側照既有(範圍 3)。
- G5 材料與介面:資1、資7、邊5、整6、正7、架3、架4、架5 → 共用 _rule_review_hits、--rule-hits、--unsure 進 cl_bj_mode、借 _load_hook_file、型錄自檢守編號唯一(範圍 2、4)。
- G6 帳欄與統計:整2、回7、正6、整4、邊8、邊9、資9、回6 → rule_hits 帶 rule 與 occurrences、登記欄位型別、統計只讀帳、AI 放行算進被放行、rule-review 沒有 --all(範圍 5、8)。
- G7 測試目錄 8 條:正9 → 覆核不套測試路徑過濾(範圍 2)。
- G8 出處不全還沒判:邊4 → 判前判後都不擋(範圍 6)。
- G9 沒跑要留帳:資4、整7、邊6、正10 → 四種原因都寫 fail-open 事件(範圍 7)。
- G10 其餘 minor:資8、正11、邊7、邊10、整8、整9、整10、整11、回8、架5 → 成本與帳大小進實務隱患與 REVISIT、--smoke 另驗覆核宣告、手冊與筆記同步清單、型錄讀不到怎麼辦、七成筆誤刪掉。
