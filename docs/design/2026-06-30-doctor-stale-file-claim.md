# 設計:doctor Check P — 失效檔案認領(doctor-stale-file-claim)

- 日期:2026-06-30
- 狀態:design-approved
- 動機來源:2026-06-30 治理日報 gap G3「doctor 只抓孤兒筆記、不抓孤兒程式碼;圖譜×程式碼交叉審計只靠偶爾手動」。收窄後 v1 取「**B 失效認領**」:圖譜正文指向**已不存在**的檔路徑(碼被刪/改名,圖譜還指著)。
- loop_id:doctor-stale-file-claim

## 目標(一句話)

`lumos doctor` 新增**軟性 Check P**:掃每個節點正文裡「指向 repo 內檔案的路徑引用」,**檔案不存在即軟提醒**——把「圖譜指向死碼」這類漂移從偶爾手動交叉審計,變成每次 doctor 都跑的確定性檢查。**不計 issues、不改 rc。**

## 收窄決定(brainstorm,2026-06-30)

G3 字面的「孤兒程式碼=有碼沒節點」太吵(lumos 刻意只記載載重碼,多數碼本就不必有節點)。三種解讀中選 **B 失效認領**(低噪、高值、確定性);**不做** A(字面孤兒,噪音最高)與 C(改動碼沒節點的漂移提醒,v1 延後)。gate 行為選**軟提醒起步**(同 Check S/V;路徑抽取仍可能偶有偽陽性,不擋 CI)。

## 前提與既驗事實(逐字審計,2026-06-30)

- **既有「code→節點認領」靠 path/stem 提及**:`scripts/hooks/claude/check-graph-sync.py:266 find_notes_mentioning` 以「檔名 stem」反查節點提及——本 spec 沿用「節點正文提路徑」即認領的既有語義,但方向相反(掃節點→驗檔在不在)。
- **doctor 現有 [2/4] Unresolved wikilinks 只抓壞 `[[wikilink]]`**(`scripts/lumos` run_doctor 內),**抓不到節點正文 inline-code 裡指向死碼的檔路徑**——Check P 補的正是這條缺口,兩者互補不重疊。
- **doctor 落點**:`run_doctor`(`scripts/lumos:360`);Check 段尾現為 T→R→S→H→K→V(`section("V")` 在 `scripts/lumos:729`,`if ci:` 在 `:749`)。Check P 接在 V 之後、`if ci:` 之前 → 段尾變 T→R→S→H→K→V→P。
- **節點原文可讀**:`(env.vault / rel).read_text(encoding="utf-8-sig")`(`scripts/lumos:804` 既有用法)。`env.notes` 為節點 dict、`env.vault` 為 vault 路徑。
- **軟提醒原語**:`warn_soft(lines, head, advice)`(`scripts/lumos:384`,不計 issues、不改 rc)、`section(idx, title)`(`:369`)、`ok(msg)`(`:372`)皆 run_doctor 閉包。

## 範圍:Check P 路徑抽取與判定

**repo_root 取法**:`git -C <env.vault> rev-parse --show-toplevel`(穩、避開 vault==root 的坑)。取不到(非 git / git 失敗)→ Check P 印 ok「(非 git repo,略過失效認領檢查)」並跳過。

**逐節點掃**(`for rel, n in sorted(env.notes.items())`),讀該節點原文,抽「檔路徑引用」:
1. 只取 **反引號 inline-code span**(`` `...` ``)——直接濾掉散文裡的 `maker/checker`、`T→R→S` 等帶斜線非路徑 token。
2. 對每個 span token:剝尾端 `:行號` / `:行-行`(regex `:\d+(?:-\d+)?$`);跳過 `http://`/`https://`/含 `://` 者;**須含 `/`**(排除裸符號如 `cmd_context`)。
3. **第一段須是 repo_root 的現有頂層目錄**(`first_seg in {p.name for p in repo_root.iterdir() if p.is_dir()}`)——錨定真實結構,`and/or` 之類不收。
4. 解析 `repo_root / token`;**不存在** → 一條 finding `{node: rel, path: token, line: <剝掉的行號或空>}`。
5. 同一節點同一路徑去重。

**輸出**:
- 有 finding → `warn_soft`,逐條 `「<rel> → <token>(已不存在)」`,advice=「碼被刪/改名?更新節點正文的路徑引用,或補對應節點」。
- 無 finding → `ok("無失效檔案認領 (節點引用的 repo 路徑都存在)")`。

## 邊界 / 非目標(YAGNI)

- ❌ **不做 A**(字面孤兒:碼沒節點)——噪音最高,非 v1。
- ❌ **不做 C**(改動碼沒節點的漂移提醒)——v1 延後。
- ❌ **不抓裸符號/函數名引用**(`cmd_context`、class 名)——非路徑、無法對檔案系統判存在。
- ❌ **不抓非反引號的散文路徑**——偽陽性來源,刻意只收 inline-code。
- ❌ **不抓整個頂層目錄被刪**的情形(第一段錨定會讓它落空)——罕見,v1 接受。
- ❌ **不改 rc、不擋 CI**(warn_soft);**不改** Check 2 wikilink 邏輯、不碰其他 check。
- ❌ **不做語義正確性判斷**——只證「指的檔還在」,不證「節點描述仍對」。

## 測試策略

CLI subprocess 風格(`run(v, "doctor")` 斷言 stdout),`t_`-prefixed,`check()` 斷言;hermetic temp vault(`mkvault`)。但因 Check P 需 repo_root=git toplevel,fixture vault 須 `git init` 並讓 vault 在該 git repo 下(temp dir `git init` 後在其中建 vault + 幾個真實檔)。

需覆蓋:
1. **失效認領報出**:repo 內節點正文含 `` `scripts/ghost.py` ``(該檔不存在)→ doctor stdout 含該節點與 `scripts/ghost.py`、含 `[P]` 段。
2. **存在路徑不報**(剝行號):建真實檔 `scripts/real.py`,節點含 `` `scripts/real.py:10` `` → 不報該路徑。
3. **散文/非路徑不報**:節點正文反引號 `` `and/or` ``、散文 `maker/checker`、反引號 `cmd_context`(無 `/`)→ 皆不報。
4. **無路徑引用 → ok**:節點無任何反引號路徑 → Check P 印 ok。
5. **非 git → 略過**:vault 不在 git repo → Check P 印「略過」ok,doctor rc 不受影響。
6. **rc 不變**:有失效認領時 doctor 仍 rc 0(warn_soft 不計 issues)。

## 知識同步影響

- `docs/methodology/圖譜即合約.md` / `對外論述.md`:可在「commit-time 強制 / doctor 巡檢」相關段補一句「doctor 亦抓圖譜指向死碼的失效檔案認領(Check P)」;無對應段則略。
- skills:`lumos-project-notes` 的 doctor 巡檢表(「健康巡檢一次到位」那段)補列 Check P;`lumos-design-loop` 無關。
- KG:落地後於 `Systems/lumos-cli-read`(doctor 屬讀/巡檢原語)summary 補一句 Check P;或新增 doctor-checks 節點(非必須,v1 放行時順手)。

## 誠實天花板

1. **死指針 ≠ 語義漂移**:Check P 只證「節點引用的檔還在」,證不了「節點對該檔的描述仍正確」(同 [test:]/[rollback:] 天花板)。
2. **路徑抽取靠 inline-code + 頂層目錄錨定**:漏裸符號引用、整頂層目錄被刪;偶有偽陽性(故軟、不擋)。
3. **B 不是 A**:Check P **不**保證「重要的碼都有節點認領」(那是 A,刻意不做);它只保證「圖譜既有的檔指針沒指空」。覆蓋率視角的「碼有沒有被記載」仍靠人 + 交叉審計(變體 B),未被本 spec 取代。
