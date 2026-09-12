severity: blocker

# 範圍

只審 `governance/review-reports/code-java補棧/r1-snapshot.patch`(Java 補棧這批 diff)。核心新增是 `scripts/lumos` 裡的 `JAVA_TEST_RE`(Java/JUnit 測試方法擷取正則)與它餵給 `discover_test_methods()` 的用法,以及 `_init_config_skeleton`/`_STACK_QUESTION_SPECS`/`test_lumos.py` 的相應改動。以下逐類交代,再列可構造的攻擊。

---

## 逐類掃描結果

1. **不可信輸入流到危險操作**:已看,無新增問題。`JAVA_TEST_RE` 擷取出的方法名被 `([A-Za-z_]\w*)` 這個字元類鎖死,不可能帶引號/分號/路徑分隔字元;真正把方法名餵進 shell 指令的地方(`scripts/lumos:23617` `run_cmd.replace("{method}", _shlex.quote(method))`)在套用前還會過 `_KILL_METHOD_OK_RE` 白名單(`scripts/lumos:23446`)——這條在本次 diff 之前就存在,沒有被這批改動繞過或弱化。`_init_config_skeleton` 產出的 JSON 值全部來自靜態表或整數計數,見下面第 4 類。
2. **繞過審查閘**:已看,**有**(見下方發現一)。`JAVA_TEST_RE` 用 `.*?`(DOTALL,可跨 `{`)取代 Kotlin 版的 `[^{]*?`,導致「合約綁定的測試名字是不是真的被 `@Test` 標註」這件事不再被正確驗證——已用完整 `lumos doctor` 跑通全流程,證實一個從未被 `@Test` 標註、內容空的方法會被判定成「real」(可執行證據),Check T 完全不出聲。
   - 另外檢查了「讓某題永遠不觸發」這個方向(七題觸發清單):`_STACK_TRIGGERS` 的 when/when_raw 機制本來就是純正則比對,任何字面模式都天生可以被換寫法迴避(例如把 `Thread.sleep` 包進反射呼叫)——這是繼承自既有 kt/cs/vue/node 棧的既有設計限制,這批 diff 只是照抄同一套機制加 java/py 兩張表,沒有引入新的規避手法,不算這次新增的漏洞,列為「推論、非本次新增」。
3. **阻斷服務**:已看,**有**(見下方發現二)。同一條 `JAVA_TEST_RE` 在「`@Test` 附近長時間找不到 `void`」時退化成 O(n²),已實測用一支 367KB 的 `.java` 檔讓 `discover_test_methods()` 單獨跑 15.7 秒,而且是二次成長曲線,可用更大檔案輕易推到分鐘級,足以拖垮 doctor / pre-push / CI 的合約測試閘。
4. **設定骨架改動的攻擊面**:已看,無。`_init_config_skeleton` 的 `ranked` 來自 `_stack_ext_counts(root)`(`scripts/lumos:14136`),而該函式對每個實際檔案的副檔名做 `if ext not in known: continue`(`scripts/lumos:14159`),`known` 只包含 `TEST_PROFILES`/`SYMBOL_PROFILES` 表裡寫死的固定字串(`.java`、`.py`…)。攻擊者放一個副檔名帶引號或控制字元的檔名進 repo,那個「怪副檔名」根本不會進 `known`,因此永遠不會被計入 `counts`,也就不會出現在最終寫進 JSON 的任何欄位裡——沒有檔名注入路徑。
5. **秘密與個資**:已看,無。`skills/java-idioms/SKILL.md`、`skills/python-idioms/SKILL.md`、`skills/lumos-design-loop/templates.md` 與新增測試 fixture 裡只有指到 Python/Requests/Ruff/Bandit 官方文件的公開連結與通用建議文字(如「API key/secret 從環境變數讀」這種建議句),沒有真實憑證、token、內部網址或個資;測試裡的樣本程式碼都是合成的購物車/訂單範例。
6. **新增依賴**:已看,無。整批 diff 只用到 Python 標準庫(`re`、`tempfile`、`json`、`decimal`、`subprocess`),沒有新增第三方套件、沒有新的外部網路呼叫。

---

## 發現一:JAVA_TEST_RE 讓「沒有 @Test、內容空」的方法被判定為真實測試,繞過合約測試閘(bound-tests-gate 的核心承諾)

severity: blocker
blocking: 是
引句:「r"@(?:Test|ParameterizedTest|RepeatedTest)\b.*?\bvoid\s+([A-Za-z_]\w*)\s*\(",」
file: `scripts/lumos:3373-3375`(消費端:`scripts/lumos:3898` `discover_test_methods()`;判定點:`scripts/lumos:1297` doctor Check T 的 `if name in methods_for(plat)`,以及 `scripts/lumos:23450` `real = method in mset` 的 bound-tests 閘)

**問題**:Kotlin 版正則(同一批程式碼旁邊)刻意用 `[^{]*?`,不讓比對跨過方法本體的 `{`,所以「@Test 後面第一個 fun」一定是它自己的方法。Java 版為了吃到 `@ValueSource(ints = {1, 2, 3})` 這種帶大括號的參數化註解,改用會跨過 `{` 的 `.*?`(DOTALL)。代價是:只要檔案裡「@Test 標註的方法」本身不是 void(不管是不是刻意的),正則會往後跳過它,抓到下一個「毫無 @Test 標註」的 void 方法的名字,並把那個名字登記成「這個方法是真的測試方法」。

`discover_test_methods()` 對整個 repo(不限 `src/`,只排除 `.git/node_modules/bin/obj/dist/build/__pycache__/publish/vendor/.vs/.idea`)做這個掃描,任何 `.java` 檔都算數。它產出的集合 `mset` 是這整條治理鏈唯一用來判斷「合約綁的 `[test:X]` 是不是真的可執行證據」的依據——doctor Check T(`scripts/lumos:1296` 附近)、`cmd_contracts`、`_bound_tests_for_diff`(`scripts/lumos:23450`,決定 code-loop 的 bound-tests 閘要不要真的去跑這支測試)全部只問「這個名字在不在 `mset` 裡」,不會去確認它旁邊真的貼著 `@Test`。

**已實跑,不是純推論**:先用最小樣本證明正則本身會抓錯名字:

```
$ python3 - <<'EOF'
import importlib.machinery
lum = importlib.machinery.SourceFileLoader("lum", "scripts/lumos").load_module()
sample = '''
public class FakeJavaTests {
    @Test
    public String helperNotVoid() { return "x"; }

    void t_critical_invariant_test() {
        // no @Test annotation here at all
    }
}
'''
print([m.group(1) for m in lum.JAVA_TEST_RE.finditer(sample)])
EOF
['t_critical_invariant_test']
```

再用完整的 `lumos doctor` 走一次端到端,證明這條誤判真的會讓治理閘放行一個空頭合約。建了一個乾淨 repo(`git -C` 全程操作,沒有碰 lumos-toolchain 本身的 repo):

- `.lumos/config.json`:`test_profile=java-junit`
- 知識庫節點 `Checkout.md`:`KEY:★INVARIANT★ 結帳金額永遠不得為負 [test:t_checkout_never_negative]`
- `src/main/java/shop/Checkout.java`:`int total() { return -1; }`(明顯違反這條 INVARIANT,單純用來讓場景合理)
- `src/test/java/shop/CheckoutTest.java`:
  ```java
  package shop;
  class CheckoutTest {
      @Test
      public String decoyNotVoid() { return "never runs, not a real JUnit test"; }

      void t_checkout_never_negative() {
          // NOTE: no @Test annotation at all. JUnit will never discover/run this.
      }
  }
  ```

跑 `python3 scripts/lumos --vault docs/demo-knowledge doctor --ci`(於該臨時 repo 目錄內),Check T 的輸出:

```
[T] 標成「不能破壞的合約」的規則,有沒有綁到一條真的會跑的測試
  ⚠ 發現 1 條 ★INVARIANT★ 綁了測試但合法性未經獨立審計 (…):
      • Systems/Checkout.md: 結帳金額永遠不得為負
```

**沒有出現「偽證據」也沒有出現「懸空」**——doctor 認為 `t_checkout_never_negative` 是一條「真實可執行測試方法」,唯一的提醒只是「還沒被獨立審計」,那是完全不同的另一件事(是否認同這條規則,不是這條測試存不存在)。對照組:若把 `decoyNotVoid` 拿掉(或把它也寫成 void),`t_checkout_never_negative` 就會落回「懸空」被 Check T 擋下——證明就是這個 decoy 造成的誤判,不是別的原因。

**影響**:這正是這批改動固定席上被標成 ★INVARIANT★ 的 `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md` 想守的東西——「任一紅/懸空(dangling/fake)/方法名不合法/證不出跑過 → blocked=True」。對 Java 專案,只要在同一個測試檔(或 repo 裡任何一個 `.java` 檔)裡放一個「@Test 標在非 void 方法上」的裝飾用方法(這種寫法本身完全能通過 javac,不需要任何特殊技巧),它後面第一個 void 方法——不管有沒有 `@Test`、不管內容是不是空的——就會被整條治理鏈當成「這個合約真的有可執行證據」。這對「拿掉關鍵測試但想讓合約看起來還站得住」或「先射後畫靶,補一個永遠不會失敗的空測試把 dangling 消掉」這種情境完全開放,而且不需要 gradle/maven 真的裝在本機或 CI 上就能讓 doctor 靜默通過(doctor Check T 本來就不執行測試,只驗證「聲稱的證據是否存在」,這條正是那份「不執行、只驗存在性」承諾被打穿的地方)。至於 code-loop 的 bound-tests 閘(真的去跑 `./gradlew test --tests`),如果專案真的接了 gradle/maven 且 CI 有跑,執行到 0 支測試理論上會被 `_ran_evidence_check` 攔下來——但這條防線完全依賴「run_cmd 有設好、CI 真的會跑到」,而 doctor 這一層(每次 `lumos doctor`、pre-push 都會跑,不需要 CI)已經先把假象蓋章通過。

---

## 發現二:同一條 JAVA_TEST_RE 對「找不到 void」的輸入是 O(n²),單一惡意 `.java` 檔可把整個測試發現流程拖到卡死

severity: blocker
blocking: 是
引句:「r"@(?:Test|ParameterizedTest|RepeatedTest)\b.*?\bvoid\s+([A-Za-z_]\w*)\s*\(",」
file: `scripts/lumos:3373-3375`(套用點:`scripts/lumos:3898-3928` `discover_test_methods()` 對每個 `.java` 檔做 `mre.finditer(txt)`)

**問題**:`.*?`(DOTALL)是單一非貪婪萬用字元,理論上不是傳統「巢狀量詞」那種指數級回溯,但當文字裡有 M 個 `@Test` 出現、而每一個之後都要掃到檔案結尾才能確認「找不到 void」時,每次嘗試都要付出跟剩餘檔案長度成正比的代價——整體是 O(M × N),M 又跟檔案大小成正比時就是 O(N²)。這正是題目問的「新加的正則有沒有能被一個惡意檔案觸發的指數級回溯」的同一類威脅(這裡是多項式而非指數,但一樣可以用一個小檔案把處理時間放大到不可用,效果相同:「把整個閘卡死＝閘等於不存在」)。

**已實跑,量出真實數字**(純規則,不靠理論):

```
n=1500  size=70500   matches=0  time=0.555s
n=3000  size=141000  matches=0  time=2.202s
n=6000  size=282000  matches=0  time=8.817s
```
(n = 檔案裡 `@Test` 出現次數,每個後面接一個回傳 int、不是 void 的方法,filler 內容都一樣;檔案倍增,時間約放大 4 倍,驗證是二次成長不是線性)

再用真正的入口函式 `discover_test_methods()` 對一個真實 repo(git 版本控制、一支測試檔)量測:

```
crafted file size: 376030 bytes (~367KB); n=@Test occurrences: 8000
discover_test_methods() over repo with ONE crafted file took: 15.708430051803589 seconds
discovered methods: set()
```

一支 **367KB** 的 `.java` 檔(現實中生成碼、Android 資源綁定類、ANTLR/protobuf 產物都很容易達到甚至遠超這個大小)就讓這一個函式單獨跑 15.7 秒。因為是二次成長,推算把檔案放大到約 1MB 左右就足以讓單次呼叫逼近甚至超過一分鐘(推論,基於上面實測的成長曲線外插,沒有真的跑滿 1MB,但曲線已經很乾淨地驗證是平方關係)。

**影響**:`discover_test_methods()` 會在下列每一次呼叫時被觸發,而且是掃**整個 repo** 裡所有 `.java` 檔(不限 `src/` 底下——`TEST_PROFILES["java-junit"]` 雖然標了 `"rglob_under": "src"`,但這個欄位在 `discover_test_methods()` 裡完全沒被讀取,函式本體就是 `os.walk(repo_root)` 全庫掃,見 `scripts/lumos:3898-3928`,所以惡意檔案放在 repo 任何角落、只要副檔名是 `.java` 且不在 `CODE_SKIP_DIRS` 裡就算數):
- 每次 `lumos doctor`(Check T)
- 每次 `lumos contracts`
- 推送前的 `code-loop` bound-tests 閘(`_bound_tests_for_diff`/`_platform_test_index`)
- 這些又是 pre-push hook 與 CI 都會呼叫的路徑

只要有人(惡意或無意)提交一支這種形狀的 `.java` 檔到 Java 消費專案裡,後續每一次跟合約測試相關的檢查都會被拖慢,規模夠大時會直接造成逾時——而這個工具鏈本身把「閘逾時/掛掉」視為和「假綠放行」一樣嚴重的失效模式(治理帳的 `red`/`unfilterable` 兩種都要擋,逾時等於閘完全發揮不了作用)。這是本次 Java 補棧新引入的行為,對照 Kotlin 版用 `[^{]*?` 天然被真實程式碼裡常見的 `{` 及早截斷,不存在同樣的放大係數。

---

## 結論

最嚴重 severity:blocker;blocking 的發現共 2 條(發現一、發現二)。
