# 第四輪收貨(拆兩份後加開的一輪,範圍:原生配置排行)

六席(正確性、邊界、整合、資源併發、回滾、架構對齊,都是 sonnet、沒參與前三輪的新代理)報告到齊後一次寫入;六份都已是正規化格式、quote-check 全數錨定、refcheck 全 ok(回滾席一處是計劃標了將新增的檔);審查席沒動 repo;邊界席建過臨時目錄,已刪。

## 發現編號

正確性 d1–d13、邊界 f1–f11、整合 j1–j7、資源併發 l1–l7、回滾 o1–o7、架構對齊 q1–q6(順序照各席報告的 F 編號),共 51 條。

## 重現與查證

| ID | 重現 | 結果 |
|---|---|---|
| l1 | 讀收集腳本第 40 行 `class Terminated(Exception)`:繼承 Exception,`except Exception` 會接住它 | HIT |
| f1 | 本機 trace_processor(/Users/enzo/.local/bin/trace_processor)跑 `select 'a"b,c' as a, 1 as b;`,輸出 `"a"b,c",1`:字串裡的引號不跳脫 | HIT |
| d1、f5 | 上網查 AOSP libunwindstack MapInfo.cpp 的 GetFullName:elf_start_offset 非 0 而且有 soname 時回傳 `name + '!' + soname`(https://android.googlesource.com/platform/system/unwinding/+/refs/heads/main/libunwindstack/MapInfo.cpp) | HIT(外部原始碼) |
| l4、f3、o1 | 讀 e2e 範本:T_LONG 預設 3600(LUMOS_E2E_LONG_TIMEOUT),收集整支是一個 step,逾時回 None 後 device_stuck 並 break | HIT(三席獨立一致) |
| j1、d2、q4 | 讀計劃第 2 步:沒打開、沒宣告測試資料、版本不夠都寫 unsupported;結果檔沒有可分辨的欄位 | HIT |
| l6 | 席位引 v57.2 trace_config.proto:欄位名是 data_source_stop_timeout_ms,計劃寫成 stop_timeout_ms(第三輪編排者查證時寫錯) | 採信(外部原始碼) |
| d3、f2 | 席位引 v57.2 unwinding.cc 與 libunwindstack:function_name 原樣送出,只在 FormatFrame 顯示時才 demangle | 採信(外部原始碼,兩席一致) |

## 根因分組與處置

- 組 A 中斷與例外(l1、l2、l3、l5、l7、f4、j4、o1 第 3 點、q5):撤掉「先寫第一段結果檔再原子替換」,回到既有合約(被中斷不寫結果檔、回 2,跟「同一個 run-id 已有結果檔就擋」與檔頭說明一致);第二段 `except Terminated: raise` 之後才 `except Exception`;離開第二段前一律 abort_record;第二段結束與 cleanup 都不再停 App(heapprofd 客戶端會自己關記帳,r3 查證),cleanup 不需要套件名。→ 折。
- 組 B e2e 單步逾時(l4、f3、o1):e2e 範本用 LUMOS_STABILITY_STEP_BUDGET_S 傳上限,收集腳本照第一段實際秒數預估第二段,不夠就不跑、寫 failed「時間不夠」;第一段的判定不被連累。→ 折。
- 組 C 沒打開與打開但失敗分不出(j1、d2、q4、o7):結果檔與 lumos 鍵都加 `enabled`;只在 enabled 為 true 且 status 不是 ok 時印「沒跑成」;skill 遇到缺鍵或 enabled 但沒拿到排行都照舊手動錄。→ 折。
- 組 D 一支範本三種輸出(j2、d13、f7):一條語句用 UNION ALL 回 site、rows、stat 三種列,第一欄 kind 區分;rows 給「有沒有錄到」,跟排行是否為空分開。→ 折。
- 組 E csv 引號(f1):文字欄位在 SQL 裡 hex() 輸出、Python 解回,照既有逗號切法;撤掉 csv.reader(順帶解掉第三輪架構對齊席的兩種解析並存)。→ 折。
- 組 F APK 內嵌 .so(d1、f5):.so 名稱取最後一個「!」之後;S5 加一次 extractNativeLibs=false 的建置。→ 折。
- 組 G mangle 名與比對(d3、f2、d10):名字比對改成 mangle 名的精確值與前綴(_Znw、_Zna、_ZNSt、_ZNKSt),用 GLOB;lumos 照存的名字印。→ 折。
- 組 H 歸屬細節(d4、d5、d6、d9、f8、f9、f10):系統路徑加 /vendor/ 等;沒有符號時按呼叫點歸併、S12 限有符號;ERROR 偽框架記「?」;呼叫者跳過 libart.so;同名 .so 的說法改準;並列加系統旗標;rel_pc NULL 寫 +0x?;名字截 500 字元。→ 折。
- 組 I 輸出細節(d7、d8、d11、d12、f6、f11、j5、q3):抬頭寫明只含開錄之後配的;S5 正常版容許一輪的配置量;d2 的 context 改成排行的理由;sites 形狀不對整段不採用(照鄰居慣例,不逐項丟);ok 但空的印一行;設定範本不設 continuous_dump_config;沒給 --stability 時鍵的值寫死。→ 折。
- 組 J 驗證位置與命名(q1、q2):型別在 _macrobench_stab_optional_err、跨段對照在 _macrobench_stab_top_err;"@default" 在 reference.md 寫明。→ 折。
- 組 K 測試工具與落點(j3、j6、q6):第 7 步列出要一起改的假 TP 分流、_ms_sql 假表、兩份檔名清單、假 adb、e2e 預算變數;三篇 Systems 的改動寫明,lands_in 加 Systems/android-e2e-acceptance。→ 折。
- 組 L 回退細節(o2、o3、o4、o5、o6):因金流退回時連鍵一起刪;殘留範本會被當專案程式;刪檔改成先列再寫字面路徑;共用解析函式寫進回退;對外送出那條改成錄檔本體不離開、彙總名字會進收據。→ 折。
- 組 M 停錄欄位名與拉檔(l6):改成 data_source_stop_timeout_ms;拉檔 T_SHORT 的代價寫進〈實務隱患〉。→ 折。

全部 51 條折入,沒有放行。

## 到頂裁定

這是拆兩份後加開的第四輪,仍有 major(l1–l4、f1、f3、f4、j1、j2、d1、d2、o1)。攤給使用者裁,使用者 2026-10-28 選「折完就收,進實作」:折入這輪全部發現、記接受風險,剩下的對錯交給實作時先紅的測試與高風險代碼審(含資源席)抓。

## 修補因果

l1–l3、l5、f4、j4、q5 落在第二輪折入時新寫的「先寫結果檔、包 try/except、cleanup 停 App」;f1、y1 那條的 csv.reader 是第三輪折入新寫的;l6 的欄位名是第三輪編排者上網查證時寫錯的;j1、d2 的「打開了但不是 ok」是第二輪折入新寫的;其餘(e2e 逾時、APK 內嵌 .so、mangle 名)前幾版就有對應的空白。
