severity: major

我只審併發與資源這一面,結論是格子檢查在推送、doctor 和單次跳過時,會對每篇改到的筆記各跑一次 git,成本跟著筆記數線性增長,而且沒有整體時間上限。

我在乾淨複本(`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/k_clone`)裡用 git 計數包裝腳本量過。測試只改筆記正文、沒動任何摘要行。

**K1 起點版本逐篇各開一次 git show,沒有批次,連沒有摘要行改動的筆記也讀**
severity: major
blocking: 是 — 推送前和 doctor 每次都跑,成本跟改到的筆記數成正比,且偏離計劃〈效能〉寫的「一批起點版本讀取」。
引句:「b = old_reader(p)」
- `_ns_slots_old_lines` 對 `notes` 裡每一篇都呼叫 `old_reader(p)`。推送時 `base_where` 不是 HEAD,`_nodehome_reader` 的 `differ` 是 None,所以每次都走 `_lens_git show`,一次一個 git 行程。
- 提交時,46 篇只改正文的暫存筆記:`note-shape --staged` 是 14 次 git、1.8 秒;加 `--slots` 變 63 次 git(其中 46 次 `show`)、3.8 秒。
- 推送時,掛鉤歷史有格子記號、239 篇只改正文的筆記:`note-shape --diff B..T` 共 267 次 git(239 次 `show`)、12.8 秒。同一個複本裡只含掛鉤變更的範圍是 28 次 git、2.1 秒。
- 照這個斜率,上千篇筆記的大型重構推送會多出約 40 秒以上。每個 git 呼叫的逾時是 20 秒(`_lens_git` 的 `timeout=20`),整段沒有總預算。
- 檔內已有 `_nodehome_cat_blobs`,註解寫明逐支 git show 的行程成本。這裡沒用它。
- 迴圈也沒先篩出有 summary 區新行的筆記。
- doctor 事後掃描走同一條路:`_ns_deleted_summary_lines(gl..tip)` 的整段 diff 和 `old_reader` 的讀取都涵蓋「上線點到遠端頂端」全部改到的筆記。`_NS_DOCTOR_SCAN_CAP`(200 個提交)只截斷逐提交的文字抽取,沒截斷這兩個成本。

**K2 單次跳過前整套評估再跑一次,逃生口變慢且沒有時間上限**
severity: minor
blocking: 否 — 失敗會被例外處理吞掉、照樣放行,但每次跳過都多付一整套評估。
引句:「extra = _ns_skip_slot_extra(root) if (staged and slots_flag) else None」
- `_ns_skip_slot_extra` 會再呼叫一次完整的 `_note_shape_eval(..., staged=True)`,又叫一次 `_nodehome_list(index)`,再加 K1 那種逐篇的 `old_reader`。
- 實測 `LUMOS_SKIP_NOTE_SHAPE=1` 加 `--slots`,暫存 46 篇筆記:0.6 秒變 3.3 秒,git 呼叫從 2 次變 63 次。
- 人通常是因為擋得不對或太慢才跳過,偏偏這時候多算一次,而且沒有整體逾時。K1 修好後這項會跟著縮小。

**K3 讀起點版本失敗被當成沒有舊版本,會把舊行誤算成新寫行**
severity: minor
blocking: 否 — 只在 git 逾時或讀取失敗時發生,而且沒能重現。
引句:「lines += _ns_summary_logical(b.decode("utf-8-sig", errors="replace")).values()」
- `old_reader` 讀不到(`git show` 逾時、失敗)和「那個版本本來就沒有這篇」都回 None,呼叫端靜默略過這篇。
- 這篇的舊行就不進 `old_keys`,只改欄位的舊行會被當新寫行去查必有鍵,結果誤擋。
- 同函式裡 `deleted is None` 是走 fail-open(「這次跳過」),讀取失敗卻是偏向擋下,處理方式不一致。
- 未能重現:要造出 `git show` 逾時,我沒找到可靠辦法。

**圖譜鏡頭(固定席)**
- 計劃〈效能〉(`筆記格子寫法與過期檢查_計劃.md` 第 185 行)寫「一批起點版本讀取」,實作是逐篇讀,即 K1。
- 計劃 [S15] 要求的跳過前計算包例外處理、算不出來就只記不帶格子欄位的跳過,實作有做到。這條只有時間成本的 K2。
- 計劃要求單趟抽取共用,實作做到:`_notelines_live_sets` 對兩個記號只開一次 `cat_blobs`,沒有多出 git 行程。
- 固定席的 `★INVARIANT★`(`lumos-cli-read`、`guard-kill`、`bound-tests-gate`、`授權與歸屬` 等):這次 diff 沒碰它們管的行為,對併發與資源面不影響。

**其餘檢查過、判不影響的項目**
- 治理帳:每次擋下或跳過多寫的 `extra` 只有 `slots_lines` 和 `slots_missing`(鍵數有限),`nodes` 沿用既有的 50 條上限。
- 輸出量:格子違規最多印 20 條(`_NS_SLOT_SHOW`),doctor 最多列 10 處,都有上限。
- 例外處理:`_ns_slots_prepare`、`_ns_slots_collected`、`_ns_skip_slot_extra` 吞掉例外後都回到「不跑格子」的一致狀態,沒有留下半套狀態;`sink` 只在 `mark2` 存在時才被填。

最高嚴重度 major,blocking 1 條
