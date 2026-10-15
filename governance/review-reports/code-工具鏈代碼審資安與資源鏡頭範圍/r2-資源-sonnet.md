severity: clean

三個問題都沒找到 finding。我讀了差異的程式與測試部分,也實際跑了 `python3.14 scripts/test_lumos.py -k lens_scope`(76 項全過,17 秒)。

**① 子程序與執行緒收尾。已讀,無 finding。**
- 三支新測試(loop next 邊界與筆記指標)沒有開背景程序或執行緒,只用同步的 `run()`。`run()` 沒帶 timeout,但這是既有寫法,新測試也沒讓它更容易卡住。
- `t_loop_next_lens_scope_marker_odd_kinds` 的壞掉符號連結,走的是 `Path.is_file()`。它對壞連結回 False,產品碼又有 `except Exception` 兜底,所以不會例外或卡住。
- 暫存目錄(`gctl-lens-*`、`gctl-test-*`)落在全套測試每輪的 `gctl-run-*` 根底下,收尾會整個清。我跑完後沒有自己的殘留。

**② 時間預算。已讀,無 finding。**
- `t_loop_next_lens_scope_marker_odd_kinds` 約 7.3 秒,`t_loop_next_lens_scope_loose_code_ids` 約 3.3 秒,兩者離 180 秒上限都有大於 25 倍的餘裕。
- 前者每個案例多跑一次不讀輸出的 `run`(`rt`),用來取 stderr 驗 traceback。這只是多花約 2 秒,不構成問題。
- 範本測試新增的逐句斷言與變異斷言只對 `templates.md` 這種小檔做 `find`/`replace`,耗時可忽略。

**③ 記憶體與二次方工作。已讀,無 finding。**
- `_tpl_dispatch_fences` 逐行掃描,仍是線性。`_rm_literal_missing` 每個斷言重新解析一次,檔案很小,不構成問題。
- 新增的 `⑥變異` 迴圈用 `t.find("\n" + head)`。找不到時 `at=-1`,會產生沒變動的文字,檢查變紅而不是假綠,也不會崩。
- `loop next` 的 `_is_toolchain_repo` 只做一次 `is_file()` 判斷,沒有走訪或讀檔。

另一個小觀察,不構成 finding:`$TMPDIR` 底下有 343 個舊的 `gctl-*` 目錄,不是這輪造成的,我沒有動。

最高等級 clean,blocking 0 條。
