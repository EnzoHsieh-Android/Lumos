severity: major

我在隔離目錄裡造了小型 repo,直接呼叫 `_note_reread_fp_diff` 量測,做完已刪除實驗目錄。

## Finding 1:整批 diff 把「太大」的單側檔也一起 diff,32 MB 守衛失效

severity: major
blocking: 是 — 數支約 40 MB 的新增文字檔就能讓 check 的逐檔 diff 吃掉 30 秒預算,使其他筆記全退回 v1 並被擋推。
引句:「base["diff_order"] = list(dict.fromkeys(e["path"] for rel in scan["cands"]」

問題:`diff_order` 收進候選 about_code 列到的所有非 `T` 檔,包含之後會被判「太大」、永遠不會呼叫 `_note_reread_fp_diff` 的檔。批次只用物件大小合計 64 MB 當上限。單側檔(新增或刪除)的 cost 只算一側,40 MB 的檔剛好塞得進去。modified 的雙側檔 cost 約 70 MB 會被擋掉。所以 `_note_reread_fp_file` 先查大小再退回 v1 的順序,在批次這層被繞過。這些檔被白白 diff 一遍,而且結果不會被用到。修補前它們是「太大」直接退回,不會碰 git diff。

失敗情境(實測):
- 設定:8 組「小檔、40 MB 新增文字檔(2000 萬行)、小檔」。每個 40 MB 檔都超過 `_NOTE_REREAD_FP_MAX`,不會被要求 diff。
- 結果:`_note_reread_fp_diff` 跑 4 次整批 git diff,各約 3.6 秒、輸出約 60 MB,合計 15.7 秒,Python 行程 RSS 約 237 MB。
- 預算:小檔本身只要毫秒。每個單次 git 有 20 秒上限,整體指紋預算約 27 秒。再多 4、5 個這種檔就逾時,所有筆記退回 v1 並記「逾時」,這些筆記照舊被擋。
- 修法方向:建 `diff_order` 與 `diff_cost` 時,用 `sizes` 排除任一側超過 `_NOTE_REREAD_FP_MAX` 的檔,並排除 `sizes` 缺漏的檔。

佐證:
- file: `scripts/lumos:36556`(`_note_reread_fp_diff`)
- file: `scripts/lumos:36533`(大小守衛只在「單支被要求」時才套)

## Finding 2:要求順序與 `diff_order` 不一致時,批次會重算,最壞變二次方

severity: minor
blocking: 否 — 要靠「某篇筆記提早退回、另一篇稍後才引用被跳過的檔」才會觸發,單人單機少見。批次大小有上限,不會失控,最壞是變慢。
引句:「if got is None or path not in got[1]:」

問題:只留最後一批,而 `diff_order` 以各檔首次被提到的位置排序。某篇筆記遇到「太大」或 diff 失敗就 `return None, why`,不再走完它剩下的檔,那些檔留在順序裡。之後另一篇筆記才引用其中一支時,它不在目前這批,就從它起重新收一批,連已快取的後面檔案也重新 diff。
- 人造的最壞形狀:3000 個長路徑檔反向要求,超過 2 分鐘沒跑完(我中止了)。
- 順向要求:3000 檔、689 條路徑一批、共 5 次 git、0.8 秒,批次本身沒問題。
- 這個反向形狀正常不會出現。真實路徑下只是多幾次整批重算。

## 已讀,無 finding

- **命令列長度**:路徑參數上限 100 KB,低於 macOS 約 1 MB 的 ARG_MAX(含環境變數)。
  - 單條路徑 4096 位元組最多,所以「至少一支」不會超限。
  - `--literal-pathspecs` 已在全域選項裡。
  - 若真的撞到 `OSError`,`_lens_git` 會回 None,被記成「逾時」或「git 失敗」,不會崩。
- **檔名切分**:480 支檔名帶雙引號、tab、換行、反斜線、空白、中文、前導空白,一次批次(1 次 git)全部切對,沒有觸發單支再問。
  - 單支再問的退路只對切不出來的那幾支多花一次 git,不會變成逐檔慢路。
  - 退路只在 `len(batch) > 1` 時啟動。
- **逾時收子行程**:`subprocess.run(timeout=)` 會殺掉 git。
- **記憶體**:一批原始輸出加切片解碼,量級是批次上限的數倍,有界。
- **縮排鏈分塊**:邏輯上每塊約 1 MB,手上只留一塊,跟作者「峰值 910 到 160 MB」的方向一致。
  - 我沒有量到 910/160 這組數字,也沒有重現 600 檔 30 篇的 16.6 到 3.1 秒。
  - 3000 檔的批次化效果與其方向一致。
- **`_note_reread_own_fps` 改用整體截止時間**:邏輯合理,無併發或資源問題。

最高等級 major,blocking 1 條。
