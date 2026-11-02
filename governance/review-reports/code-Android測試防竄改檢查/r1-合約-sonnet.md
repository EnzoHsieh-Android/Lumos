severity: major

### F1 公開的驗證紀錄漏出考場的提交編號
severity: major
blocking: 是 — 去識別化漏出私有考場的提交編號,規則判 major
引句:「mOrangePos 本機演練分支 drill/test-guard(起點 c66c81b、卷證 436dad6)」
file: `docs/lumos-toolchain-knowledge/Verification/2026-11-02_Android測試防竄改檢查實跑.md:6`
後果:這份筆記在公開 repo。`c66c81b` 是私有考場的真實提交編號,同一個編號也出現在 `android-unit-standard-drill-20261101/README.md` 的「卷證補到 c66c81b」。`436dad6` 是新漏出的。同一批新增的 `android-test-guard-drill-20261102/README.md` 卻寫「提交編號都換成代稱」,兩者互相矛盾。
重現:`grep -n "c66c81b\|436dad6" docs/lumos-toolchain-knowledge/Verification/2026-11-02_Android測試防竄改檢查實跑.md` 在 frontmatter 的 `valid_under` 命中。公開卷證目錄本身掃過了,只剩這處。改成代稱或拿掉編號即可。

### F2 S1 條款「兩個相同的 @Ignore 得到兩個不同指紋」的測試沒驗到,拿掉序號測試仍綠
severity: major
blocking: 是 — 條款綁的測試沒驗條款寫的子情況,逐條改壞卻不紅
引句:「同一支檔加兩個相同的 `@Ignore` 得到兩個不同指紋。」
file: `scripts/test_lumos.py`(`t_tq_guard_skip_added` 末段,patch 第 314–319 行)
後果:測試用的是兩支「不同函式名」各加一個 `@Ignore`,身分本來就不同,所以「第幾個相同身分」的序號沒有被驗。序號被拿掉後,放行第一條會順帶放掉第二條,而測試不會紅。計劃自己要求「實作時每道判斷逐條改壞一次確認各自會紅」,這條沒做到。
重現:在 `git archive HEAD` 解出的暫存副本上,把 `scripts/lumos` 的 `_tg_cand` 內 `[rule, file, ident, str(nth)]` 改成 `[rule, file, ident, "1"]`,跑 `python3.14 scripts/test_lumos.py -k tq_guard_skip_added`,輸出 `14 passed, 0 failed`。
另一方面,同一函式內連寫兩個 `@Ignore` 時,原碼確實給出兩個不同指紋(`c9ae3d88668f3c0f`、`82447595d3b9fa88`),所以是測試漏驗,不是程式錯。

### F3 pitfalls-code-loop 舊段落與新行為矛盾:「整道關」「放行檔讀不了自動放行」
severity: minor
blocking: 否 — 措辭與現況不同步,不致照做出錯
引句:「環境變數 `LUMOS_SKIP_LINT_NEW` 整道關;設定檔 `.lumos/config.json` 的 `lint_new` 區塊有三態(擋／只報告／關閉)」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:205`
後果:這次改動讓 off 與環境變數跳過時「比對照樣在背後跑、有候選留帳」,但這段沒改,接手的人會以為關閉就是完全不執行。第 201 行也仍說「放行檔讀不了 → 自動放行」,新行為是有作弊候選時擋下。
同一段的「放行」條目(`lint-waive <指紋> --note "<理由>"`)沒提 10 字門檻與 AI 標記。新增的段落只補了擋下與小結怎麼印。
重現:`grep -n "整道關\|放行檔讀不了" docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md` 命中第 201、204、205 行。

### F4 S19 綁的 `t_test_quality_cli` 只看整份退出碼,新加的五支測試被刪不會紅
severity: minor
blocking: 否 — 沒有存在性守衛,但五支測試本身放寬就紅(已實測)
引句:「+    def test_device_indented_frames_are_attributed(self):」
file: `scripts/test_test_quality_cli.py:340`
後果:既有的存在性守衛 `t_test_quality_drill_cli_cases_present` 的名單沒補這五支。刪掉或改名其中一支,S19 仍綠。該守衛自己的說明就寫著「S5 綁的 t_test_quality_cli 只看整份退出碼,刪掉或改名其中一支仍綠」。
重現:我在暫存副本上逐一放寬判定(縮排、去空白、字界、fail|assert、從第一個堆疊行起),五支各自翻紅,所以測試本身有效。缺的是名單。

### F5 S15 的子情況沒有測試:逾時、讀不到回答、10 字邊界
severity: minor
blocking: 否 — 條款寫了,測試只驗沒有終端與答 y/n
引句:「沒有互動終端、逾時或讀不到回答記 `origin: ai`」
file: `scripts/test_lumos.py`(`t_lint_waive_ai_marking`,patch 第 1065–1074 行)
後果:測試只涵蓋 `/nonexistent-tty`,沒有涵蓋「終端存在但沒人答」的逾時。理由門檻也只測了 4 個實字與全標點,沒測 9 字拒、10 字收的邊界。把 `< 10` 改成 `<= 10` 測試不會紅。

### F6 「抓不到」清單在標準與工具說明裡被大幅刪減,與計劃承諾不符
severity: minor
blocking: 否 — 揭露不足,但 `--json` 的 `limitations` 與標準都有簡版
引句:「**抓不到的**,寫進工具說明與標準,不宣稱」
file: `docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md:371`
後果:計劃列了約十幾項。標準〈推送前的防竄改檢查〉只剩三句,`lumos test-guard --help` 一項都沒有,文字輸出也沒有,只有 `--json` 有三條 `limitations`。最容易繞過的幾種都沒被提醒:預期值先放進變數(`val expected = 88`)、參數化測試刪資料列、catch 裡只 `println(e)`、逾時換單位、把測試檔搬進 Gradle 不編譯的目錄。照標準操作的人會對工具有過度信心。
重現:`python3.14 scripts/lumos test-guard --help` 不含「抓不到」。

### F7 Semgrep 實跑的候選數對不上
severity: minor
blocking: 否 — 證據鏈的數字待釐清,結論未必錯
引句:「18 條候選,17 條是合成樣本、1 條是上一輪演練故意放的自比壞測試」
file: `docs/lumos-toolchain-knowledge/Verification/2026-11-02_Android測試防竄改檢查實跑.md:40`
後果:`semgrep/unit-output.txt` 逐檔列出的合成樣本命中是 6+7+4+4=21 行。`drill-scan-summary.json` 的 `java:scanned` 只有 1,17 恰好等於前三個檔的總和,所以 Java 的 `$Q.` 四條很可能沒走過 `lumos test-quality scan --semgrep`。S17 寫的是「對含那幾種寫法的檔跑 `lumos test-quality scan --semgrep`,每一種都應列成候選」。驗證紀錄沒解釋 21 與 17 的差。未能直接重現,以推算為準。

### F8 驗證紀錄的 `valid_under` 寫了會立刻過期的「未提交版本」
severity: minor
blocking: 否 — `lumos doctor` 已經唸出來,是過期前提,不擋推送
引句:「工具鏈分支 tq-android-hardening 未提交版本」
file: `docs/lumos-toolchain-knowledge/Verification/2026-11-02_Android測試防竄改檢查實跑.md:6`
後果:提交後三個月再看,沒有可以重跑的工具版本編號。
重現:`python3.14 scripts/lumos doctor` 的 [Z] 段列出「[c4] 前提寫『還沒提交』 1 筆(例:Verification/2026-11-02_Android測試防竄改檢查實跑:5)」。

### F9 `Systems/test-guard` 抄了程式查得到的內部結構與過程紀錄
severity: minor
blocking: 否 — 違反筆記寫法規範,但不影響行為
引句:「2026-11-02 推送前新增告警閘的複雜度規則(C901)擋下後拆成這樣,拆前拆後對考場 776 個提交的結果一字不差。」
file: `docs/lumos-toolchain-knowledge/Systems/test-guard.md:35`
後果:CLAUDE.md〈寫筆記時〉規定「程式碼查得到的一律不寫、過程紀錄不寫」。這篇有四處:
- 第 33 行與第 35 行逐一列了 `_tg_*`、`_lint_new_*`、`_cl_say_*` 的函式分工,第 34 行列了五種治理帳種類,這些程式都查得到。
- 第 35 行寫「拆後結果一字不差」,屬過程紀錄。
- 兩條 PITFALL(「改名成非測試檔時候選記在新檔名」「`enabled =` 換行接 `false`」)的出處是「實作時測試先紅」,是上線前就修掉的開發過程,不是事故。

### F10 計劃審計紀錄提到的 `tq/gate-config` 是未定義的規則代號
severity: minor
blocking: 否 — 歷史敘述,規則表與程式裡都沒有
引句:「`tq/gate-config` 是專案裡第三種「同一次推送放寬不算數」的做法」
file: `docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md:275`
後果:接手的人會去規則表和程式找這條規則,找不到。程式裡實際有 14 個 `tq/` 代號,都沒有 `gate-config`。

## 圖譜鏡頭
讀了 `Systems/test-guard`、`pitfalls-lint-adapter`、`pitfalls-code-loop`、`room-guard`。這份 diff 沒有跟它們登記的合約衝突:這幾篇都沒有 ★INVARIANT★ 這類合約行,`lumos contracts` 回「沒有登記」。
- **格式**:12 篇相關筆記 `lumos lint` 全部 0 問題。新增的 WHY 與 PITFALL 必有鍵齊全。測試綁定的名稱全都存在,`spec-trace` 23 條款中 20 條綁了、3 條靠人、0 懸空。
- **家的歸屬重疊**:`pitfalls-lint-adapter` 的 responsibility 寫「放行檔與 lint-waive」。`test-guard` 的 responsibility 也寫「lint-waive 的 AI 放行標記」。`test-guard` 本文還列了擋下與小結的印法函式(`_cl_say_lint_block` 等),而 `pitfalls-lint-adapter` 寫這塊歸 `pitfalls-code-loop`。三篇對同一批程式各說各的歸屬,見 F3、F9。
- **`pitfalls-lint-adapter` 的 KEY 補丁**:「例外(2026-11-02)」那句與 `Systems/pitfalls-code-loop` 的「整道關」並存,見 F3。
- **去識別化**:`android-test-guard-drill-20261102` 與 `android-unit-standard-drill-20261101` 兩個目錄的 manifest 逐檔實算 sha256 全部相符,沒有漏列、缺檔。目錄內未見真實套件名、類別名、本機路徑,只有 `com.google.common.truth` 這種公開函式庫。唯一的漏出是 F1。

兩個方向的核對都成立:`lumos --help` 的頂層命令數是 98,與 `ARCHITECTURE.md`、`reference.md`、`INDEX.md` 一致。中英兩份指令參考關於 `lint-waive` 與 `lint_new.gate` 的句子語意對得上。

總結:2 條 major(私有提交編號出現在公開驗證紀錄、S1 指紋序號的測試漏驗),其餘 8 條為文件現況、測試覆蓋與筆記寫法上的 minor。
