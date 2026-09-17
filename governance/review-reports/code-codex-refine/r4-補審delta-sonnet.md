severity: major

# 補審對象

`governance/review-reports/code-codex-refine/r4-delta-snapshot.patch`(commit ad354e5f,r3 補的第二刀:標記目錄整條路徑不得經過 symlink)。這是跑滿三輪代碼審上限之後、作者自己補的修法與測試,從沒有任何審查席看過。以下全部發現都是在自己開的臨時目錄(`mktemp -d` 出來的 HOME/repo 副本)裡實跑驗證,沒有在 repo 根目錄動 commit/reset/restore/checkout/stash,也沒有改動 repo 裡任何檔案。

# 逐項回答

**1. 修法對不對、會不會自我抵銷、擋不擋得住合法的家目錄是 symlink**

修法是:
```
if d.resolve() != (Path.home().resolve() / ".cache" / "lumos" / "stop-block"):
    return False
```
這裡只對「家目錄」那一段呼叫 `.resolve()`,後面 `.cache` / `lumos` / `stop-block` 是用 `/` 字面接上去的純字串組合,不會再觸發檔案系統解析;真正會走過所有 symlink 的只有左邊的 `d.resolve()`。所以父層(`~/.cache` 或 `~/.cache/lumos`)被換成指向別處的 symlink 時,左邊會被解析到別的地方、右邊仍停在字面路徑,兩邊必然不相等,擋得住——不是把整個「預期路徑」一起 `.resolve()` 那種會自我抵銷的錯法(scripts/lumos 的 `_trusted_private_dir` docstring 裡明確描述過那個「第一版的錯法」,查證所得,見下)。

實測(在臨時 HOME 下直接 import 這支 hook 呼叫 `_stop_dir_ok`):
- 把 `~/.cache/lumos` 換成指向別的目錄的 symlink → `_stop_dir_ok` 回 `False`(擋住)。
- 把家目錄本身換成 symlink(模擬 macOS `/var` → `/private/var` 那種合法情境)→ `_stop_dir_ok` 回 `True`(沒有被誤擋)。

兩個方向都對,沒有自我抵銷,也沒有錯殺合法情況。

**2. 邊界**

用臨時 HOME 逐一驗證:
- 目錄不存在(從沒 mkdir 過):`_stop_dir_ok` 回 `False`,不擋(fail-open),不會拋例外。
- 中間一段是檔案不是目錄(`~/.cache/lumos` 是普通檔案):回 `False`。
- 權限不足讀不到中間層(`chmod 000 ~/.cache`):`d.stat()`/`d.resolve()` 觸發 `PermissionError`(`OSError` 子類),被既有的 `except OSError: return False` 接住,回 `False`,不炸。
- 目標存在但是檔案不是目錄:走到 `d.is_dir()` 那關被擋,回 `False`。
- Windows(沒有 `os.getuid`):把 `os.getuid` 臨時拿掉模擬,父層仍是 symlink 時 `_stop_dir_ok` 依然回 `False`——這條 resolve 比對本身不靠 `getuid`,在沒有 uid 概念的平台上仍然單獨擋得住父層 symlink,是這次修法的一個附帶好處(不是新問題)。

以上邊界都 fail-closed 或安全地 fail-open,沒有發現讓它誤判為「可信」的組合。

**3. 檢查與使用之間的時間差**

從決定要不要擋到真正寫標記檔,順序是:`stop_block_decision` → `_stop_mark_write` → `_stop_mark_path`(內部呼叫 `_stop_block_dir()`,一次性 `mkdir(parents=True, exist_ok=True, mode=0o700)` 之後跑第一次 `_stop_dir_ok` 檢查,只用來決定要不要 chmod/清理舊檔,不管檢查過不過都把 `d` 交出去)→ 回到 `_stop_mark_write` 再跑第二次 `_stop_dir_ok(mp.parent)` 當作真正的閘 → 過了才 `os.open(..., O_CREAT|O_EXCL|O_WRONLY)`。第二次檢查跟實際 `os.open()` 之間沒有其他 I/O,是同一段程式碼裡的下一行,曝險窗口非常小,但仍然是「先檢查、後使用」的結構,理論上同帳號的另一個行程可以在這條縫裡把目錄換掉(scripts/lumos 對同一種判準明講過這條「誠實邊界」,見發現二)。

比較嚴重的時間差不在這裡,而在更前面:`_stop_block_dir()` 的 `mkdir(parents=True, exist_ok=True, mode=0o700)` 發生在**任何**信任檢查之前——這行不在這次 r3 patch 的 diff 範圍內(patch 只改了 `_stop_dir_ok`),但它是 `_stop_dir_ok` 檢查得到的「檢查對象」的建立者,直接決定這次補的修法能不能把傷害關在「不擋、不寫」這條線之內。實測結果見發現一。

**4. 那條測試釘不釘得住**

把 `_stop_dir_ok` 還原成 r3 之前的樣子(只留 `if d.is_symlink(): return False`,拿掉整段 resolve 比對),在乾淨副本裡重跑 `python3 scripts/test_lumos.py -k t_codex_stop_block_once`:

```
✗ stop-block㉒: 父層 ~/.cache/lumos 是 symlink → 不擋、目標裡的舊檔不被清、不寫標記
✗ FAILED t_codex_stop_block_once(1 條斷言)
23 passed, 1 failed
```

還原之後這條測試真的翻紅,不是零斷言、也沒有斷言到別的東西——`check()` 那行斷言的正是「`decision` 不在 stdout 裡」這件事,還原後 hook 真的寫出 `{"decision": "block", ...}`,斷言精準抓到回歸。這條測試是有效的回歸釘。

**5. 同一件事有沒有寫兩份、判準一不一樣**

`scripts/lumos` 裡有 `_trusted_private_dir(d, *rel_segments)`(`scripts/lumos:24384`),`_lens_arm_dir_ok`(`scripts/lumos:24516`)就是薄殼呼叫它。這支 hook 的 `_stop_dir_ok` 自己重寫了一份等價邏輯(docstring 自己講「跟 scripts/lumos 的 `_lens_arm_dir_ok` 同一套威脅模型」),兩邊的判準式子本質相同(先解析家目錄那一段、後面用字面相對段組回去比對),餵同一個「父層被換成 symlink」的輸入,兩邊回傳的布林值一致(都是 `False`)——這部分沒有分裂。

**但兩邊「檢查前的動作」已經不一樣了**:`scripts/lumos` 今天(2026-09-16,commit `afe6d6a1`)新增了 `_mkdir_trusted_under_home`(`scripts/lumos:24440`),把原本「先 `mkdir(parents=True)` 整條路徑、再檢查」改成「逐層 `mkdir`、逐層檢查,任何一層不過就停手」,理由寫在它自己的 docstring 裡:「檢查不過的時候,連結指到的地方(可能是別人的目錄)已經被建出一層空資料夾了」「這是那幾處★共用的★缺口,不是誰特有」。這支 hook 的 `_stop_block_dir()`(`scripts/hooks/claude/check-graph-sync.py:623`)還停在「先整條 `mkdir(parents=True, exist_ok=True, mode=0o700)`、再呼叫 `_stop_dir_ok`」的舊寫法,r3 這次補的修法完全沒有動到這一行。也就是說:**同一個判準式子被抄了兩份,但支撐它的「怎麼建目錄」那一層,一份已經修過、一份還是舊的**——這正是本題要找的「兩份、判準不一致」,只是分裂點在呼叫端而不是判準函式本身。詳見發現一。

# 發現

發現一:`_stop_block_dir()` 用一次性 `mkdir(parents=True, exist_ok=True, mode=0o700)` 建出整條路徑,發生在 `_stop_dir_ok` 任何檢查之前;父層被換成 symlink 時,這一行會先在被害目錄裡建出一個屬於本帳號的 0700 空目錄 `stop-block`,之後才輪到檢查把「寫標記檔」擋下來。實測(在臨時 HOME、`~/.cache/lumos` 指向另一棵樹的 `victim` 目錄):
```
mkdir 前 victim 內容: []
mkdir 後 victim 內容: ['stop-block']
_stop_dir_ok(最終) = False
```
即檢查最終仍然正確拒絕、不寫標記檔、不清舊檔,但「在被害目錄裡留下一個空目錄」這個動作已經發生,而且發生在檢查判斷「不信、不碰」之前——跟同一段 docstring 明講的行為承諾矛盾。`scripts/lumos` 在今天(2026-09-16,commit `afe6d6a1`)已經把同一類「先建整條路徑再檢查」的呼叫端全部改成逐層建、逐層檢查(`_mkdir_trusted_under_home`,`scripts/lumos:24440`),而且它的 docstring 明講這正是「那幾處★共用的★缺口,不是誰特有」;這支 hook 宣稱和 `_lens_arm_dir_ok` 同一套威脅模型,卻沒有跟進這個修法。這一行(`scripts/hooks/claude/check-graph-sync.py:623`)不在 r3 這次 patch 的 diff 範圍內,r3 補的只有 `_stop_dir_ok` 本身;但 r3 正是這支 hook「重新檢視信任邊界」的時機點,而它經手的正是這個 mkdir 呼叫的檢查對象,沒有一併補上,現狀就是兩邊判準已經分裂。
引句:「不過關=不擋(寧可漏),不在別人的目錄上寫標記」
severity: major
blocking: 是
路徑: `scripts/hooks/claude/check-graph-sync.py:623`(mkdir 整條路徑,查證所得,不在本次 patch diff 範圍內)、`scripts/hooks/claude/check-graph-sync.py:640-642`(被違反的 docstring 承諾,patch 內原有 context)、`scripts/lumos:24440-24484`(查證所得:`_mkdir_trusted_under_home`,今天新修的對照版本)

發現二:`_stop_dir_ok` 的 docstring 只寫「不過關=不擋(寧可漏),不在別人的目錄上寫標記」,沒有像 `scripts/lumos` 的 `_trusted_private_dir` 那樣明講「這是路徑層檢查,擋不住同一個帳號底下的搶跑(TOCTOU)」並附 `REVISIT` 日期(`scripts/lumos:24411`起,查證所得)。這支 hook 確實存在對應的檢查-使用窗口(`_stop_mark_write` 裡 `_stop_dir_ok(mp.parent)` 之後緊接著 `os.open(..., O_EXCL)`,見上方回答 3),但 r3 這次補判準的同時沒有把這條「誠實邊界」寫回文件——docstring 自己講的是「跟 scripts/lumos 的 `_lens_arm_dir_ok` 同一套威脅模型」,實際卻沒有把那套威脅模型裡「承認擋不住什麼」的那部分一起抄過來。這是文件精度落差,不影響行為(邊界情境全部 fail-closed 或安全 fail-open,見回答 2),不是新的可被利用漏洞。
引句:「跟 scripts/lumos 的 _lens_arm_dir_ok 同一套威脅模型」
severity: minor
blocking: 否
路徑: `scripts/hooks/claude/check-graph-sync.py:640-642`

# 附:重現指令(供人照抄驗證)

還原 r3 修法看測試翻紅:
```bash
TMP=$(mktemp -d)
cp -R /path/to/lumos-toolchain "$TMP/repo"
cd "$TMP/repo"
python3 - <<'PY'
p = "scripts/hooks/claude/check-graph-sync.py"
s = open(p, encoding="utf-8").read()
old = '''        # r3 delta:父層(~/.cache 或 ~/.cache/lumos)是 symlink 也一樣——家目錄以下整條路徑不得經過 symlink
        # (家目錄本身可以是 symlink,macOS /var→/private/var 那種),所以拿「家目錄解析後 + 固定相對路徑」對照
        if d.resolve() != (Path.home().resolve() / ".cache" / "lumos" / "stop-block"):
            return False
'''
assert old in s
open(p, "w", encoding="utf-8").write(s.replace(old, ""))
PY
python3 scripts/test_lumos.py -k t_codex_stop_block_once
```

驗證發現一(mkdir 留下殘留):
```bash
python3 - <<'PY'
import importlib.util, os, shutil
from pathlib import Path
BASE = Path("/tmp/probe_boundary_root2"); shutil.rmtree(BASE, ignore_errors=True); BASE.mkdir()
spec = importlib.util.spec_from_file_location("cgs", "/path/to/lumos-toolchain/scripts/hooks/claude/check-graph-sync.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
h = BASE / "home"; (h / ".cache").mkdir(parents=True)
victim = BASE / "victim"; victim.mkdir()
os.symlink(victim, h / ".cache" / "lumos")
os.environ["HOME"] = str(h)
print("mkdir 前:", os.listdir(victim))
d = m._stop_block_dir()
print("mkdir 後:", os.listdir(victim))
print("_stop_dir_ok:", m._stop_dir_ok(d))
PY
```
