severity: minor

# r1 正確性鏡頭:掛鉤、安裝腳本、註冊、精簡版生成器、CI、文件與筆記

## F1 CI 的 3.9 守衛只擋語法,擋不到「開頭版本檢查之前就在 3.9 執行失敗」
severity: minor
blocking: 否 — 現況 scripts/lumos 在 3.9 跑得起來,是守衛範圍比宣稱窄,沒有現在就壞的行為;維護者機器上有真 3.9,本機測試 t_lumos_old_python_reexec_or_explain 補得到一部分
引句:「scripts/lumos 等三類檔必須 3.9 還能解析,舊版啟動時才跑得到開頭的版本檢查」
1. ci.yml 新增的步驟只跑 `ruff check --isolated --target-version py39 --select E9 ...`,只查語法。
2. 「跑得到開頭的版本檢查」還要求版本檢查之前的 import 與頂層敘述在 3.9 能執行。CI 跑在 ubuntu-latest + setup-python 3.14,沒有任何一步用真 3.9 起 lumos。
3. 重現:把 `import tomllib` 插到 scripts/lumos 第 60 行(標準庫 import 區)。`ruff check --isolated --target-version py39 --select E9 scripts/lumos` 輸出 `All checks passed!`(rc 0),`/usr/bin/python3 scripts/lumos python-path` 輸出 `ModuleNotFoundError: No module named 'tomllib'`。CI 這一步綠,舊版啟動卻連「需要 3.14」的說明都印不出來。
4. 語法類的替身確實守住了:同樣方式插 `print(f"{d["a"]}")`,ruff 會報 `Cannot reuse outer quote character in f-strings on Python 3.9`。缺的只有執行期那一半。
file: `.github/workflows/ci.yml:24`

## F2 升級說明漏講 Codex 掛鉤命令列改了要重新按信任,跑完 lumos install 後 Codex 掛鉤會靜默不跑
severity: minor
blocking: 否 — 只影響 Codex 側掛鉤在升級後、重新信任之前的空窗,不影響 git 掛鉤與 Claude 側;install 本身印的提示有講重審
引句:「裝好之後跑一次 `lumos install`，讓 Claude／Codex 的掛鉤也改用 3.14」
1. merge-claude-settings.py 現在把寫進設定的命令列從 `python3 "…"` 改成 3.14 絕對路徑(Codex 分支經 shlex.quote),每一條 Codex 註冊的命令列文字都變了。
2. scripts/lumos 自己寫的話是「信任綁的是 hooks.json 裡那條命令列——lumos 更新 hook 檔內容不用重審,命令列變了才要」。所以照 README 說的升級一次,所有 Codex 使用者的五支掛鉤都會落入「已註冊但未信任」。
3. README.md、README.en.md、ONBOARDING、lumos update 的 `_PY314_UPGRADE_NOTICE` 都只說「跑一次 lumos install 讓掛鉤改用 3.14」,沒有一處講「Codex 要再開一次互動 codex 按信任,否則不會跑」。設定壞掉的症狀是「不報錯就是不跑」。
4. 重現(讀碼即可):`grep -n "命令列變了才要" scripts/lumos` 對到 install 印的 Codex 尾句;而升級注意文字裡沒有對應句。
file: `scripts/lumos:18424`

## F3 pre-push 在只有推送刪除(沒有任何要叫 lumos 的東西)時,也會因找不到 3.14 而擋下
severity: minor
blocking: 否 — 只有沒有 3.14 的機器刪遠端分支才碰到,出口(--no-verify)訊息有寫;與計劃〈做法〉3 的「pre-push:標準輸入讀完之後、有 scripts/lumos 時」字面一致,只是跟 [S3]「確定這次要叫 lumos」的意圖有落差
引句:「if _lumos_py314; then」
1. pre-push 讀完 stdin 後,只要 scripts/lumos 存在就先 `_lumos_py314`,失敗就 `exit 1`,不看這次推送有沒有任何 ref 需要檢查。
2. 重現(臨時 repo,複製 scripts/lumos 與 scripts/hooks/pre-push):`echo "(delete) 0000000000000000000000000000000000000000 refs/heads/x abcdef0123456789abcdef0123456789abcdef01" | LUMOS_PYTHON=/nonexistent bash scripts/hooks/pre-push origin url; echo rc=$?` 得到 rc=1,印「擋下:這一道檢查要用 Python 3.14 跑 lumos」。刪除 ref 本來所有後段檢查都跳過。
3. 是否要改成「只有真有需要檢查的 ref 才擋」是取捨題,⚠ 我沒有讀到設計裡明說刪除也要擋的裁定。

## 已看,無 finding
- 七份內嵌「找任何 python」段:逐字一致(七份 md5 相同)。在 `set -euo pipefail`、HOME 空字串或未設、PATH 只有 py 啟動器、PATH 為空、`LUMOS_PYTHON_SEARCH_DIRS` 為空時都不中途結束:有 py 時得 `py -3`,PATH 為空時回 1 走「找不到」訊息。
- pre-commit:有 scripts/lumos 找不到 3.14 時只提醒的閘(co-change、delguard)跳過、Gate PY 擋下 rc1;沒有 scripts/lumos 時 Gate PY 不觸發,照舊只跑不需 python 的閘(實跑確認);圖譜不存在、staged 為空在更前面就放行。Gate PY 位置在 Gate 1 之後、Gate L 之前,而 Gate H、NS 對任何有 staged 的提交都會叫 lumos,所以「先擋」跟「原本後面才擋」的結果一致,沒有新增誤擋面。
- pre-push:沒有 scripts/lumos 放行;有 lumos 找不到 3.14 擋下,說明原樣轉印,不退回舊版。
- post-commit:沒有 3.14、只有 /usr/bin/python3 3.9 且固定位置清空時,照樣寫入 docs/.bypass-log.jsonl 且 rc 0(實跑確認);找不到任何 python 時 `|| exit 0`,不中斷提交。
- get.sh / install.sh / install-hooks.sh / install-graph-toolchain.sh:launcher 放在 main() 之外只有函式與字串定義,沒有副作用,curl 串流被截斷最多是語法錯誤、不會執行半段;舊安裝複本不再被讀,行為一致。
- get.ps1:`py -3` 帶參數、每個候選真的執行 `-c pass`、`$pyArgs` 展開正確。⚠ Windows PowerShell 5.1 在 `$ErrorActionPreference = "Stop"` 下 `2>$null` 對原生命令的行為,本機無 Windows 未能驗。
- merge-claude-settings.py:以 /usr/bin/python3 (3.9) 直接啟動,會問同目錄 lumos、改用 3.14 重跑並寫入絕對路徑(實跑,HOME 指向臨時目錄);舊格式 `python3 "${HOME}/…"` 註冊會被 migrate 成新命令、第二次跑全部 skip、不重複;3.9 能解析(ast.parse 通過)。
- slim-gen.py 剝段:begin/end 標記在 scripts/lumos 只各出現一次;實跑生成後產物不含 `_py_floor_gate()` 呼叫,`/usr/bin/python3` 可執行產物;只有開頭沒結尾會 SystemExit。
- CI 語法守衛:ruff 0.16.7 對 3.12 f-string 重用引號、match、except*、型別參數、type 別名、f-string 內反斜線都在 py39 目標下報 invalid-syntax;副檔名不影響(明確給路徑的無副檔名 scripts/lumos 也會被檢查)。執行期那一半見 F1。
- 文件:ARCHITECTURE 與 reference.md 的「80 個頂層命令」與 `lumos --help` 實數 80 相符;ONBOARDING 說「python3 指舊版也沒關係」與 /usr/bin/python3 實測 python-path 可運作一致;其餘敘述與程式行為對得上。
- 圖譜筆記:Systems/bound-tests-gate、codex-harness、lumos-cli-lifecycle、python直譯器選擇的新句子與程式行為(pre-push 擋下、{python} 代入、sys.executable 註冊、找任何 python 只叫 lumos)一致。計劃〈做法〉3「Gate 1–3 照跑照擋」與實作的 Gate PY 位置(擋在 Gate 2、3 之前)字面上有出入,但 Gate 2、3 在 Gate H、NS 之後本來就到不了,實質不改變結果,不列為 finding。

最嚴重等級 minor,blocking 共 0 條
