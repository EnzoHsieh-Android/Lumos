preflight-4: ran(第 1 輪已跑;本輪只審第 1 輪折入差異)

# 設計審第 2 輪席位收貨:殺傷力驗證編譯快取誤判

2 席全新、只審第 1 輪折入差異(r2-delta.diff)。2 席全收齊後才動計劃。四道機械檢查:2 份正規化;quote-check 全錨;refcheck 全數對得上;兩欄一致;repo 根 reflog 無異動。

finding 編號:c=正確性-opus、h=接手-sonnet。

| 編號 | 席 F | 等級 | 重現 | 處置 |
|---|---|---|---|---|
| c1 | 正確性 F1 | major | HIT(席位雛形實測:印了弱證據提醒,--json/kill-log 卻 weak=false);兩席一致(h5) | 折:旁路欄 `_mtime_unsure`、收尾重算 weak 算進去、--json 濾掉;新條款 S4 |
| c2 | 正確性 F2 | major | HIT(席位實測拿掉還原前等待 S1/S2 照綠、改 a 再改 b 3/3 誤判);兩席一致(h1) | 折:S2 固定兩支檔驗還原那一半;〈做法〉寫明還原前等待必要的理由 |
| c3 | 正確性 F3 | major | HIT(席位實測只記第一次 baseline,make 專案 5/5 判錯) | 折:每一次 `_kill_run` 跑完都更新測試結束秒,含每個 baseline |
| c4 | 正確性 F4 | minor | HIT(Linux 部分為席位推論);兩席一致(h2) | 折:讀回比對對象跟等待一致(上一次寫檔與測試結束取大者) |
| c5 | 正確性 F5 | minor | HIT(席位模擬撥回 6 秒卡 6.5 秒);兩席一致(h7) | 折:等待上限 3 秒 |
| h1 | 接手 F1 | major | HIT | 折:同 c2 |
| h2 | 接手 F2 | minor | HIT | 折:同 c4 |
| h3 | 接手 F3 | minor | HIT | 折:S1 補同大小傷害壞法(LIMIT = 5 → 6)那半 |
| h4 | 接手 F4 | minor | HIT | 折:S3 寫明實作後以「改設未來時間」變異驗翻紅 |
| h5 | 接手 F5 | major | HIT | 折:同 c1 |
| h6 | 接手 F6 | minor | HIT | 折:〈做法〉寫明 state 型別、記讀回值還是牆鐘、插入位置、各分支 |
| h7 | 接手 F7 | minor | HIT | 折:同 c5 |
| h8 | 接手 F8 | minor | HIT | 折:多花時間照實測更新,全套留〈實作紀錄〉 |
| h9 | 接手 F9 | minor | HIT | 折:S1 寫明清掉 PYTHONDONTWRITEBYTECODE |

重現不到而沒折的:無(refuted-set none)。放行的:無。
