severity: minor

驗收結論:這輪修補有修到,我沒找到會讓行為出錯的新問題。`units()` 把路徑每段轉小寫再比,所以 `.Git`、`sub/.GIT/y.kt` 都擋得住。我跑了 `-k choice_compile_units_guards`,1 passed。

我逐項對過你點名的極端輸入:
- **`in (x.lower() for x in …)`**:對生成器做成員判斷是合法的,語意正確。
- **`.git.bak`、`.git ` 帶空白**:不等於 `.git`,不擋是對的。macOS 上它們也不是版控資料夾。
- **`..` 之後的 `.GIT`**:`realpath` 先把 `..` 解掉,再做 `startswith` 與逐段比對,擋得住。
- **工作樹本身在叫 `.git` 的資料夾底下**:`relpath` 是相對 `wt_real` 算的,不會誤擋,也沒有新的誤殺。
- **土耳其 İ、全形 `.ＧＩＴ`**:`"İ".lower()` 會變成 `i` 加組合點,不等於 `.git`。APFS 的大小寫不分是簡單折疊、不做相容正規化,這兩種寫法在 APFS 上本來就不指到 `.git`,所以不擋是對的。
- **規格閘 REVISIT 改日期型**:格式正確,沒有帶進新問題。

同類位置還有一處沒補,屬於已登記的 14 條:`_kill_merge_apply` 的寫檔路徑完全沒有 `.git` 防護。

severity: minor
blocking: 否
`scripts/lumos:30006`:`_kill_merge_apply` 對目標檔只做 `target.startswith(c.wt_real + os.sep)`,不擋工作樹 `.git` 或 `.GIT` 底下的路徑。非合批編譯、逐支跑壞法的路徑上,配方的 `file` 若指向 `.git/hooks/x`,壞法會直接寫進去。我沒有能當場翻紅的最小重現。再者這份配方檔是自家管線產出,不是外部輸入,在單人威脅模型下風險低。補修差異自己的第 14 條也已承認「擋 .git 只做在合批編譯」,並排到第三段處理,所以不阻擋放行。

引句:「擋 .git 只做在合批編譯、沒進共用路徑判法」

總結:最高等級是 minor
