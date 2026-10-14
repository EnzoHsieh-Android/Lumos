# code-代理繞閘字樣問人 r4 收貨紀錄

## 派工前:修補鏡頭與配對案例(templates §3.1)

- 高風險上限三輪跑滿,人裁破例第四輪(cap-decision extra-round,跑滿回顧已記)。修前 9b8ce146e315797baf9414008e3d1ef7bb6c2397(r3 派工單 base_commit)→ 修後 465736e9f903bf6b0822b29f4591c07aa578834a;修補差異 `r4-repair.patch`、來源 `r4-repair-binding.json`;祖先關係 rc0。
- 歸因界線:修補與分類器拆小函式在同一提交,只能逐案例比兩版行為。
- 材料全量 2325 行,拆成程式組 `r4-part-code.patch`(新掛鉤、存活事件模組,1161 行)、測試文件組 `r4-part-rest.patch`(測試、計劃、三篇節點、scripts/lumos、merge-claude-settings.py,1164 行)、規格組 `r4-part-spec.patch`(計劃與新掛鉤,1258 行);各席記帳一律填整份 `r4-snapshot.patch`;資安派兩席分看程式組與測試文件組。

### 配對案例(載入兩版掛鉤實跑,cwd=repo 根;實驗 repo、裸庫為暫存目錄,實驗 repo 已設 remote loc 指向裸庫)

| 組 | 角色 | 案例 | 預期 | 修前 9b8ce146 | 修後 465736e9 |
|---|---|---|---|---|---|
| G1 | repair | ANSI 八進位:`git commit -$'\156' -m x` | ask | pass | ask |
| G1 | repair | $"…" 包旗標:`git push $"--no-verify" o` | ask | pass | ask |
| G1 | preserve | 引號裡的說明:`echo "別用 git push --no-verify"` | pass | pass | pass |
| G2 | repair | 連結/.. 繞出暫存根:`git -C <實驗repo>/lnk/.. commit -n -m x` | ask | pass | ask |
| G2 | repair | -c remote 改推送位址:`cd <實驗repo> && git -c remote.loc.pushurl=https://example.com/r.git push --no-ver` | ask | pass | ask |
| G2 | repair | --repo 指網路:`cd <實驗repo> && git push --repo https://example.com/r.git --no-verify <裸庫>` | ask | pass | ask |
| G2 | repair | 讀遠端設定不算改:`cd <實驗repo> && git config --get remote.o.url; git push --no-verify <裸庫>` | pass | ask | pass |
| G2 | repair | grep GIT_DIR 不算設定:`grep GIT_DIR x.md; cd <實驗repo> && git commit -n -m x` | pass | ask | pass |
| G2 | preserve | 已存在的實驗 repo 提交:`cd <實驗repo> && git commit -qm x --no-verify` | pass | pass | pass |
| G2 | preserve | 真目錄推送照問:`git push --no-verify origin feat` | ask | ask | ask |
| G3 | repair | || 右側 cd:`true || cd <實驗repo> && git commit -n -m x` | ask | pass | ask |
| G3 | repair | 換行結束 && 鏈:`false && cd <實驗repo> && true⏎git commit -n -m x` | ask | pass | ask |
| G3 | repair | 大括號群組在管線裡:`{ cd <實驗repo>; } | cat; git commit -n -m x` | ask | pass | ask |
| G3 | preserve | && 鏈裡的 cd:`cd <實驗repo> && git commit -n -m x` | pass | pass | pass |
| G4 | repair | 數字參數後接導向:`git commit -m 1 >/dev/null -n` | ask | pass | ask |
| G4 | repair | )> 黏著:`(cd <實驗repo>)>/dev/null; git commit -n -m x` | ask | pass | ask |
| G4 | preserve | 2> 導向:`git push --no-verify 2>/dev/null` | ask | ask | ask |
| G4 | preserve | 讀值加 2>/dev/null:`git config core.hooksPath 2>/dev/null` | pass | pass | pass |
| G5 | repair | 變數連續翻倍 24 次(展開成 3200 萬字;更高次數在修前會吃光記憶體,不跑) | 峰值 <5 MB | 峰值 50.3 MB | 峰值 0.0 MB |
| G1 | repair | 預篩:`git commit -$'n' -m x` | 過 | 不過 | 過 |
| G1 | repair | 預篩:`git push --no-ver\⏎ify o` | 過 | 不過 | 過 |
| G6 | repair | 修剪 copymode、每次清殘檔、失敗提示(t_hook_event_trim_tmp_unique) | 綠 | 見下 | 綠 |

- G6 的修前結果:r3 折入時對修前程式加的三條新斷言(不需要修剪時清殘檔、目錄唯讀修剪失敗印提示、權限照抄)在修前為紅,見 r3-intake.md 的改壞檢查。
- 案例只是待驗範圍,不是修好的證據;新席獨立核對與補案例。

- 修正關卡:`lumos loop fix-check code-代理繞閘字樣問人 --round r3` rc0「全部通過」(110 秒;9b8ce146 → 465736e9),修正紀錄 `r3-fix.json` 六組,同類重複的五組都寫了「上次為什麼沒守住/這次換什麼做法」。

## 收貨(九席全數交回後一次寫入)

- 九席從逐字稿取最後一則以 `severity:` 開頭的完整回答存檔(通知文字會把角括號轉成跳脫字,不用)。架構對齊席初交沒有逐條 severity 行與引句,退回只補格式重交;合約圖譜席第 4 條引句不到 10 字錨不到,退回只補長那一句重交。九份 report-normalize 都已是正規格式,引句全錨(資安-文件席 clean、零引句)。
- 邊界輸入席自述一度把三個實驗檔(old.py、new.py、_hookevent.py)誤複製到主工作目錄、已自行刪除;收貨時 `git status` 乾淨、`git reflog` 無席位提交,被審工作目錄沒有被動過。
- 合計 32 條,blocking 8 條:正確性 5(2 major)、併發資源 3(1 major)、邊界輸入 4(1 major)、通才 1、架構對齊 4、資安 6(3 major)、合約圖譜 7(1 major)、資安-文件 0、規格符合 2。

## 編排者機械重現(載入被審版 465736e9 掛鉤實跑,腳本 scratchpad r4repro.py)

| 條目 | 觀察 | 結果 |
|---|---|---|
| c1 | `false &&⏎cd <實驗repo>⏎git commit -n -m x`、`true ||⏎…` | HIT:放行 |
| c2 | `prefilter` 對 `git config --remove-section core` 回 False,分類器回 config-hookspath | HIT |
| e1 | `git push $'\c' --no-verify` | HIT:放行 |
| s1 e2 | `cat <(git commit --no-verify -m x)` | HIT:放行 |
| s2 | `(( 1<<EOF ))⏎git commit --no-verify -m x⏎EOF` | HIT:放行 |
| s3 | `git push --no-verify --push-o /tmp origin main` | HIT:放行 |
| g1 t1 | `git commit -m '' -$'n'` 放行;`sed -i '' 's/hooksPath/x/' scripts/lumos` 回 literal | HIT |
| r1 | 預篩 60 萬字 `$'\n'…` 串 1.78 秒 | HIT |
| 其餘 | 依席位描述與程式對照(r2 r3 c3–c5 e3 e4 s4–s6 a1–a4 g2–g7 p1 p2) | 採信 |

## 處置

- 32 條全部折入,0 放行,0 列為重現不到。
- 依根因:指令替換與程序替換裡的指令抽出來另外判、目錄當判不出(s1 e2,並收掉〈範圍〉原本承認攔不到的指令替換);裸 `((` 算術不當 heredoc(s2);ANSI 原地比對不切片、`\c` 不吞結尾引號(e1 r1);空字串是一般詞(t1 g1);預篩與字面判共用一個字樣比對、超長不做前處理、認拆改 core 區段與引入設定檔(c2 r1 a3);吃值長選項認縮寫、只看選項位置(s3 g5);`git-commit` 執行檔、`--attr-source`、`include.path`/`includeIf.*.path`(s4 s6 s5);`env` 帶值選項、GIT_DIR 只認前綴賦值(c4 e4);`&&`/`||` 後接換行、結構本體與大括號群組裡的 cd(c1 c3 e3);單引號與跳脫的 `$` 不展開(c5);`git remote` 只認會改位址的子指令(p1);預算用到下限就不再跑 git、進場結束復位、重新起算收成一個小函式(r2 r3 a4);修剪失敗提示帶 `telemetry-write-failed`(a1);暫存根說明改正(a2);計劃文字、條款綁定、d3 指向 d4、Systems 節點、七份預算複本的過期句、存活事件的已知接受與回頭條件(g2 g3 g4 g6 g7 p2)。
- 每組先寫先紅測試:新增案例在修前 64 條紅、修後繞閘 577 條、存活事件 26 條、預算複本守衛 31 條全綠;另加兩道全表守衛——S1 每個會問的案例都要過得了預篩、而且不是靠字面判問到的。

## 修補因果

- 有證據的修復回歸(修前問或正確、修後放行或出錯):c1(r3 的換行轉 `;`)、r1 與 r3(r3 讓預篩跑前處理、r3 新增 `_IN_HOOK`)、e1(r3 新增 `\c` 解碼)、e2 與 s1(r3 新增的導向拆法吃掉 `<(` 後的 git)、t1 與 g1(r3 新增的黏著標點分支遇空字串丟例外)→ regression-set。
- 其餘有證據屬原有漏查(兩版同結果)或未判定。

## 修後檢查

- 測試:繞閘 579、存活事件 26、預算複本守衛 31 條全綠;新增告警只剩逐字複本裡那個減號(相鄰六支掛鉤只改了過期的一句說明,告警數與修改前相同)。
- 改壞檢查 24 種全翻紅(腳本 scratchpad `mutate_r4.py`、`mutate_r4b.py`):兩種先未翻紅——ANSI 八進位改回切片、預篩超長照跑前處理——原因是測試輸入太小、量不出時間差,把輸入加到 30 萬個跳脫與 6MB 後翻紅。
- 大型與深層輸入:修完第一版量到三千層巢狀的 `$(…)`/`<(…)` 要 3.4 秒(逐層重掃是平方時間),改成一趟拆完後 0.06 秒,並加進 0.5 秒計時測試;其餘十種形狀(平鋪替換、反引號、大括號與 if 巢狀、空字串、`((`、`env -u`)都在 0.4 秒、1MB 內。
- 事件帳重放 34622 條(9 秒):過預篩 465 條;沒被截成 500 字的指令裡會問 19 條(修前 20 條)。兩版判法不同的 8 條:6 條是原本誤問的 `sed -i ''` 與被截斷指令的字面判,現在放行;2 條新問——一條是被截斷的指令,一條是在同指令才建的實驗 repo 寫 `include.path`(依決策 d3 照問)。
