# 設計審 r1 收貨紀錄(筆記標籤-過時判定與按需載入)

preflight-4: ran

## 首輪前掃(haiku,掃的是凍結前一版;報告原文 r1-preflight.md)

- ① 未定義的詞:「rtb」沒解釋 → 已在依據段補「rtb=消費專案 rtb-production-agent-demo」(修真檔,不算 finding)。「Enzo 裁」缺時間出處 → 已裁段標題帶日期,不改。
- ② 壞引用:[[Projects/漂移防治路線圖_計劃]] 不在本 repo 主線(在另一個會談的工作區、尚未推)→ 不是寫錯,推送順序要讓那篇先進主線;派工詞已告知席位。
- ③ 範圍矛盾三條:全是計劃〈現況〉已列、第 0 步要修的既有文件矛盾,不是計劃本身的矛盾。
- ④ 機械宣稱驗語意:doctor N 標記、note-shape 上線點、單次跳過環境變數 → 成立;「改檔前提示 hook 附棧別檢核題」「推播 hook 只印篇名」前掃查不到 → 編排者查證:impact-hook 的 build_ranked_context 確實附「效能檢核」段與只印篇名、合約類別,成立;計劃已補上 hook 名字(語意未變,僅補指名)。

## 收貨三道(六席)

- report-normalize:架構對齊席一處「severity 寫在條目標題行」用 `--write` 純格式搬到獨立行(不改值、不碰引句);其餘五份已正規化。
- quote-check(對 r1-snapshot.md):六份全數錨定(整合 43、架構 25、邊界 24、資源 24、回滾 22、正確性 16 句)。
- refcheck:六份引的 file:line 全部存在。
- seat-check:派工單的 materials 只列凍結快照,vacuous 豁免。

## 編排者重現(關鍵宣稱,機械驗)

| 席位 id | 重現 | 結果 |
|---|---|---|
| C1 B8 I1 R7 | impact-hook 的 CODE_EXTS 不含 .md,EXCLUDE_PATH_CONTAINS 含 "/docs/"(grep 命中兩處) | HIT 採信 |
| C2 B9 I12 K3 | `lumos search --about x` → 「不認得這幾個參數:--about」;term 為必填位置參數 | HIT 採信 |
| B1 K4 C11 I17 | `_init_config_skeleton` 遇到既有 config.json 直接 return(「既有設定不碰」) | HIT 採信 |
| A2 R2 C10 I5 K10 B4 R3 | doctor N 的 `_CNT_RE` 是 cmd_doctor 內的區域變數,不是共用函式;行內欄位解析一律 `[^\]]*` | HIT 採信 |
| 其餘 | 引句全數錨定,宣稱都附 file:line 且 refcheck 全過;同一現象多席獨立指出 | 採信 |

refuted-set:none。

## 處置

74 條全部折入(散文設計審;有 major 的條目以改設計折掉,刪減範圍也算折):判過時改接存量漂移檢查;欄位六類縮三類;正規式數量、取代鏈、設定預設 off 加 init 寫入三個「第二種做法」拿掉;教法主要管道改提交時提醒;W6 收窄並降成提醒(Enzo 裁);RULE 效力不放寬;`[until:]` 過期改提醒;search 行模式另開旗標、term 可省;回退、實務隱患、驗收條款整段重寫。Enzo 另裁三題:提醒對所有專案的新寫行都出、工具鏈也擋、重複事實降級。
