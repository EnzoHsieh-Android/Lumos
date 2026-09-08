# r3 intake — 接手視圖(代碼審驗收輪,外家 Codex,2026-09-07)

preflight-4: n/a(代碼審,非設計審)

材料:`r3-snapshot.diff`(r2 #5 折入後、相對 HEAD 的 diff)、派工詞 `r3-codex-prompt.txt`(只驗 #5;每條 finding 必附引句)、報告本體 `r3-外家codex.md`(從逐字稿最後一個 `severity:` 切出;完整逐字稿 `r3-外家codex-transcript.md`)。
席位宣告 severity: major,2 條新 finding(#6、#7),都在探針(測試)上;席位明說「同信任域與不動 hook 的範圍刀可以接受」。

## 逐條

- **#6 `os.open` 的數字 flags 繞過寫入檢查 — HIT,折**。稽核事件 `open` 的參數是 `(path, mode, flags)`;`os.open(path, O_WRONLY)` 走的是 mode=None、flags=數字,探針只看 mode、把 None 當 "r",而 hook 路徑本身在允許清單內→寫入自己不違規。折法:寫入判定同時看 mode 字串與 flags(`O_ACCMODE != O_RDONLY` 或帶 `O_CREAT/O_TRUNC/O_APPEND`);用 fd 開的(看不出目標)保守算違規。翻紅釘:hook 頂層塞 `os.close(os.open(__file__, os.O_WRONLY))` 要紅。
- **#7 允許清單放太寬 — HIT,折**。原本把 `purelib/platlib`(就是 site-packages)、`sys.prefix`、`sys.base_prefix` 都當標準庫,又用 `startswith` 沒驗目錄邊界→讀 `sys.executable` 不違規。折法:只留 `stdlib/platstdlib`、realpath 後用 `commonpath` 驗邊界。翻紅釘:hook 頂層塞 `open(sys.executable, "rb").read(1)` 要紅。
- 「仍會執行可變 hook」:席位本輪判「同信任域與不動 hook 的範圍刀可以接受」——r1 #5 的判準之爭到此收;剩下的是探針的嚴密度,r4 只驗 #6/#7。

## 帳
- r3 已記(severity major、findings 2、folded 6,7;reviewed 指紋=席位看到的計劃版本 4fb138…)。quote-check:兩條引句全數錨定。
