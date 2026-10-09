# r3 intake(代碼審)

## 材料
- 修補鏡頭:修前 9439d9e0 → 修後 9d6940ad(f3566193 只動帳本),r3-repair.patch 943 行必讀;r3-snapshot.patch(69ac44b2..9d6940ad,2012 行)只當查詢參照。
- r2 修正關卡:第一次因 prior 兩欄放在組的第一層沒過,改放 prior 物件後重跑全部通過(r2-fixcheck.log)。派席前重跑合約殺傷力配方 Systems/canary-audit 1ce7a8da1307:killed。

## 收貨
- 兩席:單reviewer-sonnet(3 條)、架構對齊-sonnet(4 條);已是正規化格式,quote-check 對 r3-snapshot.patch 全數錨定。
- COR3-2 與 ARC3-3 兩席獨立指出同一件事(分叉點算不出來時靜默)。

## 編排者重現(先寫紅測試,修前紅、修後綠;另做變異,全部翻紅後還原並 cmp 確認)

| finding | 重現 | 修前(9d6940ad) | 修後 |
|---|---|---|---|
| COR3-1 | t_arch_target_no_mainline_or_fork_not_silent ①:本機只有 trunk,範圍 <分支提交>..<分支提交> 附出分支寫的規則 | HIT 紅 | 綠;變異「沒主線照讀起點」翻紅 |
| COR3-2 / ARC3-3 | 同測試 ②③:孤兒分支分級沒說明;merge-base 失敗時派工鏡頭回空、角色鏡頭沒警告 | HIT 紅 | 綠;變異兩處各翻紅 |
| COR3-3 | t_pitfalls_diff_line_separator_cannot_hide_risk:內容帶 U+2028 的 open( 漏掃(tier standard)、帶 U+2028 的檔名被切斷 | HIT 紅 | 綠;變異改回 splitlines 翻紅 |
| ARC3-1 | 讀碼:_lens_trusted_ref 與 _range_base、_push_range_start 語意不同(後兩者回答範圍從哪裡比、失敗讓上層擋),在 docstring 寫明為什麼不併 | 讀碼 HIT | 已寫明 |
| ARC3-2 | 讀碼:狀態字串 git-fail 改 git-failed | 讀碼 HIT | 已改 |
| ARC3-4 | t_arch_target_control_chars_never_reach_prompt:目標組在 pitfalls JSON 被 _kill_esc 先改寫 | HIT 紅 | 綠;變異「再跳脫一次」翻紅;派工鏡頭附加段 JSON 也改 _json_text_escaped |

## 歸因(修補因果)
- 有證據的修復回歸:COR3-1(r2 修補把「沒有主線」退回讀起點)、COR3-2/ARC3-3(r2 修補的 _lens_trusted_ref 回 None 時四處靜默)、ARC3-1、ARC3-2、ARC3-4(都是 r2 修補新寫的程式)。以 git show 8d0a7fdd 核對這些行是該提交新增。
- 有證據的原有漏查:COR3-3(9439d9e0 與 9d6940ad 結果相同)。
- 未判定:無。

## 處置
7 條全數折入,無放行、無駁回。這是 standard 上限的第 3 輪,修補差異還要全新席位看,另記人裁 extra-round 與跑滿回顧。
