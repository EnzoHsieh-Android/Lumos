severity: minor

## Z1 `_note_versions` 說明還寫著由 `_drift_born_annotate` 共用,但拆分後它已不直接呼叫
severity: minor
blocking: 否
引句:「_note_status_seq 與 _drift_born_annotate 共用。」
file: `scripts/lumos:29988`(實際呼叫端是 `scripts/lumos:33172` 的 `_DriftBornHistory._text`;對照鄰居 `_nodehome_cat_blobs` 等說明都指到真正的呼叫端)
說明:這輪把 `_drift_born_annotate` 拆成 `_drift_born_one/_eval/_rec/_over` 並讓 `_DriftBornHistory._text` 直接呼叫 `_note_versions(first_parent=True)`,共用說明沒跟著改。結構對,只是說明指錯人,下一個讀的人會去 annotate 裡找呼叫而找不到。這正是「修法自己引入的不一致」。改成「_note_status_seq 與 _DriftBornHistory 共用」即可。

---

三問總答

1. 分層與依賴方向:一致。git 全部走 `_lens_git`(scripts/lumos:40407)、`_ns_git`(27486)、`_nodehome_cat_blobs`(26678)、`_lens_full_sha`(40422),沒有直接叫 subprocess(`_git_is_shallow` 內部那個是既有 helper,5678)。依賴方向與 `_drift_probe_scan`(33005 起)一樣:cmd_drift_scan 呼叫 `_drift_born_annotate`,再往下呼叫 `_drift_tree_env`、`_drift_probe_tree`、`_drift_probe_prefetch`、`_drift_probe_line`,跟 `_drift_probe_scan` 用同一組;沒有反向呼叫。讀指令不寫帳:`cmd_drift_scan` 這段只加註解欄位、不碰治理帳,與 lumos-cli-read 一致。`_git_is_shallow` 的 TimeoutExpired 由呼叫端接,符合其說明(5679);其他呼叫端(13755、33951)沒接,屬鄰居本身的做法不一,不算本 diff 的不一致。

2. 命名與錯誤處理:大致一致。私有函式底線前綴、常數大寫(`_DRIFT_BORN_*`、`_DRIFT_LS_CACHE_MAX`)與鄰居相同;失敗回傳用 (值, 原因) 二元組或 None(`_text` 回 (狀態, 文字)、`birth` 回 (提交, 原因, 旗標)),訊息為白話中文,與 `_drift_probe_scan` 的「判不了(超過預算)」措辭同一路。唯一不一致是 Z1 的說明指錯。⚠ 交編排者:`_drift_born_env_err` 判「是不是 git 專案」用 `rev-parse --git-dir`,另一處鄰居(29618)用 `--is-inside-work-tree`、36238 用 `--git-dir`,鄰居本身就兩種,不硬判。

3. 第二種做法:沒有引入新的 git 讀取或快取。版本清單與歷史各版讀取沿用 `_note_versions`(從 `_note_status_seq` 抽出共用)、`_nodehome_cat_blobs`;列樹快取沿用 `_DRIFT_LS_CACHE` 並把上限抽成常數;淺層判法用既有 `_git_is_shallow`。⚠ 交編排者:預算計算(`_DriftBornHistory._left` 預設 60 秒、`_drift_born_over`)是第 N 份複製,但鄰居本身就各寫各的(`_note_status_seq` 的 `_late/_to` 29962、`_drift_probe_scan` 的 `_over` 33017、`_DriftProbeTree._over` 32515),專案沒有共用的預算 helper 可對,不判不一致。⚠ partial clone 偵測(`extensions.partialClone`,33056)專案裡沒有既有做法可對。`_drift_born_*` 拆分方式:小函式以模組層私有函式、用 ctx 字典傳狀態,與 `_drift_c4_evidence(cx)`(33946)的 cx 字典、`_drift_probe_scan` 的內部 `_over` 閉包拆法同一路,類別 `_DriftBornHistory` 與 `_DriftProbeTree`、`_DriftNames` 同為「分段讀、用到才讀」的快取類別,一致。

總結:不對齊共 1 條,其中 major 0 條;最高等級 minor
