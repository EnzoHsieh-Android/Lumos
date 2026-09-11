preflight-4: ran

# r1 收貨紀錄(代碼審資安席)

## 首輪前掃(便宜 agent,固定四項清單,2026-09-11)

- ① 未定義的詞(rc1/rc2、W、第③條、MASVS、OWASP Top 10、XXE、JWT、PII、claude-code-security-review、delta 輪/判定輪)→ 直接修真檔(補一句定義或改白話),不算 findings。
- ② 壞引用:四個連結、templates.md §7.7、SKILL.md 步驟 2、commands/06 全在;§7.8 與五支測試名是本計劃要新增的,不算壞引用。
- ③ 範圍矛盾:無硬矛盾;另抓到「第五條」這個名字已被 2026-09-08 條款綁定那一步(`_disposal_clause_step`,自稱處置閘第五步)佔用 → 改名「資安席」一步、照它的形狀寫(見下方語意修正 3)。
- ④ 機械宣稱驗語意(開檔讀碼):a/c/e/g/h CONFIRMED;b WRONG、d PARTLY、f 已確認凍結機制細節 → 見下方語意修正。

## 語意類修正(修改前 → 後)

1. ④b 留痕重驗不是函式
   - 前:「那筆的報告檔要在、sha 要跟帳面一致——重用第③條的留痕重驗函式,不另寫一套。」
   - 後:「現況:處置閘的留痕重驗是寫在閘裡的迴圈,判定輪一段、intake 一段各抄一份,沒有可呼叫的函式。實作時先把『單一帳列的報告檔在且 sha 對』抽成一支小函式,原本的留痕重驗與資安席這一步共用,不再抄第三份。」
   - 依據:file: `scripts/lumos:15041` 起的判定輪迴圈、`scripts/lumos:15065` 起的 intake 迴圈;唯一單列函式 `_severity_check_row`(file: `scripts/lumos:5418`)用途不同。
2. ④d 帳列欄位名
   - 前:「帳列欄位有 … report」(隱含)
   - 後:明寫欄位是 `report_path` 與 `report_sha256`。
3. ③ 命名撞車 + 形狀對齊
   - 前:「處置閘第五條合取」「生效日:常數 `2026-09-12`」
   - 後:「處置閘加『資安席』一步(`_disposal_security_step`,照 `_disposal_clause_step` 形狀:回 fail/ok/skip、自印一行、fails 加 `資安席`)」;生效日改 `_SECURITY_SEAT_SINCE = "2026-09-12T00:00:00+08:00"`,照 `_CLAUSE_GATE_SINCE`(file: `scripts/lumos:4388`)用 `_loop_ts_key` 比,ts 讀不動 → fail。
4. ④f 凍結 / 回放(編排者自己開檔補查)
   - 發現:凍結時整個判定以 spec_sha_override 模式重算(file: `scripts/lumos:649`),且只凍判定輪那一輪的報告檔(file: `scripts/lumos:657`)。
   - 後:新增一句「凍結 / 回放模式下這一步只看帳列(席名、tier、有沒有記 report_sha256),不重讀報告檔——否則早幾輪的資安席會被判成缺證據,回放恆報假漂移」,並加一條驗收。

以上四條都沒有動到〈人裁〉節(核心裁定),不升級為正式 finding。

## r1 收貨(五席全到才動,2026-09-11)

- 格式:五份 `lumos report-normalize` 全數「已是正規化格式」。整合席(C)原始回覆開頭多一行開場白「Now I have everything verified. Here is the final report.」與一條分隔線,屬回覆包裝、不是報告本體,存檔時從 `severity: major` 那行起切;報告內容一字未改。架構對齊、邊界、整合三份裡的 `&lt;` `&gt;` 是通知管道轉義,還原成 `<` `>`。
- quote-check:通才 19 句、邊界、整合全數錨定;架構對齊 #2、外家否決 #4 各一句錨不到——兩句都是席位在引句裡又包了一層「」,被截成不到 10 字。
- refcheck:五份全數對得上,missing 0、out_of_range 0。
- seat-check:派工單是多席一檔,頂層沒有 materials 欄,工具判 vacuous 豁免(不判漏查或出界);既有派工單同形狀,非本輪新問題。

## 機械重現表(佐證通道與錨不到的引句)

| id | 怎麼試 | 結果 |
|---|---|---|
| D2 | 引句錨不到;同一件事 A3、B5、C3 三席都有錨定引句 → 開 `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md` 看 KEY 行與 d6 內文 | HIT(兩處都寫「處置閘第五條合取」) |
| E4 | 引句錨不到 → 讀 `skills/lumos-design-loop/SKILL.md` 第 20 行 | HIT(那是設計審派席步驟,補資安席會跟 [S1]「設計審不加」矛盾) |
| B1 | 數帳本席名 | HIT(308 個席名、109 個帶兩個以上連字號,含 `外家codex-gpt-5.6-terra`) |
| C1 | 同 B1 | HIT |
| A2 | 找 `t_loop_next_roster` 的不佔 W 斷言 | HIT(斷言 == 3,現行號因另一個會談的未提交改動移到 27851) |
| E6 | `lumos loop next code-repro-e6-probe --tier high`(不帶 --orchestrator) | HIT(退出碼 2,要求帶 --orchestrator;帳本零寫入) |
| C4 | `lumos loop status code-batch2 --roster --repo .` | HIT(應派 required 同門 5;加一席 required 就變 6、實派 5 → 席數不夠) |
| E1 | 讀 `_hash_chain_check` 與代碼審帳列 | HIT(代碼審每輪 reviewed=result=該輪 patch 指紋,輪與輪之間本來就不接,鏈續性檢查用不上 → 改用「檔案清單涵蓋」) |
| E2 | 讀凍結流程 | HIT(第一趟退出碼 1 照樣往下凍;第二趟帶凍結指紋重算;閉包只收判定輪檔) |

## 處置

- 24 條(A1–A5、B1–B5、C1–C5、D1–D3、E1–E6)全數折入計劃,放行 0、重現不到 0(refuted: none)。
- 核心裁定(〈人裁〉節)沒有被任何一條動到。

## 鏡像核對(便宜 agent,只看本輪 diff+席報告目錄)

- 24 條逐條 PRESENT;七個鏡像段口徑一致,舊規則字串只剩「原本…已刪除/不用…」的歷史交代;pitfalls-code-loop 的 KEY 行與 d6 已無「第五條合取」。
- 它點出兩個新寫、沒人驗過的說法,當場處理:
  1. 外家額度理由 → 改標「推論,未實測」,並指向 templates.md §3 ④ 的額度註記。
  2. 「凍結 patch 抓得出檔案清單」→ 實看兩個真實代碼審迴圈的凍結 patch(共 5 份),都是標準 unified diff、每檔一行 `diff --git a/… b/…`;另補一條:git 預設會把中文檔名加引號跳脫,既有 `_delguard_parse_diff` 不處理引號,所以計劃改寫成「兩邊先還原原字再比」,驗收加一條中文檔名的案例。
