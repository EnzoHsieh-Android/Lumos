severity: clean

我查了四個鏡頭，沒有發現作者漏看的 bug。查證都在 `/tmp/lumos-seat-work/code-主線CI/r3正確性/` 底下建的 `--shared` clone 裡做，沒有動 repo 本身。

**鏡頭 1：新斷言穩不穩，拿掉 `sorted(files)` 會不會紅。**
- 實測把 `scripts/lumos` 的 `for f in sorted(files):` 改成 `for f in files:`，`-k t_choice_cov_src_pkgs_edges` 紅在新斷言，輸出是 `{'fb'} {'fa'}`。
- 紅得穩，不靠檔案系統順序碰巧：`_rev_walk` 在 `scripts/test_lumos.py` 裡主動把 `files` 倒過來。沒排序時，檔案倒序一定先看到 B.kt，上限 1 就收到 fb。
- 這台 macOS 沒排序時正序也先吐出 B.kt（`f_fwd` 是 `{'fb'}`），所以兩邊都會紅。Linux 上正序若剛好是名字順，倒序那一邊仍然會紅。
- 有排序時，上限 1 讀到 A.kt 後 `seen=1` 不超過上限，收 fa；讀到 B.kt 時 `seen=2` 超過，停下，所以結果確定是 `{"fa"}`。

**鏡頭 2：新建的 `tmp/f/src` 會不會影響後面用 `tmp` 當根的斷言。**
- 新建發生在 `_cut_at`、`k_part`、`part`、`part_rev` 都算完之後，所以那兩條斷言不受影響。
- 後面 `calls` 那條比的是 `p1 == p2 == real_scan(tmp)`，兩邊都包含 fa、fb，仍成立。
- `froot` 的相對路徑是 `.`，`in_src` 為假，A.kt、B.kt 不會被當成測試原始碼集跳過，也不會被誤判成別的類別。
- 整個測試函式實跑 9 條斷言全過。

**鏡頭 3：還原是否完整，`redirect_stderr` 範圍對不對。**
- `finally` 同時還原 `_os_mod.walk` 與 `_CHOICE_COV_SRC_MAX`。
- 新區塊內 `_os_mod.walk = _rev_walk` 在 `try` 裡面，`real_walk` 在 `try` 之前就已取得，所以例外也還原得了。
- `redirect_stderr` 包住兩次掃描，上限警告不會漏到終端。
- 小提醒，不算 finding：`old = m._CHOICE_COV_SRC_MAX` 重新賦值是安全的，因為前一個 `_cut_at` 已在自己的 `finally` 還原過，這裡抓到的是原值。

**鏡頭 4：有沒有讓既有斷言失去作用。**
- 把 `subs.sort()` 換成 `pass` 重跑，原本的資料夾倒序斷言仍然紅，輸出是 `{'testapp','org/b'} {'bom/x'}`。新增段落沒有蓋掉它。
- 兩個排序變異（檔案層、資料夾層）各自對應到不同斷言，沒有互相遮蔽。

文件那行 PITFALL 補述（`規格閘.md`）與測試實際行為一致。

無殘留（`/tmp/lumos-seat-work/code-主線CI/r3正確性/` 已刪除。同層的 `/tmp/lumos-seat-work/code-主線CI/正確性` 與 `/tmp/lumos-seat-work/code-主線CI/r2正確性` 不是我建的，沒動）
