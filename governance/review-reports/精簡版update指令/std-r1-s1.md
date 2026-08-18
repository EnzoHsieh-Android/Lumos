# std-r1 s1 通才席審計報告(精簡版 update spec 升級後 panel)

## Finding 1 [major] hooks 回填與現行 README「刻意不裝任何 hook」的明文立場矛盾,spec 未裁定

引句：「`slim/` 新增 `hooks/`(內容=Citrus_Lumos 現行兩支,含 2026-08-18 檔頭修真——發行 repo 是它們目前唯一真身,搬回工廠)」

slim/README.md 現行第 227 行「本精簡版刻意不裝任何 hook」為刻意的產品邊界聲明非意外漂移。spec 未處理:①該聲明是否撤銷/憑什麼②回填後段落並存不矛盾③hooks 搬回後 install.py 是否動用或純夾帶。照字面執行會產出自我矛盾或悄悄反轉既有裁定卻無決策紀錄的 README。

## Finding 2 [major] 散落掃的機械測試斷言窄於 spec 宣稱的掃描範圍,已知殘留字串測不到

引句：「散落掃關鍵詞:凍結/不會有更新/不是發布通道/update——★範圍=`slim/` 全目錄(README+所有 .py/.sh/.ps1 的執行期輸出),非僅 README」

slim/README.md 第 161 行「本包是凍結快照,不會有真正的新版本可拉,見下方〈凍結聲明〉」——含「凍結」但逐字不含「不會有更新」,唯一機械斷言抓不到;且其指向的〈凍結聲明〉標題改名後成懸空引用。折入折不乾淨同型。

## Finding 3 [minor] 誠實面誤指產物檔名為「lumos.py」

引句：「Windows 自我覆寫(install.py copyfile 蓋住執行中的 lumos.py)理論上可行(python 編譯後不鎖檔)」

_install_cli 覆寫目標=`lumos`(無副檔名)與 `lumos.cmd` shim;交付包無 lumos.py。壞引用。

## Finding 4 [minor] 全域旗標前置情境未被誠實面揭露

引句：「產物 `def main():` 行後插入 argv 前置攔截(**`len(sys.argv) > 1 and sys.argv[1] == "update"`** → `return _slim_update()`——攔在 argparse 前,免動子命令註冊手術」

`lumos --vault X update` 時 argv[1]="--vault" 不命中→落 argparse invalid choice(非 crash 但呼不到 _slim_update);誠實面未揭露、測試無此排列。

max severity: major
