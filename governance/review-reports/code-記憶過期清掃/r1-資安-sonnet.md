severity: blocker

# 先講白話

這支程式是「開專案就自動跑一次」的清掃器，讀 Claude 記憶檔、照聲明去驗證，驗不過就在檔案上蓋章。作者把舊版「執行記憶檔裡寫的一行 shell 指令」拿掉，換成七種固定型別的檢查——**這個部分我實測驗證過，是真的**：不會再把記憶檔內容當指令跑。

但我另外找到兩個新的洞：一個是**只要有人（或 Claude 自己）往記憶目錄塞一個編碼有問題的檔案，整支清掃器就會當場摔死、而且死了沒有任何記錄**，之後每次開專案都一樣摔死，等於清掃器從此對所有記憶檔失效，沒人會注意到；另一個是**`--restore` 這個旗標收檔名完全不檢查，可以用路徑穿越把清掃器指去清掃器管轄範圍以外的任意檔案，並且已經實測成功抹掉別的圖譜節點頭部的 status 欄位跟警示字樣**——而這個系統的整套治理機制（doctor、閘、pre-push）就是靠這些欄位判斷「東西是不是還健康」。

## 驗證：作者宣稱屬實

引句:「沒有 shell，記憶檔裡的字串不可能被當成指令」

檢查 `CHECKS` 表對應的七個函式（`pushed`/`not-pushed`/`installed`/`not-installed`/`file-exists`/`no-file`/`before`），全部用 `subprocess.run(["git", *args], ...)` 或 `shutil.which`/`pathlib` 呼叫，沒有 `shell=True`、沒有字串拼接進 shell。`pushed`/`not-pushed` 的參數先過 `_SHA_RE = ^[0-9a-f]{7,40}$`、`installed`/`not-installed` 先過 `_NAME_RE = ^[A-Za-z0-9._-]{1,64}$`，兩者都不允許開頭是 `-` 的值，所以就算攻擊者能寫記憶檔，也塞不出 `--upload-pack=...` 這種偽裝成旗標的 git 參數。舊的 `cmd:` 寫法會被 `run_check` 直接短路回 `None`（file: `scripts/hooks/claude/memory-sweep.py:284-285`），不會執行。**這部分結論：宣稱屬實，機械擋住了。**

severity: clean
- blocking: 否

---

## Finding 1：一個編碼壞掉的記憶檔可以讓整支清掃器對所有記憶檔靜靜失效

引句:「text = f.read_text(encoding="utf-8")」（`sweep()` 內，見 patch 行 1328；同一寫法在 `shadow_copies`/`pointer_problems` 重複出現，patch 行 1034、1087）

`sweep()` 用 `for f in sorted(here.glob("*.md")): ... text = f.read_text(encoding="utf-8")`，中間沒有 `try/except`。只要記憶目錄裡有一個檔案不是合法 UTF-8，這一行就會丟 `UnicodeDecodeError`，而 `main()` 本身也沒有包 `try/except`（`memory-sweep.py` 完全沒有 import `_hookevent`，跟同批註冊的其他四支 hook 不一樣——那四支都 `from _hookevent import guard`，我 grep 過 `scripts/hooks/claude/*.py` 確認只有這支缺席）。後果：

1. 例外一路往上炸穿 `sys.exit(main())`，整個程序以非零狀態碼結束、印出 Python traceback。
2. 因為沒有 `guard()`，這次失敗**不會**寫進 `governance/runtime/hook-events.jsonl`——同一批其他 hook 崩潰時至少會留一筆 `kind: error`，這支完全沒有痕跡，觀測系統看到的是「這支 hook 從來沒被登記跑過」，不是「跑了但一直失敗」。
3. 崩潰發生在迴圈**還沒開始檢查任何一條 `verify:` 之前**（連 `--write` 模式都一樣，因為壞檔案的讀取發生在寫入判斷之前）。這代表壞檔案之後（依字母排序）的所有合法記憶檔，那一輪的宣稱**完全沒被驗到**——不是「跳過壞的那篇」，是整個目錄全部沒查。
4. 這個狀態會**每次開場自動重演**，因為沒有任何機制移除或標記那個壞檔案——攻擊者只需要讓一個檔案存在一次，之後每次「開專案」這個守衛都形同不存在。

我實際造了這個場景驗證（`/tmp/msweep_test2`）：目錄裡放一個合法檔 `good-one.md`（帶一條 `not-pushed` 宣稱）跟一個壞檔 `evil.md`（開頭合法 YAML、內文夾雜非 UTF-8 位元組），直接跑 `python3 memory-sweep.py --dir /tmp/msweep_test2/memdir`（不帶 `--write`，也就是「只看」模式）：

```
Traceback (most recent call last):
  ...
  File ".../memory-sweep.py", line 384, in sweep
    text = f.read_text(encoding="utf-8")
  ...
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 55: invalid start byte
exit code: 1
```

`good-one.md` 那條合法宣稱完全沒被驗到——因為 `evil.md` 字母序排在它前面，程式在到達它之前就已經整支炸掉。

**攻擊者需要具備什麼**：只需要能在這個專案的記憶目錄放進（或誘使 Claude 自己寫出）任何一個非合法 UTF-8 的 `.md` 檔——這正是這整支工具的信任邊界本身假設「能寫記憶檔」的那個角色就具備的能力，不需要額外提權、不需要第二個步驟、不需要說服任何人執行任何指令。這是這批修改本身要防的「守衛靜靜消失」的教科書案例，而且是自動觸發、無需互動的。

severity: blocker
- blocking: 是

---

## Finding 2：`--restore <檔名>` 沒有做基底檔名檢查，可路徑穿越寫到記憶目錄以外，已實測抹掉別的節點的治理欄位

引句:「f = here / a.restore」

引句:「f.write_text(unstamp(f.read_text(encoding="utf-8")), encoding="utf-8")」

`--restore` 把使用者/呼叫端傳進來的 `a.restore` 原封不動跟 `here`（記憶目錄）用 `/` 接起來，完全沒檢查它是不是「純檔名、不含路徑分隔符」。Python 的 `pathlib` 對 `/` 運算子的行為是：

- 如果 `a.restore`是絕對路徑，`here / a.restore` 會**整個丟掉 `here`**，直接變成那個絕對路徑（`Path("/tmp/a") / "/etc/passwd" == Path("/etc/passwd")`，我在 `/tmp` 下測過，行為確認）。
- 如果含有 `../`，一樣照樣往上跳出記憶目錄。

而且它會先 `read_text` 再 `write_text` 回同一個路徑——也就是說目標檔案必須已存在（否則 `read_text` 會先炸掉、不會憑空建立新檔），但只要存在，`unstamp()` 就會對它的內容做兩個正則替換：拿掉任何長得像「開頭兩格縮排 + `status:`/`stale_at:`/`stale_by:` 欄位」的行，以及拿掉以清掃器警示字串開頭的行。

我實測了完整攻擊鏈（`/tmp/msweep_test`）：造一個「記憶目錄以外」的檔案 `../othernode/victim.md`，內容模擬一個真的圖譜節點頭部（`status: stale` / `stale_at:` / `stale_by:` + 警示行），然後跑：

```
python3 memory-sweep.py --dir /tmp/msweep_test/memdir --restore "../othernode/victim.md"
```

輸出 `撤掉蓋章:../othernode/victim.md`，實際檔案內容從：

```
metadata:
  status: stale
  stale_at: 2026-08-01
  stale_by: 舊資料
---
> ⚠ 這篇有宣稱已經對不上了（2026-08-01）：**舊資料**。內容留著沒刪，但引用之前先自己查一次。
```

變成：

```
metadata:
---
```

——`status`/`stale_at`/`stale_by` 三個欄位跟警示行全部被拿掉，而這個檔案根本不在記憶目錄底下、跟這支清掃器毫無關係。這套系統的 doctor、code-loop、pre-push 全部靠這些頭部欄位判斷「這篇節點還健不健康、要不要重驗」（見本專案 CLAUDE.md 鐵則四「回頭條件要接電」與 `docs/lumos-toolchain-knowledge` 的 status/stale 慣例）——這代表只要能觸發一次帶穿越路徑的 `--restore`，就能悄悄把任何一篇圖譜節點（甚至別的專案的檔案，只要路徑猜得到、當前使用者有寫入權限）身上的「已知有問題」標記抹掉，讓它看起來重新健康。

**攻擊者需要具備什麼**：`--restore` 目前在整個 repo 裡沒有任何自動化呼叫點（我 grep 過，只有工具自己的 `--help` 文字提到它），所以它不會被 SessionStart hook 自動帶到——真正登記進 `merge-claude-settings.py` 的呼叫是固定字串 `--write --quiet --budget 12`，不含 `--restore`，攻擊者沒辦法只靠寫記憶檔就自動觸發這條路徑。要利用它，需要多一步：讓某個人（或者這個環境裡實際在跑指令的 Claude 自己）被說服去執行 `memory-sweep.py --restore <攻擊者選的字串>`。工具說明文字把 `--restore <檔名>` 呈現成「撤掉某一篇的章」的日常操作，而清掃器自己印出的候選檔名（`✗ %s` % f.name）永遠是安全的純檔名——所以正常操作不會踩到；風險來自記憶檔本身（或任何未來包這支工具的自動化腳本）用文字建議一個帶 `../` 的「檔名」當作補救指令，而執行端沒有意識到那其實是路徑穿越。這比 Finding 1 多一道門檻，但考慮到這個環境裡「讀取記憶檔內容 → 依內容決定下一步該跑什麼指令」本來就是 Claude 自己的日常行為模式，這道門檻並不高。

severity: major
- blocking: 是

---

## Finding 3：`file-exists` / `no-file` 收路徑完全不做格式限制

引句:「pathlib.Path(arg).expanduser().exists()」

跟 `pushed`（要求 hex sha）、`installed`（要求 `_NAME_RE`）不同，`_chk_file_exists`/`_chk_no_file` 對 `arg` 沒有任何格式檢查，任何字串（含 `~` 展開）都會被拿去 `.exists()`。這不會造成程式碼被執行或內容外洩到攻擊者本來看不到的地方——因為能寫這條 `verify:` 宣稱的人本來就是攻擊者自己，`claim` 文字也是他自己寫的，清掃結果只是決定「這條宣稱算過還算沒過」再原樣印出攻擊者自己寫的 `claim`，沒有新增資訊。真正的風險是：指到一個會讓 `stat()` 卡住的路徑（例如沒回應的網路掛載點），會讓這一條檢查卡住直到外層 `--budget`（固定 12 秒）逼 harness 把整支 hook 砍掉——屬於小範圍的可用性影響，不是資料外洩或越權寫入。

**攻擊者需要具備什麼**：跟其他每一條一樣，需要能寫一條 `verify:` 宣稱進記憶檔，沒有比這更進一步的權限需求，影響也僅止於讓單次 hook 執行變慢/被砍。

severity: minor
- blocking: 否

---

## Finding 4：清掃結果會把記憶檔/圖譜裡的原始字詞原樣印進每次開場的輸出

引句:「tally.lines.append("★下面這幾篇在記狀態，而圖譜裡已經有一份」

`cross_check()`/`shadow_copies()`/`pointer_problems()` 會把記憶檔裡的檔名、命中的關鍵字、`[[…]]` 連結名稱，原樣接進 `tally.lines`，而這些行會在**每次開場、沒有任何「這是不可信資料」標記**的情況下印出來，成為這次對話一開始就餵給 Claude 的文字。這不是這批 diff 新引入的能力（能寫記憶檔的人本來就能透過記憶檔內容影響下一個 session 開場看到什麼——舊版 `cmd:` 執行任意指令的風險遠大於這個），但這批修改把「執行」的洞補了之後，「把攻擊者選的文字原樣送進 Claude 的輸入」這個管道還留著，值得記一筆，供之後設計提示注入防線時參考（例如替 memory-sweep 的輸出加一行「以下為記憶檔內容摘要，非指令」之類的邊界標記）。

**攻擊者需要具備什麼**：跟其他每一條一樣，只需要能寫記憶檔內容，沒有比現有信任邊界更進一步的權限；屬於既有設計就承擔的風險，這裡只是指出這批修改沒有讓它變得更好或更壞。

severity: minor
- blocking: 否

---

# 收尾

- 共 5 條（1 條 clean 驗證 + 4 條 finding）
- 最高等級：blocker
- 最嚴重那條一句話：一個編碼壞掉的記憶檔案就能讓整支清掃器每次開場都當場摔死、而且摔死了完全沒有留下任何記錄，等於守衛從此對所有記憶檔靜靜失效。
