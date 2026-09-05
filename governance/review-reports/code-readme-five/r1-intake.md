# code-readme-five r1 intake(2026-09-05,standard:通才-sonnet / 架構對齊-sonnet / 外家finder-codex)
收貨:外家 1/1 錨定;通才與架構引句/行號機驗見上方指令輸出(錨不到的不採信)。manifest 0 條。
## 外家 1 major:bash 直譯器清單漏 #!/bin/dash HIT(重現 rc=1)→ 改「首行是 #! 即算程式碼」,四處同一條規則(bash 兩支+check-graph-sync+impact-hook),刪三份清單常數;測試改成真餵 dash/env -S/fish/純文字/二進位/空檔驗語意,pre-commit 實測加 dash 與 env -S。
## 通才 1 major 2 minor:major 同上(同題);minor dotfile(.pythonrc)被當有副檔名 HIT → 去掉開頭的點再判,測試加 .pythonrc 擋;minor NUL 截斷 → 改成字串前綴比對後不受影響。⚠ permission_mode=bypass/dontAsk 時 block 會不會被忽略而名額白燒:本 session 查不到官方明文,記進計劃當開放風險(REVISIT 併 10/05:看 ~/.cache/lumos/stop-block 標記數 vs 逐字稿裡 LUMOS-STOP 出現數)。
## 架構 3 major 3 minor:major①python 側三套 shebang 實作不收斂 HIT(同上,三處同一條);major②直譯器清單語意分裂 HIT(同上,刪清單);major③測試只查函式名 HIT(改語意驗);minor 死別名 codex_stop_decision HIT 刪;minor LUMOS_AUTOLOOP 預設關違 *_OFF 慣例 HIT → 改 LUMOS_AUTOLOOP_OFF 預設 1(=暫停;開回設 0);minor tee -a 寫法 HIT → 改 >> log 2>&1 + 一行進 wrapper log。
辯方:全部有翻紅重現或多席同題,未開庭。同輪有 major → accepted 空。
