# r2 intake(代碼審)

## 材料
- 修補鏡頭:修前 fd2bd3ec → 修後 d6c216c1(9439d9e0 只動帳本),r2-repair.patch 1125 行必讀;r2-snapshot.patch(69ac44b2..9439d9e0,1914 行)只當查詢參照,兩份合計超過 1800 行上限,所以照實寫在派工單 reading_note。
- r1-dispatch.json 的 base_commit 原誤填主線分叉點 69ac44b2,收 r1 時更正為凍結當下的 fd2bd3ec(原值改放 range_base);r2-repair-binding.json 的 before_provenance 有寫。
- r1 修正關卡:第一次因 category=other 缺 note 沒過,補 note 後重跑全部通過(r1-fixcheck.log)。

## 收貨
- 兩席:單reviewer-sonnet(5 條)、架構對齊-sonnet(6 條);兩份已是正規化格式,quote-check 對 r2-snapshot.patch 全數錨定。
- COR2-1 與 ARC2-1 兩席獨立指出同一件事(特殊字元只擋 C0)。

## 編排者重現(修前用 9439d9e0 的 scripts/lumos 與掛鉤暫換跑新測試,跑完換回並 cmp 確認)

| finding | 重現 | 修前(9439d9e0) | 修後 |
|---|---|---|---|
| COR2-1 / ARC2-1 | t_arch_target_control_chars_never_reach_prompt:U+2028 檔名讓 JSON 逐行解析失敗、tab 檔名、換行檔名 | HIT 紅(JSON 解析失敗、檔名被踢) | 綠 |
| COR2-2 | t_arch_target_lens_trusts_mainline_base_only ③:pitfalls --diff <分支提交>..<分支提交> 吃分支宣告 | HIT 紅 | 綠 |
| COR2-3 | 同 COR2-1 測試的 tab 檔名:舊 numstat 解析截成不存在的名字 | HIT 紅 | 綠 |
| COR2-4 | 同 COR2-1 測試:帶特殊字元的檔被踢出目標組 | HIT 紅(只列 1 支) | 綠(4 支、跳脫列出) |
| COR2-5 | t_arch_target_failure_not_silent ③④:舊碼本來就對(綠);變異「git-fail 靜默」「設計審例外回空」各翻紅 | 缺口 HIT | 守住 |
| ARC2-2 | 讀碼:改動檔清單改走 _review_role_changed_files,刪掉自寫 numstat 解析 | 讀碼 HIT | 已改 |
| ARC2-3 | 讀碼:抽 _lumos_config_at_ref,角色鏡頭與目標架構共用 | 讀碼 HIT | 已改 |
| ARC2-4 | 讀碼:抽 _lens_emit_with_extra,派工鏡頭與設計審外層共用 | 讀碼 HIT | 已改 |
| ARC2-5 | t_review_role_declaration_from_fork_point:角色鏡頭讀範圍起點版宣告 | HIT 紅 | 綠 |
| ARC2-6 | 讀碼:_on_ml 隨圖譜段改回原寫法消失;掛鉤變數 _role 改 _extra | 讀碼 HIT | 已改 |

另外修 COR2-1 時測試抓到同族:pitfalls --json 原樣輸出 U+2028,推送檢查逐行找 JSON 會切壞走 fail-open;改成 _json_text_escaped 無損跳脫(變異改回原樣輸出 → 翻紅)。
新增告警閘:修後第一次又帶進 RUF005、F401 兩條,清掉後 69ac44b2..70c1e034 為 clean。

## 歸因(修補因果)
- 有證據的修復回歸:COR2-4(r1 修補把特殊字元檔名踢出目標組)、ARC2-1(r1 修補新寫 _ARCH_TARGET_CTRL_RE)、ARC2-3(r1 修補在 _arch_targets_at 內嵌 cat-file)、ARC2-4(r1 修補新增 _dispatch_lens_spec_with_arch 複製合併尾段)、ARC2-6(r1 修補新增 _on_ml、_extra_text 呼叫處變數名)——以 git show 2cb3e330 核對這些行都是該提交新增。
- 有證據的原有漏查:COR2-1 的 U+2028 部分(修前修後同樣失敗)、COR2-2、COR2-3、COR2-5、ARC2-2(_arch_target_changed_files 在 fd2bd3ec 就存在)、ARC2-5(角色鏡頭既有行為)。
- 未判定:無。

## 處置
11 條全數折入,無放行、無駁回。同類問題(特殊字元、起點信任)第二輪再現,改成統一規則:共用的特殊字元類別與跳脫、共用的分叉點信任版本。
