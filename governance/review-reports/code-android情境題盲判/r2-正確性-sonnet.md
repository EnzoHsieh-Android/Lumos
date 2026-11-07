severity: minor

第一輪正確性席與架構對齊席的問題都真的修好了,修補本身沒有引出會做出錯誤行為的新洞。我只找到兩個 minor。這份只改了兩條引句的格式,內容、條數、severity、blocking 與總結都沒動。

我在臨時複本(`HEAD ffb47f857`)上跑了 `python3.14 scripts/test_lumos.py -k blind`,109 個通過、0 個失敗。另外用 `importlib` 載入 `scripts/lumos`,餵造出來的治理帳與推送核對輸入做了四個探針。

## 第一輪問題核對

- **正確性 F1(標記檔蓋掉治理帳):已修好。**
  - 探針:帳裡是 first 判不照做、arbiter 判不適用,`_kt_bj_read` 只從帳折出,兩票都讀到。
  - `scripts/lumos` 裡已沒有任何程式讀 `blind-judge.json`,`_kt_bj_marker_path` 與 `_kt_bj_range` 都不在了。
  - 磁碟上留著舊標記檔也不影響。舊事件寫入時用的 `_kt_bj_validate` 跟新的 `_kt_bj_vote_ok` 標準一致,舊帳不會被新驗票誤殺。
- **正確性 F2(壞票炸成放行):已修好。**
  - 形狀不對的事件整筆跳過,讀不到就當缺盲判,走的是「擋」,不是放行。
  - 讀檔失敗(OSError)得到空帳,同樣是擋。
  - 在 `_kt_bj_read` 的原始帳輸入上,先放一行 10 萬層巢狀,再放一筆好事件:巢狀行被跳過,好事件照讀。
  - 3460 萬位元組、20 萬行 `pending: blind-judge` 的帳讀完約 0.4 秒。
- **正確性 F3(`a/b` 與 `a__b` 撞檔):已修好。** 讀取已改成從帳依精確的 `branch` 欄位比對。
- **正確性 F4(三方各異):已修好。** `_kt_bj_arbitrate` 的組合我都跑過:
  - 作者適用且照做、第一盲判適用但沒照做、仲裁不適用,得到 no-majority。
  - 仲裁同作者,得到 arbiter_author。
  - 兩位盲判一致判照做或不適用,得到 blind_agree。
- **正確性 F5(全重複也 rc0):已修好。** 整份都是已有的格時回 rc2,不寫帳。
- **架構對齊 F1(範圍計算兩套):已修好。** `_codeloop_disp_range` 抽出後,推送前核對的行為與原內嵌版逐分支相同:
  - 推主線或 merge-base 算不出來,原樣用 `diff_range`。
  - merge-base 等於版本本身,走 tip-on-mainline 的空段分支。
  - merge-base 與 `diff_range` 相同時不重算。
  - 首推新分支的路徑沒變。
  - `_ml`、`_mlname` 被刪掉後,函式後面沒有殘留引用。
- **架構對齊 F2(合併提交的分支解析):已修好。** `_disp_record_for` 標記 `_merge_side` 後,盲判與表態用同一個分支名、同一側的帳。
  - 讀不到那一側的帳時給空帳,照擋,不會退回讀工作目錄的帳。
  - 實際寫入的表態事件都有 `branch`:本 repo 帳裡 295 筆 dispositions 全部帶 branch,所以「合併側紀錄沒有分支名就略過盲判核對」目前打不到。
- **架構對齊 F3–F6:** 沒有發現新問題,`dt_table` 帶出出處、`_GOV_FIELD_TYPES` 新增欄位、鍵的編解碼共用都對得上。

## 新發現

### F1 gov --stats 的「仲裁採盲判」把三方各異也算進去
引句:「for rid, c in sorted(mj.items()):」
file: `scripts/lumos:17184`(沒改到的舊行 `仲裁採作者 … 採盲判 {sum(1 for k, av in dis if arb[k] != av)}`)
severity: minor
blocking: 否

- **輸入:** 作者適用且照做,第一盲判適用但沒照做,仲裁不適用。這組在 `_kt_bj_check` 已經是 no-majority。
- **實際:** 我用 `_render_gov_situation` 實跑,同一份輸出裡同時印出「仲裁採作者 0、採盲判 1」與「沒有多數 1」。
- **預期:** 這格仲裁不同於作者,也不同於第一盲判,不該算「採盲判」。
- **原因:** 修補只改了多數決提醒的計數,沒改這行。它仍用 `arb[k] != av` 當採盲判,應改成 `arb[k] == first[k]`。
- **補充:** 引句是 patch 裡新增的多數決計數迴圈,正好在採盲判那行舊程式之後。有問題的採盲判行本身在 patch 外,以 file 行號佐證。
- **影響:** 只影響統計數字,不影響擋不擋。但這份統計是升擋前人抽樣的依據,會讓「仲裁傾向採盲判」被高估。

### F2 `--part 0` 現在悄悄變成第 1 份
引句:「arbiter=arbiter, part=bj.get("part") or 1)」
severity: minor
blocking: 否

- **輸入:** `lumos code-loop blind-judge --template --part 0`。
- **實際:** `0 or 1` 變成 1,印出第 1 份材料,rc 為 0。
- **預期:** 照原本 `_cmd_codeloop_bj_template` 的 `not 1 <= part <= parts` 回 rc2 並說超出份數。
- **原因:** argparse 預設就是 1(`scripts/lumos:76058`),`or 1` 是多餘的,而且擋掉了 0 的錯誤輸入。

總結:最嚴重是 minor(統計與參數驗證各一處),會擋 0 條。
