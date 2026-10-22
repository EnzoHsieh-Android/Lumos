---
type: verification
status: pass
date: 2026-10-23
valid_under:
  - 實機 SM-X710(Android 16、user build),小專案用 benchmark-macro 1.4.1,三次實跑在同一台、間隔數分鐘內
  - 只驗工具判得對:小專案的數字不代表任何正式 App 的效能
revalidate_when:
  - 換函式庫大版本或換裝置後第一次跑時,用新的實機結果檔重跑 t_macrobench_real_tablet_lab 那組比對
  - 改動容差算法或判退步規則時
tags:
  - type/verification
  - status/pass
  - scope/stack-knowledge
plan_refs:
  - "[[Projects/Macrobenchmark退步提醒_計劃]]"
---
# 2026-10-23_macrobench實機端到端

白話:在真的平板上確認 `lumos macrobench` 抓得到已知的變慢、正常重跑時不亂報。

- **做法**:小專案 `/Users/enzo/orca/workspaces/macrobench-lab` 跑三次——正常、注入變慢(`-e startupDelayMs 300 -e bindDelayMs 8`)、正常重跑——每次跑完拉回結果檔,用 `lumos macrobench` 跟第一次存的基準比。
- **結果**(修正容差下限之後):
  - 注入變慢:報出 4 項——冷啟動中位數 216.1→571.1ms、每幀 CPU P90 4.7→10.2ms、每幀超時 P50 -3.6→-1.0ms、每幀超時 P90 -1.7→3.6ms(標成跨零)。P99 兩項只列出。
  - 正常重跑:0 項。修正前這次誤報了每幀超時 P90 -1.7→-0.9,這就是改容差下限的原因。
  - 滑動的 P50 沒變:大部分幀不畫新列,只有畫新列的幀被拖慢,要看 P90。
- **原始檔**:三份結果檔在 `governance/research/macrobench/2026-10-23-lab-tablet/`,測試 `t_macrobench_real_tablet_lab` 直接讀它們。
- **沒驗的**:KDS 本身在這台平板上用 1.2.4 跑不起來(見計劃〈實機端到端〉);容差下限 1ms 只用一次重跑的抖動回推,沒有多次重跑量浮動。
REVISIT:2026-12-21 同一台裝置正常版重跑至少 5 次量每個指標的抖動,重訂容差百分比與下限的預設值

