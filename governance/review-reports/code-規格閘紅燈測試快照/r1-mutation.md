# r1 修補後改壞驗證(2026-11-03)

每道只改 scripts/lumos 一處、清 __pycache__、跑對應測試、還原。52 道全數翻紅;第一次跑時「沒動帳也讀」沒翻紅,查出外層提早返回與裡層讀帳條件重複互相掩護,拿掉外層重複判斷後兩道重跑都翻紅。

✓ 翻紅 不做行差、整本終點帳都算  [t_tq_guard_redbase_absent_unchanged] 9 passed, 1 failed
✓ 翻紅 欄位形狀不驗  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 路徑出界不驗  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 孤兒檔不查  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 沒提交救法不講提交與 -f  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 孤兒檔不講刪掉  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 總量不分辨  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 sha 不比  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 版本不驗  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 內嵌超長行不驗  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 內嵌路徑不驗  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 不偵測還沒提交  [t_tq_guard_redbase_unreadable] 19 passed, 1 failed
✓ 翻紅 只取最早一份  [t_tq_guard_redbase_chain] 4 passed, 1 failed
✓ 翻紅 只比最後一份  [t_tq_guard_redbase_chain] 2 passed, 3 failed
✓ 翻紅 照 ts 排  [t_tq_guard_redbase_chain] 4 passed, 1 failed
✓ 翻紅 不丟重複的新測試規則  [t_tq_guard_redbase_chain] 4 passed, 1 failed
✓ 翻紅 分岔點已有照套紅燈版  [t_tq_guard_redbase_moved_or_missing] 6 passed, 1 failed
✓ 翻紅 同名多載照猜  [t_tq_guard_redbase_moved_or_missing] 6 passed, 1 failed
✓ 翻紅 搬家不要求唯一  [t_tq_guard_redbase_moved_or_missing] 6 passed, 1 failed
✓ 翻紅 補讀不處理配不平  [t_tq_guard_redbase_moved_or_missing] 6 passed, 1 failed
✓ 翻紅 終點無斷言照比  [t_tq_guard_redbase_weakened] 13 passed, 1 failed
✓ 翻紅 紅燈版不接進比對  [t_tq_guard_redbase_weakened] 7 passed, 7 failed
✓ 翻紅 同檔不快取(比對端)  [t_tq_guard_redbase_absent_unchanged] 9 passed, 1 failed
✓ 翻紅 讀工作目錄的紅燈版  [t_tq_guard_redbase_reads_tip] 2 passed, 1 failed
✓ 翻紅 指紋不帶子規則與 token  [t_tq_guard_redbase_waive] 3 passed, 2 failed
✓ 翻紅 寫入端不分紅綠全存  [t_spec_gate_redbase_written_on_red] 27 passed, 5 failed
✓ 翻紅 逾時照存  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 多檔照存  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 不驗 UTF-8  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 寫入端超長行照存  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 被忽略的測試檔照存  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 不去重  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 判紅後不比 sha  [t_spec_gate_redbase_written_on_red] 30 passed, 2 failed
✓ 翻紅 條款不合併  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 Python 照收  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 身分不帶平台  [t_spec_gate_redbase_written_on_red] 0 passed, 2 failed
✓ 翻紅 5 MB 量原文  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 紅燈版路徑被忽略照寫  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 紅燈版資料夾不擋符號連結  [t_spec_gate_redbase_written_on_red] 28 passed, 1 failed
✓ 翻紅 上一份不擋符號連結  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 上一份不驗格式  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 判綠不排最後  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 讀不出帳不出聲  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 同檔不快取(寫入端)  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 沒講整支會提交  [t_spec_gate_redbase_written_on_red] 31 passed, 1 failed
✓ 翻紅 判綠不寫事件  [t_spec_gate_redbase_skips_after_green] 4 passed, 2 failed
✓ 翻紅 寫入前不看判綠  [t_spec_gate_redbase_skips_after_green] 5 passed, 1 failed
✓ 翻紅 補跑步驟沒那句  [t_spec_gate_redbase_skips_after_green] 5 passed, 1 failed
✓ 翻紅 分岔點等於頂端就看整本帳  [t_spec_gate_redbase_skips_after_green] 5 passed, 1 failed
✓ 翻紅 簿記清單沒加  [t_spec_gate_redbase_bookkeeping] 2 passed, 1 failed
✓ 翻紅 沒動帳也讀(改裡層讀帳條件,重跑)  [t_tq_guard_redbase_absent_unchanged]
✓ 翻紅 空樹起點照用(重跑)  [t_tq_guard_redbase_absent_unchanged]
