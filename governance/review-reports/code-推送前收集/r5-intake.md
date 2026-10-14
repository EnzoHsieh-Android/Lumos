# code-推送前收集 r5 收貨紀錄

七席全回(正確性、資源、邊界、合約、通才、架構對齊、資安),report-normalize 都不用改,quote-check 全數錨定。共 10 條,全部 minor:正1、併1(資源席)、邊1–5、合1–2、資1;通才、架構對齊 clean。資安席照工具鏈 repo 的範圍(提示注入、讀寫越界、非刻意一步繞過)沒有找到 major。

資安席回報:實驗中一條指令切換目錄失敗,後續指令跑到會談工作目錄 Backend_improve 產生一個提交(e598636f),該席已拆掉並還原(HEAD 回到 a31b2043、簽名基準檔無改動);編排者已核對 reflog 與工作目錄,確認只剩開場就有的兩行治理帳。這件事不在被審程式裡,不列為 finding。

## 處置:全部附理由放行,不再開下一輪

上限之後的輪次照規矩 minor 可附理由放行。10 條都是 minor:守衛掃描器讀不懂的 bash 邊角(刻意不補成完整解析器,方向多為多擋)、只在原生 Windows 才走的退路、測試沒釘住的邊角、簡版彙總的顯示消毒;沒有一條會讓本該擋下的推送通過。折入任何一條就要再派一輪全新席,成本與收益不成比例。

10 條逐條收進 [[Issues/推送前收集第五輪放行的小缺口]](四段齊,附 REVISIT:2026-12-15)。合2(資安範圍沒有獨立規則)由之後的「工具鏈審查鏡頭範圍」計劃處理。

## 修補因果核對(regression)

上一輪修補範圍 3305a5db..da914963(r5-repair.patch)。正1、併1、邊1–5、合1 落在第四輪修補新加的啟動器、第二發 TERM、掃描器與守衛上,判回歸;合2(資安範圍放在哪)與資1(簡版彙總的 ref 名)是原本就有的,判非回歸。

regression-set:正1,併1,邊1,邊2,邊3,邊4,邊5,合1

refuted-set:none。

## 記帳的審查行數

正確性、資源、架構對齊記 repair-hook 加 snapshot-hook(810 行),邊界記 repair-hook 加 repair-tests(520 行),合約記 repair-docs、snapshot-docs、repair-tests(1188 行),通才記 repair-hook、snapshot-lumos、snapshot-hook(1728 行),資安記 snapshot 加 repair-hook(3966 行)。
