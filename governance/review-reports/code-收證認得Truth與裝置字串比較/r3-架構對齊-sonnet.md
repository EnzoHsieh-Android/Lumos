severity: minor

**1. 分層與依賴方向:對齊。**
- 行為碼只動 `assertion_failure` 一個函式,沒有新函式、新模組或新依賴。
  - file: `scripts/test_quality.py:108-139`
  - 只改了第 115-117 行的註解和第 134 行的 `frame` 正則(`[\w$.]+` 改成 `[^\n(]+`)。
- 指紋表同步更新。
  - 我重算修後 `scripts/test_quality.py` 的 sha256,是 `5662b3e9…8185f`,和 `scripts/lumos:69694` 的 `_TEST_QUALITY_BUNDLE_DIGESTS` 一致。
  - 這是專案原有的「改收證工具就更新配套指紋」做法。
- 守衛測試沒有跨層。
  - `t_test_quality_drill_cli_cases_present` 照鄰居寫法,用 `_need_src` 加 `Path(GRAPHCTL).resolve().parent` 讀同層的 `scripts/test_test_quality_cli.py`。
  - file: `scripts/test_lumos.py:120109-120125`
- 新增反例都放進既有測試的元組,沒另開測試。
  - file: `scripts/test_test_quality_cli.py:351-360`、`:315-337`

**2. 命名與錯誤處理:大致對齊,一條不對齊。**
- 測試名前綴已對齊。
  - `t_secev_tq_*` 在 `t_secev_` 家族裡有主題式先例(`t_secev_baseline_sound`、`t_secev_cli_subcommands_parse`、`t_secev_reason_codes_match_plan`)。
  - `t_test_quality_drill_cli_cases_present` 跟 `t_test_quality_standard_android_drill_lessons` 同家族。
  - file: `scripts/test_lumos.py:114399`、`:114417`、`:120109`、`:120127`
  - 舊名 `t_drill_*`、`t_secev_drill_*` 在整個 repo 已無殘留,S5 的四個 `[test:]` 綁定也同步改了。
  - ⚠ `tq` 縮寫在 repo 裡沒有第二例,我判為可接受,不計入。
- 程式註解已補陣列比較的出處。
  - 引句:「Measured Truth 1.0.1 and JUnit 4.13.2 array-compare local JVM type」
  - 這和同函式「Measured Node reporter cause」的寫法一致。
  - file: `scripts/test_quality.py:115-117`
- REVISIT 格式對齊。
  - 計劃檔、驗證紀錄都用獨立一行的 `REVISIT:YYYY-MM-DD 一句要做什麼`。
  - 同類寫法見 `Projects/審查席唯讀隔離_計劃.md` 和 `Projects/推播miss量測_計劃.md`,驗證紀錄也有先例(例如 `Verification/2026-09-11_推播漏網量測實作.md:77`)。
  - 同日期的回頭條件在計劃檔與驗證紀錄各有一份,措辭不同,repo 裡有同日期重複的先例。
  - file: `Projects/Android單元測試標準實機演練_計劃.md:82-87`、`Verification/2026-11-01_Android單元測試標準實機演練.md:68,92,96`
- 不對齊:承認風險的散文還有一部分沒配對。
  - 計劃檔 `實務隱患` 的「金流」那條仍寫「這次沒有看平板的網路流量」,且沒有回頭條件的指向。
  - 同一檔緊鄰的「對外送出」那條已改成「(回頭條件見做法節末尾)」。
  - 驗證紀錄的 `外推邊界` 兩條(「打錯類名時誰擋,這次沒演」、「只量過 Truth 1.0.1…原生 runner 這次沒重跑」)旁邊沒有 REVISIT,但同篇其他三條都有。
  - 引句:「這次沒有看平板的網路流量,沒有證據顯示演練期間有付款相關請求。」
  - file: `Projects/Android單元測試標準實機演練_計劃.md:112` 對照 `:113`
  - file: `Verification/2026-11-01_Android單元測試標準實機演練.md:89`
  - 結構是對的(REVISIT 都在),只是同一輪修補裡有的配了、有的沒配。
severity: minor

**3. 第二種做法:現在算有明文的既有做法變體,不判 major。**
- 「公開放去識別化摘要、完整卷證留考場本機」已寫成有條件的 WHY,放在收證工具的家。
  - 引句:「公開 repo 只放去識別化摘要(代稱、子套件攤平、不放原始碼與收據快照)」
  - file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:19`
  - 欄位齊:`[出處:]`、`[因:]`、`[不選:]`、`[代價:]`、`[applies:]`,符合 CLAUDE.md〈寫筆記時〉的 WHY 欄位表。
  - `applies` 把變體限在「考場是私有專案」,「自建合成專案」仍照原本全放公開 repo 的做法,所以是原做法的條件分支,不是平行的第二套。
- 因由有對上 repo 既有的規則。
  - 「此 repo 公開:推東西前確認無公司識別資訊」在 repo 裡有明文。
- 計劃檔 `卷證放哪` 一節有撤除條件。
  - 引句:「RETIRE-IF: 工具鏈有了可以放私有卷證的地方(私有 repo 或加密卷證)」
  - 格式 `[retire:人裁] [until:2027-11-01]` 與同檔第 51 行的 RETIRE-IF 一致。
  - file: `Projects/Android單元測試標準實機演練_計劃.md:91-92`
- 這一節標題仍自稱「這次新增的做法」。我認為這是照實說明,不是矛盾。
- ⚠ 我只看到這個變體寫在計劃檔和收證工具的家兩處,`skills/lumos-project-notes/commands/test-quality-standard.md` 沒提。下一次照標準做的私有考場演練未必會讀到,這不影響這次的對齊判斷,交編排者看要不要補。

**修補三問**
- ① 上輪四項不一致:
  - 測試名前綴已改齊。
  - 程式註解已補陣列比較的出處。
  - 回頭條件已改成獨立的 REVISIT 行,但上面那條散文沒配對,仍有一處殘留。
  - 第二種歸檔做法已有明文 WHY,並限定適用條件。
- ② 既有寫法沒有被弄亂。
  - 指紋表與檔案一致。
  - 舊測試名沒有殘留。
  - `[test:]` 綁定同步。
  - 新增反例沿用既有元組。
  - REVISIT 從「卷證放哪」節移到「做法」節尾,沒有重複或遺漏。
- ③ 新發現:
  - 修前:Verification 的 `App 啟動路徑` 與計劃的「對外送出」只有散文承認「沒看流量」,沒有回頭條件指向。
  - 修後:這兩處補上了,但「金流」那條和 `外推邊界` 兩條沒有同步補。
  - 另有一個與對齊無關的筆誤:「從從第一個堆疊行起」重複了「從」。
    - file: `Systems/test-quality-cli.md:41`
    - file: `Verification/2026-11-01_Android單元測試標準實機演練.md:78`
  - 這不計入。

不對齊共 1 條,其中 major 0 條
