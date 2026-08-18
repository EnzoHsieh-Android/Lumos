---
type: project
status: doing
created: 2026-08-18
updated: 2026-08-18
tags:
  - type/project
  - status/doing
  - scope/graph-governance
aliases:
  - slim update
related:
  - "[[Projects/公開精簡版_計劃]]"
summary: |
  FLOW:update_cmd.py(slim/update_cmd.py)模板(get.sh 冪等語意包成指令)→slim-gen 生成期拼接(main() 前置攔截+函式;先於 ast.parse 自檢)→產物 lumos update=pull ~/.lumos-slim(--ff-only)→跑 dest/install.py(=slim/install.py)--force --tool-only(只更新工具,永不碰專案層 CLAUDE.md)
  KEY:--tool-only=跨版本穩定介面(合約候選,工廠測試長駐釘);全函式 try/except→rc2 fail loud;update 必須為第一參數(--vault 等全域旗標前置=argparse invalid choice);裸打 lumos 回退 argparse usage(--help 不列 update,README 為文件面)
  KEY:凍結聲明作廢——`slim/README.md`+install.py 執行期輸出(.py/.sh/.ps1)全掃五關鍵詞文字釘;slim-scan 白名單+=update、舊豁免刪
  KEY:hooks=隨包 opt-in 檔案(install.py 永不裝,非目標不變);回填來源釘 GitHub main 6e249eb;複製清單補 hooks 與 WINDOWS-NOTES.md 兩項;發行同步=~/Citrus_Lumos 先 git pull 再 diff(stale clone 誤判活例)
  TEST:九組測試見 body 測試策略節;Windows 自我覆寫(產物 lumos 無副檔名——原 spec 誤稱 lumos.py 已修——與 lumos.cmd 批次 shim)未真機驗如實標
---

> 白話:精簡版目前是「凍結快照」——沒有 update 指令,想更新只能重跑一行安裝(它本來就冪等:已裝過→git pull→重裝)。使用者裁示(2026-08-18):把這條路包成 `lumos update`,拉精簡版自己的 repo 更新。凍結聲明隨之作廢,README 相關段落同步修真。順帶治好工廠漂移:hooks/ 與 README 的改動只活在 Citrus_Lumos 發行 repo、工廠端(slim/)沒有,生成器複製清單也漏檔。

## 緣起與裁示

- 使用者問「精簡版跑 lumos update 會拉到哪版」→ 查證:精簡版根本無此指令(25 支白名單外),README 凍結聲明明文「不是發布通道」。使用者裁示:做上去,語意=pull 精簡版。
- **工廠漂移(本案順帶修)**:①Citrus_Lumos 的 `hooks/` 目錄(pre-commit/post-commit)只存在發行 repo,`slim/` 無、slim-gen 複製清單無——下次再生成即蒸發;②2026-08-18 README hooks 章同型(直接推在發行 repo);③`WINDOWS-NOTES.md` 在 slim/ 有但複製清單漏列(靠手動同步)。

PRIOR-ART: ① 最小解層級——更新機制**已存在**:`get.sh`/`get.ps1` 冪等(固定落點 `~/.lumos-slim` 已存在→`git pull --ff-only`→重跑安裝器)。`lumos update`=把同一條路包成指令:pull 固定落點+`python install.py --force --tool-only`。復用既有三件(固定落點契約/安裝器自定位/--force 覆寫)+**一個新旗標**(`--tool-only`,std-r1 折入後不再宣稱「零新邏輯」——它是本案唯一的新安裝器行為)。② 世界解過沒——self-updating CLI 標準型(rustup self update/brew update);本案更簡:委派給既有安裝器。③ 裁定=**borrow-design**(復用自家 get 腳本語意)。

## 設計

### S1 `_slim_update()`(模板檔 `slim/update_cmd.py`,slim-gen 拼接進產物)

精簡版 CLI 是生成物(slim-gen 白名單手術),完整版的 `update` 是另一件事(vendored 工具組更新)不可白名單保留——slim 專屬指令走**生成期拼接**:

- 模板內容(stdlib only):`_slim_update()` 函式——①定位固定落點 `Path.home()/".lumos-slim"`(兩平台同,與 get.sh/get.ps1 契約一致);②`.git` 不存在→rc2 fail loud+指路(手動 clone 安裝者→自己 pull+重跑 install;或重跑一行安裝);③無 git 指令→rc2;④`git -C <dest> pull --ff-only`,失敗→rc2 印 stderr 尾段(本地改動/非 ff 的訊息與 get.sh 同語意);④b pull 後檢查 `dest/install.py` 存在,缺→rc2(std-r1 外家:repo 結構異常時 subprocess 直炸 FileNotFoundError 違反 fail loud);⑤跑 `[sys.executable, dest/install.py, "--force", "--tool-only"]`,回其 rc。★`--tool-only` 為本案新增的 install.py 旗標(r1 light blocker 折入):只做「複製 CLI+複製 skills」,**跳過專案根守衛與 CLAUDE.md sentinel 合併**——install.py 原每跑必動 cwd 的 CLAUDE.md(該行為是給「cd 進專案手動安裝」設計的),update 直呼會either被守衛拒絕(cwd 非專案)or 非預期改寫使用者當前專案的 CLAUDE.md(install.py docstring 記載的同型真實事故)。update=更新工具本身,永不碰專案層★。★**全函式包 `try/except Exception`→印「update 失敗(環境): <err>」rc2**(std-r1 s2:`Path.home()` 於 HOME 未設+passwd 無對應時拋 RuntimeError,入口 `sys.exit(main())` 無外層防護→裸 traceback 違反「全路徑 fail loud rc2」;包住後仍 fail loud、不吞訊息)★。★**`--tool-only` 為跨版本穩定介面(合約候選)**:install.py 旗標判讀是寬鬆 `in argv`(未知旗標靜默忽略)——未來若拿掉/改名,已布署舊 CLI 的 update 會**靜默退回完整安裝**重演 blocker①;防線=install.py 內註解明文穩定介面+測試⑥(真 install.py --tool-only 案)長駐工廠釘住★。
- slim-gen 拼接兩處:①產物 `def main():` 行後插入 argv 前置攔截(**`len(sys.argv) > 1 and sys.argv[1] == "update"`** → `return _slim_update()`——攔在 argparse 前,免動子命令註冊手術;★長度守衛是硬規格,r1 light blocker:裸打 `lumos` 若直讀 argv[1] 會 IndexError traceback;裸打時攔截短路、**回退** argparse 原友善 usage(std-r1 外家措辭修正:非「取代」)★。★已知限制明文(std-r1 兩席):update 必須為**第一個參數**——`lumos --vault X update` 之類全域旗標前置會落 argparse「invalid choice」錯誤(fail loud 非 crash,update 不吃任何旗標,文件明講)★);②`if __name__` 前拼入模板全文。模板檔不存在→生成硬失敗(fail loud,防靜默漏拼)。★**拼接必須發生在既有 `ast.parse(new_text)` 語法自檢之前**(std-r1 整合席:自檢在寫檔前防手術語法洞,拼接若在其後=模板縮排/語法錯直接出貨、使用者端才炸 SyntaxError——順序是硬規格,壞模板→生成 rc1 不出貨)★。
- **誠實面**:argv 攔截使 `lumos --help` 不列 update——README〈更新〉節為其文件面;Windows 自我覆寫:被覆寫的是**兩個檔**——`lumos`(python 原始碼,無副檔名;直譯器讀完即關,理論安全)與 **`lumos.cmd` 批次 shim**(★cmd.exe 對批次檔逐位元組續讀,執行中被覆寫是已知危害型;本 shim 極短且 python 呼叫為末行,風險低但**與 .py 是不同的技術問題**,std-r1 兩席修正原「lumos.py」誤稱與單檔敘述★);**本輪無真機 Windows 驗證**,README Windows 驗證表如實標未驗。

### S2 slim-gen 複製清單補齊+hooks 回填工廠

- `slim/` 新增 `hooks/`——★決策脈絡明文(std-r1 兩席質疑「與『不裝 hook』裁定衝突」,以遠端現況反證後補述)★:hooks=**隨包交付的 opt-in 檔案,install.py 永不安裝/不設 hooksPath**(該非目標不變,與 install.py docstring 一字不衝——「交付檔案」≠「安裝動作」);啟用=使用者自掛,README〈選配〉章(2026-08-18 已推遠端)為其文件面;發行 repo 的 hooks 檔頭同日已修真為 opt-in 指引。**回填來源釘死=GitHub main `6e249eb`**(★勿用本機任意 clone——`~/Citrus_Lumos` 實測落後於遠端(停在 08-14),std-r1 整合席即因讀 stale clone 誤判 hooks 為「被裁定砍掉的殘餘」——同步/查證前先 `git pull`★)。hooks 檔案 mode bit:slim/hooks/* 以 +x 入庫(copytree copy2 保留),測試斷言 dist 產物兩支 hook 可執行位元。複製清單 += `"hooks"`、`"WINDOWS-NOTES.md"`、`"update_cmd.py"`?★update_cmd.py 是生成期模板非交付物,**不進**複製清單(拼進 CLI 即可,包裡多一份=雙真相)★。
- README 真相源=slim/README.md:以 Citrus_Lumos 現行版(含 hooks 章)為底回填,再加本案改動(見 S3)。

### S3 README 修真(凍結→有更新通道)

- 〈凍結聲明〉整段改寫為〈更新方式〉:`lumos update` 一行(限一行安裝的固定落點;手動 clone 者指路)或重跑一行安裝;拿掉「不會有更新」;保留「出問題可直接改單檔原始碼」精神,補「改過的話 update 的 --ff-only 會拒絕覆蓋,屬保護不是壞掉」。
- 「本版沒有的指令」警語段:`lumos update` 從例舉中移除(改留 init/self-audit/signoff),並註明 update 自本版起存在。
- 散落掃關鍵詞(★std-r1 擴後全貌,與測試 4 文字釘一字對齊,r1 迷你核對補★):「不會有更新」「凍結快照」「不是發布通道」「不會有真正的新版本可拉」「〈凍結聲明〉」(掃描時另以裸詞「凍結」「update」廣撈人工判)——★範圍=`slim/` 全目錄(README+所有 .py/.sh/.ps1 的執行期輸出),非僅 README(r1 light major:install.py 安裝結束印「凍結快照…不會有更新」,update 跑完給使用者看自打臉訊息)★;install.py 該行改為「更新:`lumos update`(或重跑一行安裝)」。

### S4 發行同步

slim-gen 重生成 → dist/ → 內容同步進 Citrus_Lumos clone(**路徑釘=`~/Citrus_Lumos`;同步與任何 diff 查證前必先 `git pull` 至遠端最新**——std-r1 整合席以 stale clone 誤判 hooks 沿革即為活例)→ push。發行 repo 與 dist 的差異收斂到零(治漂移的驗收=diff 乾淨,結果記 Verification)。

### 範圍刀(明確不做)

- **不動 install.py 的「不裝任何 hook/不設 core.hooksPath」非目標**(hooks 僅隨包,啟用恆為使用者 opt-in);不動完整版 `cmd_update` 一個字;不做版本號/changelog 機制;不做自動更新檢查;不做 Windows 真機驗證(標未驗);不動 get.sh/get.ps1(它們已是想要的語意)。

## 測試策略(TDD,先紅後綠;t_slim_* 既有慣例)

1. `t_slim_update_injection`:slim-gen 真跑→產物含 `_slim_update` 定義+main() 攔截行;模板檔缺席→生成 rc 非 0(fail loud 釘)。
2. `t_slim_update_behavior`:產物以假 HOME 執行——①無 `~/.lumos-slim`→rc2+指路訊息;②fixture 造本地 git 源+clone 為固定落點、塞假 install.py(印標記)→`lumos update` rc0+標記出現(pull+重裝真的跑)+★前置斷言:假 install.py 被以 --force 呼叫★;③dest 有本地未提交改動→pull 失敗 rc2(--ff-only 保護釘);④**PATH 無 git→rc2**(空 PATH 環境跑,pre-flight 補:S1③分支原無測);⑤**--tool-only 傳遞釘**(假 install.py 斷言收到 --force 與 --tool-only 兩旗標);⑥**真 install.py --tool-only 案**:任意 cwd(非專案根 tmp)跑→rc0 且 CLAUDE.md 未被建立/未被改(blocker 修的翻紅釘:拿掉 --tool-only 支援,此測必紅——守衛拒絕或檔案被動);⑦**裸打 `lumos`(無參數)→argparse usage+rc2,無 traceback**(blocker 2 回歸釘);⑧**pull 後 install.py 不存在→rc2**(fixture 把 dest 裡的 install.py 刪掉——S1④b 存在預檢的負向案,std-r1 迷你核對抓到唯一沒閉環到測試的折入項)。
3. `t_slim_gen` 既有案不倒退;複製清單補檔後 dist 含 hooks/WINDOWS-NOTES(斷言入 t_slim_update_injection 或既有 t_slim_gen 擴充)。
4. **文字釘**(pre-flight 補+r1+std-r1 兩席擴):斷言 `slim/README.md` 含「lumos update」與〈更新方式〉;README 與 `slim/install.py` **均不含**「不會有更新」「凍結快照」「不是發布通道」「不會有真正的新版本可拉」「〈凍結聲明〉」(★最後兩個是 std-r1 雙席獨立抓到的字面逃逸:README 第 161 行殘留句逐字避開原釘,且其指向的章節標題改名後成懸空引用★)——任一回歸即翻紅;實作時先真 grep slim/ 全目錄逐命中人工判修,釘只守回歸。
5. **S4 發行同步驗收=人工步驟,無 CI 著落(誠實明記)**:發行 repo 非本 repo 管轄,驗收指令 `diff -r dist/ <Citrus_Lumos clone>`(排除 .git)結果記入 Verification;不立自動守衛。
6. **slim-scan 豁免修真**(std-r1 整合席):update 落地後從「已移除指令」變「存在指令」——`slim-scan` 白名單 += update、**刪除** `t_slim_readme_assertions` 的 `("update","prefixed")` 舊豁免(該豁免為「本包沒有 update」的舊誠實聲明而設,語意已反轉;留著=守衛對新內容永久失能)。
7. **拼接語法案**(std-r1 整合席):故意餵語法壞的模板→slim-gen rc1 不出貨(ast.parse 自檢覆蓋拼接的翻紅釘);**hooks 執行位元案**:dist/hooks/* 兩支 +x 斷言。
8. **Path.home 防護案**(std-r1 s2):以模組載入 dist 產物,monkeypatch `Path.home` 拋 RuntimeError→`_slim_update()` 回 2 不拋例外。
9. **全域旗標前置案**:`lumos --vault X update`→argparse invalid choice 錯誤訊息+rc2,無 traceback(已知限制釘)。

## 實務隱患

- **通用三問**:併發——update 非併發場景,git 自身鎖保護;效能——冷路徑;資源——subprocess 皆 run() 同步回收。
- **風險類自答**:對外發行面——最壞後果=使用者機器上更新失敗;緩解=全路徑 fail loud rc2+指路,--ff-only 拒絕覆蓋本地改動(保護語意同 get.sh)。自我覆寫風險:POSIX 安全(檔案已編譯進程);Windows 未驗如實標。已排除:金流/對外送出(無——只拉不推)/prod 不可逆(無,git 可回)。
- **雙真相殘留**:發行 repo 被人直接改(如本次 hooks 前例)仍會漂——本案治存量,增量防不住(觀測=下次同步 diff 會現形;不立機械守衛,發行 repo 非本 repo 管轄)。

## 合約候選(收斂時複核,候選≠已標)

- 「update 只認固定落點 `~/.lumos-slim`,手動 clone 不猜路徑」——與 get 腳本的固定落點契約同源。
- 「install.py 恆接受 `--tool-only`(跨版本穩定介面;拿掉/改名=已布署舊 CLI 靜默退回完整安裝)」——std-r1 s2 折入。

## 審計修正紀錄

- **r1(2026-08-18,light 單席 generalist-sonnet;收貨三道全過)**:blocker×2/major×1 全折——①[blocker]update 直呼 install.py 會觸發 per-project CLAUDE.md 注入(cwd 像專案=非預期改寫/不像=被守衛拒絕)→新增 `--tool-only` 旗標只更新工具永不碰專案層,補真 install.py 測試+翻紅釘。②[blocker]argv[1] 裸讀使裸打 lumos 崩潰→長度守衛硬規格+回歸釘。③[major]install.py 執行期「凍結快照」訊息漏修→散落掃範圍擴 slim/ 全目錄+文字釘擴 install.py。★light ratchet 觸發:存活 ≥major→升 standard panel,續審 loop id=精簡版update指令-std,本輪不洗回★。

- **std-r1(2026-08-18/19,ratchet 升級後 panel:3 sonnet(通才/更新邊界/整合)+Gemini 外家;收貨三道全過)**:去重後 13 條,**11 折 2 駁**。折:①hooks 決策脈絡明文+回填來源釘遠端 6e249eb+mode bit 斷言(s1 major+s3 blocker 以 stale clone 反證降級後併,其衍生要求全採)②README 161 行字面逃逸+懸空引用(s1+s2 雙席)→文字釘擴五關鍵詞③--tool-only 跨版本合約(s2)→合約候選+工廠測試長駐④Path.home RuntimeError→全函式 try/except rc2(s2)⑤slim-scan 豁免語意反轉(s3)→白名單改+舊豁免刪⑥拼接先於 ast.parse 自檢=硬規格+壞模板案(s3)⑦全域旗標前置限制明文+測試(外家+s1)⑧Windows 揭露修真(lumos 無副檔名+cmd shim 批次語意,外家+s2+s1)⑨install.py 存在預檢(外家)⑩「取代」措辭(外家)⑪S4 先 pull+路徑釘(s3,其日期質疑經遠端 log 反證——6e249eb 確為 2026-08-18,席位讀 stale clone 所致)。駁:⑫main 回傳值被丟(外家)——`sys.exit(main())` 源+產物實證;⑬影子更新(外家)——update 語意=更新全域安裝通道,執行中行程屬舊版為一切更新器通性,手動 clone 已於②指路。
- **std-r1 折入迷你核對(2026-08-19,便宜席,4 命中全修,不算 loop findings)**:①PRIOR-ART「零新邏輯/只提 --force」未跟上 --tool-only→同步②測試編號 5 亂序→重排連號③S3 關鍵詞清單未展開五詞全貌→與測試 4 一字對齊④install.py 存在預檢缺負向測試案→測試 2 補⑧。
- **pre-flight(2026-08-18,機械排乾,不算 loop findings)**:3 命中全修(全在測試收口)——①S1③無 git 分支補測(behavior④)②S3 README 修真補機械釘(測試 4:凍結字樣回歸翻紅)③S4 diff 驗收明記為人工步驟+Verification 留痕,不假裝有 CI。現況宣稱五條(get 冪等/落點/自定位/複製清單缺檔/anchor 唯一性)全數核實為真。
