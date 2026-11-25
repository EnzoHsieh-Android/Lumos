severity: clean

資源席(sonnet)對這份 diff 沒有發現。唯一量到的偏慢路徑是下面的低嚴重度觀察,給不出會讓正常操作失敗的場景,所以不立 finding。

## ① 子程序與執行緒收尾
- 這份 diff 沒有新增子程序或執行緒。快篩失敗名單由 `_choice_merge_classify` 在回傳前算完,新增的 `_kill_merge_off` 和 `_kill_merge_failed_first` 只算字串、排順序,不開程序。
- 第一個訊號來時,`_KillMerge.on_signal` 照舊收掉帶 `_lumos_merge` 標記的程序群組。diff 沒有動這條。
- 新增的 `except _KillHalt: _kill_merge_off(mg, c.plat, "中斷"); raise` 在 `_kill_merge_iter` 裡。`_kill_merge_off` 對 `中斷` 只寫 `mg.off` 就提早 return,不印也不呼叫外部,所以這裡不會有程序殘留或例外蓋掉 `_KillHalt`。
- 「一個壞法也合併」讓 `--only` 單點也會量齊全部單支基準,再跑合併基準和快篩。這三種呼叫都走 `_kill_run`,逾時上限都受 `mg.remaining()` 限制(`cap = min(full, max(mg.remaining(), 1.0))`),跟以前同一個收尾路徑。
- 先紅順序只改 `yield from` 的內容順序。收尾仍在 `cmd_guard_kill` 的 try/finally 與 `_KillHook` 這一側,不是 generator 內。中斷在逐支第一支之前或之後來,走的是同一個 `between()` 與 `should_stop`,沒有新的空窗。

## ② 時間預算
- 時限門排到 `_kill_merge_ready` 最後一道,只決定「不合併、照逐支」,不會擋下正常操作。
- 量單支基準途中,`_kill_merge_singles` 每支都用實測平均重估剩下的,不夠就收手。diff 只在收手前多記 `c.merge_need`,沒改判斷。
- 單一壞法現在也會量齊全部單支基準。這個成本被 `need = 支數 × 10 × 1.5` 擋在剩餘時限之內,`cap` 也不超過剩餘時限。這是計劃已定的取捨(做法 2),不是 diff 偏離。
- 提示裡的 `X` 是 `ceil((已花 + 約需 + 60) / 100) × 100`,只是印字,不影響任何判斷。
- 斷路器與 `unclean` 計數:`_kill_merge_breaker` 把原因記進 `mg.unclean` 的條件(`elif counts`)和斷路器的 `streak` 完全相同,兩者同進同出。diff 沒改斷路器的判斷邏輯,只多印「最後一次」。

## ③ 記憶體與二次方
- `mg.unclean` 的原因字串都是固定字串:`逾時`、`被系統收掉`、`找不到 JUnit 結果檔`、`結果檔讀不出來`、`結果檔超過大小上限`。`_choice_merge_facts` 把 `_secev_junit_facts` 的原因代碼全部收斂成固定的「結果檔讀不出來」。帶數字的「N 支對不到……」回傳 `counts=False`,不進 `mg.unclean`。所以鍵數有上限,平台名數是外層上限。
- `mg.off` 以平台為鍵,每個平台只有一個值。原因字串是固定集合,基準不乾淨那類已經在 `_kill_merge_base` 把「N 支對不到……」折成「對不到名字」。
- `mg.kinds` 的鍵是 (平台, group),大小不超過這次要跑的壞法數乘平台數,每次呼叫只活一次。
- `single_runs` 只是整數。`merge_kind` 每筆事件只有幾個平台。
- 失敗名單比對是 `names × bad`。`bad` 的上限是 `_SECEV_FACTS_MAX = 100000`(file: `scripts/lumos:8756`)。我在 `/tmp/lumos-seat-work/code-選擇點變異加速第二段/資源-sonnet/` 量過:169 個名字對 10 萬筆失敗約 0.82 秒,2000 個名字約 9.6 秒。這是每次快篩失敗的上限,而且前面已經先剖析過同樣大小的 XML,所以不構成新的主要成本。我不標它,因為 lane 通常只有幾百支,真實失敗數遠低於 10 萬,講不出具體的失敗場景。

## 圖譜固定席
這次沒附固定席節點,鎖也沒給節點內容,所以沒有可逐條判的筆記。
- 鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/eebcc4fa5fe0b5a25e4a5dbf1574354faf70321c406161f2fe42fa8b2cc9ba62.json.warming` 還在,33 位元組,時間 Nov 25 12:55。
- 我沒有讀鎖內 PID,也沒有刪鎖,交給派工端處理。

總結:最高嚴重度 clean,blocking 0 條。
