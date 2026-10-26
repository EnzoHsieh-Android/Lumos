severity: major

我在臨時 clone 裡用 python3.14 載入兩版 `scripts/lumos` 直接呼叫函式、跑 CLI。沒有跑完整的 `android_e2e` 測試。

我另外一次完整的 `-k android_e2e` 在中途被我自己切換版本弄髒,已停掉,沒有結果可引用。

歸因界線:修補 490dac6a 緊接在 de8a99bc 之後,單一提交,所以下面的歸因只到「這一輪修正」。

1. 「擋下:」並沒有全部走 `_e2e_say_block`,`judge` 這一路仍原樣印外來文字
severity: major
blocking: 是
- file: `scripts/lumos:42167`(`_e2e_full_blocked`)、`scripts/lumos:42182`(`judge --precheck`)。
- 另有 `scripts/lumos:41349` 和 `42092` 也是直接 print,但文字來源較弱,我沒有實測。
- 引句:「+        _e2e_say_block(serr)」
- 計劃條款 S51 寫「e2e 指令印的每一行『擋下:』都應清掉控制字元」。
- 失敗場景:
  - 工作樹裡有一個檔名含換行和 ESC 的未追蹤檔。
  - `lumos android-e2e judge --precheck` 會把檔名原樣印進「擋下:」那一行,偽造出獨立的 `PWN-LINE` 行和 ANSI 碼。
  - `_e2e_full_blocked` 的 `why` 來自 `steps.json` 的字串,以及 `_e2e_record_update` 的錯誤訊息(`_e2e_record_err` 會帶紀錄鍵名 `k`),也是同一個問題。
- 重現:先建一個含換行的未追蹤檔,再跑 judge。
  ```
  git init pc && python3.14 -c "open('x\nPWN-LINE \x1b[31mred','w').write('1')"
  python3.14 scripts/lumos android-e2e judge --repo <pc> --precheck 2>&1 | cat -v
  ```
- 結果:修前 de8a99bc 和修後 490dac6a 輸出相同,都是 `...:x` 換行 `PWN-LINE ^[[31mred(...)`。
- 測試缺口:新測試 `t_android_e2e_text_gates` 的註解寫了「跑完寫紀錄遇到讀不懂的紀錄」,實際只測了 `waive` 和 `waive --ack`,沒測 `judge`。
- 歸因:有證據的原有漏查。修補聲稱十二處、單一出口,但 `judge` 這組沒掃到。我數修補差異只有 11 處改動,另外 4 處漏掉,「十二處」這個數字本身也對不上。

2. 新的 `_e2e_parent` 的 git 失敗保護,沒有任何測試真正碰到
severity: major
blocking: 是
- file: `scripts/lumos:41632`
- 引句:「+        return None, f"查不出 {sha[:8]} 的上一版(git 失敗或逾時)"」
- 失敗場景:有人把 `if raw is None` 那支改回 `return "", None`(也就是修補要堵的放行漏洞),測試仍全綠。
  - 新測試 `t_android_e2e_gate_r4_paths` 的 ② 是整支 `m._e2e_parent` 換成假函式,真的函式從沒被執行。
- 重現:我在臨時 clone 改成 `return "", None`,執行 `-k e2e_gate_r4_paths`,結果 `4 passed, 0 failed`。
- 行為本身是對的:
  - 合併提交回第一個上一版,和 `HEAD^1` 相同。
  - 根提交回 `("", None)`。
  - 不存在的 sha 或 `deadbeef` 回 `(None, 錯誤)`。
  - 修前不存在的 sha 會變空字串而放行,所以修補確實有效,只是沒有測試守它。
- 歸因:修補自己引入的測試缺口(守衛是這一輪新增的)。

3. 64 層邊界對尾端 `/` 與開頭 `./` 算錯
severity: minor
blocking: 否
- file: `scripts/lumos:40324`(`_e2e_relpath_err`)
- 引句:「+    if p.count("/") >= 64:   # 64 層以上」
- 失敗場景:
  - `"d/"*64`(64 層帶尾斜線)和 `"./" + 64 層` 都被判「超過 64 層」。
  - 正規化後只有 64 層,而 `"/".join(["d"]*64)` 被收。
- 重現:跑這三個輸入,前兩個回錯誤,第三個回 None。
- 修前三個都收,所以是修補造成的回歸。新測試只測不帶 `/` 尾巴的 64 與 65。
- 歸因:有證據的修復回歸。

4. `waive --list` 時間用完且還沒印任何放行時,仍印「沒有任何放行。」
severity: minor
blocking: 否
- file: `scripts/lumos:41913` 起(`_e2e_waive_list`)
- 引句:「+            print(f"注意:另有 {len(files) - i} 份沒讀(讀超過 {budget:g} 秒);再跑一次會從最新的開始讀", file=sys.stderr)」
- 重現:有一份含人放行的紀錄,`_e2e_waive_list(root, budget=0)`。
  - stderr:「另有 1 份沒讀」。
  - stdout:「沒有任何放行。」,是假陰性。
- 另一個問題:每次都從最新的開始讀,超過 60 秒後最舊的紀錄永遠列不出來。修前沒有時間上限,所以這是新行為。
- 歸因:有證據的修復回歸。

三問:
- ① 原問題的修復效果,有行為證據的有四項:
  - 路徑含換行、ESC 或 U+202E 被拒收。
  - 2MB 以上的紀錄(帶放行)被擋並標 `bad_record`。
  - `_e2e_parent` 區分 git 失敗與根提交。
  - `_e2e_clean` 拆開兩串逃逸帳字樣,實測「受波及合約的測試沒過 tier=high 且」變成「受波 及合約的測試沒過 ti er=high 且」。
  - 但 `judge` 的「擋下:」沒覆蓋(finding 1)。
- ② 相鄰路徑:
  - `_e2e_tree_blob` 沒帶 `limit` 的呼叫者(macrobench.json、門檻檔)不變,仍用 16MB;只是超限訊息多了「(16MB)」。
  - `_E2eGitErr` 經 `_e2e_tree_json` 原樣回傳,到 `_e2e_gate_load` 的 `isinstance` 判斷前沒有被字串化,型別不會掉。
  - 中文路徑、含空白路徑、63 層都收;`_e2e_clean` 不動指紋和路徑。
  - 唯一回歸是 64 層帶尾斜線或 `./` 開頭(finding 3)。
  - `mainline_newer` 與 `cfg_weakened` 的分流:base_full 為 None 時走 `mainline_newer`,三方都不同也走 `mainline_newer`;`cfg_weakened` 只在主線等於分岔點時出現。這我是讀程式推出來的,沒有單獨跑。
- ③ 同一案例的修前、修後結果:
  - 檔名帶換行與 ESC,走 `judge --precheck`:修前、修後都原樣印出。
  - `_e2e_parent` 對不存在的 sha:修前變空字串而放行,修後回錯誤並擋下(但無測試守,見 finding 2)。
  - 64 層帶尾斜線:修前收,修後拒。
  - `waive --list` 時間用完:修前無上限,修後印假陰性(見 finding 4)。

最高等級 major,擋實作的有 2 條(1、2);臨時目錄已用字面絕對路徑刪除。
