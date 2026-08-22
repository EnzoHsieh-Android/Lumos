---
type: project
status: superseded
created: 2026-08-21
updated: 2026-08-21
tags:
  - type/project
  - status/superseded
related:
  - "[[Projects/工具鏈全環節體檢_調研]]"
---
# lumos操作卡_草案

> 白話:這是要取代 CLAUDE.md 紀律區塊與各 SKILL.md 頭版的「一張卡」——Claude 每個 session 真正要守的全部。設計原則:**每條規則旁邊寫誰會提醒我、誰會擋我**;寫不出來的不進卡。目標 ≤2,000 字。★草案,未取代任何現行檔;採用要走一個 PR(動 CLAUDE.md 範本=守衛面)★。

---

## lumos 操作卡(v0,2026-08-21)

**一句話**:圖譜記「為什麼」,code 記「長怎樣」;動 code 前先讀圖譜,動完寫回,工具會在三個點擋你。

### 進場(每個任務第一步)
| 做什麼 | 指令 | 誰提醒 / 誰擋 |
|---|---|---|
| 找到相關節點 | `lumos search <詞>` → `lumos context <節點>` | ★沒人擋★(純自律)。Edit/Write 時 impact hook 會自動注入該檔的合約與相關節點——沒先查也會被塞一份 |
| 看硬合約 | `lumos contracts <節點>` | 同上;★INVARIANT★ 改了會在 pre-push 被 doctor [T] 擋 |

### 動手中
| 做什麼 | 指令 | 誰提醒 / 誰擋 |
|---|---|---|
| 改了 code → 同步圖譜 | `lumos set/append/decision-add`,body 用 Edit | **pre-commit 硬擋**「改 code 沒動圖譜」;`--no-verify` 能繞但★零留痕★(已知洞,#5) |
| 寫完節點 | `lumos lint <節點>` | ★目前沒人逼你跑★(已知洞,#6:擬併入 pre-commit) |
| 數字別寫死 | `<!--lumos:count=N re=… in=…-->` | doctor Check N 每次重算,漂了當場喊 |
| 不確定是不是合約 | **不標** | 沒人擋,但標錯=假合約,Check T 會逼你綁測試 |

### 設計 / 高風險改動
| 做什麼 | 指令 | 誰提醒 / 誰擋 |
|---|---|---|
| 設計要進實作前 | 計劃節點 → `lumos loop next <id>` 照吐的派席 → 三輪對抗審 → 人裁 | ★沒有機械閘擋「不審就實作」★;閘 `loop status` 只算帳。**老實講:它是三輪對抗審+人裁,不是「收斂才放行」** |
| 高風險 code 要 push | `lumos pitfalls --diff` 出 `tier: high` → code-loop 審 → `lumos code-loop pass\|skip --note` | **pre-push 硬擋**沒留痕的 high;skip 是合法逃生門但被數(skip 率 29%) |
| 每輪審查員收貨 | `lumos quote-check` / `refcheck` / `seat-check` | 機械判,錨不到的 finding 不採信 |

### 退場
| 做什麼 | 指令 | 誰提醒 / 誰擋 |
|---|---|---|
| 做完寫 Verification、掛 verified_by、計劃 status | `lumos new verification --plan …` / `append` / `set` | doctor 1/4~4/4 會抓孤兒與斷鏈(pre-push 跑 doctor --ci) |
| 拿掉/反轉了什麼 | `lumos search <舊名> --code` 逐句判 | delguard pre-commit 警告(★逾時會放行★,#9) |
| 收工 | `lumos doctor` 看 hard 段;push 後 `lumos ci-wait` | pre-push/CI 硬擋紅 |

### 三個逃生門(都合法,都被數)
`git commit --no-verify`(★目前不被數★)/ `lumos code-loop skip --note` / design-loop 達 cap 人裁。用了就在 commit message 或 note 寫一句為什麼。

### 不在卡上的
規格細節、歷史脈絡、已停用協議、各 Check 字母的語意 → `lumos-project-notes` reference.md 與圖譜節點。**卡上沒寫的規則,不是規則。**

---

## 這張卡跟現況的差距(採用前要先做的)

- #5 `--no-verify` 留痕、#6 lint 進 pre-commit、#9 delguard 逾時留痕——卡上三個「★」要變成真的,否則卡在騙人。
- CLAUDE.md 現行紀律區塊 3,504 字 + graph-discipline.md 範本要縮成這張卡;design-loop/code-loop SKILL.md 頭版砍到只剩「怎麼派席、怎麼記帳、怎麼收貨」三段,其餘搬 reference。
- 「收斂」一詞全面改「三輪對抗審+人裁」,對齊 15+ 案的實況。
