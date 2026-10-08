severity: clean

# 邊界-sonnet 第 2 輪報告(鏡頭:邊界與輸入)

全部在 `git clone --shared` 的 clone(HEAD 94c1e82f)實跑,沒有 finding。實跑過的邊界如下,都行為正確:

1. repo 根在符號連結底下:從 symlink 路徑 cd 進去不給 --repo 跑 reread-prepare,工作目錄建得起來、項目檔產生、資料夾守衛不誤擋。
2. .lumos 不存在:第一次建立、補 .gitignore 正常。
3. .lumos 是檔案:擋下「不是資料夾」。.lumos 是懸空符號連結:擋下,且連結目標沒被建出來。
4. 控制字元檔名:Tab、結尾 DEL(0x7f)、C1(U+0085)都進 ctrl 被跳過並在 prepare 與 check 印一句(印出前已清成空格);非 UTF-8 檔名(bad\xff,用 update-index 塞進索引)不在 ctrl 內、照常產項目檔、check 寫帳不當掉、reread-record 收得下、提交後 check 與 prepare 都算「已對照」。
5. 中文加空白檔名:產檔、record、提交、check 認得已對照,指紋口徑一致。
6. --all 與已對照混合:已提交紀錄齊全時 prepare 預設印「已對照 4 篇…略過」不產檔;加 --all 產 4 份。
7. _nodehome_side 的 deadline:已過期回 None;讀到一半過期(每篇 sleep 0.4、截止 0.5)回 None;有 share 且沒變動的節點不讀、不誤判逾時;不給 deadline 行為不變。
8. 留痕有效性簿記判法(直接呼叫 _codeloop_record_valid):簿記資料夾裡的中文加空白 .md 有效;同處 .py 與 Tab 檔名 .sh 失效;換行檔名的 .md 有效;程式檔改名搬進簿記資料夾(.md 或 .txt)失效(--no-renames 生效);reread-verdicts 下 .json 有效;大寫 .PY 沿用既有大小寫敏感判法、有效(跟其他四份副檔名清單同口徑,非本次引入)。
9. 實際 repo 內 governance/code-loop、review-reports、replay、note-verdicts 已追蹤檔沒有任何屬於程式副檔名的,新收緊不會讓現有流程的留痕誤失效。

未報項目(給不出具體失敗場景):U+2028/U+2029、雙向控制字元(U+202E)檔名不在 _NOTE_REREAD_CTRL_RE 內,但本段沒有任何 splitlines 或終端會解讀它們的路徑,實測項目檔與 record 都正常,不算缺陷。

最高等級:clean
