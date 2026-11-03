severity: major

總覽:我找到一個會讓推送閘漏放的洞,有最小重現。這個洞是 r2 要堵的「單平台含冒號的測試名不見了,被另一支同名後綴的測試頂替」的殘留變體,不是這輪新引入的。另有一條 minor。其餘三個本案鏡頭(只差空白版面、`_spec_gate_push_match` 與 `fill` 為空、`_env_missing_why`)都沒找到會擋推送的問題。

## Finding 1

severity: major
blocking: 是

file: `scripts/lumos:16017-16021`(`_spec_gate_push_one`)與 `scripts/lumos:15609-15620`(`_spec_gate_push_fill`),加上 `_spec_gate_push_match` 的單平台後綴比對。

引句:「if not split:
        cand = [m for m in fill if t.endswith(":" + m)]
        if len(cand) == 1:
            return cand[0], fill[cand[0]]」

**失敗場景**

單平台專案,計劃有兩條條款:S1 綁 `[test:gone:fee_jvm]`,S2 綁 `[test:fee_jvm]`。規格閘寫好留痕後,把 `gone:fee_jvm` 這支測試刪掉,再推送。不需要先改設定。

1. `_spec_gate_push_fill` 靠 `_spec_gate_items`,而它只收 `state == "bound"` 的條款。
2. 測試一刪,S1 變成懸空,不再是 bound,所以 `gone:fee_jvm` 這個名字不在 `fill` 裡。
3. 條款指紋只算條款文字,不算綁定狀態,所以留痕不會被判過期。
4. 留痕裡的 `t="gone:fee_jvm"` 在 `fill` 裡比不到。
5. 它走到後綴比對:`"gone:fee_jvm".endswith(":fee_jvm")`,而 `fill` 裡 S2 的 `fee_jvm` 剛好是唯一候選。
6. 於是 `gone:fee_jvm` 被換成 `fee_jvm`,綠了就放行。
7. 輸出還寫「留痕裡的 2 支測試全綠(fee_jvm、gone:fee_jvm)」,但實際只跑了 `jvm fee_jvm`。

這正是計劃做法 2 與程式註解宣稱已擋掉的情形。宣稱的理由「條款指紋相符,條款裡的名字就是當時寫留痕的那份」,漏了該條款已經因懸空被排除在 `fill` 之外。

**測試為何抓不到**

新測試 `t_spec_gate_record_keeps_platform` 的 d3 案只有 S1 一條條款,`fill` 是空的,後綴分支根本沒被碰到,而且 d3 期望的「照擋」本來就會發生。測試只擋得住 r1 舊寫法的改壞,擋不住這個變體。

**最小重現**

在 `e0603d082` 的 scripts 複本(放在我的暫存目錄,已刪)裡,把 d3 改成兩條條款:

```
_sg_plan2(kg3, "甲", ["- [S1] 結帳應收一成服務費 [test:gone:fee_jvm]", "- [S2] 結帳應顯示一般費用 [test:fee_jvm]"])
```

其餘步驟與 d3 相同,然後檢查 `r.returncode == 1`。

- 修後 `e0603d082`:`PROBE push rc 0 ['jvm fee_jvm'] ... ✓ 甲_計劃:留痕裡的 2 支測試全綠(fee_jvm、gone:fee_jvm)`,檢查翻紅。
- 修前 `06e101684`:輸出完全相同(rc 0、`['jvm fee_jvm']`、同一行綠)。

**歸因:有證據的原有漏查。** 兩版結果一致,不是修補回歸,而是 r2 想修的問題沒修乾淨。r2 的修法把後綴來源從測試索引換成條款名字,但沒把懸空條款的名字算進比對池。

**修法方向**

- 讓 `fill` 或比對池也收懸空條款的名字,這樣精確比對會先命中,名字不變,後續仍判懸空而擋下。
- 或者單平台後綴比對只在 `t` 確定是多平台寫的前綴時才用。

## Finding 2

severity: minor
blocking: 否

file: `scripts/lumos:49385-49397`(`_tg_statements` 取的敘述會把字串內連續空白壓成一格),搭配 `scripts/lumos:49731-49735` 的只差空白版面路徑。

引句:「return [] if prev["isig"] == f["isig"] else _tg_expected_cands(path, k, f, prev, kt)」

**失敗場景**

`assertEquals("a b", f())` 改成 `"a  b"`(兩格空白)或 `"a\tb"`。

- `sig` 相同、`isig` 不同,走到新的只比預期值那條。
- `_tg_statements` 把兩邊都壓成 `"a b"`,所以 `tq/expected-changed` 不會列。

`"a, b"` 改 `"a,b"` 會列,因為標點兩側的空白不被壓成同一格;`"a b"` 改 `"a b "` 也會列。

**歸因:有證據的原有漏查。**
- 修前與修後的結果都是 `[]`,我用 `_tg_fn_cands` 兩版各跑過。
- 計劃寫「字串裡的空白算內容」,只有部分成立。

## 三問

**1. 原問題修復的行為證據**

- **只差空白版面:** `-k tq_guard` 403 條全過。我另用兩版比對:沒斷言且有多行字串的測試,縮排或字串空白變動,修前列 `tq/no-assertion`,修後 `[]`。
- **改回單平台:** `jvm:fee_jvm` 單平台案照跑綠,通過。含冒號且只有一條條款的案也過,但見 Finding 1,那案沒檢驗到殘留的洞。
- **DeviceException:** `-k device_missing` 7 條過,含 Java 案。
- **規格閘整體:** `-k spec_gate` 389 條全過。

**2. 修補處的正常、錯誤與相鄰路徑**

- **鏡頭 4(a),只差空白版面:**
  - 註解掉斷言:`sig` 會變,仍走全規則,列 `tq/no-assertion` 與 `tq/assert-weakened`。
  - 超時調大:`1000` 改 `10000`,仍列 `tq/timeout-raised`。
  - CRLF 整檔轉換、多行字串整體縮排:修前與修後都是 `[]`。
  - `@Ignore` 放在 `@Test` 之前:兩版都沒由此路徑列出,是既有行為,不屬於這次改動。
  - 結論:只差空白那條路沒漏掉該判的規則,沒有誤判。
- **鏡頭 4(b),`_spec_gate_push_match` 與 `fill`:**
  - `fill` 為空時回 `(t, None)`,退回 `resolve_test_refs`,行為正確。
  - 單平台讀多平台寫的舊留痕時,後綴只在恰好一個候選時採用,符合設計。
  - 多平台路徑與修前等價:`t in fill` 等同舊的 `fill.get(t)`。
  - 例外是 Finding 1。
- **鏡頭 4(c),`_env_missing_why`:**
  - 對 None、非登記格式、`profile=None`、`bytes` 輸出,結果都與舊的行內寫法一致。
  - 唯一差別是去色碼,帶 `\x1b[31m` 的輸出修後能命中。
  - `\x1b[K` 這類 `_ANSI_RE` 不收的控制碼不會被去掉,兩版同樣不命中,同 `_ran_evidence_check` 的既有範圍。
- **鏡頭 1,新舊互讀:**
  - `_tg_functions` 產出的函式資訊一律帶 `isig`,紅燈版的 `fn` 也來自它,所以 `prev["isig"]` 直接取不會 KeyError。

**3. 新發現的同一案例修前、修後各是什麼結果**

- Finding 1:修前、修後相同,都是 rc 0 且綠(見上)。
- Finding 2:修前、修後都是 `[]`。

## 其他

- **鏡頭 2,pitfalls:** 我跑了 `lumos pitfalls --diff 06e101684..e0603d082`,輸出的 `[lint:ruff]` 全是 `test_lumos.py` 的舊行,行號都落在這輪沒改的位置。我沒逐行比對 hunk,所以只能說我沒看到命中在改動行,不能保證是 0。
- **鏡頭 3,固定席節點:** 我沒有逐條核對每個節點的合約行,以下是依牽連檔與合約內容的判斷。
  - `lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle`、`design-loop` 的 ★INVARIANT★ 各管 search 濾網、guard kill rc 與 JSON、re-inject、處置閘第五步。這份 diff 沒碰那些路徑,判不影響。
  - `測試假綠形態` 的 ★INVARIANT★ 要求修 bug 的測試配「前置斷言證明現場成立」。這輪新增的 Java 案與重新縮排案都有前置斷言。
  - 單平台含冒號案雖有 `★前置★`,但它的現場走不到後綴分支,正是 Finding 1 的測試漏洞。
- **文件不一致,minor:** 計劃的 S3 條款仍寫「設定之後改回單平台時照去掉前綴的名字跑」,與做法 2 改版後的「只拿條款名字比」不一致。照 S3 實作會做出自己切冒號的版本,也就是 r2 已否決的寫法。
- **未驗範圍:**
  - 外部 `LUMOS-ROLE-CARDS` 的角色卡:派工說判不出前後端,我沒用。
  - Java 專案的推送前路徑,只驗了規格閘那段。
  - `_gov_ledger_ignored` 與 doctor 的三處提醒,不在這輪修補差異內,我沒看。
- **清理:** 我的暫存目錄已刪成只剩 `load.py`、`p1.py`、`p2.py`、`p3.py`。

相關檔案:`/Users/enzo/harness/lumos-redbase-realrun/scripts/lumos`、`/Users/enzo/harness/lumos-redbase-realrun/scripts/test_lumos.py`、`/Users/enzo/harness/lumos-redbase-realrun/docs/lumos-toolchain-knowledge/Projects/紅燈版實跑三缺口_計劃.md`。
