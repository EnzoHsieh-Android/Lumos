# code-殺傷力配方當場試跑-r4 r3 收貨紀錄(r2 修正差異,上限輪)

機械:兩份 report-normalize 已正規;quote-check --spec r3-delta.patch 兩份全數錨定;refcheck 全 ok。

編號:t1–t3 = r3-通才-opus.md F1–F3;u1 = r3-架構對齊-sonnet.md F1。

| id | 怎麼試 | 結果 |
|---|---|---|
| t1 | 讀碼:r2 讓寫 kill-log 經 `_kill_esc`,gov 讀 kill-log(`json.loads` 後原樣印)沒跟著處理;席位附新舊版對照重現 | HIT(讀碼+席位重現):壞字元寫得進帳,gov 印就崩;帳進版控會散出去 |
| t2 | 讀碼:`_kill_esc` 用 `\u{ord(c):04x}`,U+FFFF 以上是 5 碼 | HIT |
| t3 | 對照網格:file、platform 帶替身字元仍崩,Issue 漏列 | HIT(文件) |
| u1 | 讀碼:其他帳本寫入都直接 json.dumps | HIT |

到上限(第 3 輪)有 major,攤人;Enzo 裁「收手、改回原寫法後推」。處置:4 條全折——寫 kill-log 與印 `--json` 兩行改回主線原寫法(跟 Lumos/main 逐字比對一致;t1、t2、u1 一起消失),拿掉替身字元的測試格,Issue 照實測重寫清單並記兩個坑(t3)。t1、t2 是 r2 修補造成的。改回之後相關 7 組測試全綠(guard_kill_only_ids 25、kill_recipe_check_matches 92、json_purity 6、rc_precedence 4、doctor_p2_lists_survived 13、add_try 7、fix_check_recipe_rerun 7)。
