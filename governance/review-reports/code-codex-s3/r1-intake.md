preflight-4: ran

# r1 收貨紀錄(code-codex-s3,standard)

## 前掃
- 代碼迴圈無四類前掃;patch 只含 recount.py/README、scenario_probe.py、測試。

## 外家否決(Codex)5 條(3 major 2 minor;引句 5/5、行號 6/6)
- #1 錨定「先往後」非最近距離 HIT:折入 兩方向各取最近一個 apply_patch、比距離;紅測 s3-r1①。
- #2 無 apply_patch 硬錨任意 exec HIT:折入 anchored False;紅測 s3-r1②。
- #3 runner 不看退出碼/超時 HIT:折入 instrument_fail → passed False「儀器例外」;紅測 s3-r1③ 兩例。
- #4 endswith("lumos") 太鬆 HIT(minor):折入 basename == "lumos";紅測 s3-r1④(notlumos)。
- #5 README 把 developer 訊息寫成 hook 專屬 HIT(minor):改寫「實測落點,非唯一來源,辨識靠首行標頭」。
## 架構對齊 5 條(1 major 4 minor)+1 ⚠
- major Codex 解析核心在 recount.py 重抄 HIT:折入 `_load_hook_helpers` 改回模組,版本表/三個正規式/`_js_unescape` 全借自 check-graph-sync(單源)。
- minor:`_cx_*`→借來的 `_CODEX_*`/`_js_unescape`/`_codex_text`;空行計數與 scan_file 一致;版本不在表印 stderr 一行(同 hook)、docstring 不再承諾第三個回傳值;run_one 回傳加 `harness: claude`。⚠ stdin=DEVNULL=刻意(codex exec 無 tty 會等 stdin,2026-08-23 實測),補註解。
## 單reviewer 5 條(4 major 1 minor,全 blocking:否——席自判量測工具不進閘;引句 5/5、行號 11 對/2 缺)
- F1 同輪兩次注入共用錨 HIT:折入 used_anchors(一個 apply_patch 只當一次錨)。F2 裸 stem 撞同名不同目錄 HIT(新,其他席沒抓):折入 帶路徑的詞改成完整相對路徑精確比對、不降 stem;兩個掃描迴圈同步。F3=外家 #2、F4=外家 #3、F5=外家 #4(已折)。
