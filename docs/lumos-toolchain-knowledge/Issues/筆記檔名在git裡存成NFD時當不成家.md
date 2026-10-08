---
type: issue
status: open
created: 2026-10-01
updated: 2026-10-01
aliases: []
about_code:
  - scripts/lumos
tags:
  - type/issue
  - status/open
  - scope/guards-gates
summary: |-
  PITFALL:[2026-10-01 回頭重讀守檔筆記實作時重現]檔名在 git 樹裡存成 NFD(拆開的 Unicode 寫法)的 Systems 筆記,在「不是工作目錄 HEAD 的那個提交」上當不成家:每支檔有家建一邊快照時用 NFC 路徑去讀筆記,NFD 樹裡讀不到,那一邊的家對照表整篇漏掉。重現指令在正文
  WHY:[[[Projects/守檔筆記對照改動_計劃]]〈誠實界線〉]這是每支檔有家共用函式的既有限制,回頭重讀那一案照計劃不修、只開這篇記下;會受影響的是用同一支建快照的每一道(每支檔有家推送前那半、存量漂移、回頭重讀)
related:
  - "[[Projects/守檔筆記對照改動_計劃]]"
  - "[[Systems/每支檔有家]]"
---
# 筆記檔名在git裡存成NFD時當不成家

白話:同一個中文或帶重音的檔名,Unicode 有兩種寫法(合起來的 NFC、拆開的 NFD)。macOS 的 git 預設在加檔時把檔名轉成 NFC,但從別的機器來、或關掉那個轉換加進去的檔,樹裡存的可能是 NFD。每支檔有家建某個提交的快照時,先把樹裡的路徑轉成 NFC,再拿 NFC 路徑去讀筆記內容;讀的是工作目錄 HEAD 時照磁碟讀、讀得到,讀別的提交時走 git、用 NFC 路徑查 NFD 的樹就查不到——那篇筆記在那一邊就不存在,它管的檔在那一邊沒有家。

## 重現(2026-10-01,在一個空的暫存 repo 裡)

```
git init -q r && cd r && git config user.email t@t && git config user.name t
mkdir -p docs/kg-knowledge/Systems src && echo x=1 > src/a.py && git add src/a.py
printf -- '---\ntype: system\nstatus: doing\nabout_code:\n  - src/a.py\n---\n# n\n' > n.tmp
blob=$(git hash-object -w n.tmp)
nfd=$(python3 -c "import unicodedata;print('docs/kg-knowledge/Systems/'+unicodedata.normalize('NFD','café')+'.md')")
git -c core.precomposeunicode=false update-index --add --cacheinfo 100644,$blob,"$nfd"
git commit -qm c1 && c1=$(git rev-parse HEAD)
echo x=2 > src/a.py && git add src/a.py && git commit -qm c2
```

之後在這個 repo 裡把 lumos 當模組載入,對 c1 建快照(每支檔有家那支建一邊快照的函式,圖譜給 docs/kg-knowledge),快照的筆記是空的、家對照表是空的;對 HEAD 建則讀得到(走磁碟)。

## 修法方向(建議,修的時候照這個走)

建快照時保留 git 原樣路徑,讀內容用原樣路徑或 blob 編號(存量漂移舊句檢查與回頭重讀讀內容都已經改用 blob 編號,是同一種解法);比對仍用 NFC。改的是共用函式,要一起跑每支檔有家、存量漂移、回頭重讀三組測試。

REVISIT:2026-12-31 有沒有專案真的碰到(看 rtb 與消費專案回報、或 doctor 有沒有唸到 NFD 檔名);碰到就照上面的方向修,一直沒碰到就維持記錄
