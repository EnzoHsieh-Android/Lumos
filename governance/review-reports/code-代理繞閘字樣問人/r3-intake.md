# code-代理繞閘字樣問人 r3 收貨紀錄

## 派工前:修補鏡頭與配對案例(templates §3.1)

- 末輪(高風險上限 3 輪)。修前 4e87b6821028231ccbb68cdaa8715cdc8dda5e35(r2 派工單 base_commit)→ 修後 9b8ce146e315797baf9414008e3d1ef7bb6c2397;修補差異 `r3-repair.patch`、來源 `r3-repair-binding.json`;祖先關係 rc0。
- 歸因界線:拋棄式判定整段重寫(決策 d3,只認判斷當下事實),修補與重構拆不開,只能逐案例比兩版行為。
- 材料全量 2105 行,拆成程式組 `r3-part-code.patch`(新掛鉤、存活事件模組,1037 行)、測試文件組 `r3-part-rest.patch`(測試、計劃、三篇節點、scripts/lumos、merge-claude-settings.py,1068 行)、規格組 `r3-part-spec.patch`(計劃與新掛鉤,1136 行);各席記帳一律填整份 `r3-snapshot.patch`;資安派兩席分看程式組與測試文件組。

### 配對案例(載入兩版掛鉤實跑,cwd=/Users/someone/work/repo)

| 組 | 角色 | 案例 | 預期 | 修前 4e87b682 | 修後 9b8ce146 |
|---|---|---|---|---|---|
| G1 | repair | mktemp -p 真 repo:`cd $(mktemp -d -p /Users/someone/work/repo) && git commit --no-verify -m` | ask | pass | ask |
| G1 | repair | export GIT_DIR:`export GIT_DIR=/Users/x/real/.git; cd /var/folders/tc/xmllmxtn4q5704lsy8` | ask | pass | ask |
| G1 | repair | set-url --add 推送:`cd /var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/gctl-r3exp-0qaherzg ` | ask | pass | ask |
| G1 | repair | 同指令 mkdir 建的目錄:`mkdir -p /tmp/lumos-r3case/a && cd /tmp/lumos-r3case/a && git init -q &&` | ask | pass | ask |
| G1 | preserve | 已存在的實驗 repo 提交:`cd /var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/gctl-r3exp-0qaherzg ` | pass | pass | pass |
| G1 | preserve | 已存在的實驗 repo 改掛鉤設定:`cd /var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/gctl-r3exp-0qaherzg ` | pass | pass | pass |
| G1 | preserve | 真目錄推送照問:`git push --no-verify origin feat` | ask | ask | ask |
| G2 | repair | 推送導向暫存檔:`git push --no-verify > /tmp/x.log` | ask | pass | ask |
| G2 | repair | 讀值加 2>/dev/null 不誤問:`git config core.hooksPath 2>/dev/null` | pass | ask | pass |
| G2 | preserve | 引號裡的說明文字:`echo "不要用 git push --no-verify"` | pass | pass | pass |
| G3 | repair | 註解撇號後的續行:`# don't skip⏎git commit -m x \⏎  --no-verify` | ask | pass | ask |
| G3 | repair | 跳脫反引號夾指令:`echo \`; git push --no-verify; echo \`` | ask | pass | ask |
| G3 | preserve | heredoc 內容提到繞閘:`cat <<'EOF' > n.md⏎git push --no-verify⏎EOF` | pass | pass | pass |
| G4 | repair | grep 參數裡的 LUMOS_SKIP 不誤問:`grep -n "LUMOS_SKIP_X=1" scripts/lumos` | pass | ask | pass |
| G4 | repair | merge --no-verify 不問:`git merge --no-verify main` | pass | ask | pass |
| G4 | preserve | timeout 前綴的 lumos:`LUMOS_SKIP_FIX_CHECK=1 timeout 600 lumos code-loop check` | ask | ask | ask |
| G4 | preserve | git 前的 LUMOS_SKIP:`LUMOS_SKIP_REREAD_CHECK=1 git push Lumos feat` | ask | ask | ask |
| G5 | repair | 大量沒配對 `$(` 計時 | <0.5 秒 | 3.13 秒 | 0.05 秒 |
| G6 | repair | 預篩:`git push --no-ver''ify o` | 過 | 不過 | 過 |
| G7 | repair | 修剪權限、殘檔、位元組上限、失敗清理(t_hook_event_trim_tmp_unique) | 綠 | 紅(4 條) | 綠 |

- 案例只是待驗範圍,不是修好的證據;新席獨立核對與補案例。

- 修正關卡:`lumos loop fix-check code-代理繞閘字樣問人 --round r2` rc0「全部通過」(109 秒;4e87b682 → 9b8ce146),修正紀錄 `r2-fix.json` 八組,同類重複的七組都寫了「上次為什麼沒守住/這次換什麼做法」。

## 收貨(九席全數交回後一次寫入)

- 九席從逐字稿取最後一則以 `severity:` 開頭的完整回答存檔;格式全部合格(新版共用說明的頂格 severity 規則有效),只有通才席兩條 finding 漏寫 severity 行,退回該席只補那兩行重交。引句全數錨定(資安-文件席 clean、零引句)。repo 沒被席位改動。
- 合計 32 條,blocking 9 條:正確性 7(3 major)、併發資源 4(1 major)、邊界輸入 6(1 major)、通才 2、架構對齊 3(1 major)、資安 2(2 major)、合約圖譜 6、資安-文件 0、規格符合 2(1 major)。

## 編排者機械重現(載入修後 9b8ce146 掛鉤實跑)

| 條目 | 觀察 | 結果 |
|---|---|---|
| e1 p1 | `prefilter` 對 `git commit -$'n' -m x`、`git push --no-ver\⏎ify o` | HIT:預篩 False,分類器卻判得出 |
| s1 | `git -C <暫存>/lnk/.. commit -n`(lnk 指真 repo 子目錄) | HIT:放行 |
| c1 | `false && cd <暫存> && true⏎git commit -n`、`true || cd <暫存> && git commit -n` | HIT:放行 |
| c2 g1 | `-c remote.loc.pushurl=<網址> push --no-verify loc`、`push --repo <網址> --no-verify <暫存裸庫>` | HIT:放行 |
| c3 | `git commit -m 1 >/dev/null -n` | HIT:放行(r2 修補造成的回歸) |
| s2 t1 | `rm -rf <暫存> && ln -s <真repo> <暫存> && git -C <暫存> commit -n` | HIT:放行(承認為有心改寫,d4) |
| r1 | `A=xx;` 接 22 次 `A=$A$A;` | HIT:展開未設上限(只跑到 22 次避免拖垮機器,更高次數採信席位實測 33 次 14GB) |
| a1 | `_remaining_budget` 與逐字複本 `_inner_budget` 並存 | HIT:讀碼確認 |
| 其餘 | 依席位描述與程式對照 | 採信 |

## 處置

- 32 條全部折入,0 放行,0 列為重現不到。
- 依根因:預篩用同一套前處理(e1 p1);ANSI 補八進位、`\u`、`\U`、`\c` 與 `$"…"`(c5 e1 變體);路徑不做文字化簡、交給 realpath(s1);變數展開上限 4096(r1);換行等同 `;`、`||` 兩側與 if/while 條件裡的 `cd` 判不出、大括號群組在管線或背景裡還原(c1 c4 e2 e3);`)>` 拆分(e4);檔案代號在前處理標記、修掉數字參數回歸、`{fd}>`(c3 e5);`-c remote.*`/`url.*`、`GIT_CONFIG_KEY_n` 的 remote/url、`--repo`、GIT_DIR 後的推送都不豁免(c2 g1 p2);讀遠端設定不算改動(c7);`GIT_DIR` 一般詞只認賦值形式(e6);預算拿掉第二套算法、逾時就不再跑 git、批次重跑時重新起算(a1 c6);實驗 repo 另要求沒有網路遠端(t2);同指令改寫既有路徑寫進〈範圍〉承認、決策 d4 修正 d3「封閉」說法(s2 t1);存活事件修剪改用 copymode、任何失敗都清暫存檔、每次記事件都清殘檔、修剪失敗印提示、同時追加遺失一行寫明為已知接受(a2 a3 r2 r3 r4);計劃文字(預算、修剪描述、GIT_DIR 條款)與測試缺口補齊(g2 g3 g4 g5);錨點基準在推送前重簽(g6)。
- 修後檢查:繞閘 273、存活事件 26 條全綠;12 種大型深層輸入最慢 0.17 秒、峰值 1.5MB;改壞檢查 20 種全翻紅(兩種先未翻紅、補案例後翻紅);事件帳重放 33831 條,未截斷會問 19 條。

## 修補因果

- 有證據的修復回歸:c3(r2 的「數字後接導向就刪」誤刪 `-m 1 >x -n` 的 1;修前問、修後放行)、c7(r2 的 `_changes_remotes` 把 `git config --get remote.*` 也當改動;修前放行、修後多問)、e6(r2 起 `grep GIT_DIR` 也讓豁免失效;多問方向)→ regression-set。
- 其餘有證據屬原有漏查或未判定(兩版同結果,或修前沒有對應機制)。
