severity: major

## 結構與保留原句(鏡頭 3)

- 我寫了腳本逐對比較 diff 裡 87 組 `-`/`+` 行。把 `+` 行的「(更正 2026-10-30:…)」括號拿掉後,與 `-` 行逐字相同。唯一的例外是兩處 `updated:` 日期。
- 原句全部保留。
- 沒碰到 `decisions:` 欄位、`★INVARIANT★` 行或摘要行前綴。`指令索引與情境測試_計劃.md` 的 d1/d2 不在 diff 內。
- 兩篇的 frontmatter(`Issues/散文紀律沒有退場機制.md`、`Projects/執行DAG_調研.md`)只多了摘要行內的括號,格式沒壞。

## Findings

### N1 更正內容與同一檔案內的數字互相矛盾,會讓人低估 Sonnet 級審查席的風險
severity: major
blocking: yes

位置有兩處:Agent編排篇的候選 4,以及總覽篇第 6 點。這兩處都寫「崩跌只在小模型」。但同一份 Agent編排篇在 Mitropoulos 條目的更正裡,列了 Claude Sonnet 4.5 掉 21.9 點。研究筆記表 II 還標了 `***` 顯著:DeepSeek V3 掉 42.9、Gemini 2.0 Flash 掉 16.2。只有 Opus 4.5 的 6.9 點未達顯著。

研究筆記自己的推論是「席位用哪個模型,比擋不擋表態更先決定風險大小;Sonnet 級席位(−21.9)比 Opus 級(−6.9)暴露更多」。Lumos 實際派的就是 Sonnet 席。照「崩跌只在小模型」判斷,會誤以為附作者表態對 Sonnet 席沒風險。

引句:「(更正 2026-10-30:崩跌只在小模型;v5 的 Claude Opus 4.5 只掉 6.9 點且未達顯著,唯一通用防線是不把表態放進去)」

引句:「Claude Sonnet 4.5 97.4%→75.5%(−21.9)」(同一個 diff 內,Agent編排篇 Mitropoulos 更正)

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/governance/reports/research_notes/Lumos 九類前沿研究增量/04_Agent編排.md:114`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/governance/reports/research_notes/Lumos 九類前沿研究增量/04_Agent編排.md:151`

重現指令:`sed -n '114p;151p'` 讀上面那份檔案。

### N2 把兩個不同的 17% 混在一起
severity: minor
blocking: no

九類之外篇的原句是「過度積極動作 n=52、漏放 17%」,指分類器在 52 個過度積極動作上的漏放率。更正卻寫「原文的 17% 是會談早段人擋下危險指令的比例」。那是 08-07 文章裡另一個 17%,出自人工測試。

研究筆記 08 第 189 行明說,Anthropic 的 17% 是 real overeager 動作,不是整體漏放率。更正掛錯了句子的意思。

另外,新補的「auto mode 擋下 89%」沒提總報告第 283 行的警告:獨立評估量到漏放率 81.0%,筆記 09 與 08 不能並列引用而不註明。

引句:「原文的 17% 是會談早段人擋下危險指令的比例,別寫成整體漏放率」

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/governance/reports/research_notes/Lumos 九類前沿研究增量/08_平台分發.md:189`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/governance/reports/research_notes/Lumos 九類前沿研究增量/09_介面紀律與人.md:156`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/governance/reports/reports/Lumos 九類前沿研究增量.md:283`

### N3 ImpossibleBench「79%」有漏更的同源句
severity: minor
blocking: no

守衛閘門篇和總覽篇的 79% 都補了更正。但用 grep 掃現行檔案,同一個數字還有三處沒補:
- 介面文件紀律篇第 162 行
- 介面文件紀律篇第 273 行
- 迴圈工程篇第 208 行

這三處寫的是「Claude 系列作弊 79% 以上是改測試」。依據表明明列了這是 Opus 4.1、Sonnet 時代的數字。

引句:「(更正 2026-10-30:Opus 4.1、Sonnet 時代的數字)」

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Projects/世界解重新註解2026-10_介面文件紀律_調研.md:162`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Projects/世界解重新註解2026-10_介面文件紀律_調研.md:273`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Projects/世界解重新註解2026-10_迴圈工程_調研.md:208`

### N4 散文紀律 Issue 的結論句在更正後不再成立,卻沒點出來
severity: minor
blocking: no

Issue 的 ETH 條目已加更正:p 值 87% 與 37%,兩個方向都不顯著。TDAD 條目也已加更正:9.94% 只成立在測試層。但「★兩篇合起來的意思★」那段沒動。它還寫著「最壞的情況是主動把事情弄糟」。

標題行「外部把『無效』升級成『有害』」也沒動。兩條更正都已推翻「有害」這個說法。這段只靠上方 10-12 的舊更正,讀者會以為「有害」仍成立。

引句:「(更正 2026-10-30:v3(2026-09-29)已查不到 -3% 與 +4%;p 值 87% 與 37%,兩個方向都不顯著」

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Issues/散文紀律沒有退場機制.md:113`(未動的結論句)

### N5 介面文件紀律篇內部對 d1 的描述前後不一
severity: minor
blocking: no

這份檔案的頂部白話段和兩處「3.2 倍」已補更正:4k 上限在 2026-10-11 已取消。但同檔還有:
- 第 428 行寫 d1 `valid: true`
- 第 241 行寫「先由人裁要不要回到 d1 的 4k」

兩處都沒標示已被取代。實際上 d1 已 `valid: false`、被 d2 取代,日期是 2026-10-11(見 `指令索引與情境測試_計劃.md` 的 frontmatter)。

引句:「(更正 2026-10-30:4k 絕對上限 2026-10-11 已取消;現為 13320 bytes,是基線 5256 的 253%,「3.2 倍」不再適用)」

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Projects/世界解重新註解2026-10_介面文件紀律_調研.md:241`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/shearwater/docs/lumos-toolchain-knowledge/Projects/世界解重新註解2026-10_介面文件紀律_調研.md:428`

## 零 finding 項目:對回依據的更正(各附引句與核對結果)

- **ETH 2602.11988(p 值、v3、+4%/−3% 查不到):** 與依據相符,與網路核對一致(抽驗 1)。
  引句:「(更正 2026-10-30:v3 已查不到 -3% 與 +4%,兩個方向都不顯著,只有成本約多兩成站得住)」
- **TDAD(測試層對補丁層):** 與依據、原文相符(抽驗 3)。
  引句:「(更正 2026-10-30:9.94% 只成立在測試層,補丁層 30.2%、33.3%、33.3% 差異很小,解題率也沒升)」
- **Mitropoulos v5(32/33、16/32、−6.9、−21.9、v1 實際句):** 與研究筆記 04 逐項吻合(抽驗 2)。
  引句:「遮蔽 PR 說明救回 16/32(50%)」
- **auto mode 97% 與 13.6%(143/1,053)、89%(937/1,053)、39% 對 3%:** 與原文相符(抽驗 5)。
  引句:「受控測試裡人只抓到 13.6%(143/1,053),auto mode 擋下 89%(937/1,053);計劃被拒 39%、權限提示被拒 3%」
- **Khatri 描述性界、MDE>30pp、120–200 題與「每條件 30 跑」單位錯:** 與研究筆記 01、02 相符。
  引句:「(更正 2026-10-30:單位錯,原文 §4.5 要的是約 120–200 題,不是重複次數,「scaling requires more tasks, not more repeats」)」
- **常駐範本 13320 bytes、基線 253%:** 13320/5256=2.534,與現況核對表第 13 列相符。
- **METR 02-24 與問卷 05-11:** 與依據、筆記 05、09 相符。
- **SkillsBench v4(87 題、+16.6pp、−8.1/−11.3/−11.5):** 與筆記 01 第 58 行相符。
- **Kim 的 60%(Helm、基線 1/3、0.423/0.127):** 與筆記 04 第 200 行相符。
- **+13.6% 廠商自報:** 與依據相符。
- **ECK(合成擾動、0/50 為定義性結果):** 與筆記 01 相符。
- **SpecBench(27pp、R²=0.21):** 與筆記 06 第 178 行相符。
- **Dreadnode(33.0%→18.6%→8.5%、多為查解答、每組單次):** 與筆記 06 第 36–37 行相符。
- **Codex 0.164.0 內容綁定 / Claude Code 2.1.299 / Cursor 開關 / Plugin4Shell 升 B:** 與筆記 08 相符。
- **CodeRabbit 56.3% 分母、30,776 則由 GPT-5.1 標註、24.4%(7,570/31,073):** 與筆記 03 相符,算式正確。
- **ContextCov(30.1 對 29.2、57.3 對 53.0):** 與筆記 06 相符。
- **MCR-Bench、2609.35381、METR 設計變更、捏造率 19.7% 是 2024 數字、SlopCodeBench v1/v2:** 與依據相符。

## 5 處網路抽驗

1. **ETH 2602.11988:** arXiv 頁顯示最新為 v3(2026-09-29)。摘要是「does not generally improve task success rates… over 20%」,頁面查不到 −3% 或 +4%。與更正一致。p 值 87%/37% 在內文,未查到。
2. **Mitropoulos 2603.18740:** 最新為 v5(2026-10-27),標題是 *When AI Agrees Too Much*。摘要有「32/33 (97%)」,模板式偏誤「largely fails and can raise suspicion」。16/32 不在摘要頁,是內文,未查到。
3. **TDAD 2603.17973:** 原文逐字為「The instance-level regression rates (30.2%, 33.3%, 33.3%) appear to contradict the test-level result」。6.08% 是 Vanilla,9.94% 是 TDD Prompt,1.82% 是 GraphRAG+TDD。30.2/33.3/33.3 依序對應這三組,以分母差異解釋。與更正一致。
4. **Khatri 2607.27250:** 摘要為「bounded to <=10-15pp via equivalence testing」,最新為 v1(2026-07-28)。「descriptive TOST」與「not a powered equivalence claim」不在摘要頁(依據稱在 §6),未查到。
5. **Anthropic auto mode 文章:** 發表 2026-08-07、更新 2026-10-22。97%、39%/3%、13.6%(143/1,053)、89%(937/1,053)都有。「早段擋下約 17%」是人工數字,這證實 N2 的兩個 17% 是不同量。受試者研究由 Anthropic 自己呈現,不算獨立複現。

另外順帶核對了 CodeRabbit 2607.03316(v2,2026-07-23):摘要有 31,073 對、36.4/7.3/56.3%,但「排除沒人回覆的留言」不在摘要,未查到。SlopCodeBench 2603.24755 的 v2(2026-05-07)是 36 題、196 檢查點、2.3x/2.0x,v1 的 20 題/93 檢查點未查到。

本報告最高等級:major(N1)
