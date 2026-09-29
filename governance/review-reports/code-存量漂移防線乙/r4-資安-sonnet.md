severity: minor

## F1 判不了說明把被推送的檔名原樣印到終端(推論)
severity: minor
blocking: 否 — 縱深防禦,推論,無可直接利用的執行或外洩
引句:「return (":" + "、".join(bad[:5]) + (f" 等 {len(bad)} 支" if len(bad) > 5 else "")) if bad else ""」
1. 誰:能讓提交進被檢查範圍的貢獻者;從哪裡:提交裡一支讀不出內容的檔(例如子模組、非檔案物件)的路徑。
2. 送什麼:路徑含終端控制字元(如 ESC 序列,換行除外,換行在批次讀那層已整批擋掉)。
3. 走到 _drift_bad_note,bad_paths 回傳的路徑未經跳脫,進判不了說明、印給推送的人。
4. 拿到:終端顯示被改寫(蓋掉別的輸出行)。只影響顯示,推論,未實測。
file: `scripts/lumos:22792`

## 逐類檢查
1. 不可信輸入流到危險操作:已看。cat-file --batch 的輸入是 ls-tree 回的內容編號(git 產出的十六進位),退回用的「版本:路徑」仍有 _nodehome_cat_blobs 的換行整批拒絕,且走 stdin、非 argv,無參數注入;tokenize 只做詞法掃描不執行、TokenError 與 SyntaxError 與 ValueError 都接住,無 eval/exec/反序列化。無 finding。
2. 閘被推送內容關掉或繞過:已看。刻意寫超長邏輯行(超過 2 萬詞、檔大於 15 萬字元)只會讓該檔退回正則(較寬鬆認定),屬推送者本來就能控制的筆記與程式,沒有新增能力,無 finding。
3. 密鑰與個資:已看。讀到的檔內容不印出,只印路徑(見 F1)。無其他 finding。
4. 加密與傳輸:已看,無。
5. 執行邊界:已看。不執行被推送位置的檔;git 以固定 argv 呼叫;內容編號讀取不經工作目錄故無符號連結或路徑穿越(disk 模式的 is_symlink 排除在上一版)。無 finding。
6. 行動端:已看,無。

最嚴重等級 minor,blocking 共 0 條。
