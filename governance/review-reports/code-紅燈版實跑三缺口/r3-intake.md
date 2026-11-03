# r3 收貨紀錄(code-紅燈版實跑三缺口)

## 收貨

- 兩席全新(單reviewer-sonnet、架構對齊-sonnet)審 r3-repair-review.patch(修前 06e101684 → 修後 e0603d082 的修補差異,程式、測試、筆記那一包,434 行;來源 r3-repair-binding.json;待驗案例 r3-behavior-cases.md)。報告從逐字稿原樣存檔,兩份都已是正規化格式。
- 引句:架構對齊席全數錨定(當載體);單審席 2 句有 1 句錨不到(D1 的引句跨三行),依規不採信,改由編排者機械重現撈回(下表)。
- 兩席交回期間 repo 沒被席位改動:`git status` 只有兩份新報告;`git reflog` 頂端是編排者自己的提交 e684d25ef。單審席留下的暫存目錄(/tmp/lumos-seat-work/code-紅燈版實跑三缺口/單reviewer-sonnet,4 支探針腳本)收齊後已刪。

編號:單審席 Finding 1–2 記 D1–D2,報告「其他」段的文件不一致(S3 條款仍寫去掉前綴,沒有獨立 severity 行)記 D3;架構對齊席 Finding 1–2 記 E1–E2(E1 標 ⚠ 判不準)。共 5 條;major 1 條(D1),其餘 minor。

## 編排者重現

| id | 案例 | 結果 | HIT/MISS |
|---|---|---|---|
| D1 | 單平台,S1 綁 `[test:gone:fee_jvm]`、S2 綁 `[test:fee_jvm]`;規格閘留痕後刪掉 gone:fee_jvm、fee_jvm 綠,推送前驗收(scratchpad probe_d1.py,用 test_lumos 的 fixture) | push rc 0、實際只跑 `jvm fee_jvm`、輸出「留痕裡的 2 支測試全綠(fee_jvm、gone:fee_jvm)」 | HIT(撈回錨不到的引句) |
| D2 | `assertEquals("a b", f())` 改 `"a  b"` | 讀碼:`_tg_statements` 用 `re.sub(r"\s+", " ", …)` 連字串裡的空白一起壓;席位兩版實跑都回空 | HIT |
| D3 | 計劃 S3 寫「照去掉前綴的名字跑」 | grep 成立,做法 2 在 r2 已改 | HIT |
| E1 | `t.endswith(":" + m)` 是第二處讀「平台:名字」格式 | 讀碼成立 | HIT |
| E2 | `_spec_gate_push_one` 拿常數 `_ENV_MISSING_WHY` 比,判紅那邊走存取函式 | 讀碼成立 | HIT |

## 歸因(修前 06e101684、修後 e0603d082)

| id | 歸因 | 依據 |
|---|---|---|
| D1 | 有證據的原有漏查 | 席位兩版實跑同為 rc0 綠;r2 想修的頂替沒修乾淨(比對表只收 bound 條款) |
| D2 | 有證據的原有漏查 | 席位兩版實跑同為空 |
| D3 | 有證據的修復回歸(文件) | r2 改了做法 2 的單平台說法,沒同步 S3 |
| E1 | 有證據的修復回歸 | 後綴比對是 r2 修補新寫的 |
| E2 | 有證據的修復回歸 | 具名欄位的 why 是 r2 修補新加的,推送前那邊仍讀舊常數 |

regression_set:D3、E1、E2。

## 到頂與人裁

r3 是 standard 的第 3 輪(上限 3),仍有 major(D1)。依規停下攤人;2026-11-03 Enzo 裁「拿掉這段、換形狀(推薦)」:整段拿掉「改回單平台時比對條款名字後綴」的相容邏輯(同一類 r2、r3 連兩輪 major),改回單平台後舊留痕讀不到時照擋並明講是設定改了,不記逃逸;順手修 minor,再派一小輪只驗這次修補。Enzo 另補一條規則:「兩輪都碰到就上網找」。

## 先查世界(兩輪都碰到的兩類,2026-11-03)

- 單平台比對舊留痕(r2 A1/C3、r3 D1):測試報告工具的測試識別碼由框架資訊算出,重構或升版後會變、那段歷史從頭開始(Allure:https://allurereport.org/docs/how-it-works-test-identifiers/);要接續就建明確的新舊對照表(Orangebeard:https://orangebeard.io/en/ongecategoriseerd/how-can-you-preserve-test-history-when-tools-change/)。兩家都不用猜名字後綴接。本案照此:身分格式變了(設定從多平台改單平台)就明講要重建留痕,不猜。
- 字串裡的空白(r1 R1、r2 C2/A2、r3 D2):語言的詞法規則是「詞與詞之間的空白可互換,字串裡的不行」(Python 語言參考 Whitespace between tokens:https://sethna.lassp.cornell.edu/DM/Documentation/Python/ref/whitespace.html);比對程式碼時通用做法是切詞後只壓字串外的空白、字串原樣保留,`git diff -w` 正因為不分這兩種而會藏住字串裡的改動(https://ikit.app/blog/ignore-whitespace-diff-hidden-bug)。本案照此:斷言抽取改成只壓字串外的空白(同 `_tg_ident` 用的那支掃描)。

## 根因分組與處置(全數折入)

| 組 | 根因 | id | 處置 |
|---|---|---|---|
| 1 | 改回單平台的相容靠猜名字(r2 切冒號、r3 比後綴),連兩輪被打穿 | D1、E1、D3 | 換形狀:拿掉後綴比對(`_spec_gate_push_match` 刪掉、`_spec_gate_push_fill` 回到只在多平台建);單平台時留痕名字帶冒號、在測試索引找不到 → 照擋、講明「多半是設定從多平台改回單平台前寫的,照現在的設定重跑規格閘」,不跑測試、不記逃逸;S3 條款同步 |
| 2 | 斷言抽取連字串裡的空白一起壓 | D2 | 斷言文字只壓字串外的空白(同一支 `_C_STRIP_PAT` 掃描認字串) |
| 3 | 環境原因字串兩條讀法 | E2 | 推送前改成看原因是不是表裡任一格的 why(集合),拿掉 `_ENV_MISSING_WHY` 常數 |
