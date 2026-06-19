# 設計:收斂留痕(Convergence Recording)— loop-engineering 設計管線的 Component A

- 日期:2026-06-19
- 狀態:設計草案(待 canary-護的 Sonnet 審計 loop 收斂)
- 方向:lumos 治理朝 loop engineering(見 memory `lumos-governance-direction-loop-engineering`)
- 角色:**Component A**(lumos 機械層)。Component B(編排 skill,讓每個計畫自動進 loop)另立子專案,消費 A。

## 0. 動機

審計 loop 現在的終止(「審穩了沒」)是**人在判**。要讓 loop 能**自我終止、無人看顧**,終止判準必須是**機械、可記錄、可查詢**的——不是 agent 說了算。收斂留痕 = 把每一輪審計記下來 + 由 lumos 從紀錄算出收斂。B skill 只要問 `lumos loop status` 就知道該不該停。

## 1. 範圍(v1)

- **只做 Component A**:lumos 的機械原語(記錄 + 計算收斂)。編排 skill(B)另立。
- 對象 = 設計/spec 的對抗審計 loop(我們在跑的那種)。
- 不做:lumos spawn agent(編排在 skill 層);B skill;離散 gov 源(複用 canary-log)。

## 2. 資料模型:一「審計輪」= canary 記錄 + 2 個欄位

複用既有 `.canary-log.jsonl`(不新增 log)。`lumos canary record`(既有)加**兩個選用欄位**:
```
lumos canary record caught|missed --loop <id> --severity clean|minor|major|blocker [--auditor] [--note]
```
- `--loop <id>`:把這輪歸到某個設計 loop(slug,如 `convergence-recording`)。
- `--severity`:這輪審計員找到的**最嚴重** finding(`clean`=無 / `minor` / `major` / `blocker`)。**語義(R1-BLOCKER-2):這是「忠實轉錄審計員自己標的最嚴重 finding」,不是編排者的獨立意見**——審計員本來就逐條標 blocker/major/minor,這裡記它的 max。整合性假設見 §4。
- 不帶 `--loop`/`--severity` → 一般 ad-hoc canary 記錄(行為同現在)。
- 寫入 schema 加兩鍵:`{…既有…, "loop", "severity"}`(選用)。
- **`--loop` 有給但 `--severity` 沒給(或為 "")→ `loop status` 一律當「未收斂」**(R1-MAJOR-3:逼明確宣告,不得把缺值當 clean)。

## 3. 收斂計算(lumos 機械算,唯讀)
```
lumos loop status <id> [--need K]   # K 預設 2
```
讀 `.canary-log.jsonl`、篩 `loop==id`。**一筆 `--loop` 記錄 = 一輪**;**排序用檔案 append 順序**(不是 `ts` 排序——`ts` 只到秒,同秒兩輪會並列;append 順序唯一且即時間序,R1-MAJOR-2)。判定:
- **CONVERGED ⟺ 最後 K 輪(sliding tail-K:篩出該 loop 的記錄、保留 append 序、取最後 K 筆)全是「`kind==caught` 且 `severity∈{clean,minor}`」**(canary 抓到=審計員醒著;無 blocker/major;**缺 severity 視同未收斂**,R1-MAJOR-3)。R2-MAJOR-1:是 **tail-K 滑動窗**——前面有髒輪不影響,只看最後 K 筆;不是「每一輪都得乾淨」。
- 否則「⏳ 還需 N 輪乾淨」,**N = need −(tail 從最後一筆往回數、連續合格的輪數)**(R3-MINOR:有髒輪時 N 不會虛低;最後一輪就髒 → N=need)。
- 該 loop 記錄數 < K → 未收斂(exit 1)。
- `--need` 防呆:**`need = max(1, need)`**(R3:不引入未定義常數;< 1 直接夾到 1)。
- **篩選規則(R2-BLOCKER-2)**:`rec.get("loop") == loop_id`(嚴格等值;舊 ad-hoc 記錄無 `loop` 鍵 → `None != id` 自然排除)。`loop_id` CLI 入口保證非空。
- **輸出**:第一行 status,接著每輪一行 tab 分隔(`順位\tkind\tseverity\tts\tnote`;順位 = 該 loop 篩出後 append 序的 1-indexed 位置;無 note 給空字串)當留痕,讓 B skill 不必 screen-scrape。
- **exit code(給 B skill 機器讀)**:`0`=CONVERGED、`1`=未收斂(**含「該 id 還沒有任何記錄」= 還沒開始審,R2-MAJOR-2**)、`2`=**真錯誤**(參數錯 / 檔讀不到)。「沒記錄」和「I/O 錯」分開,讓 B 能分辨「該起一輪」vs「基礎設施壞了」。

## 4. 為什麼這形狀(以及「機械」到什麼程度,R1-BLOCKER-2 誠實校正)
- 「留痕」= 那一串 round 記錄本身(怎麼一輪輪收斂的);`gov` 看得到這些 canary 事件。**這塊是純收益、與整合性無關**——本來人眼判收斂不留痕、無法事後查;現在每輪 caught+severity 都記下、收斂條件可被任何人**重查**(R2:用「重查」不用「重算」——公式可重算,但 append-only 無簽章的輸入仍可被偽造,見 §5 整合性)。
- `loop status` 是**對「忠實記下的審計員判決」做機械計算**——它把「人含糊地說『看起來收斂了』」換成「連 K 輪 caught+乾淨 這個可被重算的條件」。**但它不比輸入更可信**:`severity` 是編排者轉錄審計員的最嚴重 finding,沒有寫入端驗證。一個想早點收工的編排者可以記假的 `clean`。
- **整合性假設(明說)**:本機制成立的前提是「編排者忠實轉錄審計員的判決」。這跟 canary「植入者忠實判定有沒有抓到」是**同一個沒閉合的迴歸**——它把問題從「審計員審得好不好」往上換成「編排者記得準不準」,後者較難自欺、但**不是 tamper-proof**。
- 為什麼還是有意義:converged 一輪 = **canary 抓到(審計員醒著)** + 那個醒著的審計員**自己標的最嚴重 finding 是 clean/minor**。兩個訊號疊起來,比「人眼掃一下說 OK」強得多、且可查。

## 5. 誠實天花板(兩層,都別過度信任)
1. **完整性**:收斂只證明「連 K 輪醒著的審計員沒找到 blocker/major」,**不證明沒有更深的問題**。完整性靠多輪 + 多視角的 loop 本身,不靠把門檻調嚴。
2. **整合性**(見 §4):`severity` 自報、無寫入端驗證 → `loop status` 的 CONVERGED 是「**忠實記錄下、可重算的綠燈**」,不是「防竄改的正確性證明」。

→ 定位:這是**可觀測性 + 摩擦 + 一個地板**,不是 oracle。對「無人看顧的自動 loop」夠用(把終止從不可查的人判,變成可查的條件);對「有人想刻意作弊」不設防(那不是它的目標)。

## 6. 範圍 / YAGNI(v1 不做)
- ❌ 新增獨立 `.loop-log.jsonl` / gov 第 5 源(複用 canary-log)。
- ❌ 離散「converged」寫入事件(收斂任何時候可從紀錄算出;rounds 本身就是留痕)。
- ❌ Component B(編排 skill)——另立子專案。
- ❌ lumos spawn agent。

## 7. 受影響(含明確 argparse/dispatch,R1-BLOCKER-1)
- `scripts/lumos`:
  - `canary record` 加 `--loop`/`--severity`(`choices=("clean","minor","major","blocker")`)兩選用 arg。**完整 threading(R3-BLOCKER)**:`cmd_canary(env, kind, auditor=None, token=None, note=None, loop=None, severity=None)`;dispatch 改 `cmd_canary(env, args.kind, args.auditor, args.token, args.note, args.loop, args.severity)`;寫入 rec 時 `if loop: rec["loop"]=loop` / `if severity: rec["severity"]=severity`(沒給就不寫鍵——別只在 argparse 加 arg 卻漏接到 function/寫入)。
  - 新增 `loop` 頂層 subparser → `lsub = loop.add_subparsers(dest="lcmd", required=True)` → `st = lsub.add_parser("status")` → `st.add_argument("loop_id")`(**`dest="loop_id"`,不用 `id` 免遮蔽內建**,R2-BLOCKER-1)+ `st.add_argument("--need", type=int, default=2)`。
  - dispatch:`if args.cmd == "loop":` → `if args.lcmd == "status": return cmd_loop_status(env, args.loop_id, args.need)`(別重蹈現有 `canary` dispatch 沒讀 `ccmd` 的覆轍)。
  - `cmd_loop_status(env, loop_id, need=2)`(**簽名給 need 預設,防直接呼叫漏傳**,R2-MINOR-3):讀 canary-log(append 序、**不要 ts-sort**——R2:`cmd_gov` 有 ts-sort 別照抄)、篩 loop、tail-K 算收斂、印 status+輪歷史、回 0/1/2。
- `cmd_gov`:canary mapper 的 `detail` **必須**附 loop/severity(R1-MAJOR-1,必做),且**放最前**(R2-MAJOR-3,避 `[:50]` 截斷)。**確切 lambda(R3-MAJOR,含舊 ad-hoc 無此鍵的條件處理)**:
  ```python
  load(".canary-log.jsonl", lambda d: {..., "detail": (
      (f"loop={d['loop']} sev={d.get('severity','?')} · " if d.get("loop") else "")
      + (d.get("auditor","") + " " + d.get("note","")).strip())})
  ```
  舊記錄無 `loop` → 前綴空、行為同現在。
- `skills/lumos-project-notes/SKILL.md`:canary 協議那節補「記 round(帶 --loop/--severity)+ `loop status` 看收斂」。
- `scripts/test_lumos.py`:測試。

## 8. 驗收標準
- `canary record caught --loop L --severity major` → canary-log 該筆含 `loop`/`severity`。
- `loop status L`(CLI 路徑,非只測內部函式,R1-BLOCKER-1):連 2 輪 caught+clean(或 minor)→ 印 `CONVERGED` 且 **exit 0**;最後 2 輪有一輪 missed/major/blocker → 印「還需」且 **exit 1**。
- 該 loop 記錄數 < 2 → exit 1;**該 id 無記錄 → exit 1**(還沒開始,非錯誤,R2-MAJOR-2)。
- **sliding tail-K(R2-MAJOR-1)**:3 輪 = [major, caught+clean, caught+clean] → **CONVERGED**(前面髒輪不算);3 輪 = [clean, clean, major] → 未收斂(最後一輪髒)。
- `--loop L` 但**缺 `--severity`** 的輪 → 視同未收斂(exit 1),不得當 clean(R1-MAJOR-3)。
- `gov` 顯示帶 loop/severity 的 canary 列時,detail **開頭**含 `loop=`/`sev=`(R2-MAJOR-3,即使 auditor/note 長也不被 `[:50]` 截掉)。
- 測試函式:`t_loop_status`(新,測 loop status CLI/exit code/tail-K)+ `t_canary` 擴充(測帶 --loop/--severity 的 record 與 gov detail)。
- 既有測試全綠(回歸)。

## 審計修正紀錄
### 第一輪(canary-護的 Sonnet 對抗審計;canary=`pinned:true`,**抓到**)
- R1-BLOCKER-1:寫明 `loop` argparse + dispatch + CLI 驗收測試(別重蹈 `ccmd` 沒讀的覆轍)→ §7/§8。
- R1-BLOCKER-2(深):`severity` 自報、無寫入端驗證 → 「機械自我終止」是過度宣稱。誠實校正:severity=忠實轉錄審計員 max finding;明說整合性假設(同 canary 沒閉合的迴歸);定位為可觀測性+地板、非 tamper-proof oracle → §2/§4/§5。
- R1-MAJOR-1:gov mapper 附 loop/severity 改必做 → §7/§8。
- R1-MAJOR-2:排序用檔案 append 序(非 ts 秒級,同秒會並列);定義「一筆=一輪」→ §3。
- R1-MAJOR-3:`--loop` 缺 `--severity` 視同未收斂 → §2/§3/§8。
- R1-MINOR-1:`loop status` 輸出格式 + exit code(0/1/2)寫明 → §3/§8。
- canary 驗證:審計員精準點名植入的 `pinned:true`(列為「Deliberately Out-of-Place Defect」+ MAJOR-4)→ **這輪審計員醒著**;但 severity=blocker → 本輪不計入收斂。

### 第二輪(canary-護;canary=指向不存在的 §9,**抓到**)
- R2-BLOCKER-1:`loop status` positional 用 `dest="loop_id"`(不用 `id` 遮蔽內建)→ §7。
- R2-BLOCKER-2:篩選明訂 `rec.get("loop") == loop_id` 嚴格等值 → §3。
- R2-MAJOR-1(真 major):「最後 K 輪」明訂為 **tail-K 滑動窗**(非「每輪都得乾淨」)+ 加 3 輪驗收測試 → §3/§8。
- R2-MAJOR-2:「無記錄」改 exit 1(還沒開始)、exit 2 只留真錯誤 → §3/§8。
- R2-MAJOR-3:gov detail 的 loop/severity 放最前(避 `[:50]` 截斷)→ §7/§8。
- R2-MINOR:`cmd_loop_status` 別照抄 cmd_gov 的 ts-sort、need 簽名給預設、「重算」改「重查」→ §3/§4/§7。
- canary 驗證:審計員抓到 §9 dead-ref(列 MINOR-1 + 「structurally suspicious / signature of a forgotten plant」)→ **醒著**;severity=major → 本輪仍不計入收斂。R1 整合性 reframe 經確認無殘留 overclaim。

### 第三輪(canary-護;canary=未定義常數 `LOOP_DEFAULT_K`,**抓到**)
- 前兩輪修正**全部經 code 驗證 hold**。
- R3-BLOCKER(真,silent-bug 風險):`cmd_canary` 的 loop/severity 完整 threading(argparse→dispatch→function 簽名→寫入)寫明確切簽名 → §7。
- R3-MAJOR:gov mapper 的 detail lambda 寫出確切版(含舊記錄無 loop 鍵的條件)→ §7。
- R3-MINOR:`LOOP_DEFAULT_K` 改 `need = max(1, need)`(不引未定義常數)、「還需 N」的 N 公式寫明 → §3。
- canary 驗證:審計員精準點名 `LOOP_DEFAULT_K`(「Likely the round-3 plant... structurally out-of-place」)→ **醒著**;severity=major → 本輪不計入收斂。連 3 輪 caught(canary 機制穩定);severity blocker→major→major,逼出的 gap 一輪比一輪細。
