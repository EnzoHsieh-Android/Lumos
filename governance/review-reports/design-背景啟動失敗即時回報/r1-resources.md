severity: major

F1：`Popen` 與 `unlink` 雙故障仍會留下無工作者的鎖，使下一次呼叫重新等到逾時；設計只限制文案，沒有規定可供後續呼叫辨識的失敗狀態或復原行為。

severity: major

severity: major

blocking: 是

引句:「清不掉鎖時訊息也不能宣稱鎖已不存在。」

file: `governance/review-reports/design-背景啟動失敗即時回報/r1-snapshot.md:31`

file: `scripts/lumos:33921`

file: `scripts/lumos:33951`

重現/因果：令 `subprocess.Popen` 拋 `OSError`，並令該鎖的 `Path.unlink()` 拋 `PermissionError`；依 S1，本次會回 rc 2，但鎖仍在。隨即在無快取下再次呼叫 `_lens_wait_or_warm(..., deadline=0)`：`_take_lock()` 因鎖存在而回未取得，接著直接走 `_lens_report_lock_timeout()`，回 rc 5；鎖也因專案已取消過期自動接手而持續殘留。可在 `t_lens_spawn_failure_reports_error` 加入上述雙故障後的第二次呼叫，斷言不得退化成 `timed_out=true`；目前照設計字面會翻紅。設計需明定身份安全的失敗標記／後續立即分類或停用暖機的處置，並以測試釘住；不能只要求提示「檢查鎖位置」。

總結：最高 severity high，blocking 1。
