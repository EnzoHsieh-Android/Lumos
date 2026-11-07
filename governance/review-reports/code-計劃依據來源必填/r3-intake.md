# code-計劃依據來源必填 r3 收貨(2026-11-07)

範圍:修補差異 `3edab28be..5076190af`(r3-repair.patch,1410 行)一包,七席全新都看整份。修正關卡 r2 通過。這輪是 high 上限第 3 輪。

## 收貨三道

- 正規化:七份 `report-normalize` 皆「已是正規化格式」。
- quote-check:正確性、邊界、資源、通才、架構對齊全數錨定;資安席 clean、沒有引句;合約席 6 句有 1 句(F6)錨不到——那句引的是計劃第 34 行,這輪修補沒改到那行、不在 patch 裡,編排者另在計劃檔機械重現(見重現表)。
- refcheck:正確性、邊界、合約的 missing 是測試裡的示範路徑(`scripts/a.py` 等),不是佐證;其餘對得上。
- seat-check:七席皆只觀測,材料只有一份 patch。

## 前輪驗收

- 第二輪 23 條:合約席把 r2 F2、F3 的改壞重做,皆翻紅;F1(規格閘舊 PITFALL)、F4、F5 核對修好(F5 另指出目錄 `scripts/` 應擋仍未進預期值表——併入 G6 一起看)。
- 合約席另做 45 道改壞、跑完 34 道,8 道全綠,即合約 F2–F5。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 三約1 | `grep -n 'd12\|20 秒' Projects/高風險測試證據加嚴_計劃.md`:d12 仍 `valid: true`,第 161、255 行仍寫逾時 20 秒 | HIT |
| 三約6 | `git show 5076190af:<計劃>` 第 34 行仍寫「交給既有的 `_validate_repo_ref`」 | HIT |
| 三約2–5 | 席位改壞實驗(`-k psrc` 120 過 0 敗) | HIT |
| 三正1、三通3 | 席位實跑:行中未閉合 `<!--` 跨過表格列,下一列被吃掉 | HIT |
| 三邊1、三通4 | 席位實跑:超長 `:行號` 讓 `int()` 丟 ValueError | HIT |
| 三通1 | 席位讀碼:`_plan_first_days` 只留 `_計劃.md`,`_expected_requirement` 拿不到其他路徑的日期 | HIT |
| 三架1、三架2、三架3 | 讀碼對照既有 `_nodehome_list`/`_drift_list`、`_validate_repo_ref` | HIT |
| 三資源1、三資源2、三通2 | 席位實跑:8000 行每行未閉合 `<!--` 約 7.9 秒,平方成長 | HIT |
| 其餘 minor(三正2、三邊2、三通5) | 讀碼與席位實跑 | HIT |

## 先查世界

PRIOR-ART:HTML 註解第二次被打穿(同一個判讀連兩輪)——GFM 0.29-gfm 表格擴充:「Each row consists of cells containing arbitrary text, in which inlines are parsed」,每列各自解析行內內容,行內註解不會跨列(https://github.github.com/gfm/ 4.10 Tables);同規格 Raw HTML 第 638、639 例顯示段落內的原始 HTML 可以跨行。採用:整類拿掉跨行分支——行內 `<!--` 只在同一行判:同一行有 `-->` 才算註解、蓋掉那段;沒閉合照 CommonMark 0.31.2 6.6 照一般文字留著(編排者原裁「沒閉合蓋到行尾」與 GFM 每列各自解析的依據矛盾,會留下正確性 F1 的誤擋,修補代理指出後改裁);行首區塊照 CommonMark 0.31.2 第 2 型保留。刻意偏離:段落內跨行的行內註解,後幾行當看得見的文字(出處欄是表格,偏離碰不到;寫進計劃)。排除:在跨行分支裡再加「遇到表格列、清單項就停」的字面判斷(又是一層靠字面的補丁,下一輪同類會再被打穿)。
PRIOR-ART:樹清單第四份實作、行號算法複製——專案紀律「補防護工具先找既有」:共用 `_nodehome_list`/`_drift_list` 與 `_validate_repo_ref` 的讀行邏輯,不另立一套。
PRIOR-ART:決策取代——專案紀律第 2 條,開頭欄位用 `lumos decision-add`/`decision-supersede` 改,不在正文標註了事(d11 被 d12 取代時就是這樣做)。

## 分組與去向(輪內有 major,全數折入)

- G1 註解形狀:三正1、三通3、三約2(major);三通2、三資源1、三資源2(minor)
- G2 行號與行數:三邊1、三架2(major);三通4、三約3、三約4(minor)
- G3 樹清單:三架1(major);三架3、三通5、三約5(minor)
- G4 首次加入日:三通1(major)
- G5 「先提交」提示誤報:三正2、三邊2(minor)
- G6 筆記:三約1(major);三約6(minor)

修補派給乾淨的修補代理,臨時目錄 `/tmp/lumos-seat-work/戊線修補r3/`。
