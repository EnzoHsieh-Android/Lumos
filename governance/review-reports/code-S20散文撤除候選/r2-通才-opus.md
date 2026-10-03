severity: major

# code-S20散文撤除候選 r2 通才席(opus)報告

看了什麼:r2-delta.patch 全部 161 行(scripts/lumos 三個 hunk、scripts/test_lumos.py 一個 hunk),對照 r2-snapshot.patch 的筆記改動(漂移防治路線圖_計劃、筆記測試綁定要存在_計劃、Systems/lumos-cli-read 的 PITFALL 行)與 r1-intake.md。實驗都在 `git clone --shared` 出來的臨時目錄跑(repo 本身沒動),用 python3.14 直接載入 scripts/lumos 呼叫 `_ns_tr_says_retire`,並把 r1 版判法(20 字前綴、只看第一個裁定、沒切段)寫成對照函式一起跑;測試只跑 `-k prose_retire_by_verdict_verb`。

## F1 修法把「裁定」到冒號之間的字、以及第一個裁定之前的字整段丟掉,r1 抓得到的撤除現在漏列
severity: major
blocking: 是
引句:「seg = ln[m.end():ms[k + 1].start() if k + 1 < len(ms) else len(ln)]」
file: `scripts/lumos:28952`(`_NS_TR_VERDICT_RE` 前綴放寬到 60 字)
file: `scripts/lumos:29392`(段落從 `m.end()` 起算)

1. 一句白話:這版只要一行裡出現「裁定」且 60 字內有冒號,就只看冒號後面那段;冒號前面(包括「裁定」與冒號之間)講的撤除完全不看。r1 那版遇到「裁定後面不是改寫/保留」會退回整行判,所以抓得到;這版拿掉了退路,是這輪修正自己造成的漏判。
2. 輸入 A(很常見的寫法,動詞直接黏在裁定後、後面帶理由冒號):`  - 2026-10-01 代使用者裁定撤除這條,理由:展示批次改版後流程不再需要`。正則把「裁定撤除這條,理由:」當前綴吃掉,段落只剩「展示批次改版後流程不再需要」,沒有「撤除」→ 第 29393 行條件不成立 → 回 False。r1 版回 True。
3. 輸入 B(撤除寫在裁定之前):`  - 撤除這條(使用者裁定,見 https://example.com/x)`。正則把「裁定,見 https:」當前綴,段落是「//example.com/x)」,前面的「撤除這條」不在任何段裡 → False。r1 版回 True。
4. 同形狀的其他輸入(實測皆 r2=False、r1=True):`代使用者裁定撤除舊測試,改綁 [test:t_new]`(`[test:` 的冒號被當成裁定冒號,而 rtb 回傳正好說「原掛的測試搬到撤除說明行」,說明行帶 `[test:` 是真實形狀);`這條撤除了;待裁定 10:30 會議`(時間的冒號)。
5. 為什麼要緊:筆記測試綁定要存在_計劃自己寫明散文撤除「規則擋不到,只會進 doctor 候選」——這張候選表是散文撤除唯一的網,漏列就是安靜放過一條還掛活測試的已撤條款。
6. 最小重現(當場翻紅):在 `t_doctor_s20_prose_retire_by_verdict_verb` 的 cases 加兩條
   `("R1裁定撤除後面跟理由冒號", "- [S1] 當 x 時應 y [test:test_alive]\n  - 代使用者裁定撤除這條,理由:展示批次改版後流程不再需要", True)`、
   `("R2撤除在裁定之前", "- [S1] 當 x 時應 y [test:test_alive]\n  - 撤除這條(使用者裁定,見 https://example.com/x)", True)`,
   跑 `python3.14 scripts/test_lumos.py -k prose_retire_by_verdict_verb` → `✗ R1裁定撤除後面跟理由冒號:列  []`、`✗ R2撤除在裁定之前:列  []`,14 passed, 2 failed。
7. 修法建議(一條統一規則,不逐點補):只把「段首是改寫、改為、改成、保留、維持」的那些段(從那個裁定的 `m.start()` 到段尾)從整行挖掉,剩下的文字(第一個裁定之前、非豁免段、前綴裡的字)照舊用「有撤除、沒保留」判。手算過:⑤⑥⑦ 現有案例結果不變,A、B 會回 True。
8. 圖譜:Systems/lumos-cli-read 的 PITFALL 行與兩篇計劃都寫「每個『裁定…:』各切一段」,沒寫「裁定之前與前綴裡的字不看」這個副作用;修完若保留任何「不看」的範圍要寫進那行。

## F2 「保留」只做子字串比對、動作詞只認段首原字,兩個方向各有誤判
severity: minor
blocking: 否
引句:「and "撤除" in seg and "保留" not in seg:」
file: `scripts/lumos:29393`

1. 漏判:「保留」出現在別的詞裡也會否決整段。`  - 裁定:撤除,不保留舊測試`、`  - 裁定:撤除整條條款(保留字不受影響)` → 都回 False,但兩句都是在講撤除。
2. 誤判:動作詞前面多一個字或符號就認不得。`  - 裁定:已改寫,舊守衛撤除`、`  - 裁定:**改寫**:舊守衛撤除`(Markdown 粗體)、`  - 裁定:(改寫)舊守衛撤除` → 都回 True,跟 ①「裁定:改寫:舊守衛撤除」同一種意思卻被列。
3. 這兩種 r1 就有(對照函式同結果),不是本輪引入,但本輪把「保留」否決搬進每段判、把引號剝除做成段首正規化,正是收斂這類變體的位置;段首可順手剝掉 `*`、`(`、`(` 與「已/將」,「保留」改成前面不是「不」才算。
4. 已確認沒問題的:段首全形空白(U+3000)`str.lstrip()` 會剝掉,`裁定:　改寫,舊守衛撤除` 正確回 False。

## F3 新測試有兩處空轉:空行釘與三個動作詞拿掉照綠
severity: minor
blocking: 否
引句:「("⑧空行之後的說明不算下一層", "- [S1] 當 x 時應 y [test:test_alive]\n\n  - 這條撤除了", False),」
file: `scripts/lumos:29402`
file: `scripts/test_lumos.py:65493`

1. 空行釘空轉:把 `_ns_tr_sub_says_retire` 的 `not ln.strip() or` 拿掉(只留縮排比較),清 `__pycache__` 後跑 → 14 passed, 0 failed。原因:案例用的是真正的空字串行,縮排 0 ≤ 條款行縮排 0,本來就會因縮排條件停下;`not ln.strip()` 只對「只有空白字元的行」(例如兩個空格)有作用,而那種行沒有案例。docstring 新寫的「遇到空行就停」因此沒有任何測試守。要釘就把空行寫成 `"\n  \n"`(只有空白)。
2. 動作詞表只釘了兩個:把 `_NS_TR_KEEP_VERBS` 改成只剩 `("改寫", "改為")` → 14 passed, 0 failed。「改成」「維持」沒有案例;「保留」在動作詞表裡是多餘的(段裡有「保留」本來就被第 29393 行的 `"保留" not in seg` 否決),拿掉它行為不變。
3. 有殺傷力的部分也驗過:前綴改回 20 字 → ⑤紅;加 `ms = ms[:1]`(只看第一個裁定)→ ⑥紅;docstring 說的翻紅釘成立。
4. 對照固定席 Systems/測試假綠形態 的 ★INVARIANT★(還原修法測試要翻紅):第 1 點就是「現場走不到被測分支」那一型。

## 圖譜鏡頭(固定席分組摘要)
- Systems/lumos-cli-read(家,★INVARIANT★ search 排除 superseded):這輪改的是 doctor S20,不碰 search 的濾網,INVARIANT 不受影響;同節點新寫的 PITFALL 行描述與 r2 程式一致,但沒提 F1 的副作用(見 F1 第 8 點)。
- Systems/測試假綠形態(★INVARIANT★):F3 第 1 點正好是它定義的空轉型。
- Systems/design-loop(★INVARIANT★ 設計審處置閘)、Systems/pitfalls-code-loop、Systems/loop-convergence-recording、Issues/code-loop守衛main-direct盲區:講的是審查迴圈與記帳,這次差異沒碰到那些路徑,不適用。
- Systems/每支檔有家、Systems/筆記內容閘:改到的兩支檔都有家(scripts/lumos、scripts/test_lumos.py),脈絡寫回 lumos-cli-read 與兩篇計劃,沒看到新的無家檔或帶行號引用的新行。
- 其餘「超出上限只列名」節點未逐篇讀。

最高等級:major,blocking 共 1 條
