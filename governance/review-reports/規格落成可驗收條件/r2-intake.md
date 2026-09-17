# r2 收貨紀錄(規格落成可驗收條件_計劃)

- 派工單 `r2-dispatch.json`;凍結審材 `r2-snapshot.md`(指紋 9815210f7c32bc10、261 行);六席全新(正確性2/邊界2/接手2/回滾2/簡化守護者2/架構對齊2,sonnet),外家席缺席(Codex 額度)。
- 席報告先落在 repo 外暫存區,六份到齊才搬進本目錄;`report-normalize --write`(正確性2 改 1 處,其餘已正規);`refcheck --repo .` 六份全 ok(missing 0 / out_of_range 0)。
- 通知管道把角括號轉成 HTML 實體(`&lt;` `&gt;`),存檔時還原成原字元;不是改引句。
- 席位自身的尾行矛盾(不改、記下):邊界2 尾行先寫「blocking 計 5 條」又寫「共 6 條」;接手2 正文 finding 2 標 blocking 否、尾行卻算進 blocking。以每條 finding 自己那行為準。

## quote-check(對回 r2-snapshot.md)
| 席 | 結果 |
|---|---|
| 正確性2 | 全數錨定 |
| 接手2 | 全數錨定 |
| 架構對齊2 | 全數錨定 |
| 邊界2 | 7 句 1 句錨不到(#6 用「…」拼了兩段);該條(B6)由編排者重現 |
| 簡化守護者2 | 5 句 3 句錨不到(#1 把表格列拼成句、#4 改字、#5 <10 字);B16/B3/B19 由編排者重現 |
| 回滾2 | 整份沒寫「引句:」只給 file:line;五條全部由編排者重現 |

## 編排者重現(機械)
- **B16 分級用量**:重跑審查帳。我當初的腳本多加「帳列 round 以 r 開頭」篩選 → standard 629 / high 89 / light 3(今日帳)、迴圈 128;拿掉該篩選 → 記錄層級 622/96/12、迴圈層級 93/10/11、迴圈 159。**被篩掉的 67 列裡 light 9 筆全無輪次欄位** → 席位對,「只用 3 次」是假象。127 vs 159 同一口徑差異。
- **B8 CI 子字串**:`scripts/lumos` 原判準 `"test" in failed_step.lower()`;`latest`、`attestation` 命中 → 成立。
- **B9 代碼審 any()**:原碼 `_has_code = any(v=="code")` 配輪級 `severity` → 成立。
- **B10 推送閘雙重命中**:`code-loop check` 在 tier=high 且合約測試紅時回傳 `bt["reason"]+"(tier=high,--bound-tests-advisory 不適用)"`,reason 以「受波及合約的測試沒過:」開頭;pre-push 兩個 `grep -q` 都會中 → 成立。
- **B11 測試名不存在**:`grep -n t_escape_auto_unreviewed_twoway\|t_escape_auto_ci_only_test_step scripts/test_lumos.py` 零命中 → 成立。
- **B1/B3/B5**(設計層):照 spec 文字逐步走判定路徑,席位描述的繞法都走得通(已排除行不限節不限類;S6 條件③對空集合恆真;「當然」開頭無逗號兩邊都不合)。
- **B20 tag 無先例**:`git tag -l` 空 → 成立。

## 去重對照(B1–B30;全折,放行 0)
| id | 內容 | 席 | 嚴重度 | 型 | 折法 |
|---|---|---|---|---|---|
| B1 | 已排除行跳過無範圍/類限制=洗白豁免 | 正F1、邊F1 | blocker | spec | 只跳實務隱患節內合格四類行;判定與證明共用 `_excluded_line`;S16 改寫、新 S23 |
| B2 | 已排除行變體(全形冒號/縮排/引用)認不出→自我否決復發 | 邊F2 | major | spec | `_excluded_line` 去前綴、冒號兩形都收 |
| B3 | 全標 [keeps] 整份繞過「每條紅」 | 正F3、邊F3 | blocker | spec | 至少一條未標 keeps + keeps 測試在 git 歷史早於計劃建立;新 S25 |
| B4 | [keeps] 形狀/位置/大小寫未定 | 邊F4 | minor | spec | 定死半形小寫、同行任意位置、INV_TAG_RE 家族;變體當沒標並提示 |
| B5 | 當然/在此/若干句首誤判成觸發詞 | 正F2、邊F5 | major | spec | 停用詞表(只增不刪)+ 擋下訊息說明;新 S26 |
| B6 | 紅不分斷言假/跑不起來 | 邊F6 | major | spec | 借 bound-tests-gate:跑到 1 支且失敗才算紅,0 支=弱證據擋下;新 S27 |
| B7 | 前 30 份計數口徑/規則版本未定 | 邊F7 | major | spec | 分母口徑寫死、留痕帶 door_rule 版本、改版從零重數 |
| B8 | CI 步驟名子字串比對 | 正F4 | major | code | `_ci_step_is_test` 切詞;t_escape_auto_ci_only_test_step 釘 |
| B9 | 代碼審掛勾輪級 any() | 回F1 | major | code | `--finding-severity` 逐條;沒給退回輪級並標 precision=round;新 S22 |
| B10 | 推送閘兩個 grep 同時命中、第二筆歸因錯 | 回F2 | major | code | 只認「tier=high 且」;t_escape_auto_unreviewed_twoway ④c 釘 |
| B11 | S18/S19 綁的測試名不存在;「全綁測試」宣稱為假 | 接F5、接F11 | major | code | 拆成兩支真測試;誠實界線改寫 |
| B12 | 共用檢查器與 manual 政策矛盾 | 接F2 | major | spec | 檢查器吃 door 參數;「相同判定」定義為同 door 下相同 |
| B13 | design-loop INVARIANT 新文字與綁定測試未定 | 接F3 | major | spec | 新文字草稿寫進第四節;綁 t_disposal_clause_gate + t_disposal_step5_shares_checker |
| B14 | 留痕後計劃被改,推送閘對舊測試名下手 | 接F4 | major | spec | 留痕記計劃 sha256;過期擋下重跑;新 S24 |
| B15 | _round_valid_m2 白名單擴充語意未定 | 簡F2 | major | spec | spec-gate 不計分子不判無效;留痕帶 loop 不帶 round;新 S28 |
| B16 | 分級用量 629/83/3 無法重現(+127 分母) | 簡F1、簡F6 | blocker | spec | 數字與口徑訂正;d3 理由改寫(d11);KEY 行重寫 |
| B17 | 三條絕對門檻無推導依據 | 簡F3 | major | spec | 明寫「是拍的,正當性只來自 RETIRE-IF 收斂」 |
| B18 | 每條紅的前置成本沒估 | 簡F4 | major | spec | 第四節寫成本前移;S13 印條款數/紅測試數 |
| B19 | 推送閘讀所有 doing 留痕不分範圍 | 簡F5 | major | spec | 只讀本次範圍碰到的計劃;doing>30 天 doctor 提醒;S21 改寫 |
| B20 | pre-spec-gate tag 無機械綁、無先例、與 anchor「錨」撞詞 | 回F3、架構對齊(⚠) | minor | spec | 改成把落地提交 sha 寫進回退節 |
| B21 | fail-open 雙重失敗只剩 stderr | 回F4 | minor | spec | 誠實寫 + REVISIT |
| B22 | 絕對門檻誰數、非機械閘 | 回F5 | minor | spec | 明寫 S13 印、人讀人裁不自動擋 |
| B23 | 文法很鬆(不應也含應)沒誠實寫 | 接F1 | minor | spec | 第二節加一句 |
| B24 | 要動什麼漏 CLAUDE.md / lumos update | 接F6 | minor | process | 表加一行 |
| B25 | 其他 9 處 kind 白名單讀側沒交代 | 接F7 | minor | spec | 併進 B15 段落 |
| B26 | 第三條 _LANDING_GATE_SINCE 沒提 | 接F8 | minor | spec | 三條常數關係寫死 |
| B27 | S21 測試要真 git 沙盒、成本高 | 接F10 | minor | spec | 推送前段落寫明 |
| B28 | push-gate:unreviewed 冒號複合值不合命名慣例 | 架構對齊 | minor | code | 全面改 push-gate-unreviewed(程式/hook/測試/計劃) |
| B29 | lands_in 正文重複、格式不同 | 架構對齊 | minor | spec | 刪正文那行 |
| B30 | 取最新留痕未寫明;unreviewed 過渡期恆零筆未交代 | 邊(查證段)、正F5 | minor | spec | 第四/五節各加一句 |

接F9 是逐條核對紀錄不是 finding,不列。

## 程式同步(先紅後綠、三處翻紅釘)
- `scripts/lumos`:`_ci_step_is_test`;`cmd_canary --finding-severity` + 掛勾逐條判 + `precision`;`_auto_escape(extra=)`;階段名改連字號。
- `scripts/hooks/pre-push`:unreviewed 分支 `grep -q "tier=high 且"`;階段名改連字號。
- `scripts/test_lumos.py`:新 t_escape_auto_ci_only_test_step / t_escape_auto_unreviewed_twoway / t_escape_auto_code_finding_severity;t_escape_auto_scope_rules 縮成代碼審那段。`-k escape_auto` 28 passed;釘 a(子字串)→③c③d 紅、釘 b(grep 整詞)→④c 紅、釘 c(不看逐條)→① 紅,還原後全綠、hook 執行位保留。
- 圖譜:KEY 行用 summary 指令重寫(數字訂正+r2 折入行);d3→d11、d10→d12;正文 30 處替換;lint 0 問題;spec-trace 27 條/綁了 7/懸空 20(未寫)。
