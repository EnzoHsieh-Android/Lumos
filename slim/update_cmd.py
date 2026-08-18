# update_cmd.py — 精簡版 `lumos update` 生成期拼接模板
#
# ★這不是交付檔★:slim-gen 在生成產物 CLI 時把本檔全文拼進去(連同 main() 的
# 前置攔截),之後才跑 ast.parse 語法自檢——模板壞了=生成失敗不出貨,不會壞在
# 使用者端。本檔不進 dist/ 複製清單(拼進 CLI 即可,包裡多一份=雙真相)。
#
# 行為=get.sh 的冪等語意包成指令:pull 固定落點 ~/.lumos-slim(--ff-only)→
# 跑包內 install.py --force --tool-only(只更新工具本身,永不碰專案層)。
# ★update 必須為第一個參數★:前置攔截只認 sys.argv[1]=="update",全域旗標
# 前置(lumos --vault X update)會落回 argparse 的 invalid choice(fail loud)。


def _slim_update():
    """精簡版更新:git pull 固定落點後重跑包內安裝器(--force --tool-only)。
    全路徑 fail loud rc2;任何意外例外(如 HOME 未定義使 Path.home() 拋
    RuntimeError)一律轉一句訊息+rc2,不噴 traceback。"""
    import shutil as _sh
    import subprocess as _sp
    try:
        dest = Path.home() / ".lumos-slim"
        if not (dest / ".git").exists():
            print(f"ERROR: 找不到 {dest}(或不是 git clone)——`lumos update` 只服務"
                  "一行安裝的固定落點。", file=sys.stderr)
            print("  手動 clone 安裝的話:到你的 clone 目錄 git pull 後重跑 install;"
                  "或直接重跑一行安裝(見 README 安裝節)。", file=sys.stderr)
            return 2
        if _sh.which("git") is None:
            print("ERROR: 找不到 git 指令——請先安裝 git 再跑 update。", file=sys.stderr)
            return 2
        r = _sp.run(["git", "-C", str(dest), "pull", "--ff-only"],
                    capture_output=True, text=True)
        if r.returncode != 0:
            print(f"ERROR: {dest} 更新失敗(可能有本地改動,或不是 fast-forward)。",
                  file=sys.stderr)
            print("  " + (r.stderr or r.stdout).strip()[-1000:], file=sys.stderr)   # 截尾保留:實測 git 的 fatal: 關鍵行在尾端(r2 delta 實證,推翻前註解)
            print("  若你動過裡面的檔案:這是 --ff-only 的保護不是壞掉——確認沒有要留"
                  "的東西後,備份/刪掉該目錄再重跑一行安裝。", file=sys.stderr)
            return 2
        _pull_msg = r.stdout.strip().splitlines()
        if _pull_msg:
            print(_pull_msg[0])   # 首行=「Already up to date.」或「Updating a..b」——有沒有拉到新東西一眼可判(r2 delta 實證:末行是 diffstat 碎片)
        inst = dest / "install.py"
        if not inst.is_file():
            print(f"ERROR: {inst} 不存在——交付包內容可能不完整;請重跑一行安裝。",
                  file=sys.stderr)
            return 2
        # 不 capture:安裝器的輸出(含 PATH 提示)原樣給使用者
        r2 = _sp.run([sys.executable, str(inst), "--force", "--tool-only"])
        return r2.returncode
    except Exception as e:   # fail loud 但不噴 traceback(Path.home 之類環境例外)
        print(f"ERROR: update 失敗(環境): {e}", file=sys.stderr)
        return 2
