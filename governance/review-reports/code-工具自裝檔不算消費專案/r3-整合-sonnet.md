severity: minor

## 逐 hunk 讀完 diff 後的兩個新發現

### F19 about_code 新正規化只補了寫側,舊的排序加分(讀側)仍用另一套不解析 `..` 的正規化
severity: minor
blocking: 否 — 只影響固定席排序加分(軟訊號),不影響正確性/推送閘,也非 r3 引入的退步
引句:「about_code 一項的比對鍵:斜線統一、去 ./ 與 ..(純字面,不查檔案」
佐證:file: `scripts/lumos:19631` `_impact_mark_about` 裡的 `_norm = lambda s: str(s).replace("\\", "/").strip().removeprefix("./")` 只剝開頭的 `./`,不解析 `..`;file: `scripts/lumos:19615` `_impact_about_counts` 用同一顆殘缺 `_norm` 建計數表。
實測(讀不到「已修好的 about_code 值」的具體重現):寫一篇 `about_code:\n  - src/../src/a.ts` 的筆記,呼叫 `_impact_about_counts`/`_impact_mark_about` 目標 `src/a.ts`,`about_hit` 完全沒被標上(親測,見下方 repro)。這個欄位本身現在(靠新 `_about_code_norm`)已經會把新寫入正規化乾淨,但舊資料或直接手改檔案仍可能是 `../` 形式,兩套正規化不一致就是內部不一致,依規要報。

### F20 cmd_new 掛 verified_by 那段只接 OSError,新的同一行清單 ValueError 會穿透、蓋掉「筆記已建好」的提醒
severity: minor
blocking: 否 — 純訊息誤導(rc2 看起來像全部失敗,但新驗證筆記其實已落盤),非本輪新退化(基準版 3cc12430 對任何 scalar 形式的 verified_by 一樣會穿透同一段,只是觸發條件更寬)
引句:「工具看不懂同一行裡的逗號」
佐證:file: `scripts/lumos:12237-12238` `cmd_new` 的 `for rel in sys_rels:` 迴圈只 `except OSError as e:`,不接 `ValueError`/`RuntimeError`;外層 `scripts/lumos` `main()` 對 `cmd_new(...)` 才有 `except (ValueError, RuntimeError) as e: print(f"擋下:{e}")`。
親測重現:目標 Systems 筆記 `verified_by: "[[Verification/A]], [[Verification/B]]"`(同一行清單),跑 `lumos new verification X --systems Systems/Target.md` → 新驗證筆記檔案★已經寫到磁碟★,但整個指令印出「擋下:verified_by 寫成同一行的清單…」、rc2,完全沒有 `cmd_new` 內建的「筆記建好了,但…沒寫成功」提醒。這個路徑本輪沒被觸碰,是既有缺口,不算 r3 新增的洞,附上是因為此輪審查鏡頭明確要求驗這個交互。

## 前兩輪修法驗收

F1:修到 — 反轉 `_is_vendored_path` 成前綴比對後,`t_pitfalls_diff_ignores_vendored_toolchain`⑤與`t_doctor_s3_ignores_vendored_toolchain`②b 立即翻紅(親測)
F2:修到 — lint 過濾層仍套同一支 `_is_vendored_path`,反轉同一支函式後⑦相關情境跟著失守,親測有殺傷力
F3:修到 — 反轉刪除行分支不傳 `_skip_vendored` 後,⑥(純刪行棧別觸發)立即翻紅(親測)
F4:修到 — `set` 已整條拒收 about_code(⑧親測擋下且原值不動),append/remove 改走單一值轉清單
F5:修到 — 反轉 `_about_code_path` 呼叫後,⑤翻紅且真的把 `/etc/hosts` 寫進 about_code(親測,危害重現)
F6:修到 — LIST_KEYS 內只剩 append/remove 一套規則,`cmd_set` 不再分流處理清單欄位
F7:修到 — append 走 `fmt_list_item` 既有引號邏輯,④(含「: 」路徑)測試通過
F8:修到 — 讀 `scripts/lumos:1434-1456`(doctor S4)確認 about_code 僅加分不建連結,與事故筆記描述一致
F9:修到 — 全檔只剩一處 `_VENDORED_TREE_DIRS` 定義,安裝/移除/授權測試三處共用
F10:修到 — 命名與訊息已與鄰居(`_about_code_norm`/擋下句式)一致
F11:修到 — `_stack_ext_counts` 每目錄只算一次 `relpath`,不重算
F12:修到 — ④(工具鏈本體不可跳過)測試仍在且通過
F13:修到 — 反轉 `_list_scalar_value` 回舊版原始字串比對後,⑨b(引號/多空白繞法)立即翻紅(親測)
F14:修到 — 拿掉 cmd_append 的「已經有」早退後,⑩立即翻紅(親測)
F15:修到 — 拿掉 `_about_code_path` 大小寫/NFC 檢查後,⑬立即翻紅(親測)
F16:修到 — 同一次反轉一併證實⑪(`src/../src/a.ts` 與 `src/a.ts` 去重)翻紅(親測)
F17:修到 — 反轉 cmd_remove 的正規化比對後,⑫立即翻紅(親測)
F18:修到 — 授權測試改吃 `getattr(m, "_VENDORED_TREE_DIRS", ())`,不再手寫第二份目錄清單

## 風險掃描清單驗證

manifest 那 1 條(`scripts/lumos:17660` 命中 `open(`):誤報 — 該行是 `_stack_changed_ok` docstring 裡描述「命中 open(...)」這個掃描目標的中文說明文字,不是真正開檔案的程式碼;diff 裡其餘 `open(` 新增全在測試 fixture 裡故意寫進暫存 repo 的假樣本檔,同屬誤報。

總結:最高 severity minor,blocking 共 0 條
