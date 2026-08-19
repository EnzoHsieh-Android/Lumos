# 閘觸發帳統計 r2 — 對抗審計(s2:推論效度席)

審查對象:`/tmp/閘觸發帳統計-r2.md`(154 行)。本席只查一件事:**這份統計能不能撐住它要撐的結論**——
「閘響幾次 / 從沒響 / 沒收斂」→「這道紀律該不該退場」。round1 已抓過的(去重歧義、除以零、
假收斂 0.8、平均公式、六→九節點……)不重報,只查 round1 漏掉、且我能拿真資料印證的洞。

方法:直接讀 `scripts/lumos` 的 `cmd_gov`/`run_doctor` 原始碼,並對 `docs/.governance-log.jsonl`
(20,139 行)與 `docs/lumos-toolchain-knowledge/` 實際跑 python/grep 核對文件裡的每個數字與敘事。

---

## F1(major)—「五道零觸發」把「查過沒事」跟「這功能整個 repo 從沒人用過」混為一談

文件把 `check-r/check-j/check-k/check-e2/check-e3` 五道並列成同一桶「零觸發」,並主張:

引句:「所以零筆=真的沒響過,不是沒接線」

這句只排除了「沒接線」一種可能,但漏了第三種、而且在真資料裡**確實發生**的狀態:**閘的前置條件
(某欄位/標記被用過)本身在整個 vault 裡出現次數=0,導致該閘的核心邏輯段從未被執行過一次**,
跟「執行過、掃過真資料、沒找到違規」是完全不同等級的證據。

實測(`scripts/lumos:1289-1291`):

```python
_regen_rels = [(rel_, n_) for rel_, n_ in sorted(notes.items())
               if isinstance(n_.fields.get("regen"), str) and n_.fields.get("regen").strip()]
if _regen_rels:
    section("J", ...)   # check-j 整段(含 gov_events.append)都包在這個 if 裡
```

我對 vault 全掃:

```
$ grep -rl "^regen:" docs/lumos-toolchain-knowledge/ | wc -l
0
```

**目前 vault 沒有任何節點帶 `regen:` 欄位。** 這代表 `check-j` 這個 `if` 區塊,不管 `doctor --ci`
跑了幾百次,**連進都沒進去過一次**——它的「0」不是「查過 420 次 commit、沒違規」,而是
「這個檢查所稽核的實務(from-scratch 重生節點標 `regen:`)本身在這個 repo 裡還沒被用過」。這是
「這道紀律有沒有用」與「這個功能有沒有人用」兩件事,文件把它們摺成同一種零。

對照組:`check-k`(★COMBO★,6 個檔用了)、`check-e2`/`check-e3`(`decision_refs`/`valid:false`
決策各有 1/4 個檔存在)、`check-r`(★IRREVERSIBLE★/★CHECKPOINT★ 16 個檔存在)——這四道的前置
條件在 vault 裡是**存在**的,零觸發是它們真的掃過真資料沒找到問題,屬於文件想講的那種「零」。
只有 `check-j` 是不同性質的零,卻被塞進同一列同一句話帶過。若這份統計未來被拿去論證「check-j
這道紀律可以退場」,論證依據其實是「沒人用 regen」而非「check-j 抓得住/抓不住問題」——兩者對
「紀律要不要退場」這題给出的答案完全相反(前者該推廣 regen 用法,後者才是退場理由)。

---

## F2(major)—收斂指標的最大宗資料源(check-s,佔原始行 90.8%)量的是「有沒有蓋章」,不是「有沒有修好」

文件的收斂算法(S1)明講只對 `hard=false` 且 `kind=warned` 的 advisory 算,理由是防範
「anchor-approve 那種低頻人為動作被算成假收斂」。但 `check-s` 本身**恰好完全符合**這個過濾條件
(`scripts/lumos:819,825`:`{"gate": "check-s", "kind": "warned", "hard": False, ...}`),於是
文件用來保護 anchor-approve 的那道過濾網,對 check-s 完全不生效。

`check-s` 判定「已收斂」的機制是比對 frontmatter 的 `self_audit` 日期是否 ≥ `updated` 日期
(`scripts/lumos:806-825`)。這是一個**人手動填寫、日期字串比對**的欄位,而 `run_doctor` 的
docstring(`scripts/lumos:804`)自己承認:「真實性無法機械驗(lumos 不 spawn agent)」——這句是
程式碼註解,不是本文件的文字,列在此處當 file:line 佐證,不算引句錨點。

也就是說:check-s 能機械驗的只有「這個日期欄位有沒有被碰過、日期夠不夠新」,**驗不了那次
self_audit 是不是真的做了 L4 審查**。這正是文件自己算出來的收斂數字要被戳破的一種讀法——它
同樣可能只是「有人把 self_audit 欄位打上今天日期以讓 doctor 閉嘴」。文件實算的那句收斂數字:

引句:「但不是全然零收斂**——實算 `check-s` 的收斂指標(曾被警告、且已停止再被警告的節點比例)=**12/42=0.286**」

這句話把「12/42=0.286」直接當「收斂」的實測結果呈現,但如上所述,分子的每一筆「已收斂」都只是
「self_audit 日期 ≥ updated 日期」這個可被手動蓋章滿足的條件,不是「問題真的被修好」的證據。

我對文件宣稱的 12 個「已收斂」節點逐一核對現況(`docs/lumos-toolchain-knowledge/Systems/*.md`
frontmatter),結果:

```
lumos-refcheck            self_audit: sonnet/2026-07-24
risk-tiered-review        self_audit: sonnet/2026-07-24
compose-metrics-adapter   self_audit: sonnet/2026-07-24
lint-version-watch        self_audit: sonnet/2026-07-24
pitfalls-lint-adapter     self_audit: sonnet/2026-07-24
cochange-guard            self_audit: sonnet/2026-07-24
guard-kill                self_audit: sonnet/2026-07-24
cross-family-audit        self_audit: sonnet/2026-07-24
```

八個(文件說九個,我按 `check-s` 節點/日期實算只拿到八個同日 2026-07-24 停 + 一個 2026-07-30
再停的 `lint-declaration-health`,詳見「附註」)彼此無關的子系統(lint 稽核器、compose 量測、
kill 稽核、cross-family 稽核……)在同一天被蓋上一模一樣的 `self_audit` 字串,這正是文件自己也
觀察到的模式:

引句:「節點在 2026-07-24 同日一起停,像是一次批次補審」

文件觀察到這個模式卻沒有往下追:**這模式本身就是「self_audit 真實性驗不了」這條已知限制的
具體實例**——同日批次蓋章跟同日批次真的各自做了獨立 L4 審查,從 ledger 上是**無法區分**的兩件
事,而 check-s 恰恰是那個「不受 anchor-approve 式假收斂過濾保護」的最大資料源(佔原始 20,139
行裡的 18,283 行=90.8%)。若日後有人拿「12/42=0.286 已收斂、30 個還在念」去論證「check-s 效果
一般,可以考慮降級」,這個數字本身就可能是「check-s 被蓋章式規避」的證據而不是「check-s 沒用」
的證據——兩種解讀导向完全相反的治理動作,而文件的統計設計無法區分。

---

## F3(major)—母體定義本身漏掉了 CLAUDE.md 明講、真正在擋 push 的硬閘,而非把它們算成「零觸發」

S1 明講母體:

引句:「母體 = `lumos gov` 既有讀入的帳(bypass/rot-queue/governance/canary/kill/signoff/ci)」

CLAUDE.md 自己說 pre-push 的閘是「doctor --ci + anchor verify + tier=high 未過 code-loop 硬擋」
三道。我讀了 `scripts/hooks/pre-push` 全文:

- `anchor verify`(呼叫 `cmd_anchor_verify`,`scripts/lumos:9993-10029`)失敗會 `exit 1` 直接擋下
  push;我讀完整個函式,裡面**沒有任何 `gov_events`/`_append_governance_log` 或任何寫檔呼叫**——
  它只 print 到 stderr,不寫進七帳的任何一本。
- `test_lumos.py` 全量測試失敗一樣 `exit 1` 擋下 push(`scripts/hooks/pre-push` 約行 57-72),
  同樣沒有任何 ledger 寫入。

這代表:**這兩道貨真價實、CLAUDE.md 點名的硬擋閘,在 `lumos gov --stats` 的輸出裡連「零觸發」
一列都不會出現**——不是進了零觸發桶被文件要求的自曝限制句保護,而是完全不存在於 gate 清單裡。
對照文件本身給的「母體」定義,這是**技術上自洽**的(母體就是七帳的並集,anchor verify/測試閘
本來就不寫七帳),但對這份文件宣稱的用途——「給『紀律要不要退場』提供第一手資料」——是一個
**未聲明的覆蓋率缺口**:凡是靠 hook 直接 `exit 1`、不寫治理帳的閘,永遠不會出現在任何統計桶裡,
包括「零觸發」桶。裁定者若拿 `--stats` 的輸出當「所有治理紀律的觸發史一覽」使用(這正是文件
緣起段暗示的用法:「哪道閘從沒響過」),會完全看不到 anchor verify/測試閘存不存在這個問題,
比誤判成「零觸發」更隱蔽。

---

## F4(major)—強制自曝措辭是針對 round1 抓到的具體偽陽性訂做的,沒有覆蓋 F1/F2 這兩種一樣存在於真資料裡的偽陽性

文件對零觸發桶要求的措辭:

引句:「窗口內零筆——可能從未觸發,也可能是有效嚇阻或守的情境還沒發生;零觸發不等於無價值」

這句列舉的兩種原因(「有效嚇阻」「情境還沒發生」)都預設了「這個閘的邏輯確實有在跑,只是沒抓到
東西」。但 F1 證實的 `check-j` 是第三種、更根本的原因:**這個閘要稽核的實務欄位在 vault 裡連一次
都沒被用過,閘的核心邏輯段從未執行**。這句措辭讀起來完全不會讓人聯想到「也可能是被稽核的功能
根本沒人用」,而這正是拿真資料一查就查得到的狀況。

不收斂桶的措辭:

引句:「入此桶不等於該閘無用——低頻人為留痕也可能因基數小而落入,判讀前先看 kind」

這句只保護「低頻人為留痕」(對應 anchor-approve)這一種偏誤,而 F2 證實的 `check-s` 偽陽性——
「收斂看起來是修好了,但收斂訊號本身是不可機械驗證的自填日期欄位,且觀測到明顯的同日批次蓋章
模式」——完全是另一種、措辭沒提到的偏誤。這兩處措辭都是**針對 round1 三席實際抓到的具體案例
量身訂做**,不是「窮舉這類指標的已知失效模式後寫出的通用警語」,所以碰到 F1/F2 這種同樣藏在
真資料裡、round1 沒抓到的偽陽性,措辭起不到自曝作用——是裝飾性的,不是機制性的護欄。

---

## F5(major)—Growth-test 的豁免理由承諾了這把尺做不到的事

文件用來豁免「第一問(真事故)」的核心論證:

引句:「先造尺是解開死結的唯一入口」

這句話的隱含承諾是:造出這把尺之後,「紀律要不要退場」這題就有了可信的量測依據。但 F2、F3
合起來說明:對真正高風險、真正需要靠這把尺做退場/保留裁決的兩類案例——① 硬擋閘(anchor
verify、測試閘)、② 收斂訊號依賴人工自填欄位的建議閘(check-s,佔資料 90.8%)——這把尺要嘛
完全測不到(①),要嘛測到的是一個承認驗不了真偽的代理指標(②)。真正測得準、測得乾淨的是
`check-e1/e2/e3/k` 這幾道低量、機械觸發條件明確的閘。所以「先造尺是解開死結的唯一入口」這句
話用來讓整個 `--stats` 功能豁免「查無事故」的資格審查,但它能兌現的範圍其實只有一部分——對
`check-s`(最大宗)和硬擋閘(CLAUDE.md 點名的關鍵治理機制),這把尺並不能解開死結,只是換了一種
量不準的方式繼續量不準。文件應把豁免範圍限縮到它真正能測準的機械觸發類閘,而非用同一句話涵蓋
全部。

---

## 附註(核對過程中的事實澄清,非獨立 finding)

- 12 個「已收斂」節點(check-s)我逐一用 `find`/grep 核對過,**全部仍存在於原名稱下**
  (`docs/lumos-toolchain-knowledge/Systems/*.md`),沒有被改名/刪除/歸檔/排除的情況——這點
  文件的「已停止出現」判讀不是因為節點消失而失真,而是如 F2 所述,因為訊號本身驗不了真偽。
- 我按實際 `nodes`+`ts` 重算 check-s 的「同日停」批次,拿到的是 8 個 2026-07-24 + 1 個
  2026-07-30(`lint-declaration-health`)+ 1 個 2026-07-16 一次性(`check-j-regen-guard`)+
  1 個 2026-08-16(`lumos-cli-read`),共 12 個,與文件「九個」的計數口徑有一個節點差異
  (`lint-declaration-health` 我算在 07-30 那批而非 07-24)。這是計數細節,不影響 F2 的論證
  （即便真是 9 個同日停也一樣支持「批次蓋章」的解讀),不單獨列 finding。
- `check-e1` 的 181 個 commit 確實是 `check-s` 420 個 commit 的子集(我用 python 實算驗證,
  `e1_commits <= s_commits` = True),文件這個宣稱是對的。

---

## 嚴重度統計

blocker: 0 / major: 5 / minor: 0
