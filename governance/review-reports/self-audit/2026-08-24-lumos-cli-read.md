# Self-audit: Systems/lumos-cli-read.md

角色:自足性審計員,不知道任何開發脈絡,只讀該筆記 + 對照 `scripts/lumos` 原始碼與 `scripts/test_lumos.py`(不改任何檔案)。
問題:一個沒有背景的人照這篇的描述去理解/使用 CLI 讀面(14 個 read/traverse 原語),會不會被帶錯?
筆記路徑:`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md`(稽核時 `updated: 2026-08-23`,`self_audit: sonnet/2026-08-16`)

---

## 逐條核對

### 共同地基:find_vault → load_vault → Env(87-88 行)

**站得住**。`find_vault`(9833)、`load_vault`(192)、`Env`(270)三者存在,`class Env` 確實持有 `notes`/`by_stem`/`edges`(雙向)。「不改圖譜節點檔,context/show 寫 usage-log、doctor --ci 寫 governance-log」的措辭與 `cmd_context`(6305起,呼叫 `_usage_log`)、`cmd_show`(6247起,呼叫 `_usage_log`)、`_append_governance_log`(430起)的實際行為一致。

### 「14 個原語」清單本身(90-108 行)

**站得住**——逐條核對如下:

- `search`(1670 `cmd_search`):`--path/--regex/--files-only/--code/--include-superseded/--any/--no-any`全部存在於 argparse(15529-15545),幫助字串與筆記描述一致。**排除 fenced+inline code、`--code` 才含**、**排除 superseded、`--include-superseded` 逃生**、**多詞回退預設開、`--no-any` 關**,三條核心行為都在 `cmd_search` 原始碼裡逐段可核實(1637-1888)。
- `context --brief`(6305 `cmd_context`):`--brief` 存在(15337),頭部先印 `meta`,再印「提醒:這篇有『動了會壞』的合約」+ 逐條 `★INVARIANT★/★DEBT★`(用 `extract_contracts`),語意正確;唯一極小落差見下方「非致命觀察」。
- `show --body-only`(6247 `cmd_show`):`--body-only` 存在(15346),重開檔失敗走 `try/except` → `print(...,file=sys.stderr); return 2`,不是裸 traceback,與筆記描述逐字相符。
- `contracts`(2456 `cmd_contracts`):`★INVARIANT★`/`★DEBT★` 顯示、`[test:]` 未綁印「⚠ 提醒:沒綁測試」,`extract_contracts` 的 `INVARIANT_RE`/`DEBT_RE` 錨定 `^KEY:` 開頭(1919-1922),「只認 KEY 行前綴標準格式」屬實。
- `doctor [--ci]`(459 `run_doctor`,非 `cmd_` 前綴):`--ci` 確認等於 `--strict` + 無色彩(15325-15329 argparse help 字串逐字一致)。但**列出的 check 清單不完整**,見下一節「站不住」。
- `links`/`backlinks`(1888 `cmd_links`,`reverse=True` 即 backlinks):兩個子指令共用同一函式,argparse 15331-15333 迴圈註冊,屬實。
- `map --depth`(1898 `cmd_map`):`↺` 標記與「已出現過」語意逐字對上(1898-1916)。
- `export --folders <…> [dot|mermaid]`:**站不住**,見下方獨立小節。
- `query`(6649 `cmd_query`,2026-08-16):`--tag`(可重複 AND)/`--no-tag`/`--active`/`--contract`/`--linked`/`--include-superseded`/`--json` 全部存在(15563-15576),行為（`--active` 排收案態集合、`--contract` 用真解析器、`--linked` 1-hop 不含錨點、預設排 superseded、bare rc2)逐條與程式碼吻合。
- `decisions [--superseded]`(6449 `cmd_decisions`):存在。
- `stale [--match] [--candidate]`(6560 `cmd_stale`):**「bare `--candidate` 或空 `--match` 直接 rc2」逐字對上**(6560-6569:`if candidate and not match: ... return 2`)。
- `recent --days`(6704 `cmd_recent`)、`stats`(6714 `cmd_stats`):皆存在且行為簡單、與描述一致。

### `export` 語法描述 —— **站不住**

- 筆記寫的是 `export --folders <…> [dot|mermaid]`(第 101 行),讀起來像是 dot/mermaid 可以接在 `--folders` 值後面當一個獨立的（類位置）參數。
- 程式碼證據:`scripts/lumos` 15582-15586 只有 `--format {mermaid,dot,html}`(預設 mermaid)與 `--folders FOLDERS [FOLDERS ...]`(`nargs="+"`),**沒有任何位置參數**接收 dot/mermaid。`lumos export --help` 實際輸出:
  ```
  usage: lumos export [-h] [--format {mermaid,dot,html}]
                      [--folders FOLDERS [FOLDERS ...]] [--output OUTPUT]
                      [--standalone]
  ```
- **實測會被帶錯,不是理論推測**:照筆記字面打 `lumos export --folders Systems dot`,因為 `--folders` 是 `nargs="+"` 貪婪吃參數,"dot" 會被吃進資料夾清單(變成一個不存在、被忽略的資料夾名),`--format` 仍是預設值 `mermaid`——**實際跑出來是 mermaid 輸出,不是使用者以為指定的 dot**,而且不報錯、不提示,完全靜默走錯路。
- 附帶:筆記也完全沒提到 `--format html`(互動視圖)這個選項,而同一篇筆記下方「近期修正」花了兩大段講 export html 的功能迭代——讀者從「14 個原語」這節完全看不出 export 能產生 html。

### doctor 的 check 清單 —— **部分站不住(不完整)**

- 「14 原語」bullet(96-97 行)與 summary KEY 行(第 21 行)列出的 check:1/4~4/4、同名守衛、frontmatter lint、Check T/R/H、Check P、Check E1/E2/E3、Check J。
- 程式碼裡 `run_doctor` 實際的 `section(...)` 呼叫(468-1385)還有:**1.5/4(frontmatter 收尾)、Check M(status 欄位與標籤一致)、Check C(跨專案核心指標存在性)、Check S(L4 自足性審計提醒)、Check S2(about_code 標後正文又改)、Check K(唯一測試提醒)、Check D(CLAUDE.md 紀律區塊比對範本)、Check V(valid_under 超過 90 天未回頭看)、Check Y(方法/類別是否存在於程式碼)、Check N(重算標記數字校驗)、Check W(工具鏈版本落後)**——大約再多 10 個獨立檢查段落,筆記兩處(bullet 與 KEY 行)都完全沒提。
- 這不是「筆記沒空間寫全部細節」的正常取捨,因為筆記已經逐個點名到字母(T/R/H/P/E1/E2/E3/J),讀者很自然會把這串當成「doctor 檢查的完整清單」,實際上漏了將近一半。尤其 Check Y(方法/類別改名/找不到)與 Check V(前提 90 天未重驗)是相對常見會觸發、且對「這篇筆記還可不可信」判斷很關鍵的檢查,遺漏比較傷。

### `parse_decisions(decisions/stale)`(DEP 行,第 29 行)—— **站不住**

- 筆記寫:`DEP:...｜parse_decisions(decisions/stale)｜...`,語意是 `parse_decisions` 由 `decisions` 與 `stale` 兩個指令共用。
- 程式碼證據:`grep -n "parse_decisions(" scripts/lumos` 命中 962/1037/2392/2399/2769/6453/6459/7969/7986/8033/8076/8082——全部落在 `run_doctor`(Check R/Check E2 需要)、`cmd_decisions`(6449-6459)、`decision-add`/`decision-supersede`/`decision-reindex` 之內。**`cmd_stale`(6560-6649)整段完全沒有出現 `parse_decisions` 或 `decision` 字樣**——`stale` 讀的是 `valid_under`/`revalidate_when` 兩個純量/清單欄位,跟決策(`decisions:` frontmatter 區塊)無關,不共用 `parse_decisions`。
- 這條 DEP 行邏輯上抄了 `status_of(links/map/stale 標狀態)`與`extract_contracts(contracts/context 共用)`同款句式,但套錯了函式——正確的「decisions/stale 共用」關係在程式碼裡查無實據。

### 「13 個」vs「14 個」讀指令計數矛盾 —— **站不住(內部自相矛盾)**

- 文件標題與開場白(第 82-83 行)、`## 14 個原語` 標題都說「14 個」,列出的 14 條也數得出剛好 14(search/context/show/contracts/doctor/links/backlinks/map/export/query/decisions/stale/recent/stats)。
- 但 frontmatter `decisions[d1].content` 與 body `## 關鍵設計` 第一條(110-111 行)都寫「**13 個**讀指令不改圖譜節點檔」。
- 這不是筆誤式的隨機數字,而是兩種不同計數口徑沒有互相校準:若把 `links`/`backlinks`(共用同一 `cmd_links` 實作)算成 1 個原語,總數是 13;若照 CLI 兩個獨立子指令算,是 14。文件同時用了兩種口徑卻沒有註明,會讓對照著數的讀者以為自己漏數或多數了一個。`query` 是 2026-08-16 才加入的第 14 個(KEY 行 18 有明確日期),`d1` 決策內容 `decided: 2026-06-26`——早於 `query` 加入,**沒有跟著更新到 14**,是尚未同步的舊帳。

### 相關 > 實作落點(120-121 行)—— **站不住(遺漏兩個原語)**

- 這行列的函式:`cmd_search/cmd_context/cmd_contracts/run_doctor/cmd_links/cmd_map/cmd_export/cmd_decisions/cmd_stale/cmd_recent/cmd_stats + load_vault/Env/find_vault`。
- **完全漏了 `cmd_show`(2026-07-21 加入)與 `cmd_query`(2026-08-16 加入)**——這兩個都是「14 個原語」清單裡正式列出的項目,函式本身也確實存在(6247/6649)。跟前一節的「13 vs 14」矛盾同源:新原語加進了主表,卻沒同步更新到文件尾端的實作指標清單。

### 相關 > 操作表權威(119-120 行)—— **站不住(指向的內容已不存在)**

- 筆記寫:「`skills/lumos-project-notes/SKILL.md`(25 子命令全覽:讀取 14 + 寫入 7 + 安裝/生命週期 4)」。
- 實讀 `skills/lumos-project-notes/SKILL.md` 全文(81 行):現狀是一份「一頁手冊」,按「進場/動手前/寫回/收工」四階段組織,**完全沒有「25 子命令全覽」或「讀取14+寫入7+安裝生命週期4」這種分類清單**。這份分類清單目前的真正落點是 `commands/INDEX.md` 的「二、八類子檔」表(按情境分八類,不是按讀/寫/安裝三分),且 `INDEX.md` 裡也數不出「25」這個總數的分解方式。
- 讀者照這行去 SKILL.md 找那個 25 條分類表會撲空,要另外找到 `commands/INDEX.md` 才對得上——這行的指路已經過期。

### `scripts/lumos:416 自述`(KEY 行 21,doctor 段)—— **站不住(行號漂移)**

- 筆記引用「寫者=doctor --ci＋anchor approve,scripts/lumos:416 自述」。
- 實際該自述字串位於 `scripts/lumos:435`(`_append_governance_log` 的 docstring),第 416 行現在是完全無關的 `_reco_fused`/feature 評分程式碼。屬於檔案成長後行號漂移沒跟著改,不是內容錯,但照著行號去讀的人會讀錯地方。

### `git_last_change_dates`(KEY 行 12)—— **站不住(過時表述)**

- 筆記寫:「是 about_code 過期判準的材料...尚未接進 impact,只是原語」,語氣是「還沒接,以後可能會接」。
- 程式碼證據:`grep -n "git_last_change_dates(" scripts/lumos` 只命中函式自己的 `def`(13754),**全 repo 零呼叫點**。同檔 `t_git_last_change_dates_batch` 測試的 docstring 明講:「★原為 about_code 過期判準的材料,2026-08-24 該判準改記正文雜湊後本函式暫無呼叫者,保留★」——也就是 about_code 過期判準的設計已經改道走「正文雜湊」,不再打算接這個函式進 impact,這個函式目前是被留著但**沒有下文**的孤兒工具,不是「還沒輪到」的待辦。筆記的措辭會讓人誤以為這是進行中的既定計劃。
- 註:此變更與下一條的 `LUMOS_IMPACT_HARD_PIN`一樣,發生在 2026-08-24(commit d0456b8,與本次稽核**同一天**),屬於「同一次工作內寫回」規矩追不上的最新落差,非長期漂移。

### `LUMOS_IMPACT_HARD_PIN` 預設值(summary KEY 行 14)—— **站不住(當下已錯)**

- 筆記寫:「RISK 類 indirect 不再保送必看——`LUMOS_IMPACT_HARD_PIN=1` 時降入 JSON 頂層 lane 參考道(**預設 0** 待考卷轉正)」。
- 程式碼證據:`scripts/lumos:14466`:`_hard_pin = int(_impact_knob("LUMOS_IMPACT_HARD_PIN", 1))`——**預設值是 1,不是 0**。`git log -S'"LUMOS_IMPACT_HARD_PIN", 1' -- scripts/lumos` 定位到 commit `d0456b8`(2026-08-24,今天),commit message 明講「轉正」。同倉 `t_impact_hard_pin_lane` 測試 docstring 也已更新為「預設(2026-08-24 考卷轉正=1)」——**同一個 repo 內測試檔已經追上,筆記 KEY 行沒追上**,是本篇裡最直接會讓人判斷錯「這個旗標現在到底預設開還關」的一條。
- 影響:如果有人照這句話理解「預設不影響現有 RISK 排序,要手動開 `=1` 才會把 RISK indirect 降級」,今天開始這個理解是反的——不設定環境變數的話,RISK indirect **現在就已經**被降到 lane、不進 pinned 必看集合了。

### `[test:]` 引用逐條核對(★★重點★★)

以下全部**逐條實跑** `python3 scripts/test_lumos.py -k "<測試名>"`,函式存在、內容與筆記宣稱相符、全部通過:

| 測試名 | 對應宣稱位置 | 結果 |
|---|---|---|
| `t_context_header_extra_tag_families` | KEY 14 標籤收編 | ✓ 存在,驗的正是「頭部攤出 priority/scope/flag 家族」,通過 |
| `t_impact_contract_risk_axis` | 同上 | ✓ 存在,驗 RISK·值分類與軸序,通過 |
| `t_impact_hard_pin_lane` | 同上 | ✓ 存在,驗 lane 降級/cap/free 集不動,通過(且證實了上面的預設值落差) |
| `t_search_aliases_field` | KEY 15 aliases | ✓ 存在,通過 |
| `t_quote_check_normalization_and_verdict` | KEY 16 quote-check | ✓ 存在,rc0/rc1/rc2 語意驗證通過 |
| `t_query_tag_and`/`t_query_no_tag_and_active`/`t_query_contract_uses_real_parser`/`t_query_linked_scope`/`t_query_forget_superseded`/`t_query_bare_rc2`/`t_query_json` | KEY 18 query | ✓ 全部存在,逐條斷言與 `cmd_query` 行為一致,57 案例全過 |
| `t_search_multiword_fallback_is_default_and_only_on_zero`/`..._reports_per_term_coverage`/`..._scope_message_covers_path_and_superseded` | KEY 23 多詞回退 | ✓ 全部存在,39 案例全過 |
| `t_search_forget_superseded` | KEY 25 真遺忘 | ✓ 存在,19 案例全過 |
| `t_check_j_regen`/`t_check_j_git` | KEY 21 Check J | ✓ 全部存在,27 案例全過 |

**沒有發現掛羊頭賣狗肉的測試名**,也沒有發現測試存在但驗的不是那句話的情況——這部分的自驗宣稱可信。

### 非致命觀察(不列入「站不住」,僅供參考)

- `context` 段落用「頭部直接攤出 ⚠ 合約」形容合約顯示——實際輸出文字是「提醒:這篇有『動了會壞』的合約,動手前一定要看」,並沒有字面 `⚠` 符號(`⚠` 目前只用在「狀態表過期偵測」那個獨立警示)。語意上「頭部顯眼位置提示合約」仍然成立,只是符號描述不精確,不影響使用,不列為站不住。

---

## 總結

**這篇整體站不住(否)。**

核心行為描述(14 個原語各自的旗標、真遺忘排除、多詞回退、query 的 WHERE 語意、doctor --ci、show/contracts/map 的具體語法)大部分都對照程式碼站得住,而且列出的 `[test:]` 逐條實跑全部存在且測的真是那句話,沒有造假證據的問題,這部分做得紮實。

但有多處會實際帶錯人,其中兩處是可以直接讓人跑出錯誤結果或去錯地方:

1. **`export --folders <…> [dot|mermaid]` 語法描述會讓人跑出靜默錯誤的輸出**——照字面打 `--folders X dot` 會被 `--folders`(nargs="+")吃掉,`--format` 仍是預設 mermaid,不報錯、結果卻不是使用者要的格式(已用實際指令驗證此路徑)。
2. **`LUMOS_IMPACT_HARD_PIN` 預設值寫反**(筆記說預設 0,程式碼今天起預設 1),同倉測試已經追上但筆記沒有,會讓人誤判 RISK 類節點目前到底有沒有被降級。
3. **`parse_decisions(decisions/stale)` 這條 DEP 關係查無實據**——`cmd_stale` 完全不呼叫 `parse_decisions`。
4. **doctor check 清單漏掉約 10 個實際存在的檢查段落**(M/C/S/S2/K/D/V/Y/N/W + 1.5/4),讀者無法從這篇得到 doctor 完整的檢查範圍。
5. **「13 個」與「14 個」讀指令計數在同一篇內自相矛盾**,`query` 加入後主表更新到 14,但「關鍵設計」與 frontmatter 決策 d1 停在舊的 13。
6. **「相關 > 實作落點」漏列 `cmd_show`/`cmd_query`**,「相關 > 操作表權威」指向的 SKILL.md「25 子命令全覽」段落已經不存在(現狀是 `commands/INDEX.md` 的八類分法)。
7. `scripts/lumos:416` 的自述行號已漂移到 435(小,但會讓人讀錯地方)。
8. `git_last_change_dates` 的「尚未接進,只是原語」語氣掩蓋了「原本的接法(about_code 判準)已經改道、目前零呼叫點」的事實。

第 1、2 項是「照做會得到錯結果/錯判斷」等級的問題,第 3-8 項是「查不到/會撲空/認知不完整」等級,但數量不少,累積起來會讓一個沒有背景的人對這份筆記的可信度打折扣。

## 修正建議

1. `export` 那行改成 `export [--format mermaid|dot|html] [--folders <資料夾…>]`,明確標出 `--format` 是獨立旗標、`--folders` 是貪婪多值,並補上 html 格式的存在(對應下方「近期修正」的大量 html 相關內容)。
2. summary KEY 行 14 的 `LUMOS_IMPACT_HARD_PIN`「預設 0 待考卷轉正」改成「預設 1(2026-08-24 已轉正,`=0` 為逃生旗標)」。
3. DEP 行把 `parse_decisions(decisions/stale)` 改成 `parse_decisions(decisions 專用;doctor Check R/E2 亦呼叫)`,拿掉 stale 的錯誤歸屬。
4. doctor 段落(bullet 與 KEY 行 21)補列缺的 check(至少點名 M/S/S2/V/Y 這幾個較常觸發、影響判斷的),或者改成「詳見 `lumos doctor --help` / 原始碼 `section(...)` 全清單,以下只列跟合約/關係鏈直接相關的幾條」這種明確聲明「非窮舉」的寫法,避免讀者誤把列出的當成全部。
5. 統一「13/14」計數口徑——若把 links/backlinks 當一個原語算,`## 14 個原語` 標題與開場白改成 13;若照 CLI 14 個獨立子指令算,`關鍵設計` 與 frontmatter `d1` 改成 14,兩處挑一種說法且互相對齊。
6. 「相關 > 實作落點」補上 `cmd_show`/`cmd_query`;「相關 > 操作表權威」把 SKILL.md 那句改指到 `commands/INDEX.md`(八類子檔),或者先確認 SKILL.md 是否該恢復那段分類、二選一同步。
7. `scripts/lumos:416` 改成當下正確行號(或乾脆只寫函式名 `_append_governance_log`,不釘死行號,行號本來就會隨改動漂移)。
8. `git_last_change_dates` 那句補一句「about_code 過期判準已改道走正文雜湊,本函式目前零呼叫點,保留供未來用途」,不要只寫「尚未接進」帶出仍在排隊的錯誤印象。
