# 精簡版update指令 std-r1 編排者對帳報告(carrier;light r1 ratchet 升級後 panel)

四席(3 sonnet 分鏡頭+Gemini Flash 外家,單發 REST)findings 去重 13 條,**11 折 2 駁**。s3 整合席一條 blocker 經編排者以遠端 git 現況機械反證降級(其查證用了落後遠端五天的本機 stale clone——矛盾原文在 GitHub main 6e249eb 均已修掉),但其衍生的四個要求全數採納;該誤判本身轉化為 S4 的「先 pull 再查證」硬步驟(活教材)。逐條處置與錨定引句(逐字取自 std-r1-snapshot.md):

## 折入(11)

**f1 hooks 決策脈絡未明,與「刻意不裝 hook」聲明疑似衝突**(s1 major+s3 blocker 降級後併)
引句：「`slim/` 新增 `hooks/`(內容=Citrus_Lumos 現行兩支,含 2026-08-18 檔頭修真——發行 repo 是它們目前唯一真身,搬回工廠)」
處置=folded:明文 hooks=隨包 opt-in 檔案、install.py 永不裝(非目標不變);回填來源釘 GitHub main 6e249eb;範圍刀加「不動 install.py hooks 非目標」;mode bit 斷言入測試。

**f2 README 161 行字面逃逸+〈凍結聲明〉懸空引用**(s1+s2 雙席獨立)
引句：「散落掃關鍵詞:凍結/不會有更新/不是發布通道/update——★範圍=`slim/` 全目錄(README+所有 .py/.sh/.ps1 的執行期輸出),非僅 README」
處置=folded:文字釘擴五關鍵詞(含「不會有真正的新版本可拉」「〈凍結聲明〉」);實作先真 grep 逐修,釘守回歸。

**f3 --tool-only 無跨版本相容合約(寬鬆 in-argv 判讀,拿掉=舊 CLI 靜默退回完整安裝)**(s2)
引句：「update=更新工具本身,永不碰專案層★」
處置=folded:合約候選補列;install.py 註解明文穩定介面;測試⑥真 install.py 案長駐工廠釘。

**f4 Path.home() RuntimeError 裸 traceback**(s2)
引句：「緩解=全路徑 fail loud rc2+指路」
處置=folded:_slim_update 全函式 try/except Exception→rc2 印錯;測試 8(monkeypatch 拋→rc2 不拋例外)。

**f5 slim-scan 舊豁免語意反轉,守衛對新內容失能**(s3)
引句：「`lumos update` 一行(限一行安裝的固定落點;手動 clone 者指路)或重跑一行安裝」
處置=folded:slim-scan 白名單 += update;刪 `("update","prefixed")` 舊豁免;測試 6。

**f6 拼接與 ast.parse 自檢順序未定**(s3)
引句：「模板檔不存在→生成硬失敗(fail loud,防靜默漏拼)。」
處置=folded:拼接先於自檢=硬規格;測試 7 壞模板→rc1 不出貨。

**f7 全域旗標前置繞過攔截**(外家+s1)
引句：「產物 `def main():` 行後插入 argv 前置攔截(**`len(sys.argv) > 1 and sys.argv[1] == "update"`** → `return _slim_update()`——攔在 argparse 前,免動子命令註冊手術」
處置=folded:已知限制明文(update 必須為第一參數,前置旗標=argparse invalid choice fail loud)+測試 9。

**f8 Windows 自我覆寫揭露不精確(lumos.py 誤稱/漏 cmd shim 批次語意)**(外家+s2+s1 三席)
引句：「Windows 自我覆寫(install.py copyfile 蓋住執行中的 lumos.py)理論上可行(python 編譯後不鎖檔)但**本輪無真機 Windows 驗證**,README Windows 驗證表如實標未驗。」
處置=folded:檔名修正(lumos 無副檔名+lumos.cmd);批次檔逐位元組續讀語意差異明文;未驗照標。

**f9 install.py 存在性預檢缺失**(外家)
引句：「⑤跑 `[sys.executable, dest/install.py, "--force", "--tool-only"]`,回其 rc。」
處置=folded:④b pull 後檢查存在,缺→rc2。

**f10 「取代 argparse usage」措辭矛盾**(外家)
引句：「★長度守衛是硬規格,r1 light blocker:裸打 `lumos` 若直讀 argv[1] 會 IndexError traceback,取代原本 argparse 的友善 usage★)」
處置=folded:改「裸打時短路回退 argparse 原 usage」。

**f11 日期引註/clone 路徑質疑**(s3 兩條 minor 併)
引句：「②2026-08-18 README hooks 章同型(直接推在發行 repo)」
處置=folded(修正版):遠端 log 實證 6e249eb=2026-08-18(日期屬實,席位讀 stale clone);S4 釘路徑 ~/Citrus_Lumos+同步/查證前必先 git pull。

## 駁回(2)

**f12 main 回傳值被丟棄致 rc 靜默成功**(外家)
引句：「產物 def main(): 行後插入 argv 前置攔截(len(sys.argv) > 1 and sys.argv[1] == "update" → return _slim_update()——攔在 argparse 前,免動子命令註冊手術;★長度守衛是硬規格,r1 light blocker:裸打 lumos 若直讀 argv[1] 會 IndexError traceback,取代原本 argparse 的友善 usage★)」
處置=refuted:源檔與 dist 產物結尾均為 `sys.exit(main())`(grep 實證)——回傳值即退出碼。

**f13 影子更新(執行中程式未變=假象)**(外家)
引句：「①定位固定落點 Path.home()/".lumos-slim"(兩平台同,與 get.sh/get.ps1 契約一致);②.git 不存在→rc2 fail loud+指路(手動 clone 安裝者→自己 pull+重跑 install;或重跑一行安裝)」
處置=refuted:update 語意=更新全域安裝通道;執行中行程屬舊版為一切更新器通性(rustup/brew 同);手動 clone 情境②已指路。

## 收貨三道紀錄

quote-check 四席全數錨定(light r1 席 1 條半形冒號格式病機械正規化);refcheck 0 missing;seat-check unreported 各 1(快照路徑字串未貼,協議格式面)。

## 折入後衛生

fold-check 無 flag(summary 鏡像補齊);折入迷你核對另派(結果記審計修正紀錄)。
