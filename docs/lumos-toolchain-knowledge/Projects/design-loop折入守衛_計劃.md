---
type: project
status: done
created: 2026-07-05
updated: 2026-07-05
tags:
  - type/project
  - status/done
related:
  - "[[design-loop折入漂移_機械守衛]]"
  - "[[design-loop]]"
summary: |-
  FLAG:DECISION
  KEY:解 design-loop 折入漂移(每輪把 finding 折進 body 後、鏡像段 summary/schema/審計紀錄/天花板忘了同步→下輪審計員耗 finding 抓自傷漂移、污染 G2)。修法=折入強制一致性閘,非 lint 靜態檢查
  KEY:先前 ①§-ref+②summary→body token 方案被否決——逐條對照 impact loop 9 輪真漂移,①命中0(只抓 canary)②≈0(真漂移是反向遺漏/同token改值/跨段矛盾,token-presence 抓不到)
  KEY:真失效=「折完 body 忘了回頭看鏡像段」(忘記看非看不出)→ 機械化重點=強制列舉鏡像段 + 兩個可機械化漂移偵測
  FLOW:折 findings 進 body → 寫審計修正紀錄 → lumos fold-check <真檔 path> → 解每個 flag+逐段勾鏡像段一致 → grep canary=0 → commit
  KEY:fold-check 輸出=①鏡像段列舉(summary block/每個 json fence/審計紀錄/天花板 逐段複查)②value-drift flag(全文域同識別詞不同值,命中 2..depth vs 1..depth、fold-check <node> vs <path>)③reverse-omission flag(全文高訊號 token --flag/★MARKER★/帶副檔名檔名 某段缺,排除 <…> placeholder+FENCE+審計段,命中 summary 漏 --json;T5 降噪移除 CamelCase/backtick 散文 token 237→24)
  DECISION:兩交付=lumos fold-check 指令(顧問級,有flag rc1)+ design-loop skill step 7 加強制子步(源在 lumos-toolchain repo user-scope skill)
  DECISION:閘是紀律非防篡改(同 design-loop 本身,lumos 擋不住不跑就 commit);跨段語意矛盾清單逼看不替判;啟發式有假陽假陰
  DEP:[[design-loop]]
  TEST:已實作(branch feat/fold-check,528 passed;2 design-loop 輪+TDD 5 task+opus 終審);VERIFY:[[2026-07-05_design-loop折入守衛]]
decisions:
  - content: 折入強制一致性閘(fold-check + skill step7)取代靜態 lint ①§-ref+②token
    id: d1
    context: 初版想給 lumos lint 加 §-ref 解析+summary→body token 檢查
    why_chosen: 逐條對照 impact loop 9 輪真折入漂移:①命中0(只抓 canary)②≈0——真漂移是反向遺漏/同token改值/跨段語意矛盾,token-presence 打不中。改攻工作流:強制列舉鏡像段(逼看,治跨段矛盾)+value-drift(治改值)+reverse-omission(治反向遺漏)
    decided: 2026-07-05
    valid: true
verified_by:
  - "[[2026-07-05_design-loop折入守衛]]"
---
# design-loop 折入守衛_計劃

> **狀態**:設計定稿(2026-07-05 brainstorming)。解 [[design-loop折入漂移_機械守衛]] Issue。待 design-loop → writing-plans → 實作。

## 背景:折入漂移是 design-loop 的機制自傷

`lumos-design-loop` 每輪把審計 finding 折進真檔 spec 的 **body**,但鏡像段(frontmatter `summary` block、body 內每個 ` ```json ` fence、`## 審計修正紀錄`、`## 誠實天花板`,以及跨 body 段的重複描述)**無機械綁定要跟著同步** → 下輪乾淨審計員讀到「body 改了、鏡像段沒跟」的內部漂移,把它當 finding。**這些是 loop 機制自傷(~2/輪),污染 G2 枯竭判準、拉長輪次、遮住真收斂**。實證:「主動影響幅度偵測」9 輪 findings 10→7→7→8→6→5→5→8→7 不枯竭,約 ~2/輪是折入漂移。

## 被否決的路:①§-ref + ②summary→body token 靜態 lint

初版想給 `lumos lint` 加靜態文件內檢查。**逐條對照 impact loop 9 輪的真折入漂移後否決**:

| 真漂移 | ①§-ref | ②token |
|---|---|---|
| 2..depth vs 1..depth(同 token 改值) | ✗ | ✗(兩邊都含 depth) |
| summary 漏 MultiEdit(反向遺漏) | ✗ | ✗(②只查 summary→body) |
| 見§1 但§1沒提 core_refs(內容不符,§1標題存在) | ✗(只驗標題存在) | ✗ |
| 跨段語意矛盾 / 審計紀錄未標翻案 / schema 範例漂移 | ✗ | ✗ |

① 對真漂移命中 **0**(只抓 design-loop 每輪往工作副本植入的 canary——那批壞 §-ref 用不存在的節號如 §6/§7/§8;那是校準用注入、非真漂移);② ≈ **0**。真漂移是**反向遺漏、同 token 改值、跨段語意矛盾**三型,token-presence 靜態檢查打不中要害。故改攻工作流。

## §1 架構:折入強制一致性閘(工作流 + 機械輔助)

真失效=「折完 body 忘了回頭看鏡像段」——是**忘記看**,不是**看不出來**。機械化重點:**強制列舉鏡像段**(逼看)+ **兩個可機械化的漂移偵測**。兩交付:
- **(A) `lumos fold-check <path>`**:機械輔助,出「折入後一致性複查清單 + flag」。value-drift/reverse-omission **全文域跑**(不只 summary↔body)——r2-F1 實證:`<node>`(§1)vs`<path>`(§2)是 **body 段↔body 段** 漂移,只查 summary↔body 抓不到。
- **(B) `lumos-design-loop` skill step 7**:折入後**強制**跑 fold-check、解 flag、逐段勾一致才 commit。

## §2 `lumos fold-check <path>` 演算法

**介面**(r1-F3):吃**檔路徑**(`lumos fold-check <path>`,同 `refcheck` 取 `md_path`),**非 vault 節點名**——因 design-loop 折的真檔在我們慣例是 `Projects/*_計劃.md`(vault 內),但 skill 現文寫 `docs/design/<id>.md`(vault 外);吃 path 兩者都涵蓋。**讀盤**(r1-F6):`Note` 不存 body,fold-check 必 `read_text()` 讀原始 text(同 refcheck),非用已載入 index。

讀 text → 拆 frontmatter/body → 輸出(⚠ **value-drift/reverse-omission 掃描域排除 `## …審計修正紀錄` 段**——該段刻意引用歷史/被翻案的舊值如「fold-check `<node>`」,掃它必假陽;審計紀錄仍列入①鏡像段供人複查、但不進②③自動掃):
1. **鏡像段列舉**:掃 `summary` block、每個 ` ```json ` fence、`## …審計修正紀錄`、`## …誠實天花板` → 各印「☐ 複查 <段>:與 body 一致?」。**標題比對容節號前綴**(r1-F5:regex `^##\s+(§\d+\s+)?(審計修正紀錄|誠實天花板)`,免漏掉「## §4 誠實天花板」這種帶節號的)。**（治 mode 3 跨段矛盾 / 審計紀錄未標翻案 / schema 漂移——強制拉到眼前。）**
2. **value-drift flag**(全文域):抽全文的「pattern-value」——**單一抽取法**(r2-F7:不混兩法),**只保留兩個低假陽 pattern**(實作 T2-C1 修正:原列的 `§\d+`/`\d+min` 移除——§1/§2/§3 是不同章節、5min/10min 是不同合法值,非「同識別詞不同值」,必然假陽):① `\d+\.\.\w+`(range 記號,key=後綴詞如「2..depth」的 `depth`、value=前導數字;舊 `\d\.\.\d` 配不到因 depth 是字母)② `fold-check \S+`(泛化「指令+值」,key=`fold-check`、value=其後 token)。**同一識別詞在不同處出現不同值 → flag**(r2-F1:`fold-check <node>` §1 vs `<path>` §2 → flag)。`⚠ value-drift: 「fold-check <node>」vs 「fold-check <path>」`。**（命中 mode 2 同 token 改值 + body↔body 漂移。）**
3. **reverse-omission flag**(全文域):抽全文**高訊號 token 三類**(實作 T5 降噪:原含 backtick-code/CamelCase 對長技術 spec 爆量假陽 237 條→收窄後 24 條全真):① `--flag`(`--\w[\w-]*`)② `★MARKER★`(★…★)③ **帶已知副檔名的檔名**(`\w[\w./-]*\.(json|py|md|sh|txt|kt|cs|vue|js|ts|yml|yaml)`,避純版本號噪音)。**排除 `<…>` placeholder**(r2-F5)、FENCE 內容(T4-Critical:先 `FENCE_RE.sub` 剝三重 backtick,對稱 `_refcheck_scan`)、審計紀錄段。summary 缺 body 有的 → flag。`⚠ reverse-omission: body 有「--json」summary 無`。**（命中 mode 1 反向遺漏;代價=失去 CamelCase/backtick 散文 token 的 recall,由 mirror-section 列舉+value-drift 兜底。）**
4. **rc + 閘語意**(r2-F6:**閘是紀律非機械 abort**):有 flag → rc 1、無 → rc 0——rc 是**給操作者(Claude)的訊號**,不是 script 硬 abort;step 7 由 Claude 讀 flag+逐段勾後才 commit(同 design-loop 整體「lumos 出訊號、Claude 據紀律行動」)。`--json` 輸出供機器讀,schema:
```json
{"path":"...","mirror_sections":["summary","## §4 誠實天花板","## §N 審計修正紀錄"],
 "value_drift":[{"key":"fold-check","a":"<node>@§1","b":"<path>@§2"}],
 "reverse_omission":[{"token":"backtick code","present_in":"§2","missing_in":"summary"}]}
```

## §3 `lumos-design-loop` skill step 7 改動

skill 源在 **lumos-toolchain repo**(`skills/lumos-design-loop/SKILL.md`、symlink 進 `~/.claude/skills/lumos-design-loop/`)。step 7 現文:折辯方存活 findings 進真檔(**折時**把該輪寫進審計修正紀錄,是 fold 的 inline 附帶動作,r2-F9)→ `grep canary=0` → commit。加強制子步,**時序關鍵**(r1-F4:審計修正紀錄本身是鏡像段,fold-check 須在它寫完後跑才掃到本輪真實狀態):
> 折 findings 進真檔 → **寫審計修正紀錄** → **跑 `lumos fold-check <真檔 path>`** → 解掉每個 flag、逐段勾「鏡像段與 body 一致」→ `grep -c '<canary token>' = 0` → commit。

## §4 誠實天花板
1. **跨段語意矛盾(mode 3)**:清單**逼你看**、不能**替你判**——仍需人/Claude 判斷。
2. **啟發式有假陽/假陰**:value-drift 可能誤報巧合共識別詞;reverse-omission **刻意排除 `<…>` placeholder**(r2-F5:`<path>` 這種佔位符非識別字,不 flag),故 placeholder 層級的漂移抓不到(它靠鏡像段列舉逼看兜)。
3. **閘是紀律非防篡改**:同 design-loop 本身——lumos 擋不住「不跑 fold-check 就 commit」,靠調用+誠實。fold-check 是**可觀測+摩擦+把鏡像段推到眼前**,不是 oracle。

## §5 測試
- **fold-check 單元**(`scripts/test_lumos.py`):summary「2..depth」+body「1..depth」→ value-drift;**全文域**——§1「fold-check <node>」+§2「fold-check <path>」(同識別詞不同值,body↔body)→ value-drift(r2-F1);body「--bar」不在 summary → reverse-omission(高訊號 token;CamelCase/backtick 已降噪移除,T5);**`<path>` placeholder 不 flag**(r2-F5);乾淨節點 → 無 flag、rc 0;有 flag → rc 1;鏡像段列舉齊(summary/json fence/審計紀錄/天花板,標題容節號 r1-F5);`--json` 輸出符 §2 schema(path/mirror_sections/value_drift/reverse_omission)。
- **回歸**:對現有 `主動影響幅度偵測_計劃`(已多次固化)跑 fold-check → 應乾淨或只剩已知可接受 flag,證不誤傷。

## 審計修正紀錄(lumos-design-loop)

**r1**(canary type=a caught;存活嚴重度 major;auditor sonnet;7 真 finding 折入;**dogfood:手動套 fold-check 方法論**):
- **F2 major**:value-drift regex `\d\.\.\d` 配不到「2..depth」(depth 是字母)。→ 改 `\d+\.\.\w+`。
- **F3 major**:`fold-check <node>` 只搜 vault,但 skill 折的是 `docs/design/<id>.md` 檔。→ 改吃 `<path>`(同 refcheck)。
- **F4 major**:審計修正紀錄本身是鏡像段 → fold-check 須在**寫紀錄後**跑。→ §3 時序改「寫紀錄→fold-check→grep→commit」。
- **F5 major**:鏡像段標題精確比對「## 誠實天花板」漏掉自己的「## §4 誠實天花板」。→ regex 容節號前綴。
- **F6 minor**:「純記憶體」誤導(Note 不存 body)。→ 改「讀盤」。
- **F7 minor**:value-drift 鄰接視窗/關鍵詞比對未定。→ 定同行+精確 substring。
- **F8 minor**:canary §6/§7/§8 語境不明。→ 註明是每輪植入的校準 canary。

**r2**(canary type=b caught;存活嚴重度 blocker;auditor sonnet;8 真 finding 折入;**dogfood 金礦**):
- **F1 blocker**:§1 殘留 `fold-check <node>`(r1-F3 只改 §2)——**「講折入漂移」的 spec 自己犯折入漂移,且我手動 fold-check dogfood 也漏**。→ 修 §1 + **暴露設計 gap:value-drift/reverse-omission 改全文域**(body↔body,原只 summary↔body 抓不到)。**鐵證:機械 fold-check 是剛需,手動不夠。**
- **F3 major**:`--json` schema 未定。→ §2 補 schema。
- **F4 major**:summary KEY 漏 `backtick code`(§2 有)。→ 同步。
- **F5 major**:§4 天花板「<path> 抓不到」vs §2「backtick code 會抓」矛盾。→ reverse-omission 明確排除 `<…>` placeholder。
- **F6 major**:「rc 供閘判讀」vs「顧問級」vs step7 散文 閘語意衝突。→ 定「閘是紀律、rc 是給 Claude 的訊號非機械 abort」。
- **F7 minor**:value-drift 混兩抽取法。→ 定單一 pattern-value 法。
- **F8 minor**:「--json schema fence」vs「每個 json fence」術語。→ 統一。
- **F9 minor**:§3 step7 現文順序描述不準(寫紀錄是 fold inline)。→ 更正。

## 收斂狀態(2 輪 → 轉 TDD)

canary 2/2 全抓。findings [7,8]。**r2 是 dogfood 金礦**:這份「講折入漂移」的 spec 自己犯了兩條折入漂移(§1 殘留 `<node>`、summary 漏 backtick code),**且我手動 fold-check 也漏抓**——鐵證 (i) 折入漂移隱蔽到手動壓不住、(ii) 機械 fold-check 是剛需、(iii) 漂移不只 summary↔body 還有 body↔body(設計據此改全文域)。**遞迴洞察**:此 spec 的真收斂器正是它要造的 fold-check——沒工具只能手動(已證不足),工具 TDD 建好後回頭能抓 r1-F1/r2-F1/F4、並加速未來所有 loop(含自身)。故同 impact:**設計良好、dogfood 證必要 → 轉 writing-plans+TDD**,剩餘精度交真測。使用者顯式選 TDD 路(2026-07-05)。**誠實天花板**:自指 meta-spec(含 drift 範例)會讓 value-drift 假陽(範例「<node> vs <path>」),靠 audit-record 排除 + 操作者判 warning。

## 落地後回指
實作完成 Verification 用 `plan_refs: "[[design-loop折入守衛_計劃]]"` 回指;更新本節點 `TEST:` + `verified_by`;Issue [[design-loop折入漂移_機械守衛]] 轉 status/done。
