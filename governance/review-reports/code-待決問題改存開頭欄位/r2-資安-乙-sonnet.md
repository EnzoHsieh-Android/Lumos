severity: clean

skill 檢查:python-idioms 的邊界驗證、秘密不進 log、反序列化與 shell 條款存在。專案資安類 linter 輸出:無。

1. 子程序與命令拼接:已看,無。
   - 所有 `subprocess` 呼叫(`_sp.run` 的 git 指令、`_sp.Popen`)都是 list 形式,沒有 `shell=True`,沒有 `eval`、`exec`、`os.system`。
   - `Popen` 的程式是 `sys.executable` 加 `GRAPHCTL`。`GRAPHCTL` 由 `Path(__file__).resolve().parent / "lumos"` 算出(`scripts/test_lumos.py:30`),指向 repo 內部,不是不可信位置。
   - 傳進去的參數是測試寫死的字串(`題{i}`、`Projects/c{rnd}_計劃`)和 `tempfile`、`mkvault()` 產生的路徑。沒有外部輸入,沒有環境變數注入點。
2. 暫存目錄:已看,無。
   - `tempfile.mkdtemp(prefix="gctl-qfm5-")` 建立的目錄權限是 0700,不會有可預測路徑被搶先佔用的問題。
   - 其他測試用 `mkvault().parent.parent / "qfm1"` 等路徑,位於 mkvault 的暫存樹下,沒有寫到固定的 `/tmp` 路徑。
3. `git commit --no-verify`:已看,無。
   - 出現在 `t_qfm_gate_holds_blocking` 和 `t_qfm_push_remind_ranges`,對象是 `git -C <d>`,而 `d` 是測試建的暫存 repo。
   - 跳過的是暫存 repo 自己的 hook,不是專案 repo 的 pre-commit/pre-push,不算繞過專案的閘。
   - 使用者全域設定的 `-c user.email=t@t` 是用 `-c` 單次帶入,沒有寫進全域設定。
4. 技能與筆記對代理的指示:已看,無。
   - `SKILL.md`、`03-寫回圖譜.md`、`reference.md` 的改動只是把「待決問題」從正文改成用 `lumos question-add` 和 `question-set` 寫進開頭欄位。
   - 沒有教人跳過檢查、執行不明指令或把秘密寫進檔。文中提到的 `LUMOS_SKIP_NOTE_SHAPE=1`、`drift fix` 等都是此 patch 之前就有的舊字句,不在這次增加的範圍。
   - 指令範例的參數是 shell 安全的:文件明講 `decision=#dN` 的 `#` 在字中間,shell 不會當註解。
5. 密鑰與個資:已看,無。
   - 我掃了 `postgres://`、`user:pass@`、`sk-`、`AKIA`、`ghp_` 和 email 等樣式,沒有命中。
   - `t@t` 是假資料。
   - 計劃筆記第 245 行提到 MCP Toolbox 連資料庫用「唯讀帳號」,只有描述,沒有帳號密碼或連線字串。
6. 執行邊界:已看,無。
   - 測試只讀寫 repo 內與暫存的路徑。
   - 沒有碰 `~/.claude`、`expanduser`、`chmod`、`rm -rf`、`curl`。
   - CI 執行的是 repo 內的 `scripts/lumos`,沒有載入外部位置的檔。
7. 新依賴:無。這個 patch 只動測試檔、筆記和技能文件,沒有新 `import` 第三方套件,也沒有動 requirements。
8. 其他類別:已看。
   - 筆記裡 `--decision "<節點>#dN"` 這種由使用者指定節點路徑的欄位,其驗證(例如路徑穿越)在主程式那半,不在這份 patch 內。
   - 這份 patch 的測試只用了合法的 `#d1`、`Projects/e2_計劃#d1` 等值,沒有帶 `../` 的案例。這是測試覆蓋面的觀察,不是可利用的洞,也不報為發現。

總結:被審的測試檔、圖譜筆記和技能文件沒有可利用的資安洞,所有項目都是 clean。
