severity: major

## F1 鎖檔建不起來被當成「別人拿著」,init/update 靜默卡滿 60 秒
severity: major
blocking: 是
引句:「        with _vault_write_lock(docs_dir):」
file: `/home/user/Lumos/scripts/lumos:17866`
file: `/home/user/Lumos/scripts/lumos:41917`
失敗場景:
1. 家目錄的 ~/.cache 不可寫或不可信(沙箱、唯讀 HOME),`_vault_lock_where` 退到 docs/ 底下放鎖檔;docs/ 又不可寫(唯讀掛載、別的帳號擁有的 checkout)。
2. `_ensure_docs_gitignore` 一進 `_vault_write_lock`,`_excl_lock_try` 的 `os.open(O_EXCL)` 丟 PermissionError/EROFS,該函式對 `except OSError` 回 False,跟「鎖被別人持有」同值。
3. `_cm` 的 `while not _excl_lock_try(...)` 每 0.05 秒重試到 60 秒,才拋 RuntimeError,被外層 `except (OSError, UnicodeDecodeError, RuntimeError)` 吞掉回 [],畫面上沒有任何「在等鎖」的提示。
4. 這步在 `_init_additive_setup` 裡,`lumos init` 與 `lumos update` 都會走。就算 .gitignore 已經齊全、根本沒東西要寫,也先拿鎖,所以整條指令白白卡一分鐘。
重現(已跑):docs/ 設 555、HOME 指向 555 的目錄,以 nobody 身分呼叫 `_ensure_docs_gitignore`,輸出 `[] 60.0 s`。重現檔 /tmp/gls-r3/rp/t.py。
修法方向:先讀檢查「缺不缺」再拿鎖(缺才鎖),或讓 `_excl_lock_try` 區分 OSError(不可建)與 FileExistsError(被持有),前者直接放棄。

## F2 追加寫入端的 is_symlink/nlink 檢查與 open 之間有時間窗,open 又跟隨捷徑
severity: minor
blocking: 否
引句:「            with open(gi, "ab") as f:」
file: `/home/user/Lumos/scripts/lumos:21092`
失敗場景:
1. 程序 A 通過 `gi.is_symlink() or not gi.is_file() or gi.stat().st_nlink > 1` 檢查,`read_bytes()` 之後、`open(gi,"ab")` 之前,另一個對 docs/ 有寫入權限的使用者把 .gitignore 換成指向受害者檔案的捷徑(或 FIFO)。
2. `open(...,"ab")` 沒帶 O_NOFOLLOW,會跟捷徑,把 `.governance-local.jsonl` 等兩行追加進目標檔(FIFO 則永遠卡住,且卡在鎖裡,30 秒後被別人當過期鎖接手)。
3. 鎖只擋 lumos 彼此,擋不住外部程序。內容受限、需要先有 docs/ 寫入權,所以只給 minor;用 `os.open(O_WRONLY|O_APPEND|O_NOFOLLOW|O_NONBLOCK)` 再 fstat 驗 S_ISREG/nlink 可關窗。
⚠ 讀端 `is_file()` 到 `read_bytes()` 之間換成 FIFO 同理會卡讀,同一個修法一併處理。

## 已走過沒問題的範圍
- 兩個程序同時補:同一把鎖(鎖鍵為 docs_dir 的 realpath)序列化,讀到缺才追加,不會補兩份;O_EXCL 建檔路徑撞上對方新建的檔會 FileExistsError 回 [],可接受。
- 巢狀/重入:`_VAULT_LOCK_HELD` 處理,init 內不會自己卡自己。
- 建檔後被殺在寫入前:留下空 .gitignore,下次當作全缺追加,自癒。
- 追加中途被殺(半行):下次因原檔不以換行結尾先補換行再追加,不會黏成一行。
- 鎖過期接手(`_excl_lock_try` 的 stat 與 rename 之間的老 TOCTOU)只在 30 秒以上的殘鎖加兩個同時接手者才發生,後果最多是重複追加兩行,無害;屬共用的既有輔助,不歸這份 diff。
- 記憶體:.gitignore 整份讀入,是使用者自己的一般檔(捷徑、FIFO 已擋),體積不構成耗盡。
- `_usage_log` 的 `is_symlink` 後 `open(...,"a")` 同屬 F2 型時間窗,但寫入的是自己的流水行、不在鎖內,影響與既有 `_gate_event` 相同,不另列。
- 圖譜鏡頭:派工訊息尾端沒附 LUMOS-IMPACT 固定席筆記,無從逐條作答。

總結:最大問題是鎖不可建時 init/update 靜默卡 60 秒(F1,已重現),其餘為低風險時間窗。
