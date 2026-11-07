severity: minor

第六輪正確性席 F1 已修好(實跑確認)。我用真鉤子的 `_git_status_entries` 建了一個 monorepo 來跑。專案是 `sub/` 時,兄弟目錄 `other/b.py` 被刪、`top.py` 被刪或改名,都不再被回傳。同名前綴的 `sub dir/`(目錄名含空白)也不會被誤收。專案根就是 repo 根時,全部條目照回。

PATH 清洗段也實跑過。測了 `::`、前導或結尾冒號、`.`、空字串、`env -u PATH`、含空白或 `*` 的絕對項,結果都符合預期。

另外,圖譜根在 `project_root/docs` 底下,所以出口過濾不會把 `graph_touched` 的筆記條目濾掉。

本輪鏡頭 2、3、4(`shell=False`、過濾器關閉、`_lens_git` 加 stdin)的程式碼不在這份補丁裡。補丁在 `scripts/lumos` 只動了一個說明字串,所以這幾題沒有可審的改動。

### F1 安裝腳本取到相對路徑的 python 就整個拒絕,不往後找
- 場景:`install.sh`、`get.sh` 等四支安裝腳本不洗 PATH。PATH 有 `.` 或空項,而目前目錄剛好有一支 `python3.14`(例如在某個 venv 的 bin 目錄裡跑安裝)。
- 輸入:`PATH=".:/usr/bin:/bin"`,`LUMOS_PYTHON_SEARCH_DIRS` 指到一個放了可執行 `python3.14` 的絕對目錄,目前目錄也有 `./python3.14`。
- 實際:`_lumos_any_python` 回傳失敗,訊息是「找到的 python 是相對路徑 ./python3.14 … 不用」,接著印「找不到任何 python」。
- 預期:跳過相對那一支,繼續找固定位置或 `python3`,用到那支絕對路徑的 3.14。
- 原因:`_lumos_any_python_find` 取到第一個命中就 return。新增的 `case` 是在 find 回傳之後才判斷,不會回頭試下一個候選。
- 後果:裝有合格 python 的機器被安裝腳本誤擋,不過訊息講明了原因。三支 git 掛鉤先洗過 PATH,不會遇到這條。
- 補丁、計劃和圖譜筆記都只講「當找不到」,沒提「不往後找」這個代價。

severity: minor
blocking: 否
引句:「取到的不是絕對路徑就當找不到(PATH 有空項或相對項時 command -v 會回 ./python3.14 這種,解到目前目錄的檔;代碼審 r6 資安席 F1)」

總結:最嚴重是 minor(安裝腳本遇到相對路徑的 python 就不往後找,誤擋合格機器),會擋 0 條。
