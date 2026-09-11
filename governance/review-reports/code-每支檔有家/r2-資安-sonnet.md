severity: minor

逐類檢視(這一輪新改的 scripts/lumos / hooks / test_lumos.py,背景同前:被 git 掛鉤在不可信 repo 內容上自動執行):

1. 不可信輸入流到危險操作:已看。`--diff` 範圍改走 `_lens_range_ok`(恰兩點、兩端都有,不收三個點),`--staged`/`--diff` 互斥改回手判斷、中文訊息,無新的 subprocess/shell 插值面。
2. 登入與權限:已看,無。
3. 密鑰與個資:已看。新加的兩處警告訊息(config.json 捷徑檔、lands_in 寫法看不懂/指到圖譜外面)都只印路徑或判定字串,不印檔案原文。
4. 加密與傳輸:已看,無(無網路)。
5. 執行邊界(F9/F10 這輪要驗收的正是這裡):F10(`_nodehome_landing_sizes`)已用 `_lands_in_bad` 擋 `../` 寫法、再用 `p.resolve().relative_to(vbase)` 擋捷徑,我用 `git commit` 一支指到圖譜外目錄的捷徑檔(`Systems/捷徑.md` 型)實測會被擋。F9(`_nodehome_config` 直讀工作目錄那支)只加了 `p.is_symlink()` 判斷葉節點,沒有比照 F10 用 resolve+relative_to 查整條路徑——見 G1。
6. 新依賴:已看,無(delta 裡新 import 全是測試檔案內的標準庫 `re`/`io`/`contextlib`/`os`)。

### G1 每支檔有家設定檔的捷徑防護只查葉節點,`.lumos` 目錄本身是捷徑仍會被跟讀
severity: minor
blocking: 否 — 讀到的內容一樣只拆成 mode(on/warn/off 三選一)/max_files(int)/ignore(字串清單)三類已驗證值,不回顯原文,且要有效果還得受害者本機在捷徑目標路徑下剛好存在一支 config.json——同 r1 對這條完全無防護時的判準,屬縱深防禦缺口不是可直接外流的洞
引句:「if p.is_symlink():」
佐證 file: `scripts/lumos:17722`(`_nodehome_config` 的 `from_snapshot=False` 分支,只查 `p.is_symlink()`——`p` 是 `.lumos/config.json` 本身,不是整條路徑);對照 `scripts/lumos:22933-22941`(`_nodehome_landing_sizes` 用 `vbase = (Path(root)/vault_rel).resolve()` 再 `p.resolve().relative_to(vbase)`,同一輪修法對「目錄本身是捷徑」有擋、這裡沒有);呼叫點 `scripts/lumos:980`(`run_doctor` 一開頭就跑);`scripts/hooks/pre-push:136` 每次 `git push` 自動跑 `doctor --ci`;新測試 `scripts/test_lumos.py:37822`(`t_nodehome_config_disk_read_skips_symlink`)只覆蓋「config.json 本身是捷徑」,沒有覆蓋「`.lumos` 目錄本身是捷徑」這個變體
攻擊路徑(推論成分:能重現繞過本身,但要真的改變行為需要受害者本機在解析後路徑剛好有一支 config.json,這段我沒有可控管道):惡意投稿者把 `.lumos`(整個目錄,不是 config.json)commit 成指到某個絕對路徑的捷徑 → 受害者 clone → `git push` 觸發 `lumos doctor --ci` → `_nodehome_config` 對 `.lumos/config.json` 呼叫 `p.is_symlink()`,因為 lstat 只看路徑最後一段、中繼的 `.lumos` 一定會被作業系統跟過去,所以回 False → 照樣 `p.is_file()`/`read_text()` 讀進去 → 我用暫存目錄實測:`git init` 一個 repo、把 `.lumos` commit 成指到外部目錄的捷徑、`git clone` 到另一個資料夾模擬受害者,`Path(".lumos/config.json").is_symlink()` 回 `False`、`read_text()` 讀出外部目錄那支 config.json 的原文(見下方重現指令)。

重現指令(在 /tmp 底下,不動 repo):
```
TMP=$(mktemp -d); mkdir -p "$TMP/outside"; echo '{"node_home":{"gate":"off"}}' > "$TMP/outside/config.json"
git init -q "$TMP/repo" && cd "$TMP/repo" && git config user.email a@b.com && git config user.name a
ln -s "$TMP/outside" .lumos && git add .lumos && git commit -q -m evil
cd "$TMP" && git clone -q repo victim && cd victim
python3 -c "from pathlib import Path; p=Path('.lumos/config.json'); print(p.is_symlink(), p.is_file()); print(p.read_text())"
```
預期輸出:`False True`,接著印出 `{"node_home":{"gate":"off"}}`(外部檔內容被讀進來,新加的 `if p.is_symlink()` 守衛完全沒攔到)。

## 第一輪修法驗收
F9:沒完全修 — 新守衛只查 `config.json` 這個葉節點是不是捷徑,`.lumos` 目錄本身是捷徑時 `is_symlink()` 回 False、照樣讀到外部檔(已用 git commit+clone 重現,見 G1)
F10:修到 — `_lands_in_bad` 擋掉非 `Systems/<名>` 與 `../` 寫法,`p.resolve().relative_to(vbase)` 連「`Systems` 目錄本身是捷徑」這種變體都擋得住(我另外用暫存目錄重現驗證,行為正確),新測試也覆蓋了葉節點捷徑與 `../` 兩種寫法

總結:最高 severity minor,blocking 共 0 條
