severity: major

我只在臨時 git repo 裡跑了一個實驗(`_residual_tier_hits`,驗證第 1 條),刪除治理帳列的偵測是在那個 repo 裡直接測的。其餘條目是讀碼推論,沒有跑。

severity: major
blocking: 是 — 同一節點裡拿掉殘留標記,在守的檔相同時不會升 high,這正是你們最怕的「該升不升」。
引句:「gone = set(bguard) - set(hguard)」
問題:`_residual_index_view` 用 (節點, 殘留指標) 當鍵,把同一節點下所有合約的守備檔併成一組。同一節點的兩條合約常常指向同一筆決策(例如一筆決策逐型列出殘留)。這時拿掉其中一條的 `[residual:]` 有兩個後果。第一,(節點, 指標) 這一對仍然存在,`removed` 不會觸發。第二,`about_code` 是節點層級的、測試檔常在同一支檔,所以 `bguard[p] - hguard[p]` 是空集合,`shrunk` 也不會觸發。
具體失敗情境:
- 輸入:起點索引有兩筆 entry,fp=A 與 fp=B,節點同為 Systems/x,殘留同為 Projects/p#d1,test_files 同為 t/t1.py;頂端只剩 A,B 的標記被拿掉。
- 結果:我實跑 `_residual_tier_hits`,輸出只有 `{'asks_dropped': 1}`,沒有 `removed`,也沒有 `shrunk`。如果這次推送沒動那個問答列,合約 B 的殘留就被無聲拿掉,分級不升 high,也不會走代碼審。
- 補救方向:比對時把鍵加上 fp,或改用 (節點, fp, 指標)。
佐證:``file: `scripts/lumos:44532`(`_residual_tier_hits` 的 removed/shrunk 段)``

severity: minor
blocking: 否 — 只多開一條改名後重問的路,而且本來就能換編號繞過。
引句:「c1.1 與 c1-1 是同一個;c11 是另一個」
問題:新的反例編號正規化把 `c-1` 與 `c1` 分成兩個編號(實測:c-1→`c-1`、c1→`c1`、c_1→`c-1`)。上一輪它們是同一個。
具體失敗情境:
- 反例 `c1` 已經被判過 testable,同一節點的黑名單裡是 `c1`。
- 再用 `--case c_1` 或 `c-1` 問一次並判 untestable:key 是 `c-1`,不在 `hard` 裡,也不算 prev,問答寫得進去。
- `_residual_check` 看 `verdicts("c-1")` 時也不含 testable,殘留可以放行。
- 這等於為了避免 c1.1 與 c11 相撞,放掉了 c1 與 c-1 這類常見的改寫。換成全新編號(c2)本來就繞得過,所以這條只是縮小了「同一個反例」的認定範圍。

severity: minor
blocking: 否 — 日期順序檢查有兩處會默默不檢查,但不會多擋,也不影響升級。
引句:「elif audit_day < max(days):」
問題:
- `audit_day` 只從結尾符合 `YYYY-MM-DD` 的 `[audit:]` 抓。格式不合(例如 `2026-7-29`,或日期後面還有字)就得到 `None`,整段順序檢查靜默略過,連提示都沒有。
- 比對只到「天」。同一天先審計、後問答的順序反了,照樣通過。
- `guard audit --date` 可以任填日期,填未來日期就永遠不早於問答。
- 時區方面,`ts` 與 `audit_day` 都是本機當地日期,同一台機器上沒有偏差。
- 另外,指紋演算法改了之後,舊指紋的 residual-ask 問答對不上新指紋。但只有 testable 黑名單不看指紋,所以不放行問題,只是需要重問,這是設計內的結果。

已讀,無 finding:
- 治理帳刪除列偵測:只算 gate 為 residual-ask 的刪除行,別的閘名裡剛好含這個字串的列不誤判;讀不出 JSON 的列算入,git 失敗回 -1 當成有。已讀 `_residual_ask_rows_dropped`;偵測本身在實驗裡抓到被刪的 testable 列(`asks_dropped: 1`)。
- `_residual_index_read_at` 用 ls-tree 分辨 missing 與 unreadable:沒有索引的 repo 仍是 missing,不會誤升。
- `_residual_index_write` 的「沒事可做不碰檔」比對:舊索引帶 tests 欄時會重寫一次,結果正確;符號連結或非一般檔走 `_write_refusal_reason`。
- `_residual_claim_fp` 的句尾標點與 NFKC 正規化:句中符號保留,不會把不同合約併成一個。

總結:最高等級是 major,blocking 共 1 條(同節點共用殘留指標時,拿掉其中一條合約的標記不會升高風險)。另有 2 條 minor,不擋。
