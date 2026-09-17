preflight-4: ran

# r4 收貨紀錄(規格落成可驗收條件_計劃)

- 前掃:lint 0 問題;refcheck ok 5/missing 0;spec-trace 33 條/綁了 7/懸空 26(未寫,預期);prose-lint 3 處「若干/在此」是停用詞表例字,不改。
- 凍結審材 r4-snapshot.md(指紋 13ced0b54387a35a、302 行);六席全新(*4-sonnet);外家席缺席(Codex 額度)。
- 簡化守護者3 原版在固定席段把 severity 寫在句中,正規化器修不了;請該席(保留脈絡)重傳,它把固定席八條各補了獨立 severity/blocking 行、finding 內容一字未改;以重傳版存檔記帳(條數 17)。架構對齊3 只有 1 條獨立 finding(其餘四段是「對齊」),記 1。
- 席報告先落 repo 外暫存區,六份到齊才搬進本目錄;`report-normalize --write`(正確性4 改 3 處、邊界4 改 1 處、回滾4 改 1 處);`refcheck --repo .` 六份 ok。HTML 實體還原同前幾輪。
- 席位尾行矛盾(不改、記下):接手4 的 F4 標頭寫 blocking 是、內文寫否,尾行自己更正為否;簡化4 的 F6 有兩行重複的 severity: blocker(正規化器已合併)。

## quote-check(對回 r4-snapshot.md)
| 席 | 結果 |
|---|---|
| 邊界4、回滾4、簡化守護者4、架構對齊4 | 全數錨定 |
| 正確性4 | 5 句 1 句錨不到(#5 <10 字;該條是「查無 finding」的 F5) |
| 接手4 | 13 句 1 句錨不到(#6 只引了半句);該條(D14)由編排者重現 |

## 編排者重現(機械)
- **D1 `created` 可改**:`lumos set --help` 明寫改單一值欄位,`created` 不在禁改清單 → 成立。
- **D2 CI/推送閘來源無精度欄**:`_ci_red_escape` 與 `cmd_loop_escape --auto` 呼叫 `_auto_escape` 都沒帶 `extra` → 成立。
- **D3 逐條嚴重度只驗子集**:原碼 `set(sevs) <= F` → 成立;已改成 `== F`,測試 ⑥ 先紅後綠。
- **D6 「每條機械重現」是假話**:r1/r2/r3 intake 的重現段各 10/8/8 條,對 23/30/22 → 約 1/3 → 成立。
- **D14 `_plans_in_range` 不讀 lands_in**:函式只認 `Projects/*.md` → 成立。
- **D15 pre-push 已有幾個家**:about_code 列它的 Systems 節點 4 篇 → 「只准一個家」不成立,多家是常態;接手4 F6 的前提錯、但「規格閘節點只該用連結指」這半句採納。
- **D7 支數解析未進 `_RAN_EVIDENCE`**:讀 `_RAN_EVIDENCE` 表(逐棧 profile)→ 成立。

## 去重對照(D1–D21;全折;Enzo 裁「拆兩份、先上半套」後,折入落點分三篇)
| id | 內容 | 席 | 嚴重度 | 型 | 折到哪 |
|---|---|---|---|---|---|
| D1 | keeps 既存性看 `created`,自填可改(同族第三次) | 正F2、簡F6 | blocker | spec | 雙向門放行_計劃 r4 折入段:改用計劃檔首次入 git 的提交 |
| D2 | 門檻分子排除 CI/推送閘來源(無精度欄) | 正F4、回F2 | blocker | spec | 逃逸自動記_計劃:精度欄只排除 round;雙向門 r4 折入段 |
| D3 | `--finding-severity` 只驗子集可靜默壓下逃逸 | 邊F1 | blocker | code | 程式改全集檢查+測試 ⑥;逃逸自動記_計劃表格 |
| D4 | 「(五)實務隱患」括號前綴沒涵蓋 | 邊F2 | major | spec | 雙向門 r4 折入段(_section_lines 收斂) |
| D5 | pytest 支數漏 skipped/error;skip/xfail 歸類未定 | 邊F3、正F3 | major | spec | 主計劃第三節(半套:含 skipped 等相加);雙向門 r4 折入段 |
| D6 | 「每條機械重現」與卷證不符 | 簡F5 | major | spec | 主計劃誠實界線改寫(約三分之一) |
| D7 | 支數解析只覆蓋 Python、未進 `_RAN_EVIDENCE` | 簡F7、架構對齊 | major | spec | 主計劃 PRIOR-ART/要動什麼(收進逐棧表);雙向門 r4 折入段 |
| D8 | `_section_lines` 是找節的第三套 | 架構對齊 | major | spec | 雙向門 r4 折入段(收斂成一支) |
| D9 | 規則版本綁錯條款、bump 無測試 | 接F1 | major | spec | 雙向門 r4 折入段 |
| D10 | 推送閘要讀 lands_in 但 `_plans_in_range` 不讀 | 接F2 | major | spec | 雙向門 r4 折入段;逃逸自動記_計劃註明只認計劃檔 |
| D11 | 合約草稿漏回退節 | 接F3 | major | spec | 主計劃第四節草稿補回退節 |
| D12 | `door: one-way` 無條款 | 接F4 | major | spec | 雙向門 r4 折入段 |
| D13 | S13 要印條款數/紅測試數,條款沒寫 | 接F5 | major | spec | 主計劃 S11(半套改印紅綠弱證據數);雙向門 r4 折入段 |
| D14 | pre-push 的家(接手席說只准一個家) | 接F6、架構對齊 | major | spec | 前提不成立(四篇家);規格閘節點只用連結指——主計劃要動什麼表 |
| D15 | 外部節點合約變動不在指紋內 | 回F5 | major | spec | 雙向門 r4 折入段 |
| D16 | CI 步驟名自帶 `;` 切錯段 | 回F1、邊F6 | major | code | 逃逸自動記_計劃誠實界線(只會少判不會多判,接受) |
| D17 | 已落地改動的圖譜落點(規格閘節點不存在) | 回F4 | major | process | 逃逸自動記_計劃獨立成篇、lands_in loop-convergence-recording 並補 KEY |
| D18 | 條款區塊指紋正規化未定義 | 邊F5、架構對齊 | minor | spec | 雙向門 r4 折入段(寫死) |
| D19 | 回退 sha 分兩次提交填哪次 | 回F3 | minor | spec | 主計劃回退節一句 |
| D20 | `_DOOR_RULE_VERSION` 命名族系 ⚠ | 架構對齊 | minor | spec | 雙向門(開審時定);不改 |
| D21 | 三層條款比例 27/30/42;先不開雙向門可砍 10 條;拆兩份;承重牆空窗;34/538 只算規則① | 簡F1–F4、F8 | major | spec | **Enzo 裁拆兩份先上半套**——主計劃縮成 11 條、雙向門待命、逃逸獨立;34/538 缺口記雙向門 r4 折入段 |

## 拆分後的三篇(記帳時被審文件仍是 r4 凍結版,拆分是折入的一部分)
- `Projects/規格落成可驗收條件_計劃`(半套,11 條,status doing)、`Projects/逃逸自動記_計劃`(已落地,9 條全綁,doing)、`Projects/雙向門放行_計劃`(草案,status todo,18 條草案)。三篇 lint 0 問題。
