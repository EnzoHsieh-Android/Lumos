---
type: system
status: done
created: 2026-06-26
updated: 2026-06-26
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-06-19_canary-audit]]"
summary: |-
  FLOW:對抗審計一份 spec → 在工作副本偷植 1 個純加性 canary(指向不存在章節/引用未定義詞)→ 不告訴審計員、正常跑審 → 判定:審計員清楚描述該瑕疵=抓到(只信同類同段 findings)/沒描述=放水(判決作廢、換 canary 重跑)→ `lumos canary record caught|missed` 記一筆 → `lumos gov` 第 4 源彙整成審計員可靠度史
  KEY:test-the-tester——這套方法論把判斷外包乾淨審計員,canary 是「注意力下限」探針,擋掉『審計員根本沒讀/只吐通用回應』失敗模式
  KEY:協議是主體(skill 規則),lumos 只做極小 helper:record 留痕 + gov 唯讀彙整;lumos 不 spawn agent、植入/判定留在對話/skill 層
  KEY:提交的文件永遠不含 canary;token(CANARY-<hex>)只是定位記號,非「抓到」的機械證明——唯一算數的是審計員正確描述了那個瑕疵
  KEY:auto-mint token 用 secrets.token_hex(非時間戳:秒解析度同秒會撞被 dedup 誤折);每筆 token 唯一供 gov dedup 第 5 鑑別子
  KEY:gov dedup key 第 5 子用 r.get("token","")(不可 r["token"]——舊三源無此鍵會 KeyError 弄爆 gov);只 canary mapper 輸出 token 鍵
  DEP:scripts/lumos cmd_canary｜cmd_gov(.canary-log.jsonl 第 4 源)｜env.vault.parent 定位寫入｜skills/lumos-project-notes(canary 協議)
  TEST:t_canary｜t_canary_loop_fields(258 passed)
  VERIFY:[[Verification/2026-06-19_canary-audit]]
decisions:
  - content: token 不是「抓到」的機械證明,只當定位記號;唯一算數的是審計員清楚且正確地描述了那個植入瑕疵
    context: design-loop r1 canary 審計揪出的真 blocker(R1-F2):若以 token 字串出現在輸出裡當「抓到」,審計員可能只順手提到 token 卻沒真懂瑕疵,假乾淨
    why_chosen: 整套機制的價值是探測「審計員有沒有醒著讀」;機械字串比對能被表面提及騙過,只有正確描述才證明真的讀懂了那段
    decided: 2026-06-19
    valid: true
  - content: v1 canary 只收純加性(additive)瑕疵——指向不存在章節的交叉引用、或約束引用未定義詞;禁「與另一節矛盾的需求」這類非局部型
    context: design-loop r1(R1-F3):非局部 canary 會牽動被矛盾的那節、污染審計員對該節的真實 findings,移除 canary 也救不回
    why_chosen: canary 要能乾淨植入再移除、不汙染真實 findings;純加性瑕疵只動自己那一處,移除後其餘審計結果仍可信
    decided: 2026-06-19
    valid: true
  - content: gov dedup 第 5 鑑別子用 r.get("token","") 而非 r["token"];既有三源 mapper 不加 token 鍵,只 canary mapper 輸出 token
    context: design-loop r3 唯一 must-fix(R3-Issue1):既有三條 mapper 的舊事件 row 沒有 token 鍵,r["token"] 會對所有舊事件 KeyError 弄爆 lumos gov;且 canary 每筆 token 唯一,不加鑑別子會被 dedup 折成單列(R1-F4)
    why_chosen: .get 對舊事件回 "" 行為不變、crash-free;canary token 唯一當第 5 鑑別子才不會把多筆 missed 折成一列丟失可靠度史
    decided: 2026-06-19
    valid: true
---
# canary-audit

`lumos canary` + gov 第 4 源 + skill 協議 —— 給「對抗設計/spec 審計 loop」的 **test-the-tester**:每輪偷植一個已知瑕疵(canary)驗審計員有沒有在認真抓,放水的審計員判決作廢重跑。

源起:日報 2026-06-18 Gap 1「內迴圈派 Sonnet 當審計員,卻從沒檢查它這一輪到底有沒有在認真抓」+ Codex `/goal` 共識「你判斷『做完沒』的那套檢查必須比迴圈本身更可靠」。

## 解決什麼
這套方法論把判斷外包給乾淨審計員(spec/設計的對抗審計 loop)。一個放水審計員回報的「沒問題/看起來不錯」是最危險的假乾淨——自主迴圈只會更快更自信地犯錯。canary 把「審計員審得好不好」這個難自查的問題,換成「植入者判得準不準」這個較難自欺的問題。

## 範圍(v1)
- **只做對抗設計/spec 審計**:被審的是你控制的文件,能乾淨地植入瑕疵再移除。
- **不做圖譜自足性審計**(§795/§831):審計員讀真實圖譜,植 canary 會污染圖譜 → 延後。
- 形式 = skill 協議規則(主體)+ 極小 lumos helper(只記 log + 餵 gov);**lumos 不 spawn agent**,植入/判定留在對話/skill 層。

## 協議(寫進 skill 的規則,5 步)
1. 在工作副本植 1 個**純加性** canary,給唯一 token。**提交的文件永遠不含 canary。**
2. 正常跑審計,**不告訴審計員有 canary**(告訴就作弊)。
3. 判定:審計員**清楚且正確描述**該瑕疵=抓到(這輪是醒的,只信同類同段真實 findings)/ 沒描述=放水(判決作廢、換不同 canary 重跑,`record missed`)。
4. 連 2 次 missed 升級:換更強模型 / 把文件切小;升級前先 `lumos gov --since 7` 看 missed 史。
5. panel 變體:N 個審計員各給自己的 canary,漏抓自己的那個從投票剔除。

**校準鐵則**:canary 要「認真審計員一定抓得到、但不一眼看穿」,對齊你真正在意的瑕疵類型。

## 天花板(誠實合約)
抓到 canary 只證明審計員**醒到足以抓那一個、那一類、那一段**的植入瑕疵,**不證明抓到所有真實瑕疵**。canary 抓得到的失敗模式 = 「審計員根本沒讀 / 只吐通用回應」;**抓不到**的 = 「讀了、但對複雜權衡判斷錯」——後者 canary 無能為力,別在密集 spec 上因 canary pass 就過度信任。迴歸沒閉合:判定者=植入者本人,無外部檢查,canary 是**降低放水機率的摩擦**,非閉合驗證迴路。

## Helper(`scripts/lumos`)
- `lumos canary record caught|missed [--auditor M] [--token T] [--note ...]` → append 一筆到 `<vault.parent>/.canary-log.jsonl`(`cmd_canary`,用 `env.vault.parent` 定位、不額外載圖)。
- argparse:`canary`(頂層)→ `dest="ccmd"` → `record` 子 parser → `kind` positional `choices=("caught","missed")`(非法值 argparse 自動 rc2)。
- `--token` 沒給則自動鑄 `CANARY-<secrets.token_hex(4)>`(隨機、非時間戳;見 decisions)。schema:`{ts,kind,auditor,token,note}`。
- `lumos gov` 把 `.canary-log.jsonl` 當**第 4 源**讀,明確 mapper(`gate:"canary"`),dedup key 加第 5 鑑別子 `r.get("token","")`(見 decisions)。canary 寫自己的 log,不碰 doctor 的 `.governance-log.jsonl`。

## 後續延伸(非本設計稿)
程式現況含 `--loop` / `--severity` 欄位與 `lumos loop status`(收斂留痕,2026-06-19 另一設計、commit `7858ce7`):把每輪記成帶 loop 的 canary,`lumos loop status <slug> --need 2` 算「連 K 輪 caught 且 severity∈{clean,minor}」→ exit 0 綠燈進實作。本節點聚焦 canary-audit 本體;收斂留痕細節見其專屬節點/設計稿。

## v1 明確不做
圖譜自足性 canary｜自動注入/判定工具｜`lumos canary` 擋任何東西(record-only)｜`lumos canary new`(已砍,record 自動補 token)｜非局部 canary 類型。

## 相關
- 設計稿:`docs/design/2026-06-19-canary-audit.md`(4 輪 Sonnet 對抗審計收斂)。
- 實作落點:`scripts/lumos` `cmd_canary` + `cmd_gov` 第 4 源 mapper;`skills/lumos-project-notes/SKILL.md` canary 協議段。
- 實作 commit:`58ae539`(canary record + gov 第 4 源)。
