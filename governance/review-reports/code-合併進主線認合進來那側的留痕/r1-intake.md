# code-合併進主線認合進來那側的留痕 r1 收貨

席報告 8 份(正確性 3、邊界 3、整合 3、併發 3、回滾 4、架構對齊 3、資安 3、規格符合 2,共 24 條)。quote-check:整合、資安、規格符合各 1 句錨不到(分別引自 pre-push 掛鉤原檔、計劃正文、程式字串的近似寫法,非凍結 patch 逐字);所屬發現另有錨定席或編排者重現,照下表。資安報告總結句含等級字樣,請該席自改後收回。refcheck 全 ok。

彙整 id:正確性 c1–c3、邊界 e1–e3、整合 i1–i3、併發 n1–n3、回滾 rb1–rb4、架構對齊 a1–a3、資安 s1–s3、規格符合 sp1–sp2。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| e1 c1 n1 a2 | 邊界席:PATH 前放 git 包裝讓 `rev-parse --is-shallow-repository` 睡 23 秒再跑 check;正確性、併發席注入 TimeoutExpired | traceback / RAISED TimeoutExpired | HIT(三席) |
| e1 c1 n1 a2 | 編排者修後:`t_codeloop_merge_side_edges` ⑥ 注入 TimeoutExpired;翻紅「例外不收成判不了」 | 修後綠、翻紅紅 | HIT |
| a1 | 讀碼:`_merge_side_git` 與既有 `_lens_git`(scripts/lumos 同檔)同功能 | 重複入口 | HIT |
| i1 c2 | 編排者翻紅「不是合併也講理由」「全零起點也講理由」 | ②、②b 紅 | HIT |
| s3 | 編排者翻紅「分支名不跳脫」 | ①b 紅 | HIT |
| e2 | 邊界席實測拿掉起點條件後「主線本機多了沒推過的提交」rc0;編排者補 edges ⑦ | 修後綠 | HIT |
| c3 e3 | 正確性、邊界席實測 t_codeloop_check_merge_side_pass 109–116 秒(上限 180) | 拆成三支 | HIT |

## 處置

全折(24 條):例外一律收成判不了不認(e1 c1 n1 a2);改用 `_lens_git`(a1);每關各自期限、合併判斷與帳本共用快取、表態那關期限加回(n2 n3 rb4 a2 i2);不適用時不接原因(i1 c2);分支名 `_esc_clean`(s3);逾時措辭與判不了分開講(sp1);a3 同函式 import 寫法統一;測試補格與拆分(sp2 e2 c3 e3);筆記補不認形狀、帳本可手寫的天花板(i3 s1)、回頭條件(s2 i3);回退節補沒有單獨開關、事件形狀、混版本一次性紅燈(rb1 rb2 rb3)。
