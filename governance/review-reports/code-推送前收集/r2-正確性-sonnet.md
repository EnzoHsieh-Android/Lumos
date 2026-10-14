severity: clean

已讀修補的掛鉤與主程式兩份,沒有找到「某道擋下被吞掉、變成放行」的路,也沒有其他 finding。實驗放在指定的暫存目錄,做完已刪。

- **放行站點是否都經收尾:已讀,無 finding。**
  - `_codeloop_guard_verdict` 裡所有 `return` 不是走 `_fin`(即 `kg.fin`),就是走 `kg.hit` 回來的 `_stop`。
  - 不帶旗標時,`hit` 回傳原 dict(非空,為真),所以 `if _stop: return _stop` 等於原本的早退。
  - 帶旗標時,`hit` 回 `None` 繼續往下;之後的放行 dict 進 `_codeloop_kg_finish`,不會蓋掉清單裡已記下的擋下。
  - `reason_kind` 從呼叫端搬進 `hit` 之後,不帶旗標時輸出不變。
- **收集模式下 pitfalls 失敗:已讀,無 finding。**
  - `kg.lint_on_pf_fail` 只在帶旗標時照跑新增告警閘,擋下被記下。
  - 接著 `_fin(pf_fail)` 把放行 dict 併進非空清單,結果仍是擋下;`kg.tier` 保持 `unknown`。
  - 清單是空的時候才是 fail-open 放行,跟修補前相同。
  - `_codeloop_pitfalls_tier` 的例外與 JSON 解析仍在 try 裡。
  - guard_verdict 內留下的 `_sys`、`graphctl`、`_sp`、`_json` 都還有用到,不是死碼。
- **`elif` 後的兩種逃逸:已讀,無 finding。**
  - 合約測試紅優先,缺留痕那一筆在兩句同時出現時不記,這是設計取捨。
  - 只缺留痕時,「tier=high 且」仍會記一筆。
  - 逃逸帳是 `|| true`,不影響擋不擋。
  - 擋下的記錄走 `pp_record_block`,與逃逸無關;`_cl_n` 為 0 時至少補一筆。
- **`pp_keep_log` 在紅時搬檔失敗:已讀,無 finding。**
  - 在 `/bin/bash` 3.2 實測 TMPDIR 不存在、來源檔不存在、正常三種情形。
  - 前兩種印出「(沒能存…)」且不留空檔,正常情形回路徑。
  - 後面仍是 `exit 1`,不是放行。
- **子殼收 TERM:已讀,無 finding。**
  - 在 `/bin/bash` 3.2 用兩組 `( run_group … ) &` 加兩片 `sleep` 模擬。
  - 對外層送 TERM 後,外層 rc=143,4 個 sleep 全數收掉,`_pids` 這個 local 陣列在陷阱裡可見。
  - 若子殼單獨被砍,回傳 143,父層判為 `_rc=1`,仍是擋下。
  - INT 被背景子殼忽略,由父層陷阱轉成 TERM 送出,是通的。
- **版本探測:已讀,無 finding。**
  - 基準版(e0da694b)的 `scripts/lumos` 裡沒有 `--keep-going` 字樣,所以舊版不會誤判成新版。
  - 讀不到檔時 `_CL_KG=0`,退回舊的記一筆。
  - 代碼審判定的版本探測不再執行 lumos,從 `pp_stop_if_signaled` 清單移掉是一致的,測試也改成斷言不執行 `--help`。
- **其餘:已讀,無 finding。**
  - `pp_record_block` 的重導向包法、`tee … >&2 2>/dev/null`(BSD tee 開不了檔仍照樣輸出)、`grep … 2>/dev/null`(讀不到時退回全套,方向安全)。
  - `push-summary` 的 `split("\n")` 與 `_note_audit_root`(非 git 專案回 2,掛鉤退簡版後仍 exit 1)。
  - 漂移測試的 reason_kind 抓取正則涵蓋所有產生點。
- **資料狀態五問:** 空(count>0 但暫存檔讀不到)、少行、含特殊分隔字元的 ref、暫存目錄被刪、舊版 lumos,最後落點都是擋下或較保守的全套,沒有變成放行。

最高等級 clean,blocking 0 條。
