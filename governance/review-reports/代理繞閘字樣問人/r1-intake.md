preflight-4: ran

# r1 收貨紀錄(代理繞閘字樣問人)

## 首輪前掃(便宜 agent,固定清單①未定義詞②壞引用③範圍矛盾④機械宣稱驗語意)

①②③與存在類命中直接修真檔,不算 findings;④語意類命中逐條修真檔並留前後對照如下。本計劃沒有「核心裁定」節,前掃沒有動到需升級的裁定。

| # | 類 | 修改前 | 修改後 |
|---|---|---|---|
| p1 | ④語意 | 只寫新增掛鉤檔與 merge 註冊 | 加 `_GLOBAL_CLAUDE_HOOKS`(否則不複製、`_prune_dangling` 剪掉註冊)、`enforcement_status` 一列、釘列數測試 24→25、`_VENDORED_TREE_FILES`、`ANCHOR_FILES`;lands_in 加 Systems/lumos-cli-lifecycle |
| p2 | ④語意 | 未提 `HOOK_BUDGET` 會在命令列附 `--budget` | `HOOK_BUDGET` 加鍵 5 秒;掛鉤忽略命令列參數;S4 加帶 `--budget 5` 案例 |
| p3 | ④語意 | commit 帶含 `n` 的短旗標組即命中 | 逐字看短旗標,遇吃值旗標(`-m -F -C -c -t`,`-S -u` 只黏著)停;`-mnote`、`-m -n` 不命中;S1/S2 加案例 |
| p4 | ①範圍 | 列 `HUSKY=0` | 不列,〈範圍〉寫理由(Lumos 閘走 core.hooksPath,HUSKY=0 關不到);S2 加 `HUSKY=0 git commit` 放行 |
| p5 | ④語意 | 未提 Codex | `_codex_entries` 會原樣把 Bash matcher 寫進 Codex → 改為跳過;S5 加 Codex 目標無註冊 |
| p6 | ④語意 | heredoc 內容「放行」只寫在條款 | 做法加「切段前剝掉 heredoc 內容」;〈範圍〉加 `bash -c`、`$()`、`eval` 攔不到;S2 加 `<<-"END"`、`<<EOF \| tee` 案例 |
| p7 | ③範圍 | PRIOR-ART 未講與總覽第 7 名差異 | 補:只 Claude、不寫治理帳、不列 LUMOS_STOP_BLOCK_OFF 與 HUSKY=0 |
| p8 | ④語意 | RETIRE-IF 量「使用者按允許的比例」 | 事件帳無此欄;改為掛鉤自記 `ask:` note + 事件帳同指令有無執行紀錄;取捨以 decision-add 記 |
| p9 | ④語意 | 每次判完都記 ok 存活事件 | `guard` 每次跑 git 子程序並寫事件,檔滿 512KB 砍到 2000 行 → 會擠掉其他掛鉤;預篩移到 guard 之外,只有過預篩才記;S4 加「沒過預篩不寫事件」 |
| p10 | ④語意 | 任何例外放行,寫 error | 明定 `guard(..., swallow=True)`,內部吞例外要 `mark("error")`;S4 加壞事件記 error |
| p11 | ④語意 | lumos-guard「有結構規則禁止跑外部指令與寫檔」 | 改為「依 d4 不跑外部指令、只對審查席生效」 |
| p12 | ②引用 | 對照舊決定只寫 d4 | 改為 d3、d4(d4 取代 d3 事後查部分,保留 Bash 粗擋) |
| p13 | ③範圍 | 實測段未註明模式 | 註明「非互動模式」 |

## 開案前舊否決比對(lumos rejections 209 筆,按概念)

- 「不新增寫帳」(rtb 實測回饋⑤):本計劃只在既有 `_hookevent` 存活事件加 note,不開新帳 → 不撞。
- impact 鏡頭機械化 d2 重開條件「守衛誤擋會訓練人繞過,誤擋率是首要設計約束」:本計劃選逐段解析寧可漏問,同向 → 不撞。
- 審查席唯讀隔離 d4(粗擋寧可誤擋):範圍不同(審查席/擋 vs 主會談/問人),計劃 PRIOR-ART 已寫明 → 不撞。
- 審查跑滿回顧 d3「專案慣例偏好機械擋」:本計劃是機械問人,不是只提醒 → 不撞。

## 機械排乾

- refcheck:6 條宣稱,5 條對得上,1 條 missing 是本計劃要新增的 `scripts/hooks/claude/bypass-ask-hook.py`(預期)。
- prose-lint:0。pitfalls --check:有節,命中類四類皆有答。
- spec-gate:風險高(守衛面、不可逆關鍵字、連到 lumos-cli-lifecycle);條款 6 條全標(綁 5、人 1);S1–S5 紅(未實作,合法);相依回歸 1 支綠。

## 收貨(四席全數交回後一次寫入)

- 四份席報告從逐字稿取最後一則以 `severity:` 開頭的完整回答原樣存檔;`git status` 只有我自己開案產生的 `docs/.canary-log.jsonl` 改動,`git reflog -3` 無席位提交。
- report-normalize:四份皆已是正規化格式。quote-check:四份全數錨定。refcheck:通才 12/12、邊界 8/9(missing 為本計劃要新增的掛鉤檔)、資安 0、架構對齊 20/20。seat-check:只觀測,通才、資安、架構對齊未逐字提到快照路徑(引句全錨定快照,判讀時不扣)。
- 彙總載體 `r1-carrier.md`:四份報告逐字串接,只在每條 severity 行前加 `ID:` 行;33 條,全數錨定。

## 編排者機械重現(判讀前自己跑過)

| ID | 觀察 | 重現命令 | 結果 |
|---|---|---|---|
| t1 b7 s3 b10 | shlex 不把換行當分隔、`);` 黏成一詞、前綴詞讓程式名不是 git | `python3.14 -c` 以 `shlex.shlex(c,posix=True,punctuation_chars=True)` 切三條指令 | HIT:`git status\ngit push --no-verify` → 同一段;`(cd /tmp/x && true); git push` → `');'`;`timeout 60 git push` 首詞 timeout |
| t3 b3 | `git config --unset core.hooksPath` 是拆閘 | `sed -n 23245,23251p scripts/lumos`、`grep -n 'unset core.hooksPath' scripts/lumos` | HIT:lumos deinit 拆閘即此指令(23249、23430) |
| t4 | LUMOS_SKIP_* 有些是 lumos 自己的閘讀 | `grep -o 'LUMOS_SKIP_[A-Z_]*' scripts/lumos` | HIT:9 個,含 FIX_CHECK、NOTE_AUDIT、LINT_NEW、CODE_LOOP、BOUND_TESTS |
| a1 b4 | HOOK_BUDGET 每項都要有 `_inner_budget` 逐字複本 | `sed -n 17908,17925p scripts/test_lumos.py`、`grep -n '^_BUDGET_RATIO' -A30 scripts/hooks/claude/impact-hook.py` | HIT:測試以 `--budget` 載入並呼叫 `mod._inner_budget`;另有 `_sigs` 唯一版本守衛 |
| a2 b5 t9 | 事件名須等於列名;無近期成功是 stale 不是 unknown | `sed -n 23325,23356p scripts/lumos` | HIT:`e.get("hook") != hook_name` 且無紀錄回 stale |
| a3 | 存活事件只記活著沒、不記成效 | `sed -n 9575,9582p scripts/lumos` 與 `_hookevent.py` 檔頭 | HIT:明文「不印注入 N 次——那是成效」 |
| b2 s2 | 暫存目錄有真工作副本對真遠端推送 | 一次性腳本掃事件帳 `git … push … --no-verify` 與 `cd /tmp` | HIT:push --no-verify 暫存 5、真目錄 3;config hooksPath 暫存 16(全為審查席新實驗 repo)、真目錄 7(全為讀值) |
| b11 | 10 萬字單詞 shlex 約 0.25 秒 | 席位實測(邊界席報告),本輪改以長度上限 2 萬字走字面判,不再重量 | 採信(折入改做法,原量測不再是瓶頸) |
| 其餘 | heredoc、預篩、cd 語意、mktemp、全域選項、暫存根名單等 | 以凍結快照字面推演,與席位描述一致 | 採信 |

## 處置

- 33 條全部折入計劃(見計劃〈審計修正紀錄〉r1),0 條放行,0 條列為重現不到。
- 依根因分九組折:①切段改成「任何不在引號裡的 git 詞開始一條 git 指令」(t1 t7 b7 b10 s3);②拋棄式判定:生效目錄定義、子殼層、cd -/~、realpath、mktemp 只認賦值變數、暫存根對齊 lumos-guard、commit/設定類以 git-common-dir 確認非真 repo 工作樹、push 以遠端位址判(t2 t8 b1 b2 b8 s1 s2 a6);③拆閘形狀:config --unset/空值/--replace-all/--add,LUMOS_SKIP_* 接 lumos 指令(t3 t4 b3);④安裝面:逾時預算逐字複本、anchor approve、事件名對齊列名(a1 a2 b4 b5 b6);⑤存活事件不記問人,量測改重跑分類函式(a3);⑥heredoc 邊界(t5 b9 s4);⑦預篩吃原始文字、自包 try、拿掉「同一行」、加縮寫、次數更正(t6 b12 a5);⑧長度上限與三種最壞形狀計時(b11);⑨措辭:stale/unknown、逾時不留痕與不用失敗即擋、厚掛鉤有意偏離、無人值守、S6 退路改用使用者自己驚嘆號前綴執行、測試補提交訊息含字樣(t9 s5 s6 a4)。
- 鏡像核對另派便宜代理看本輪 diff(材料含本卷證目錄),結果另存 `r1-mirror-audit.md`。

## 鏡像核對處理(r1-mirror-audit.md)

- 第一段 1–10 條全處理:S2 here-string 句移到 S1 並改「後面的繞閘照問」;S1 補 merge/rebase/am/cherry-pick/revert 與 config 寫入形狀;〈做法〉寫明其他命中類型不給拋棄式豁免、mktemp 目錄的 push 仍照遠端規則;預篩改為同時有 `git`、`commit` 與含 n 短旗標,照定案預篩重量為一週 371 次(28480 條中;三字樣 279、另 92);error 事件說法限定「過了預篩之後」;兩條 decision-add 已記(d1 厚掛鉤偏離、d2 寧可漏問與拋棄式只給確定非真 repo);「現為 24 列」改「原為 24 列已改 25」;計劃寫出 `_temp_roots()`;沒加引號的字面與重設 hooksPath 回 Lumos 目錄列為刻意接受的誤問。
- 第二段 b3、b12、a4 未完成的部分同上補齊;測試補 S1 十二案、S2 十案、S3 九案、S4 一案(decide 吞例外要 mark error)。
