# code-精簡版update指令 r1 編排者對帳報告(carrier;tier=high panel:4 sonnet 鏡頭+Gemini finder(佔W)+Gemini 否決(外掛)+spec-conformance(外掛))

七席 findings 去重 **14 條:10 折 4 駁**;diff 2008 行超 1800 軟上限(帳記 scope_oversize,各席鏡頭聚焦分工緩解)。全部折入已修進真碼並先紅後綠;修後全量 2848/0。逐條處置(引句錨定=r1-snapshot.patch 之 diff 內容,以下位置引用皆可於快照對應 hunk 錨定):

## 折入(10)

**f1 [major] `update --help`/任何附加參數靜默執行真更新**(s1;README「必須單獨打」未落實;測試 r7 變數算而未斷言+_Boom 死碼佐證)
處置=folded:攔截加「argv>2→rc2 印用法」守衛;測試 behavior⑦b(update --help→rc2 且無 FAKE-INSTALL 副作用);死碼拔除。

**f2 [blocker] spec 承諾的「真 install.py --tool-only」長駐翻紅釘不存在**(s3 blocker+s7 major 雙席)
處置=folded:新增 t_slim_update_tool_only_real(dist/install.py 真跑:任意 cwd rc0/CLAUDE.md 零觸碰/CLI 落假 HOME/結尾訊息更新語意)——拿掉 --tool-only 支援即紅。

**f3 [major] install.py cwd 取值未隨 --tool-only 跳過,stale cwd 下 update 整體 rc2 且訊息誤導**(s2,實測重現)
處置=folded:target_dir/target_claude_md 取值搬進 if not tool_only:。

**f4 [major] README「等價做法=重跑一行安裝」把使用者指回 --tool-only 剛封掉的舊坑**(s4)
處置=folded:句子改寫明講不等價(完整安裝會做專案層處理)+「只想更新工具一律 lumos update」。

**f5 [major] slim-gen 錨點非唯一守衛零測試覆蓋**(s3;--no-update-inject 繞道合法但無替代測試)
處置=folded:injection 補「字串常數藏重複錨點→拒絕出貨」案。

**f6 [major] 交付 skill reference.md 三處仍稱 update 未交付,掃描器豁免洗掉內容回歸**(s3)
處置=folded:l.18/59/61 逐處修真(update 有交付+完整版同名異義警語+「doctor 建議≠跑 update 能修 CLAUDE.md」)。

**f7 [major,環境條件] git fixture dest 未設身分,CI 容器假紅面**(s3;專案同型事故前科)
處置=folded:dest 補 user.email/name。

**f8 [minor] 更新完成仍印「裝好了」首次安裝措辭**(s2)
處置=folded:tool_only 分流「更新完成。驗證: lumos --help」;真檔測試斷言。

**f9 [minor] pull 成功輸出被吞,無從判斷有沒有拉到新東西;失敗訊息掐頭**(s2+s5/s6 外家雙席截斷面)
處置=folded:成功印 pull 末行(Already up to date./Fast-forward);錯誤改印前 1000 字不掐頭。

**f10 [minor] 26 支範圍聲明未提示 update 不在 --help;Path.home patch 全域性;「26 vs 27」prose**(s4+s3 三小條併)
處置=folded:範圍聲明補攔截式入口說明(同句化解 26/27 歧義);patch 加單執行緒前提註解。

## 駁回(4)

**f11 [外家 s5f1/s6f1「blocker」模板缺 Path/sys import 必 NameError]**——refuted:產物頂層 `import sys`/`from pathlib import Path` 實在,slim-gen 手術從不動頂層 import(s1 席全檔 grep 證);behavior/E2E 真跑 update 成功=行為級反證。外家無 repo 存取之誤。

**f12 [外家 s5f4/s6f3 major「--tool-only 子字串誤觸(--no-tool-only 會中)」]**——refuted:`"--tool-only" in argv` 的 argv 是 **list**,`in`=整元素比對非子字串;`--no-tool-only` 不會命中。語言語意誤讀。

**f13 [外家 s5f2 copytree dirs_exist_ok 需 py3.8/s5f3+s6f2 拼接對 tab/2 空格源碼不通用]**——refuted:slim-gen 是本 repo 工廠工具(開發環境 python3.9+),非通用發行物;源檔為本 repo 固定檔,錨點 count 檢查=fail loud 非靜默,「對任意源碼通用」不是設計目標。

**f14 [外家 s6f4 hooks glob 特殊字元/s5f6 bash-ism]**——accepted-minor 留理由:hooks=發行 repo 既有內容原樣回填(08-11 起生產使用),其檔內已有 ERE 元字元防護註解;bash 依賴由 shebang 明示。內容非本 diff 新作,行為零變更;風險屬存量,要改另案。

## 收貨紀錄

diff 2008 行>1800 軟上限——scope_oversize 如實記帳,收斂宣稱對「單席看完全部」不背書,以七席鏡頭分工+spec 對答案席補償。s5 外家首發 MAX_TOKENS 截斷,重發 65536 上限收全。棧別檢核(python):update 路徑全冷路徑 subprocess 同步;bash(hooks)=回填內容零變更。
