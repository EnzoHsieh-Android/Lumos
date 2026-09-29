severity: minor

## F1 超過大小上限的 package.json 被當成「沒有」,往上找父層改判
severity: minor
blocking: 否
引句:「            blobs = {k: (v.decode("utf-8", "replace") if v is not None else None) for k, v in zip(want, got)}」
file: `scripts/lumos:20669`(呼叫 capped)、`scripts/lumos:20508`(_node_flavor_at 遇 None 往上找)
場景:git 版路徑上,最近那份 package.json 超過 512KB 時,_nodehome_cat_blobs_capped 回 None,和「這個版本沒有這支檔」無法區分,_node_flavor_at 會往父層找、改用根層 package.json 判角色。這跟 b2 修掉的是同一類(在但讀不了,卻被當成沒有、改判父層),只是 git 版這邊沒套用「回空字串=判不出」。不是本輪新引入(舊的 ls-tree 過濾同樣行為),而且 512KB 的 package.json 很罕見,所以只標 minor。要對齊 b2 的話,超上限的物件在 blobs 裡放 "" 而不是 None。未實跑重現(推論自程式)。

## F2 兩趟批次讀取各拿完整 timeout,總耗時可到預算兩倍
severity: minor
blocking: 否
引句:「    got = _nodehome_cat_blobs(repo_root, [specs[i] for i in ok], timeout=timeout) if ok else []」
file: `scripts/lumos:23338-23340`
場景:_review_roles 把剩餘預算 left 當 timeout 傳進來,第一趟 --batch-check 和第二趟 --batch 各自都拿滿 left。git 在慢磁碟或大 repo 上兩趟都逼近上限時,角色計算實際可用到 2×left(預設預算 3 秒 → 最多約 6 秒),超出 _role_budget 宣稱的上限,再擠壓後面圖譜段的期限。只在 git 異常慢時才發生,所以是 minor。

## 其他被追過、判不成問題的點
- _nodehome_cat_sizes 索引對位:--batch-check 每個輸入行恰好回一行(找到:「sha type size」;找不到或有歧義:「spec missing/ambiguous」,只有 2 欄所以是 None)。路徑含空白不影響,因為找到時輸出不回顯 spec。含換行的路徑會讓對位錯開,但 _review_role_wanted 已用 "\n" in p 濾掉(`scripts/lumos:20700` 一帶),package.json 候選也由那個 p 衍生,所以實際不會發生。樹或子模組在第二趟由 _nodehome_cat_blobs 依非 blob 一律回 None,對得上。
- 第二趟 git 失敗:_nodehome_cat_blobs 回 None,capped 回 None,呼叫端設 timed_out,沒有對位問題。ok 為空時直接回全 None。
- _NODE_FLAVOR_CACHE:grep 只有 _node_pkg_text 一處讀寫,沒有別的呼叫者把它當 flavor 用。
- _json_at_ref 呼叫者只有 3 處(`scripts/lumos:17258` vendored manifest、`scripts/lumos:20659`、`scripts/lumos:30916-30917`)。_lens_git 用 text=True,r.stdout 是 str,lstrip("﻿") 不會 TypeError。BOM 容許與 RecursionError 都只讓「原本被當壞而放棄」的情況變成正常處理或維持放棄,不會讓 manifest 或 cochange 誤信。
- 期限:_t0 在 _dispatch_lens_role_text 呼叫之前取,扣期限時點不變,抽出後仍正確。

## r2 修正驗收
- b1(_json_at_ref 容許 BOM):已修好。str 上 lstrip 正確,三個呼叫者行為只往「更寬容」走,無誤信風險;新測試走真路徑。
- b2(_node_pkg_text 讀不了回空字串):已修好(工作樹側)。空字串走 json.loads 失敗 → None,不往上找;errors="replace" 讓 UTF-16 解析失敗而判不出。git 側「超上限」仍是同類缺口,見 F1(非本輪新增)。
- b3(RecursionError 與空測):已修好。_json_at_ref 已接 RecursionError,舊空測拿掉,新測試走真路徑。
- b4(大小上限放批次讀取層):已修好、無帶進對位錯誤;附帶兩趟各拿完整 timeout,見 F2。
- b5(重叫前記除錯):已修好。_debug 在重新組 argv 之後、重叫之前。
- b6(兩處寬接印例外類別):已修好。_dispatch_lens_role_text 抽出後仍寬接並印類別名,輸出到 stderr,不污染 stdout 的 JSON。
- b7(註解改寫):已修好。

總結:最嚴重 minor;blocking 0 條
