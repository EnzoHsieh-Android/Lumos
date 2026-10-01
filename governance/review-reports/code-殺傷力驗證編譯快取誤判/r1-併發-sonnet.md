severity: minor

# 併發-sonnet:時序與資源鏡頭

## F1 每條配方固定多等約 1.7 秒、粗精度檔案系統或時鐘往回撥時每條最壞約 12 秒,沒有整體上限也沒有關閉開關
severity: minor
blocking: 否
引句:「time.sleep(1.0)」
佐證:file: `scripts/lumos:13751`(patch 中 _kill_after_write;審材外未另有呼叫端逾時,grep `guard kill` 在 scripts/lumos 找不到外層 subprocess/timeout 包裝)

1. 實測(sim.py,照 patch 邏輯在 macOS APFS 模擬:wait→寫→after_write→跑 `true`→記 r→wait→還原→after_write):平均 1.69 秒/條配方,全是新增的等待(每條配方寫兩次,每次都要等進下一秒)。73 條約 2 分鐘;原本測試很快的節點會從近乎 0 變成 2 分鐘級。可接受,但沒有關閉開關。
2. 理論最壞:每次 wait 最多 3 秒、每次 after_write 最多 3 次 sleep(1.0)=3 秒,每條配方 2 次 wait+2 次 after_write ≈ 12 秒,73 條 ≈ 15 分鐘。觸發條件:只到 2 秒的檔案系統(utime 取整後仍不超過 floor),或時鐘往回撥使 mstate["w"]/["r"] 停在「未來」——因為 w 只在成功時更新,之後每條配方都耗盡 3 秒 wait 與 3 秒重試且全判弱證據,不會自癒。屬極端環境,結果有被標 `_mtime_unsure` 變弱,行為誠實,只是慢。
3. 逾時不被吃掉:m_timeout = max(b_elapsed*5, floor) 只包 _kill_run 本身,等待在外面,不影響 killed/timed_out_weak 判定;LUMOS_KILL_TIMEOUT_FLOOR 測試覆寫不受影響。
4. 同機兩個 guard kill 併發:mstate、mt_warned 都是函式區域變數,worktree 路徑各自唯一,沒有共享檔或鎖,互不影響;兩個同時跑也不會互相拉長等待。
5. 時鐘往回撥:_kill_wait_new_second 有 3 秒 deadline,不會空轉成死迴圈(核對通過)。
6. 次要:Linux 上 mtime 取自核心粗粒度時鐘,可能比 time.time() 落後數毫秒,秒界線附近會讓 after_write 第一次讀回判不過而多 sleep 1 秒再 utime,結果仍正確只是多等 1 秒。
建議(非必要):對 mstate 加整組累計等待上限,或在連續兩次 after_write 失敗後本組直接放棄等待、只標弱證據,避免最壞 15 分鐘。

最高等級:minor
