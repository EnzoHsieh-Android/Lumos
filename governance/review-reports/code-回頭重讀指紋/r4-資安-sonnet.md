severity: major

本席實驗在 `/private/tmp/claude-501/.../scratchpad/cr-rf4-資安/` 下做。這個資料夾與三個實驗 repo 已刪,`reread-fp` 沒被動過。`$TMPDIR` 下另有大量 `gctl-*` 暫存(共 718 個)。我只刪確定是自己建的,其餘無法辨認歸屬,留給原會談處理。

總結:第三輪的「祖先核對」只擋得住「偽造 `origin/main` 加上用 `origin` 這個遠端名推送」這一條路。核對本身、以及指紋對 git 環境的隔離,各有一個可重現的繞過。

severity: major
blocking: 是 — 推主線時,只要改用另一個遠端名或直接用網址推,祖先核對就不跑,第三輪的偽造 ref 洞原樣重現,守檔筆記不會被重讀
引句:「target = f"refs/remotes/{remote}/{pushed_ref[len('refs/heads/'):]}"」
- 核對只在 `refs/remotes/<--push-remote>/<被推分支>` 剛好是主線候選之一時才執行。主線候選永遠取自 `_lens_default_remote`(通常是 `origin`),跟 pre-push 給的遠端名無關。
- 攻擊步驟:
  1. 把 `refs/remotes/origin/main` 指到藏了改動的提交(同第三輪)。
  2. 加一個指向同一網址的別名遠端 `git remote add o2 <同網址>`,或乾脆直接推網址。
  3. 執行 `git push o2 HEAD:main`。pre-push 收到的遠端名是 `o2`(或網址),target 變成 `refs/remotes/o2/main`。
  4. 候選裡沒有這個 ref,`hit` 為 False,函式直接 return,沒做任何核對。
- 實驗(`exp1.py`,沿用 `_rfp_repo`、`_rfp_two_branches`,偽造 origin/main 並記好紀錄):

```
origin    rc= 1  …不是遠端 refs/heads/main 現在的值…的祖先…先 git fetch origin 再推
alias o2  rc= 0  回頭重讀提醒:這次要對照的 1 篇守檔筆記都對照過這一版程式了
url       rc= 0  回頭重讀提醒:這次要對照的 1 篇守檔筆記都對照過這一版程式了
```

- 原因:核對的觸發條件綁在遠端名的字串上,沒有綁「這次推的是不是主線」。
- 佐證:`reread-fp/scripts/lumos`(`_note_reread_bp_vs_remote`,patch 內 `target = …` 與 `if not hit and not err: return` 兩行)。

severity: major
blocking: 是 — `.git/info/grafts` 能讓分岔點偽造成「藏了改動的提交」。這不用動任何遠端追蹤 ref,祖先核對也照樣通過,誠實分支的對照紀錄可套到藏了改動的分支上
引句:「os.environ["GIT_NO_REPLACE_OBJECTS"] = "1"」
- 入口只關了 `git replace`,沒關 `.git/info/grafts`。實測 git 2.39.2 在 `GIT_NO_REPLACE_OBJECTS=1` 下仍讀 grafts(只印棄用提示)。
- 攻擊步驟:
  1. 真實遠端主線是 M(origin/main 沒被偽造)。attack 分支含藏了改動的提交 evil。
  2. 寫 `.git/info/grafts`:`<M> <base> <evil>`,讓 M 看起來也是 evil 的後代。
  3. `merge-base(tip, M)` 變成 evil,分岔點上移,evil 的改動不在 `bp..tip` 的 diff 裡。
  4. 核對 `merge-base --is-ancestor evil M` 在 grafts 下也成立,所以祖先核對放行。
- 實驗(`exp3.py`:先在 honest 分支記紀錄,再複製到 attack 分支,推 main,舊值是 M):

```
no graft    rc= 1  …擋下(指紋對不上)
with graft  rc= 0  回頭重讀提醒:這次要對照的 1 篇守檔筆記都對照過這一版程式了
```

- 前一輪的 replace 修補同類,但沒清到 grafts。
- 建議:入口同時設 `GIT_GRAFT_FILE=os.devnull`,或在 `_lens_git` 一律帶 `-c core.graftFile`,並加一條紅測。
- 佐證:``file: `reread-fp/scripts/lumos:53264` ``(入口設環境變數處)。

severity: major
blocking: 是 — `GIT_DIFF_OPTS=-u0` 會蓋掉指紋指令明寫的 `-U3`。改動的前後文不再進指紋,同一個函式內搬位置的改動指紋相同
引句:「_NOTE_REREAD_DIFF_ARGS = ("--no-ext-diff", "--no-textconv", "--no-color", "--src-prefix=a/", "--dst-prefix=b/")」
- 子行程繼承呼叫者的環境。實測 git 2.39.2:`git diff -U3` 在 `GIT_DIFF_OPTS=--unified=0` 或 `-u0` 下前後文行數為 0。入口只清了 `GIT_NO_REPLACE_OBJECTS`。
- 攻擊步驟:
  1. 用 `GIT_DIFF_OPTS=-u0` 跑 prepare/record,再 `GIT_DIFF_OPTS=-u0 git push`。
  2. 同一行 `payload()` 插在 `src/a.py` 第 15 行(誠實位置)或第 5 行(可疑位置),兩者縮排鏈相同。
  3. 兩種位置的指紋相同,因此誠實位置的對照紀錄可以套到可疑位置。
- 實驗(`exp2.py`):

```
GIT_DIFF_OPTS=None  insert@15: 0156f480a4e073fe  insert@5: 758874eee8c7f202   (不同,正常)
GIT_DIFF_OPTS=-u0   insert@15: 9c141ed2db2dbf36  insert@5: 9c141ed2db2dbf36   (相同)
```

- 第一輪修的「搬到結構相同的函式指紋不變」,在環境變數下又打開了。
- 建議:入口清掉 `GIT_DIFF_OPTS`、`GIT_EXTERNAL_DIFF`、`GIT_CONFIG_COUNT` 和 `GIT_CONFIG_PARAMETERS`,或改用 `env -i` 式的乾淨環境。
- 佐證:``file: `reread-fp/scripts/lumos:36220` ``(`_NOTE_REREAD_DIFF_ARGS`)。

severity: minor
blocking: 否 — 單次跳過寫進的是工作目錄裡被追蹤的帳檔,沒有隨這次推送一起送出,事後還能用 git 還原掉,所以「跳過會留帳」只防得住不小心,防不了刻意繞過
引句:「_gate_event_or_warn(root, "note-reread", "skipped-env", "LUMOS_SKIP_REREAD_CHECK")」
- 實驗:在 clone 的 repo 設 `LUMOS_SKIP_REREAD_CHECK=1`,跑 `reread-check --gate` 後 rc=0,`docs/.governance-log.jsonl` 多一行 `skipped-env`,`git status` 顯示 `M docs/.governance-log.jsonl`(未提交)。
- 這次推送的提交裡不含這筆帳,`git checkout docs/.governance-log.jsonl` 就能清掉。
- 本輪修補把「逾時照擋」的退路定為單次跳過,並說明跳過會留帳,這個前提只在「帳之後被提交」時成立。
- 這在單人、AI 依序操作的威脅模型下接近設計取捨,所以只列 minor。
- 佐證:``file: `reread-fp/scripts/lumos:37574` ``。

沒找到能繞過的部分(已讀程式推演,沒有實驗證實):
- **非 ASCII 但像標點的行**:全形標點等被當成有字的行,只會讓縮排鏈多一個節點或多截斷一次,方向偏保守。這種行必須出現在自己的 diff 裡才有用,指紋會跟著變,所以不構成繞過。
- **純標點行造成相同的鏈**:標點行本來就是同樣的文字,跳過它不會讓本來不同的鏈變成相同。縮排深度仍留在新增行本身的前導空白裡,所以沒有新增繞過路徑。
- **`GIT_NO_REPLACE_OBJECTS`**:入口在 `main()` 設定,子行程繼承,replace 這條實測未被繞過。
- **其他 git 環境**:`diff.external`、`textconv` 和屬性檔路徑,指令都已固定。

最高等級 major,blocking 3 條。
