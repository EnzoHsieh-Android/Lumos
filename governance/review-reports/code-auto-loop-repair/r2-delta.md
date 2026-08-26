### d-f1 skip 分支 covered 寫失敗的安全網被同輪 continue 打穿,gap 無聲永久消失
severity: major
引句:「留給 trap 放回(code-r1 ext-f1:不准寫失敗還標已處置)」
佐證:file: `governance/autonomous-loop.sh:375`
說明:失敗分支接 continue,迴圈重選 gap 把 $GAP_JSON 蓋掉;trap 只認當下值,舊 gap 已被 pop 又不在任何變數。席位以 chmod 唯讀 covered 實跑重現:log 講「改由收尾放回」,結束後三個檔案查無此 gap,$42 已燒。r1 要堵的洞在此重開更隱蔽版。

### d-f2 整跑鎖 mkdir 與寫 PID 之間 TOCTOU,空 pid 被當殘鎖,兩行程可同時進臨界區
severity: major
引句:「OLDPID="$(cat "$LOCKDIR/pid" 2>/dev/null || echo '')"」
佐證:file: `governance/autonomous-loop.sh:17`
說明:「pid 還沒寫」與「pid 寫過但行程死了」走同一條接管路;席位放大窗口重現兩行程都 holds lock。既有兩條鎖測試都先寫好 pid 才起跑,沒測窗口。

### d-f3 in-flight 回收:requeue 失敗照樣刪標記,log 永遠講「已放回」
severity: major
引句:「殘留的選中 gap 已放回($RQ0)"」
佐證:file: `governance/autonomous-loop.sh:97`
說明:RQ0='?' 時 rm -f 照跑、唯一證據自我銷毀;finalize 的 rm(:72)同款不看 RQ。斷電當下正是檔案系統最容易怪、python 最容易再錯的時候,回收路徑缺了 skip 分支同輪立的「成功才算數」防線。

### d-f4 covered 壞行每次 load 重覆撈進 .bad,無界增長;「跟 backlog 同款」宣稱不成立
severity: major
引句:「逐行容錯(code-r1 s3-f3/conf-f1):covered 跟 backlog 同款 append-only jsonl,」
佐證:file: `governance/autonomous_loop/gap_select.py:25`
說明:backlog 壞行被下一次 _save 整檔重寫自然移除(一次性);covered 永遠 append-only 無重寫,同一壞行實測 4 次 load 疊 4 份進 .bad+4 次警告,跨執行永久重複。backlog 測試斷言太鬆(assertIn 不驗次數)。

## 逐項查過乾淨
封閉列舉 13 值全覆蓋;state 先落原子;歸檔尾段自驗+防黏;converged 路徑 ext-f2 正確(直線無 continue);record 集合比對;_save PID 後綴。
