severity: minor

逐類結果:

1. 不可信輸入流到危險操作:放行阻塞題的路徑已看,無可利用處。
   - 我試了 block scalar 界線、同形字鍵名(全形、大小寫、引號鍵,NFKC 加 casefold)、多個 pending_questions、頂格非 ASCII 鍵、tab 或不斷行空白縮排、header 後接 `\t#`。
   - 每種都落到「整份當無法判定」的錯誤,或被當成文字,沒有讓阻塞題消失的路。
   - Default_Ignorable_Code_Point(DICP)表與 Unicode 16 逐段對過,沒有缺段。
   - 錯誤訊息裡的使用者文字大多用 `!a` 或 `!r`,控制字元和雙向覆寫都會被跳脫。
   - 唯一剩下的缺口是下面第二條(藏字)與第三條(訊息未清洗)。
2. 權限與守衛繞過:
   - signoff 還原的路徑固定是 `env.vault / rel`,`_write_lf` 用暫存檔加 `os.replace`,不會跟著符號連結寫到庫外。
   - 硬連結也因為換 inode 而不會改到別處。
   - `rglob` 不跟隨目錄符號連結,所以只檢查檔案本身是否為符號連結夠用。
   - WriteBlocked 同時是 ValueError 與 RuntimeError,main 外層和 guard 分支都接得到,不會被靜默吞掉。
   - 缺口是簽核帳檔沒檢查符號連結,見下面第一條。
3. 密鑰與個資:已看,無。
4. 加密與傳輸:已看,無。
5. 執行邊界:`git rev-parse` 用 list 參數,沒有 shell。已看,無。
6. 行動端:不適用。
7. 新依賴:只多了標準庫 `bisect`,無。

發現:

severity: minor
blocking: 否
引句:「log = env.vault.parent / ".signoff-log.jsonl"」
簽核帳檔 `.signoff-log.jsonl` 沒有符號連結檢查,而這輪宣稱的是「讀前與寫前都檢查符號連結」。
- 攻擊路徑(推論):
  - 誰:惡意 repo 的作者。這個帳檔在 `.gitignore` 與帳檔清單裡是 `docs/.signoff-log.jsonl`,會進 git,所以可以在 repo 裡放成符號連結。
  - 送什麼:把它指到受害者家目錄裡的檔案(例如 `~/.zshrc`,用絕對路徑猜得到使用者名稱),再放一篇檔名含 `$(…)` 的計劃筆記。
  - 拿到什麼:受害者在這個 repo 跑 `lumos signoff` 時,`open(log,"ab")` 會把含該檔名的 JSON 行(`{"ts": …, "node": "…$(…)…"}`)追加到目標檔。zsh 解析那一行時,雙引號內的 `$()` 可能被展開執行。
  - 新增的失敗還原 `log.write_bytes(log_before)` 也會跟著連結寫。
- 這個缺口舊程式碼就有,這輪重寫 signoff 時沒補上。要利用得有人在陌生 repo 實際簽核,所以只算縱深防禦。
- 佐證 file: `scripts/lumos:9141`(在 36d4ffed 版)

severity: minor
blocking: 否
引句:「or (_pq_is_letterish(v[i - 1]) and _pq_is_letterish(v[i + 1])))」
ZWJ(U+200D)、ZWNJ(U+200C)、軟連字號(U+00AD)只要夾在任兩個字母之間就放行,ASCII 拉丁字母之間也算。
- 攻擊路徑(推論):
  - 誰:惡意計劃筆記的作者。
  - 送什麼:在待決問題的 `text:` 裡,每個字母間隙選「不放、ZWJ、ZWNJ、軟連字號」四種之一,編碼出隱藏位元。相鄰兩個 DICP 被擋,所以每個間隙最多一個。
  - 拿到什麼:人眼看不到、AI 讀到的是帶零寬字元的 token,是一個隱形的資訊通道,可以夾帶指令。頻寬低,AI 也得會解碼。
- 同理,U+FE0F、U+FE0E 出現與否也能在每個 emoji 後各藏一位元。
- 規格說「合法位置放行」,但 ZWJ 與 ZWNJ 在拉丁字母間沒有任何合法用法。若要收緊,可限定兩側同屬非拉丁文字(例如印度系、阿拉伯文字)。
- 佐證 file: `scripts/lumos:6981`(在 36d4ffed 版)

severity: minor
blocking: 否
引句:「raise WriteBlocked("寫完讀回來檢查,發現欄位區塊多了會讀錯的寫法,這次寫入不算成功:" + "; ".join(sorted(introduced)))」
WriteBlocked 統一由 main 外層以 `print(f"擋下:{exc}")` 印出,沒有清洗。
- 這一條訊息帶的 lint 指紋含有欄位區塊的原文片段,例如 `l2.strip()[:60]` 與 `line.strip()`。
- 攻擊路徑(推論):惡意筆記裡的 ESC 序列或雙向覆寫字元,若剛好成為「這次寫入新增的 lint 指紋」,就會原樣印到終端。
- 要讓攻擊者原文變成新增指紋需要巧合條件,利用難度高。
- 建議:外層邊界印出時過一次 `_esc_clean`。
- 佐證 file: `scripts/lumos:20448`(在 36d4ffed 版)

總結:這輪改法在放行阻塞題與符號連結守衛上沒有找到可直接利用的洞,剩下三條都是縱深防禦(帳檔符號連結、字母間零寬字元藏字、擋下訊息未清洗),均為推論,不阻擋合併。
