severity: minor

### F1 頂層測試資料夾的副檔名比對沒有正規化大小寫,和 `_testmap_ext` 既有慣例不一致
severity: minor
blocking: 否 — 失效方向是「照舊要家」(安全方向,不會放行真程式檔),只是重新製造出這次要修的同一種誤擋,機率低
引句:「ext = "." + name.rsplit(".", 1)[1] if "." in name.lstrip(".") else ""」
1. `_nodehome_in_stack_test_dir` 自己算 `ext` 時沒有 `.lower()`;同檔案裡既有的 `_testmap_ext`(給同一組副檔名判定用)明文 `.lower()`。實測:`_nodehome_is_test("PosTerminalTests/Fixture.swift", {"PosTerminal","PosTerminalTests"})` 回 `True`,但只把副檔名改大小寫 `Fixture.SWIFT` 或 `Fixture.Swift`,同一支檔在同一個合法測試資料夾裡就回 `False`(見下方重現)——錨定的兩個條件(同名資料夾、棧的副檔名)都滿足,只因為大小寫沒過,就變回「這支檔要家」,是這次要修的同一種誤擋在窄範圍裡復發。
2. 實務發生率低(Xcode/`.NET` 慣例都是小寫副檔名),但 macOS/Windows 的大小寫不敏感檔案系統讓這種檔名不無可能出現而不會被人注意到。
3. 修法很輕:`ext` 那行照 `_testmap_ext` 加 `.lower()` 即可,兩處判定就會一致。

重現(在 `/tmp` 私有副本 in-process 載入,不動 repo):
```
python3 -c "
import importlib.machinery, importlib.util
l=importlib.machinery.SourceFileLoader('m','scripts/lumos'); s=importlib.util.spec_from_loader('m',l)
m=importlib.util.module_from_spec(s); l.exec_module(m)
td={'PosTerminal','PosTerminalTests'}
print(m._nodehome_is_test('PosTerminalTests/Fixture.swift', td))   # True
print(m._nodehome_is_test('PosTerminalTests/Fixture.SWIFT', td))   # False——同一支檔只差副檔名大小寫
"
```
輸出:`True` / `False`(已在暫存副本實跑驗證)。

佐證:
file: `scripts/lumos:17816` `_nodehome_in_stack_test_dir` 自己抽副檔名,沒呼叫既有的 `_testmap_ext`、也沒 `.lower()`
file: `scripts/lumos:19862-19865` `_testmap_ext` 明文 `.lower()` 正規化,是這支程式一貫的既有慣例
file: `scripts/test_lumos.py:36720-36777` 新測試 `t_nodehome_stack_test_dirs_not_required` 沒有任何大小寫變體案例,沒殺到這個差異

### F2 頂層 Tests 結尾兩道錨可以同時被巧合滿足,業務資料夾仍可能被判成免家
severity: minor
blocking: 否 — 需要「同名資料夾」與「該棧副檔名」兩個條件同時巧合成立,比第一輪那個「只看名稱結尾」寬鬆到近乎必中的洞窄很多;逃生口 `node_home.ignore` 仍可補
引句:「if base and ext in exts and base in top_dirs:」
1. 兩道錨(去掉結尾要有同名頂層資料夾、副檔名要屬於貢獻那個結尾的棧)只驗證「命名巧合」,不驗證那個資料夾是不是真的 Xcode/`.NET` 測試 target(例如沒有檢查裡面有沒有 XCTestCase/[Fact] 這類框架標記)。只要團隊剛好把一個 Swift 或 C# 業務模組取名成 `<X>Tests`,同時又有一個同名的 `<X>` 頂層資料夾(未必是它的「本體」,可能只是巧合撞名),這支業務檔就會被判成不用家。
2. 實測(暫存副本):頂層有 `Payment/`(真正的付款功能)與 `PaymentTests/`(假設這其實是「付款沙盒測試模式」這種業務功能,不是 xUnit 測試 target),裡面的 `SandboxModeController.swift` 被判 `_nodehome_is_test(...) == True`——不用家。
3. 這是名稱啟發式本身的天花板(這支程式到處都有這種明文取捨,例如 Python 用檔名前後綴而非真的解析框架標記),不是這次改動獨有的新問題,而且比第一輪抓到的「只看名稱結尾就整批放」窄很多(需要兩個巧合同時成立);事故筆記「沒涵蓋」段沒有把這個方向的殘餘風險寫進去,值得之後補一句,但不構成擋這次提交的理由。

佐證:
file: `scripts/lumos:17811-17821` `_nodehome_in_stack_test_dir` 的兩道錨都只比字面(資料夾存在、副檔名屬於該棧),不驗資料夾內容
file: `docs/lumos-toolchain-knowledge/Issues/各棧測試資料夾被當成要家.md:33`(diff 新增)「沒涵蓋」段落列的都是「過嚴」方向的殘餘(巢狀 Xcode、Sources/AppTests 對不上、commonTest/testFixtures),沒提到這個「過鬆」方向的殘餘

## 逐項判定

- 風險掃描指定項(`_NODEHOME_STACK_TEST_DIRS` 模組層級快取沒鎖):判誤報。全檔沒有 threading/multiprocessing,lumos 是單一 Python 行程跑到底的 CLI,不存在兩個執行緒同時把這個全域變數從 `None` 改成 tuple 的窗口;同檔案裡 `_TESTMAP_DIR_RE = None # lazy` 是同款既有寫法(`scripts/lumos:19859`),這次只是照抄慣例,不是新引入的風險面。r1 已判同一結論,r2 delta 沒有改變並發模型。
- 呼叫端一致性(提交前 / 推送前 / 健檢 S8):三段都經同一支 `_nodehome_required`(`scripts/lumos:18005`)算 `top_dirs` 並傳給 `_nodehome_is_test`——提交前/推送前經 `_nodehome_evaluate`(18222-18223 呼叫處)、健檢 S8 經 `_nodehome_ledger`(18497、18513 呼叫處),沒有任何一段繞過新邏輯或用到 `_nodehome_is_test` 預設的空 `top_dirs`;唯一用到預設值的是測試檔自己手動傳入的情境,不影響正式呼叫路徑。判不影響。
- 錨定跟 `_detect_test_dir` 的語意是否同義(prompt 指定要查):實測 `_detect_test_dir` 的 rglob 分支(`scripts/lumos:8649-8658`)本來就是「資料夾名命中、且 `src` 出現在路徑任何一段之前」,不要求 `test`/`androidTest` 是 `src` 的直接子層;新 `_nodehome_in_stack_test_dir` 的 `under_src` 那行(`scripts/lumos:17821`,同一行 r1→r2 沒有改動)語意跟它一致——用 `app/src/main/java/test/Foo.py` 這種「test 不是 src 直接子層」的路徑實測,兩邊行為一致,不是這次 delta 造成的落差。判不影響。
- 「Tests/AppTests/Helper.swift」這個測試案例(check ②的一部分):實測它其實是被既有 `_testmap_is_test` 的目錄正則(整段等於 `test(s)?` 的路徑段,大小寫不敏感)先攔下,不是被這次新加的 suffix 錨定邏輯接住——測試結果正確,但沒有真的驗到這次新加的「SwiftPM Tests/ 頂層」語意(sufs 對 `top="Tests"` 算出 `base=""`,falsy 直接不比對)。不影響正確性,只是測試覆蓋的說法跟實際命中路徑有落差,severity 太低且非本次要修的行為,不另立 F。
- 圖譜鏡頭(`r2-lens.txt` 列出的 bound-tests-gate、canary-audit、guard-kill、slim-get-一行安裝、slim-install-安裝器、slim-uninstall-一行卸載、授權與歸屬、測試假綠形態,以及超出上限只列名的其餘節點):這次 diff(含 r2 delta)只新增/修改 `_nodehome_stack_test_dirs`/`_nodehome_in_stack_test_dir`/`_nodehome_is_test`/`_nodehome_required` 裡 `_nodehome_*` 前綴的邏輯與對應測試,沒有觸碰測試執行、canary 記錄、guard kill rc、`.ps1` 編碼、CLAUDE.md 注入、LICENSE vendoring 或回歸釘機制的任何程式路徑,判全部不影響——跟 r1 對同一批節點的判定一致,r2 delta 沒有擴大波及面。

總結:最高 severity minor,blocking 共 0 條
