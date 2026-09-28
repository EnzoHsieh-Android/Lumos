severity: major

# 驗收輪 通才4-opus

審材:驗收-delta.patch(第 3 輪修正差異)。四個鏡頭都看了。另外在自己複製的 scripts 裡做了 8 個變異(故意把修正改回去):新回歸 t_note_audit_code_review_r3_regressions 對 8 個全部翻紅(全零只認 40、不切行尾註解、第一層讀檔含註解、R 也算刪除、拿掉未追蹤純刪除檢查、第一層不指名、名字不認引號、截斷不講共幾個)。所以這支回歸本身是真的在守東西,沒有空轉的斷言。
全零常數擴成 40|64 位:用到它的每個地方都是 fullmatch,已逐一看過(file: `scripts/lumos:23391`、`scripts/lumos:24121`、`scripts/lumos:24420`、`scripts/lumos:29199`、`scripts/lumos:29203`、`scripts/lumos:31808`)。在 _lens_push_base 裡,起點是 64 個 0 時原本就會走「本機找不到」那條分支,現在只是換成「新分支首推」的說明,算法不變;代碼審留痕那道也是同一條路。這個改動沒有找到副作用。

## F1 decision-amend 新加的「純刪除」拒絕,在任何遠端分支跟工作目錄有差異時,都會誤擋全新筆記(違反 S12)

severity: major
blocking: 是 — S12 規定「遠端沒有該編號應准改」,現在只要有遠端參照多出一篇筆記就拒絕,而多人協作的 repo 幾乎一定是這個狀態
引句:「if toks is None or pure_del:」

判法是:對每一個遠端追蹤參照跑 `git diff --name-status -M <ref> -- <圖譜夾>`(拿那個參照的樹跟工作目錄比),只要有任何一個 D 就拒絕。問題是 D 的意思只是「這個參照上有這支檔、我的工作目錄沒有」,跟「使用者把它搬走了」是兩回事。下面這些正常情況都會出現 D:
- 同事在 origin/feat 新寫了一篇筆記,還沒合進主線;
- 主線在我開分支之後多了新筆記,我的分支還沒 rebase;
- 舊的遠端分支還留著一篇筆記,主線後來刪掉了。工具只跑 `git fetch --all`,沒加 `--prune`,所以遠端上那條分支就算已經刪了,本機的追蹤參照還是會一直留著。
- fork 工作流裡的 upstream/main。

在這些情況下,每一篇還沒 git add 的全新筆記都改不了,而遠端其實根本沒有這個決策編號。錯誤訊息講的是「如果是改名,請先 git add 新舊兩邊」,但使用者根本沒改名,會被誤導。r2 的版本在同樣情境下都放行,所以這是這一輪的修正自己引入的問題。新回歸的 ③c 只造了 origin/main 一個參照,所以測不到。

file: `scripts/lumos:24916`(先跑 `for-each-ref refs/remotes`,再對每個參照做檢查)、`scripts/lumos:24935`(拒絕的地方)

最小重現(腳本:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/acc4/repro_amend.py。它用 test_lumos 的 _na_repo、_nh_node 造出 origin/main 帶決策 d1 的 D.md,然後按下面幾種情境各跑一次 `decision-amend Systems/Fresh d1 --field context`):

```
$ python3 repro_amend.py            # 這一輪的 scripts/lumos
[A 遠端有別人分支多了一篇筆記,全新未追蹤筆記] rc=2  擋下:這篇筆記還沒加進 git,而 refs/remotes/origin/feat 上有圖譜檔在工作目錄不見了——如果是改名,請先 git add 新舊兩邊(或用 git mv),工具才認得出它在遠端的舊路徑
[A2 對照:只有 origin/main] rc=0 ✓ decision-amend Systems/Fresh.md d1.context 改好了(這條決策還沒推上去)
[B 主線已刪、舊遠端分支還留著那篇] rc=2  擋下:這篇筆記還沒加進 git,而 refs/remotes/origin/old 上有圖譜檔在工作目錄不見了——…
[C 同 A 但先 git add] rc=0
$ python3 repro_amend.py r2         # 同樣情境換成 a72a0e2e(r2)版的 lumos
[A …] rc=0 ✓ …改好了   [A2 …] rc=0   [B …] rc=0   [C …] rc=0
```

修法方向:純刪除的舊路徑只能當「候選的舊路徑」,不能一看到就拒絕。要讀 `<ref>:<被刪路徑>` 的內容(可以直接用已有的 _nodehome_cat_blobs 批次讀),只有裡面真的有 `id: <did>` 才拒絕。這才是 S12 的語意(遠端有這個編號才擋),而且 git add -u、commit -a 那兩種搬檔照樣擋得住。

順帶一提:dl 和緊接著的 ns 跑的是同一條 git 指令,每個參照都跑了兩次,可以共用一次的結果。

補一條回歸:在 ③c 之外,再造一個 origin/feat 多一篇無關筆記的情境,斷言全新筆記 rc=0。

## F2 行尾註解裡有引號時不會被切掉,註解裡寫到的「fetch-depth: 0」會被當成真的設了完整歷史

severity: minor
blocking: 否 — 只會少唸一句提醒,不擋任何東西,也不會損壞資料;要碰到得是註解裡剛好同時有引號和那串字
引句:「_CI_TRAILING_COMMENT_RE = re.compile(r"\s+#[^'\"]*$")」

規則是:` #` 後面只要出現引號,這段就不算註解。英文註解裡的撇號很常見(don't、it's),所以下面這種寫法:

```
          fetch-depth: 1  # don't: fetch-depth: 0 is slow
      - run: python3 scripts/lumos note-audit check --diff x
```

實測結果是 `_ci_jobs_calling_without_full_history → []`,也就是漏唸了。同樣的形狀如果出現在 run 那一行,例如 `- run: echo skip  # python3 scripts/lumos note-audit check (it's off)`,那一步被註解掉了,「沒呼叫」卻不會唸。這個限制 docstring 有寫(「後面沒有引號的」),但誠實界線和計劃裡都沒寫,而且這一輪的修正本來就是要讓「註解不算」這件事可靠。

file: `scripts/lumos:25001`(_CI_TRAILING_COMMENT_RE 與下面的 _ci_workflow_texts)

重現:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/acc4/yaml_battery.py 裡的 "comment apostrophe fetch" 那一案,輸出 `[]`(預期是 `[('w.yml','audit')]`)。

修法方向:掃一遍這一行,記住目前是不是在單引號或雙引號裡,只切「不在引號裡的 ` #`」。不然就是把這個限制寫進誠實界線。

其他在鏡頭 1 下試過、沒出問題的寫法(都照預期):
- `jobs: {}`
- CRLF 換行
- run: | 裡面有長得像 key 的行
- jobs 之後才出現頂層 on:
- 工作項目用 4 格縮排
- 引號裡的 ` #`

最嚴重 severity:major;blocking 共 1 條(F1)。
