severity: major

## b1 C-34 的「if 區塊最後一個陳述」那一支把 `ofRule` 拿掉,樣本照綠
severity: major
blocking: 是 — 守衛的必要行為(樣本要守住規則每個選項)沒被守住,有具體改壞而測試全綠。
- 輸入:`api.yml` 的 C-34 `value-used` 最後一個 `all:` 分支,把 `nthChild: {position: 1, reverse: true, ofRule: {matches: code}}` 的 `ofRule` 拿掉。
- 走法:我把規則檔 C-34 到 C-37 段內每個行內 `{a, b}` 選項逐一拿掉,再跑 `choice_sample_problems`(真的 ast-grep 0.51.2)。拿掉這個 `ofRule` 後問題清單為空,樣本全綠。
- 壞在哪:最後一個陳述後面接行尾註解的 if 區塊(下面這種)應該 HIT。原規則 HIT 第 4 行;拿掉 `ofRule` 後只剩別的行,第 4 行不再命中。
  ```
  val v2 = if (c) {
      go()
      x.let { it + 1 } // 註解
  } else 0
  ```
- 新樣本裡「最後一個陳述 + 註解」只放在 `list.map { … }` 的 lambda 裡,守的是 `value-pos` 那一處的 `ofRule`。`value-used` 裡 if、when、try、catch 區塊最後一個陳述的 `ofRule` 沒有對應樣本。
- 派工案例 G1 宣稱「規則每一行、行內每個選項拿掉都要有一行翻紅」,這一個選項不在作者列的等價例外裡(例外只有父節點種類固定、`regex: '^[-+]'`、`stopBy: end`、literal-arg 的 `nthChild reverse`)。
- 修法方向:補一行 if 區塊或 try 區塊、最後一個陳述後接行尾註解的 HIT 樣本。
引句:「// 第四輪補齊:規則每一行、行內每個選項拿掉都要有一行翻紅(註解排除、最後一個陳述、when 掛在 if 底下、方法名比對;代碼審 r4 c1)」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml:179`
歸因:有證據的原有漏查。修前 59c41038 的樣本沒有任何 `ofRule` 那一行的守衛,修後補了 `value-pos` 那處但沒補 `value-used` 這處。兩版樣本核對都不會因拿掉它而紅,不是修補造成的回歸。我沒另跑修前版,修前樣本是修後的子集,這是推論。

## b2 表列號 `C-0` 被收下,撤號那一行卻不認 `C-0`,測試沒釘
severity: minor
blocking: 否 — 不合規的列號會被收下,但有具體條件才會碰到(要有人真的寫 `C-0`),修補後測試仍綠。
- 輸入:選擇點表有一列 `| C-0 | …`。
- 修後(`re.fullmatch(r"[CA]-[1-9][0-9]*", rid)`):報「列號要寫成 C-<n>」。這是對的,同撤號那一行的 `[1-9]` 一致。
- 我把正則改成 `[CA]-(0|[1-9][0-9]*)`(收下 `C-0`),跑 `-k choice_table_batch2` 20 項、`-k choice_samples_batch2` 33 項,全綠。新測試只釘 `C-040`、`C-４０`、`C-4０`、`A-01`,沒有 `C-0`。
- 後果:表可以有 `C-0` 這一列,但要撤時 `已撤列號:C-0` 會被報「看不懂」,撤號守衛對它不成立。
- 派工要的極端輸入 `C-0` 沒有測試。
引句:「for label, rid in (("前導零", "C-040"), ("全形數字", "C-４０"), ("全形混半形", "C-4０")):」
file: `scripts/test_lumos.py:146024`
歸因:有證據的原有漏查。修前 `C-0` 被收下(實測修前 `choice_tables` 回傳 `['C-1','C-0']`,無問題);修後已報錯,只是缺測試。

## 其他極端輸入的結果(無 finding)
兩版都實跑(`rules_dir=False`,真函式 `choice_tables`):
- `C-` 沒有數字、`C-40` 後接零寬空白(U+200B)、小寫 `c-40`、BOM 開頭:該列被列號正則靜默略過,兩版相同,修後沒有惡化。有對應規則檔時 `_choice_rules_match` 會報「規則 … 在型錄沒有對應的列」,沒有規則檔就等於沒有這一列。
- `C-40` 後接全形空白 U+3000、NBSP、tab、無前後空白:`strip` 後仍是 `C-40`,正常收下、撤號照擋。
- `C-` 後接 3000 位 9:收下,耗時無感,兩版相同。
- `C-040`、`C-４０`(全形數字):修前被收下,撤 `C-40` 時繞過撤號,修後報「列號要寫成 C-<n>」。這是真修復。
- 樣本檔改 CRLF 換行:`choice_sample_problems` 對全部樣本回 0 個問題。標記正則的 `\s*$` 吃掉 `\r`。
- 多行 lambda、`/* 註 */ // HIT` 兩種新樣本寫法在 ast-grep 0.51.2 下通過。更早的 ast-grep 版本我沒有裝,**未驗**。
- 新增的 14 行只加在 `choice-batch2.kt`,既有樣本檔沒動。`choice-batch2.kt` 只被 `t_choice_samples_batch2` 讀(`scripts/test_lumos.py:146073`),沒有行指紋 pin 釘它。
- C-34 到 C-37 規則檔逐行刪除與行內選項拿掉的掃描:除 b1 外,倖存的都在作者列的等價例外裡。具體是父節點種類固定的 `kind:`、`regex: '^[-+]'`、literal-arg 的 `nthChild reverse`,以及 C-37 literal-arg(由 C-36 與 C-37 一字不差的比對測試守)。

## 圖譜鏡頭
- `Systems/kotlin規則包`(家):改動只動 `check.py` 的 `choice_tables` 列號驗證與樣本。計劃第 4 點已補「半形數字、不帶前導零」,與程式相符,不影響合約。
- `Systems/bound-tests-gate`(★INVARIANT★):`check.py` 與 `test_lumos.py` 列在牽連檔。我沒讀到這份改動改了綁定測試判定邏輯,只動了選擇點表的列號檢查與樣本,不影響。
- `Systems/guard-kill`、`Systems/lumos-cli-lifecycle`、`Systems/測試假綠形態`、`Systems/lumos-cli-read` 的合約(guard kill rc、re-inject、還原翻紅釘、search 排除 superseded):這次改動不碰 `scripts/lumos`。我也沒找到這些合約被牽動的路徑,判不影響。
- 「這次新增的殘留」段:鏡頭算超時,段內寫「算不出來」。我沒讀 `governance/residual-index.json`,**未判定**。

## 三問
1. 原問題(表列號 `C-040`、全形數字繞過撤號)的修復效果:有。
   - claim:表列號寫成非半形、前導零時要報錯。
   - input:`| C-040 |`、`| C-４０ |`,撤號 `C-40`。
   - expected:報「列號要寫成 C-<n>」。
   - before:`choice_tables` 回傳 `['C-1','C-040']`,無任何問題,撤號被繞過。
   - after:回傳 `['C-1']`,報 `('C-040','列號要寫成 C-<n>(半形數字、不帶前導零),這裡是「C-040」')`。
   - comparison:`C-0` 同樣由「收下」變成「報錯」(b2)。
2. 修補處的正常、相鄰路徑:成立。
   - 正常列號 `C-40`(含無空白、tab、NBSP、U+3000 前後空白)兩版相同,撤號 `C-40` 照擋。
   - 撤號那一行的判法未動。
   - 乾節點 `A-01` 由同一段程式報錯,測試有釘。
   - `-k choice_table_batch2` 20 項、`-k choice_samples_batch2` 33 項、`-k choice_points_compose` 7 項在修後全綠。
3. 新發現的同一案例修前、修後各是什麼結果:b1 和 b2 都不是修補造成的回歸。
   - b1:修前樣本沒有那一處的守衛,修後也沒有,拿掉 `ofRule` 兩版樣本核對都綠。
   - b2:修前收下 `C-0`,修後報錯,只缺測試。

未驗範圍:
- 修前版本沒有逐項重跑 b1 的規則改壞掃描。
- `choice_points` 整組(`-k choice_points`)在我這邊逾時被中止,以派工案例的「修後全綠」為準,我沒獨立重跑。
- 沒有測 ast-grep 其他版本。

臨時目錄:repo 副本、before 工作樹、實驗檔夾我已用字面絕對路徑刪除。留下 `exp1.py`、`mut.py`、`mut2.py` 三支小腳本在 `/tmp/lumos-seat-work/code-選擇點第二批/邊界-sonnet/`,由編排者收貨後刪。

最嚴重:major;blocking 共 1 條
