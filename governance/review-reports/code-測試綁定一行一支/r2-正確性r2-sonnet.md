severity: minor

## 已驗主張與證據

我在 `/tmp/lumos-seat-work/code-測試綁定一行一支/正確性r2-sonnet/repo` 切到修後版 590dfeac,另用 46cd75f5 對照。

**① 原問題的修復效果**
- 修後跑 `python3.14 scripts/test_lumos.py -k note_wording`,結果是 44 passed、0 failed。
- 直接呼叫 `_ns_wd_binding_hit` 驗證:
  - `[Test:t_c1,t_c2]` 修前回 None,修後回綁定 2 支。
  - `[test：t_d1,t_d2]` 修後認得。
  - `[test:Kotlin:`a b`,Swift:x]` 的名稱印成「Kotlin:a b、Swift:x」,沒有 `\0`。
  - 範例寫在行內程式碼裡的 `` `[test:x]` 真的 [test:t_a,t_b] `` 只算後面那組,2 支。
  - `[test:`t_one`,t_one]` 去重後回 None,配對案例 I 成立。
  - `[test:t_a,todo]` 和重複名稱都被濾掉。
- 名稱多於 5 支時只列前 5 支並講總數(`_NS_WD_BINDING_SHOW = 5`)。
- 同一行數量先命中時綁定另外出一則,測試 ⑧ 綠。

**② 修補處的相鄰路徑**
- `_ns_wd_line_hit` 改回清單後,數量與位置維持原本的先後與互斥:count 命中時略過 position,否則取第一個符合的括號,然後 `break`。
- 舊行尾補括號的重算:`_ns_wording_hints` 在有命中時用 `len(o.rstrip())` 當 cut 重算,`t_note_wording_tail_append` 綠。
- 舊行已有 `[test:t_a]`、只補 `更 [test:t_b]`,補上的那段只有 1 支,不提醒(我試過 cut=11,回 None)。這是計劃寫明的「只看補上的那段」,不算洞。
- cut 切在多位元組字或方括號中間:
  - 全部是字元索引,不是位元組,所以不會切壞字。
  - 引號遮罩在 `masked` 上算區段,套到 `ln` 時長度不變,位置一致。
  - 我用 `[test:t_a` 加 `,t_b]` 補尾驗過,tail 沒有欄位,回 None,沒有誤報。
  - cut 落在未閉合的反引號 span 中間時會漏報。這種舊行末尾帶未閉合反引號的情形我找不到實際路徑,所以不報。
- `tag` 型別從清單改成字串,我 grep 過,只有 `_ns_wording_emit` 一處讀它,已同步改。
- ledger 的 `lines` 改成 `len({(path, line)})`,同一行出兩則只算一行。

**④ 隔離**
- 綁定規則丟例外時,`_ns_wording_hints` 在 `_ns_wording_collect` 的 try 裡。
- 結果是 `box["items"]=[]` 加 `box["error"]`,`_ns_wording_emit` 只印一句「沒跑完」,不改 rc。
- `t_note_wording_binding_isolated` 對有、沒有違規兩種情況都驗到 rc 不變,另兩組提醒(否定現況句與前綴)照常。
- 代價是同一次提交裡數量與位置兩則也一起不出。它們同屬 wording 組,我不當作 finding。

**③ 同案新發現**:見 F1,修前與修後結果相同。

**未驗**:全套測試、`governance/review-reports/`(依指示不讀)、非 `\0` 的其他遮罩副作用。

### F1 `[test:]` 值內夾著引號段時,引號被遮成 `\0\0\0` 當成一支測試名,誤報綁定並把 NUL 印到 stderr
severity: minor
blocking: 否 — 只提醒不擋,觸發需要在 `[test:]` 值裡放成對引號,實際很少見。
引句:「bh = _ns_wd_binding_hit(_inline_blank(ln, quotes), cut)」
失敗場景:新寫一行 `甲 [test:t_a,「x」]`。引號遮罩先把 `「x」` 換成 `\0\0\0`。`slot_parse` 與 `_test_names_of` 把它切成非空名稱 `"\0\0\0"`,`_ns_tr_placeholder` 也不濾,於是去重後 2 支。
- 印出「這行綁了 2 支(t_a、\x00\x00\x00)」。
- 實測 `[test:t_a,「x」,t_b]` 會變成「3 支」。
- note-shape 的 test_refs 與 S20 看的是原字,這裡看的是遮過的字,跟計劃「同一套」的說法不一致。
- 建議:名稱含 `\0` 的一律略過,或只遮 `[test:` 欄位之外的引號。
歸因:有證據的原有漏查(修前 46cd75f5 的 masked 版同樣產生 `['t_a','\x00\x00\x00']`,本輪修補沒有引入也沒有修掉)。
佐證行:`scripts/lumos:31506`(`_ns_wd_binding_hit`)、`scripts/lumos:31499`
查證命令與結果(兩版皆在 `/tmp/lumos-seat-work/code-測試綁定一行一支/正確性r2-sonnet/`):
- 修後:`python3.14 probe.py` 得 `(2,'binding','這行綁了 2 支(t_a、\x00\x00\x00)')`。
- 修前:`python3.14 probe2.py` 得 `(2,'binding',['t_a','\x00\x00\x00'])`。

總結:共 1 條,最高 minor
