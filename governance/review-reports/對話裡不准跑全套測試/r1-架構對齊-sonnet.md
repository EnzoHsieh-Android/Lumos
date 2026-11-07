severity: major

## F1 擋下判斷的位置寫得不夠死,照字面放會被預設切片搶先分流而擋不到
severity: major
blocking: 是
引句:「參數解析完、`_isolate_environment()` 之前呼叫;擋下時印訊息到 stderr、回 2,不建暫存目錄、不載入任何測試」
佐證 file: `scripts/test_lumos.py:49686`(`_fanout_wanted` 在 `main()` 裡、`_isolate_environment()` 之前,不帶條件的全套已經在這裡被分流給 `_fanout_main`);`scripts/test_lumos.py:49397`(帶 `LUMOS_FANOUT_CHILD` 的子程序一律不切,也不會回頭到擋下判斷)

「_isolate_environment() 之前」有兩個可放的位置。放在 `_fanout_wanted` 之後,最常見的「不帶任何參數」全套已經走進 `_fanout_main`,擋下函式碰不到。只有 `--shard` 和 `--serial` 的情形擋得到,S1 的第一列會紅。這個專案的鄰居是在 `main()` 開頭依序處理:先清環境,再嚴格解析參數,擋下檢查跟在 `keyword_pos` 合併之後。擋下檢查必須明寫在 `keyword_pos` 合併之後、`_fanout_wanted` 之前。這是結構性的落點問題,不算風格,所以 blocking。

## F2 逃生門的命名與留帳慣例跟鄰居不同
severity: minor
blocking: 否
引句:「不寫任何檔(執行器不准改工作目錄,測試本身會驗工作目錄乾淨)」
佐證 file: `scripts/lumos:41535`(`LUMOS_SKIP_LINT_NEW` 命名為 SKIP、只認 `== "1"`);`scripts/lumos:56928-56930`(`LUMOS_SKIP_REREAD_CHECK` 略過時印一行並 `_gate_event_or_warn(...,"skipped-env",...)` 留帳)

鄰居的逃生門有兩個共同點。一是統一叫 `LUMOS_SKIP_*`,新逃生門叫 `LUMOS_ALLOW_FULL_SUITE`。二是略過時都寫一筆 `skipped-env` 到治理帳。「執行器不准改工作目錄」是這個專案裡 `test_lumos.py` 自己的特殊情況,理由成立,但計劃沒說這是跟 `LUMOS_SKIP_*` 慣例不同的刻意例外。

- 命名:`test_lumos.py` 本身沒有任何逃生門,同層沒有對照。`ALLOW` 和 `SKIP` 語意相反,可以接受,但要寫一句理由。
- 留帳:要在「天花板」第 2 條(「只印一行、不留帳」)旁補明這是刻意偏離 `skipped-env` 慣例的例外,並寫出「為什麼這裡不能寫帳」。

## F3 擋下訊息格式與既有「擋下:…」單行慣例略有差異
severity: minor
blocking: 否
引句:「訊息三段:發生什麼(對話裡不准跑全套)、為什麼(約 8 分鐘、超過工具上限、推送前閘會自己跑)、怎麼辦」
佐證 file: `scripts/test_lumos.py:49650-49665`(`擋下:--suite keys 要配 --keys…`、`擋下:--shard … 不合理` 等,一律單行以「擋下:」開頭、`file=sys.stderr`、`return 2`)

回傳碼 2 和輸出到 stderr 與鄰居一致。多行訊息如果第一行不以「擋下:」開頭,就跟鄰居不一致。訊息第一行要寫成「擋下:…」,後面再接三段。

## 四問

1. **分層與依賴方向**:放在 `test_lumos.py` 的 `main()` 入口、讀環境變數、回傳 2,跟鄰居一致。新增 `_chat_full_suite_block(args, env)` 做成獨立判斷函式,跟 `_fanout_wanted`(`scripts/test_lumos.py:49391`)的形狀一致,沒有跨層。需要的是明寫呼叫點(F1)。範圍 4「`CLAUDECODE` 跟清 `GIT_*` 同一段」有小偏差:`GIT_*` 是在 `main()` 開頭、參數解析前清掉(`scripts/test_lumos.py:49618`),擋下判斷要用解析後的參數,所以 `CLAUDECODE` 只能在判斷之後才拿掉,不會在同一段。
2. **命名與錯誤處理**:`LUMOS_` 前綴和 `== "1"` 嚴格比對,跟 `LUMOS_SKIP_*` 的「只認 1」一致。回傳碼 2 和 stderr 一致。差異是逃生門名稱和留帳(F2),以及訊息首行格式(F3)。
3. **第二種做法**:判斷「是不是推送前閘」用 `LUMOS_PUSH_ATTEMPT`,判斷「是不是切片子程序」用 `LUMOS_FANOUT_CHILD`。兩個標記都是專案已有的(`scripts/hooks/pre-push:393`、`scripts/test_lumos.py:49388`),沒有另造第二種判斷法。逃生門的第二種慣例(只印不留帳)已在 F2 說明,不算引入新判斷法,所以不獨立升 major。⚠ `CLAUDECODE` 在專案裡原本只用於 `scenario_probe.py:1162` 的 `pop`,拿它當「在對話裡」的標記是新用法。但專案沒有現成的對話判斷法,所以不算第二種。
4. **落點**:`lands_in: Systems/測試執行器` 合理。該節點的 `about_code` 列了 `scripts/test_lumos.py`,它是這支檔的家,前一份相關計劃 `測試總檔預設切片_計劃` 也落在同一篇。這篇節點已在 repo 裡(提交 36697056a),參考資料說「會談目錄還沒有這篇」只是會談目錄較舊,不影響落點。

不對齊共 3 條
