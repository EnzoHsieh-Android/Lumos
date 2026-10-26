severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/769b2e46…json.warming` 不存在,所以沒有鎖要處理。

實驗環境:`git clone` 到 `/tmp/lumos-seat-work/code-e2e-by-feature/鏡頭3-邊界與輸入-sonnet/`。其中 `lum` 是修後 787dd51b,`lum-pre` 是修前 9e21d491,`proj` 是自造的假 Android 專案(`login`、`home` 兩個功能)。版本用 `git -C <目錄> rev-parse HEAD` 確認。

## F1 工作目錄裡已暫存的改名只算新路徑,舊路徑所屬功能漏挑
severity: minor
blocking: 否
- file: `scripts/lumos:63108`(`_porcelain_z_paths`),被 `_e2e_changed_files` 的 `files.update(_dirty_non_bookkeeping(root) or [])` 呼叫。
- 失敗場景:`git mv app/src/login/A.kt app/src/home/A2.kt` 還沒提交,就跑 `android-e2e select --changed`。
  - 結果只挑到 `home.main`、`home.alt`,沒挑到 `login.basic`。
  - 原因是 `_porcelain_z_paths` 遇到改名只收新路徑,舊路徑被跳過。
  - 同一個改名提交之後,走 `diff --no-renames` 就會挑到 `login.basic`。同一個改動,提交前後挑出的功能不同。
  - 刪除也一樣:`git rm` 的檔案在工作目錄是 `D` 單一條目,會挑到;只有改名漏掉。
- 歸因:有證據的原有漏查。修前 9e21d491 與修後 787dd51b 同一案例結果相同,都是 `["home.main","home.alt"]`。
引句:「    files.update(_dirty_non_bookkeeping(root) or [])」

## F2 效能測試方法名允許 `$`,但換進 `sh -c` 時會被當變數展開
severity: minor
blocking: 否
- file: `scripts/lumos:40374`(`E2E_BENCH_NAME_RE`),範本 `scripts/templates/android-e2e-run.sh` 的 `st.step("macrobench", ["sh", "-c", cmd], …)`。
- 失敗場景:情境列 `macrobench: ["Foo$Bar"]`,`macrobench_cmd` 裡 `{{TEST}}` 沒用單引號包。
  - 設定檢查通過,但 `sh -c 'echo run Foo$Bar and $HOME/x'` 實際輸出 `run Foo and /Users/enzo/x`。
  - 內部類別方法名會被截成 `Foo`,`$HOME` 之類會展開成環境變數內容。
  - 不能注入指令:`; & ( ) 空白 \ #開頭 -開頭 換行` 都被擋下(實測)。
  - 所以洞只限於「值被改寫」,不是指令執行。
- 修法選項:regex 拿掉 `$`,或範本把名字用 `shlex.quote` 後再換進指令。
- 歸因:修補有效但留了這一個洞。
  - 修前 lum-pre 對 `Foo$(id)`、`a;b`、`#x`、`a b`、換行、`-x`、`a&b` 全部放行;修後除 `$`、`#`(非開頭)、`.` 外全擋。
  - `Foo$Bar`、`$HOME`、`a$$` 在兩版都放行。
  - 這一條屬有證據的原有漏查(修補只收窄、沒收到 `$`)。
引句:「E2E_BENCH_NAME_RE = re.compile(r"[A-Za-z0-9_.$][A-Za-z0-9_.$#]*")」

## F3 `features.paths` 允許寫法不正規的路徑,收了卻永遠對不到
severity: minor
blocking: 否
- file: `scripts/lumos:40428` 起的 `_e2e_feature_head_err`,比對在 `_e2e_changed_features`。
- 失敗場景:`paths: ["app/./src/login"]`、`["app//src/login"]`、`["."]`、`["./"]` 都通過設定檢查。
  - 比對用 `_e2e_under(f, _e2e_norm(x))`,`_e2e_norm` 只去頭尾的 `./` 和 `/`。
  - 改 `app/src/login/A.kt` 時,輸出 `unmatched: ["app/src/login/A.kt"]`,`login.basic` 沒被挑。
  - 設定看起來對,卻靜默不生效;`"."` 寫成「整個專案」也一樣不生效。
  - `app/src/login/`、`./app/src/login`、前後空白會被正規化,正常。
  - `..` 與絕對路徑有被擋(實測)。
- 歸因:有證據的原有漏查。修前修後同案例同結果。
引句:「    bad = next((x for x in f["paths"] if Path(x).is_absolute() or ".." in Path(x).parts), None)」

## F4 `--changed` 改到共用 flow 或門檻檔時,只要同時有別的命中就不提醒
severity: minor
blocking: 否
- file: `scripts/lumos:40495` 起的 `_e2e_changed_features`。
- 失敗場景:同時改 `.maestro/shared/common.yaml`(`runFlow` 叫的共用 flow,不在 `e2e.flows`)和 `app/src/login/A.kt`。
  - 輸出 `unmatched: []`,共用 flow 的改動沒被提醒。
  - 計劃把共用 flow 和門檻檔算進指紋,改了就該重跑;`unmatched` 的警語寫的卻是「推送前的整套跑照樣會驗到」。
  - 只改共用 flow 或門檻檔時,會因對不到任何功能回 2,訊息有列檔名,這種情況沒問題。
  - 問題只在「混合命中」時被默默丟掉。
- 歸因:有證據的原有漏查(修前修後同案例結果相同)。是否要提醒屬設計取捨,嚴重度保守。
引句:「        elif _e2e_norm(f) in all_flows or any(_e2e_under(f, _e2e_norm(d)) for d in e2e["app_dirs"]):」

## F5 `--case` 搭 `--changed` 時,`--changed` 對不到就整個擋下,連指名的情境也不跑
severity: minor
blocking: 否
- file: `scripts/lumos:40545`(`_e2e_select`)。
- 失敗場景:乾淨工作目錄跑 `select --case login.basic --changed`。
  - 回 `擋下:--changed 對不到任何功能:改到的檔 (沒有改動)`,rc 2。
  - 指名的 `login.basic` 本來可以跑。
  - 合約(S23)只寫「一個功能都對不到時回 2」,沒寫與 `--case` 並用時的語意。
  - 屬語意不清,不是資料損壞。
- 歸因:未判定是否算缺陷。我沒對修前版另外查證合約意圖,只確認兩版行為相同(都擋下)。
引句:「        hit, unmatched, note, err = _e2e_changed_features(root, e2e, feats)」

## 邊界輸入逐項結果(正向主張,修後 lum,同案例修前見括號)
- `--feature ""` 的行為:argparse 回「expected one argument」,範本改成空字串交給 select 後回「沒挑到任何情境」。
  - 兩者都是 rc 2,不會誤整套跑。修前版的範本已有同樣解析。
- 其他參數實測:
  - `--feature=`、`--feature login,,home`、重複 `--feature login`、`' login '`、`--case login.basic,` 都正確。
  - `--case login`(無點)、`--case a.b.c` 都回「不認得」,且列出可用清單。
- 範本參數:
  - `--no-perf` 單獨整套跑:修後擋下並說明。
  - `--bogus`:修後擋下。
  - 修前 `--no-perf` 單獨出現不報錯(`SELECTIVE` 為假,旗標被默默忽略);修前 `--bogus` 會被當 run-id。
  - 兩者都有修前範本程式碼證據(`git -C lum-pre show` 看 `elif a != "--preflight": rest.append(a)`)。
  - 修前行為跑不起來:我的假專案門檻檔不全,範本先在記憶體 check 擋下。這部分只算程式碼證據,行為面未判定。
- `cycles` 為 `0`、`"3"`、`True`、`2.0` 修前修後都擋;`10001` 修前放行、修後擋(修復有效)。
- `--changed` 各情境:
  - 空白與中文檔名、刪除、未追蹤新目錄都正確。
  - 已提交的改名走 `--no-renames`,正確。
  - detached HEAD 正確。
  - 沒有主線時回 2,並附「找不到主線分岔點…只看工作目錄」說明,不崩。
  - 淺 clone 我沒另外跑,未判定。
- 記憶體情境名限 `[A-Za-z0-9_-]+`,拼成 `<run-id>.<情境>` 不會跳出產物目錄。收集腳本對 run-id 另有 `[A-Za-z0-9._-]+` 且禁全點的檢查。
- 設定檢查實測:
  - `features` 為空物件被擋(讀程式確認;未另跑)。
  - `cases` 清單為空,以及 `visual` 未在 `e2e.visual` 列出,被擋(讀程式確認;未另跑)。
  - `macrobench_cmd` 兩個 `{{TEST}}` 用 `replace` 全換,正常。
- 未驗範圍:真機流程(adb、Maestro)沒跑;記憶體情境 judge 路徑只讀程式、沒實跑;`guard kill` 與 `-k android_e2e` 全套測試沒跑。

## 三問回答
1. 原問題修復效果:有行為證據的有名字限制(`#x`、含空白、`;`、`&`、`-x` 從放行變擋下)、`cycles` 上限(10001 從放行變擋下)、不認得旗標與孤立 `--no-perf`(讀範本修前修後原始碼確認),並由 lum 與 lum-pre 同一輸入對照。`$` 沒擋是 F2。
2. 修補處相鄰路徑:`--feature`、`--case`、`--changed`、`--preflight`、run-id 位置都正常。已提交的改名正常,未提交的改名漏舊路徑(F1,原有)。
3. 新發現的同案例修前修後:F1 至 F5 都已用 lum-pre 與 lum 對照(F5 只確認行為相同),結果相同,所以都不是修補造成的回歸。

## pitfalls manifest
內建 `open(` handle 題只命中一處:`with open(p, "a", encoding="utf-8") as fh` 在測試檔 `t_android_e2e_history_edges`。這是 `with` 管理的 handle,判誤報。它也不在本席必讀的 pack 差異裡(只在修補差異)。

## 圖譜鏡頭
派工附的固定席備援寫明「這次沒附固定席節點」,所以沒有固定席筆記可逐條判。
我自己讀了計劃筆記〈Android端到端驗收_計劃〉的 S22–S28 與〈指紋〉段,比對如下:
- S23 沒寫「改名」與「共用 flow、門檻檔」的挑法(對應 F1、F4)。
- 第 55 行寫「改共用 flow 或改門檻都要重跑」,與 `unmatched` 不含共用 flow 的行為不對齊,建議筆記或程式二選一補齊。
- S26 寫效能測試方法名「開頭 #、含空白」不合規則,沒提 `$`,與 F2 呼應。
這些是對照結果,不是額外圖譜指令的查詢結果。

這輪沒找到修補造成的回歸,留下五條原有的小缺口,其中以「`$` 在 `sh -c` 裡被展開」與「未提交改名漏舊路徑」最值得補。
