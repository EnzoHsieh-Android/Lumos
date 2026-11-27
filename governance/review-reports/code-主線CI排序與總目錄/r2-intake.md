# r2 收貨紀錄(code-主線CI排序與總目錄)

材料:r2-repair.patch(285be5974..4dd4ff18b,78 行,r1 折入的修正,兩席主看)、r2-snapshot.patch(Lumos/main..4dd4ff18b,171 行)。兩席全數交回後才一次從逐字稿存檔,兩份都已是正規化格式、引句全數錨定。架構對齊席 clean。

修補因果:G1 不是 r1 修補造成的(檔案層排序在 r1 原始改動就沒有測試守,正確性席也寫明「修正前就有」),--regression-set none。

## 發現與去向

| id | 席 #條 | 原報 | 一句 | 去向 |
|---|---|---|---|---|
| G1 | 正確性 #1 | minor | 「同一個資料夾的檔案照名字排序」沒有測試守,拿掉 sorted(files) 照綠 | 折:補 f/src 底下 A.kt、B.kt 兩支不同套件,上限 1 時正序與檔案倒序都只收到 A.kt 的套件 |

## 機械重現

| id | 做法 | 結果 |
|---|---|---|
| G1 | 拿掉 _choice_cov_src_pkgs 的 sorted(files),原測試照綠(席位實測);補斷言後同樣拿掉,新斷言紅({'fb'} 對 {'fa'}),還原後全綠、git diff 正式程式無殘留 | HIT |

## 先查世界

- PRIOR-ART:G1 跟 r1 F1 同屬「測試情境碰不到被守的那一支」——照 lumos-project-notes〈實作測試品質〉,每個被宣稱的行為各有一個會紅的案例;資料夾層與檔案層排序是兩個獨立行為,各造一個碰得到的情境。Python 官方 os.walk 文件:filenames 清單順序同 os.scandir、未定義,https://docs.python.org/3/library/os.html#os.walk 。
