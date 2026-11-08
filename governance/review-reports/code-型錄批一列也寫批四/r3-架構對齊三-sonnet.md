severity: minor

審查範圍:`r3-repair.patch` 的修補差異,對照 `r3-snapshot.patch` 與既有檔。結論是結構都對,只有一處寫法跟同檔鄰居不同(minor)。

## 問 1 分層與依賴方向

錯誤訊息從常數 `_B4_SKIP` 組字串,做法跟 check.py 其他訊息一樣,沒有跨層呼叫。

引句:「        return ["第四批通電批次寫了接電標籤,但口徑判成還沒接上(段裡註記" + "、".join(_B4_SKIP) + ",或規則預設關、沒有規則碼)"]」

- 對照一:`configs/ast-grep/kotlin-android/check.py:215` 的 `"決策表表頭缺欄:" + "、".join(missing)`,同樣是中文前綴加「、」串接。
- 對照二:同檔 `:338` 的 `"觸發字含常用字:" + "、".join(bad)`,寫法一致。
- `_B4_SKIP` 就定義在同一支檔(`:119` 附近),`_batch4_problems`(`:350` 起)直接讀它,沒有越檔。
- 同一條修補把 `batch4_expected_tags` 的 docstring 改成指向 `_B4_SKIP`,不再抄一份字表。這是收斂,不是新增。

這一問沒有不對齊。

## 問 2 命名與寫法

**STATE-5 與 ARCH-17 的註記**:格式跟既有註記一致。

引句:「androidx:UnsafeLifecycleWhenUsage(只管 finally/catch 碰 UI,不管單純呼叫 launchWhenStarted)」

- 對照:`skills/kotlin-idioms/checks-catalog.md` 既有 `(只管 finally/catch 碰 UI,不管單純呼叫 launchWhenStarted)`,以及 `(相關:只管 repeatOnLifecycle 要在 onCreate、onViewCreated 呼叫,擋不到根本沒包,2026-11-08 讀官方檢查頁)`。STATE-5 補的是第二種,跟既有的「(相關:…,日期 讀官方檢查頁)」寫法相同。
- 兩條補的註記都落在 `_B4_SKIP` 認得的字樣上(「相關」「只管」是照算接電的說法),沒有發明新字樣。

**測試斷言**:跟鄰居一致。

引句:「    check("r2 折入 自檢錯誤訊息列出口徑的每個排除字樣", all(w in msg for w in ck._B4_SKIP),」

- 對照:`scripts/test_lumos.py:129156` 起的兩條新斷言,用的是同函式 `t_kt_catalog_batch4_wiring`(`:128` 起)既有的 `check(名稱, 條件, 詳情)` 形式。
- 它們沿用既有的 `ck._batch4_problems`,同樣是透過 `ck` 去讀 check.py 的私有名稱。

**新的 REVISIT 行**:寫法對,放的位置跟同檔鄰居不同。

引句:「REVISIT:2027-02-08 接了 CI 範本的 Android 消費專案跑過一次 Android Lint 之後,拿型錄標批四(CI 範本:Android Lint)的每列壞例真跑一次」

- 寫法:`REVISIT:YYYY-MM-DD 一句要做什麼`,符合專案 CLAUDE.md 鐵則 4,括號裡附了為什麼。
- 位置:它是檔尾的獨立正文行(`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:96`,不縮排)。同一份筆記既有的兩條 REVISIT 都在 summary 區塊裡、縮排兩格(`:27`、`:47`)。
- 為什麼這算不對齊:同檔的慣例是放 summary。
- 為什麼只標 minor:別篇有正文層的先例,`Systems/macrobenchmark-adapter.md:65` 就是正文層 REVISIT,而且 `:28` 在 summary 也有一條。所以不是第二種做法,只是跟同檔鄰居不同。

1. 新 REVISIT 放在正文檔尾,不跟同檔 `kotlin規則包.md:27`、`:47` 的 summary 內縮排寫法
severity: minor
blocking: 否

## 問 3 第二種做法

沒有在測試或別處另立排除字表。

引句:「    段裡帶排除註記(check.py 的 _B4_SKIP)或預設關的規則不准被標成已接電。口徑住在 check.py(代碼審 r1 架構席:不在測試裡另立一套)。」

- 新斷言用 `ck._B4_SKIP` 當唯一來源,逐字比對錯誤訊息與型錄〈輸入與口徑〉。
- 我 grep 了 `scripts/*.py` 與 `scripts/lumos`,`_B4_SKIP` 只出現在 check.py 本身和 `scripts/test_lumos.py` 的引用與註解,沒有另一份「待查、預設關、相近、opt-in」的字表。
- 型錄的口徑句與筆記 WHY 是給人讀的文字,對 `_B4_SKIP` 的同步由新斷言守住。WHY 行雖列了詞,但沒有機械檢查它,屬於說明文字,不算第二種做法。

不對齊共 1 條,其中 major 0 條
