preflight-4: ran

# v4 r1 前掃留痕(折入後指紋 07d5409b2e3414c70f70d1e2a76b0d243b46a9403a126a7d93fce8b85e5e10aa)

## ★地基級(1,已折並立 Issue)★
- **「git 腿看得到所有 Bash 改檔」不屬實**:git 腿只在圖譜已動過分支被呼叫、列缺筆記;閘門 1/2 只看逐字稿;sed -i 在閘門 2 靜默 return 0。→ 既有閘本來就漏純 Bash 改碼,立 [[Issues/收工閘漏掉純Bash改碼]];v4 [S2] 改 git 優先重佈線(d11)。**論點(入口/意圖/事實)未被打到,死的是機制宣稱。**

## ④ 不屬實/精修已改(6)
- 擋一次=每 session 一次(標記檔 7 天才清)→ v4 需自己的標記;「被擋過一次」無可稽核留痕(只有自陳)。
- 逐字稿認不得=整支略過,不是退回 git。
- `touched_graph_via_cli` 加分支會吃掉既有筆記提醒(:628 的 OR)→ 另寫函式與分支。
- Codex 第三條驗收=非阻擋提醒路徑、離線重播;block→續做未驗→ v4 第一版只承諾 Claude 側。
- `rel_cascade_create` 會寫 header、canary-log 不寫→ 裁不寫 header。
- ★「126 篇」錯,正確 150(v3 兩席實查);126 是 spec-trace 未使用篇數——編排者把兩個數字混了(當日第九次同型)★。

## ④ 屬實(4)
Bash 五種操作/session_id :679(Codex 側合理但未直接驗)/_BOOKKEEPING_FILES :14128 加字串即生效/check-graph-sync 在 ANCHOR_FILES(當日補)→改必走 anchor approve。425 筆/天與 886 vs 43,481 出處 v3 r1-邊界.md:5,:18。

## 補充
安裝版 hook 703 行 vs repo 源檔 835 行,:468 後錯開 132 行(源檔多 _trusted_lumos 段,未 install)→ 實作對源檔、行號重查。
