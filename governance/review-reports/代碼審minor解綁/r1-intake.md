# 代碼審minor解綁 r1 收貨紀錄

preflight-4: ran

## 首輪前掃(便宜代理,固定清單四項)

①②③與存在類直接修真檔;語意類修真檔並列在下面(修改前 → 後)。核心裁定(major 以上照舊必折、minor 可附理由放行)沒有被前掃動到。

| 類 | 命中 | 修改前 → 後 |
|---|---|---|
| ②引用 | PRIOR-ART 引「probe輪退場 d5」,那份計劃沒有 d5 | 改引 設計審收斂重定義_計劃 d5,並註明 probe輪退場 d2 原文轉述 |
| ②引用 | 「templates.md §3 的嚴重度一段」不存在 | 改成〈編排者判讀規則〉的 severity 錨,§3 派工詞指向它 |
| ③矛盾 | S6 理由寫「舊帳沒有在 major 輪放行 minor」,實際有兩份凍結判定放行過(沒帶逐條嚴重度) | 理由改成「沒帶逐條嚴重度、走照舊分支」;明寫 `_REPLAY_ENGINE_REV` 不 bump |
| ③矛盾 | 辯方合法把 major 降成 minor 後要放行,會被數量檢查誤擋 | 新增選填降級清單 `--downgraded-set`(比照 `--refuted-set` 的 intake 核對),分母加上它;新增 S8 |
| ④語意 | 記帳時檢查:載體不一定最後記,同輪報告可能還沒入帳,檢查被靜默跳過;載體自己的報告也沒算 | 數量檢查改到處置閘做(讀全輪 latest,含載體);報告讀不到照留痕重驗 fail-closed |
| ④語意 | `_report_reported_count` 數的是「非 clean」不是「minor+clean」 | 改寫成用 `_report_severities` 去檔級行後數 minor 與 clean |
| ③矛盾 | 「必須給齊」沒有條款 | 改成:沒標逐條嚴重度就走舊規則(放行即判不過),`--finding-severity` 維持選填,不需另加檢查 |
| ①未定義 | 數量檢查的分子沒講是 accepted 內還是全部 | 寫明分子=accepted 內標 minor/clean 的 id 數 |
| ③矛盾 | 逃生口說「去重」會誤擋,實際去重只會變少 | 改寫成「一條拆兩個 id、或降級沒記」 |
| 其他 | SKILL 第 7 步後段「架構對齊與棧別檢核題 minor 可 accepted」會變成重複 | 手冊一併收斂 |

## r1 收貨(七席到齊後)

報告存檔:六席同門從逐字稿取最後一則含頂格 severity 的回答;外家 Codex 取 stdout 的最終回答。`report-normalize --write` 只對可執行性、相容回放兩份做了「⚠ 搬到下一行」的純格式搬移。判準證據席的總結句被判成「總結藏更高等級」(句中引了「維持 major」字樣),退回該席,該席自己重寫總結句,用它的原文替換最後一行。

### 引句錨不到的機械重現

| id | 報告 | 引句 | 重現 | 結果 |
|---|---|---|---|---|
| T7 | r1-通才-sonnet.md | 同一個席同一份報告只算一次 | `grep -n "同一席同一份報告只算一次" r1-snapshot.md` → 第 39 行 | HIT(多抄一個「個」字,原文在) |
| P2 | r1-放水攻擊-sonnet.md | 再數 minor 與 clean 的宣告行;同一席同一份報告只算一次(鍵 `(auditor, report_sha25 | 同上第 39 行含全句 | HIT(引句在反引號中間截斷,原文在) |

### 判讀時的查證更正

- 判準證據席說凍結判定裡「major 輪加非空 accepted」有四個迴圈。查 `governance/replay/code-純文件子集/verdict.json` 與 `code-prose-conv-impl/verdict.json`:兩者的放行在 r3、r1,判定輪是 r3b(accepted 空)、r2(minor),所以「判定輪」符合的只有原本兩份。計劃照查證結果寫。
- 處置閘步驟順序:`scripts/lumos` 的 `_loop_status_disposal` 先在處置集合區塊判 accepted、再做留痕重驗,之後才是條款、資安、落點、回顧各獨立步驟;新步驟接在獨立步驟序列。
- `--refute-verdict` 寫側已強制 evidence 的 id 必在 accepted(blocker 輪例外);但帳上只存 agree/evidence/concern 字樣,不存 file:line——所以計劃要求降級放行的理由裡附 file:line,由處置閘驗存在。

### 編號與去向(載體記帳用)

根因分組:A 防放水機制(數量配平 → 逐條指回原報);B 降級(另開旗標 → 沿用辯方表態);C 判準落點與內容;D 舊帳、回放與回退;E d2 與同步;F 計數口徑與數字;G 去向、量測與退場條件;H 實作細節。

| id | 席 | 原報 | 組 | 去向 |
|---|---|---|---|---|
| T1 | 通才 F1 | major | A | 折:改逐條指回,原報 major 都要指到 folded |
| T2 | 通才 F2 | major | B | 折:撤降級清單,沿用 evidence + file:line |
| T3 | 通才 F3 | major | D | 折:改寫成只判最後一輪,列 code-規格閘半套 r1 |
| T4 | 通才 F4 | major | G | 折:去向可從帳列出,RETIRE-IF 改人工抽查 3 條 |
| T5 | 通才 F5 | minor | G | 折:不選欄補「只限修補範圍」 |
| T6 | 通才 F6 | minor | H | 折:新旗標照 --finding-severity 可重複 |
| T7 | 通才 F7 | minor | A | 折:不再數數量 |
| T8 | 通才 F8 | minor | G | 折:RETIRE-IF、REVISIT 改量法 |
| A1 | 架構對齊 1 | major | A | 折:新獨立步驟、走 _prov_check,不在 ② 讀報告 |
| A2 | 架構對齊 2 | major | B | 折:沿用 --refute-verdict |
| A3 | 架構對齊 3 | minor | B | 折:降級清單撤掉,無需共用 helper |
| A4 | 架構對齊 4 | minor | C | 折:判準移到 §3 代碼審派工詞與 SKILL 第 4 步 |
| E1 | 可執行性 F1 | major | A | 折 |
| E2 | 可執行性 F2 | major | B | 折 |
| E3 | 可執行性 F3 | major | A | 折:讀同輪每一列帳的報告,不取最新 |
| E4 | 可執行性 F4 | minor | B | 折 |
| E5 | 可執行性 F5 | minor | H | 折:讀不到或 sha 不符,新步驟自己判不過、errors=replace |
| E6 | 可執行性 F6 | minor | D | 折:S11 理由改寫,保留「major 一律折」 |
| E7 | 可執行性 F7 | minor | A | 折:clean 不提供空間 |
| E8 | 可執行性 F8 | minor | H | 折:加測試造帳提醒、S3/S8/S9 邊界案 |
| P1 | 放水攻擊 1 | major | A | 折 |
| P2 | 放水攻擊 2 | major | A | 折 |
| P3 | 放水攻擊 3 | major | B | 折 |
| P4 | 放水攻擊 4 | major | A | 折:refuted-set 指到原報 major 判不過(S6) |
| P5 | 放水攻擊 5 | minor | A | 折:逃生口只寫改正重記 |
| P6 | 放水攻擊 6 | minor | A | 放行:席位自己判定沒開新洞,換輪是既有 delta 語意,無需改動 |
| P8 | 放水攻擊 附帶 | minor | D | 折 |
| C1 | 相容回放 1 | major | A | 折 |
| C2 | 相容回放 2 | major | E | 折:decision-add 取代 d2、保留訊息原句 |
| C3 | 相容回放 3 | minor | E | 折:同步清單補齊六處 |
| C4 | 相容回放 4 | minor | D | 折:回退 bump 回放版本 |
| C5 | 相容回放 5 | minor | G | 折:明寫逃逸自動記與修正關卡的行為變化 |
| C6 | 相容回放 6 | minor | A | 折 |
| J1 | 判準證據 ① 分母 | minor | F | 折:78 輪、55 輪受益、17% 有標 |
| J2 | 判準證據 ① 週評通知 | minor | F | 折:寫成單一個案 |
| J3 | 判準證據 ① 凍結判定數 | minor | D | 折:查證後仍是兩份判定輪(見上) |
| J4 | 判準證據 ② d2 | minor | E | 折 |
| J5 | 判準證據 ③ 判準 | minor | C | 折:不以綁定為前提,補修補主張、守衛類 |
| J6 | 判準證據 ⑤ 防放水強度 | minor | A | 折 |
| J7 | 判準證據 ④ 收斂效果 | minor | G | 折:實務隱患寫量測、REVISIT 加收斂指標 |
| X1 | 外家 F1 | major | A | 折 |
| X2 | 外家 F2 | major | B | 折:降級放行要 evidence 且理由附可核對 file:line |
| X3 | 外家 F3 | major | A | 折 |
| X4 | 外家 F4 | major | A | 折 |
| X5 | 外家 F5 | major | C | 折 |
| X6 | 外家 F6 | major | D | 折:回退必 bump `_REPLAY_ENGINE_REV` |

放水攻擊第 7 條原報 clean(讀不到報告擋得住),不是發現,不列編號。

### 折入後鏡像核對

便宜代理一席只看本輪改動,報 13 條內部不一致(條款寫側記不進帳、規則沒條款、辯方降級放行沒人回頭看、同步清單漏辯方表態「純記帳」各處、lands_in 不符、旗標去重未定等),全數折入計劃。P3 補法 3「降級後仍留逃逸帳」不採:逃逸帳是事後發現缺陷才記的帳,降級當下不是缺陷;改由 REVISIT 從載體帳列出 evidence 放行逐條回頭核,並計入 RETIRE-IF。
