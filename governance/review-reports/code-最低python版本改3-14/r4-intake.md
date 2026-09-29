# r4 收貨紀錄(code-最低python版本改3-14;上限後破例一小輪)

破例依據:第 3 輪仍有 major,Enzo 2026-09-29 裁「修完再破例審一小輪」。
凍結材料:r4-snapshot.patch(r3 折入的修正差異 b0eff2af..2620dfbf,git diff -U10,排除卷證目錄與兩本治理帳;596 行,sha256 7471fee5…)。4 席全新:單 reviewer opus、架構對齊 sonnet、資安 sonnet(Sonnet 5.5)、外家 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。

## 席位收貨

- 4 席全交,等完成通知、ls 確認後才讀;clone-314 的 reflog 只有編排者自己的提交,席位沒動 repo。
- report-normalize 4 份都已是正規化格式;quote-check:單 reviewer、架構對齊全錨定;資安、外家兩席 clean、報告裡沒有引句。
- 發現 5 條(單 reviewer 4、架構對齊 1、資安 0、外家 0);major 1(架構對齊 F1),其餘 minor。
- 本輪有 major,accepted 必須是空的,5 條全折。
- 上限處置:破例輪仍有 major,再問人;Enzo 同日裁「修完直接推」。★這一輪的修正差異沒有再經過審查★,每條各有翻紅測試。

## 機械重現(在審的那一版 2620dfbf 上跑;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 架構對齊 F1(四支安裝腳本各貼一行、測試守不到) | 讀 t_python_launcher_blocks_agree:只比 begin/end 之間;那一行在 end 標記之後 | HIT:讀碼確認;席位附的「四份全刪 118 passed」沒重跑,修完這一行已不存在(搬進共用段) |
| 單 reviewer F1(只講略過、不講後果) | 讀 2620dfbf 的 install.sh:印的是 `_LUMOS_ANY_NOTE`,內容只有「略過」 | HIT |
| 單 reviewer F2(掛鉤驗 3.14 要求整段輸出等於記號) | 讀 2620dfbf 的 pre-commit python-314 段:沒有 tail -n 1 | HIT:讀碼確認;修完用 sitecustomize 多印一行釘測試 ②b |
| 單 reviewer F3(uv 出錯只取最後一行) | 席位附的真 uv 在壞 uv.toml 旁的多行輸出;讀 2620dfbf 的 _py_uv_find:取 err[-1] | HIT:讀碼確認;測試的假 uv 改成照真 uv 的多行形狀 |
| 單 reviewer F4(計劃段落錯位) | 讀計劃〈實作時的決定〉:lumos.cmd 那段接在「安裝腳本當場講」後面 | HIT |

## 處置

- 全部折進程式、測試與筆記(細節在計劃〈實作時的決定〉與〈審計修正紀錄〉代碼審 r4 段):
  - 架構對齊 F1、單 reviewer F1:印原因搬進 shell 共用段(`_lumos_any_python` 包一層,找到別支而且有略過原因時印原因與後果),四支安裝腳本各自那一行拿掉;七份共用段照舊由 t_python_launcher_blocks_agree 逐字守;測試 ⑦c。
  - 單 reviewer F2:驗 3.14 取最後一行;測試 ②b。
  - 單 reviewer F3:帶第一行 error 與最後一行;⑤e 的假 uv 照真 uv 的多行形狀、斷言兩行都要在。
  - 單 reviewer F4:lumos.cmd 那段與 REVISIT 行搬回「目前目錄裡的同名檔不收」那條。
- 翻紅驗證(每項在乾淨複本改壞一處、清快取後跑對應測試):拿掉 tail -n 1 → ②b 紅;不印略過原因 → ⑦c 紅;uv 只取最後一行 → ⑤e 紅。
- refuted 無;accepted 無。
