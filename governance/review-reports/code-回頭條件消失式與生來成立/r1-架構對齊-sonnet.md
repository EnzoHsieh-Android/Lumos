severity: major

# 架構對齊審查(r1)

## 三問

1. 分層與依賴方向:新程式都落在 `_DriftProbeTree`、`_drift_probe_cond_candidate`、`_probe_*` 這一層,沒有跨層直呼;`_drift_gone_typo_hint` 加在 `_drift_probe_check` 之後、不讓 `_drift_probe_judge` 認得鍵,跟既有「判定函式不認得條件鍵」一致(對照 file: `scripts/lumos:32612`)。唯一的分層疑點是 Z3。
2. 命名與錯誤處理:`_probe_gone_err`、`_probe_gone_backtick_err`、`_drift_gone_text` 沿用 `_probe_*_err`、`_drift_*` 前綴;但 `_probe_check_value` 回傳 (值, 錯誤) 二元組,鄰居 `_probe_value_err`、`_probe_named_err` 都只回錯誤說明或 None(Z3、Z5)。
3. 第二種做法:有。git 讀檔分支的大小上限另起一套、不用既有的 `_nodehome_cat_blobs_capped`(Z1);「是不是資料夾」在 `present` 另算一次(Z4)。

**Z1 帶字串的 when-gone 在 git 模式另起一套讀檔與大小上限,繞過既有的批次讀取上限層**
severity: major
blocking: 是 — 引入第二種做法:專案已有把上限放在批次讀取層的 `_nodehome_cat_blobs_capped`,新增的 `_read_raw` 兩個模式用兩種上限寫法,git 模式根本沒有上限。
引句:「self._raw[p] = _DRIFT_RAW_TOO_BIG if f.stat().st_size > _DRIFT_GONE_MAX_BYTES else f.read_bytes()」
file: `scripts/lumos:26527`(`_nodehome_cat_blobs_capped` 的說明:「上限放在批次讀取這一層,不另起查法」)
file: `scripts/lumos:32205`(`_drift_cat` 呼叫的是不帶上限的 `_nodehome_cat_blobs`)
1. 輸入:被推送的提交裡有一支 30 MB 的一般檔,筆記寫 `[when-gone:big.txt::zzz]`。
2. 走到:`_DriftProbeTree.prefetch` 呼叫 `_read_raw`,非 disk 模式走 `_drift_cat` 把整支檔讀進記憶體,存進 `self._raw`,之後 `_drift_gone_text` 才用 `len(b) > _DRIFT_GONE_MAX_BYTES` 判超限。
3. 壞在哪:disk 模式先 `stat` 再決定讀不讀(超過就存一個 `object()` 哨兵),git 模式卻是讀完才比、而且 30 MB 一直留在 `_raw` 裡。同一個類別裡同一件事兩種寫法,且 git 模式(推送判定,會擋的閘)沒有記憶體上限;鄰居 `_ROLE_MAX_BYTES`、`_NS_APPEND_BASE_MAX_BYTES` 都是走 `_nodehome_cat_blobs_capped`。另外 `_DRIFT_RAW_TOO_BIG = object()` 這種哨兵混進 bytes|None 的字典,鄰居的做法是「超限回 None」。
4. 重現(實跑輸出,臨時 repo 內一支 30000000 位元組的檔):
   ```
   t=m._drift_probe_tree(r,sha); print(t.gone("big.txt::zzz"), t.gone_why, len(t._raw["big.txt"]))
   -> None {'big.txt::zzz': '超過 2 MB'} 30000000
   ```
   判定正確(判不了),但 `_raw` 裡存著完整 30000000 位元組,證明上限沒擋在讀取層。

**Z2 `_read_raw` 的工作目錄分支少了 `_read` 每支檔都看的預算檢查**
severity: minor
blocking: 否 — 結構對、只是跟同類別既有的 `_read` 行為不一致。
引句:「for p in todo:                 try:                     f = Path(self.root) / p」
file: `scripts/lumos:32323`(`_read` 的 disk 分支在迴圈裡每支檔先 `if self._over(): return False`,說明寫「工作目錄模式也每支檔前看預算」)
1. 輸入:`drift scan`(disk 模式)帶一批 `[when-gone:路徑::字串]`,預算快用完。
2. 走到:`_read_raw` 只在迴圈外看一次 `self._over()`,迴圈內不看。
3. 壞在哪:`_read` 那段註解(代碼審 r2 併發席)明講的就是這個漏洞,`_read_raw` 把 `_read` 的骨架抄了一份卻漏掉這一句。這也是 Z1 的第二個症狀:`_read_raw` 與 `_read` 是兩份幾乎重複的讀檔骨架。

**Z3 反引號的檢查放在提交形狀層與格子層,沒進其他鍵共用的值驗證 `_probe_value_err`**
severity: minor
blocking: 否 — 分工有作者寫明原因(解析器拿到的是剝過行內程式碼的文字),結構可以成立;但錯誤處理的落點跟其他鍵不同。
引句:「err = _probe_check_value(k, val)[1] or (_probe_gone_backtick_err(v) if k == "gone" else None)」
file: `scripts/lumos:3885`
file: `scripts/lumos:27988`(`_ns_revisit_cond_viol` 另外 `errs.append(bt)`)
1. 輸入:`when-gone` 字串含反引號。
2. 走到:其他鍵的所有值錯誤都從 `_probe_value_err` → `_probe_parse` 的 `errs` 出來,scan、check、doctor 都看得到;gone 的反引號錯誤只在 `_ns_revisit_cond_viol`(提交形狀)與 `_slot_retire_err` 兩個呼叫端各接一次,`_probe_parse`/`_probe_value_err` 不含這條。
3. 壞在哪:兩個呼叫端的接法也不同(一個 `or` 接在 `[1]` 後面、一個 `errs.append`),`_probe_check_value` 回二元組而 `_probe_value_err` 回單值,讀者要記兩套。`_slot_retire_err` 的 `[1]` 索引取值也是鄰居沒有的寫法。⚠ 是否該收進單一驗證點,取決於作者「看原文」的前提能否在 `_probe_parse` 層拿到原文;diff 內看不出,判不準。

**Z4 「是不是資料夾」在新函式另算一次,與同檔既有的資料夾判斷各寫各的**
severity: minor
blocking: 否 — 結構位置對,只是同一件事的實作分散。
引句:「self._dirs = {q.rsplit("/", i)[0] for q in self.entries for i in range(1, q.count("/") + 1)}」
file: `scripts/lumos:32787`(`_drift_probe_row_problems` 用 `any(f.startswith(v.rstrip("/") + "/") for f in tree.files)` 判 when-file 指到資料夾)
file: `scripts/lumos:32569`(候選篩選另用 `t.startswith(path + "/")`)
1. 輸入:`[when-file:src/lib]` 與 `[when-gone:src/lib]` 指同一個資料夾。
2. 走到:when-file 的資料夾判斷只看 `tree.files`(一般檔),when-gone 的 `present` 看 `entries`(含連結檔、子模組)並預先算 `_dirs` 集合。
3. 壞在哪:同一棵樹對「資料夾」有兩套定義。只含子模組或連結檔的資料夾(例:`vendor/` 底下只有子模組),when-file 的警告不認它是資料夾,when-gone 認得。計劃〈做法〉3 自己也強調「在」的定義要一致,但沒有說明為什麼 when-file 的提示不改用 `present`。

**Z5 `_drift_cond_split(v, k=None)` 同一支函式兩種呼叫形式混用**
severity: minor
blocking: 否 — 結構對,命名/介面不一致。
引句:「def _drift_cond_split(v, k=None):」
file: `scripts/lumos:32561`(`_drift_cond_split(v)` 不帶 k 的既有呼叫:`unread_for`、`one`、`_drift_probe_cond_candidate` 的 symbol/test 分支)
1. 輸入:任何 symbol/test 條件。
2. 走到:同一個類別裡 `prefetch` 與 `unread_for` 的 gone 分支帶 k,`one` 與 `_drift_probe_cond_candidate` 的 symbol/test 分支不帶;`prefetch` 對 symbol/test 也傳 k(被忽略)。
3. 壞在哪:k 的預設值 None 等於「symbol/test 的切法」,呼叫端要自己記得 gone 必須傳 k、忘了傳會默默按「最後一個 ::」切(gone 的字串裡可有 ::,切錯不報錯)。沒有任何機制擋「gone 忘了傳 k」。

## 沒問題的項目

- `_probe_check_value` 同時被 `_probe_parse` 與 `_slot_retire_err` 呼叫,收掉了撤除條件那條路原本不轉反斜線的第二套判定(對照 file: `scripts/lumos:3885`、`scripts/lumos:32019`),方向正確。
- 「條件怎麼選」提醒、`_probe_value_err` 與 `_slot_retire_err` 的鍵清單改由 `_PROBE_KEYS` 組字,沒有再各寫一份。
- `_drift_gone_typo_hint` 加在判定之後,不讓 `_drift_probe_judge` 認得條件鍵。
- `_drift_row_unread` 沿用 `unread_for` 點名,沒另寫第二套點名。

## 固定席節點

- Systems/bound-tests-gate、guard-kill、lumos-cli-lifecycle 等合約行:本 diff 不涉及這些合約的行為(只動 `_probe_*`、`_DriftProbeTree`、紀律範本);紀律範本改動後 `CLAUDE.md`、`AGENTS.md` 與範本的差異只差撤除條件那一句,三份一致(diff 內可見)。lumos-cli-lifecycle 的「re-inject 只覆蓋 sentinel 之間」不受影響。

最高 severity:major(Z1)
