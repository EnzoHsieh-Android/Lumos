<!-- r1 鏡像核對(便宜代理,只看本輪 diff 與卷證;不是審查席) -->
## 第一段:鏡像一致

**逐項核對(你點名的八項)**
- **事件名**:一致。〈做法〉、S4、S5 和測試都寫 `pretooluse-bypass-ask-hook`,舊的 `bypass-ask-hook` 字樣已沒有殘留。
- **存活事件記不記「問了」**:一致。PRIOR-ART、〈做法〉(「不加任何『問了』的備註」)、〈回退〉、〈實務隱患〉、S4 測試(`not note`)都是不記。
- **長度上限**:一致。〈做法〉兩處、S4、測試都是 2 萬字。
- **預篩次數**:一致。〈量測〉和〈實務隱患〉都是約 392 次(268+124)。
- **heredoc 規則**:〈做法〉、〈範圍〉、白話摘要互相吻合。
- **LUMOS_SKIP 範圍**:大致一致,差異見下面第 3 條。
- **enforcement 顯示什麼**:一致。〈做法〉寫 stale 或 unknown 且不進分母,〈實務隱患〉寫 error 事件要看 `lumos gov --stats`。
- **拋棄式判定規則**:〈量測〉第 33 行自己註明舊口徑比定案寬,所以不算矛盾。其餘不一致見下面各條。

**不一致或缺口**
1. **S2 條款與 S2 測試相反**。
   - S2 條款寫:「here-string 與引號裡出現 `<<` 時,掛鉤 應 不輸出、放行」。
   - 測試 `t_bypass_ask_ignores_mentions` 的後半段斷言:`cat <<< "x"\ngit push --no-verify` 這類指令要 ask。
   - 條款漏寫「後面還有真繞閘就照問」,字面讀會與測試相反。
2. **S1 的涵蓋比〈做法〉窄**。
   - S1:「`-c core.hooksPath=` 接 commit/push」。〈做法〉:接 commit/push/merge/rebase/am/cherry-pick/revert。
   - S1:「在 git commit/push 或 lumos 指令前設 `LUMOS_SKIP_*`」。〈做法〉:commit/push/merge。
   - 白話摘要只說「推送或提交」,沒提 merge。
3. **〈做法〉的拋棄式判定沒涵蓋全部命中類型**。
   - 豁免規則只列 commit/merge、`config-hookspath`、`c-hookspath` 接 commit/merge、`lumos-skip` 接 commit/merge,以及 push。
   - 沒說明:`c-hookspath` 接 rebase/am/cherry-pick/revert,以及 `lumos-skip` 接 lumos 指令,在暫存目錄裡算不算拋棄式。⚠ 看起來是預設「問」,但沒寫。
4. **mktemp 目錄的 push 判定互相打架**。
   - 第 89 行:「`VAR=$(mktemp …)` 的新暫存目錄一律算拋棄式」。
   - 第 88 行:push 時「目錄還不存在、沒寫遠端 → 非拋棄式」。
   - `d=$(mktemp -d); git -C $d push --no-verify` 該走哪條沒定。⚠
5. **392 次的量測口徑已過時**。
   - 392 是依 b12 的舊定義(commit 之後同一行出現含 `n` 的短旗標)量的。
   - 〈做法〉現在是看整段原始 stdin,只要同時有 `commit` 和含 `n` 的單橫線旗標就過預篩,範圍更寬。
   - b12 建議的「`commit` 前要有 `git`」沒採納,所以 `pre-commit` 路徑仍會過預篩。
   - 〈量測〉第 35 行三個字樣寫 `--no-verify`,〈做法〉預篩用 `--no-veri`。
   - 〈實務隱患〉的 392 因此可能偏低。⚠
6. **〈實務隱患〉對 error 事件的說法略過了預篩階段**。
   - 第 122 行與「自我治理」寫「丟例外會記 error」。
   - 〈做法〉說預篩階段的例外是放行且不記事件。
7. **PRIOR-ART 說的決策紀錄還沒落地**。
   - PRIOR-ART 寫「以 `lumos decision-add` 記進本篇 decisions」,共兩處(薄殼偏離、逐段解析對比 d3/d4)。
   - 計劃的 frontmatter 沒有 `decisions:` 欄位,`Systems/代理繞閘問人` 節點也還不存在。
   - 這可能只是待辦。⚠
8. **「現為 24 列」可能已過期**。
   - 〈做法〉寫「釘住列數的測試(現為 24 列)同步改成 25」。
   - carrier 的 t 席紀錄說 `scripts/test_lumos.py` 的 36231 行已經是 25,而且工作樹裡這個檔有未提交改動。⚠
9. **測試依賴的名稱計劃沒寫**。測試覆寫 `m._temp_roots`,但〈做法〉只命名了 `decide` 和 `bypass_reasons`。
10. **「找 git 詞」規則會誤問未加引號的字面**。
    - 〈做法〉:段裡任何一個等於 `git` 的詞都算起點。
    - `echo git push --no-verify`(未加引號)會被問,但白話摘要承諾「字面提到一律放行」。
    - S2 只測了整串加引號的情形。⚠

## 第二段:33 條逐 ID 對照

- **t1**:有。〈做法〉「切詞與切段」「找 git 指令」,S1 和測試已涵蓋多行、括號、`then`、`env`、`timeout`。
- **t2**:有。〈做法〉第 83、89 行只追蹤 `VAR=$(mktemp)`,S3 有反例。
- **t3**:有。第 77 行 `config-hookspath` 含 `--unset`、`--unset-all`、`--replace-all`、`--add` 和空字串值,測試已涵蓋前三項。
- **t4**:有。第 78 行 lumos 指令前的 `LUMOS_SKIP_*` 也命中,S2 已改成「git 與 lumos 以外」。
- **t5**:有。heredoc 規則已補,bash/sh/ssh 的 heredoc 列進〈範圍〉當攔不到。
- **t6**:有。預篩看原始 stdin,不限同一行。
- **t7**:有。第 71 行:子指令前所有 `-` 開頭的詞都跳過,吃值的選項再多吃一個詞。
- **t8**:有。第 82–85 行涵蓋相對路徑、`~`、`cd -`、子殼層、`TMPDIR`。字面 `$TMPDIR/x` 只靠「展開不了的變數 → 判不出」隱含處理。
- **t9**:有。mktemp 反例、`--unset` 案例、提交訊息反例、長度上限、stale 措辭都補了。
- **b1**:有。同 t2。
- **b2**:有。第 87–88 行用 `rev-parse --git-common-dir` 和 `remote get-url`,〈量測〉第 33–34 行補了依據。
- **b3**:只處理一半。`--unset` 和空值都補了。反向問題(Lumos 安裝時自己把 `core.hooksPath` 設成 `scripts/hooks`,重設會被問)計劃沒表態。⚠
- **b4**:有。第 58 行複本預算、吃 `--budget 5`,S4 有測試。
- **b5**:有。事件名對齊,stale/unknown 措辭已更正,error 事件的說法也已更正。
- **b6**:有。第 99 行 `lumos anchor approve`。
- **b7**:有。換行當分隔、`);` 等標點詞、續行都有寫。
- **b8**:有。生效目錄、`cd` 追蹤、realpath、`TMPDIR`、`cwd` 缺欄都有寫。
- **b9**:有。here-string、引號內 `<<`、多個 heredoc、無結束字、`<<-` 都有寫。
- **b10**:有。「任何詞等於 git」取代程式名比對,縮寫 `--no-verif` 也算。
- **b11**:有。2 萬字上限加字面判,S4 有三種最壞形狀的計時。
- **b12**:只處理一半。392 次和原始 stdin 預篩、只讀一次、預篩有 try/except 都改了。「`commit` 前加 `git`」沒採納,量測口徑也沒重算(見第一段第 5 條)。
- **s1**:有。第 81–82 行,`-C` 優先、後者覆蓋前者、判不出就當非拋棄式。
- **s2**:有。push 目標檢查和共用 git 目錄檢查。
- **s3**:有。同 t1、b10。
- **s4**:有。找不到結束字就不剝。
- **s5**:有。〈實務隱患〉第 122 行補了逾時放行且不留痕,也討論了不採用 `onFailure: block` 的理由。
- **s6**:有。S6 的 manual 條款改成用驚嘆號前綴自己執行,並要求改 deny 前重讀 RETIRE-IF。
- **a1**:有。第 58 行。
- **a2**:有。事件名對齊。
- **a3**:有。PRIOR-ART 和〈做法〉第 57 行不再記問了幾次。
- **a4**:只處理一半。偏離的理由寫進了 PRIOR-ART,但 `decision-add` 還沒做(見第一段第 7 條)。⚠
- **a5**:有。第 52 行。
- **a6**:有。realpath、聯集 `/var/tmp`、`..` 處理。

審計紀錄寫「33 條全部折入」,實際是 b3、b12、a4 各有一小塊沒處理或還沒落地。blocking 18 條的計數正確。

**〈做法〉有寫但五支測試沒驗的行為**
- **拋棄式判定**:
  - `pushd`/`popd`、`cd` 無參數、目標含 `$(` 或反引號。
  - 相對 `cd` 疊加,`-C` 優先於 `cd` 的反向情形,`git -C .` 或 `-C ..`。
  - 符號連結經 realpath,`TMPDIR` 沒設或為空,以及暫存根清單本身(測試把 `_temp_roots` 整個換掉)。
  - 變數必須先出現才展開。
  - push 的 `./`、`../`、`file://` 目標,`remote get-url` 查不到,git 子程序逾時。
  - `lumos-skip` 在暫存目錄,merge 在暫存目錄。
- **命中規則**:
  - `c-hookspath` 接 rebase/am/cherry-pick/revert。
  - `config` 的 `--add`、`--replace-all`、`--list`。
  - commit 吃值旗標 `-C -c -t -u`。
  - 非 `--no-verify` 前綴的詞(如 `--no-verified`)。
  - `export LUMOS_SKIP` 接 lumos 指令,`LUMOS_SKIP` 接 merge。
- **切詞**:
  - 引號內的換行留在詞裡(多行提交訊息)。
  - 單引號內的「反斜線加換行」保留。
  - `2>&1` 之類的複合標點。
- **heredoc**:
  - `<<` 結束字不能縮排(只有 `<<-` 吃 Tab)。
  - `$((1<<2))` 算式。
  - 無結束字的 heredoc 只有計時測試,沒有單獨驗證「不剝」。
- **預篩與錯誤**:
  - 預篩階段丟例外(測試只送非 UTF-8 和非字串 command,這兩種都在 UTF-8 替換或預篩 try/except 之外或之內不確定走哪條)。
  - 「`main` 內部吞例外時要 `mark("error")`」:`decide` 內丟例外的測試只檢查不往外丟、回放行,沒檢查有 error 事件。
- **註冊**:
  - 逾時預算複本逐字相同和 `anchor-baseline` 鍵集合,靠既有守衛測試,不在這五支裡。
  - 〈做法〉第 98 行的 stale/unknown 顯示沒有測試。

**測試有、計劃沒寫成條款的**:非 UTF-8 輸入和非字串 `command` 的放行(S4 條款沒列),以及 `_temp_roots` 這個介面名。

相關檔案:
- 計劃:`/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/docs/lumos-toolchain-knowledge/Projects/代理繞閘字樣問人_計劃.md`
- 測試:`/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/test_lumos.py` 的 `t_bypass_ask_*`,約第 40987–41230 行
