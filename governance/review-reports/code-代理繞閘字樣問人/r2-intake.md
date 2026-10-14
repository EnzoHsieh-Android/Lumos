# code-代理繞閘字樣問人 r2 收貨紀錄

## 派工前:修補鏡頭與配對案例(templates §3.1)

- 修前 b5be3aadf52851f125cd0588c9914a4d8854bb31(r1 派工單 base_commit,同範圍重生 r1 凍結 patch 的 sha256 一致)→ 修後 4e87b6821028231ccbb68cdaa8715cdc8dda5e35;修補差異 `r2-repair.patch`、來源 `r2-repair-binding.json`;祖先關係 rc0。
- 歸因界線:掛鉤主體在修補時整支重構(引號追蹤、前處理、走訪改成兩個類別),修補與重構是同一次改寫拆不開;只能逐案例比兩版行為,不能逐行歸因。
- 材料超過 1800 行(全量 1927 行),拆成程式組 `r2-part-code.patch`(新掛鉤、存活事件模組、測試,1471 行)與文件註冊組 `r2-part-doc.patch`(計劃、三篇節點、scripts/lumos、merge-claude-settings.py,456 行);各席記帳一律填整份 `r2-snapshot.patch`。資安派兩席分看兩組。

### 配對案例(載入兩版掛鉤實跑 bypass_reasons,cwd=/Users/someone/work/repo)

| 組 | 角色 | 案例 | 預期 | 修前 b5be3aad | 修後 4e87b682 |
|---|---|---|---|---|---|
| G1 | repair | 詞中間 # 不吞後面的推送:`git checkout -b fix#1 && git push --no-verify` | ask | pass | ask |
| G1 | repair | 訊息 heredoc 有撇號後的 -n:`git commit -m "$(cat <<'EOF'⏎don't do it⏎EOF⏎)" -n` | ask | pass | ask |
| G1 | repair | 引號裡的括號後 -n:`git commit -m "(" -n` | ask | pass | ask |
| G1 | preserve | heredoc 內容提到繞閘:`cat <<'EOF' > note.md⏎git push --no-verify⏎EOF` | pass | pass | pass |
| G1 | preserve | 引號裡的說明文字:`echo "不要用 git push --no-verify"` | pass | pass | pass |
| G1 | preserve | 詞首註解:`# git commit -n -m x` | pass | pass | pass |
| G2 | repair | --git-dir 指回真 repo:`cd /tmp/nonexist && git --git-dir=/Users/x/real/.git commit --no-verif` | ask | pass | ask |
| G2 | repair | config --global 在暫存目錄:`cd /tmp && git config --global core.hooksPath /dev/null` | ask | pass | ask |
| G2 | repair | mktemp 子路徑用 .. 繞出:`S=$(mktemp -d); cd $S/../../Users/x && git commit -n -m x` | ask | pass | ask |
| G2 | repair | cd 到不存在又沒建的目錄:`cd /tmp/nonexist-r2case; git commit -n -m x` | ask | pass | ask |
| G2 | preserve | mktemp 新目錄提交:`d=$(mktemp -d); git -C $d init -q; git -C $d commit -qm x --no-verify` | pass | pass | pass |
| G2 | preserve | 同指令建的暫存目錄:`mkdir -p /tmp/lumos-r2case-new/a && cd /tmp/lumos-r2case-new/a && git ` | pass | pass | pass |
| G2 | preserve | 真目錄推送照問:`git push --no-verify origin feat` | ask | ask | ask |
| G3 | repair | timeout 前綴的 lumos:`LUMOS_SKIP_FIX_CHECK=1 timeout 600 lumos code-loop check` | ask | pass | ask |
| G3 | repair | --config-env 改掛鉤目錄:`git --config-env=core.hooksPath=H push` | ask | pass | ask |
| G3 | repair | 先賦值再 export 名稱:`LUMOS_SKIP_X=1; export LUMOS_SKIP_X; git push` | ask | pass | ask |
| G3 | preserve | LUMOS_SKIP 接跑測試:`LUMOS_SKIP_REREAD_CHECK=1 python3.14 scripts/test_lumos.py -k reread` | pass | pass | pass |
| G3 | preserve | git 前的 LUMOS_SKIP:`LUMOS_SKIP_REREAD_CHECK=1 git push Lumos feat` | ask | ask | ask |
| G4 | repair | 預篩:續行後頂在行首的 -n(`git commit -m x \⏎-n`) | 過 | 不過 | 過 |
| G5 | repair | 幾百段都要查 git(測試 t_bypass_ask_fallbacks_and_budget) | 1 秒內且問 | 約 300 段超過 5 秒 | 綠 |
| G6 | repair | 固定暫存檔名被佔住時修剪(t_hook_event_trim_tmp_unique) | 修剪到 2000 行 | 4001 行(紅) | 綠 |

- 案例只是待驗範圍,不是修好的證據;新席獨立核對與補案例。

- 修正關卡:`lumos loop fix-check code-代理繞閘字樣問人 --round r1` rc0「全部通過」(110 秒;修正前 b5be3aad → 修正後 4e87b682),修正紀錄 `r1-fix.json` 七組;記成 spec/process 不用修正紀錄的:r3、g1、t4、t5、a2、p3、p4、p5。

## 收貨(九席全數交回後一次寫入)

- 九席(程式組:正確性、併發資源、邊界輸入、通才、架構對齊、資安;文件註冊組:合約圖譜、資安-文件、規格符合,皆 sonnet)從逐字稿取最後一則以 `severity:` 開頭的完整回答存檔;`git status` 只有自己的帳本追加,`git reflog` 無席位提交。
- 合約圖譜席最後一條清理指令(帶萬用字元的 rm)卡在權限確認近 30 分鐘,停掉後請它不跑工具直接交報告;它的臨時目錄由編排者刪。
- 格式:併發資源、通才、架構對齊、資安、合約圖譜、規格符合以 `report-normalize --write` 做純格式搬移(縮排在條列裡的 severity 行搬成獨立一行);架構對齊總結句藏了更高等級的字樣、資安一行以「嚴重度:」開頭,退回兩席只改那一處重交。
- quote-check:八份全數錨定;合約圖譜 1 句(把多行的 lands_in 寫成一句、含 `\n`)錨不到,以機械重現採信(見下表 g3)。資安-文件席 clean、零引句。

## 編排者機械重現(載入修後 4e87b682 掛鉤實跑,修前 b5be3aad 對照)

| 條目 | 觀察 | 結果 |
|---|---|---|
| s2 c5 e6 t4 | `export GIT_DIR=<真repo>/.git; cd <暫存>; git commit -n` | HIT:修後放行 |
| s3 | 同指令 mkdir 後 `ln -s` 真 repo 再 cd 提交 | HIT:修後放行 |
| s4 e4 | `git remote set-url --add --push origin /tmp/zz && git push --no-verify origin` | HIT:修前問、修後放行(修補回歸) |
| s1 c6 t3 e9 | `cd $(mktemp -d -p <真repo>) && git commit --no-verify` | HIT:修後放行 |
| e1 c2 | `git push --no-verify > /tmp/x.log`(cwd 真 repo) | HIT:修後放行 |
| c1 e3 | `# don't skip⏎git commit -m x \⏎ --no-verify` | HIT:兩版皆放行 |
| r1 t5 | `"git commit -n; " + "$(" * 9990` 計時 | HIT:修後 3 秒(修前 0.01 秒) |
| t1 | `grep -n "LUMOS_SKIP_X=1" scripts/lumos` | HIT:修後誤問 lumos-skip |
| g3 | 修後計劃 `lands_in` 只列兩篇,沒有 Systems/掛鉤存活事件 | HIT:`git show 4e87b682:<計劃>` 第 14–16 行 |
| a2 r2 | `_hookevent` 修剪後權限 | 採信(席位實測 0644→0600) |
| 其餘 | 依席位描述與程式對照 | 採信 |

## 處置

- 39 條全部折入,0 放行(同輪有 major),0 列為重現不到。
- 換形狀(同類第二次出現):拋棄式豁免改成只認判斷當下就存在、用 git 確認過的事實,同指令推論(建目錄、mktemp、remote add/set-url)全拿掉,以決策 d3 記下;這一刀一次涵蓋 s1 s3 s4 c6 e4 e5 e9 t3 等。
- 其餘依根因:導向在切詞當下認定並連同目標剔除(e1 c2 c3 e2);續行改在單趟前處理裡接、ANSI 解碼、跳脫字遮罩(c1 e3 c4 e9 的 `$'n'`);GIT_DIR 一族在任何位置出現就不豁免(s2 c5 e6 t4);管線與條件式 cd(e8);LUMOS_SKIP 只認前綴身分(t1);只有 commit 與 push 算閘,merge 等不問(g2);`--remove-section core`(e9);`host:path` 一律當網路位址(t2);git 失敗只認「不是 repo」(資安類 1 的副作用,c-系列);同指令動過遠端設定不豁免推送(另補);git 總截止時間(c7);括號一次配對與相鄰佔位詞合併(r1 t5,另補反引號);預篩拆引號(s5);存活事件修剪權限、殘檔、位元組上限、失敗清理(a2 r2 c8);計劃落點、回退中間狀態、S4 字面判條款、merge 的範圍矛盾、新語法測試(g1–g5 p1);自寫切段器理由寫進 PRIOR-ART(a4,判 minor:需求不同、不能互相 import);模組頂層載入共用模組寫進程式註解(a1);`_Sep` 無先例的理由寫進註解(a3)。
- 修後檢查:229 + 24 條斷言全綠;15 種大型與深層巢狀輸入最慢 0.15 秒、峰值 1.5MB;改壞檢查這輪 17+4 種全翻紅(私用區字元改走字面那道判定多餘、已拿掉);事件帳重放 29884 條,未截斷會問 16 條(3 真繞閘、約 6 條同指令建實驗 repo——換形狀的代價、其餘為已刪目錄的重放假象)。

## 修補因果(templates §3.1)

- 有證據的修復回歸(席位附修前修後兩版結果,編排者重現):s4、e4(同指令 `set-url --add` 修前問、修後放行)、r1、t5(大量沒配對 `$(` 修前 0.01 秒、修後 3 秒)、r2(修剪中途被砍的殘檔修前會被覆蓋、修後累積)、t1(grep 參數裡的 LUMOS_SKIP 修前不問、修後誤問)、c4(跳脫反引號夾指令修前問、修後放行)→ 記入 regression-set。
- 部分變體是回歸、主體是原有漏查:c1(`$'…'` 加續行那一變體)、e2(指令含私用區字元那一變體)、e3(`$'a\'b'` 加續行)、e9(`-$'n'`、`git init -b`/`clone` 值旗標那幾個變體)——主體在修前就漏,不列入 regression-set,變體已一併修掉。
- 其餘有證據屬原有漏查或未判定(a 系列架構形狀、g 系列文件測試落差、p1、c7 git 卡住總時間舊版未造同場景、c8 未判定)。

- 載體:第一次以含原引句的彙總記帳被擋(載體引句必須全錨,帳未寫入);合約圖譜席原報告已記帳綁指紋不動,請該席只把第 3 條引句換成能逐字對上材料的單行原文、其餘不改重交,存為 `r2-合約圖譜-sonnet-引句更正.md`,彙總載體改從這份組,41 句全數錨定。
