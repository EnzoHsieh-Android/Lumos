severity: major

**第 1 問 分層與依賴方向:對齊**
- 斷言歸因的新判斷放在 `assertion_failure` 裡,位置跟既有的各框架分支一樣。Truth 的兩個型別用精確比對,跟 NUnit 的 `==` 同一種寫法。 file: `scripts/test_quality.py:112-136`
- 配套指紋表只換了 `test_quality.py` 那一格的 sha256,沿用既有機制。 file: `scripts/lumos:69701`
- 安全證據閘沒有另寫一套歸因。它從 `_secev_junit_facts` 讀報告,跟收證用同一個 `junit()`,所以沒有跨層直呼,也沒有長出第二份判定。 file: `scripts/lumos:8828-8843`
- 測試狀態的做法跟鄰居一致:`_sg_junit` 裡 `failure_rt` 旁邊加了一個 `failure_truth`,沒有另開一套假資料。 file: `scripts/test_lumos.py:113855-113856`
- 新守衛 `t_secev_fault_truth_assertion_counts_like_assertion` 拿 `failure_truth` 跟一般 `failure` 比判定,結構跟 `t_secev_s07_fault_not_real_detection` 同一型。 file: `scripts/test_lumos.py:114371-114382`
- 標準守衛 `t_test_quality_standard_android_drill_lessons` 沿用 `t_test_quality_standard_android_unit_section` 的讀法:`_need_src`、截出該節、用 `check` 逐條比對。 file: `scripts/test_lumos.py:120066-120088`

**第 2 問 命名、註解、PITFALL 與小節格式、卷證**
- 註解和 PITFALL 格式對齊。
  - 註解用英文 `Measured …`,跟既有的 `Measured Node reporter cause` 同一寫法。 file: `scripts/test_quality.py:115,121,130`
  - 新 PITFALL 補齊了出處、根因、防回歸三格,位置在同族那條「原生 reporter 抹掉型別」的緊鄰下方,還點明「這是上一條的同族」。 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:38,40`
  - 測試名 `test_..._is_attributed` 和 `..._is_not_attributed` 跟 `test_xunit_generic_logger_assertion_is_attributed` 同一命名。 file: `scripts/test_test_quality_cli.py:189,221,229-302`
- 日期小節也對齊。「實機演練」那條補在同一天的 Android 本機單元測試節裡,內文自帶演練計劃的連結,沒有另開節。 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:81-84`
- 卷證的分法跟前例不同。
  - 上一次(`test-quality-three-platforms-20261008`)的做法是:完整卷證全放進公開 repo,共 731 個檔。每個平台、每個階段各有 `receipt.json`、`report.xml`、`snapshot-N.txt`、原始 log,另有可重放的腳本(附成 `.txt`)和覆蓋全部檔案的 `manifest.json`。 file: `governance/eval/results/test-quality-three-platforms-20261008/README.md:3`
  - 它的「實機專案放外面」只有重跑環境在 `/Users/enzo/lumos-test-quality-lab-20261008`,歸檔本身是完整的。 file: `governance/eval/results/test-quality-three-platforms-20261008/README.md:3`
  - 這次公開的只有 21 個檔,是去識別化摘要,檔案是 `fault-checks/`、`bad-test-checks/`、`fault-matrix-*.json`、`controls.json`,沒有收據、快照、原始報告和 patch。 file: `governance/eval/results/android-unit-standard-drill-20261101/README.md`
  - 公開這份摘要自己承認「不能單獨重跑 `lumos test-quality check`」。完整卷證在考場私有 repo 的本機分支,不推。 file: `governance/eval/results/android-unit-standard-drill-20261101/README.md:3`
- 我在 `docs/`、`governance/eval/results/` 裡找不到「公開去識別化摘要加本機完整卷證」的前例。
  - `去識別` 在 `governance/MAPPING.json:2` 是盲審編碼對照表,在 `Systems/retrieval-ranking.md:91` 是 goldset 洗牌,兩者都不是卷證歸檔。
  - 這是第二種卷證做法,見下面第 3 問。
- 驗證紀錄的 manifest 風格、前言欄位、`revalidate_when` 都跟前例一致。

不對齊條目:

引句:「卷證分兩處:公開的工具鏈只放去識別化摘要」
- 這是第 3 問那條第二種做法在卷證格式上的呈現,這裡不重複計數。
- 另外,新卷證目錄的檔名帶中文,例如 `fault-checks/M1-排序號加1.json`、`bad-test-checks/b1_…--M7-新增欄位對調.json`。前兩個卷證目錄的檔名都是純 ASCII(我查過 `git ls-files`,非 ASCII 檔名為零)。 file: `governance/eval/results/android-unit-standard-drill-20261101/fault-checks/`
severity: minor

引句:「t_secev_fault_truth_assertion_counts_like_assertion」
- 同一組 `t_secev_` 測試的名稱都帶流水號前綴,如 `t_secev_s07_…`、`t_secev_r1_…`。 file: `scripts/test_lumos.py:117072`
- 新守衛沒有這個前綴。
- 它的 `check` 標籤寫成 `S5:`,取的是演練計劃的條款編號。但同組鄰居的 `S7` 指的是安全證據閘計劃的條款,同一前綴下容易讀成同一份編號。 file: `scripts/test_lumos.py:114399-114414`
severity: minor

**第 3 問 第二種做法:有一個**
- 引入的是「卷證只公開去識別化摘要、完整可重跑卷證只留考場私有 repo 的本機分支」。
  - 用這種做法的原因是 Enzo 2026-11-01 的裁示:工具鏈 repo 公開,考場是公司私有 repo。理由成立,但它仍然是專案原本沒有的歸檔做法。
  - 後果是 S1、S2、S4 的 `[manual:]` 驗收條款,讀者在公開 repo 裡只看得到摘要,重跑不了。
  - 計劃裡這件事只是一行做法敘述,沒有訂「什麼情況適用這個分法」和「日後怎麼收斂成唯一做法」,所以下次演練無從判斷該走哪一種。 file: `docs/lumos-toolchain-knowledge/Projects/Android單元測試標準實機演練_計劃.md:78`
  - ⚠ 交編排者:這條判 major,是依「引入第二種做法」這條錨。使用者的裁示解釋了為什麼這樣做,但沒改變它是第二種做法。折法有兩條:一是把它升成有適用條件的 WHY,二是寫一行 `RETIRE-IF`。
引句:「卷證分兩處:公開的工具鏈只放去識別化摘要」
severity: major
- 其餘沒有新增做法。歸因擴充、指紋表、守衛測試、標準補條文都沿用既有機制。

**第 4 問 落點:合理,不用另開**
- `Systems/test-quality-cli` 的負責範圍同時涵蓋收證歸因和「測試品質接入標準的各棧補充」。 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:6`
- 它的 `about_code` 已列 `test_quality.py`、`test_test_quality_cli.py`、`scripts/lumos`。 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:9-12`
- 同一篇早已放了前端節、Room 節、Android 本機單元測試節三個兄弟小節,以及「給安全證據閘用的讀法」。因此歸因 PITFALL 和標準補條文都該寫在這篇,另開一篇會把同族拆散。
- 安全證據閘的判定結果變化,也由「給安全證據閘用的讀法」這種寫法承接。`Systems/安全證據閘` 對「非斷言失敗是 invalid」的描述語意沒變,不必動。 file: `docs/lumos-toolchain-knowledge/Systems/安全證據閘.md`
- 演練的結果和對照表落在 `Verification/2026-11-01_Android單元測試標準實機演練`,不屬於 `lands_in` 的「現況」,位置對。

不對齊共 3 條,其中 major 1 條
