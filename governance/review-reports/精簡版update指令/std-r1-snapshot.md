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
---

> 白話:精簡版目前是「凍結快照」——沒有 update 指令,想更新只能重跑一行安裝(它本來就冪等:已裝過→git pull→重裝)。使用者裁示(2026-08-18):把這條路包成 `lumos update`,拉精簡版自己的 repo 更新。凍結聲明隨之作廢,README 相關段落同步修真。順帶治好工廠漂移:hooks/ 與 README 的改動只活在 Citrus_Lumos 發行 repo、工廠端(slim/)沒有,生成器複製清單也漏檔。

## 緣起與裁示

- 使用者問「精簡版跑 lumos update 會拉到哪版」→ 查證:精簡版根本無此指令(25 支白名單外),README 凍結聲明明文「不是發布通道」。使用者裁示:做上去,語意=pull 精簡版。
- **工廠漂移(本案順帶修)**:①Citrus_Lumos 的 `hooks/` 目錄(pre-commit/post-commit)只存在發行 repo,`slim/` 無、slim-gen 複製清單無——下次再生成即蒸發;②2026-08-18 README hooks 章同型(直接推在發行 repo);③`WINDOWS-NOTES.md` 在 slim/ 有但複製清單漏列(靠手動同步)。

PRIOR-ART: ① 最小解層級——更新機制**已存在**:`get.sh`/`get.ps1` 冪等(固定落點 `~/.lumos-slim` 已存在→`git pull --ff-only`→重跑安裝器)。`lumos update`=把同一條路包成指令:pull 固定落點+`python install.py --force`。零新邏輯,復用既有三件(固定落點契約/安裝器自定位/--force 覆寫)。② 世界解過沒——self-updating CLI 標準型(rustup self update/brew update);本案更簡:委派給既有安裝器。③ 裁定=**borrow-design**(復用自家 get 腳本語意)。

## 設計

### S1 `_slim_update()`(模板檔 `slim/update_cmd.py`,slim-gen 拼接進產物)

精簡版 CLI 是生成物(slim-gen 白名單手術),完整版的 `update` 是另一件事(vendored 工具組更新)不可白名單保留——slim 專屬指令走**生成期拼接**:

- 模板內容(stdlib only):`_slim_update()` 函式——①定位固定落點 `Path.home()/".lumos-slim"`(兩平台同,與 get.sh/get.ps1 契約一致);②`.git` 不存在→rc2 fail loud+指路(手動 clone 安裝者→自己 pull+重跑 install;或重跑一行安裝);③無 git 指令→rc2;④`git -C <dest> pull --ff-only`,失敗→rc2 印 stderr 尾段(本地改動/非 ff 的訊息與 get.sh 同語意);⑤跑 `[sys.executable, dest/install.py, "--force", "--tool-only"]`,回其 rc。★`--tool-only` 為本案新增的 install.py 旗標(r1 light blocker 折入):只做「複製 CLI+複製 skills」,**跳過專案根守衛與 CLAUDE.md sentinel 合併**——install.py 原每跑必動 cwd 的 CLAUDE.md(該行為是給「cd 進專案手動安裝」設計的),update 直呼會either被守衛拒絕(cwd 非專案)or 非預期改寫使用者當前專案的 CLAUDE.md(install.py docstring 記載的同型真實事故)。update=更新工具本身,永不碰專案層★。
- slim-gen 拼接兩處:①產物 `def main():` 行後插入 argv 前置攔截(**`len(sys.argv) > 1 and sys.argv[1] == "update"`** → `return _slim_update()`——攔在 argparse 前,免動子命令註冊手術;★長度守衛是硬規格,r1 light blocker:裸打 `lumos` 若直讀 argv[1] 會 IndexError traceback,取代原本 argparse 的友善 usage★);②`if __name__` 前拼入模板全文。模板檔不存在→生成硬失敗(fail loud,防靜默漏拼)。
- **誠實面**:argv 攔截使 `lumos --help` 不列 update——README〈更新〉節為其文件面;Windows 自我覆寫(install.py copyfile 蓋住執行中的 lumos.py)理論上可行(python 編譯後不鎖檔)但**本輪無真機 Windows 驗證**,README Windows 驗證表如實標未驗。

### S2 slim-gen 複製清單補齊+hooks 回填工廠

- `slim/` 新增 `hooks/`(內容=Citrus_Lumos 現行兩支,含 2026-08-18 檔頭修真——發行 repo 是它們目前唯一真身,搬回工廠);複製清單 += `"hooks"`、`"WINDOWS-NOTES.md"`、`"update_cmd.py"`?★update_cmd.py 是生成期模板非交付物,**不進**複製清單(拼進 CLI 即可,包裡多一份=雙真相)★。
- README 真相源=slim/README.md:以 Citrus_Lumos 現行版(含 hooks 章)為底回填,再加本案改動(見 S3)。

### S3 README 修真(凍結→有更新通道)

- 〈凍結聲明〉整段改寫為〈更新方式〉:`lumos update` 一行(限一行安裝的固定落點;手動 clone 者指路)或重跑一行安裝;拿掉「不會有更新」;保留「出問題可直接改單檔原始碼」精神,補「改過的話 update 的 --ff-only 會拒絕覆蓋,屬保護不是壞掉」。
- 「本版沒有的指令」警語段:`lumos update` 從例舉中移除(改留 init/self-audit/signoff),並註明 update 自本版起存在。
- 散落掃關鍵詞:凍結/不會有更新/不是發布通道/update——★範圍=`slim/` 全目錄(README+所有 .py/.sh/.ps1 的執行期輸出),非僅 README(r1 light major:install.py 安裝結束印「凍結快照…不會有更新」,update 跑完給使用者看自打臉訊息)★;install.py 該行改為「更新:`lumos update`(或重跑一行安裝)」。

### S4 發行同步

slim-gen 重生成 → dist/ → 內容同步進 Citrus_Lumos clone(hooks/README 此後由管線攜帶)→ push。發行 repo 與 dist 的差異收斂到零(治漂移的驗收=diff 乾淨)。

### 範圍刀(明確不做)

- 不動完整版 `cmd_update` 一個字;不做版本號/changelog 機制;不做自動更新檢查;不做 Windows 真機驗證(標未驗);不動 get.sh/get.ps1(它們已是想要的語意)。

## 測試策略(TDD,先紅後綠;t_slim_* 既有慣例)

1. `t_slim_update_injection`:slim-gen 真跑→產物含 `_slim_update` 定義+main() 攔截行;模板檔缺席→生成 rc 非 0(fail loud 釘)。
2. `t_slim_update_behavior`:產物以假 HOME 執行——①無 `~/.lumos-slim`→rc2+指路訊息;②fixture 造本地 git 源+clone 為固定落點、塞假 install.py(印標記)→`lumos update` rc0+標記出現(pull+重裝真的跑)+★前置斷言:假 install.py 被以 --force 呼叫★;③dest 有本地未提交改動→pull 失敗 rc2(--ff-only 保護釘);④**PATH 無 git→rc2**(空 PATH 環境跑,pre-flight 補:S1③分支原無測);⑤**--tool-only 傳遞釘**(假 install.py 斷言收到 --force 與 --tool-only 兩旗標);⑥**真 install.py --tool-only 案**:任意 cwd(非專案根 tmp)跑→rc0 且 CLAUDE.md 未被建立/未被改(blocker 修的翻紅釘:拿掉 --tool-only 支援,此測必紅——守衛拒絕或檔案被動);⑦**裸打 `lumos`(無參數)→argparse usage+rc2,無 traceback**(blocker 2 回歸釘)。
3. `t_slim_gen` 既有案不倒退;複製清單補檔後 dist 含 hooks/WINDOWS-NOTES(斷言入 t_slim_update_injection 或既有 t_slim_gen 擴充)。
4. **文字釘**(pre-flight 補+r1 擴):斷言 `slim/README.md` 含「lumos update」與〈更新方式〉、不含「不會有更新」;**且 `slim/install.py` 原始碼不含「不會有更新」**(執行期輸出同掃)——凍結字樣回歸即翻紅。
5. **S4 發行同步驗收=人工步驟,無 CI 著落(誠實明記)**:發行 repo 非本 repo 管轄,驗收指令 `diff -r dist/ <Citrus_Lumos clone>`(排除 .git)結果記入 Verification;不立自動守衛。

## 實務隱患

- **通用三問**:併發——update 非併發場景,git 自身鎖保護;效能——冷路徑;資源——subprocess 皆 run() 同步回收。
- **風險類自答**:對外發行面——最壞後果=使用者機器上更新失敗;緩解=全路徑 fail loud rc2+指路,--ff-only 拒絕覆蓋本地改動(保護語意同 get.sh)。自我覆寫風險:POSIX 安全(檔案已編譯進程);Windows 未驗如實標。已排除:金流/對外送出(無——只拉不推)/prod 不可逆(無,git 可回)。
- **雙真相殘留**:發行 repo 被人直接改(如本次 hooks 前例)仍會漂——本案治存量,增量防不住(觀測=下次同步 diff 會現形;不立機械守衛,發行 repo 非本 repo 管轄)。

## 合約候選(收斂時複核,候選≠已標)

- 「update 只認固定落點 `~/.lumos-slim`,手動 clone 不猜路徑」——與 get 腳本的固定落點契約同源。

## 審計修正紀錄

- **r1(2026-08-18,light 單席 generalist-sonnet;收貨三道全過)**:blocker×2/major×1 全折——①[blocker]update 直呼 install.py 會觸發 per-project CLAUDE.md 注入(cwd 像專案=非預期改寫/不像=被守衛拒絕)→新增 `--tool-only` 旗標只更新工具永不碰專案層,補真 install.py 測試+翻紅釘。②[blocker]argv[1] 裸讀使裸打 lumos 崩潰→長度守衛硬規格+回歸釘。③[major]install.py 執行期「凍結快照」訊息漏修→散落掃範圍擴 slim/ 全目錄+文字釘擴 install.py。★light ratchet 觸發:存活 ≥major→升 standard panel,續審 loop id=精簡版update指令-std,本輪不洗回★。

- **pre-flight(2026-08-18,機械排乾,不算 loop findings)**:3 命中全修(全在測試收口)——①S1③無 git 分支補測(behavior④)②S3 README 修真補機械釘(測試 4:凍結字樣回歸翻紅)③S4 diff 驗收明記為人工步驟+Verification 留痕,不假裝有 CI。現況宣稱五條(get 冪等/落點/自定位/複製清單缺檔/anchor 唯一性)全數核實為真。
