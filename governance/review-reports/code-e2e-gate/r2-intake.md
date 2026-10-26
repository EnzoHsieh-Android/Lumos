# r2 收貨與去向(2026-10-27)

材料:r2-snapshot.patch(0701350..ce46398a,3209 行)加修補鏡頭 r2-repair.patch(0aecbf90 → ce46398a)與 r2-repair-binding.json。7 席全新代理:正確性(C)、邊界(B)、資源(P)、合約與文件(K)、通才(G)、架構對齊(A)、資安(S)。七份報告從逐字稿存檔;架構對齊席只做了 report-normalize --write 的純格式搬移(列表式等級搬成獨立行)。quote-check 七份全數錨定、refcheck 全部對得上。

這輪有 major,照代碼審規則 accepted 必須為空:28 條全折(修正前 ce46398a → 修正後見 r2-fix.json)。

## 重現(觀察與判準分開驗)

| id | 重現 | 結果 |
|---|---|---|
| C1、G1 | 舊分支(分岔點與 feat 都沒有 e2e 段、主線後來加了)只改 README:ce46398a 回 blocked「App 程式卻跟分岔點不一樣」;補 t_android_e2e_gate_cfg_sides 第一組,修前紅 | HIT |
| C2、K3 | 提交整段刪掉 e2e:擋下的接下來印 git merge <主線>、在意的原因說 App 不一樣;補同一支第二組三條,修前紅 | HIT |
| C3 | 提交的紀錄 runs.result=maybe:擋下印 waive 指令,waive 回 2 寫不進去;補同一支第三組,修前紅 | HIT |
| B1 | 紀錄是 20 萬個 [:waive --list 與 --ack --all 印 RecursionError 的 traceback;補 t_android_e2e_record_scan ①,修前整支 EXCEPTION | HIT |
| B2、K1 | 501 份紀錄:lumos 與掛鉤都不講有幾份沒讀;最新一份太大時 lumos 佔名額、掛鉤不佔,兩邊筆數不同;補 ②四條,修前 EXCEPTION | HIT |
| P1、P2 | 讀紀錄沒有總時間上限(席位實量 500×2MB 大清單掛鉤 37.9 秒、doctor 179 秒);補 ③,budget=0 時兩邊都要講沒讀到幾份,修前不支援 | HIT(席位量測 + 測試翻紅) |
| K2 | 一份嚴格規則讀不懂、寬鬆規則數得到待看的紀錄:--ack --all 回 2 停在半路;補 ④,修前紅 | HIT |
| B3 | app_dirs ["app","app/src/main"]:被推送端算指紋說 app/src/main 不存在;補 t_android_e2e_input_guards ⑤,修前紅 | HIT |
| B4、G3 | waive --commit 給 600 字的 z:原樣寫進紀錄;給了指紋不給 --commit 時存 null;補 ②三條,修前紅 | HIT |
| P3 | 十萬支檔對一萬兩千條功能路徑:舊歸屬判斷 96.4 秒;補 t_android_e2e_owner_index,修前紅 | HIT |
| P4 | LUMOS_TTY_TIMEOUT=1e10 通過檢查;補 ③,修前紅 | HIT |
| G2 | 400 個情境、250 字分支名:_gate_event_fit 量的行沒有 ref,寫出超過 4096;補 ④,修前 _gate_event_fit 不收 ref 參數 | HIT |
| S1 | CI=1 跑 code-loop check:放行、治理帳沒有任何 android-e2e 事件;補 t_android_e2e_gate_ci_escape,修前紅 | HIT |
| S2 | 檔名帶換行與 ESC 的 App 檔:擋下原因原樣帶控制字元;補 ①,修前紅 | HIT |
| K4 | S10 條款寫「提交這支紀錄」,程式印「這一版的查證紀錄還沒提交」 | HIT(讀碼) |
| K5 | 把 pre-push 逃生路的 Android 那段刪掉、AI 待看行改字頭,接線測試照綠;補兩條斷言 | HIT(席位改壞實測) |
| K6 | 四處還寫五道或五句 | HIT(grep) |
| A1 | 全檔只有這一道用例外帶結果提早結束 | HIT(讀碼) |
| A2 | 安全證據的結果欄位叫 gate_code,這一道叫 code | HIT(讀碼) |
| A3 | 掛鉤複本改了名、內容改寫過,兩邊一致只靠 7 份樣本的行為測試 | HIT(讀碼) |
| A4 | 正式程式讀 LUMOS_E2E_GATE_BUDGET;安全證據閘的預算測試在行程內給參數 | HIT(讀碼) |
| S3 | 擋下訊息印現成的放行指令,沒有終端時 AI 一步放行 | HIT(計劃明講的設計) |
| S4 | 被推送提交自帶的 waivers 不驗來源、--commit 不驗 | HIT(前者為刻意偽造帳本欄位,範圍外;後者同 B4) |

## 去向(根因分組,一條規則補一組)

1. 兩端設定比較與擋下訊息:C1、G1、C2、K3、C3 → 折。兩端都沒有 e2e 段也算設定一樣;拿掉 e2e 段不叫人合主線、在意的原因改講拿掉了驗收設定;紀錄讀不懂時叫人修好或刪掉那份紀錄、不印放行指令。
2. 讀工作目錄紀錄的規則:B1、B2、K1、K2、P1、P2、A3 → 折。doctor、--ack 與開場掛鉤同一套寬鬆讀法(只 json.loads、接住 RecursionError、太大的佔名額不讀、總時間 3 秒、講沒讀到幾份);--ack 一份寫不進去不停在半路;嚴格讀法 _e2e_load_json 也接 RecursionError;掛鉤的 _e2e_ai_pending_one 跟 lumos 同名、逐字相同,測試比語法樹。
3. 外來或人給的輸入:S2、B4、G3、S4(--commit 那半)、P4、G2、B3 → 折。擋下原因的檔名過 _esc_clean;--commit 只收解得到的提交、存 40 碼、沒給存 HEAD;等待秒數上界一天;_gate_event_fit 收 ref、量的跟寫的同一行;app_dirs 一項包住另一項時每一項都算看到。S4 的另一半(提交裡自填的放行)屬刻意偽造帳本欄位,範圍外不加機制,寫進這裡留痕。
4. 出口留帳:S1 → 折。CI 出口也記一筆治理帳 ci,提醒行講明不是 CI 就清掉變數;不改「CI 不跑這道」的設計。
5. 效能:P3 → 折。歸屬判斷改成按改到的檔每一層前綴查表。
6. 跟鄰居的做法:A2、A4 → 折(欄位改叫 gate_code;預算不讀環境變數,測試在行程內給 budget,刪掉 _e2e_env_secs);A1 → 折成 Systems/android-e2e-acceptance 的 WHY 行(為什麼用例外帶結果、對外介面跟鄰居一樣)。
7. 設計取捨的縱深:S3 → 折。放行指令旁加一行講明 AI 放行的後果、放行前先跟使用者講。
8. 文件:K4、K5、K6 → 折。條款改成程式印的那句;接線測試補逃生路與 AI 待看行兩條斷言;四處五道/五句改六。

## 修補因果(載體帶 --regression-set)

- 有證據的修復回歸:C1、G1(r1 加的設定比較讓兩端都沒有 e2e 段的放行消失,修前 not-required、修後 blocked,兩席都實跑兩版)、C2、K3(r1 新加的拿掉 e2e 段擋下沿用合主線提示)、B2(r1 新加的 500 份上限沒有測試)、B4、G3(commit 欄位 r1 新加)、K2(r1 把 doctor 改成寬鬆讀法,跟 --ack 的嚴格寫入不一致)、G2(r1 新加的 _gate_event_fit 呼叫沒傳 ref)。
- 原有漏查(修前修後同樣):C3、B1、B3、K1、K4、K5、K6、P1、P2、P3、S2、A1、A3、A4。
- P4:席位寫成修復回歸,但它自己的說明是修前只擋 ValueError、同樣不處理過大的值;判原有漏查(修補沒封全,不是修補造成)。
- S1:席位寫成修復回歸(r1 把出口併到最後,擋下也被改寫成 ci);修前 CI 出口排在讀設定之前,殘留 CI 變數時同樣整道不判、同樣不留帳,判原有漏查。
- A2、S3、S4:設計或命名,不分回歸。
