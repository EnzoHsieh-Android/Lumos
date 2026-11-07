# code-計劃依據來源必填 r4 收貨(2026-11-07)

範圍:修補差異 `5076190af..ffef27ca9`,排除卷證目錄(r4-repair.patch,1135 行)一包,七席全新都看整份。上限三輪跑滿後人裁加開(cap-decision extra-round、跑滿回顧已記)。修正關卡 r3 通過。

## 收貨三道

- 正規化:七份皆已是正規化格式。
- quote-check:邊界、資源、合約、通才、架構對齊全數錨定;正確性、資安 clean、沒有引句。
- seat-check:材料只有一份 patch。

## 前輪驗收

- 第三輪 20 條:六席各自核對自己那幾條,皆修好(正確性實跑表格兩列、先提交五種情境;資源量到 8000 行 7.4→0.01 秒、單行 8 萬個 10.55→0 秒;合約把 F1–F6 的改壞重做,皆翻紅;架構對齊確認不再自列 ls-tree、行數收成一份、解碼一致)。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 四架1 | 讀碼:`_plan_blob` 自開 `git cat-file blob`,既有 `_nodehome_cat_blobs_capped` 有大小上限 | HIT |
| 四邊1 | 席位實跑:出處格含 NUL,`_plan_src_miss_reason` 的 `os.path.realpath` 丟 ValueError | HIT |
| 四約1、四通2 | `Systems/規格閘.md` 第 62 行仍寫「行中的要後面同一段真有 --> 才算」與 `git ls-tree` | HIT |
| 四資源1 | 席位實跑:130MB 檔峰值 494MB→1217MB | HIT |
| 四約2–4 | 席位改壞實驗(相關子集全綠) | HIT |
| 四邊2、四通1 | 席位實跑:`.GIT/config`、`Lnd/b.py` 經連結仍叫先提交 | HIT |
| 四架2、四邊3、四通3、四通4 | 讀碼與席位實跑 | HIT |

## 先查世界

PRIOR-ART:讀單支 blob 另開一條路——專案紀律「補防護工具先找既有」:`_nodehome_cat_blobs_capped` 的說明寫「上限放在批次讀取這一層,不另起查法」,採用它。
PRIOR-ART:路徑含 NUL——Python `os.path.realpath`/`os.lstat` 遇內嵌 NUL 丟 ValueError(https://docs.python.org/3/library/os.html#files-and-directories 「ValueError ... embedded null byte」;`pathlib.Path.is_file` 會吞掉);採用:先擋 NUL、os 呼叫接 OSError 與 ValueError。
PRIOR-ART:容器內的 HTML 區塊(四邊3、四通3)——CommonMark 0.31.2 第 5 章容器區塊:引用區塊與清單項內的內容另按容器規則解析,區塊註解隨容器結束而結束(https://spec.commonmark.org/0.31.2/#container-blocks )。不採:要照規格做就得另寫容器解析,本迴圈剛在手冊立了「沒有規格依據就不新增規則」,照頂層規則判的偏差多數是多擋,少擋的只有刻意把表藏進清單項區塊註解的寫法(見下方更正);寫成計劃裡的刻意偏離。

## 分組與去向(輪內有 major;原報 major 全折,原報 minor 三條附理由放行)

- H1 讀 blob:四架1(major);四資源1、四約3(minor)→ 改走 `_nodehome_cat_blobs_capped`,行數只計數,補 CRLF 測試。
- H2 擋下原因:四邊1(major);四邊2、四通1(minor)→ 先擋 NUL、`.git` 大小寫不分、大小寫掃描涵蓋連結。
- H3 連結讀法:四架2(minor)→ 修補代理查明既有介面拿不到連結的物件編號,要改 `_nodehome_list`/`_drift_list` 共用行為(牽連漂移檢查整串呼叫端)才做得到;改判放行,見下。
- H4 筆記:四約1(major);四通2、四約2(minor)→ 規格閘 WHY 改成現況並補綁定。
- H5 測試與清理:四約4、四通4(minor)。
- 放行:四邊3、四通3(minor)——容器內區塊註解照頂層規則判,不另寫容器解析(理由見〈先查世界〉第三條),計劃偏離列補一句。更正:編排者原寫「偏差只多擋」不成立——修補代理實測一種會少擋的寫法(整張表放進清單項、用 `- <!--` 開頭的區塊註解藏起來,規格上看不到、檢查卻當成有表);要刻意這樣寫才會發生,屬威脅模型排除的刻意偽造,照放行。
- 放行:四架2(minor)——連結檔名在 git 裡存成 NFD 時讀不到目標,只會多擋、不會放錯;要動共用的列樹函式才修得到,為一條 minor 動共用行為不划算。
