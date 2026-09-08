# 條款綁測試算進度 r1 — 收貨與編排者機械重現

preflight-4: ran

分級 standard(3 席算人數:通才 / 接手的人 / 簡化守護者,＋架構對齊、外家否決)。
被審的是「設計審產出的驗收條款,實作時認領→勾掉怎麼不漂」的設計提案;上一案四版被打穿後的續案。
★上一案 r1 的編制留了 `seat_shortfall,單家族` 警示(只派一席算人數),這輪照 `loop next` 的名單派滿三席。★

## 前掃(preflight-4)——乾淨 agent 只給原始問題,逐句開碼驗

十條機械宣稱:**六條符合、兩條部分符合、一條不符合**,另抓到一個範例會自打臉、三個未定義詞、一個裁定 id 指錯。
全部在凍快照之前修進真檔;語意類逐條列前→後:

| 類 | 命中 | 修改前 → 修改後 |
|---|---|---|
| ④ 不符合 | 「CI 帳每個 sha 一筆」 | 實算 127 個 sha 裡 7 個有兩筆(等待逾時後補 success)→ 改成「每次 run 一筆;同 sha 取最新一筆,no-run/timeout 不算證據」 |
| ④ 部分 | 「Check T 只讀 System 節點摘要」 | 機制是「任一節點 frontmatter summary 欄位,不限型別」,只是今天只有 System 這樣寫 → 照實改;「不讀正文」那半對 |
| ④ 部分 | 「spec-trace 認領=驗證筆記正文提到 [SN]」 | 漏了 `plan_refs` 欄位回指這個硬條件,且掃的是全文 → 改成「plan_refs 回指+全文出現 [SN]」 |
| ② 壞引用 | S1 範例 `t_takeover_rechecks_pid_before_stealing` | 真名是 `test_…`、在 unittest class 裡;本 repo `test.method_regex` 只認頂層 `def t_…`,照抄範例會被判懸空 → 換成真的 `t_handoff_view`,並把 regex 盲區(144 支 class 內測試認不到)寫進 S1 |
| ① 未定義 | Beads / Spec Kit / 「照 d8」 | 前兩個當場一句解釋;d8 其實是「hook 事件帳」那條,我要指的是 v1 的 d2「只蓋四分之三」→ 改寫成原則、不指 id |

★前掃順帶逼出一段本來沒寫的隱患★:CI 帳當證據源是上一案 v1 的回鍋。已在「實務隱患」正面寫,並要求席位拿 v1 六個 blocker 群逐條打。
六條符合的:test-cache 只存 failed 清單、`lumos task` 不存在、bound-tests 帳不記測試名、`resolve_test_refs` 前綴未定義 raise、33 篇/15 篇、841 支/0 對——前掃自己重算的數字跟我的一致。


## 收貨三道

| 席 | quote-check | refcheck | seat-check |
|---|---|---|---|
| 外家否決(Codex terra/medium) | ✅ 3/3(正規化:第一句去巢狀「」同句截短、去重複印出的第二份) | ok 5 | 3 份材料未提(觀測) |
| 架構對齊 | ⚠ 9 句 1 句錨不到(「沒綁」<10 字,在「對齊」段、不掛 finding) | ok 22 | 2 份未提 |
| 接手的人 | ✅ 全數錨定 | ok 14 | 6 份未提 |
| 通才 | ✅ 全數錨定 | ok 17 | 4 份未提 |
| 簡化守護者 | ⚠ 13 句 5 句錨不到(F2 多一字「到」/F5、F6 粗體箭頭/F10 『』/F11 截斷) | ok 11 | 8 份未提 |

簡化席錨不到的五句怎麼處理:F2(Check Y 是提醒不擋)與 F5(整套紅≠這條壞)**我自己機械重現後撈回**(下表);F10、F11 是確認型不需處置;F6(尚無證據混三種)不採信,但 f8 的列字拆法自然把它解了,intake 記一句、不算它的功。
碰到材料少是因為五席各有鏡頭,引 file:line 當證據一律算合法。

## 編排者自己重現的(≥major 一律自己查過才折)

| # | 席 | 我怎麼驗 | 結果 |
|---|---|---|---|
| f1 證據 sha 上沒那支測試 | 外家 blocker | `git grep -E '^def t_handoff_view' 9854ba5`(合併前 commit)→ 沒有;而 CI 帳寫入欄位只有 ts/run_id/sha/branch/workflow/conclusion | **HIT**,而且修法量過:在 sha 上 `git grep` 27ms、`git show` 抽本文可比對 |
| f2 bound-tests 帳套不到單支 | 外家 blocker、簡化 F4 | 讀 `_bound_tests_log` 寫入欄位:nodes+「N 綠」計數,無測試名 | **HIT** → 砍掉不當證據源 |
| f3 同 checkout last-write-wins | 外家 major | `_write_lf` docstring 原文「read-modify-write 的併發 last-write-wins 窗仍在(單機 CLI,不上鎖,accepted)」 | **HIT**,我寫的「衝突走 git」只對跨 checkout 成立 |
| f4 CI 讀法跟 ci-status 打架 | 架構 major、通才 F3、簡化 F3/F9 | 讀 17101-17109 註解與碼;把既有規則套到 7 個多筆 sha:6 個報 timeout-waiting、1 個報 failure——跟我寫的「取最新一筆」答案不同 | **HIT** → 沿用既有、抽共用 |
| f5 表塞 handoff 撤了它的免審理由 | 接手 F-S3-1 | 讀 接手視圖_計劃 KEY 行:「不判完成」四處、「不印進度、不印完成」 | **HIT** → 表搬去 spec-trace |
| f6 設計審出口零約束 | 接手 F-S3-2/F-VS、架構 minor、簡化 F12 | 讀 SKILL.md 第 8/10 步與 `_loop_status_disposal`:只驗處置與 hash,不看 [SN]/[test:] | **HIT** → 處置閘加一步 |
| f7 REVISIT 不在行首 | 接手/通才 F8/簡化 F13 三席獨立 | 用 E5 同一套 strip 邏輯跑那行 → False | **HIT** → 獨立一行,重跑 grep 確認 `^- REVISIT:` |
| f8 列字沒帶天花板 | 接手 F-S2-1、簡化 F5/F10 | CI conclusion 是整套級(欄位讀過) → 「紅」不一定是這條 | **HIT** → 每列自帶「單支未證 / 不一定是這條」 |
| f10 懸空≠寫錯 | 通才 F2 | 對 test_autonomous_loop.py 套 method_regex → 0 支;名字明明在檔裡 | **HIT** → 分「設定認不到」、不進分母 |
| f11 handoff 掃 4.5MB 帳 | 通才 F6 | `wc -c docs/.governance-log.jsonl` | HIT 但被 f2+f5 消解(不讀那本、表不在 handoff) |
| f12 配對範圍沒定義 | 通才 F7 | `SPEC_CLAUSE_RE`/`TEST_REF_RE` 都是全文正則,無行邊界 | **HIT** → 同一行 |

## 折入的十四條(去重後;席位原編號→折入編號)

f1 證據 sha 必含測試且本文相同(外家 1)/ f2 砍 bound-tests 證據源(外家 2、簡 F4)/ f3 同 checkout 併發訂正(外家 3)/
f4 CI 讀法沿用 ci-status 抽共用(架 1、通 F3、簡 F3、簡 F9)/ f5 表搬 spec-trace、handoff 只指路(接 F-S3-1)/
f6 處置閘擋沒標條款+單一裁決來源(接 F-S3-2、接 F-VS、架 2、簡 F12 分階段)/ f7 REVISIT 獨立一行(接 F-REVISIT、通 F8、簡 F13)/
f8 每列自帶天花板、尚無證據拆兩列(接 F-S2-1、簡 F5、簡 F10、簡 F6 順帶)/ f9 四態不是三態、懸空明列(接 F-S2-2 ⚠、通 F4)/
f10 懸空分「寫錯 / 設定認不到」、後者不進分母(通 F2)/ f11 掃描成本明列(通 F6)/ f12 配對範圍=同一行(通 F7)/
f13 措辭三處:regex 要 t_ 前綴、Check Y 提醒不擋、System 節點非機制限制(通 F1、簡 F2、通 F5)/
f14 `[manual:]` 給沒測試可掛的條款(從「散文級」升格為標記,接手席 F-S3-2 的「寫不出來標散文級」要機器認得到才擋得了)。

**確認型五條不列處置**(不是缺陷,是席位開碼確認宣稱成立):簡 F1(_classify_one 可沿用)、簡 F7/F8/F10(v1 三群 blocker 不成立)、簡 F11(合約候選段是純文件改)。

## ★一個裁量要攤給 Enzo★

簡化席 F12 主張「先只出 S1 量習慣,S2 押後」。我折成**S2 設計現在審完、實作列第二階段、開工條件=REVISIT 量到 ≥五成**。
理由:r1 全部 blocker 都落在 S2,而 S2 的價值押在 S1 的習慣;這不是把難的那塊丟掉——S2 的修法(f1/f4/f8)全寫進去、席位審過。
但「核心價值」是否包含「現在就要證據欄」,是 Enzo 的裁量;我判分階段不算捨徑,若不同意,把開工條件那行刪掉即可、設計不用重審。

## 我判錯、被席位糾正的

- 我寫「同 sha 取最新一筆」以為是沿用既有讀法——其實既有碼註解明文拒絕這種讀法。
- 我以為把表塞進 handoff 是「用既有入口」——那個入口免設計審的理由正是「不判完成」。
- 我寫的回頭條件自己就是鐵則四說的「純散文=沒人會回頭」——三席獨立抓到,而且 doctor 真的讀不到。
- 接手席原判 `Systems/design-loop` 不受影響——折入 f6 之後**受影響**(處置閘語意變),intake 在此更正、合約候選已列。

## 留痕紀律

★這一份在按下記帳之前寫完★,含上面「攤給 Enzo」與「我判錯」兩段。carrier=通才(全錨、算人數、8 條);其餘四席各記一筆留痕不帶處置清單。

## 處置

14 條**全部折入,accepted 為空**——輪內有 blocker(外家席),依規則 accepted 必空。

(本檔在此之後不再修改。)
