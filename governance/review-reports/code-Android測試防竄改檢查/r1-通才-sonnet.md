severity: major

## 圖譜鏡頭

- `Systems/test-quality-cli`:新增的五支裝置歸因測試(縮排、第一行去空白、字界、`fail|assert` 限定、從第一個堆疊行起算)我各放寬一次,都翻紅。`t_secev_tq_device_text_fault_counts_like_assertion` 要把收證歸因整段拿掉(同步更新配套指紋)才翻紅;不更新指紋時整條路都壞,`dev == plain` 兩邊同為 `(None, [])` 仍成立,靠前置斷言 `rt != plain` 才擋得住。這部分與節點宣稱相符。
- `Systems/test-guard`:
  - 節點寫「候選指紋用規則、檔案、函式名加本體簽名、第幾個」。實際上 `tq/skip-added` 的身分帶整段本體簽名,本體一改放行就失效(見 F4)。節點沒寫這個代價。
  - 計劃做法一寫「同一個身分第二次出現,指紋不同」,`tq/expected-changed` 沒做到(見 F8)。
- `Systems/測試假綠形態` 的 KEY②「守衛的能力宣稱比它實際擋得住的寬」:`t_tq_guard_build_config`、`t_tq_guard_no_assertion` 等的「翻紅釘」清單就是這一型(見 F7)。
- 固定席沒附上,是我自己讀節點判的。

### F1 完整類別名寫的跳過註記全部漏抓
severity: major
blocking: 是 — 加跳過標記是這支工具的第一目的,而完整類別名寫法繞得過去
引句:「_TG_SKIP_RE = re.compile(r"@(?:org\.junit\.)?Ignore\b|@Disabled\b|@SdkSuppress\b|@FlakyTest\b|@Config\s*\(\s*sdk\b"」
file: `scripts/lumos:48635`
`@Ignore` 有照顧到 `org.junit.` 前綴,另外四種沒有。`@` 後面一定要緊接短名,所以 `@org.junit.jupiter.api.Disabled`、`@androidx.test.filters.FlakyTest`、`@androidx.test.filters.SdkSuppress`、`@org.robolectric.annotation.Config(sdk = …)` 都不會命中。S1 只測短名。計劃「抓不到的」清單也沒列這個。
重現:`python3.14 /tmp/lumos-seat-work/code-Android測試防竄改檢查/通才-sonnet/repro.py fqn`
```
@Disabled                                               (1, [('tq/skip-added', ...CalcTest.kt)])
@org.junit.jupiter.api.Disabled                         (0, [])
@androidx.test.filters.FlakyTest                        (0, [])
@org.robolectric.annotation.Config(sdk = [28])          (0, [])
```

### F2 類別層級的跳過次數跨檔合算,互抵,候選還記到別的檔
severity: major
blocking: 是 — 一次推送解開 A 檔的 `@Ignore`、替 B 檔新加 `@Ignore`,工具判成乾淨
引句:「dst[ident] = dst.get(ident, 0) + n」
file: `scripts/lumos:48989`(`_tg_test_file`),歸檔在 `_tg_hit_cands` 的 `next(...)`(約 `scripts/lumos:49000`)
跳過與門檻字樣的次數表是所有改到的測試檔合在一起。類別層級的 `@Ignore` 不在任何函式裡,身分是 `("tq/skip-added","","@Ignore")`,各檔相同,所以能互抵。候選的檔案又取「第一個含這行文字的測試檔」,不是命中的那一檔。放行檔綁的是 `rule+file+ident+nth`,所以放行會綁到錯的檔。
重現:`python3.14 /tmp/lumos-seat-work/code-Android測試防竄改檢查/通才-sonnet/repro.py swap`
```
A 拿掉 @Ignore、B 新加 @Ignore: (0, [])
A 本來就有 @Ignore(只改了別處)、B 新加 @Ignore: (1, [('tq/skip-added', '.../ATest.kt')])   <- 該記 BTest
```
這是為了「測試搬檔不算新增」做的跨檔合算,卻讓類別層級的註記也跟著合算。

### F3 註記和 `fun` 寫在同一行時,`expected =` 完全看不到
severity: major
blocking: 是 — S1(既有測試新加 `expected =`)與 S5(帶 `expected =` 的測試不算沒斷言)在同一行寫法下兩頭都錯
引句:「"annot": "\n".join(lines[s - 1:decl])」
file: `scripts/lumos:48442`
`annot` 只收宣告行「以上」的行(切片不含 `decl` 那一行),同一行的 `@Test(expected = …) fun x()` 不在裡面。`_TG_EXPECTED_ANN` 和 `prev["annot"] == f["annot"]` 都靠它,所以:
- 既有一行寫完的測試加上 `expected = IllegalStateException::class`:不列(假陰性,這正是把失敗改成「預期例外」的作弊)。
- 新寫的、同一行帶 `expected =` 的合法例外測試:被誤列 `tq/no-assertion`(假陽性)。
- Java 的 `@Test(expected = AssertionError.class) public void adds()` 同一行也一樣(我另跑 Java 版也漏)。
S1、S5 的樣本都是分兩行寫,所以測試抓不到。
重現:`python3.14 /tmp/lumos-seat-work/code-Android測試防竄改檢查/通才-sonnet/repro.py expected`
```
同一行:既有測試加 expected= (0, [])
分兩行:既有測試加 expected= (1, [('tq/skip-added', ...)])
同一行:新寫的例外測試(合法) (1, [('tq/no-assertion', ...)])
```

### F4 早就被跳過的測試只要改本體,就被判成新加跳過;放行指紋也跟著本體變
severity: minor
blocking: 否 — 候選本來就不是定罪,代價是誤報加重複放行(每次要終端問人)
引句:「who = f["name"] + ":" + hashlib.sha256(f["sig"].encode("utf-8", "replace")).hexdigest()[:8]」
file: `scripts/lumos:48683`
`owner` 帶整段本體簽名(為了讓測試搬檔時身分不變)。主線上已有 `@Ignore` 的測試,在分支上只改了本體(`f()` 改成 `f(2)`),身分就換了,舊 `@Ignore` 被當成新增。反過來,放行過的 `tq/skip-added` 之後再改本體,指紋就變,要重新放行。S11 的「指紋不變」只測了上下文位移、整檔重新縮排、搬家。
重現:`python3.14 /tmp/lumos-seat-work/code-Android測試防竄改檢查/通才-sonnet/repro.py bodyedit` → `(1, [('tq/skip-added', ...)])`。

### F5 `_lint_new_relax` 的空樹早退沒有任何測試釘住
severity: minor
blocking: 否 — 守衛的一個分支沒有測試,實際影響是新 repo 第一次推送
引句:「if base_sha == _EMPTY_TREE_SHA:」
file: `scripts/lumos:39009`
拿掉這一行,`-k lint_new`(61 條)和 `-k lint_waive`(21 條)全綠。行為卻不同:第一次推送(起點是空樹)而專案設定 `gate: warn` 時,空樹那一版沒有設定檔、被當成預設 block,於是誤報「放寬」,把這次強制判 block,還多寫一筆 `relax-deferred`。S13 的空樹樣本用預設設定,走不到這裡。
重現(變異加行為):
- `python3.14 /tmp/lumos-seat-work/code-Android測試防竄改檢查/通才-sonnet/runm1.py` 的 M1 輸出 `lint_new => 61 passed, 0 failed`。
- `python3.14 /tmp/lumos-seat-work/code-Android測試防竄改檢查/通才-sonnet/p5.py <原版或變異版>`:原版 `mode= warn`;拿掉早退後 `mode= block`,並多出 `relax-deferred` 事件。

### F6 `lint-waive` 與健檢的四個新分支改壞測試照綠
severity: minor
blocking: 否 — 覆蓋面問題,沒有一條會讓驗收條款失守
引句:「if _lint_waiver_ai_unacked(it) and (ack_all or k == key)」
file: `scripts/lumos:37910`
`runm1.py` 實跑,以下改壞全部維持綠:
- M5 把 `--ack <指紋>` 改成只認 `--all`:`lint_waive` 21 條全綠。測試只跑 `--ack --all`。
- M2 把理由門檻 10 改成 5:全綠。測試只用 4 個字(被拒)和 12 個字(放行),邊界 9 和 10 沒人釘。
- M3 把健檢新增的五種帳(`skipped` 等)的顯示整段拿掉:全綠。`t_lint_new_warn_off_and_relax` 的檢查名寫「健檢把…各自數出來」,其實只測 `_lint_new_kind_counts` 這個函式,沒跑 doctor。
- M4 拿掉「比對本身壞了」時印給人的單次出口 `LUMOS_SKIP_LINT_NEW=1 …`:全綠。S13 只斷言「作弊比對沒跑完」。

### F7 測試說明的「拿掉一條就紅」過頭,至少五種拿掉測試照綠
severity: minor
blocking: 否 — 假陽性方向的名單,不影響擋不擋
引句:「翻紅釘:_TG_BUILD_RES 拿掉一條、test 區塊判法只看同一行、dependsOn 拿掉不看 → 紅。」
file: `scripts/test_lumos.py:120800`
`runm3.py` 實跑 `-k tq_guard`,下列拿掉後都是 `114 passed, 0 failed`:
- Q1 `_TG_BUILD_RES` 的 `not(Annotation|Class|Package)` 那條。
- Q2 `_TG_CI_KEYS` 的 `if: false`、`continueOnError`、`is_skippable`、`ignore_failure`。
- Q3 `_TG_ASSERT_RE` 的 `awaitComplete`、`expectNoEvents`、`confirmVerified`。
- Q4 `_TG_SNIFF` 的 `isRunningTest`、`isRobolectric`。
- Q5 `_TG_SKIP_RE` 的 `Assumptions.assume`。
`t_tq_guard_no_assertion` 的 docstring 寫「斷言字表拿掉一種」同樣不實。清單比測試實際釘住的寬,對應圖譜 KEY②。

### F8 同一支函式裡兩條相同的「預期值被改」共用同一個指紋
severity: minor
blocking: 否 — 放行一條會順帶放掉另一條
引句:「out += [_tg_cand("tq/expected-changed", path, f["start"], f"{k}\x00{c}") for a, c in _tg_pairs(so, sn) if _tg_expected_changed(a, c, kt)]」
file: `scripts/lumos:49110`
這裡沒傳 `nth`。計劃寫「同一個身分第二次出現,指紋不同,放行第一個不會順帶放掉第二個」。實測 `assertEquals(1, f(1))` 連寫兩行、都改成 `assertEquals(5, …)`,得兩條候選,指紋同為 `ce00b306442dc746`,行號也同為 4。S4 沒有這個樣本。

### F9 沒宣告檢查工具的專案,範圍兩端算不出來時從「無設定」變成「自動放行並記帳」
severity: minor
blocking: 否 — 罕見範圍,但會讓健檢的「自動放行」數字摻進假的
引句:「if not tip or not start:」
file: `scripts/lumos:38954`
原本「沒宣告任何檢查工具」(no-config)先於範圍解析,現在解析搬到最前面。同一個無 lint 設定的專案,範圍是 `aaaa…aaaa..<提交>`(起點本機沒有)或單一參考點:
- 舊版:`status=no-config, autopass=False`。
- 現版:`status=env-unavailable, autopass=True`。
`_codeloop_lint_new_step` 因此寫一筆 `fail-open`。重現:`python3.14 /tmp/lumos-seat-work/code-Android測試防竄改檢查/通才-sonnet/p15.py <舊版 lumos_base.py 或 w1/scripts/lumos>`。

### F10 擋下的推送同時被記成自動放行
severity: minor
blocking: 否 — 帳的口徑,舊流程已有類似狀態
引句:「out["autopass"] = False     # 有候選卻放不掉:擋下,不記自動放行」
file: `scripts/lumos:38968`
只有 `waiver_err` 這一支會把 `autopass` 清掉。作弊候選成立(擋下),而檢查工具那一半提早回 `env-unavailable`(例如 `.lumos/lint-deps.json` 壞掉)時,`blocked=True` 與 `autopass=True` 並存。`p7.py` 實跑:`status=blocked, autopass=True`,帳上多一筆 `fail-open`,內容是擋下理由「1 條新增告警(其中 1 條是作弊候選)」。

所有重現腳本與變異結果都在 `/tmp/lumos-seat-work/code-Android測試防竄改檢查/通才-sonnet/`(複製的 repo 在 `w1`,原 repo 沒動),要刪的話請編排者收貨後整個刪;全部發現已寫完,共 3 條 major(F1 到 F3)和 7 條 minor。
