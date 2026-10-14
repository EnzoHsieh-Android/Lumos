severity: major

審查席:資源與時間。我讀了材料、前掃紀錄與 `scripts/lumos`,並在 scratchpad 做了實驗。實驗倉庫已刪。

## Finding 1

severity: major
blocking: 是 — 二進位檔或標了 `-diff` 的檔,兩種不同的改動算出同一個指紋。這會讓「該重讀」被當成「已對照」,正是計劃自己的 RETIRE-IF 所指的失敗。
引句:「每檔去掉 `index` 行、把 `@@ -a,b +c,d @@` 的數字換成固定字樣,其餘每一行(含空白、含上下文行、含檔頭的路徑)原樣雜湊」

問題:這份改動指紋只靠 `git diff` 文字,而且把唯一帶內容身分的 `index` 行(blob 編號)也去掉了。diff 遇到二進位檔,或被 `.gitattributes` 標成 `-diff` 的檔,只印一行 `Binary files a/x and b/x differ`。去掉 `index` 行之後,對這支檔的任何改動指紋都一樣。舊指紋認的是頂端 blob 編號,所以舊指紋抓得到,新指紋抓不到,等於退步。

失敗情境:
- 某篇筆記的 about_code 列了截圖基準圖或 fixture。作者改成圖 A、prepare 並對照完,之後又改成圖 B。
- check 算出的指紋與紀錄相同,該篇被當成已對照,推送放行。

實驗:

```
# 同一個 base,對 b.bin 做兩種不同改動,用計劃選項跑 diff
$ git --literal-pathspecs diff <計劃選項> $B $T1
diff --git a/b.bin b/b.bin
index af824ab..91d1f4b 100644
Binary files a/b.bin and b/b.bin differ
# 去掉 index 行後,內容只剩上面這三行以外什麼都沒有,兩種改動無從分辨

# x.json 加 `-diff` 屬性,{"a":2} 與 {"a":99} 兩種改動(去掉 index 行後)的雜湊
4d06bd772248ee889d1cab7d52713f9b
4d06bd772248ee889d1cab7d52713f9b
```

建議:對這類檔把 blob 編號納入指紋(例如 `--binary`,或以 `git diff --raw` 取兩邊 oid)。

## Finding 2

severity: major
blocking: 是 — 照字面實作時 git 以 129 失敗,整個功能會靜默變成永遠退回 `v1`,而 S1 到 S7 只要有一條走真實 git 就紅。
引句:「再加 `--literal-pathspecs --no-renames --diff-algorithm=myers --inter-hunk-context=0 -U3`」

問題:`--literal-pathspecs` 是 git 的全域選項,要放在 `diff` 前面。放在 `diff` 後面,git 會印 usage 並以 rc=129 結束。現有程式也是把它放在 `diff` 前面(`scripts/lumos:36216`)。計劃把它跟 diff 專屬選項寫成同一串。

失敗情境:
- 實作者照計劃串接,git 失敗。
- 計劃第 3 點把「git 失敗」歸為退回 `v1`,所以不會有任何錯誤訊息,只是從來不走 `v2`,主線前進後照樣全部重讀。
- 若 S1 這類測試只斷言「退回 `v1` 的結果也相同」之類的寬條件,測試不會紅。

實驗:

```
$ git diff --literal-pathspecs HEAD~1 HEAD   → rc=129
$ git --literal-pathspecs diff HEAD~1 HEAD   → rc=0
```

建議:計劃明寫「全域選項放 `diff` 前」。另外,S1 要能區分「走了 `v2`」與「退回 `v1`」,例如斷言指紋不等於 `v1` 的值。

## Finding 3

severity: minor
blocking: 否 — 只影響逾時與壞環境下的行為,而且對 push 閘是偏保守(多擋)。
引句:「組 diff 那次 git 逾時(`_lens_git` 預設 20 秒)」

問題:`reread-check` 有 30 秒的軟上限 `_NOTE_REREAD_BUDGET_SEC`(`scripts/lumos:35999`)。新增的 diff 用固定的 20 秒 `_lens_git` 上限,不吃剩餘預算。

連鎖後果:
- 算指紋(`_note_reread_fps`)在 `_note_reread_verdicts` 之後、`_note_reread_layer2` 之前。diff 若吃滿 20 秒才逾時,後面第二層拿到的預算所剩無幾。
- 第二層一過截止時間就丟 `_NoteRereadStop`(逾時)。`gate=block` 時「判不了」就是擋,不是退回 `v1`。
- 所以計劃說的「退回只會讓已對照的被多列」在這條路徑不成立,實際是整個推送被擋。
- 反方向也有問題:逾時是看時間的,同一份輸入有時算 `v2`、有時算 `v1`。prepare 沒有截止時間,check 有。prepare 記的是 `v2`,check 逾時算成 `v1`,紀錄就對不上。這又回到舊設計否決含 diff 指紋的理由「提醒永遠消不掉」。

建議:
- diff 的 timeout 取 `min(20, 剩餘預算)`。
- 逾時時明寫是退回 `v1`,還是進入「判不了」。
- 在計劃或驗收條款裡補一句「`v1` 與 `v2` 並存時 check 永遠只算其中一種」的保證,或承認此不確定性並附回頭看的條件。

## Finding 4

severity: minor
blocking: 否 — 屬於記憶體與正確性的邊角,不影響正常的原始碼檔。
引句:「所有候選的 about_code 聯集只跑一次 `git diff`,逐檔結果快取起來給每篇用」

問題:
- (a) 輸出沒有大小上限。實測一支 120MB 的 about_code 檔全行改動,git 本身只花 1.33 秒、RSS 約 622MB,輸出 244MB。
  - Python 端要用 `capture_output` 收進記憶體,再切檔、解碼、逐行正規化,峰值估計在 1GB 以上。
  - 這個大小在 20 秒內不會逾時,所以也不會退回 `v1`。
  - 材料沒有要求輸出上限,也沒有「單檔 diff 超過 N 就記成 `v1`」的規則。
  - 真實的 `scripts/lumos`(3.2MB)只要毫秒,沒有問題。
- (b) 快取沒說 key 與生命週期。若實作成模組全域、只用路徑當 key,會出兩個問題:
  - 一次 push 的 hook 處理多個 ref 時,不同頂端會共用第一個 ref 的 diff。
  - `test_lumos.py` 在同一個行程裡跑很多暫存 repo,都叫 `a.py`,會互相污染。
  - 計劃只說「同一次 check 或 prepare 裡」,但沒說放在 `scan` 裡,也沒說 key 含 `(base, tip, 檔)`。
- (c) 解碼用 `errors="replace"` 時,不同的非 UTF-8 位元組都變成同一個替代字元。實測 `b"\xe9"` 與 `b"\xe8"` 解出來相等,為 True。在 Big5 或 latin-1 的原始檔裡,只差位元組的兩種改動會得到同一個指紋。
  - 計劃寫「原樣雜湊」,但沒說雜湊位元組還是解碼後的字串。

建議:
- 對單檔 diff 設大小上限,超過就退回 `v1`。
- 快取放進 `scan`,key 含 `(base, tip, 檔)`。
- 雜湊直接用位元組,不要先解碼。

## Finding 5

severity: minor
blocking: 否 — 只影響本機設定與別支 worktree 造成的指紋抖動,結果偏保守(多列)。
引句:「S5 補 `diff.interHunkContext`、`diff.mnemonicPrefix`」

問題 1:釘住的 diff 設定還是有漏。
- 實測 `diff.suppressBlankEmpty=true` 會把空白上下文行從單一空格變成空行。同一支改動的雜湊就變了(`f3e3a577…` 對 `8de40af5…`)。
- `core.attributesFile` 與 `.git/info/attributes` 也會讓同一支檔在不同機器上走 `-diff`,指紋不同。
- S5 的列舉表漏了這兩類。CI 與本機的差異只造成多列,但同一台機器上全域設定不同的 hook 環境也會讓 prepare 與 check 對不上。

問題 2:分岔點取決於共用 refs。
- 計劃 S3 只保證「同一份 refs 狀態下必然相同」。
- 多 worktree 共用 `refs/heads`,另一個會談把本機 `main` 快轉到含有作者部分提交,或把 `main` 推進到含頂端。這時 `merge-base --all` 的結果變成頂端本身,第 3 點會退回 `v1`。
- 一個 prepare 和 check 之間做了這種動作的分支,v2 紀錄全部失效。`gate=block` 下需要重 prepare。
- 另外,指向頂端的本機分支「多於一條」時退回目前簽出的分支。新開的 worktree 分支剛建好時就常是多條指向同一個提交。這時換一個 worktree 跑 prepare 與 check,選到的遠端可能不同。
- 這是被計劃接受的「偏保守」方向,不會漏判,但應該在計劃裡明寫成已知會抖動,並附回頭看的條件。

建議:補 `diff.suppressBlankEmpty`,並把「分岔點取決於本機共用 refs,他人移動本機 main 會讓 v2 紀錄失效」記為已知行為。

## 已讀,無 finding

- 主線前進後 rebase、作者改動不變時指紋不變:設計合理。`git merge-base --all HEAD <候選…>` 是對候選的假想合併求共同祖先,候選集合在 fetch 後只會單調變新,不會把分岔點拉回更舊的位置。
- prepare 到 check 之間 `git fetch` 但沒 rebase:分岔點不變,指紋不變。
- 效能:在 `reread-fp`(2911 個提交)上,`git rev-list --count HEAD` 約 18ms、`merge-base --all` 約 18ms,`_push_pick_base` 的歷史計數成本可忽略。
- 紀錄檔格式不變、`v1`/`v2` 輸入不撞、`reread-record` 不重算對照指紋:已讀,無 finding。

我另外在 `/tmp/claude-501/` 留的暫存輸出(`x.out`、`x.err`)與 scratchpad 的實驗倉庫都已刪除。

最高等級 major,共 2 條 blocking(Finding 1、2),其餘 2 條 minor 非 blocking。
