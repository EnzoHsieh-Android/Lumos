### e-f1 「兼任 duals」一名兩義:真兼任(≥2 席重名)與命名辨識歧義(關鍵字撞兩家)觸發條件語意皆異
severity: major
引句:「兼任 duals、unknown 降級、席數短缺 shortfall 五種」
佐證:file: `scripts/lumos:5103`
佐證:file: `scripts/lumos:5115`

### e-f2 「兩出口」低估實際出口:rid 綁定後到終點前還有三個 return 2,真 rN 走到會靜默跳過對帳
severity: major
引句:「PASS/FAIL 兩出口前的共用收尾」
佐證:file: `scripts/lumos:10131`
佐證:file: `scripts/lumos:10151`

### e-f3 log 寫入的局部失敗語意未定義——外層 try/except 吞掉後續異常,最該被看見時反而漏記
severity: major
引句:「異常行真的印出時,append 一行到」
佐證:file: `scripts/lumos:4707`
說明:一輪多異常時第一條 log 炸=整段吞;兩季覆核判準恰是這個 log,失敗集中在異常密集時=誤判「從沒發生」而錯誤退場。

### e-f4 「22475-22480 兩條」行號指錯函式:那段是 t_loop_next_roster;真正同帶斷言在 t_loop_status_roster_check 22508-22514
severity: major
引句:「16 條中 14 條零改動、22475-22480 兩條依」
佐證:file: `scripts/test_lumos.py:22475`
佐證:file: `scripts/test_lumos.py:22508`

## 查過乾淨
--disposal 與 --settle CLI 本就互斥,[S4] 除外與 [S1] 無條款衝突;16 條機械數確認。
