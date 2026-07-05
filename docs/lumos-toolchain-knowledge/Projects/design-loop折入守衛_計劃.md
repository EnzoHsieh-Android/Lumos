---
type: project
status: doing
created: 2026-07-05
updated: 2026-07-05
tags:
  - type/project
  - status/doing
related:
  - "[[design-loop折入漂移_機械守衛]]"
  - "[[design-loop]]"
summary: |-
  FLAG:DECISION
  KEY:解 design-loop 折入漂移(每輪把 finding 折進 body 後、鏡像段 summary/schema/審計紀錄/天花板忘了同步→下輪審計員耗 finding 抓自傷漂移、污染 G2)。修法=折入強制一致性閘,非 lint 靜態檢查
  KEY:先前 ①§-ref+②summary→body token 方案被否決——逐條對照 impact loop 9 輪真漂移,①命中0(只抓 canary)②≈0(真漂移是反向遺漏/同token改值/跨段矛盾,token-presence 抓不到)
  KEY:真失效=「折完 body 忘了回頭看鏡像段」(忘記看非看不出)→ 機械化重點=強制列舉鏡像段 + 兩個可機械化漂移偵測
  FLOW:折 findings 進 body → 寫審計修正紀錄 → lumos fold-check <真檔 path> → 解每個 flag+逐段勾鏡像段一致 → grep canary=0 → commit
  KEY:fold-check 輸出=①鏡像段列舉(summary block/每個 json fence/審計紀錄/天花板 逐段複查)②value-drift flag(summary 與 body 共關鍵詞、鄰接值不同,命中 2..depth vs 1..depth)③reverse-omission flag(body 顯著 token --flag/★MARKER★/檔名/CamelCase 不在 summary,命中 summary 漏 MultiEdit)
  DECISION:兩交付=lumos fold-check 指令(顧問級,有flag rc1)+ design-loop skill step 7 加強制子步(源在 lumos-toolchain repo user-scope skill)
  DECISION:閘是紀律非防篡改(同 design-loop 本身,lumos 擋不住不跑就 commit);跨段語意矛盾清單逼看不替判;啟發式有假陽假陰
  DEP:[[design-loop]]
  TEST:未實作(設計定稿,待 design-loop → writing-plans)
decisions:
  - content: 折入強制一致性閘(fold-check + skill step7)取代靜態 lint ①§-ref+②token
    context: 初版想給 lumos lint 加 §-ref 解析+summary→body token 檢查
    why_chosen: 逐條對照 impact loop 9 輪真折入漂移:①命中0(只抓 canary)②≈0——真漂移是反向遺漏/同token改值/跨段語意矛盾,token-presence 打不中。改攻工作流:強制列舉鏡像段(逼看,治跨段矛盾)+value-drift(治改值)+reverse-omission(治反向遺漏)
    decided: 2026-07-05
    valid: true
---
# design-loop 折入守衛_計劃

> **狀態**:設計定稿(2026-07-05 brainstorming)。解 [[design-loop折入漂移_機械守衛]] Issue。待 design-loop → writing-plans → 實作。

## 背景:折入漂移是 design-loop 的機制自傷

`lumos-design-loop` 每輪把審計 finding 折進真檔 spec 的 **body**,但鏡像段(frontmatter `summary` block、`--json` schema fence、`## 審計修正紀錄`、`## 誠實天花板`)**無機械綁定要跟著同步** → 下輪乾淨審計員讀到「body 改了、鏡像段沒跟」的內部漂移,把它當 finding。**這些是 loop 機制自傷(~2/輪),污染 G2 枯竭判準、拉長輪次、遮住真收斂**。實證:「主動影響幅度偵測」9 輪 findings 10→7→7→8→6→5→5→8→7 不枯竭,約 ~2/輪是折入漂移。

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
- **(A) `lumos fold-check <node>`**:機械輔助,出「折入後一致性複查清單 + flag」。
- **(B) `lumos-design-loop` skill step 7**:折入後**強制**跑 fold-check、解 flag、逐段勾一致才 commit。

## §2 `lumos fold-check <path>` 演算法

**介面**(r1-F3):吃**檔路徑**(`lumos fold-check <path>`,同 `refcheck` 取 `md_path`),**非 vault 節點名**——因 design-loop 折的真檔在我們慣例是 `Projects/*_計劃.md`(vault 內),但 skill 現文寫 `docs/design/<id>.md`(vault 外);吃 path 兩者都涵蓋。**讀盤**(r1-F6):`Note` 不存 body,fold-check 必 `read_text()` 讀原始 text(同 refcheck),非用已載入 index。

讀 text → 拆 frontmatter/body → 輸出:
1. **鏡像段列舉**:掃 `summary` block、每個 ` ```json ` fence、`## …審計修正紀錄`、`## …誠實天花板` → 各印「☐ 複查 <段>:與 body 一致?」。**標題比對容節號前綴**(r1-F5:regex `^##\s+(§\d+\s+)?(審計修正紀錄|誠實天花板)`,免漏掉「## §4 誠實天花板」這種帶節號的)。**（治 mode 3 跨段矛盾 / 審計紀錄未標翻案 / schema 漂移——強制拉到眼前。）**
2. **value-drift flag**:抽 summary 的「關鍵詞+鄰接值」,對 body 同關鍵詞比鄰接值,不同 → `⚠ value-drift: summary「2..depth」vs body「1..depth」`。**抽取規則**(r1-F2/F7):值 pattern 涵蓋 `\d+\.\.\w+`(配得到「2..depth」——舊 `\d\.\.\d` 配不到,因 depth 是字母)、`\d+min`、`§\d+`、`\bdepth\b`/`\bttl\b` 等關鍵詞的**同行**鄰接數字;比對視窗=**同一行**,關鍵詞用精確 substring。**（命中 mode 2 同 token 改值。）**
3. **reverse-omission flag**:抽 body 顯著 token(`--flag`/`★MARKER★`/`\w+\.\w+` 檔名/CamelCase/backtick code),不在 summary → `⚠ reverse-omission: body 有「MultiEdit」summary 無`。**（命中 mode 1 反向遺漏。）**
4. **rc**:有 flag → rc 1(供 skill 閘判讀)、無 → rc 0;`--json` 可選。本身顧問級(印清單+flag);「強制」在 skill step 7 紀律。

## §3 `lumos-design-loop` skill step 7 改動

skill 源在 **lumos-toolchain repo**(`skills/lumos-design-loop/SKILL.md`、symlink 進 `~/.claude/skills/lumos-design-loop/`)。step 7 現文含:折辯方存活 findings 進真檔 → **寫該輪進審計修正紀錄** → `grep canary=0` → commit。加強制子步,**時序關鍵**(r1-F4:審計修正紀錄本身是鏡像段,fold-check 須在它寫完後跑才掃到本輪真實狀態):
> 折 findings 進真檔 → **寫審計修正紀錄** → **跑 `lumos fold-check <真檔 path>`** → 解掉每個 flag、逐段勾「鏡像段與 body 一致」→ `grep -c '<canary token>' = 0` → commit。

## §4 誠實天花板
1. **跨段語意矛盾(mode 3)**:清單**逼你看**、不能**替你判**——仍需人/Claude 判斷。
2. **啟發式有假陽/假陰**:value-drift 可能誤報巧合共詞;reverse-omission 對非顯著 token(如 `<path>` placeholder)抓不到。
3. **閘是紀律非防篡改**:同 design-loop 本身——lumos 擋不住「不跑 fold-check 就 commit」,靠調用+誠實。fold-check 是**可觀測+摩擦+把鏡像段推到眼前**,不是 oracle。

## §5 測試
- **fold-check 單元**(`scripts/test_lumos.py`):summary「2..depth」+body「1..depth」→ value-drift flag;body「MultiEdit」不在 summary → reverse-omission flag;乾淨節點 → 無 flag、rc 0;鏡像段列舉齊(summary/json fence/審計紀錄/天花板);有 flag → rc 1。
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

## 落地後回指
實作完成 Verification 用 `plan_refs: "[[design-loop折入守衛_計劃]]"` 回指;更新本節點 `TEST:` + `verified_by`;Issue [[design-loop折入漂移_機械守衛]] 轉 status/done。
