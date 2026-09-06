# Lumos 上手指南(ONBOARDING)

> **Lumos —— 揭開全 AI 開發的黑箱,照亮通往正確需求的路。**

給新加入、要開始用「圖譜即合約」方法論的人:照著做就能跑起來。概念介紹在 [README](README.md),這裡只管「怎麼裝、怎麼用」。

---

## TL;DR — 一鍵裝好(推薦)

clone 專案後,在專案裡跑一個指令——**連 Lumos 本體都會自動幫你 clone**,給 AI 的操作手冊(skills)、全域 `lumos` 指令、檢查程式(hooks)一次到位:

```bash
git clone <你的專案> && cd <你的專案>
python3 scripts/lumos bootstrap
# 然後重啟 Claude Code session(給 AI 的提示要在 session 開頭載入)
```

之後每 clone 一個新專案,同樣跑一次 `python3 scripts/lumos bootstrap` 即可(機器已設定好的部分會自動跳過)。

> **專案還沒導入過 Lumos**(repo 裡沒有 `scripts/lumos`)?改走:
> ```bash
> cd <你的專案> && curl -fsSL https://raw.githubusercontent.com/EnzoHsieh-Android/Lumos/main/get.sh | bash
> # 會先問一句「要把 <路徑> 建成 lumos 專案嗎?」按 y 才建;細節與 Windows 作法見 README §3
> ```

---

驗收:重啟 session 後跑一次 `lumos enforcement`,它列每一層防護有沒有接上(Codex 那幾行會停在「本機讀不到信任狀態」,那是天生測不到)。

授權:[MIT](LICENSE)。工具鏈自己的檔案適用;工具寫進你專案的東西(設定檔裡的紀律區塊、你寫的圖譜筆記)是你的。

## 前置需求

| 需要 | 用途 | 沒有會怎樣 |
|------|------|-----------|
| `git` | 全部 | 無法運作 |
| `python3` | lumos 指令與 hooks(純標準庫,不裝任何套件) | 無法運作 |
| Claude Code | AI 才會自動載入方法論與提示 | 工具能跑,但 AI 不會自動照規矩走 |
| Codex CLI(選用) | 想讓「外家席」用另一家模型審(design-loop / code-loop 的否決席) | 那席換成同一家模型,收斂結論要降級成「單家族視角下未發現」 |
| 吃得起配額的訂閱方案(選用) | 設計審 / 代碼審一輪會同時派三到四個子代理讀全份材料 | 手動一輪一輪跑仍可用,只是慢;其餘功能不受影響 |
| notesmd-cli(選用) | 只有改筆記檔名/搬檔時用(`graph-rename.sh`) | 平常用不到;需要時 `fetch-notesmd.sh` 可抓 |

---

## bootstrap 底下做了哪三件事(手動版)

一鍵就是把這三步自動化;知道分層,出問題才知道去哪修:

**① 每台機器一次:裝共用 skills**

skills 是寫給 AI 看的操作手冊,整台機器**共用一份**,用捷徑(symlink)連進 Claude Code 的目錄:

```bash
git clone <lumos-toolchain repo URL> ~/harness/lumos-toolchain
cd ~/harness/lumos-toolchain && ./install.sh
```
- 之後**更新=對這個目錄 `git pull`**,捷徑即時生效,不用重裝。

**② 每個專案 clone 一次:裝 hooks**

hooks 是提交/推送時自動跑的檢查程式,git 規定一個 repo 一份,所以每次 clone 都要裝:

```bash
cd <你的專案> && scripts/install-hooks.sh --force
```
裝三樣:git hooks(提交/推送的關卡)、Claude hooks(開場提示、改檔前附合約、派工前附相關節點、收工核對圖譜有沒有跟上)、Claude 設定註冊。`--force` 是必要的——不加會跳過你機器上的舊版不更新。

**③ 選用,每台機器一次:全域 `lumos` 指令**

```bash
python3 scripts/lumos install     # 之後任何目錄直接打 lumos,不用 python3 scripts/lumos
```

---

## 日常使用

**三句核心紀律**(也注入在每個專案的 CLAUDE.md 裡):

1. 圖譜(`docs/<專案>-knowledge/`)記「為什麼+邊界+驗過沒」;code 只是「現在長這樣」。要懂系統,先查圖譜。
2. 影響行為/決策的改動,**同一次工作內**把脈絡寫回圖譜(提交關卡會擋沒寫的)。
3. 動圖譜的結構化欄位走 `lumos` 指令,別直接改 `.md` 開頭(正文段落可以直接編輯)。

**常用指令:**
```bash
lumos search <詞>             # 查圖譜(中文概念之間加空白)
lumos context <節點>          # 進場掃脈絡:節點+鄰居,合約突顯在最上面
lumos contracts [節點]        # 動模組前查硬合約
lumos doctor                  # 全圖健檢
lumos new <型別> <名稱>       # 建新筆記(system/verification/issue/project)
lumos set / append / decision-add   # 改欄位、加連結、記決策(都寫完自驗)
```

**接手的專案圖譜是空的?** 走「節點還原」七步——從 code 和 git 把脈絡撈回來落成節點:白話版見 [README §6](README.md),快查表在 skills 的 `commands/09-節點還原.md`。

---

## 更新

| 要更新什麼 | 怎麼做 |
|--------|--------|
| 共用 skills+全域指令 | `cd ~/harness/lumos-toolchain && git pull`(捷徑即時生效) |
| 某專案裡的工具組(lumos/hooks/紀律範本) | 在該專案跑 `lumos update`——自動拉最新、重新複製進專案、同步 CLAUDE.md;**圖譜資料不動** |

---

## 卸載

裝與卸對稱,記這句:**整台機器一次拆=`lumos teardown`;只拆這個 repo=`lumos deinit`;只移全域指令=`lumos uninstall`**。teardown 永遠保留圖譜文件;細節見 README §7 結尾。

---

## 疑難排解

| 症狀 | 原因與解法 |
|------|-----------|
| AI 沒有自動照圖譜方法論走 | 機器層沒裝:`ls ~/.claude/skills/` 看有沒有 `lumos-*`;沒有就跑步驟① |
| commit 被擋「改了 code 沒更新圖譜」 | 正常,這就是關卡。把對應筆記更新了再提交;真的與圖譜無關(改錯字之類)才用 `git commit --no-verify` |
| `lumos: command not found` | 沒做步驟③;改打 `python3 scripts/lumos`,或確認 `~/.local/bin` 在 PATH |
| hooks 沒作用 | 這個專案跑過 `scripts/install-hooks.sh --force` 沒?`git config core.hooksPath` 應顯示 `scripts/hooks` |

---

## 維護者備註(owner)

- **這個 repo 是整套工具組的唯一源**(指令/hooks/安裝器/範本/skills 都住這)。改任何工具組檔案=改這裡→push;skills 改完各機器 `git pull` 即同步,指令/hooks 改完各專案要跑 `lumos update` 才吃到。
- 要把 Lumos 裝進一個新專案,站在 Lumos 目錄也可以:
  ```bash
  ~/harness/lumos-toolchain/scripts/install-graph-toolchain.sh --target <新 repo 路徑> --slug <知識庫名>
  ```
  重跑=更新工具組,圖譜資料永遠不動。
- **不放進這個 repo**:各專案的業務圖譜、發版/部署腳本、只有單一專案在用的框架選型。跨專案通用的技術棧慣例 skill(kotlin / vue / csharp-idioms)住這裡,因為它們不綁任何一個專案——邊界跟 README〈邊界與延伸閱讀〉同一句,改一邊要一起改。
- 此 repo 公開:推東西前確認**無公司識別資訊**(專案名/表名/業務規則);skills 與範本只用通用範例。
