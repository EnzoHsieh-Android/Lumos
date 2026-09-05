# r3 delta 回歸(末輪,只看第 2 輪修法的 delta)

## 0. 前置警示:patch 已經跟 live 檔案脫鉤(必須先講,否則以下判讀會失真)

`git hash-object` 比對:live `scripts/hooks/pre-commit`/`post-commit` 的 blob hash 跟這份 `r3-snapshot.patch` 標的 post-image hash(`fa141e6`/`5f8e3c2`)對不上——live 檔已經把手動四段 `${path//.../…}` replace 換成 `printf '%b' "$path"`,且 `scripts/test_lumos.py` 已多一條 `r2f` 測試,注解直接寫「r3 外家」。也就是說:這份 patch 描述的狀態,在我動筆前已經被別的動作(疑似同一輪的另一位外家 finder)發現問題並且修掉了。

以下所有驗收,都是針對 **`r3-snapshot.patch` 這份 snapshot 本身**(用 `git cat-file -p fa141e6`/`5f8e3c2` 重建出跟 patch index hash 完全一致的檔案,在乾淨臨時 repo 裡實跑),不代表目前 repo HEAD 的即時狀態。

---

## (a) 修復驗收(在重建出的 patch 內容上實跑 `bash scripts/hooks/pre-commit`)

1. `bin/weird"tool`(dash shebang,git 印成 `"bin/weird\"tool"`)→ **擋**(rc=1,訊息列出該檔)。
2. `..foo`(sh shebang)→ **擋**(rc=1)。
3. `Makefile`+`NOTES` 純文字 → **放行**(rc=0)。
   同時用重建檔跑了 `python3 scripts/test_lumos.py -k t_precommit_shebang_script_counts_as_code`,7 個 check 全綠,與手動實跑結果一致。
severity: clean

## (b) 解引號順序 + substring 邊界

- 用 python 直接建檔案讓 git 產生真實 C 引號輸出:`a\"b`(反斜線緊接引號,4 raw bytes)git 印成 `"a\\\"b"`;`a\\b`(兩個反斜線)git 印成 `"a\\\\b"`。實際餵進 hook 的解碼邏輯,兩者都正確還原成原始檔名,`git show ":$path"` 都找得到。
- 對 `\`、`"`、`a`、`b`、tab 五種字元做窮舉(長度 1–4 全組合)+ 200 組隨機(長度到 8),共 864 個真實 git 產生的 staged 項目,逐一解碼再 `git show` 驗證:**0 個失敗**。手算也驗證了 `\"`→`"` 與 `\\`→`\` 兩步交換順序,對這幾類字元組合仍會算出相同結果(兩種 escape 在退位邊界上剛好互不干擾)。**順序沒有找到 bug。**
severity: clean
引句:「path="${path//\\\"/\"}"; path="${path//\\\\/\\}"; path="${path//\\t/$'\t'}"」
file: `scripts/hooks/pre-commit:127`

- `${path:1:${#path}-2}` 在 `path` 為 2 字元 `""`(空檔名)時安全(算出 length=0 的合法 substring)。真正會炸的是 `path` 只有 1 個字元(裸的 `"`,無收尾引號)—— `${#path}-2=-1`,GNU bash 5 與 macOS 內建 bash 3.2 都會噴 `substring expression < 0`,因為 hook 有 `set -u`(第一行 `set -u`,見兩檔 line 18),接下來對 `result`/`path` 的引用會是「unbound variable」再噴一次。**但實測用真實 git 輸出無法產生短於 4 字元的 C 引號路徑**(要觸發引號,內容至少要有一個需要跳脫的字元,最短跳脫是 2 字元,加兩端引號 = 4),所以這個邊界在真實 `git diff --cached --name-only` 輸出上打不到。把裸 `"` 直接餵進函式(合成輸入,非 git 產生)實測:噴一行 bash 錯誤到 stderr,但函式吞下去回傳「非 shebang code」,**不會讓整支 hook 中止**(exit code 正常往下走)。
severity: minor(理論邊界,無法用真實 git 輸出重現,且 fail-open 不炸整支腳本)
blocking: 否
引句:「path="${path:1:${#path}-2}"」
file: `scripts/hooks/pre-commit:127`

## (c) tab / 換行

- 含 tab 的檔名(git 印成 `"bin/tab\tfile"`)→ hook 正確解碼、`git show` 找得到、**擋**(實跑驗證)。
- 含「真實換行位元組」的檔名(git 印成 `"bin/nl\nfile"`,是文字上的反斜線+n,不是真的換行字元,所以不影響 STAGED 逐行讀)→ hook 目前**沒有** `\n` 的解碼規則(只有 `\"`、`\\`、`\t` 三種),解碼後路徑仍帶著字面上的 `\n` 兩個字元,`git show` 找不到對應 blob → **不擋**(實跑驗證 rc=0,乾淨 staged 只有這一個檔時完全放行)。
- 這跟 (d) 下面那條控制字元/八進位的洞是**同一個根因**:解碼器只列舉了 3 種 escape,C-quote 實際的字元集合(`\a \b \f \n \r \t \v \\ \"` + 任意 byte 的 `\NNN` 八進位)遠不只這些。用真實 0x01 控制字元建檔(git 印成 `"bin/weird\001tool"`)實測同樣**不擋**(rc=0)。
- 這條注解本身寫的是「git 對含 `"` `\` 或**控制字元**的檔名會印成 C 式引號…先解引號」——但實作只接住了雙引號、反斜線、tab 三種,沒接住「控制字元」這個注解自己承諾的範圍,是前輪修復沒修完整,不是全新回歸。`governance/review-reports/code-readme-five/r3-外家finder.md` 獨立測到同一個洞(八進位 `\001` 案例),兩邊互證。
severity: major
blocking: 是
引句:「或控制字元的檔名會印成 C 式引號」
file: `scripts/hooks/pre-commit:125`(注解)、`scripts/hooks/pre-commit:127`(實作只解 3 種)
最小重現:`{"bin/weird\x01tool": "#!/bin/sh\necho\n"}` staged 後跑 `bash scripts/hooks/pre-commit`,rc=0(應該要擋卻放行)。

## (d) `${base%%[!.]*}` 邊界 + bash 3.2 相容性

- `base="..."`(全是點)與 `base=""`(空字串):兩種邊界在 GNU bash 5.3 與 macOS 內建 `/bin/bash`(3.2.57)上結果一致,都算出 `stripped=""`,不誤判為「有副檔名」,**不炸**。
- 額外測了 `..foo`→`foo`(通過)、`.pythonrc`→`pythonrc`(通過)、`notes.txt`→`notes.txt`(判有副檔名,return 1)、`a.b.c`、`...x.y` 等組合,bash 3.2 與 bash 5 結果全部一致。
- `bash -n` 對兩支 hook 全檔用 `/bin/bash`(3.2)語法檢查都過;用 `/bin/bash scripts/hooks/pre-commit` 真跑 `bin/weird"tool` 案例,結果與 GNU bash 5 一致(擋下)。巢狀 `${base#"${base%%[!.]*}"}"` 在 bash 3.2 上沒問題。
severity: clean

## (e) pre-commit / post-commit 兩份函式是否逐字一致

用 `git cat-file -p` 重建出跟 patch index hash 完全比對得上的兩個檔案,`awk` 抓出 `is_shebang_code()` 整個函式體後 `diff -u`:**只有兩處差異**——① 注解「staged 內容」vs「剛 commit 的 內容」;② `git show ":$path"` vs `git show "HEAD:$path"`。其餘(含新加的解引號區塊、`base` 去點判斷、shebang 比對)逐字相同。
severity: clean
引句:「base="${path##*/}"; base="${base#"${base%%[!.]*}"}"; [[ "$base" == *.* ]] && return 1」
file: `scripts/hooks/pre-commit:129`、`scripts/hooks/post-commit:54`

## impact-hook.py / 測試新增(③④)

- `impact-hook.py` 的 diff 只刪掉兩個空行(`_is_excluded_path` 與 `_shebang_is_code` 之間),純排版,無行為變化。severity: clean
- `scripts/test_lumos.py` 新增的 `r2d`(雙引號檔名)、`r2e`(`..foo`)兩案,對重建出的 patch 內容實跑 `python3 scripts/test_lumos.py -k t_precommit_shebang_script_counts_as_code`,7 個 check(含這兩個新案)全綠。severity: clean

---

## 總結

- 三個修復點裡,①(C 引號解碼)只做對了「雙引號/反斜線/tab」這三種,沒做到注解自己講的「控制字元」全集,是**帶著已知殘留的修復**——這輪測得到的最小重現(控制字元 `\x01`)會讓程式碼變更靜默繞過圖譜同步閘,判 major/blocking。②(去點判斷)在兩種 bash 版本、多種邊界值下都乾淨。③(測試/impact-hook.py 清理)乾淨。
- ⚠ 需要提醒使用者的流程訊息:這份 r3-snapshot.patch 描述的狀態已經被 live 檔案的後續修改(`printf '%b'`)超前——如果 live 檔案已經把 major 那個洞堵上,這份報告的 major finding 可能已經是「歷史帳」,建議下一步先確認 live HEAD 對這條的實際狀態,而不是直接拿這份報告去擋 merge。

max severity: major
