severity: minor

## ①提示注入

已看,無。擋下訊息與候選的外來字串都走 `_tg_cand`。實測結果:

- 檔名走 `_out_clean(file, 500)`,原因走 `_out_clean(extra, 300)`。
- 留痕的 token 另外在 `_tg_rb_metas` 裡過 `_out_clean(..., 40)`。
- 孤兒檔的 token 取檔名主幹,也過同一個 `_out_clean(..., 40)`。

控制字元和換行出不來,偽造不出「接下來」這類段落。測試名、條款、路徑、內嵌路徑和寫入端的 `_redbase_attach` 印出行,也都過 `_out_clean`。

剩下的只是 40 字內的自由文字。那要有人在 PR 裡偽造治理帳的 token 欄,屬單人威脅模型之外的外來文字回顯,不另列。

patch 引句:「extra=f"規格閘紅燈版 {tok}:{reason}")」

## ②讀寫越界與執行越界

已看,無。實測結果:

- 讀紅燈版全走 git 物件(`cat-file --batch`),不讀工作目錄,也不跟捷徑。
  - 路徑先過 `_tg_rb_path_ok`(限 `governance/redbase/` 底下的 .json,不准 `..`、反斜線、控制字元)。
  - 內嵌測試檔路徑過 `_tg_rb_entry` 的檢查(限 repo 相對的 .kt/.java,不准 `..`、開頭 `/`、控制字元)。
- 寫入端的資料夾名用 `isalnum` 過濾。
  - `_note_audit_safe_dir` 逐層擋符號連結,建完再查一次。
  - 測試檔路徑先 `resolve().relative_to(repo)`。
  - `check-ignore` 的參數放在 `--` 後面。
- 寫入端去重用的「讀上一份紅燈版」,走 `_repo_path_unsafe` 加 sha256 核對,路徑也過 `_tg_rb_path_ok`。
- `_tg_rb_deleted` 的路徑來自 `git log`,已用 `core.quotePath=false`。我用中文迴圈資料夾實測,刪除偵測有抓到。
- 路徑只進 `rev:path` 的 stdin 規格,不進 argv。含空格或冒號的路徑,`cat-file --batch-check` 的解析不會讀錯大小。

patch 引句:「_d, why = _note_audit_safe_dir(rr, dir_rel)」

## ③非刻意、一步就能繞過的守衛

### S1 分岔點(主線)已有同函式鍵的測試,紅燈版整支不比,「補斷言、跑紅、再刪掉」無痕
severity: minor
blocking: 否 — 計劃白紙黑字定的契約(紅燈版只護「分岔點不存在的新測試」,既有測試改走分岔點比對),且相對主線沒有變弱;但這是 r4 驗收時唯一實測繞得過的口子
引句:「if k in by_path[p][0]:」
file: `/Users/enzo/harness/lumos-spec-snapshot/scripts/lumos:49881`(`_tg_rb_compare`)。寫入端 `/Users/enzo/harness/lumos-spec-snapshot/scripts/lumos:14258`(`_redbase_find_one`)不看分岔點,照樣存紅燈版,而且不印「這支不受保護」。
攻擊路徑四件:
- 誰:照常操作的 AI,或使用者本人。
- 從哪裡:在主線上已有的測試函式裡補一條新行為的斷言,規格閘跑紅(紅燈版存了),實作做不到,再把那條斷言刪掉,最後 commit 並推送。
- 送什麼:推送版的測試跟主線版逐字相同,所以分岔點比對沒有變化可列。紅燈版因為 `k in by_path[p][0]` 被 `continue` 跳過。
- 拿到什麼:新行為的斷言憑空消失,規格閘留痕和紅燈版都在,推送前比對卻 0 條候選。測試保護被拿掉,這正是這道守衛要擋的事。
- 前提:被綁的是既有函式,不是新函式。新函式不受影響,實測照常列 `tq/redbase-weakened`。

重現:
- 用 `/tmp/lumos-seat-work/code-規格閘紅燈測試快照/資安-sonnet/t6.py` 建小 repo。
- 主線有 `FooTest.shouldDouble`,只有一條 `assertEquals(10, ...)`。
- 分支加上 `assertEquals(900, Foo.calc(3))`,用 `_redbase_write` 存紅燈版並提交。
- 下一個提交刪掉 900 那條。
- 跑 `_tg_start` 加 `_tg_analyze`,輸出是 `ERR None`,候選清單為空。
- `git diff --stat origin/main HEAD -- app` 也是空的。
- 對照組:同一支測試改成「分岔點不存在的新函式」,會列兩條 `tq/redbase-weakened`。

歸因:有證據的原有漏查。修前版本 `0fcc214af` 的 `_tg_rb_compare` 已有同一行 `continue  # 分岔點就有:照舊拿分岔點當前一版`,r4 的修補沒有碰它。

其餘 r4 修補驗收,都在小 repo 實測有效:
- 沒有留痕的孤兒檔:各自直接跟推送版比,並另列一條 `tq/redbase-unreadable`。
- 同一個提交刪舊檔加內容相同的新檔:兩邊都被抓到,`--no-renames` 有效。
- 刪掉紅燈版與治理帳那一行:照刪掉前的內容比,仍列 `tq/redbase-weakened`。
- `git add -N` 登記的紅燈版:算還沒提交,擋下。
- 壓提交、合併主線(治理帳衝突取聯集)、直接在 main 上工作、搬檔、改測試名:都沒有繞過。
- 已看,無新的 blocking 級問題。

本輪已看完三類:沒有 major 以上,只有 S1 一條 minor,是原有的設計取捨。
