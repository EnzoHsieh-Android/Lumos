severity: clean

## 逐類檢查

1. 不可信輸入流到危險操作:已看,無 finding。
   - NFD 重讀(_drift_cat_nfc)把樹清單來的路徑組成 `<版本>:<路徑>`,經 stdin 餵給 `git cat-file --batch`,不進 shell、不進 argv,沒有 git 參數注入面。
   - 路徑含換行時 _nodehome_cat_blobs 整批回 None,結果是判不了。這條在 check 走「要處理」,只會讓推送多擋,不會放行。
   - 名稱進正規式時用 re.escape。ast 只 parse 不執行,沒有 eval 或反序列化。
   - 表態指令只印固定集合裡的 kind。
   - file: `scripts/lumos:23092`(_nodehome_cat_blobs,含換行整批 None)
2. 登入與權限、推送閘能否被推送內容關掉:已看,無 finding。
   - 讓某支檔讀不出來,或讓 ast 丟 MemoryError,現在的結果是「判不了」或退回正則。
   - check 把判不了算要處理,fail-closed,推的人拿不到繞過。
   - 開關可被同一個提交改成 off,這是既有 RULE 已記載的界線,不在本差異範圍。
3. 密鑰與個資:已看,無 finding。讀到的程式檔與筆記全文只拿來比對名稱,發現訊息只印路徑、行號與該行條件原文,不印檔案內容,也不寫進治理帳(note 只含筆數與判不了說明)。
4. 加密與傳輸:已看,無。
5. 執行邊界:已看,無 finding。
   - 沒有執行不可信位置的檔。
   - git 呼叫沿用 `-C` 與 `--`,`-e` 的既有寫法。
   - 工作目錄模式(disk)讀檔前先過 self.files 成員檢查,路徑穿越由 _probe_bad_path 與「.」新增的拒絕擋掉。
   - 已看:disk 模式對符號連結指向 repo 外的檔仍會讀。內容不外流,只影響是否有某名稱的判定,而且這條讀法在本差異之前就有,只是 decode 改成 utf-8-sig,不構成可利用的洞,不報。
6. 行動端:不適用,已看,無。

最高:clean,blocking 共 0 條。
