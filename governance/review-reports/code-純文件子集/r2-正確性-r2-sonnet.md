severity: blocker

## F1 keys/docs 子集配 4 片分片時,只要選中的測試數 < 片數,推送必被誤擋(訊息還說「有測試沒過」但其實全過)

severity: blocker
blocking: yes

引句:「_run_group() {   # $1=log 前綴,其餘=執行器參數;每片一個子行程,回傳 0=全綠、3=每片都選中 0 支、1=有紅」
引句:「for _p in "${_pids[@]}"; do _r=0; wait "$_p" || _r=$?; [[ "$_r" -eq 3 ]] && _any3=1; [[ "$_r" -ne 0 && "$_r" -ne 3 ]] && _bad=1; done」

觀察到什麼:
`_run_group` 的註解自己寫死一個模型——「3=每片都選中 0 支、1=有紅」,把「單一片分到 0 支」跟「整批選中 0 支」當同一件事、都預期回 3。但 `scripts/test_lumos.py` 實際上是兩條完全不同的路:
- 整批(分片之前)`--suite` 選中 0 支 → `file: \`scripts/test_lumos.py:29380-29385\`` → 回 **3**。
- 分片之後,「這一片」分到 0 支(整批選中的測試數 < `--shard` 的片數 N,平均切不夠分)→ `file: \`scripts/test_lumos.py:29401-29404\`` → 回的是 **1**,不是 3。這段程式碼不在這輪 diff 裡(純 context,round 2 完全沒碰,也沒被測到)。

`--suite keys`/`light` 這條路的 `affected_keys` 設計目標就是「小改動只挑幾個函式名」(見 patch `_affected_test_keys` 的說明),選中的測試數常常只有 1、2、3 支;而 pre-push 預設 `_shards=4`(`file: \`scripts/hooks/pre-push:371\``,`_shards="${LUMOS_TEST_SHARDS:-4}"`)。只要選中數 < 4,用「k % n == i-1」分片必定有片分到 0 支,那一片回 1 → `_bad=1` → `_run_group` 回 1(不是預期中的 3)→ 外層 `elif "$_krc" -ne 0; then _rc=1`(patch 裡的 light 分支)把整趟推送判成「有紅」,印「擋下:test_lumos.py 有紅,有測試沒過」,即使實際跑到的測試全部通過、根本沒有任何一支失敗。

怎麼重現(輸入→錯誤輸出,在本 repo 直接跑、唯讀,未改動任何檔案):
```
$ python3 scripts/test_lumos.py --list --suite keys --keys _range_base
t_test_suite_docs_only_judgement          # 只選中 1 支

$ for i in 1 2 3 4; do
    python3 scripts/test_lumos.py --suite keys --keys _range_base --shard "$i/4" >/tmp/o$i.log 2>&1
    echo "shard $i rc=$?"
  done
shard 1 rc=0   # 分到 1 支,18 passed, 0 failed
shard 2 rc=1   # 擋下:第 2 片一支測試都沒分到——片數比測試數還多
shard 3 rc=1   # 同上
shard 4 rc=1   # 同上
```
按 `_run_group` 同一套邏輯(`_bad`/`_any3` 判定)手動組合這四個離開碼:
```
_bad=0; _any3=0
for r in 0 1 1 1; do
  [[ "$r" -eq 3 ]] && _any3=1
  [[ "$r" -ne 0 && "$r" -ne 3 ]] && _bad=1
done
[[ "$_bad" -eq 1 ]] && echo "GROUP RESULT: rc=1(有紅,推送被擋)"
```
輸出:`GROUP RESULT: rc=1(有紅,推送被擋)`——而實際上唯一真的跑到的那 1 支測試(18 個斷言)全過,沒有任何測試失敗。

為什麼是 bug 而不是風格:
這直接破壞這批改動宣稱要達成的合約——「light/keys 子集要能讓小改動的推送更快過」,結果變成「keys 選中的測試數只要 < 4(小改動閘存在的目的正是讓 affected_keys 很小),推送就一律被誤擋」,而且擋下訊息是「test_lumos.py 有紅,有測試沒過」,對使用者是假訊息(沒有任何測試真的紅),會誤導人去找不存在的壞測試,或直接推去用 `--no-verify`——而這支腳本自己在別的地方明講「那條零留痕」是最不希望發生的結果。`--suite docs` 因為目前文件子集有 209 支測試(遠大於 4 片),日常不會踩到,但 `--suite keys`(light 路徑的主力機制)幾乎每次小改動都會踩到,屬於**新功能的主要使用情境系統性壞掉**,不是邊角案例。

file: `scripts/hooks/pre-push:404-422`(`_run_group` 定義與呼叫端 `_krc`/`_rc` 判定)
file: `scripts/test_lumos.py:29380-29404`(整批 0 支回 3、單片 0 支回 1 的分岔點)
file: `scripts/hooks/pre-push:371`(`_shards="${LUMOS_TEST_SHARDS:-4}"`,預設 4 片)

## 其餘鏡頭檢查過、沒發現新洞

- `_docs_only_file` 副檔名白名單:`.JSON`(大寫)、`docs/.env`(無副檔名)、`docs/a.py.md`(取最後一段副檔名 `.md`)都照設計走(大小寫用 `.lower()`;無副檔名一律非文件;`docs`(無斜線)、`docs2/` 因為比對用 `path == w` 或 `startswith("docs/")`,都不會誤配)。`.md.bak` 因最後副檔名是 `.bak`(不在清單)→ 正確判非文件、跑全套,方向安全。
- LICENSE 全名比對:`governance/LICENSE` 先被 `governance/` 目錄前綴命中「路徑白名單」,但因為它本身不在 `_DOCS_ONLY_PATHS` 的全名清單裡、又沒有副檔名,最後仍被判非文件(強制全套)——方向保守安全,不是漏洞。
- `_range_base` 對 `a...`(右端空)、`...b`(左端空)、空字串:三點範圍空端落回 `HEAD` 再 merge-base、空字串直接回 `None`,跟 patch 裡 t_test_suite_docs_only_judgement 的 ⑩⑪ 案例對得上,沒有繞過。
- `light_ok` 對「範圍只有簿記帳」:回 `suite=docs`(不是 `light`),此時 `light_ok` 硬編 `False` 但 pre-push 只在 `_suite_this == "full"` 才會去看 `light_ok`,這個值不會被用到,不是活的洞。「非文件檔全被 `.lumos/config` ignore 掉」:`_is_code_file` 對 ignore 的檔回 False,會讓它落在 `non_docs` 但不進 `code`,使 `light_ok` 變 False(逼全套),方向一樣保守安全。
- `_affected_test_keys` 的頂格 `def` 正則對 hunk 標頭 `@@ … @@ class Foo:`(不接 def,不會誤配)與 `@@ … @@ def`:本機用 git 預設(未設定 `diff.python.xfuncname`,repo 沒有這條 `.gitattributes` 設定)實測兩個巢狀函式案例,git 的 hunk 標頭 context 只會挑「行首無縮排」那一行當函式名(即使真正最近的外層函式是縮排的巢狀 `def`,git 也不會選它),所以 `\s*` 那段不會把縮排的巢狀 def 吃進去當「頂層」——沒能重現這個誤配。
- `_keys_suite_select` 的 30% 上限對極小測試集(tests=2):確認 `cap*len=0.6` 時任何選中 1 支的 key 都會被丟掉(`1 > 0.6`),但 production 呼叫這支函式時 `tests` 一律是完整全域測試清單(1000+ 支),沒有被預先篩小的路徑,這個極端值不會在真實呼叫鏈裡出現,判 clean(非 major)。
- `--suite docs --list -k x` 的交互:`--suite` 選子集發生在 `-k`/`--keyword` 套用之前(main() 裡 `_args.suite` 分支先跑,關鍵字過濾邏輯在後面),`--list` 分支對兩者都是印名字不執行,沒發現顯示錯誤名單或吃掉旗標的情況。
- pre-push 多 ref 時 `_SUITE_KEYS` 累積與 `_suite_this` 判定:讀 code 確認是逐 ref 迴圈內用 `${_SUITE_KEYS:+$_SUITE_KEYS,}$_k` 累加(不會覆蓋前一個 ref 的 keys),`_SUITE_FULL`/`_SUITE_LIGHT` 也是逐 ref OR 進去、迴圈外才判 `_suite_mode`,邏輯上一致,沒有另外構造多 ref 案例實跑驗證(時間有限,留給下一輪若要機械覆蓋可以加)。
