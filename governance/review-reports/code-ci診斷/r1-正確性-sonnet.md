severity: blocker

# r1 正確性審查——CI「切片測試紅了印診斷」那段 shell

審的材料:`governance/review-reports/code-ci診斷/r1-snapshot.patch`(36 行,只動 `.github/workflows/ci.yml` 的「Full test suite」那一步)。這段 diff 已經在 main 上(commit `8b0dfa8a`),不是待審的暫存改動,所以下面找到的問題是現在就活著的。

背景一句話:這步用的是 GitHub Actions 沒寫 `shell:` 時的預設殼——`bash --noprofile --norc -eo pipefail {0}`。已核對過 `.github/workflows/ci.yml` 全檔和 `.github/` 底下都沒有任何 `shell:`/`defaults:` 覆寫(`grep -n shell -R .github/` 零結果),所以「這一步是 bash -e」只講對一半:實際上 `pipefail` 也開著,而 pipefail 開不開,正是下面這條發現能不能踩到的關鍵開關。

## 發現一:第二道 grep 找不到東西時,整支腳本會在 pipefail 下當場死掉,後面沒跑到的片全部消音

新增的診斷分兩層:第一層(抓「所有 ✗ 與 EXCEPTION,給總覽」)用的樣式是 `^  ✗|EXCEPTION`,涵蓋範圍夠寬,幾乎不會落空。但第二層(挑「要展開前後文的那幾行」)用的樣式更窄,只認「每支測試跑完印的彙總行」`✗ FAILED <名字>(N 條斷言)`或 `EXCEPTION`——這兩種都是 `scripts/test_lumos.py` 裡「單一斷言失敗」這條主流路徑才會印的字樣(file: `scripts/test_lumos.py:28484`)。同一支測試還有另外三種真實會發生的「紅」,印的字樣完全不含「FAILED」也不含「EXCEPTION」:

- 逾時:file: `scripts/test_lumos.py:28492` 印的是「✗ TIMEOUT ...」
- 一條斷言都沒驗到:file: `scripts/test_lumos.py:28479` 印的是「✗ ...: 跑完了但一條斷言都沒有」
- 跳過支數超過基準線判紅:file: `scripts/test_lumos.py:28561` 印的是「✗ 判紅:這台是來源 repo...」,而且這行印在總彙總行(file: `scripts/test_lumos.py:28542`)之後才把 FAIL 加 1(file: `scripts/test_lumos.py:28567` 的 `return` 讀到的是加過的值),所以連「, N failed」那行都可能還停在「, 0 failed」——這一片會紅純粹是因為那一行「✗ 判紅」。

這三種情況下,外層判斷「這片紅不紅」(`, [1-9][0-9]* failed" 或 "^  ✗`)照樣抓得到、判定沒錯,但第二道窄樣式的 `grep -nE "^  ✗ FAILED|EXCEPTION" ... | head -3 | cut -d: -f1 | while read ln; do ... done` 一個字都比對不到,`grep` 回傳碼是 1。這是一條沒被 `if`/`&&`/`||` 保護的獨立管線敘述,pipefail 開著時整條管線的結束碼會被判成非 0,`set -e` 立刻讓整支 step 腳本中止——連同一片剩下要印的「失敗處前後文」「以下是該片尾端」`tail -25`都不會印,更嚴重的是**後面還沒跑到的片(第 3、4 片)整段迴圈直接被砍掉,連它們原本一定會印的 `tail -25` 都消失**,也繞過了原本統一收尾用的 `exit $rc`。

這三種恰好都是「CI 紅、本機綠」最常見的成因(跑在共用 runner 上才會超時、跳過數才會跟本機不同),也就是這次改動本來想解決的那類案例。實測用構造的紀錄檔重現如下。

引句:「grep -nE "^  ✗ FAILED|EXCEPTION" "/tmp/shard-$i.log" | head -3 | cut -d: -f1 | while read ln; do」

severity: blocker
blocking: 是——這是已經在 main 上的行為,下一次遇到「紅的那片沒有印出 ✗ FAILED/EXCEPTION 字樣」(逾時、零斷言、skip 基準線判紅)就會複現;後果不是「判定錯」而是「診斷用的新功能自己先斷氣,還把舊有『四片都印尾端』的保底行為也一起拖垮」,比改之前更難查,應該在合併前補上保護再上。

## 發現二:新的兩道 grep 沒有比照同一支腳本裡既有的「防 -e 誤殺」寫法

同一個 step 裡,舊碼本來就知道要防這件事:file: `.github/workflows/ci.yml:34` 的 `wait "$job" || rc=1` 用 `||` 接住背景工作的非 0 結束碼,不讓 `set -e` 把整段迴圈砍斷;同一份工作流程稍後的 file: `.github/workflows/ci.yml:71`(`git cat-file -e ... || BEFORE="$EMPTY"`)和 file: `.github/workflows/ci.yml:73`(`python scripts/lumos code-loop check ... || { rc=$?; ...; exit "$rc"; }`)也都是同一種「先接住、自己決定要不要死」的寫法。這次新加的兩道 `grep`(file: `.github/workflows/ci.yml:41` 與 file: `.github/workflows/ci.yml:43`)是本步驟裡少數沒有套用這個既有慣例的獨立管線敘述,才會被發現一裡的情境刺穿。

引句:「grep -nE "^  ✗|EXCEPTION" "/tmp/shard-$i.log" | tail -40」

severity: minor
blocking: 否——單獨看這一行不會觸發中止(`tail -40` 對空輸入也回 0,見下方實驗②/④),真正會炸的是發現一那條;這裡列出來是說明為什麼會漏——同一支腳本明明已經有現成的防護寫法可以抄,這次沒抄。

## 檢查過、沒發現問題的部分

- `set -u`:新增行只用到既有的 `$i`、迴圈自己 `read` 出來的 `$ln`,沒有引用任何未賦值變數。
- `while read ln` 裡的算術展開 `$((ln>12 ? ln-12 : 1))`:bash 的算術情境支援 C 風格三元運算,語法合法;`ln` 一定來自同一份檔案裡 `grep -n` 抓到的行號,不可能大於檔案總行數,所以永遠不會出現「起始行號超出檔案範圍」。
- `sed` 的結尾行號(`ln+3`)超出檔案總行數時:不管是這台機器的 BSD sed 還是 CI 用的 GNU sed,對「結尾位址超過檔尾」都是印到檔尾就停、不是報錯(已用 2~3 行的極短檔實測,見下表);唯一會報錯的是「起始位址」本身不合法,而上面已經說明起始位址不可能出現那種情況。
- 輸出量:三段輸出各自有硬上限——`tail -40`(每片最多 40 行)、`head -3` 後每個命中最多展開 `12+1+3=16` 行(最多 3 個命中,即 48 行)、`tail -25`;四片全部疊起來也就數百行等級,不會到「上萬行」。
- 這一步的紅/綠判定本身:確認過發現一那種「提前中止」的案例裡,提前中止一定發生在「這片真的有失敗、`rc` 本來就會被設成 1」的前提下(外層 `if` 判紅為真,代表 `wait` 那支子行程本來就以非 0 結束),所以就算腳本在中途被 `errexit` 打斷,整個 step 仍然是紅——不會把紅誤判成綠。問題只出在「診斷印不完整、後面的片被消音」,不是「判定顛倒」。

## 實驗記錄

以下每個案例都是把 diff 裡的原始 shell 逐字抄到 `/tmp/ci-shell-test/`,搭配 `set -eo pipefail`(對照這一步實際會用到的 GitHub Actions 預設殼)實測,沒有動過 repo 裡任何檔案。

| 餵的紀錄檔(內容重點) | 對照的情境 | 輸出結果 | 判定 |
|---|---|---|---|
| 只有 `✓` 與 `40 passed, 0 failed` | ①全綠 | 正常印尾端,不進診斷分支 | 正常 |
| 中段有一行 `✗ 某斷言 detail`,接著同一測試的彙總行 `✗ FAILED t_middle_broken(1 條斷言)`,前後各十來行 `✓` | ②紅在中間 | 兩層診斷都正確找到、印出前後文,再印尾端 | 正常 |
| 第 1 行就是 `✗ FAILED t_first_line_broken(1 條斷言)` | ③紅在開頭第一行 | `sed` 起始行自動夾到 1,沒有報錯,前文只印得到的部分 | 正常 |
| 0 位元組空檔 | ④空檔 | 外層 `grep -q` 沒命中,判綠,不進診斷分支,腳本沒中斷 | 正常 |
| 2 行:`✗ FAILED t_x(1 條斷言)` + `1 passed, 1 failed` | ⑤只有兩三行的極短檔 | `sed` 結尾行超出檔案總行數,照樣印到檔尾、`rc=0`,沒有報錯 | 正常 |
| 只有 `40 passed, 3 failed`(整檔沒有任何 `✗`) | ⑥沒有 ✗ 但結尾寫著 failed | 外層判紅命中(靠「, 3 failed」),第一層 `grep` 找不到東西(rc=1)、第二層也找不到——單獨測第二層:管線在 pipefail 下回傳非 0 | **腳本會被 `set -e` 中止** |
| 4 片組合:①(綠)+ ⑥的變體(只印「這次跳過 N 支…」+「✗ 判紅:這台是來源 repo…」,沒有任何 `FAILED`/`EXCEPTION` 字樣)+ ③(紅在開頭)+ ①(綠) | 完整跑一次四片迴圈,模擬 `test_lumos.py` 真實存在的 skip 基準線判紅路徑 | 印完第 2 片的「這一片紅了…」標題後,腳本就以 `rc=1` 中止;第 2 片的「失敗處前後文」沒印出來,**第 3 片(真的有一行 ✗ FAILED 在第一行)和第 4 片(全綠)完全沒有任何輸出**,也沒有走到腳本原本收尾用的 `exit $rc` | **確認發現一成立** |

## 結論

這段 diff 在最常見的「單一斷言失敗」情境下沒問題,`set -u`、三元算術展開、`sed` 邊界、輸出量都經過實測沒發現異常。但新增的第二層前後文擷取管線,遇到 `test_lumos.py` 自己本來就有的三種非典型紅(逾時、零斷言、跳過基準線判紅)時,會在 GitHub Actions 預設的 pipefail 殼下被 `set -e` 提前打斷整支腳本,導致後面還沒跑到的片全部沒有輸出、連改動前就有的「四片都印尾端」保底行為也一起被犧牲掉——而這三種紅剛好就是最容易長成「CI 紅、本機綠」的那種。這條已經在 main 上,建議把兩道新 grep 比照同一支腳本裡既有的 `|| rc=1` / `|| { ... }` 寫法接住空結果,再上。

全篇最高等級為最嚴重的一級(阻擋合併),共有一條發現落在會擋的等級。

## 驗收(2026-09-15)

先講結論:協調者這項訂正是對的,我自己重查了一遍,證據站得住;原本報告裡「機制」那半沒錯,但「後果」那半確實講重了。

**第一步:查「這一步實際用哪種殼」有沒有搞錯。** 我原本認定「沒寫 `shell:` 時,GitHub Actions 在 Linux 上一樣會帶 `pipefail`」,這個假設本身要重查,不能只採信轉述。用 `WebFetch` 讀了 GitHub 官方文件(workflow 語法頁的 shell 段落),又另外用 `WebSearch` 交叉核對社群踩坑紀錄(`actions/runner` 專案的 issue #1955、#353,`actions/runner-images` 的 issue #4459,`github/docs` 的 issue #18933),結論一致:**沒有明寫 `shell:` 時,Linux 上的預設呼叫是 `bash -e {0}`,不含 `-o pipefail`;只有明寫 `shell: bash` 才會變成 `bash --noprofile --norc -eo pipefail {0}`**。這件事本身在社群裡被踩過很多次、也曾經是文件寫錯被回報修正的對象,不是我或協調者憑印象講的。接著核對 repo:`grep -n shell -R .github/` 在整個 `.github/` 底下零命中,`.github/workflows/ci.yml` 也沒有 `defaults:`。所以這一步目前實際跑的,就是不含 pipefail 的預設殼——我原本審查報告裡「這一步的預設殼有開 pipefail」這個前提是錯的。

**第二步:不採信協調者的殼測結果,自己重跑一次。** 拿原本(折之前)那段診斷碼,搭配我先前造的四片組合(第 2 片是「skip 基準線判紅」——只印「✗ 判紅:...」,不含 FAILED/EXCEPTION 字樣;第 3 片紅在開頭第一行;其餘綠),分別在 `bash -e`(無 pipefail,真實設定)和 `bash -eo pipefail`(我原本測的那種)各跑一次:

| 殼 | 結果 |
|---|---|
| `bash -e`(這一步實際的設定) | 四片全部印完,`!!!! 全部 4 片跑完 !!!!` 與 `exit $rc` 都有執行到,沒有中止 |
| `bash -eo pipefail`(原本報告測的那種) | 跟原本報告一樣,印完第 2 片標題後就死,第 3、4 片完全沒輸出 |

這證實了協調者說的「後果被誇大」:我原本形容的「整支腳本會被中止、後面的片全部消音」,在**這一步目前實際的設定下不會發生**;只有額外疊上 `pipefail`(例如日後有人把這步改寫成明寫 `shell: bash`)才會發生。機制本身(第二道 grep 認不得「逾時 / 零斷言 / 跳過基準線判紅」這三種紅、找不到東西就回非零)沒有錯,錯的是我把「只在 pipefail 殼下才會引爆的地雷」講成了「現在就會引爆」。

**第三步:驗折法。** 工作樹裡 `.github/workflows/ci.yml` 現在的內容(尚未 commit)是把兩道 grep 都接上 `|| true`,並把第二道的樣式擴充成 `^  ✗ (FAILED|TIMEOUT|判紅)|EXCEPTION|^  ✗ .*一條斷言都沒有`。核對過 `scripts/test_lumos.py` 全檔,所有會印出「✗ ...」的地方只有 6 處:`scripts/test_lumos.py:86`(單一斷言的明細行,格式是「✗ {name} {detail}」)以及另外 5 處「每支測試跑完印一行」的彙總/標記行——`scripts/test_lumos.py:28479`(零斷言)、`:28484`(FAILED 彙總)、`:28492`(TIMEOUT)、`:28496`(EXCEPTION)、`:28561`(跳過基準線判紅)。折法的樣式涵蓋了全部 5 個彙總/標記行;第 86 行的明細行不需要單獨認得,因為它一定緊貼著某個彙總行,前後文視窗(往前 12 行)本來就會把它帶進來。

自己另外造了三種各自單獨出現、都不含 FAILED/EXCEPTION 字樣的紀錄檔(純逾時、純零斷言、純跳過基準線判紅),搭配一片全綠,湊成新的四片組合,分別在 `bash -e` 和 `bash -eo pipefail` 兩種殼下各跑一次折過的版本:

| 殼 × 內容 | 結果 |
|---|---|
| `bash -e` + (綠、純逾時、純零斷言、純跳過判紅) | 四片全部印完,三種非典型紅都正確抓到名字與前後文,`exit $rc` 有執行到 |
| `bash -eo pipefail`(最壞情境)+ 同一組四片 | 結果相同:四片全部印完,三種非典型紅都正確抓到名字與前後文,沒有中止 |

兩種殼、四種內容組合(含最壞情境)都驗過,折法有效,沒有發現殘留的「非典型紅仍抓不到」或新引入的中止路徑。

**結論:** 協調者的訂正查證屬實,我原本報告的後果描述確實誇大了目前的真實風險——目前這一步不會因為這個問題而中止或消音。折法(`|| true` 接住 + 樣式擴充 + 註解說明兩種殼的差別)已經同時解決了「機制」(認不得三種非典型紅)和「後果」(萬一日後殼被改成帶 pipefail 也不會中止)兩層,自己重建的實驗沒有找到反例。

Sources:
- [Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsshell)
- [Fail-fast/pipefail behaviour for default shell inconsistent with documentation · Issue #1955 · actions/runner](https://github.com/actions/runner/issues/1955)
- [Default non-Windows bash is not invoked as documented · Issue #353 · actions/runner](https://github.com/actions/runner/issues/353)
- [Default `bash` shell doesn't seem to run with `-o pipefail` · Issue #4459 · actions/runner-images](https://github.com/actions/runner-images/issues/4459)
- [Incorrectly stated that -eo pipefail is applied by default for bash when shell is not specified · Issue #18933 · github/docs](https://github.com/github/docs/issues/18933)
