preflight-4: ran

## 前掃語意修正

前掃一席唯讀掃 `Projects/資安風險提問分階段_計劃`(2026-10-19),作者逐條開檔重驗後修真檔。下面只記「④機械宣稱驗語意」類(某機制現在會做 X 但不成立);①未定義詞、②壞引用、③自相矛盾與存在類命中直接修真檔,不在這裡逐條記。佐證行號以修改當下的 `scripts/lumos` 為準(分支 EnzoHsieh-Android/security-gate,基底 301b0916)。

### P4-1 「至少兩個不同強詞才觸發」現在的引擎做不到

- 修改前:「- 需求與架構兩階段要求至少兩個**不同的**強詞才觸發。」(沒提引擎要改);arch-sec-secrets、arch-sec-supply 的觸發寫「…任一」。
- 修改後:新增「**觸發規則的新資料形狀(引擎改動,新增)**」一段:新項改用選填鍵 `triggers`(`words`、`min_distinct`、選填 `plus_any`),既有 25 項照舊只用 `when`;一項只能二擇一;判斷收成一支函式;`--stage --json` 照樣原樣序列化,新項多 `triggers` 鍵、既有項 JSON 逐字不變。arch-sec-secrets、arch-sec-supply 改成各自詞表至少兩個不同的詞;拿掉「安裝」「套件」「pip」,改用 `pip install` 加詞界。條款加 S6 撞詞樣本、S11。
- 佐證:`scripts/lumos:49099` `_pitfalls_stage` 用 `any(re.search(w, text) for w in f["when"])`,任一條命中就觸發;`scripts/lumos:49109` `--json` 把 facets 整列 `json.dumps`;`scripts/lumos:31055-31058` `_REQ_FE_WHEN` 的詞界寫法 `(?<![a-z0-9])…(?![a-z])`。

### P4-2 verify-sec-evidence 與 open 格子不能靠 `pitfalls --stage` 列

- 修改前:verify-sec-evidence 觸發「計劃連到登記了資安護欄的 Systems,或觸發了上面任一資安面」;〈四〉「open 只在盤點與 `pitfalls --stage` 的驗證、交付階段列出。」
- 修改後:verify-sec-evidence 改成只看文字(通用強詞至少兩個不同的);新增「**跟筆記庫有關的檢查放在讀得到筆記庫的指令**」一段:計劃連到哪些有資安登記的 Systems、open 格子由 `security list` 與 `spec-gate`(新增一行提醒、不擋)列出,`--stage` 只多印一行指路;〈四〉改成「open 只在 `security list` 列出、spec-gate 提醒」。條款加 S13。
- 佐證:`scripts/lumos:49082` `_pitfalls_stage(md, stage, as_json, diff=None)` 只收計劃檔路徑;`scripts/lumos:49095` 只讀那一個檔;`scripts/lumos:49100` 待決問題也從那份檔的開頭欄位解析(註解「不需要筆記庫」);函式裡沒有 inventory 或 coverage 的輸入。

### P4-3 「盤點照舊列為待審適用性」不是照舊

- 修改前:不適用那列的格子狀態「`not_applicable`;盤點照舊列為待審適用性(盤點不裁核可足不足)」。
- 修改後:「`not_applicable`;盤點另列一區「待審適用性的格子」(新增輸出,見下)」,並加「**待審適用性的格子是新行為**」一條:v2 新增 `applicability_pending_cells`,跟既有 `applicability_pending_control_ids` 分開;另寫明護欄層與格子層 not_applicable 的差別與 S3 判法。
- 佐證:`scripts/lumos:7215` `applicability_pending_control_ids` 只取護欄自己 `reported_status == "not_applicable"`(在 `_secinv_surface` 裡),沒有 considerations。

### P4-4 「358 篇計劃有 221 篇命中」「草案 99 篇」的口徑

- 修改前:「本 repo 358 篇計劃有 221 篇命中(2026-10-19 實數)」;「2026-10-19 在本 repo 358 篇計劃上量:現行 deliver-security 觸發 221 篇;草案「至少兩個不同強詞」觸發 99 篇。」
- 修改後:現行數字照可重跑指令重算並寫口徑:提交 301b0916 上 `Projects/` 358 篇筆記有 222 篇命中,其中檔名帶 `_計劃` 的 298 篇有 188 篇命中(用 deliver-security 那條正規式對全文 `re.search`,本篇自己也算在內),附重跑指令;草案的 99 篇沒有可重跑的指令、詞表也已改,刪掉,改寫成上線前用同一種指令量。
- 佐證:`scripts/lumos:31048` deliver-security 的 `when` 是 `會員|使用者|帳號|權限|個資|付款|登入|管理員`;重算指令與輸出(298 188;全部 358 222)在本輪作者的終端機跑出。

### P4-5 risk_accepted 的到期判法

- 修改前:「`risk_accepted`;到期隔天自動變回 `open`」(沒有起算點,30 天上限也沒說是新增)。
- 修改後:30 天從核可決策的 `decided` 日起算;到期日當天仍有效、隔天變回 open,跟盤點現在處理護欄例外的時點一樣;補償措施、到期日進 considerations 欄位;核准來源照姊妹計劃 d6(簽章金鑰)。S4 跟著改。
- 佐證:`scripts/lumos:7148-7151` 護欄例外是 `exp < today` 才列 `exception_expired`,當天只提示;現況沒有最長 30 天的上限,是新增規則。

## 前掃判錯、沒改的

- 無。前掃各條重驗都成立。前掃「未核」的 ASVS SSRF 章節已查:OWASP ASVS 官方 GitHub 標籤 `v5.0.0_release` 的 `5.0/en/0x10-V1-Encoding-and-Sanitization.md` 有 1.3.6(SSRF),所以 outbound 補掛 V1、保留 V4、V15(本篇自建對應);其餘外部標準條目維持前掃的「未核」,本輪沒查。

## r1 處置

r1 七席共 51 條(blocking 33 條,數法:各席報告裡 `blocking: 是` 的行數)。組別照編排者裁定:B 計劃本身是 H1–H19,跨兩篇的照 G 組(G6 相容、G13 核可物件)。正確性、回滾兩席用數字編號,照原編號;架構對齊席沒有編號,依報告出現順序記成 F1–F7;邊界席的 F9 是「已讀無 finding」,不算一條。

| 席位發現 | 組 | 處置 | 一句 |
|---|---|---|---|
| 正確性-sonnet#1 | H8 | folded | file_upload 補 authz-object、authn-identity、flow-abuse;export、file_download、message_consumer 補 authn-identity;export 的大量請求歸 file-handling 塞爆空間那格,不另加 flow-abuse;表的改動標明待使用者照 d1 核可 |
| 正確性-sonnet#2 | H6 | folded | 覆蓋只算 active、concerns 含 security、非 retired;candidate 另一態 candidate:<id> |
| 正確性-sonnet#3 | H5 | folded | 有沒有工具由姊妹計劃閘門讀 security-tools.json 判,逐類寫替代欄,多類取聯集,S5 指到姊妹計劃 S14 |
| 正確性-sonnet#4 | H1 | folded | 棄「建立時版號」,資料列寫入時帶 threat_table_version;S10 改寫 |
| 正確性-sonnet#5 | H9 | folded | 核可不合格的列不參與互斥;considerations 壞參照列 cell_errors |
| 正確性-sonnet#6 | H15 | folded | S9 樣本改成「權限」與「登入」,兩個詞同時在 deliver-security 觸發詞與通用強詞裡 |
| 正確性-sonnet#7 | H14 | folded | 詞界照實寫、每元素帶 (?i)、允許複數 s;session、token 在本 repo 的命中數寫進〈三〉(見下 M5) |
| 邊界-sonnet#F1 | H1 | folded | 同 正確性#4 |
| 邊界-sonnet#F2 | H2/G6 | folded | v1/v2 雙讀、預設與並存規則以姊妹計劃〈一〉為準,本篇指過去 |
| 邊界-sonnet#F3 | H3 | folded | `_secinv_check_links` 對 assets、surfaces 放行字面 @repo,只放寬這一個字;一 repo 根一組與全庫一份 inventory 一致 |
| 邊界-sonnet#F4 | H4 | folded | asset_ids 空陣列列 surface_without_assets;S16 |
| 邊界-sonnet#F5 | H5 | folded | 同 正確性#3 |
| 邊界-sonnet#F6 | H9 | folded | 五種壞 considerations 都列 cell_errors;S19 |
| 邊界-sonnet#F7 | H9/G9 | folded | S4 補 30 天整、31 天、到期早於核可、決策缺 decided |
| 邊界-sonnet#F8 | H14 | folded | 詞界照實寫;S6、S7 的十篇樣本列出檔名並釘提交 e56c7234 |
| 整合-sonnet#F1 | H1 | folded | 同 正確性#4;類別改名或刪除列 unknown_category |
| 整合-sonnet#F2 | H6 | folded | 同 正確性#2;S18 |
| 整合-sonnet#F3 | H3 | folded | 同 邊界#F3;S15 |
| 整合-sonnet#F4 | H2/G6 | folded | 同 邊界#F2 |
| 整合-sonnet#F5 | H5 | folded | 同 正確性#3 |
| 整合-sonnet#F6 | G13 | folded | considerations 用姊妹計劃的核可物件與內容簽章,兩種 outcome 都要簽;v2 清單由姊妹計劃〈一〉持有 |
| 整合-sonnet#F7 | H10 | folded | spec-gate 先看連到的節點有沒有圍欄字樣、走共用公開函式、open 口徑寫清楚並另印全庫總數;lands_in 補 Systems/規格閘 |
| 整合-sonnet#F8 | H11 | folded | 新增 `security list --questions`,帶 [cell:<id>]、上限 30、--plan 去重、{角色}規則;S21 |
| 整合-sonnet#F9 | H13 | folded | A 臂釘新風險面上線前的 lumos 版本,寫進〈五〉並列入 P2 處置說明 |
| 整合-sonnet#F10 | H14 | folded | 允許複數 s;S7 加 tokens、secrets 樣本 |
| 整合-sonnet#F11 | H16/H18 | folded | 七列寫進情境出題、triggers 形狀寫進 pitfalls-code-loop、漂移測試比標題版號、表格逐欄切集合比;盤點契約段與 P2 處置說明已列。七項風險面不加漂移守衛:既有 25 項本來就沒有,不是這次引入的缺口 |
| 整合-sonnet#F12 | H4/H5 | folded | 多類取聯集;空 asset_ids 列錯 |
| 資源-sonnet#F1 | H12 | folded | considerations 改成圍欄頂層鍵,可拆在各 Systems 節點 |
| 資源-sonnet#F2 | H10 | folded | 讀不完整時 cells 標 unknown 不給 open 數,spec-gate 只印警告;S20 |
| 資源-sonnet#F3 | H12 | folded | 格子上限 100000、預設只印計數與 open、--all 逐格;S22;量測寫成 REVISIT |
| 資源-sonnet#F4 | H12 | folded | 先建(入口、資產、類別、角色)索引一次線性建表 |
| 資源-sonnet#F5 | H10 | folded | spec-gate 先看連到節點有沒有圍欄字樣才建快照 |
| 資源-sonnet#F6 | H11 | folded | 候選題上限 30、以格子 id 去重、重跑冪等 |
| 回滾-sonnet#1 | H10 | folded | 格子層錯誤放 cell_errors、不進 errors,姊妹計劃閘門寫明不讀 |
| 回滾-sonnet#2 | H2/G6 | folded | 雙讀版先上線,回退舊工具前先降圍欄,〈回退〉指到姊妹計劃 |
| 回滾-sonnet#3 | H1 | folded | 未知類別 id 列 unknown_category(不擋);版號跟資料列走 |
| 回滾-sonnet#4 | H10 | folded | spec-gate 那行出任何錯只印一行警告,不影響判門與留痕 |
| 回滾-sonnet#5 | H19 | folded | 表正本與鏡像常數同一提交退 |
| 架構對齊-sonnet#F1 | H10 | folded | spec-gate 走 security list 也用的公開共用函式,不另寫解析、不用一般 Env |
| 架構對齊-sonnet#F2 | H18 | folded | 指路行改成表的選填鍵 hint 由通用迴圈印;--json 照原樣序列化 |
| 架構對齊-sonnet#F3 | H3 | folded | 寫明在 `_secinv_check_links` 放寬、只對 @repo |
| 架構對齊-sonnet#F4 | G13 | folded | 例外與 considerations 共用同一個核可物件、同一支檢查、同一種 30 天算法(從 approved_on 起算) |
| 架構對齊-sonnet#F5 | H17 | folded | 入口上的欄位改名 boundary_crossed,寫明跟護欄 trust_boundary 的差別 |
| 架構對齊-sonnet#F6 | H14 | folded | 每個 words 元素各自帶 (?i) |
| 架構對齊-sonnet#F7 | H16/H10 | folded | 威脅類別表另開 Systems/資安威脅類別表 當正本,不擴大情境出題;lands_in 補 Systems/規格閘 |
| 外家finder-codex#F1 | H7 | folded | authz-object、authn-identity、flow-abuse 三類格子鍵加角色,controls 加 actor_ids;S17 |
| 外家finder-codex#F2 | G13 | folded | considerations 兩種 outcome 都要內容簽章,沒簽不算數 |
| 外家finder-codex#F3 | H9 | folded | 不合格列不參與互斥、有有效護欄就是 control;S3、S4 改寫 |
| 外家finder-codex#F4 | H1 | folded | 同 正確性#4 |
| 外家finder-codex#F5 | H2/G6 | folded | 同 邊界#F2 |
| 外家finder-codex#F6 | H11 | folded | 同 整合#F8 |

## r1 機械重現

工作樹 /Users/enzo/orca/workspaces/lumos-toolchain/security-gate,基底 e56c7234;合成 vault 放 /private/tmp/claude-501/sec-fold2/,做完已刪。

- M1(G5):`python3.14 scripts/lumos security list` → rc 0、`read_complete: true`、`registration_complete: false`、零條目、errors 空(細節見 `governance/review-reports/安全主張驗收閘/r1-intake.md` 的 M1)。
- M2(H3,@repo 在 `_secinv_check_links`):合成護欄 `surfaces:["@repo"], assets:["@repo"]` → rc 2,兩筆 `reference_error`(assets、surfaces 指到 inventory 沒有的 ID);對照組 S1/A1 rc 0。HIT。
- M3(H2,schema_version):同塊改 `schema_version: 2` → rc 2,`unknown_schema_version`「schema_version 只支援 1」。HIT。
- M4(H4,空 asset_ids):inventory 的入口寫 `asset_ids: []` → rc 0、errors 空,通過驗證。HIT:現行讀取器放行空陣列,格子會靜默一格都不長。
- M5(H14,觸發詞):提交 e56c7234 上,用〈三〉的通用強詞表、每元素 `(?i)(?<![a-z0-9])詞s?(?![a-z0-9])` 對 `Projects/*_計劃.md` 全文 `re.search`:298 篇、71 篇至少兩個不同強詞、21 篇同時有 session 與 token、7 篇只靠這兩個詞湊到兩個、156 篇零命中;S6 的十篇從零命中裡取,S7 的十篇從命中四個以上不同強詞裡取(資安護欄唯讀盤點_計劃 是三個)。
- M6(pre-push 對 tag):`scripts/hooks/pre-push` 只有 `refs/heads/*` 那條路叫 `code-loop check`,tag 走 advisory;CI `on:` 沒有 tags(細節見姊妹 intake 的 M4)。
- M7(blocking 數):`grep -cE 'blocking: ?是'` 逐席:正確性 4、邊界 5、整合 9、資源 2、回滾 4、架構對齊 3、外家 6,共 33;發現數 7、8、12、6、5、7、6,共 51。

## 帳上 id 對照

帳上發現 id = 席名縮寫 + 席報告內編號:正=正確性-sonnet、邊=邊界-sonnet、整=整合-sonnet、資=資源-sonnet、回=回滾-sonnet、架=架構對齊-sonnet、外=外家finder-codex(例:正3 = 正確性-sonnet#F3)。發現種類一律 spec(被審文件缺陷)。
