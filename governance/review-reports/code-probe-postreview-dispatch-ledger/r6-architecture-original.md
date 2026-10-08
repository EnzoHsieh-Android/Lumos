severity: major

## Finding ARCH6-01
severity: major
blocking: 是
引句:「umask = os.umask(0)
    os.umask(umask)」
file: `scripts/lumos:14941`(對照 `scripts/test_lumos.py:2100`、`scripts/lumos:14944`)
- 既有做法:專案的原子寫入原語 `_write_lf` 明文寫著「★不用 mkstemp 再改權限★」,理由是讀 umask 要「設成 0 再設回來」,那一瞬間別的執行緒建的檔權限會錯。
- 它的做法是用 `os.open(tmp, O_WRONLY|O_CREAT|O_EXCL, 0o666)`,讓 umask 自己生效,不碰程序級狀態。
- 測試 `t_write_lf_perm...` 還釘著「_write_lf 不碰整個程序的 umask」(`scripts/test_lumos.py:2100`)。
- 這次新增的 `_atomic_write_bytes` 做了專案已否決的事:先用 `NamedTemporaryFile`(0600),再用 `os.umask(0)` 加還原去讀 umask,最後 `fchmod`。
- 隱患:`_atomic_write_bytes` 同樣被消融腳本 import,可能多執行緒呼叫,存在同一個競態。
- 這是第二種做法,而且是專案自己寫進測試的反例。
- 修法是改用 `O_EXCL|0o666` 開暫存檔,再視需要 `fchmod`,或者在筆記裡寫明為何這裡可以破例。
- 不一致 1 檔(`scripts/scenario_probe.py`)。
- 表態記錄 `py-hotpath`/`py-parallel` 答的是 na/satisfied,這條跟那兩題對不上,屬張力。

## Finding ARCH6-02
severity: minor
blocking: 否
引句:「old.st_uid == os.geteuid():
        mode = stat.S_IMODE(old.st_mode) & 0o666」
file: `scripts/lumos:14946`
- 既有 `_write_lf` 對既有檔一律 `shutil.copymode`,不看擁有者。
- 這次新增「擁有者是自己才沿用權限,否則用 0o666 去掉 umask」。
- 專案裡 `geteuid` 先前只用來判斷「是不是 root」(`scripts/test_lumos.py:9375`、`27416` 等),沒有拿來決定權限策略的先例。
- 這是新的權限策略,不是命名或日誌的差異,所以我標 minor 加 ⚠ 交編排者判斷:算「第二種做法」就升 major。
- 既有 X:copymode 不看擁有者。隱患 Y:別人預先放好的寬權限檔會被繼承。這次 Z:加擁有者判斷。不一致 1 檔。

## Finding ARCH6-03
severity: minor
blocking: 否
引句:「with patch.object(mod.os, "geteuid", return_value=wide.stat().st_uid + 1):」
file: `scripts/test_lumos.py:11434`(既有的 `mock.patch.object` 用法;沒有 patch `os.geteuid` 的先例)
- `mod.os` 就是全域的 `os` 模組,所以這個 patch 在 with 區塊內影響整個程序,不只探針模組。
- 既有 patch 都是針對被測模組的函式或 `sys.argv` 這類範圍窄的物件。
- 子程序測試的先例是 `_bootstrap_run`,用 `stdin=DEVNULL` 加 `setsid`(`scripts/test_lumos.py:9686-9696`)。
- 新增的 `t_confirm_tty_no_ctty_session_survives` 用 `start_new_session=True`,跟那個先例一致;`SceneOnly` 的 `_SrcOnly` 守衛也比照 `os.setsid` 檢查。
- 不一致 1 檔。

## Finding ARCH6-04
severity: minor
blocking: 否
引句:「from scenario_probe import _atomic_write_bytes  # 原子寫入同樣只留探針那一份」
file: `governance/eval/ablation_lumos_first.py:33`(對照 `governance/eval/retrieval_eval_multiword.py:31`)
- 既有:`governance/eval` 用 `sys.path.insert` 加上 `# noqa: E402 ★單一實作來源★` 去 import 公開函式與常數。
- 這次的 import 方式本身一致(沿用同一個 `sys.path.insert`),也消掉了一份重抄的實作,方向是對的。
- 差異:這是第一次 import 下劃線私有名,而且另開一行,沒有併進上面那個 import,也沒有 `# noqa: E402`。
- 消融腳本還留著自己的 `_atomic_write_text` 薄包裝,跟探針的同名函式重複。
- 隱患:探針把私有名改掉,消融腳本才會壞。
- 不一致 1 檔。

## 三問

1. **分層與依賴方向:對齊,沒有跨層直呼。**
   - 新碼放在 `scripts/scenario_probe.py`,由它的 `main()`(`scripts/scenario_probe.py:1102` 附近)呼叫,再由 `governance/eval/ablation_lumos_first.py` 向下 import。
   - 這個方向跟既有 `ablation_lumos_first.py:33` 與 `retrieval_eval_multiword.py:31` 一致。
   - 唯一差異是 import 私有名(見 ARCH6-04),屬 minor,不是跨層。
   - `scripts/lumos` 沒有被牽連,所以沒有橫向的跨檔呼叫。

2. **命名與錯誤處理:對齊。**
   - `_output_target_problem` 回傳「字串或 None」,呼叫端印 `✗ … ,停手` 並 `return 2`,這跟 `scenario_probe.py` 既有的 `✗ --runs 至少 1` 寫法逐字同形(同檔 `1107-1111`)。
   - `_atomic_write_bytes` 對唯讀檔 raise `PermissionError(13, …, path)` 是標準 OSError 形狀。
   - 既有呼叫端 `:1357` 本來就沒有 try 包它,所以沒有新的不一致。
   - 歷史檔用 `os.open(... O_APPEND|O_NOFOLLOW)`,跟 `scripts/lumos:15835` 一致;`scripts/lumos:7907` 也有同形的 `getattr(os, "O_NOFOLLOW", 0)` 寫法。
   - 暫存檔名 `.probe-out-*.tmp` 跟 `_write_lf` 的 `名.pid-uuid.tmp-wlf` 不同,但原本探針就用 `NamedTemporaryFile`,不算新做法。

3. **第二種做法:有。**
   - 程序級 `os.umask(0)` 讀取:專案明文否決並有測試釘住,是第二種做法(ARCH6-01,major)。
   - 以擁有者決定沿用權限:沒有先例,標 ⚠(ARCH6-02)。
   - `O_NOFOLLOW` 開檔:有先例,對齊。
   - 測試 patch `os.geteuid` 模擬他人:沒有先例,而且 patch 的是全域 `os`(ARCH6-03)。

總結:不對齊共 4 條,其中 major 1 條
