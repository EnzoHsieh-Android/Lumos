# Lumos 公開精簡版

這是知識圖譜工具 lumos 的**離職交接精簡版**——目的只有一個：讓接手的人能讀懂既有專案留下的知識圖譜（`docs/{project}-knowledge/`）。可讀是目標，可維護是加分，本包不設任何機械強制（不擋 commit、不擋 push、不裝任何 hook）。

## 怎麼裝

包裡有一支機器層安裝器，只做兩件事：①把 `lumos` 裝到 `~/.local/bin` ②把技能說明實體複製到 `~/.claude/skills/lumos-project-notes/`（不是 symlink，交付包搬走／刪掉後 skill 仍在）。

**一行安裝**（把交付包拉到固定落點 `~/.lumos-slim` 再自動執行安裝器）：

```bash
curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/get.sh | bash
```

不想 `curl | bash` 也可以，**兩行分開跑**（效果完全一樣，只是自己掌控每一步）：

```bash
git clone https://github.com/citrus-android-developer/Citrus_Lumos.git ~/.lumos-slim
~/.lumos-slim/install.sh
```

兩種方式都會把套件放在 `~/.lumos-slim`（見下方〈`~/.lumos-slim` 是什麼〉），再執行套件裡的安裝器；若目標（全域指令或 skill 目錄）已存在，加 `--force` 覆寫（skill 目錄會先備份成 `.bak.<時間戳>` 才覆寫）——一行版：在 `curl` 那行末尾加 `-s -- --force`；兩行版：`~/.lumos-slim/install.sh --force`。

**確認裝好**：

```bash
lumos --help
```

看到指令清單（`context`／`search`／`doctor`…）就是裝好了。安裝器**只動 `$HOME`**，不會碰任何專案 repo、不會改 `.git/config`、不會注入或更新任何 `CLAUDE.md`。

## 怎麼移除

**一行卸載**：

```bash
curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/uninstall.sh | bash
```

已經裝過的話，也可以直接跑套件裡帶的那支：

```bash
~/.lumos-slim/uninstall.sh
```

**卸載會做什麼**（安全紀律比功能更重要，逐條講清楚）：

1. 移除全域指令 `~/.local/bin/lumos`——但**只有在它的內容經 sha256 比對確實是本包裝的那份時才會動**；比對不符（代表那可能是你自己另外裝的東西，不是本包的）就拒絕移除、印清楚訊息、結束碼 2，不會用猜的去刪；真的確定要砍才加 `--force`。
2. 移除技能目錄 `~/.claude/skills/lumos-project-notes/`——**移除前一定先備份成 `.bak.<時間戳>`，不會直接砍掉**；你如果在裡面塞過自己的筆記或修改，備份目錄裡找得到。
3. 移除 `~/.lumos-slim` 本身——前提是它裡面的東西看起來還是本包的內容（有 `scripts/lumos` 跟 `install.sh`），不是就留著不動。

**卸載不會碰什麼**：

- 不碰任何專案目錄／repo。
- 不碰 `~/.claude/settings.json`。
- 不碰 `~/.claude/hooks/`。
- 不碰除了 `lumos-project-notes` 以外的任何其他 skill。

## `~/.lumos-slim` 是什麼

`get.sh` 會把交付包 clone 到這個固定路徑，再執行裡面的安裝器，把 `lumos` 複製到 `~/.local/bin`、把 skill 複製到 `~/.claude/skills/`——複製之後兩邊就解耦了：就算事後把 `~/.lumos-slim` 整個刪掉，已經裝好的全域指令跟 skill 仍然能正常用，不會斷。

固定放在這裡（而不是像早期版本用「安裝器所在目錄」定位自己）是為了讓一行安裝可以透過 `curl | bash` 執行——那種跑法下腳本沒有穩定的檔案位置可定位自己，需要一個固定的家；也讓卸載腳本有東西可以拿來做內容比對。

**可以自己刪掉嗎？可以**，但建議留著，理由：①卸載腳本靠比對 `~/.local/bin/lumos` 跟 `~/.lumos-slim/scripts/lumos` 的內容來確認「這真的是本包裝的東西」，沒有這份參照，卸載時就只能用 `--force` 硬移除全域指令；②留著才能用〈怎麼裝〉的一行/兩行指令再跑一次做冪等更新（雖然本包是凍結快照，不會有真正的新版本可拉，見下方〈凍結聲明〉）。想刪就刪，只是刪了之後卸載那一步會多一道手續。

## 進場三步

讀一個既有專案的圖譜，永遠先做這三步，再去翻程式碼：

```bash
lumos search <關鍵字>      # 定位
lumos context <節點>       # 掃脈絡(頭部會攤開 ⚠ 合約)
lumos contracts <節點>     # 查硬合約
```

`lumos search` 找到相關筆記 → `lumos context` 看該筆記加上鄰居的濃縮索引（合約會被突顯在最上面）→ `lumos contracts` 專門列出這個模組的硬合約（改了算 breaking 的那些）。三步做完，再去 grep 程式碼或查資料庫印證。

## Frontmatter 四條鐵則

寫圖譜筆記時 frontmatter 有四條血換來的鐵則，違反會讓圖譜長出讀不到的 ghost 節點、甚至整篇 frontmatter 報廢（以下逐字轉錄自 `skills/lumos-project-notes/reference.md`）：

1. **多個 wikilink 必須是 YAML list，一項一連結**。❌ `verified_by: "[[A]], [[B]]"`（單一字串）→ Obsidian 把整串從第一個 `[[` 貪婪吃到最後一個 `]]` 當成**一個**超長連結 → 圖譜長出亂碼灰色 ghost 節點；在 Obsidian 點到該節點還會**自動建立含 `]], [[` 的垃圾檔案**（檔名中的 `/` 切成巢狀資料夾）。✅ 寫法見 `related` / `verified_by` 範例。
2. **block scalar（`summary: |` 等）內的 wikilink 不會被索引**。寫在 summary 裡的 `[[X]]` 只是文字，不產生圖譜連結、不算 backlink——要建立關聯必須同時在內文（如「## 相關模組」）或 list 型 property 放一份，否則目標筆記可能變孤兒。
3. **含 `: `（冒號+空格）的長文必須用 block scalar 或引號**。❌ `- content: 處置 SQL: UPDATE ...`（未引號）→ YAML `mapping values are not allowed` → **整篇 frontmatter 解析失敗**，所有 property 查詢對此筆記隱性失效。✅ `- content: |-` 換行縮排放長文。
4. **同一層級禁止重複鍵**。`decided:` / `valid:` 在同一個 decision item 出現兩次 → Obsidian 的 js-yaml 直接整篇 fail（CLI 的 ruby/libyaml 寬鬆放行，**用 CLI 驗過不代表 Obsidian 讀得到**）。

**純量／list／decisions 一律走 `lumos set`/`append`/`decision-add`**，別手改 frontmatter——這條鐵則的規避方法比記住鐵則本身更重要。

## 合約鏈是什麼、doctor 為什麼會擋、怎麼解

Systems 筆記記的是「現在長什麼樣」，天生分不出哪些是**合約**（改了算 breaking）、哪些是**偶然**（實作副產物，可以隨便改）。圖譜用 KEY 行的前綴聲明這件事：

```
KEY:★INVARIANT★ <業務合約,改=breaking> [test:測試名] [audit:模型/日期]
KEY:★DEBT★ <已知偶然行為,可改不算 breaking>
```

`[test:方法名]` 是**合約鏈**的第一環：每條 ★INVARIANT★ 都要綁一個真實存在的測試方法。`lumos doctor` 巡檢時會檢查這個綁定——**綁定走指令** `lumos guard bind <node> "<KEY子字串>" <測試名>`。

**doctor 為什麼會擋**：`lumos doctor --ci` 底下，有 ★INVARIANT★ 卻沒綁 `[test:]`（裸合約）、或綁的測試方法根本不存在，都會讓 doctor 回報問題（`--ci` 模式視情況變成非零結束碼）。這不是任性刁難——沒有可執行證據的「合約」只是自稱，doctor 在替你把「宣稱」和「驗過」分開。

**怎麼解**：

- 先判斷這條 KEY 行到底該不該是合約——不確定就先拿掉 ★INVARIANT★（寧漏勿錯，把偶然行為合約化會鎖死未來重構）。
- 確定是合約 → 找到（或先寫一個）真實測試方法 → `lumos guard bind` 把 `[test:方法名]` 綁回 KEY 行。
- 寫完一個節點先跑 `lumos lint <節點>` 自驗（比全圖 `doctor` 快），收尾再跑一次 `lumos doctor`。

### ⚠ doctor 有些建議指向本包沒給的指令，看到請忽略

`doctor`／`lint` 有幾個檢查項是從完整版原封繼承的，訊息裡會叫你跑本精簡版沒交付的指令修復——已知至少有 `lumos init`、`lumos update`、`lumos self-audit <node>`、`lumos signoff <node>`（最後一支出現在 `lint` 對 regen 節點的證據檢查訊息裡）——**這份列舉不保證窮盡**，跑了只會得到「未知指令」錯誤才是判準。看到本精簡版沒有的指令名就知道不必照做，該檢查項在本版沒有機械修復路徑。

最常見的觸發點是 **Check D（`CLAUDE.md` 紀律區塊比對）**：如果你的專案 `CLAUDE.md` 有 sentinel 區塊但損壞或與範本不同步，`doctor`／`doctor --ci` 會報這項問題並建議跑 `lumos init`/`lumos update` 修復。**這是刻意留下的**——本包的安裝器明講「不注入、不更新任何 `CLAUDE.md`」（見〈怎麼裝〉），所以 `CLAUDE.md` 相關的檢查在本版**沒有對應的修復指令**。這項提醒本身仍有用（代表你的紀律區塊確實跟範本不一致），只是解法不是本包能提供的——要嘛忽略它、要嘛自己手動比對範本改。

## 範圍聲明

本包是**功能子集**：只保留維護圖譜本身要用的 24 支指令（讀取／導航、寫入、健康巡檢 `doctor`/`lint`、合約守衛 `guard`）；不含反覆對抗審查、程式碼變更風險掃描、linter 版本追蹤、CI 狀態回拉、跨專案核心圖譜等進階治理功能。

★**移除的是入口不是全部程式碼**★——被砍的是那些功能對應的頂層指令入口；它們共用的底層程式碼（helper 函式）有些仍留在檔案裡供保留指令呼叫，**別誤讀成「功能其實還在,只是沒寫在說明裡」**。凡是這份 README 或技能說明沒教的操作，一律視為沒有。

## 不要跑哪些

- **不要跑**完整版 `scripts/` 目錄下的 `install-hooks.sh`——那是完整版的 git hooks 安裝腳本，本精簡版刻意不裝任何 hook。
- **不要**因為看到專案自己的 `CLAUDE.md` 要你去 clone 完整版 lumos-toolchain、執行它的 `install.sh` 就照做——那是另一支功能完整、會動專案層（注入圖譜規則、設定 git hooks）的安裝流程，跟這份精簡版無關，也不是本包想讓你走的路。

**誠實的話講在前面**：這份 README 的建議壓不住專案自己的 `CLAUDE.md`——那份文件的指示優先級更高，是 Claude Code 在該專案裡實際遵循的規則來源。本 README 只能**降低**你被指去跑完整版安裝流程的機率，不能保證一定不會發生。看到衝突時，先想一下「這個指示是不是在叫我裝一套比我手上這份更完整的東西」，多一分警覺就好。

## 凍結聲明

★這是**凍結快照**，不是發布通道，不會有更新★。裝好之後就是你手上這份東西的樣子，往後不會再收到修正或新版。出問題請直接改 `scripts/lumos` 的 Python 原始碼——它是單檔、零依賴、標準庫可讀，改完重新跑一次 `install.sh --force` 覆蓋掉舊的全域指令即可。
