# 怎麼發一版出去(給維護者的 checklist)

白話:`main` 是開發線,推壞了沒關係,因為**沒有人跟著 main**。
`release` 是對外線,只有你把它快轉過去,別人才拿得到。
發版就是「把 release 快轉到你認可的那個 commit」,其餘都是留紀錄。

**這份刻意不寫成腳本**:發版低頻、不可逆(有人已經裝了就收不回),
而且每一步都需要人在場看一眼再決定。寫成腳本只會讓人閉著眼睛按 Enter。

## 0. 前置

- `gh auth status` 確認登入(**第 2 步等 CI** 與 **第 5 步開 Release** 要用;第 3 步是純 git,不需要)。
- 工作樹乾淨、人在 `main`、跟遠端同步。

## 1. 寫版本與變更紀錄

- `scripts/lumos` 的 `LUMOS_VERSION` 就是版本的唯一來源;`CHANGELOG.md` 第一筆要跟它一致
  (有守衛盯著,兩邊任一邊解析不到就紅)。
- 標題格式**恰好**是 `## vMAJOR.MINOR — YYYY-MM-DD`(全形破折號,版本帶 v)。
- commit、push。

## 2. 等 CI,而且要看判定不是看回傳碼

```
lumos ci-wait --json
```

★**只看回傳碼會出事**★:`ci-wait` 回傳 0 涵蓋六種判定裡的五種——
沒裝 `gh`、沒登入、網路斷都會「放行」(它刻意設計成不擋流程)。
所以要看 `verdict` 欄位**等於 `green`** 才往下走。不是 green 就停下來查清楚。

## 3. 把對外線快轉過去(這一步才是「放出去」)

```
git push Lumos main:release
```

- **不是 fast-forward 就讓它失敗,不要 force**。政策是只前滾、不改寫。
- ★這一步要加 `--no-verify`,而且理由要說清楚★(2026-09-07 第一次發版實測):
  推送閘是拿「這次推送的 ref 相對遠端那條 ref 的差集」去算風險等級。
  `release` 這條線上的內容**跟 main 完全一樣、剛剛才過完整套閘與 CI**,
  但對閘來說 release 是另一條 ref,差集是「整段歷史」,於是判成高風險、要求重審。
  第一次發版時 release 根本還不存在,差集更是全部。
  **這一步搬的是通道,不是新程式碼**——所以繞過本機閘是對的,
  但**前提是第 2 步真的看到 green**,不然就是拿沒驗過的東西當對外線。
- 遠端在你的 clone 裡叫什麼名字自己確認(`git remote -v`);
  本 repo 的維護者機器上叫 `Lumos`,不是預設的 `origin`。

## 4. 打 tag(留紀錄用,不是安裝通道)

```
git tag -a vX.Y -m "<一句話>"
git push Lumos vX.Y
```

- 安裝通道是**分支**不是 tag:`git clone --branch <tag>` 會進 detached HEAD,
  之後 `git pull --ff-only` 必定失敗,`lumos update` 也就更新不了(2026-07-30 裁定)。
  ★2026-09-07 訂正★:當初的理由寫的是「**靜默**停在裝機那一版」,那半句現在不成立——
  2026-09-06 起拉不到來源會直接中止並講明原因(fail-closed),不再只印一行警告就繼續。
  所以結論一樣(釘 tag 就收不到更新),但**現在你會被告知**,不是無聲無息。
- 上次 tag 建了但推失敗要重跑:先 `git tag -d vX.Y`。

## 5. 開 GitHub Release

```
gh release create vX.Y
```

notes 直接抄該筆 CHANGELOG。

## 發完之後要知道的兩件事

- **raw 有 CDN 快取**(數分鐘級)。移動 release 之後,
  `curl … /release/get.sh` 短時間內仍可能拿到舊的那份。**這是延遲不是錯誤。**
- **一台機器可能同時跑三個版本**:全域指令(捷徑指向來源 clone)、
  各專案自己複製的一份、全域 AI hooks(來源是最後一個跑安裝的專案)。
  `lumos --version` 只回答你現在打的那一支。

## 還沒放出去的有哪些

```
git log release..main --oneline
```
