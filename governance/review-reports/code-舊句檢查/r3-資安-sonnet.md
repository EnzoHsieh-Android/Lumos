severity: minor

## F1 超長行不管有沒有提到消失的名稱,一律讓 block 擋下,而且表態不掉
severity: minor
blocking: 否
引句:「return bool(handle) or res["state"] in _DRIFT_M1_UNKNOWN or bool(res.get("long_lines"))」
佐證行:file: `scripts/lumos:28629`(_DRIFT_M1_LINE_MAX = 20000;超過就 continue 略過,只計數)
1. 重現(在 r3 凍結後的 repo 上,用 test_lumos 的 _nh_repo/_m1_note/_m1_run 組):設定 old_sentence=block;筆記 Systems/Data.md 放一行 `"| a | b |" * 3000`(超過 20000 字、跟程式無關的資料表);另一篇筆記沒提到任何舊名稱;推送只把 src/a.py 的 `def old_func_x` 刪掉。
2. 實際輸出:rc 1,「擋下:舊句檢查:這次消失 1 個名稱;有 1 行太長沒看(超過 20000 字),看得到的行沒有提到」,並印「判不了…LUMOS_SKIP_DRIFT_CHECK=1 git push」。
3. 壞在哪:超長行只要存在於任一篇會被掃的筆記,就把所有「有名稱消失」的推送在 block 模式擋住;該行實際上可以連 `name in line` 都沒命中(這裡就沒有),卻沒辦法用 `drift ack` 表態放行(沒有發現可綁),只剩把那行拆短或 LUMOS_SKIP_DRIFT_CHECK(會留帳)。同 repo 的任何協作者提交一行 20001 字的筆記,就讓已設 block 的其他人每次改名都被卡到有人拆行。預設是 warn,所以只影響自己把 old_sentence 設成 block 的專案;有出口(拆行、單次略過),不是永久鎖死,所以只列 minor。
4. 反向(拿超長行讓 block 放行):不成立,超長行現在算判不了,已驗 rc 1。

## F2 「剖不動 / 用文字比對」那一行的程式檔路徑沒過方向控制字元跳脫
severity: minor
blocking: 否
引句:「支用文字比對:" + "、".join(_drift_m1_show(x, 200) for x in (u + t)[:3])」
佐證行:file: `scripts/lumos:28711`(_drift_m1_show 只走 _esc_clean,不換 Cf 字元)
1. 這輪修正只把 `_drift_m1_show_row`(筆記路徑、原文、說明)接上 `_drift_c4_show_name`,「只修了報上來的那個輸入」:同一份輸出裡 `_drift_m1_print_extra` 印的 res["unparsable"]/res["text_defs"] 是被推送的程式檔路徑(推送者可控),仍走 `_drift_m1_show`,方向覆寫字元原樣進終端。
2. 重現:`m._drift_m1_print_extra({"unparsable":["src/‮yp.py"],"text_defs":[],"too_long":0,"bad_notes":0,"other_files":0})`,輸出的位元組含 E2 80 AE(RLO);`ascii(m._drift_m1_show("src/‮yp.py"))` 得 `'src/‮yp.py'`,沒有被換成可見寫法。帳的 text_defs_paths、rows.path 同樣是 _drift_m1_show,RLO 直接寫進治理帳。
3. 影響:只是終端顯示順序偽裝(那一行沒有可照貼的指令),不會造成執行;另 `_drift_c4_show_name` 只換 Cf,U+2028/U+2029(Zl/Zp)不換,`_esc_clean` 也不管它們,實測兩者對 "a b" 都原樣通過;終端多半不當換行,故不另立。

## 已試過、不成立(給收貨端省重跑)
- `_mkdir_private_layer` 的 chmod 導去別的目錄:`cur.mkdir(mode=0o700)` 成功才走到 `_chmod_no_follow`,後者 O_NOFOLLOW|O_DIRECTORY 開最後一層再 fchmod,連結會 ELOOP 回 False;各上層在前一輪迭代已驗過不是連結、是自己的、group/other 不可寫。同群組/其他使用者要動手得先能寫上層,而上層可寫就被判不信。剩下同 UID 搶跑,屬原註解已承認的誠實邊界。
- 假快取:group_ok 撤回後,目錄必須自己擁有且 0700,別的使用者放不進檔;快取鍵含 blob 內容編號,`_lens_cache_read` 再驗擁有者與 group/other 不可寫。FIFO 卡讀取:同樣需要能寫進 0700 自己的目錄,不可行。
- ledger-miss.jsonl 的 FIFO:O_WRONLY|O_NONBLOCK 開無讀端 FIFO 得 ENXIO 走 OSError 回 False;有讀端則 S_ISREG 擋下。目錄本身別人放不進。
- 超長行判不了讓推送卡死時間:單行最壞實測 20000 字、約 1800 個名稱命中 0.03 秒,900 個路徑名稱 0.42 秒;每行前 check_time,超時上限至多多一行。
- 不印指令的條件:`_drift_c4_show_name(path) != path` 對非 UTF-8(替身字元)與 Cf 都成立;名稱端已由 `_drift_m1_name_canon` 擋 Cc/Cf/Cs/Zl/Zp,`--name=` 過 `_drift_sh`,無法夾帶。

## 圖譜鏡頭逐條判定
- lumos-cli-read(search 預設排除 superseded 的 INVARIANT):本 diff 不碰 search,不影響。
- bound-tests-gate(code-loop check 逐支真跑綁定測試):不動 code-loop check;只新增/改測試函式,不影響。
- guard-kill(rc 優先序與 --json 純度):不動 guard kill,不影響。
- 授權與歸屬(授權檔不得進 _VENDORED_TOOLKIT;主程式 SPDX 檔頭):diff 沒動白名單與檔頭,不影響。
- 測試假綠形態(還原翻紅釘要有前置斷言):新測試 t_drift_m1_review_r2_* 的翻紅釘各自帶前置斷言(如「那一行真的超過上限」),不影響。
- lumos-cli-lifecycle(re-inject 保留 sentinel 外內容)、design-loop(處置閘第五步)、pitfalls-code-loop:不動對應路徑,不影響。
- 只列名者(deinit、slim-*、guard 類等):diff 只改共用 `_mkdir_private_layer`,新建層改 0700 對這些節點的行為只有「umask 寬鬆時不再建出 group 可寫層」,不破壞其合約。

最高等級:minor
