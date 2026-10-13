severity: minor

沒有會擋合併的問題。我在 `qo-frontmatter` 工作樹跑了 `python3.14 scripts/test_lumos.py -k qfm`,171 個案例全綠。七篇筆記(五篇點名的加情境出題、pitfalls-code-loop)`lumos lint` 都是 0 問題。故障變體都做在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r3-合約圖譜-sonnet/repo` 的副本,沒動 repo。

**先答你點名的幾件事**
- **寫入鎖說法成立:** 我逐一 grep 了 `atomic_write_verify(` 的所有呼叫者(約 27 處)。每一處不是自己有 `@_vault_locked`,就是外層有 `_vault_write_lock`(guard plan/settle/abandon/kill、set/append/remove、drift 修復等)。「所有呼叫 `atomic_write_verify` 的入口都拿同一把」在這個範圍內成立。
- **S1–S3 新綁的測試名都存在,也都綠。** 但綁定位置有落差,見 finding 1。
- **決策 d13 與 d12 跟程式一致:** d13 說規格閘擋阻塞沒結的需求與架構題、`--stage` 列題,與程式相符。d10、d11 是 `valid: false` 且各指向 d13、d12。
- **其餘搜尋詞無過期句:** `_decision_cmd_locked`、`_strict_list_scan`、「沒寫平台前綴就只比名字」在 repo 內已無殘留。「只列需求風險面」只出現在已作廢的 d10、d11 內文,合理。
- **新加的斷言抓得到真錯:** 我手動還原缺陷試了其中三條。t_qfm_r2_folds ⑦⑧(改名、左端空著)和 ⑥(平台設定只講一次)都會翻紅。lint 在壞設定下印四次,⑥ 就紅。問題只在綁定位置(finding 1)與一個過度宣稱(finding 2)。

1. 條款 S1 的綁定沒涵蓋它新寫的行為。
severity: minor
   blocking: 否
   - S1 字面寫「改名的跟舊路徑比、左端空著當 HEAD」,綁的卻是 t_qfm_gate_holds_blocking 和 t_qfm_push_remind_ranges。守這兩個行為的是 t_qfm_r2_folds ⑦⑧,而它只綁在 S2。
   - 重現:在副本拿掉 `git_range.startswith("..")` 區塊,並把 `_pq_renames` 換成 `{}`。S1 兩支綁定測試 2 passed、17 passed 全綠,t_qfm_r2_folds 才紅(⑦⑧ 兩條斷言)。
   - 結果:條款綁定測試無法證明條款說的話。
   - 引句:「(整份刪掉的不比、改名的跟舊路徑比、三點範圍用合併基準、左端空著當 HEAD)」
   - 佐證:`docs/lumos-toolchain-knowledge/Projects/待決問題改存開頭欄位_計劃.md:116`、`scripts/test_lumos.py:56457`、`scripts/test_lumos.py:56510`
   - 歸因:有證據的修復回歸(這輪新增條款句與綁定時漏綁)。

2. 鎖測試的「翻紅釘」說明過度宣稱,鎖檢查本身也比說法寬。
severity: minor
   blocking: 否
   - docstring 說「`--all` 不拿鎖 → ② 翻紅」。我在副本拿掉 `cmd_decision_reindex` 的 `@_vault_locked`,t_qfm_frontmatter_writers_take_lock 仍 2 passed。原因是失敗模式變成 reindex 自己被拒寫,而 ② 只看 question-add 的 rc 和題數。
   - 實際翻紅的是 `-k reindex`(5 failed),那些測試不在 S3 綁定裡。
   - 另外 `atomic_write_verify` 用 `any(_VAULT_LOCK_HELD.values())`,拿著別的筆記庫的鎖也過。這點我只讀程式碼判斷,沒實測,歸因未判定。
   - 引句:「翻紅釘:拿掉 atomic_write_verify 的鎖檢查 → ① 翻紅;--all 不拿鎖 → ② 翻紅。」
   - 佐證:`scripts/test_lumos.py:56480`、`scripts/lumos:19923`
   - 歸因:有證據的修復回歸(本輪新測試的過度宣稱)。

3. `Systems/規格閘.md` 還列著已刪的函式,新函式沒列。
severity: minor
   blocking: 否
   - 這篇的負責清單寫 `_pq_git_read_many`,修補已刪掉它,改用 `_pq_renames` 和共用的 `_nodehome_cat_blobs`,清單沒補。
   - 查證:`grep -n "def _pq_git_read_many" scripts/lumos` 無結果;`def _pq_renames` 在 `scripts/lumos:8078`。lint 沒擋。
   - 引句:「`_pq_push_remind`、`_pq_git_read_many`、`_clause_check`」
   - 佐證:`docs/lumos-toolchain-knowledge/Systems/規格閘.md:81`
   - 歸因:有證據的修復回歸。

4. `decision-amend` 新拿了寫入鎖,鎖逾時會直接噴 traceback,筆記卻說會「擋下」。
severity: minor
   blocking: 否
   - 重現:另一程序持鎖 75 秒,我跑 `lumos --vault v decision-amend Projects/a_計劃 d1 --field context --text x`,等了 60.7 秒後輸出 `RuntimeError` 堆疊。
   - 原因:`scripts/lumos:53003` 附近只接 `ValueError`,其他入口接 `RuntimeError`。
   - 筆記 `lumos-cli-write.md` 寫「鎖殘留時這些指令會等 60 秒才回擋下」,對 amend 不成立。
   - 修前 amend 不拿鎖,沒有這條路徑。
   - 引句:「def cmd_decision_amend(env, rel, did, field, text):」
   - 佐證:`scripts/lumos:41596`、`scripts/lumos:53003`
   - 歸因:有證據的修復回歸。

5. 原計劃第 38 行仍把待決問題寫成「另案」,並指向已作廢的 d10。
severity: minor
   blocking: 否
   - 該句寫「規格閘與 lint 讀它的部分已撤出,改存開頭欄位另案(決策 d10)」。
   - 第 211、226、282、299、312 行也引 d10,但多是歷史說明,可留。
   - 引句:「正文一節暫時只是給人看的清單,情境出題的寫法」
   - 佐證:`docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:38`
   - 歸因:有證據的原有漏查。這輪只改了 d10/d12/d13 區塊,沒掃到正文。

**三問**
- ① 原問題修復有行為證據。
  - 決策指令與 question-add 同時跑,兩邊都不丟(t_qfm_decision_add_shares_lock 綠)。
  - 沒拿鎖就呼叫 `atomic_write_verify` 會拒寫。
  - 零寬、雙向覆寫、孤立代理字元會被拒,我另用 `question-add` 實測 U+200B、U+202E,都 rc2 且不動檔。
  - 路徑錯與撞名的決策連結被擋,連結比對不分大小寫(副本實跑 `projects/A_計劃#d1` 也過)。
  - 判定時整庫只掃一遍(linear_cost ③)。
- ② 相鄰路徑仍成立:
  - 正常題目、冒號與井號、`[]` 上加題、both-way 的讀寫都綠。
  - 頂格 `status:`、`source:` 不再誤擋,旗標掉到頂格才擋。
  - 其餘寫入入口全數持鎖,如上。
  - 唯一偏離是 finding 4 的 amend 逾時路徑。
- ③ 本輪新發現的同一案例,修前修後結果:
  - amend 逾時:修前不拿鎖、無此路徑;修後噴 traceback。
  - 規格閘.md 的 `_pq_git_read_many`:修前函式存在、說法正確;修後函式已刪、筆記過期。
  - 手動拿掉 `reindex --all` 的鎖:修前無鎖檢查,不丟題但會蓋掉;修後 reindex 自己被拒寫、題數不變,所以 ② 照綠。

總結:合約與程式大致一致,寫入鎖說法成立;只有綁定位置、一個過度宣稱的翻紅釘、一個過期符號和 amend 逾時訊息這幾個小缺口,沒有會擋合併的問題。
