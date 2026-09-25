severity: major

## F1 顯示的「現在幾 KB」跟「上限幾 KB」用了不同進位,逼近門檻時數字會反過來騙人
severity: major
blocking: yes
引句:「% (size / 1024, lines, _INDEX_MAX_LINES, _INDEX_MAX_BYTES // 1000)」

`index_size_note` 裡「現在 X KB」這段(第 427 行左右)這次改成 `size / 1024`(1024 進位),
但同一句話裡「開場只載入前 …或 %d KB」用的上限數字還是 `_INDEX_MAX_BYTES // 1000`(1000 進位,
沿用舊碼沒改)。新加的註解寫「KB 跟本檔其他地方一樣按 1024 算」,但實際只改了一半,兩個數字
不同基準,逼近門檻時會顯示成「現在的 KB 數比上限還小」,跟訊息本身在講「已經被截掉」自相矛盾。

實測(在 exp-r2 複本跑,repo 唯讀未改):造一個剛好 25000 bytes(等於 `_INDEX_MAX_BYTES`,
b_ratio=1.0,超過 0.95 大聲喊門檻)的 MEMORY.md:

```
記憶索引 MEMORY.md 現在 24.4 KB、1 行;開場只載入前 200 行或 25 KB(取小的),超過的部分開場看不到
——★快被截掉了(或已經截掉)★,新條目加在最後,最先讀不到的是最近學到的經驗。
```

讀者看到的是「現在 24.4 KB」小於「上限 25 KB」,卻被告知「已經被截掉/快被截掉」——這正是
CLAUDE.md 要求的「數字旁一句是什麼+門檻」該互相對得上的地方,這裡對不上。同一個問題也在
`raw is None`(超過單篇上限)那支訊息裡:「有 %d KB,遠超過開場載入上限 %d KB」,size 用
`// 1024`、門檻仍 `// 1000`,只是那支因為數字差距夠大(111 KB vs 25 KB)沒有明顯翻車,
但單位不一致的根因跟上面同一處。

重現步驟:
```
python3 - <<'EOF'
import subprocess, tempfile, sys
from pathlib import Path
hook = Path("scripts/hooks/claude/memory-sweep.py").resolve()
d = Path(tempfile.mkdtemp(prefix="gctl-ms-"))
(d / "MEMORY.md").write_text("a" * 25000, encoding="utf-8")
r = subprocess.run([sys.executable, str(hook), "--dir", str(d), "--quiet"],
                    capture_output=True, text=True, timeout=60)
print(r.stdout)
EOF
```
建議:兩處都改成同一種進位(既然新加的意圖是「跟本檔其他地方一樣按 1024 算」,`_INDEX_MAX_BYTES`
的顯示也一併換成 `// 1024`,或乾脆兩個都留 1000 跟原本一致),別只改一半。

---

已看,無:`_index_bytes` 本體的資安防護邏輯(lstat→_pre_reason→O_NOFOLLOW/O_NONBLOCK 開檔→
fstat 比對 dev/inode→再用 `_pre_reason` 檢查 mode→超過 `MAX_BYTES` 就不讀內容只回大小→
`finally: os.close(fd)`)跟 `_read_own_file`/`_opened_reason` 的防護項目對得上(符號連結、
非一般檔、開檔前後換檔的 TOCTOU、單篇上限),沒有漏掉哪一項;`os.close(fd)` 在所有 return 分支
(含 try 區塊內提早 return)都會透過 `finally` 執行到,沒有漏關或重複關的問題(用
`os.fdopen(fd, ..., closefd=False)` 避免了雙重關閉)。實際跑了三個邊界:①剛好 25000 bytes
(門檻上,確認 F1 的數字問題)、②組出的符號連結(指到目錄外的大檔),用未修改前的 `p.read_bytes()`
版本跑同一測試會讓 ⑤⑥ 兩個新斷言翻紅(重現:把 `_index_bytes` 換回直接 `p.read_bytes()` 後
跑 `python3 scripts/test_lumos.py -k memory_sweep_index_size`,⑤⑥ 皆 FAILED,符合注釋裡
「改回直接讀檔 → ⑤紅」的翻紅釘宣稱,只是實測連⑥也一併翻紅,注釋沒提到⑥,這只是注釋沒寫全、
不影響測試本身有效),③`MEMORY.md` 是目錄的情況,hook 靜默略過不崩潰(對應 `_pre_reason` 的
`S_ISDIR` 分支)。`raw is None` 分支回報的大小來自 `st.st_size`(開檔後 fstat 拿到的真實大小,
非 `len(raw)`),所以「遠超過」訊息裡的 KB 數是準的,不是只讀了 `MAX_BYTES+1` 就拿去充當總檔案
大小(這點原本擔心會有低估風險,實測 111 KB 檔案正確顯示 111 KB)。新增的兩個測試案例(⑤符號
連結、⑥超大檔)本身跑得動、也真的對得上要驗的行為,把測試檔案本體跟本體以外的路徑分開建,沒有
把大檔寫進被測目錄裡混淆計數。全套子集 `python3 scripts/test_lumos.py -k memory_sweep_index_size`
在乾淨複本上 6/6 通過。
