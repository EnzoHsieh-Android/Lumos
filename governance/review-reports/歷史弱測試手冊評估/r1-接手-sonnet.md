severity: major

我跑了兩個入口:`historical_test_quality.py` 約 8 秒,`preflight_passed` 為 true;`historical_case_corpus.py` 約 20 秒,12 組全部 `qualified=True`。我另外跑了 `historical_handbook_trial.py --controls`,八個控制全過。manifest 與 v2 卷證逐欄相同,只有 `runner_sha256` 不比對。spec 裡的提交編號、斷言數(4/4、8/12、5/8)、2 秒 alarm、15 秒逾時都和程式常數一致,`d92e4ae5`、`631d7e3b`、`2e261846` 都存在。問題出在重跑模型臂、判斷哪一案該退場、新增案例這幾處。

ID: HND-1
severity: major
blocking: 是
引句:「handbook 強制提供正式共用手冊〈實作測試品質〉全文」
審材外佐證 file: `governance/eval/historical_handbook_trial.py:266`
審材外佐證 file: `governance/eval/historical_handbook_trial.py:267`
審材外佐證 file: `governance/review-reports/test-quality-historical-model-trial/manifest.json`
問題與判準:
- handbook 臂每次執行都現讀 `skills/lumos-project-notes/commands/03-寫回圖譜.md`,用字串 `**測試必須有獨立的判準` 當錨點切出來,沒有讀凍結快照。
- 我實測:2026-10-07 試行存在 manifest 裡的手冊是 1129 字,現行 repo 切出來是 1234 字,SHA 前 16 碼 `afcdd0c5…` 對 `a11758c3…`,內容已經不同。
- 三個月後的人照 spec 重跑 handbook 臂,拿到的不是原實驗處理。spec 要求「來源／手冊／執行器快照 manifest」,但沒有任何程式路徑能把 manifest 裡的手冊餵回去。
- 手冊若改標題或錨點句,`split(...)[1]` 會 IndexError。
- 內文只要出現 `### ` 子標題,`split('## ')` 也會把手冊截斷,因為 `### ` 裡含有 `## `。
- 判準:spec 沒說手冊臂的來源是活檔、不可重現,也沒給「從 manifest 還原手冊」的辦法。

ID: HND-2
severity: major
blocking: 是
引句:「任一組合無法重播、強錯版失敗理由超出固定目標、正常基準紅或環境錯，該案不進模型效果分母」
審材外佐證 file: `governance/eval/historical_case_corpus.py:98`
審材外佐證 file: `governance/eval/historical_case_corpus.py:105`
審材外佐證 file: `governance/eval/historical_test_quality.py:99`
審材外佐證 file: `governance/eval/historical_test_quality.py:103`
問題與判準:
- 「失敗理由超出固定目標」在 corpus 入口看不到。資格只比 `len(checks)` 與 `failed == expected`(失敗索引),不比斷言標籤,也不比 detail 文字。
- 同一個鎖案例在 `historical_test_quality.py` 會驗目標標籤和「巢狀拿同一把鎖卡住了」。到了 corpus 入口這兩項檢查消失,所以同索引、不同原因的紅燈也會被判 qualified。
- 「該案不進分母」沒有機器輸出。`summary.json` 只有全域 `controls_passed`;`effect_candidates` 是照 `CASES` 角色靜態列出,不看是否 qualified。
- 首批失敗的卷證 `test-quality-historical-corpus-preflight/summary.json` 就是 `controls_passed: False`,但 `effect_candidates` 仍照列兩案。
- 所以這條 RETIRE-IF 只能靠人讀 12 列 `qualified` 來判,spec 沒講。接手者看 `effect_candidates` 就會把已失格的案算進分母。
- 判準:退場條件要有逐案可觀測的輸出。

ID: HND-3
severity: minor
blocking: 否
引句:「[manual:執行固定入口並核對四組明細]」
審材外佐證 file: `governance/eval/test-quality/README.md:45`
審材外佐證 file: `governance/eval/historical_test_quality.py:81`
審材外佐證 file: `governance/eval/historical_case_corpus.py:13`
問題與判準:
- S1、S2、S3 三條 `[manual:]` 都寫「執行固定入口」「執行 corpus 入口」,沒給路徑,也沒給 `--out`。入口與指令只在 Systems 筆記的 `repro:` 和 README 裡。
- 前置條件 spec 完全沒提:
  - 完整本地 git 歷史(淺層 clone 會在 `git show` 丟 `CalledProcessError`)。
  - POSIX 與 SIGALRM。
  - `--out` 必須是不存在的新目錄(`exist_ok=False`)。
  - Java 案例依賴 `governance/review-reports/code-java補棧/r1-snapshot.patch`,而這個路徑在程式裡寫死。
- repo 內沒有任何測試綁這三支腳本。我搜了 `scripts/` 和 `governance/eval/*.py`,只有它們自己互相引用,所以入口壞了沒有機械訊號。
- 判準:`[manual:]` 條款至少要寫出可複製的命令與前置條件。

ID: HND-4
severity: minor
blocking: 否
引句:「證據應保存完整歷史來源提交、檔案與測試片段 SHA、執行器 SHA、原始輸出和逾時調整」
審材外佐證 file: `governance/review-reports/test-quality-historical-lock-preflight-v2/report.json:8`
審材外佐證 file: `governance/review-reports/test-quality-historical-lock-preflight-v2/instrument-disposal.md:1`
審材外佐證 file: `governance/eval/historical_test_quality.py:106`
問題與判準:
- 鎖 v2 卷證的 `runner_sha256` 是 `9d8b0dee…`,對應提交 `6adb9bf1`。
- 現行 `historical_test_quality.py` 在 `fab5309c` 加了 `method` 參數和 `_load_lumos` 別名,SHA 變成 `9d3886d2…`。
- `instrument-disposal.md` 仍寫「v2 對應已提交入口」,現在已經不成立。
- 接手者照 S2 重跑後比對執行器 SHA 會對不上,卻沒有任何文字說明是哪個提交造成的。
- 模型試行也有同樣問題:兩批 runner 的 SHA 是 `055f6d08…`(有快照檔)和 `cb605cc1…`(對應 `b1af81a9`),現行是 `7d7cd835…`(`598e41b2` 重構後)。
- `instrument` 欄是寫死的字串,不是從實際替換結果算出來的(程式只 assert 了 `_sig.alarm(8)` 出現一次)。
- 判準:S2 應寫明「卷證 SHA 對應哪個提交」,或證據目錄要附 runner 快照。

ID: HND-5
severity: minor
blocking: 否
引句:「Java弱8／強12斷言，強錯版預期第9–12條失敗」
審材外佐證 file: `governance/eval/historical_case_corpus.py:21`
審材外佐證 file: `governance/eval/historical_case_corpus.py:19`
問題與判準:
- spec 和 Verification 都用 1 起算的「第 N 條」。程式 `failed_indices` 是 0 起算(Java `[8,9,10,11]`、圍欄 `[5,6]`、鎖 `[3]`),而且 `enumerate(checks)` 直接比對。
- spec 沒標明是 0 起算。接手者照 spec 的「第 9–12 條」填新案例,會全部差一。
- 判準:S3 的「預定失敗索引」要寫明起算基準。

ID: HND-6
severity: minor
blocking: 否
引句:「固定三案的原弱、強測試及提交／快照，先寫manifest才執行12個組合」
審材外佐證 file: `governance/eval/historical_case_corpus.py:28`
審材外佐證 file: `governance/eval/historical_case_corpus.py:53`
審材外佐證 file: `governance/eval/historical_case_corpus.py:89`
審材外佐證 file: `governance/eval/historical_case_corpus.py:93`
審材外佐證 file: `governance/eval/historical_case_corpus.py:106`
問題與判準:
- spec 和 Systems 筆記都沒告訴接手者新增案例要改哪幾處。實際要同時改:
  - `CASES`(method、weak_checks、strong_checks、failed_indices)。
  - `load_materials()`(每案的 provenance 手寫)。
  - 第 89 行的 `case['id']=='lock-reentrancy'` 才縮 alarm。
  - 第 93 行的 `!= 'java-discovery'` 才免 `★前置★` 標籤。
  - 第 106 行寫死 `retired_effect_control: 'lock-reentrancy'`。
- `commit_files()` 用 `JAVA_BLOBS` 的鍵當要取的檔案清單,名字像 Java 專用,其實所有案例共用。
- 判準:這些寫死的例外會讓新案例失敗,方向是 fail-closed,所以只算 minor。但 spec 該列出擴充點。

ID: HND-7
severity: minor
blocking: 否
引句:「固定案例集應保留提交或快照來源、各檔SHA、原／實跑測試SHA、12組原始結果及預定失敗索引」
審材外佐證 file: `governance/eval/historical_case_corpus.py:94`
審材外佐證 file: `governance/eval/historical_case_corpus.py:74`
審材外佐證 file: `governance/eval/historical_test_quality.py:107`
問題與判準:
- corpus 輸出沒有「原測試 SHA」。`manifest.json` 沒有測試 SHA,`results.json` 每列只有實跑版 `test_sha256`。
- 原測試只存在 `test-materials.json` 的全文裡,接手者要自己重算。
- 單案入口 `historical_test_quality.py` 反而有 `original_test_sha256`。兩個入口對 S2、S3 的要求落差不一致。

ID: HND-8
severity: minor
blocking: 否
引句:「後續正常需求／執行介面／首次生成協議另凍結，計劃doing」
審材外佐證 file: `docs/lumos-toolchain-knowledge/Verification/2026-10-07_不同失效歷史案例集資格重播.md:49`
問題與判準:
- 計劃最末段只用散文說「另凍結」,沒有 REVISIT,也沒有「完成了就把狀態改成什麼」的條件。
- 2026-11-07 的回頭條件只存在 Verification 筆記裡。
- 第 28 行已關閉的 REVISIT 寫「後續固定案例集入口見本次模型驗證紀錄」,「本次」指哪一篇讀不出來。
- 判準:純散文的回頭條件沒人會回頭。

實務隱患逐類答:
- 金流:已讀,無 finding。入口只重播本機歷史測試,沒有收款或交易路徑。
- 對外送出:已讀,無 finding。重播不連網;模型臂只送取鎖函式、手冊和題目。手冊內容漂移的問題記在 HND-1,與對外送出無關。
- 不可逆:已讀,無 finding。重播時 HOME、TMPDIR 都指向 `tempfile` 目錄,結束自動清除。`--out` 目錄由使用者指定且必須是新目錄。
- 守衛面:已讀,無 finding。入口只驗考卷,不碰提交、推送、權限等正式守衛。

總結最嚴重 severity: major;blocking 共 2 條
