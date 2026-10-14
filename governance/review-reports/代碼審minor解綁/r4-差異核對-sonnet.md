severity: minor

引句:「寫側前置檢查(共用函式之外的唯一一道,先於核對)」
severity: minor
blocking: 否
這一句跟同段後面「記帳當下就核對完」那條互相矛盾。那條寫「適用條件(有沒有 major 席、blocker 席)也由函式內判,寫側不另寫一份」。前置檢查卻在寫側另判「本輪沒有 major 席、accepted 為空」,等於把適用條件的一半寫了第二份。它也沒處理 blocker 席的情況,S28 的條款同樣沒涵蓋。具體輸入:blocker 輪、載體帶 `--finding-source`、accepted 非空。字面實作下前置檢查會放行,共用函式判「不適用」,而寫側遇到「不適用」該怎麼辦,計劃沒寫。舊寫側只擋 severity 為 blocker 的載體自己放行(`file: scripts/lumos:10755`),擋不到「同輪另有 blocker 席」。若寫側照寫入處理,帶 `finding_sources` 的載體進帳,閘端才失敗(S5),載體又不能重記,白花一輪,正好是計劃自己想避免的路徑。應該是:寫側在「共用函式回不適用」時一律 rc 2,把 blocker 席也寫進 S28,並刪掉前置檢查裡重複的 major 席與 accepted 判斷,或明說它只是早退。

引句:「位置參數改成可收多份」
severity: minor
blocking: 否
現行 `report-normalize` 是單一位置參數,直接呼叫 `cmd_report_normalize(args.path, write=args.write)`(`file: scripts/lumos:56165`)。該函式只吃單一路徑,內部是 `Path(path).read_text`。計劃只規定 `--items` 與 `--write` 互斥,沒規定不帶 `--items` 時給多份報告怎麼辦。照字面把參數改成 `nargs='+'` 後,執行 `report-normalize a.md b.md`(沒帶 `--items`)會把 list 傳進去而丟例外,或只處理第一份而默默忽略其餘,二擇一。S27 也沒測這條。應該是:沒帶 `--items` 時多於一份就 rc 2 並指路。

差異改到的其他地方我都看了,沒找到問題。具體是:序號正規式、存正規化路徑、一條原報只撐一個放行與原報 major 可被多個折入 id 指到的互相搭配、`finding_sources` 的型別與 gov 略過該列的行為(與 `_drift_jsonl_parse` 後的 `continue` 一致)、S19 到 S28 的改寫。

派工詞尾端沒有 hook 附的固定席節點。

總結:minor,blocking 0 條。
