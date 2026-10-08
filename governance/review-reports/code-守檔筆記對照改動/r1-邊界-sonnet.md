severity: minor

範圍:對凍結 patch 的 reread-check / reread-prepare / reread-record 在自建 clone(--shared 自 negguard 的 94e28375)與合成 repo 實跑。已跑且行為正確(不另列):空範圍、新分支首推(全 0 起點)、刪除分支(全 0 終點)、tag、只給 --push-remote 一個、--diff 缺 .. 或多於一組 ..、終點不存在、終點為 `--help`、起點不存在(有/無推送參數)、淺層 clone、沒有圖譜、設定壞值(非 JSON、頂層清單、note_reread 非物件、gate 為 null/清單/block/off)、NFD 檔名、檔名含 `[id]*`、改名(相似度不足被 git 當刪除加新增,屬 git 行為)、筆記/程式內含 `{{DIFF}}` `{{NOTE}}` `{{TIP}}`(單次掃描,材料原樣保留)、超大 diff(117 萬字元,截斷註記正確、0.9 秒)、報告各種歪格式(沒 json、兩個區塊取最後、未收尾退回前一段、CRLF、行號為布林/字串/3.0/0/超界/重複、quote 為物件、why 為 null、頂層為物件、縮排的圍欄不收、大小寫 JSON、1e400、NaN、沒開頭四行、非 UTF-8 報告)。全部 rc 合契約(check 恆 0;record 該整份拒收的 rc2)。

## F1 筆記路徑含非 UTF-8 位元組時,提醒已印出卻又宣告「這次沒提醒」,且沒寫治理帳
severity: minor
blocking: 否
引句:「except Exception as e:      # noqa: BLE001 —— 提醒版:沒預料到的錯也不擋推送」
佐證行:file: `scripts/lumos:1228`(_gate_event 內 `f.write(_json.dumps(ev, ensure_ascii=False) + "\n")`,對含孤立代理字元的字串丟 UnicodeEncodeError)
1. 重現:合成 repo 用 `git update-index --index-info` 放入檔名 `docs/p-knowledge/Systems/ba\xffd.md`(about_code 含 src/foo.py),兩個提交各改一次該筆記與 src/foo.py,跑 `python3 scripts/lumos note-audit reread-check --diff <前>..<後> --repo .`。輸出依序是「有 1 篇守檔筆記…還沒對照」、該路徑、reread-prepare 指令,接著一行「回頭重讀提醒:這次沒提醒:沒預料到的錯誤(UnicodeEncodeError)」,結尾的「這只是提醒、不擋…」沒印,rc=0。
2. 原因:掛在 reminded 那筆的 `nodes=[pre + r for r in left][:50]`(與 note 內的路徑)帶 surrogateescape 路徑進 _gate_event,json 寫檔失敗;外層 `except Exception` 接住後改印「沒提醒」並再記一次 skipped(同樣含原因字串,這次不含路徑,可能成功)。結果同一次輸出自相矛盾,且這次的 reminded 事件沒進治理帳(doctor/統計看不到)。reread-record 的 `nodes=[meta["筆記路徑"]]` 若路徑含非 UTF-8 同理,但項目檔寫出的路徑已被 _nodehome_show 轉義,未觸發。
3. 影響:只提醒、不擋,推送不受影響,僅限檔名非 UTF-8 的筆記(罕見,macOS 上根本建不出來);嚴重度 minor。建議帳的 note/nodes 先過 _esc_clean / _nodehome_show 再寫。
4. 順帶觀察(不計條):含非 UTF-8 位元組內容的筆記,在 about_code 解析處靜默不成為候選,check 顯示「沒有要對照的家筆記」——與既有筆記內容審同一限制,未見此 diff 新增。

最高等級:minor
