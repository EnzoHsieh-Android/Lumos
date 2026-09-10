# r4 收貨紀錄(編排者)

★第四輪是高風險三輪上限之後、由負責人(Enzo)2026-09-10 裁定加開的★,審第三輪 17 條修法與整批完整 diff。
派出七席:五席 Claude(正確性/邊界/整合/併發資源/架構對齊,sonnet)+兩席外家 Codex。
★外家兩席都沒有產出★:23:13 派出,37/46 秒就撞到 Codex 帳號用量上限(「try again at Sep 11th, 2026 3:02 AM」)。
本輪以五席 Claude 收齊為準——★結論只代表 Claude 一家看過★,沒有外家視角。
五席全數收齊後才動工作目錄。報告本體一律從各席的輸出紀錄(tasks/<id>.output)抽,不從完成通知抄(通知會把 < > 轉碼)。
邊界席一處純格式搬移(report-normalize --write:F37 的 severity 行後面接的說明移到下一行,不改等級、不改內容)。
五份報告 quote-check 全數錨定。

## 第三輪 17 條的驗收

五席一致判 F19–F22、F24–F29、F31、F33–F35 修到。
F23:整合席判「修到,但比對鍵那一側讀不到目錄時默默退回字面」(→ 本輪 F45);其餘四席判修到。
F24:邊界席判「修到但修出新洞」(讀不到的工具檔直接中斷 → 本輪 F36)。
F25:邊界席、併發資源席判「修到但另有新洞」(Windows 那條鎖、撤銷繞過鎖 → 本輪 F37、F39)。
F30:架構對齊席判「沒修到」(--plan 那條回掛還只接 OSError → 本輪 F44)。
F32:正確性席判「修出新洞」(引號裡只有空白 → 本輪 F46)。

## 去重後的發現(本輪)

| id | 等級 | 一句話 | 哪幾席抓到 |
|---|---|---|---|
| F36 | blocker | 工具檔讀不到(權限、被鎖)時,_vendored_state 逐檔讀內容沒包例外,健檢與風險掃描直接噴錯中斷 | 邊界 F36 |
| F37 | major | 寫入鎖是專案裡第二套鎖機制(flock);Windows 那條路也沒有明確解鎖 | 架構對齊 F37、邊界 F37 |
| F38 | major | 讀某版本檔案內容另寫了一套 cat-file --batch 解析,專案各處用的是 git show | 架構對齊 F38 |
| F39 | major | about-code revert 清 about_code_stamp 那步直接呼叫底層函式,繞過寫入鎖 | 併發資源 F36 |
| F40 | minor | 鎖開不起來時默默不上鎖 | 併發資源 F37 |
| F41 | minor | 同一個程序巢狀拿鎖會自己卡 60 秒,訊息還說「別的程序在寫」 | 併發資源 F38 |
| F42 | minor | _write_lf 讀 umask 的寫法會短暫改掉整個程序的 umask,多執行緒不安全 | 併發資源 F39 |
| F43 | minor | 指紋清單跟既有的錨點基準線同概念、格式不同 | 架構對齊 F39 |
| F44 | minor | new verification --plan 那條回掛只接 OSError | 架構對齊 F36 |
| F45 | minor | about_code 比對鍵在目錄讀不到時默默退回字面比對 | 整合 F1 |
| F46 | minor | 引號裡只有空白的舊值,加項目後留下一筆空白垃圾項 | 正確性 F36 |

## 編排者機械重現(修改前的程式=本輪凍結版本;暫存 repo)

| id | 怎麼重現 | 結果 |
|---|---|---|
| F36 | 消費 repo 放 chmod 000 的 scripts/lumos,跑 pitfalls --diff HEAD | HIT:PermissionError traceback |
| F37 | 讀碼:grep fcntl/msvcrt 全檔只有 _vault_write_lock 一處;既有 _take_lock 是 O_EXCL 建鎖檔;Windows 分支沒有解鎖呼叫(Mac 上跑不到那條路,席位自標未能重現) | HIT(讀碼) |
| F38 | 讀碼:_git_show_many 是全檔唯一手刻 cat-file --batch 協定的地方;_json_at_ref 等用 git show | HIT(讀碼) |
| F39 | 讀碼:about-code revert 第 11364 行直接呼叫 _cmd_remove_scalar | HIT(讀碼) |
| F40 | 讀碼:except OSError: yield 不印任何東西 | HIT(讀碼) |
| F41 | 讀碼+席位實測:同程序巢狀 with 兩層,內層等滿 60 秒 | HIT |
| F42 | 讀碼:_um = _os.umask(0); _os.umask(_um) | HIT(讀碼) |
| F43 | 讀碼:vendored.json 沒有 version,anchor-baseline 有 | HIT(讀碼) |
| F44 | 讀碼:--plan 那段 except OSError | HIT(讀碼) |
| F45 | 讀碼:_about_code_key 以 `real, _ =` 丟掉讀不到的訊號 | HIT(讀碼) |
| F46 | `tags: "  "` 後 append x | HIT:寫成兩項 `"  "` 與 x |

## 判讀

- F36:讀不到的工具檔=存在、但不算原封不動(照樣掃),不中斷。
- F37/F40/F41:寫入鎖改用專案既有的鎖檔做法——把 dispatch-lens 的 _take_lock 抽成共用 _excl_lock_try(行為不變),
  寫入鎖在它上面每 0.05 秒重試、最多 60 秒;鎖檔照 dispatch-lens 快取的先例放 ~/.cache/lumos/,不放共用暫存目錄;
  同程序巢狀直接過;鎖的資料夾建不起來照寫但講一聲。沒有 msvcrt 那條路了,Windows 走同一套。
- F38:改用既有的 git show 包裝(_lens_git 補一個位元組模式,非 UTF-8 內容不會在解碼時噴錯);指紋清單用既有的 _json_at_ref 讀。
- F39:清 stamp 改走有上鎖的 cmd_remove(value=None 就是整欄拿掉)。
- F42:照 mkstemp 同樣的獨佔建唯一名做法,但權限給 0o666 讓它受 umask 管,不讀也不改 umask。
- F43:指紋清單加 version 欄位;不走錨點那種「人核可才改」的流程,理由寫在程式註解(這份是安裝時的事實紀錄,錯的方向是多掃)。
- F44:--plan 那條也接擋下與逾時。F45:remove 找不到、而且目錄讀不到時,訊息講明要用筆記裡原本的寫法。
- F46:單一值讀出來先去前後空白,引號裡只有空白就是空的;寫完自我檢查的「原本每一項都還在」也不把空值算成一項。
- code 迴圈:輪內有 blocker 與 major,accepted 必須是空的——十一條全折。

## 編排者自己抓到的(不是席位發現,不進處置清單)

- O5(派人之前):_stack_changed_ok 的說明文字還寫著第三輪之前的參數名(skip_vendored),已在凍結前修進工作目錄。
- O6(寫測試時):風險掃描讀整份差異用文字模式,提交裡只要有非 UTF-8 內容就整支中斷——既有問題、跟這批無關,
  這輪不修(修了又是一段沒審過的改動),另開事故筆記 Issues/風險掃描遇到非UTF-8內容整支中斷 追蹤。
