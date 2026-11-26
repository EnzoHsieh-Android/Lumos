severity: minor

整體說明:我逐 hunk 讀過 `scripts/lumos` 與 `scripts/test_lumos.py` 的改動,也追了 `_kill_measure_singles` 與 baselines 的呼叫端,沒有找到會讓程式做出錯誤行為的 major。下面 4 條都是測試保護不足或筆記過期。m1、m2 兩個變異我實際改壞跑過,相關測試仍全綠。m3、m4 有翻紅。m5 因我誤刪工作目錄而沒跑成,所以不列。

**固定席(圖譜鏡頭)**:這次改到 `guard-kill.md`(直接影響面)、`規格閘.md`、計劃 `選擇點存活回指條款_計劃.md` 與 Issue 筆記。計劃與 guard-kill 的 PITFALL 已更新。`規格閘.md` 內仍有兩條沒跟上的舊描述,見 finding 3、4。guard-kill 的 INVARIANT 沒有被破壞。

**逐項查證(沒有 finding)**
- `_choice_cov_src_pkgs` 讓更多測試被判為「可信」。因為 Robolectric 專案若覆蓋壞掉,所有專案類別都是 0,所以擴大範圍不會讓壞掉的覆蓋被放行。
- 空殼結果檔略過。`junit()` 先丟 `zero_cases`,再丟 `suite_error`;帶 `errors` 的空殼經 `ghost_suite` 仍被拒。
- 快取基準的 `setdefault`,鍵與 `_kill_measure_singles` 一致。
- 掛覆蓋逾時改為等不掛重跑綠才斷路,邏輯正確。

severity: minor
blocking: 否
`scripts/lumos`(`_choice_cov_base_read`):驗證條件 `doc["rc"] != 0 or doc["to"]` 沒有測試守著。
引句:「or type(doc.get("to")) is not bool or doc["rc"] != 0 or doc["to"]):」
失敗場景:我把 `doc["rc"] != 0 or doc["to"]` 拿掉(只留型別檢查),`-k choice_merge_stray`、`-k choice_cov_robo_exec`、`-k choice_cov_resume` 全部 `5 passed, 0 failed`。`.base.json` 存了 rc=1 或逾時的非綠基準時,續跑會把它當綠基準放回 baselines。guard-kill 的 `b_rc != 0` 分支就不會判 abort,而是照樣拿壞基準去套壞法。新增的測試只驗「取快取後不再逐支重量」這一條正向路徑,缺損、型別錯與非綠這幾個拒收分支都沒有案例。

severity: minor
blocking: 否
`scripts/lumos`(`_CHOICE_COV_ROBO_ENV`):`SdkEnvironment` 這項沒有測試。
引句:「"org/robolectric/internal/SdkEnvironment")   # 每支測試開跑前建 Android 環境的類別」
失敗場景:我把 `SdkEnvironment` 從元組拿掉,`-k choice_cov_robo_exec` 仍 `5 passed, 0 failed`。新測試只用 `AndroidTestEnvironment` 與 `AndroidSandbox$1`。另有一個方向性風險:Robolectric 判定從「任何 `org/robolectric/` 類別」縮窄成三個固定類別名,未來版本改名時,Robolectric 測試會被當成非 Robolectric。若它又剛好專案類別數是 0,這個 0 就被信成「真的沒經過」而直接記存活。以前的寬判定是偏向「不明」較安全的方向。這條風險有 `--cov-audit` 抽查兜底。

severity: minor
blocking: 否
`docs/lumos-toolchain-knowledge/Systems/規格閘.md`:原有的 WHY 行(補修內容沒碰到)還在描述舊的專案類別與 Robolectric 判定。
引句:「WHY:覆蓋可信看專案類別有紀錄數:lumos 自己用 Python 讀 JaCoCo exec 二進位格式」
失敗場景:該行仍寫「數類別名所在套件是改到的原始檔 package 宣告」和「有沒有 `org/robolectric/` 開頭的類別」。實作已改成平台主程式全部 package,以及 `AndroidTestEnvironment` 等三個環境類別。同一篇新增的 PITFALL 與這行互相矛盾。下一個 session 的 AI 若照這行寫,會改回舊行為。這是會誤導決策的筆記漂移。

severity: minor
blocking: 否
`docs/lumos-toolchain-knowledge/Systems/規格閘.md`:續跑快取那一行沒補 `.base.json`。
引句:「WHY:覆蓋的續跑快取存每支測試的覆蓋資料檔(不是分析結果),放 .lumos/note-audit/choice-cov/<at_sha>/」
失敗場景:實作現在每支測試另存同名 `.base.json`,而且舊快取沒有它就整份作廢重量。筆記只講存 `.exec`,沒有提 base.json 及其作廢規則,也沒有測試守著這個行為。

總結:最高等級是 minor
