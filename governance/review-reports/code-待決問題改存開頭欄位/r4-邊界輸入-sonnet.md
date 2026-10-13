severity: blocker

**發現一:範圍切斷規則把任何 2 格縮排的清單項都當成「題目行」,誤擋合法筆記,連工具自己寫出來的檔都讀不懂**

severity: blocker
blocking: 是
歸因:有證據的修復回歸

`_pq_scan` 在遇到範圍結尾的頂格鍵後,往後找 `_PQ_ITEM_RE.match`。這個正規式是 `^  - (.*)$`,只要是 2 格縮排加 dash 就中,不要求 `id:`。所以 `pending_questions` 後面接 `lands_in:`、`related:`、`tags:`、`decisions:`,甚至 `summary: |-` 區塊內的 `  - 條列`,都會被判成「清單被切斷」。

最小重現(只用 CLI,不手寫畸形檔):

```
筆記:type/status/summary 三個欄位,沒有 decisions
lumos question-add Projects/x_計劃 "非阻塞題" --class c --stage 實作     (rc 0)
lumos decision-add Projects/x_計劃 "甲決策" --decided 2026-10-12         (rc 0,decisions 被加在 pending_questions 之後)
lumos question-set Projects/x_計劃 Q1 status=已決 decision=#d1
lumos spec-gate Projects/x_計劃 --no-run
```

| 版本 | `question-set` | `spec-gate` |
|---|---|---|
| 修前 | `✓ question-set … Q1 改了 status、decision` | `待決問題: ✓ — 1 題,沒有擋進實作的` |
| 修後 | `擋下:這篇的待決問題清單本身讀不懂(第 12 行:這一題寫在 pending_questions 清單範圍外:第 11 行頂格的 'decisions' 把清單切斷了…)` | `待決問題: ✗ — 開頭欄位 pending_questions 清單無法判定` |

- **修後的影響**:沒有任何阻塞題的筆記,規格閘也被擋下。lint 同樣報錯,`question-add` 和 `question-set` 都拒寫,而且訊息叫人把 `decisions` 移走,但那是工具自己寫的。
- **先加題、後補決策是正常流程**:`decision-add` 在沒有 `decisions:` 時加在開頭欄位末尾,`lumos append lands_in` 也是,兩者都會落在 `pending_questions` 之後。
- **直接餵 `pq_parse`**:`pending_questions` 後接 `lands_in:\n  - Systems/x`、`related:`、`tags:`、`summary: |-` 內含 `  - id: foo`,修前都是 `errs=[]`,修後都報「清單被切斷」。
- **另兩個輸入**:`status: x` 後接 `  - id:Q3`(沒空格)或 `  - text: Q3`,修後也被擋。這兩個算誤擋還是該擋有爭議,但同樣是因為正規式不要求 `id:`。
- **筆記與程式對不上**:計劃筆記〈讀法〉寫的是「題目行(`  - id:`)」,程式匹配的是任何 `  - `。

引句:「if _PQ_ITEM_RE.match(fm_lines[k2].rstrip()):」
file: `scripts/lumos:7000`(正規式在 `scripts/lumos:6924`,以修後 `d6bb423f` 為準)

兩版查證:`git show 646dc3a8:scripts/lumos` 與 `d6bb423f:scripts/lumos` 各自 `pq_parse` 同一輸入,修前 `errs=[]`,修後有錯。實跑檔在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r4-邊界輸入-sonnet/` 的 `t2.py`、`vg_before/`、`vg_after/`。

建議:改成只認 `^  - id:`。同時要處理「後面頂格鍵底下的清單項」,例如只在範圍結束後、再遇到 `  - id: Q<n>` 且不是在其他頂格鍵的子結構裡時才報。

**發現二:放行的格式字元讓「只有看不見字元」的題目文字通過**

severity: minor
blocking: 否
歸因:有證據的修復回歸

`question-add $'\u200d\u200c' --class c --stage 需求 --blocking` 在修後成功,印出 `記下一題待決問題「‍‌」`,題目在畫面上是空白。修前同樣輸入被擋。放行字元單獨出現、放在開頭或結尾、連續 500 個,都讀得懂,且 `_yaml_plain_ok` 都回 True。雙向覆寫、零寬空格、LRM、WJ、MVS 仍擋,與 ZWJ 並用也擋。

引句:「return c in "\u200c\u200d\u00ad" or 0xE0020 <= ord(c) <= 0xE007F」
file: `scripts/lumos:6935`

兩版查證:`lumos_before` 對同輸入的 `pq_parse` 報錯,`lumos_after` 回 `ok`。

**已驗證沒問題的項目(兩版行為已比對)**
- **旗標大小寫**:`Blocking`、`bLoCkInG`、`"Blocking"` 修後報錯。`blocking : true` 兩版都報。全形字母與 `blocking_x` 不擋,屬預期。
- **範圍夾雜**:註解行與空行夾在中間,規則照樣觸發,沒有漏。合併衝突標記修前修後訊息相同。第二個 `pending_questions:` 在修後除了「寫了兩次」還多報一條切斷,是重複報錯,不影響擋與否。
- **決策連結**:只有 `projects/a.md` 時 `Projects/A#d1` 為 ok。`A.md` 與 `a.md` 並存時,`Projects/A`、`Projects/a`、`Projects/a.MD` 修前都是 bad,修後 ok。NFD 路徑、`.MD` 副檔名行為正常。`Projects//a`、`./Projects/a`、`a.md.md` 都是 missing,沒有誤放行。
- **推送前**:對下列範圍逐一比對,修前修後相同,rc 都是 0,沒有回歸。範圍:tag、帶註解的 tag、短 sha、`HEAD~0~1`、`@~1..@`、`^{}`、`^{commit}`、前後空白、`...`、`..`、`HEAD~1...`、`...HEAD`、`a..b..c`。

**三問**

①原問題的修復效果:
- 帶頂格鍵、後面還有題的清單現在會擋,旗標大小寫、emoji 連接字、大小寫並存的路徑、鎖逾時、`-` 開頭的推送範圍都有實跑證據。
- 但範圍切斷這一條修過頭,見發現一。

②修補處的正常、錯誤與相鄰呼叫路徑:
- 正常路徑被破壞:`decision-add` 或 `append` 之後的筆記讀不懂,`question-add` 和 `question-set` 拒寫,`spec-gate` 誤擋。
- 錯誤路徑和推送前路徑仍成立。
- 路徑完全相符優先與不分大小寫仍成立。

③新發現案例修前與修後:
- 發現一:修前讀得懂,規格閘 ✓,`question-set` 成功;修後讀不懂,規格閘 ✗,`question-set` 拒寫。
- 發現二:修前報錯,修後通過。

圖譜鏡頭:
- `lumos-cli-write.md` 與 `規格閘.md` 已同步新鎖規則與 `_pq_renames`。
- `lumos-cli-read.md` 第 232 行的文法描述沒提範圍切斷與旗標大小寫不分,屬輕微缺漏。
- `pitfalls-code-loop.md` 無衝突。
- 計劃〈讀法〉寫「`  - id:`」,與程式實際匹配的「任何 `  - `」對不上,見發現一。

總結:本輪修補把範圍切斷規則寫得過寬,擋掉「`pending_questions` 之後還有 2 格縮排清單」的合法筆記,連 `decision-add` 後的筆記也讀不懂,這個回歸會擋合併。
