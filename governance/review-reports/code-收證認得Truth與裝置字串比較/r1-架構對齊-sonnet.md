severity: minor

整體判斷:這份 diff 沒有引入第二種做法,也沒有跨層直呼。有三處跟鄰居不一致,都屬 minor。

## 1. 分層與依賴方向:對齊

- 斷言歸因的新增碼放在既有的 `assertion_failure`,沒有新函式或新模組。Truth 兩個型別放在 NUnit 與 Xunit 分支之間,裝置那路改的是原來的 `if not kind:` 分支。
  - file: `scripts/test_quality.py:108-138`
  - 讀 XML 文字的方式仍是 `''.join(node.itertext())`,跟 Node、AGP 無型別分支一致。
  - Truth 用 `kind in (…)` 比對精確字串,跟 `kind == 'NUnit.Framework.AssertionException'`(第 113 行)同一類做法。
- 指紋表是在同一個提交裡直接改 `scripts/lumos` 的單行字典,沒有另設更新工具或別的流程。
  - file: `scripts/lumos:69701`
  - 前例同樣是這樣改:`git show c70b3d6af -- scripts/lumos` 中 `_TEST_QUALITY_BUNDLE_DIGESTS` 同一行被直接替換。
- 新增的標準守衛測試 `t_test_quality_standard_android_drill_lessons` 用的是現有那一套。
  - 它放在 `t_test_quality_standard_android_unit_section` 之後,沿用 `_need_src`、`GRAPHCTL` 相對路徑、`sec` 切節法,以及 `check("S6:…")` 與結尾 `print("  ✓ …")`。
  - file: `scripts/test_lumos.py:120045-120067`
  - 沒有維護測試清單,測試靠 `t_` 前綴被發現,跟鄰居一致。

## 2. 命名與錯誤處理:大致對齊,有三處 minor

對齊的部分:
- 程式註解沿用「Measured …」英文前綴和換行寫法。
  - file: `scripts/test_quality.py:121`
- 測試命名 `test_<對象>_is/are_(not_)attributed` 跟既有 `test_android_native_assertion_without_type_is_attributed`、`test_xunit_generic_logger_assertion_is_attributed` 是同一形狀。
  - file: `scripts/test_test_quality_cli.py:189-230`
  - 正反例成對,有反例守住「訊息只提到型別名」,跟 `test_runtime_exception_mentioning_xunit_message_not_assertion` 一樣。
- 筆記的 PITFALL 帶齊 `[出處:] [根因:] [防回歸:]`,後面接補充句,跟「原生 reporter 抹掉型別」那條同形。
  - file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:38,40`
- 日期小節沿用既有的「2026-11-01 Android 本機單元測試節」,只加一條 bullet,沒有另開小節。

不對齊的條目:

**(a) 測試 fixture 的寫法**

鄰居的 junit 測試都是單一 `b'<testsuite>…'` 字面量加一個斷言,檔內其他測試方法裡沒有註解(整檔只有第 1 行的 shebang)。新測試有三點不同:
- 用 `for` 迴圈跑多組 fixture。
- 用 `%` 格式化加 `.encode()` 組 XML(Truth 型別那支)。
- 用 `text.replace(b"<", b"&lt;").replace(b">", b"&gt;")` 現場跳脫(裝置兩支),並在各測試內加了中文註解。

結構仍是同一個 `junit()` 入口,但組 fixture 的方式是檔內原本沒有的。
- file: `scripts/test_test_quality_cli.py:232-282`
- 對照: `scripts/test_test_quality_cli.py:189-230`

引句:「rows = junit(b'<testsuite><testcase name="x"><failure>' + text.replace(b"<", b"&lt;").replace(b">", b"&gt;") + b"</failure></testcase></testsuite>")」
severity: minor

**(b) 筆記小節少了綁定測試的句尾**

三個兄弟小節(前端、Room、Android 本機單元)的 bullet 都以「綁的測試 `t_…`」收尾。新增的那條演練 bullet 沒有,但它對應的守衛測試 `t_test_quality_standard_android_drill_lessons` 已經存在。
- file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md`(2026-11-01 小節,新增那條 bullet)

引句:「實機演練(2026-11-01,[[Projects/Android單元測試標準實機演練_計劃]])之後,同一節補了」
severity: minor

**(c) 標準文件的引用格式**

這一節原本的慣例是:官方條目集中列在末尾的「來源(核對當天看到的更新日期)」,非官方的標「社群:」。新增的協程 bullet 把 kotlinx-coroutines-test 的連結直接寫在正文,也沒進末尾的帶日期來源清單。它用的出處標記是「演練實測」,是這節原本沒有的第三種。
- file: `skills/lumos-project-notes/commands/test-quality-standard.md`(〈怎麼寫才算數〉的協程第三條,「儀器測試不換 Main 時」那一條)

引句:「([kotlinx-coroutines-test 說明](https://github.com/Kotlin/kotlinx.coroutines/blob/master/kotlinx-coroutines-test/README.md):`Dispatchers.Default` 不走虛擬時間;演練實測)」
severity: minor

## 3. 第二種做法:沒有

- 辨識斷言:沿用 `kind` 精確比對加既有的 `re.fullmatch`/`re.search` 結構,沒有新機制。裝置那路仍是「JUnit `Assert` 堆疊」加第一行型別,只是把 `startswith` 換成 `fullmatch`。
- 讀 XML:沒有新讀法,仍用 `itertext()`。
- 工具函式:沒有自創函式。
- 指紋表:見第 1 問,做法同 c70b3d6af。
- 標準守衛測試:寫法同 `t_test_quality_standard_android_unit_section`。
- 驗證紀錄:Verification 筆記的 frontmatter 欄位(`valid_under`、`revalidate_when`、`plan_refs`)跟 `測試品質第四輪修補驗證.md` 同形。沒有 `self_audit` 欄位,但抽查的 2026-10-20 至 21 的幾篇驗證紀錄同樣沒有,不算不對齊。

我還看到「Measured device text (2026-11-01)」多帶了日期,鄰居的 Measured 註解沒有。這太小,沒列為條目。

不對齊共 3 條,其中 major 0 條
