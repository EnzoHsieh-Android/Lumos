severity: minor

## lint-F1

severity: minor
blocking: 否

引句:「def _nodehome_mark_note_content(repo_root, groups, vault_rel, tag_judge=None, route_cfg=None, route_skip=frozenset()):」

觀察：機械雙版本lint-new在函式加入讀取候選與快取後，Ruff C901由main7增為14，新增告警關卡會擋。
判準：不要把真正增加的複雜度與簽名改變重報的舊告警一起waive。
修法：沿原讀取層抽單一group證據收集與两版cache，mark8/helper6；判定層不新開Git讀取。快取8控制綠，相關原架構釘及nodehome子集另跑。
這是編排者機械補充，不算第八位獨立finder；raw lint-new及乾淨辯方均保留。evaluate52→52的精確waiver另有日期REVISIT，沒有關全閘。
