severity: minor

## F1 超長行讓帳記成 warned/blocked,計劃〈做法〉3 與 S6 的 kind 對照表沒寫這一種
severity: minor
blocking: 否
引句:「done 而要處理 0(只列出幾筆都一樣)→ `passed`;done 而要處理有東西 → warn 記 `warned`」
file: `scripts/lumos:29436`
file: `scripts/lumos:29316`(`_drift_m1_busy` 含 `bool(res.get("long_lines"))`)
1. 輸入:done、候選 3、要處理 0、有一行超過 2 萬字沒看。
2. 程式:`_drift_m1_busy` 為真,帳 kind 記 `warned`(block 記 `blocked` 帶 hard),state 仍是 done、handle/listed 記整數。
3. 計劃〈做法〉3 帳那條與 S6 的 kind 對照寫「done 而要處理 0 → passed」,同節「有東西」定義也只列 timeout、git-failed、unreadable(沒有 error、沒有超長行)。這件事只在〈實作紀錄〉r2 的「我自己的判斷」一句帶過。
4. 連帶:RETIRE-IF 的「判不了占比」分子只數 state 是 timeout、git-failed、unreadable、error;超長行擋下的推送 state 是 done,不進分子,樣本不足檢查看不到這類「沒判完」。〈實作紀錄〉說「用 long_lines 另數」,但 RETIRE-IF 與〈做法〉4 沒有這一項。
5. 結論行句型也只在程式裡:S17 與〈做法〉3 結論行清單沒有「有 N 行太長沒看」與 error 那兩句(S17 的 `[test:t_drift_m1_conclusion_lines]` 沒釘它們;它們由 r1/r2 補的測試釘住,實跑翻紅有效)。
影響:前後說法不一致,照計劃字面寫測試或做 REVISIT 量測的人會漏掉這兩種。行為本身有測試釘住(見下面實測)。

## F2 「新建層不明給 0700 → 紅」的還原翻紅單改一處不成立
severity: minor
blocking: 否
引句:「新建的層一律明給 0700,建完再用不跟連結的 chmod 收一次」
file: `scripts/lumos:34925`
1. `_mkdir_private_layer` 同時做 `mkdir(mode=0o700)` 與 `_chmod_no_follow(cur, 0o700)`,兩者在 umask 002 下各自足以得到 0700(umask 只能減權限,mkdir 的 mode 已是 0700)。
2. 實跑:只把 mkdir 改回 `cur.mkdir()` → `t_drift_m1_review_r2_strict_home_dirs` 4 過 0 敗;只把 chmod 那行改成 `return True` → 4 過 0 敗;兩處一起拿掉 → 2 過 1 敗。
3. 計劃〈代碼審 r2 折入〉寫「翻紅:新建層不明給 0700 → 紅」,字面上單改「不明給」(mkdir 不帶 mode)測試不紅。不是行為缺陷(兩道互為備援、少一道結果一樣),只是計劃宣稱的翻紅與實際不符,也沒有測試證明「建完再 chmod 收一次」自己有作用。

## 圖譜鏡頭固定席逐條判定
- lumos-cli-read(★INVARIANT★ search 排除 superseded):diff 不碰 search 路徑,不影響。
- bound-tests-gate(code-loop check 對綁定測試逐支真跑):diff 只新增 `t_drift_m1_review_r2_*` 並沿用既有 `[test:]`,不動該閘判準;`range-unavailable` 這個結果詞只被引用、沒改該閘,不影響。
- guard-kill、授權與歸屬、測試假綠形態、lifecycle、design-loop:本輪改動不碰 guard kill rc、`_VENDORED_TOOLKIT`、re-inject、處置閘;測試假綠形態(還原翻紅要有前置斷言)——r2 三支新測試都有前置斷言(①②③各有 check),實跑我對 8 個修法逐一還原,其中 7 個翻紅,未翻紅的即 F2。不影響。
- pitfalls-code-loop(RISK):不影響。

## 實測摘要(clone 於 e6725219,`-k drift_m1` 全綠 230 過)
逐條把修法改回去只跑綁的測試:
- 翻紅:超長行不算判不了、block 不印提示、結論不講長行、桶內每 256 個不看時間、名稱索引不看時間、留痕開檔不帶 O_NONBLOCK、入口兜底改成只接別種例外、bidi 路徑不換寫法與提示照印、doctor old_sentence=off 那行拿掉、old_sentence 預設 warn 改 block(設定壞掉與缺省)、no-base 記 skipped、gov 去重鍵拿掉 check、候選端名稱正規化改回只擋控制字元、S18 名稱長度不篩、Python 判定只看終點/起點版只認終點——全紅。
- 沒翻紅:僅 F2 的單改一處。
- 計劃內部說法:〈與參考實作的刻意差異〉1–12 與〈做法〉2、3 的 group_ok 舊說法(〈代碼審 r1 折入〉)已在 r2 段註明作廢,不算矛盾。

最高等級:minor
