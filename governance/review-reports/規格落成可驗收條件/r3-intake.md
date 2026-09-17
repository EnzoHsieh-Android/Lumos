preflight-4: ran

# r3 收貨紀錄(規格落成可驗收條件_計劃)

- 前掃:lint 0 問題;refcheck ok 5/missing 0;spec-trace 27 條/綁了 7/懸空 20(未寫,預期);prose-lint 兩處「若干」是停用詞表的例字不是模糊用法,不改。
- 凍結審材 r3-snapshot.md(指紋 eee6c7a6ece3b4db、292 行);六席全新(*3-sonnet);外家席缺席(Codex 額度)。
- 席報告先落 repo 外暫存區,六份到齊才搬進本目錄;`report-normalize --write`(邊界3、回滾3 各改 1 處);`refcheck --repo .` 六份 ok(回滾3 的 2 筆 missing 是把三個行號用斜線寫成一串,核對器讀不懂,不是壞引用)。通知管道的 HTML 實體(`&lt;` `&gt;`)存檔時還原成原字元。
- 席位尾行矛盾(不改、記下):正確性3 尾行 blocking 寫 1/2/4/5,正文是 1/3/4/5;邊界3 尾行寫 4 條,正文 F4 也是 blocking 是(5 條)。以每條 finding 自己那行為準。

## quote-check(對回 r3-snapshot.md)
| 席 | 結果 |
|---|---|
| 正確性3、接手3、回滾3、簡化守護者3 | 全數錨定 |
| 邊界3 | 8 句 1 句錨不到(#1 <10 字);該條(C1)由編排者重現 |
| 架構對齊3 | 6 句 1 句錨不到(#5 引的是 Systems/每支檔有家 節點,不在審材);該段是「對齊」判斷不是 finding |

## 編排者重現(機械)
- **C7 CI 工作名前綴**:`grep -o '"failed_step": "[^"]*"' docs/.ci-log.jsonl | sort | uniq -c` → `test/Anchor verify (baseline 缺失必紅)` 3、`test/code-loop gate (push 後盾;體檢` 3、`test/自主迴圈測試` 2;`.github/workflows/ci.yml` 唯一 job id 是 `test`;`_ci_failed_step` 組 `f"{job}/{step}"` → 成立(兩席各抓一半:前綴與中文)。
- **C10 INV_TAG_RE 無 keeps 分支**:`scripts/lumos:3408` 只有 test|audit|kill|src|git 與 manual → 成立。
- **C11 懸空只提醒**:`_disposal_clause_step` 對懸空只印「只提醒不擋,spec-trace 會唸」並回 ok → 成立。
- **C4 借的判準不數支數**:`_ran_evidence_check` docstring 明寫「證的是有東西跑過,不是跑的是你要的那一支」→ 成立;`-k` 子字串比對由 CLAUDE.md「關鍵字比對測試函式名」佐證。
- **C1 節標題變體**:`grep -rhoE '^##+ .*實務隱患.*' Projects/*.md | sort | uniq -c` → 8 種變體(含「實務隱患(逐類答)」「實務隱患(M1)」) → 成立。
- **C2 pickaxe 繞法**:`git log -S` 不限路徑、不驗至今存活,照 spec 文字逐步走,舊名繞法成立。
- **C6 kinds None + sevs 給 → precision finding**:`scripts/lumos` 掛勾 `_precision = "finding"` 不看 kinds → 成立。
- **C12 S23 抄錯**:凍結稿第四節寫「S23 綁測試」,S23 內容是已排除行照掃 → 成立。

## 去重對照(C1–C22;全折 22——blocker 輪不准附理由放行,席位自判無缺陷的兩條以一句核可寫進正文)
| id | 內容 | 席 | 嚴重度 | 型 | 處置 |
|---|---|---|---|---|---|
| C1 | 「實務隱患節」邊界未定義(標題變體、層級、起訖) | 正F1、邊F1 | blocker | spec | 折:二級標題去序號/括號後以實務隱患開頭、到下一 ##;`_section_lines`;新 S29 |
| C2 | keeps 既存性用 pickaxe 可被舊名繞過;squash/未提交未交代 | 正F3、邊F6、簡F2 | blocker | spec | 折:改看 created 前提交樹裡同檔有無 def;改名/未提交擋;預埋提交寫進殘餘 |
| C3 | 停用詞表不齊 | 正F2 | minor | spec | 折:承認不齊、報錯不靜默、訊息帶加詞方法 |
| C4 | 跑到 ≥2 支未定義;借的判準不數支數;-k 子字串 158 組撞名 | 正F4、邊F4、簡F1 | major | spec | 折:解析支數 N==1;N≥2 擋;PRIOR-ART 訂正「不是借的」;殘餘段補撞名;新 S32 |
| C5 | precision=round 的列在門檻分子怎麼算 | 正F5、接F4、回F2 | major | spec | 折:分子只數 finding 與手動列;新 S34 |
| C6 | 給嚴重度沒給型別仍標 finding | 邊F3 | major | code | 折:程式改 kinds None → round;測試 ⑤ |
| C7 | CI failed_step 帶工作名前綴、中文步驟名切成空 | 回F1、邊F2 | blocker | code | 折:只看「/」後步驟名+認「測試」;測試 ③e/③f;表格改寫 |
| C8 | 留痕整檔 sha 太敏感 | 邊F5 | major | spec | 折:改條款區塊指紋;新 S31 |
| C9 | `_excluded_line` 前綴字元集另寫一套 | 架構對齊、邊F7 | major | spec | 折:借 `_CLAUSE_LEAD_RE` 同一組 |
| C10 | [keeps] 不在文法;INV_TAG_RE 無 keeps 分支 | 邊F8 | blocker | spec | 折:文法加 [keeps]?;要動什麼加分支 |
| C11 | 新合約草稿「測試存在」會靜默改掉懸空只提醒 | 接F1 | blocker | spec | 折:door=one-way 保留只提醒;two-way 懸空=擋;草稿改寫 |
| C12 | 「S23 綁測試」抄錯應為 S28;其餘 9 處讀側無條款 | 接F2 | major | spec | 折:S28 改成涵蓋全部讀側、每處餵一筆 |
| C13 | door_rule 無條款/初值/改版判準 | 接F3、簡F3、簡F7 | major | spec | 折:整數常數初值 1、bump 條件、新 S33 |
| C14 | 回退基準 sha 待填無提醒 | 接F5 | major | spec | 折:REVISIT 改綁 S8 落地必填 |
| C15 | S21 一條兩判準 | 接F6 | minor | spec | 折:拆成 S21+S30 |
| C16 | S25 也要 git 沙盒沒寫 | 接F7 | major | spec | 折:一句 |
| C17 | 雙重失敗的 REVISIT 量不到目標事件 | 回F3 | major | spec | 折:承認量不到、刪那條 REVISIT、改寫線索 |
| C18 | range 要沿用 push-range 不得自算 merge-base | 簡(固定席段) | minor | spec | 折:一句 |
| C19 | r2 折入數上升的原因要明寫 | 簡F8 | minor | spec | 折:誠實界線一段 |
| C20 | 33 條全自指、零條驗使用者行為 | 簡F6 | minor | spec | 折:誠實界線寫明結構性自指 |
| C21 | d11 新理由是否換說法 | 簡F4 | minor | spec | 折:為什麼段加一句「d11 理由與數字獨立,r3 核可」 |
| C22 | keeps 三層防線能否合併 | 簡F5 | minor | spec | 折:第三節加一句「三層各防不同面,不合併」 |

## 程式同步(先紅後綠)
- `_ci_step_is_test`:只看「/」後段、`;` 分段、認「測試」;測試 ③e/③f 先紅後綠。
- 掛勾 `_precision`:kinds None → round;測試 ⑤ 先紅後綠。`-k escape_auto` 31 passed。
- 圖譜:正文 22 處替換;summary --add KEY(r3);lint 0;spec-trace 33 條/綁了 7/懸空 26(未寫)。
