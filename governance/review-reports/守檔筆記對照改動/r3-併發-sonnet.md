severity: major

# 第 3 輪 併發-sonnet(併發與資源)

實測:在 shared clone 上量 `_nodehome_side`(頂端 0.19 秒〔頂端等於 HEAD 走磁碟〕、起點不共用約 0.8~1.6 秒、75 篇 Systems)、`_nodehome_golive` 的 `git log -S`(0.05 秒)、治理帳 15 MB / 97630 行(每次推送多寫幾行無感)。30 秒軟上限在工具鏈量級守得住;每 ref 各 30 秒、共用函式內部不收截止時間,計劃已誠實寫「軟上限」,不重報。掛鉤只認 130、`_write_lf` 暫存檔名每次唯一、治理帳單行 append,這幾處已讀,無 finding。

## F1 項目檔名只有指紋加編排者,指紋又不含筆記內容,同一篇兩次 prepare 會互蓋,record 拿錯版本的行號與全文
severity: major
blocking: 是
引句:「兩個會談同時對同一篇 prepare,項目檔名帶編排者,不互蓋」
file: `scripts/lumos:26383`
1. 第 2 輪把項目指紋改成「只看程式那一半」(不含筆記 blob),檔名是 `reread-<項目指紋>-<編排者>.md`。同一篇、同一版程式、同一編排者(兩個 claude 會談,或同一會談前後兩次)算出的檔名完全相同,而檔頭記的筆記 blob 編號、筆記行數、範圍終點卻可以不同。
2. 具體場景:會談 A 對 T1 prepare(筆記 N1,120 行)、派出判定者;判定者跑幾分鐘。這期間作者(或同工作目錄的另一個會談)先把筆記改了(N2,135 行,同一份程式沒變,指紋不變——這正是第 2 輪要的行為)再重跑 prepare(例如照掛鉤提醒印的指令)。第二次 `_write_lf` 原子替換,直接蓋掉第一份。判定者交回的報告是針對 N1 的行號,`reread-record` 卻讀檔頭 N2 的行數、從 N2 的 blob 撈「那一行當時的全文」。
3. 結果:行號沒超出範圍就被收下,但紀錄檔的「原句/當時全文」是 N2 那一行,跟判定者看到的 N1 那一行不是同一句;超出範圍就被當壞項丟掉。REVISIT 那天抽 30 行判真假的母體就是這些紀錄,準度量測被污染卻查不出來(`provenance_ok` 只比對 prepared 指紋,指紋相同所以是 true)。計劃自己在〈實務隱患〉宣稱不互蓋,是第 2 輪折法把它弄破的。既有 `note-audit` 的清單指紋含內容所以沒這問題(`_note_audit_render_list` 的指紋),本案照抄檔名慣例卻換了指紋定義。
4. 修法方向:檔名再加筆記 blob 前 8 碼(或範圍終點前 8 碼),或 record 時核對「報告 `prepared:` 指紋 + 檔頭 blob」與判定者實際看到的一致(報告多要求抄一行 note blob)。前者最省。

## F2 提交紀錄檔的指令沒帶路徑,共用工作目錄時會夾帶別的會談已暫存的檔
severity: minor
blocking: 否
引句:「reread-check 只認已提交的紀錄」
file: `docs/lumos-toolchain-knowledge/Projects/守檔筆記對照改動_計劃.md`(第 3 節末段與第 6 節的 `git add governance/reread-verdicts && git commit`)
1. 兩處都寫 `git add governance/reread-verdicts && git commit`,commit 沒有 `-- governance/reread-verdicts`。同工作目錄另一個會談若已 stage 了自己的檔,這個提交會把它們一起帶走(專案記憶「同工作區 add 夾帶」的既知形狀)。
2. 理由放行:只影響提交整潔、不影響本閘正確性;順手把指令改成 `git commit -- governance/reread-verdicts` 即可。

最高等級:major;blocking 共 1 條
