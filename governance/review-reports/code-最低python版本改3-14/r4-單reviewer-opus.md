severity: minor

# 代碼審 r4(破例一小輪)單 reviewer — 正確性與邊界

審材:`git diff b0eff2af..2620dfbf` 凍結版 r4-snapshot.patch(596 行)。在 clone-314(HEAD 2620dfbf)用 /opt/homebrew/bin/python3(3.14)跑了 t_python_resolver_order_and_floor(15 過)、t_hooks_block_without_python314(13 過)、t_doctor_flags_stale_hook_python(10 過)、t_python_launcher_blocks_agree(12 過)、t_installers_require_python314(6 過)。另外在 `git clone --shared` 出來的臨時副本裡做了反向驗證(故意改壞):`_py_which` 改回整條解析,⑤f 翻紅;pre-commit 的驗證段改成一律放行,①b 翻紅。pre-push 那段跟 pre-commit 必須逐字相同,由 t_python_launcher_blocks_agree 在 `scripts/test_lumos.py:51444` 起的兩行守住。

各塊結論:
- `_py_which` 只解析所在目錄那一層:已看,無 finding。符號連結指進子目錄的繞法已擋,macOS 的 /var 與 /private/var 兩種寫法都比到了,「目前目錄是家目錄時,底下的直譯器不能消失」這條也沒退步。
- pre-commit/pre-push 驗 python-path 回的路徑:修到了根上(假的 python3.14 不會再讓所有閘假放行)。Git Bash 的 `C:\...` 路徑有配對到,結尾的 `\r` 有去掉。另有一條 minor,見 F2。
- doctor 兩家目錄分開、精確比對:已看,無 finding。我逐一對過 merge-claude-settings.py 的 `_hook_cmd` 歷來寫出的形狀:POSIX 寫 `${HOME}`、Windows 寫解析後的家目錄、Codex 寫 `CODEX_HOME/hooks` 的絕對路徑,另有 2026-06-26 那段時間寫過的絕對家目錄。四種都在比對集合裡,舊註冊(寫著 /usr/bin/python3 的那種)照樣會被抓去探版本。
- uv 找不到與執行失敗分開:分類結果是對的,但錯誤訊息只取最後一行,在真的 uv 上會丟掉關鍵資訊。見 F3。
- 安裝腳本當場印 LUMOS_PYTHON 被略過:見 F1。
- 計劃與筆記:見 F4。

## F1 安裝腳本只印了「略過」,沒講後果,安裝照樣成功,下一次提交才被擋
severity: minor
blocking: 否 — 使用者現在看得到原因,錯誤判定沒變,只是說明不夠
引句:「if [ -n "$_LUMOS_ANY_NOTE" ]; then printf '%s' "$_LUMOS_ANY_NOTE" >&2; fi」
file: `install.sh:53`
file: `install.sh:20`
1. 條件:設 `LUMOS_PYTHON=/nonexistent/python3.14`,而且機器上另有 /opt/homebrew/bin/python3.14。
2. 內嵌的找 python 那段先把 LUMOS_PYTHON 略過,改用 python3.14,然後印出 `LUMOS_PYTHON=/nonexistent/python3.14 不存在、不能執行或不是 python,略過。`,回傳碼 0。接著以 3.14 exec lumos install/init。因為版本已經夠,開頭的檢查不會去讀 LUMOS_PYTHON,所以安裝成功。
3. 同一個環境下跑 `lumos python-path`:回 2,印「擋下:LUMOS_PYTHON 指的不是一支可用的 Python 3.14」。所以下一次提交,pre-commit 會擋下。
4. 重現(把 install.sh 的內嵌段抽出來跑,再用同一個環境變數跑 python-path):
   `LUMOS_PYTHON=/nonexistent/python3.14 bash <抽出的內嵌段+印出段>` → 印出上面那句「…略過。」、EXE=/opt/homebrew/bin/python3.14、rc=0
   `LUMOS_PYTHON=/nonexistent/python3.14 /opt/homebrew/bin/python3 scripts/lumos python-path` → rc=2
5. 新加的那行註解自己也寫了「之後掛鉤問 lumos 會因同一個值擋下」,但印出來的只有「略過」。這兩個字讀起來像是無害。r3 要解決的是「安裝安靜成功,下一次提交才因同一個值被擋」,現在做到了「不安靜」,「成功之後才擋」沒變,使用者也沒被告知會被擋。四支安裝腳本(install.sh、get.sh、install-hooks.sh、install-graph-toolchain.sh)都是同一行。

## F2 掛鉤驗 3.14 的方式比 lumos 自己的探針嚴:標準輸出多一行就誤擋
severity: minor
blocking: 否 — 只有特殊環境(sitecustomize 或 .pth 往標準輸出印東西)會誤擋,而且誤擋時會印說明,不會假放行
引句:「if [ "$("$LUMOS_PY" -c 'import sys; print("LUMOS_PY314_OK" if sys.version_info >= (3, 14) else "OLD")' 2>/dev/null | tr -d '\r')" = "LUMOS_PY314_OK" ]; then」
file: `scripts/hooks/pre-commit:108`
file: `scripts/lumos:159`
1. lumos 的 `_py_probe` 只看最後一行(`last = out[-1]`),python-path 在掛鉤那頭也是 `tail -n 1`。掛鉤新加的驗證卻要求整段輸出剛好等於 `LUMOS_PY314_OK`。
2. 重現:`PYTHONPATH=<一個目錄,裡面的 sitecustomize.py 只寫 print("site hello")>` 之下
   `python3 scripts/lumos python-path 2>&1 | tail -n 1` → `/opt/homebrew/bin/python3`(lumos 判合格)
   用同一支跑掛鉤那條 `-c` 探針 → 輸出 `site hello\nLUMOS_PY314_OK`,不等於記號,結果是 pre-commit/pre-push 擋下,訊息寫「不是 3.14 以上的 python」。
3. 同一支直譯器,lumos 說合格、掛鉤說不是,擋下的理由跟實情對不上。只取最後一行(`| tail -n 1`)就能跟 lumos 對齊,擋假程式的能力不受影響。⚠ 這種環境不常見,所以只標 minor。

## F3 uv 出錯時只取最後一行:真的 uv 在設定檔壞掉時,最後一行不含檔名;測試用的假 uv 形狀跟真的不一樣
severity: minor
blocking: 否 — 「執行失敗」和「找不到」分對了,只是說明的內容缺了關鍵資訊
引句:「if r.returncode == 0 or (err and "No interpreter found" in err[-1]):」
file: `scripts/lumos:189`
file: `scripts/test_lumos.py:51203`
1. 這台機器上的 uv 0.11.19:在一個放了壞 `uv.toml`(內容 `garbage[[`)的臨時目錄裡跑 `uv python find --system --no-python-downloads ">=3.14"`,回 2,標準錯誤有好幾行:`error: Failed to parse: \`uv.toml\`` / `  Caused by: TOML parse error…` / 插入號指示行 / `key with no value, expected \`=\``。
2. 在同一個目錄呼叫 `_py_uv_find(time.monotonic()+15)`,實際回的是 `(None, '執行失敗(回傳碼 2:key with no value, expected \`=\`)')`,沒有 uv.toml 這個檔名,使用者看不出是 repo 根的哪個設定檔壞了。
3. ⑤e 的假 uv 只印一行 `error: Failed to parse: uv.toml`,所以斷言 `"uv.toml" in why` 會過。拿真的 uv 就不成立:這個斷言守的是一個真實 uv 不會出現的輸出形狀。取第一行 `error:` 開頭的那行(或頭尾兩行都帶上)才會含檔名。
4. 反方向我也驗了:「找不到」的情況,真的 uv 只印一行 `error: No interpreter found for Python >=3.14 in managed installations or search path`(試過 >=3.15、==3.12.1、3.13.0、>=3.16,以及沒帶 --system 的情況,都只有一行),分類正確。

## F4 計劃裡 lumos.cmd 那段被搬進了「安裝腳本當場講」那條,跟上下文不接
severity: minor
blocking: 否 — 只是文件內部不一致,不影響行為
引句:「包裝檔 `lumos.cmd` 裡照舊寫指令名(版本管理工具換 exe 是常態),那一層不在這次範圍」
file: `docs/lumos-toolchain-knowledge/Projects/最低Python版本改3.14_計劃.md:119`
1. r3 之前,「包裝檔 lumos.cmd…PowerShell 安裝入口不受影響」這段接在「目前目錄裡的同名檔不收」那條後面,講的是目前目錄的攻擊面,後面緊接著 `REVISIT:2026-12-29 決定 lumos.cmd 要不要改寫絕對路徑`。
2. 這次改動把這段從目前目錄那條移除,接到新加的「安裝腳本在 `LUMOS_PYTHON` 被略過、改用別支時當場講」後面。現在讀起來變成「安裝腳本印略過原因」這個決定的一部分,跟 LUMOS_PYTHON 無關。REVISIT 行也跟著掛在錯的那條下面。
3. 目前目錄那條(第 116 行)少了「lumos.cmd 這層不在範圍、既有攻擊面」這條界線。

最嚴重等級 minor,blocking 共 0 條(共 4 條 minor)。
