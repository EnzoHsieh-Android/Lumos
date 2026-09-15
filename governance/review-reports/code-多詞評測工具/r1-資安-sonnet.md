severity: blocker

## 發現一：污染守衛只在「重組候選池」那條路徑擋，實際量測（`--labels`）完全不擋，只印到 stderr

引句:「print("  ★重組候選池時不接受污染★:改乾淨再跑一次。", file=sys.stderr)」

這行 `return 2` 的擋，寫在 `if bad:` 底下再巢一層 `if a.rebuild_pool:`（`governance/eval/retrieval_eval_multiword.py:191-193`）。往下讀 `main()` 整段：`bad, docs = contaminated(a.vault, pool)`（`governance/eval/retrieval_eval_multiword.py:181`）算出污染清單之後，只有「有污染 **且** 有帶 `--rebuild-pool`」才會 `return 2`；正常跑量測（帶 `--labels`、不帶 `--rebuild-pool`）那條路徑，`if bad:` 區塊只是把警告印到 `sys.stderr`，接著程式碼原封不動往下跑到 `labels = load_labels(a.labels)`（`governance/eval/retrieval_eval_multiword.py:212`），用被污染的 pool 照常算 nDCG/MRR/precision 並把數字印到 stdout。

我實際跑了一次來確認（不是用診斷 script 演示，是直接跑這支被審的檔）：造一個 vault，讓其中一篇筆記逐字含有題庫的查詢字串（模擬「查詢字面被寫進圖譜」），然後：

```
python3 governance/eval/retrieval_eval_multiword.py --labels labels.json --pool pool.json --vault vault -k 5 2>/dev/null
```

結果：**rc=0**，stdout 印出完整的「量測」報告（候選數、nDCG、MRR、P@5 全部照印），完全沒有任何字樣提到污染——污染訊息只在沒被丟掉的 stderr 才看得到。也就是說：這套工具自己的文件在 diff 開頭就寫了「這是治理用的量測工具，數字會拿去做決定」，而且 `contaminated()` 的 docstring 明白寫著這正是它要擋的事（"整串當片語查"那一臂命中、"拆詞"那一臂不觸發、兩臂量出一樣的數字、且不報錯）——但這支守衛實際只在維護時手動重建候選池那條分支生效，在真正產出治理數字的量測分支形同虛設。凡是把 stdout 導去存檔（治理報告很典型的用法）、或只是沒特別去看 stderr 的人，都會拿到一份「看起來正常、其實某幾題兩臂根本沒測到任何東西」的報告，而且無從察覺。

這正對應題目點 5 問的「有沒有辦法從外面塞一篇筆記，讓分數往想要的方向動而不被發現？」——答案是有，而且不需要用 `--rebuild-pool`，只要平常跑量測就行，訊息還會被最常見的 stdout-only 擷取方式吃掉。

severity: blocker
blocking: 是

## 發現二：`write_json_atomic` 的暫存檔名可預測、寫入前不驗證是不是符號連結——攻擊者可讓它把內容寫穿到任意檔案，且輸出檔本身變成指向該檔的連結

引句:「tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")」

`governance/eval/retrieval_eval_multiword.py:160-165`：

```
def write_json_atomic(path, data):
    path = pathlib.Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)
```

`tmp` 的檔名完全是 `<輸出路徑>.tmp`，沒有任何隨機成分（不是 `tempfile.mkstemp`），而且 `Path.write_text()` 不帶 `O_NOFOLLOW`，遇到符號連結會照樣跟過去寫。我直接對著這支被審的檔案做了一次端到端驗證（沒有另外寫模擬程式）：

1. 準備 `victim/important.txt`（模擬任何操作者帳號寫得到的檔案——repo 內的 `scripts/lumos`、`.git/config`，或 repo 外的 `~/.ssh/authorized_keys`、`~/.bashrc` 都是同一類目標）。
2. 在真正跑重組之前，先手動建一個符號連結 `out.json.tmp -> victim/important.txt`（模擬「污染守衛守不住的另一個管道」：任何能把檔案塞進這個目錄的人或程式，都能預先埋一個同名的 `.tmp` 符號連結）。
3. 執行真正的指令：
   ```
   python3 governance/eval/retrieval_eval_multiword.py --pool pool.json --vault vault --rebuild-pool out.json
   ```
4. 結果：程式印出「✓ 候選池重組好了...→ out.json」、**rc=0**，看起來完全正常。但：
   - `victim/important.txt` 的內容已經被新組好的候選池 JSON **覆蓋掉**（`tmp.write_text()` 跟著符號連結寫穿了目標檔）。
   - `os.replace(tmp, path)` 對符號連結做的是「搬動連結本身」而不是解參照，所以搬完之後 `out.json` 自己也變成一個指向 `victim/important.txt` 的符號連結（`readlink out.json` 印出 `/tmp/.../victim/important.txt`），不是獨立檔案——之後任何人讀 `out.json` 讀到的其實是那個被攻擊者選定的目標檔，之後任何人再對同一個輸出檔名重跑一次，也會繼續透過這個連結寫穿到同一個目標。

被覆蓋的目標檔內容雖然是攻擊者不能自由指定的 JSON（不是任意內容注入），但**目標路徑是攻擊者選的**——這已經是完整的「任意檔案覆寫／破壞」原語：可以拿來打壞 `scripts/lumos`（工具鏈自己）、`.git/config`、`.git/hooks/*`，或 repo 外操作者帳號寫得到的任何檔案，且過程完全靜默（成功訊息照印、rc=0）。對照題目給的門檻——「能塞檔案或塞內容的人或程式」本來就被列進威脅模型（包含被騙的自動化流程、其他會談的 AI）——把符號連結塞進這個目錄，跟塞一篇筆記是同一個信任邊界，而重組候選池的操作者（通常是人或排程）卻是用自己完整的帳號權限在跑這支工具，這正是攻擊者從「只能塞內容」跳板到「能覆寫操作者寫得到的任何檔案」的橋樑，不是「反正同帳號本來就能為所欲為」可以打發的那種等級。

順帶一提，這個 repo 自己在 `scripts/lumos` 裡已經有處理過同一類風險的既有寫法（`os.O_NOFOLLOW`、`tempfile.mkstemp` 給暫存檔一個不可預測的名字，例如 `scripts/lumos:11848`、`scripts/lumos:23838`、`scripts/lumos:25800`），這支新函式沒有沿用，等於重新引入了一個庫裡本來已經修過的洞。

severity: blocker
blocking: 是

## 發現三（次要）：讀語料進記憶體沒有檔案大小上限

`contaminated()`（`governance/eval/retrieval_eval_multiword.py:94-117`）對每一篇 `*.md` 都是整篇 `read_text()` 讀進一個字典、留到 `rebuild_pool()` 共用。作者自己表態的效能數字（528 篇、5.5 MB）是以現有語料規模估的，但程式碼本身沒有任何檔案大小或總量上限。威脅模型裡「能塞檔案的人或程式」如果塞進一篇異常大的 `.md`（例如從外部整包貼進來、忘記裁切），這支工具會整篇讀進記憶體，沒有任何提示或擋停，在跑量測/重組的機器上造成吃記憶體變慢甚至 OOM。影響範圍侷限在「跑這支工具的那次執行」，不會外溢，且前提（能把巨大檔案塞進被追蹤的圖譜目錄）本身也已經是治理上該被攔的事，所以不到 major，僅供參考。

severity: minor
blocking: 否

## 檢查過但沒找到洞的攻擊面

- **子行程參數注入**：`search_files()` 用 `subprocess.run(args, ...)` 的 list 形式呼叫，不經 shell，`query` 是單一 argv token，不會被拆成多個旗標；就算 `query` 剛好整串等於某個旗標字面（如 `"--path"`），最壞結果只是該次 `lumos search` 因缺 `term` 而以非 0 結束、`search_files` 靜默回空清單——候選池的另外兩個來源（`term_top`/`cooccur_top`）不經過這支子行程，不受影響，不構成「分數可被誰刻意操縱到特定方向又不被發現」的管道，跟發現一是不同等級的問題。
- **符號連結導致讀到語料目錄外的內容造成 DoS（目錄穿越式無窮遍歷）**：實際對著這支審的邏輯用的 `pathlib.Path.rglob()` 做了實測（分別用 Python 3.12.13 與 3.14.6 起一個目錄符號連結、一個自我循環符號連結）——兩個版本的 `rglob("*.md")` 都**不會**遞迴進入符號連結的目錄，符號連結本身會被列成一個項目但不會展開，找不到連結指向的檔案。這個假設在我實測前以為是問題，但驗證結果是乾淨的，沒有據此開一條發現。
- **讀進來的內容被當成指令**：`docs` 字典裡的筆記全文只拿去做子字串比對（`q in txt`）和 `str.count()`，沒有任何 `eval`/`exec`/動態 import/以內容決定要開哪個檔案的路徑，讀進來的圖譜內容不會反過來控制這支工具的控制流。
