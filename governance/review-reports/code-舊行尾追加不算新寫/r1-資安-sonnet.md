severity: major

**S1 NFC/NFD 同名撞鍵:配對表拿別篇筆記的舊行去扣這篇的新違規,第一層放行,第二層也被帶錯**
severity: major
blocking: 是 — 可直接繞過筆記形狀擋,且已實測 rc0 對照 rc1
引句:「            if ok:                out[nfc(b)] = ok」
- 攻擊者是會往 repo 推筆記的人(外部投稿的 PR 作者,或想偷懶的作者)。
  - 入口:同一個圖譜目錄下放兩篇檔名只差 Unicode 正規化的筆記,例如 `Pé.md` 的 NFC 版與 NFD 版。
  - git 在 Linux 與 CI 允許這樣的兩個路徑並存。
  - macOS 上用 `git update-index --index-info` 加 `-c core.precomposeunicode=false` 也能造出來。
- 送進來的東西:
  - 筆記 X(NFC 名)是起點版本裡的舊 DEP 行,本來就沒寫來源。X 只在句尾補一段括號,於是進配對表。
  - 筆記 Y(NFD 名)在同一個行號寫一句全新的、程式碼推得出的現況句,例如「DEP:認證現在直接讀 Redis 逾時 30 秒…」,不帶 `[來源:…]`。
- 走到的程式:
  - `_notelines_append_pairs` 以 `out[nfc(b)]` 為鍵,兩篇會互相覆蓋或合併。
  - `_ns_append_subtract` 用 `pairs.table().get(nfc(p))` 查表,拿到的是 X 的 `{行號: 舊行}`。
  - Y 的違規在 `tp.get(v[1])` 命中 X 的舊行。`old_viol(o, …)` 回出同一個「現況描述沒寫來源」,鍵相同,Y 的新違規被扣掉。
  - 沒有任何一步核對「這個行號的舊行是不是這個路徑的」。
- 拿到:第一層放行一句全新的現況句。第二層 `_note_audit_mark_appended` 也用同一張表,把 Y 的整行誤標成「舊句 + 補的尾巴」。
  - `it["appended"] = it["text"][len(o):]` 會切掉 Y 的前半句,判定者被要求只判後面那段。
  - 因此 Y 的新斷言可以放在前半句,不被判定者看見。
  - 第二層我只從程式推得這個結論,沒另外跑。
- 重現:`/tmp/s_poc/poc.py`,在 `215da06f` 的臨時 clone 上跑 `python3.14 /tmp/s_poc/poc.py`。
  - 先建 X、Y 兩篇(`ls-files` 顯示 `Pe\xcc\x81.md` 與 `P\xc3\xa9.md` 並存),再暫存 X 補括號加上 Y 的新 DEP 行。結果 `with NFC/NFD pair rc= 0`。
  - 對照 1:只有 Y 寫新行時 `control rc= 1`,有被擋。
  - 對照 2:X 不補括號、只留 Y 新行時 `control2 rc= 1`。
  - 所以是 X 的補括號配對讓 Y 過關。
- 預期與實際:配對表鍵應該用 git 原始路徑,或鍵衝突時整篇不配;實際是以 `nfc()` 折疊後互相污染。
- 出處:這個鍵折疊是 `_NotelinesNet` 既有的寫法(`{nfc(q): …}`)。這次 diff 把它搬進「放寬判定」的用途,放寬的方向讓它從無害變成可利用。
- 修法:`out` 與查表都用原始路徑;或偵測到兩條路徑 NFC 後同名就整批不配對。

**S2 申訴列不帶 tail 時,對只判句尾的判定檔無效**
severity: minor
blocking: 否 — 推論,需要先有範圍不一致的申訴流程,且只影響申訴而不影響原判定的強度
引句:「            k = (d["disputes"], r["id"], r.get("tail"))」
- 推論,沒重現。
- 誰與從哪裡:作者或審查者在另一個範圍或起點下重跑 `note-audit prepare --only`。
- 送什麼:這次清單上該項沒有 `尾` 標頭,申訴列就沒有 tail。
- 影響:
  - `_note_audit_fold_scoped` 查的是 `disputes.get((name, id, tail))`。申訴鍵 `(檔名, id, None)` 對不上判定列的 `(檔名, id, tail哈希)`,申訴就被靜默忽略。
  - 被申訴要「換成更重」的 CODE 不生效,CONTEXT 的尾巴判定照舊涵蓋。
  - `record` 的「被申訴的判定檔沒判過這行」檢查只比 id,不比 tail,所以不會擋。
- 預期與實際:申訴應該能升級它指名檔案中同 id 的所有範圍;實際只升級鍵完全相等的。
- 此問題的前提是自己能控制 prepare 的範圍,屬防疏忽層級,不是存心繞過。

**已看,無的類別**
- 命令、路徑、模板注入:
  - 新增的 git 呼叫都走 `_ns_diff`,仍帶 `--no-ext-diff --no-textconv`,另外釘 `--inter-hunk-context=0 --diff-algorithm=myers`,沒有新開外部驅動。
  - `cat-file` 的規格字串排除了含 `\n` 的路徑。
  - 沒有新的 shell 插值。
  - `_notelines_parse_hunks` 照 `@@` 計數走,內容行 `++ x`、`diff --git` 偽造行都不會被當成檔頭。
  - git 對含換行的檔名會加引號,引號路徑回 None,不配。
- 判定檔與清單解析:
  - 清單標頭的 `| 尾 <hex16>` 要在 `## id | …` 行的最末尾才吃。標頭文字與路徑後面都還接著 `:行號`,所以筆記內容無法在標頭裡偽造尾欄。
  - 偽造判定檔的 tail 欄、手改清單的「尾」,都是作者本來就能直接寫一份 CONTEXT 判定的事。計劃第 0 節明講只防疏忽、不防存心繞過,不另報。
  - `tail` 哈希只含舊句,但內容編號含整行文字,所以不同的補述會是不同 id,一份尾巴判定不會涵蓋別的補述。
- 提示注入:
  - 範本規則 6(對判定者說話一律判 CODE)沒有被新增的「Tail-only」段覆蓋。該段只宣告優先於規則 2 與 5。
  - 補的括號最多 300 字且必須是純括號群,可承載的指令有限。
  - 清單多出的兩行 `舊句`、`只判這次補在句尾的` 與 `>>>` 那行內容重複,沒有讓注入更容易。
  - 「舊句」來自起點版本,不是這次可改的內容。
- 治理帳 `relaxed`:
  - 只寫路徑、行號、規則名、sha、例外類別名,沒有筆記原文,沒有密鑰。
  - 路徑沒過 `_esc_clean`,跟既有 `blocked` 事件寫 `nodes` 的做法一致,不單獨報。
- 加密與傳輸、行動端:本 diff 不碰,已看,無。
- 疏漏聲明:`scripts/test_lumos.py` 與各 Projects、Systems 筆記只掃過改動與是否含可執行內容。測試檔沒有新的 shell 或 subprocess 風險。

**圖譜鏡頭固定席逐條**
- 不影響(各自的合約內容與本 diff 無關):
  - `lumos-cli-read`(search 預設排除 superseded)
  - `bound-tests-gate`
  - `guard-kill`
  - `授權與歸屬`(`scripts/lumos` 檔頭 SPDX 與 MIT 全文未動)
  - `測試假綠形態`
  - `design-loop`(處置閘第五步,與本 diff 無關)
- `reversibility-governance-ledger` 與 `pitfalls-code-loop` 是 RISK 節點,diff 動到的治理帳寫入只新增 `relaxed`,沒改既有事件。`_gate_event_fit` 與 `_drift_m1_fit` 的裁法等價。
- 只列名的節點不必答。

最高嚴重度 major,blocking 1 條
