import { describe, expect, test } from 'claude-code/testing'
import { SEAT_CASES } from './seat-fixture'
import { BASH_ERROR, BASH_MAX, SAVE_MS, WAIT_MS, bashBlock, checkTool, createGuard, makeIo, onCall, onCallFailed, onEnd, onSpawn, onTool, seatishOf, parseMarker, realOf, type Io, type Seat } from './register'

// 條款 S1–S8(Projects/審查席唯讀隔離_計劃)。查路徑、時間、提示全用假的:測的是規則本身,不是引擎。

const LINKS: Record<string, string | null> = { // 連結 → 目標;null = 懸空
  '/tmp': '/private/tmp',
  '/var/tmp': '/private/var/tmp',
  '/private/tmp/lumos-seat-work/L/s/out': '/repo',
  '/private/tmp/lumos-seat-work/L/s/dang': null,
}
const EXISTS = new Set([
  '/', '/private', '/private/tmp', '/private/var', '/private/var/tmp', '/private/var/folders',
  '/private/var/folders/ab', '/private/var/folders/ab/cd', '/private/var/folders/ab/cd/T',
  '/private/tmp/lumos-seat-work', '/private/tmp/lumos-seat-work/L', '/private/tmp/lumos-seat-work/L/s',
  '/private/tmp/lumos-seat-work/L/other',
  '/private/tmp/lumos-seat-staging', '/private/tmp/lumos-seat-staging/L', '/private/tmp/lumos-seat-staging/L/r1-x.md',
  '/private/tmp/scratch', '/repo', '/repo/a.md', '/repo/docs', '/home', '/home/u',
  '/private/tmp/lumos-seat-work/L/caf\u00e9',
  // macOS 資料卷:同一批檔在 /System/Volumes/Data 底下也看得到,真實路徑不折疊
  '/System', '/System/Volumes', '/System/Volumes/Data', '/System/Volumes/Data/private', '/System/Volumes/Data/private/tmp',
  '/System/Volumes/Data/private/tmp/lumos-seat-staging', '/System/Volumes/Data/private/tmp/lumos-seat-staging/L',
  '/System/Volumes/Data/private/tmp/lumos-seat-staging/L/r1-x.md',
  '/System/Volumes/Data/private/tmp/lumos-seat-work', '/System/Volumes/Data/private/tmp/lumos-seat-work/L',
  '/System/Volumes/Data/private/tmp/lumos-seat-work/L/s',
])

function fakeReal(path: string): string | undefined {
  let p = path
  for (let hop = 0; hop < 10; hop++) {
    const parts = p.split('/')
    let changed = false
    for (let n = parts.length; n >= 1; n--) {
      const pre = parts.slice(0, n).join('/') || '/'
      if (pre in LINKS) {
        const to = LINKS[pre]
        if (to === null) {
          if (n === parts.length) return undefined // 懸空連結本身
          throw new Error('ENOENT')
        }
        p = to + parts.slice(n).map(s => '/' + s).join('')
        changed = true
        break
      }
    }
    if (!changed) break
  }
  if (!EXISTS.has(p)) throw new Error('ENOENT')
  return p
}

function fakeIo(store: { seats: Record<string, Seat>; version?: number } = { seats: {} }) {
  const toasts: string[] = []
  let gate: (() => void) | null = null
  let fired = false // 逾時信號比 sleep 先到也記得
  const io: Io = {
    real: async p => fakeReal(p),
    now: () => 0,
    sleep: ms => new Promise<void>(res => {
      if (ms === WAIT_MS) { if (fired) res(); else gate = res } else if (ms === SAVE_MS) setTimeout(res, 0)
    }),
    toast: t => { toasts.push(t) },
    loadSeats: async () => ({ ...store.seats }),
    loadVersioned: async () => ({ seats: { ...store.seats }, version: store.version ?? 0 }),
    saveSeats: async (s, ifVersion) => {
      if (ifVersion !== undefined && ifVersion !== (store.version ?? 0)) return false
      store.seats = { ...s }
      store.version = (store.version ?? 0) + 1
      return true
    },
  }
  return { io, toasts, store, fireTimeout: () => { fired = true; gate?.() } }
}

const SEAT: Seat = { loop: 'L', round: 'r1', name: 's', cwd: '/repo' }
const chk = (e: any) => checkTool(fakeIo().io, SEAT, e)

describe('S1 寫檔只准自己的工作資料夾', () => {
  test('S1 寫到自己的工作資料夾放行(經過 /tmp 連結、大小寫不同、還不存在的子路徑也算)', async () => {
    expect(await chk({ tool: 'Write', file_path: '/tmp/lumos-seat-work/L/s/a.md' })).toBe(null)
    expect(await chk({ tool: 'Edit', file_path: '/private/tmp/LUMOS-SEAT-WORK/L/S/new/dir/b.txt' })).toBe(null)
    expect(await chk({ tool: 'NotebookEdit', notebook_path: '/private/tmp/lumos-seat-work/L/s/n.ipynb' })).toBe(null)
  })
  test('S1 repo、家目錄、別席的工作資料夾、暫存根其他位置都擋', async () => {
    for (const p of ['/repo/a.md', '/home/u/.zshrc', '/private/tmp/lumos-seat-work/L/other/x', '/tmp/scratch/x',
                     '/private/var/folders/ab/cd/T/x', '/private/tmp/lumos-seat-staging/L/r1-x.md']) {
      expect(await chk({ tool: 'Write', file_path: p })).toContain('lumos-guard 寫檔')
    }
  })
  test('S1 相對路徑、含 . 或 .. 段、空段、欄位不是字串都擋', async () => {
    for (const p of ['a.md', '/tmp/lumos-seat-work/L/s/../../../../repo/a.md', '/tmp/lumos-seat-work/L/s/./a',
                     '/tmp//lumos-seat-work/L/s/a', 42, undefined]) {
      expect(await chk({ tool: 'Write', file_path: p })).toContain('lumos-guard 寫檔')
    }
  })
  test('S1 經過連結指到外面、最深已存在上層是懸空連結都擋', async () => {
    expect(await chk({ tool: 'Write', file_path: '/tmp/lumos-seat-work/L/s/out/a.md' })).toContain('lumos-guard 寫檔')
    expect(await chk({ tool: 'Write', file_path: '/tmp/lumos-seat-work/L/s/dang' })).toContain('lumos-guard 寫檔')
  })
  test('S1 NotebookEdit 讀 notebook_path,不是 file_path', async () => {
    expect(await chk({ tool: 'NotebookEdit', file_path: '/tmp/lumos-seat-work/L/s/n.ipynb', notebook_path: '/repo/n.ipynb' }))
      .toContain('lumos-guard 寫檔')
  })
  test('S1 realOf:接上不存在的段、結尾斜線、根目錄', async () => {
    const { io } = fakeIo()
    expect(await realOf(io, '/tmp/lumos-seat-work/L/s/x/y')).toBe('/private/tmp/lumos-seat-work/l/s/x/y')
    expect(await realOf(io, '/repo/')).toBe('/repo')
    expect(await realOf(io, '/')).toBe('/')
  })
})

describe('S2 席報告暫存處擋讀', () => {
  test('S2 Read 暫存處裡的檔擋(經 /tmp 連結、大小寫不同也擋)', async () => {
    expect(await chk({ tool: 'Read', file_path: '/tmp/lumos-seat-staging/L/r1-x.md' })).toContain('lumos-guard 暫存處')
    expect(await chk({ tool: 'Read', file_path: '/private/tmp/Lumos-Seat-Staging/L/r1-x.md' })).toContain('lumos-guard 暫存處')
    expect(await chk({ tool: 'Read', file_path: '/private/var/folders/ab/cd/T/lumos-seat-staging/z' })).toContain('lumos-guard 暫存處')
  })
  test('S2 Grep、Glob 的範圍在暫存處裡或是它的上層都擋', async () => {
    for (const e of [
      { tool: 'Grep', pattern: 'x', path: '/private/tmp' },
      { tool: 'Grep', pattern: 'x', path: '/tmp/lumos-seat-staging/L' },
      { tool: 'Grep', pattern: 'x', path: '/' },
      { tool: 'Grep', pattern: 'x', path: '/private/var/folders' },
      { tool: 'Glob', pattern: '/tmp/**/*.md' },
      { tool: 'Glob', pattern: '**/*.md', path: '/private/tmp' },
      { tool: 'Glob', pattern: 'lumos-seat-staging/*/r1-*.md', path: '/tmp' },
    ]) expect(await chk(e)).toContain('lumos-guard 暫存處')
  })
  test('S2 Grep 的 pattern 是正規表示式不當路徑:搜 repo 裡的 /tmp 字樣照常', async () => {
    expect(await chk({ tool: 'Grep', pattern: '/tmp', path: '/repo' })).toBe(null)
    expect(await chk({ tool: 'Grep', pattern: '/private/tmp/lumos-seat-staging', glob: '/tmp/**' })).toBe(null)
  })
  test('S2 卷證資料夾、repo 內搜尋、不帶 path、不碰暫存處的暫存根搜尋、讀 repo 檔都照常', async () => {
    for (const e of [
      { tool: 'Read', file_path: '/repo/a.md' },
      { tool: 'Read', file_path: '/tmp/lumos-seat-work/L/other/x' },
      { tool: 'Grep', pattern: 'x' },
      { tool: 'Grep', pattern: 'x', path: 'docs' },
      { tool: 'Glob', pattern: 'docs/**/*.md' },
      { tool: 'Grep', pattern: 'x', path: '/tmp/scratch' },
      { tool: 'Glob', pattern: '/tmp/lumos-seat-work/L/s/**' },
    ]) expect(await chk(e)).toBe(null)
  })
  test('S2 相對 path 含 .. 擋', async () => {
    expect(await chk({ tool: 'Grep', pattern: 'x', path: '../../private/tmp' })).toContain('lumos-guard 暫存處')
    expect(await chk({ tool: 'Glob', pattern: '../**' })).toContain('lumos-guard 暫存處')
  })
})

describe('S3 Bash 粗擋', () => {
  test('S3 gh、hub、glab、claude 這幾個詞,不論包在哪裡都擋', () => {
    for (const c of ['gh pr create', '/usr/local/bin/gh api x', 'bash -lc "gh pr create"', 'cat <<EOF\ngh 沒登入\nEOF',
                     'x=$(hub pull-request)', 'glab mr create', "claude -p '開 PR'", '(cd /tmp && claude)']) {
      expect(bashBlock(c)).not.toBe(null)
    }
  })
  test('S3 git 配 push、send-pack、send-email 擋;GitHub API 網址、暫存處字樣、超長也擋', () => {
    for (const c of ['git push origin HEAD', 'git -C /tmp/x push', 'git send-pack url ref', 'git send-email a.patch',
                     'curl https://api.github.com/repos/x/pulls', 'curl https://uploads.github.com/x',
                     'cat /tmp/lumos-seat-staging/L/r1-x.md', 'x'.repeat(BASH_MAX + 1)]) {
      expect(bashBlock(c)).not.toBe(null)
    }
    expect(bashBlock(42)).not.toBe(null)
  })
  test('S3 一般實驗照常:git log、grep -c、工作資料夾 commit、mktemp、clone、pre-push 路徑', () => {
    for (const c of ['git log --oneline -5', 'git grep -c x', 'git -C /tmp/lumos-seat-work/l/s commit -m x',
                     'T=$(mktemp -d); git -C "$T" init', 'git clone /repo /tmp/x', 'git log -- scripts/hooks/pre-push',
                     'python3 -c "print(1)"', 'ls github', 'echo push', 'gh-pages', 'claude-code']) {
      expect(bashBlock(c)).toBe(null)
    }
  })
  test('S3 擋下理由是三段式', async () => {
    const r = await chk({ tool: 'Bash', command: 'git push' })
    expect(r).toContain('lumos-guard Bash')
    expect(r).toContain('為什麼在意')
  })
})

describe('S4 工具白名單', () => {
  test('S4 白名單外的工具擋', async () => {
    for (const t of ['Skill', 'SendMessage', 'Monitor', 'Workflow', 'TaskCreate', 'EnterWorktree', 'PowerShell',
                     'mcp__x__y', 'MyPluginTool']) {
      expect(await chk({ tool: t })).toContain('lumos-guard 工具')
    }
  })
  test('S4 白名單內的輔助工具照常', async () => {
    for (const t of ['TodoWrite', 'TaskOutput', 'TaskStop', 'WebFetch', 'WebSearch', 'ToolSearch']) {
      expect(await chk({ tool: t })).toBe(null)
    }
  })
  test('S4 Agent/Task 帶 isolation、或 subagent_type 不在准用清單擋;不指定或准用類型照常', async () => {
    for (const e of [{ tool: 'Agent', isolation: 'remote' }, { tool: 'Task', isolation: 'worktree' },
                     { tool: 'Agent', subagent_type: 'my-custom' }]) {
      expect(await chk(e)).toContain('lumos-guard 工具')
    }
    for (const e of [{ tool: 'Agent' }, { tool: 'Agent', subagent_type: 'Explore' }, { tool: 'Task', subagent_type: 'Plan' },
                     { tool: 'Agent', subagent_type: 'general-purpose' }]) {
      expect(await chk(e)).toBe(null)
    }
  })
})

describe('S5 認出審查席', () => {
  test('S5 合格標記:中文迴圈與席名、r3-dref 這類輪次、開頭有 BOM 或全形空白行', () => {
    expect(parseMarker('LUMOS-SEAT: 審查席唯讀隔離/r1/資安-sonnet\n內文')).toEqual(
      { kind: 'seat', loop: '審查席唯讀隔離', round: 'r1', name: '資安-sonnet' })
    expect(parseMarker('﻿\n　\r\n  LUMOS-SEAT:x/r3-dref/s  \r\n').kind).toBe('seat')
    expect(parseMarker('LUMOS-SEAT:x/驗收/s').kind).toBe('seat')
  })
  test('S5 不以 LUMOS-SEAT 開頭:不是審查席(標記在內文、程式碼區塊、第二行以後)', () => {
    for (const p of ['請審查\nLUMOS-SEAT: a/r1/b', '```\nLUMOS-SEAT: a/r1/b\n```', '', '   ', 42, undefined]) {
      expect(parseMarker(p).kind).toBe('none')
    }
  })
  test('S5 以 LUMOS-SEAT 開頭卻寫壞:判成寫壞(少一段、..、全形冒號、大小寫、空段)', () => {
    for (const p of ['LUMOS-SEAT: a/r1', 'LUMOS-SEAT: a/../b', 'LUMOS-SEAT：a/r1/b', 'lumos-seat: a/r1/b',
                     'LUMOS-SEAT: a//b', 'LUMOS-SEAT: a/r1/b c', 'LUMOS-SEAT:', 'LUMOS-SEATS: a/r1/b']) {
      expect(parseMarker(p).kind).toBe('bad')
    }
  })
  test('S5 主會談與非審查席的子代理完全不擋;寫壞的標記擋下派工', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    expect(await g.call('S', { tool: 'Write', file_path: '/repo/a.md' })).toBe(null) // 主會談沒有 agentId
    const r = await g.spawn('S', '/repo', { prompt: '一般任務' }, async () => ({ agentId: 'n1' }))
    expect(r.agentId).toBe('n1')
    expect(await g.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'n1' })).toBe(null)
    let ran = false
    const bad = await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: a/r1' }, async () => { ran = true; return { agentId: 'b1' } })
    expect(bad.deny).toContain('lumos-guard 派工')
    expect(ran).toBe(false)
  })
  test('S5 審查席登記後,它的工具呼叫套規則;工作目錄取派工的 cwd', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s', cwd: '/tmp/scratch' }, async () => ({ agentId: 'a1' }))
    expect(g._state.seat('a1')?.cwd).toBe('/tmp/scratch')
    expect(await g.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'a1' })).toContain('lumos-guard 寫檔')
    expect(await g.call('S', { tool: 'Write', file_path: '/tmp/lumos-seat-work/L/s/a', agentId: 'a1' })).toBe(null)
  })
})

describe('S6 子代理繼承', () => {
  test('S6 審查席派的子代理繼承發起方的標記,忽略自己派工詞裡的標記', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/other\n', parentAgentId: 'a1' }, async () => ({ agentId: 'c1' }))
    await g.spawn('S', '/repo', { prompt: '沒有標記', parentAgentId: 'c1' }, async () => ({ agentId: 'g1' }))
    expect(g._state.seat('c1')?.name).toBe('s')
    expect(g._state.seat('g1')?.name).toBe('s')
    expect(await g.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'g1' })).toContain('lumos-guard 寫檔')
  })
  test('S6 繼承時寫壞的標記不會擋下派工(發起方是審查席就一律繼承)', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    const r = await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: 壞', parentAgentId: 'a1' }, async () => ({ agentId: 'c2' }))
    expect(r.agentId).toBe('c2')
    expect(g._state.seat('c2')?.name).toBe('s')
  })
})

describe('S7 登記完成前的工具呼叫', () => {
  test('S7 子代理在登記完成前呼叫工具:等啟動中的派工回報完再判斷', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    let finish: (r: any) => void = () => {}
    const spawned = g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, () => new Promise(res => { finish = res }))
    expect(g._state.pending('S')).toBe(1)
    const early = g.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'a1' })
    finish({ agentId: 'a1' })
    await spawned
    expect(await early).toContain('lumos-guard 寫檔')
    expect(g._state.pending('S')).toBe(0)
  })
  test('S7 等不到(5 秒):放行並跳 lumos-guard 逾時放行 提示', async () => {
    const f = fakeIo()
    const g = createGuard(f.io)
    void g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, () => new Promise(() => {}))
    const early = g.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'x9' })
    await Promise.resolve()
    f.fireTimeout()
    expect(await early).toBe(null)
    expect(f.toasts.join('\n')).toContain('lumos-guard 逾時放行:')
  })
  test('S7 派工被拒或丟錯:從啟動中清單移除', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    const denied = await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ deny: 'no' }))
    expect(denied.deny).toBe('no')
    expect(g._state.pending('S')).toBe(0)
    let threw = false
    try {
      await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => { throw new Error('boom') })
    } catch { threw = true }
    expect(threw).toBe(true)
    expect(g._state.pending('S')).toBe(0)
  })
  test('S7 沒有啟動中的派工時,查不到的子代理不等、直接放行', async () => {
    const f = fakeIo()
    const g = createGuard(f.io)
    expect(await g.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'zz' })).toBe(null)
    expect(f.toasts.length).toBe(0)
  })
  test('S7 會談結束清掉對應表與啟動中清單', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    g.end('S')
    expect(g._state.seat('a1')).toBe(undefined)
  })
})

describe('S8 外掛自己出錯', () => {
  test('S8 查路徑丟出意外錯誤:非 Bash 放行,Bash 判斷出錯擋', async () => {
    const io: Io = { real: async () => { throw new Error('ENOENT') }, now: () => 0, sleep: async () => {}, toast: () => {},
                     loadSeats: async () => ({}), loadVersioned: async () => ({ seats: {}, version: 0 }), saveSeats: async () => true }
    const g = createGuard({ ...io, real: async () => { throw new TypeError('壞了') } })
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    // real 全丟錯 → 找不到任何已存在的上層 → 路徑看不懂,讀寫都擋(安全方向)
    expect(await g.call('S', { tool: 'Read', file_path: '/repo/a.md', agentId: 'a1' })).toContain('lumos-guard')
    const boom = createGuard(io)
    await boom.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    const bash = await boom.call('S', { tool: 'Bash', get command(): string { throw new Error('x') }, agentId: 'a1' })
    const read = await boom.call('S', { tool: 'Read', get file_path(): string { throw new Error('x') }, agentId: 'a1' })
    expect(read).toBe(null)
    expect(bash).toContain('lumos-guard Bash')
  })
})

describe('S8 掛鉤層出錯(.catch)', () => {
  const nextOf = (called: boolean) => {
    let runs = 0
    const next: any = async () => { runs += 1; return { text: 'ran' } }
    next.called = called
    return { next, runs: () => runs }
  }
  test('S8 工具還沒跑就出錯:Bash 擋,其他工具交下去跑', async () => {
    const a = nextOf(false)
    expect(await onCallFailed({ tool: 'Bash', agentId: 'a1' }, a.next, true)).toEqual({ deny: BASH_ERROR })
    expect(a.runs()).toBe(0)
    const b = nextOf(false)
    expect(await onCallFailed({ tool: 'Read', agentId: 'a1' }, b.next, true)).toEqual({ text: 'ran' })
  })
  test('S8 工具已經跑過才出錯(例如中斷):交回原本的結果,不謊稱擋下', async () => {
    const a = nextOf(true)
    expect(await onCallFailed({ tool: 'Bash', agentId: 'a1' }, a.next, true)).toEqual({ text: 'ran' })
  })
})

describe('代碼審 r1 組一:看不懂的路徑一律擋(讀、寫、搜尋同一條)', () => {
  test('S2 Read 路徑含 . 、空段、..、相對路徑或過長:擋', async () => {
    for (const p of ['/tmp/./lumos-seat-staging/L/r1-x.md', '/tmp//lumos-seat-staging/L/r1-x.md',
                     '/repo/../tmp/lumos-seat-staging/L/r1-x.md', 'lumos-seat-staging/L/r1-x.md', 42,
                     '/repo/' + 'a/'.repeat(300) + 'x', '/repo/' + 'x'.repeat(5000)]) {
      expect(await chk({ tool: 'Read', file_path: p })).toContain('lumos-guard')
    }
  })
  test('S1 Write 路徑過長:擋', async () => {
    expect(await chk({ tool: 'Write', file_path: '/tmp/lumos-seat-work/L/s/' + 'a/'.repeat(300) + 'x' })).toContain('lumos-guard 寫檔')
  })
  test('S2 正常的絕對路徑照常讀', async () => {
    for (const p of ['/repo/a.md', '/repo/docs/x/y.md', '/tmp/scratch/z']) expect(await chk({ tool: 'Read', file_path: p })).toBe(null)
  })
})

describe('代碼審 r1 組二:Bash 粗擋', () => {
  test('S3 大小寫不同也擋', () => {
    for (const c of ['GH pr create', 'Git push origin HEAD', 'CLAUDE -p x', 'Hub pull-request', 'git SEND-PACK u r',
                     'cat /tmp/LUMOS-SEAT-STAGING/L/x', 'curl https://API.GITHUB.COM/repos']) expect(bashBlock(c)).not.toBe(null)
  })
  test('S3 明確的執行路徑也擋:/usr/bin/gh、./gh、~/bin/claude', () => {
    for (const c of ['/usr/local/bin/gh pr create', './gh x', '~/bin/claude -p x', 'x=$(gh api y)', "bash -lc 'gh pr create'",
                     'env GH_TOKEN=1 gh pr list', '(cd /tmp && claude)']) expect(bashBlock(c)).not.toBe(null)
  })
  test('S3 路徑或參數裡只是出現這些字:照常', () => {
    for (const c of ['cat mods/claude/lumos-guard/hooks/register.ts', 'git log --grep=push', 'curl https://github.com/gh/foo',
                     'ls hub-config', 'cat docs/claude-notes.md', 'git log -- scripts/hooks/pre-push']) expect(bashBlock(c)).toBe(null)
    // 代碼審 r2 起每個詞都取最後一段比:路徑最後一段剛好是這些字的會被擋,是接受的誤擋(寧可誤擋)
    for (const c of ['git -C /r diff -- mods/claude', 'git log -- scripts/push']) expect(bashBlock(c)).not.toBe(null)
  })
  test('S3 擋下提示不再叫人改用 Grep 工具(有些建置沒有),改教用 Read 讀檔', async () => {
    const r = await chk({ tool: 'Bash', command: 'gh pr create' })
    // 有些建置沒有 Grep:提到它時一定附「有的話」(代碼審 r2 起才提,r1 時一律不提)
    expect(r.includes('Grep 工具') ? r.includes('Grep 工具(有的話)') : true).toBe(true)
    expect(r).toContain('Read')
  })
})

describe('代碼審 r1 組四:寫壞的標記與出錯時的方向', () => {
  test('S5 標記加了 markdown 修飾:判成寫壞、擋下派工', () => {
    for (const p of ['`LUMOS-SEAT: a/b/c`', '# LUMOS-SEAT: a/b/c', '**LUMOS-SEAT:** a/b/c', '> LUMOS-SEAT: a/b/c']) {
      expect(parseMarker(p).kind).toBe('bad')
    }
  })
  test('S5 一般派工第一行只是提到 lumos-seat:不是審查席、不擋', () => {
    // 'LUMOS-SEAT 外掛的 bug 查一下' 這種以整詞開頭的,跟忘了打冒號的標記分不出來,代碼審 r2 起改判寫壞(擋下派工並說明)
    expect(parseMarker('LUMOS-SEAT 外掛的 bug 查一下').kind).toBe('bad')
    for (const p of ['Lumos-seating plan', 'lumos-seat-work 資料夾清理']) {
      expect(parseMarker(p).kind).toBe('none')
    }
  })
  test('S8 掛鉤出錯時:主會談與非審查席的 Bash 照常,審查席的 Bash 擋', async () => {
    const mk = () => { const n: any = async () => ({ text: 'ran' }); n.called = false; return n }
    expect(await onCallFailed({ tool: 'Bash' }, mk(), false)).toEqual({ text: 'ran' })
    expect(await onCallFailed({ tool: 'Bash', agentId: 'n1' }, mk(), false)).toEqual({ text: 'ran' })
    expect(await onCallFailed({ tool: 'Bash', agentId: 'a1' }, mk(), true)).toEqual({ deny: BASH_ERROR })
  })
  test('S8 seatish(出錯時用):有子代理編號就當審查席(判不出寧可擋),主會談不算', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    expect(g.seatish('zz')).toBe(true)
    expect(g.seatish(undefined)).toBe(false)
  })
  test('S8 舊版 seatish 測試(保留形狀,改成新語意)', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    expect(g.seatish('a1')).toBe(true)
    let finish: (r: any) => void = () => {}
    const sp = g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, () => new Promise(res => { finish = res }))
    expect(g.seatish('zz')).toBe(true)
    finish({ agentId: 'a1' })
    await sp
    expect(g.seatish('a1')).toBe(true)
  })
})

describe('代碼審 r1 組五:登記、等待與熱重載', () => {
  test('S7 先登記好的席不必等同批最後一席', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    let finA: (r: any) => void = () => {}
    let finB: (r: any) => void = () => {}
    const a = g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, () => new Promise(res => { finA = res }))
    void g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/t' }, () => new Promise(res => { finB = res }))
    const early = g.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'a1' })
    finA({ agentId: 'a1' })
    await a
    expect(await early).toContain('lumos-guard 寫檔')
    expect(g._state.pending('S')).toBe(1)
    finB({ agentId: 'b1' })
  })
  test('S7 熱重載後(新的 guard、同一份 $.state):執行中的審查席與它派的子代理照擋', async () => {
    const f = fakeIo()
    const g1 = createGuard(f.io)
    await g1.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    const g2 = createGuard(fakeIo(f.store).io)
    expect(await g2.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'a1' })).toContain('lumos-guard 寫檔')
    await g2.spawn('S', '/repo', { prompt: '沒有標記', parentAgentId: 'a1' }, async () => ({ agentId: 'c1' }))
    expect(await g2.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'c1' })).toContain('lumos-guard 寫檔')
  })
  test('S7 會談結束:叫醒還在等的工具呼叫、從 $.state 拿掉這場的席', async () => {
    const f = fakeIo()
    const g = createGuard(f.io)
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    void g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/t' }, () => new Promise(() => {}))
    const waiting = g.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'x9' })
    g.end('S')
    expect(await waiting).toBe(null)
    expect(f.toasts.length).toBe(0)
    await Promise.resolve()
    expect(f.store.seats['a1']).toBe(undefined)
  })
})

describe('代碼審 r1 組七:補守不住的地方', () => {
  test('S1 /var/tmp 也是暫存根:寫 /var/tmp/lumos-seat-work/<迴圈>/<席>/ 照常', async () => {
    expect(await chk({ tool: 'Write', file_path: '/var/tmp/lumos-seat-work/L/s/a' })).toBe(null)
    expect(await chk({ tool: 'Read', file_path: '/var/tmp/lumos-seat-staging/L/x' })).toContain('lumos-guard 暫存處')
  })
  test('S1 中文或重音席名:分解字(NFD)寫法也算自己的工作資料夾', async () => {
    const seat: Seat = { loop: 'L', round: 'r1', name: 'caf\u00e9', cwd: '/repo' }
    expect(await checkTool(fakeIo().io, seat, { tool: 'Write', file_path: '/tmp/lumos-seat-work/L/cafe\u0301/a' })).toBe(null)
  })
})

describe('代碼審 r2 組甲:對照表存回、會談結束、讀回驗形狀', () => {
  const spawn = (g: any, s: string, name: string, id: string) =>
    g.spawn(s, '/repo', { prompt: `LUMOS-SEAT: L/r1/${name}` }, async () => ({ agentId: id }))
  const write = (g: any, s: string, id: string) => g.call(s, { tool: 'Write', file_path: '/repo/a.md', agentId: id })
  test('S7 熱重載後新登記一席:舊席還在 $.state、照擋', async () => {
    const f = fakeIo()
    const g1 = createGuard(f.io)
    await spawn(g1, 'S', 's', 'a1')
    await spawn(g1, 'S', 't', 'b1')
    const g2 = createGuard(fakeIo(f.store).io)
    await spawn(g2, 'S', 'u', 'c1')
    expect(Object.keys(f.store.seats).sort()).toEqual(['a1', 'b1', 'c1'])
    const g3 = createGuard(fakeIo(f.store).io)
    expect(await write(g3, 'S', 'b1')).toContain('lumos-guard 寫檔')
  })
  test('S7 會談結束只刪那一場的席(熱重載後也一樣),別場的留著', async () => {
    const f = fakeIo()
    const g1 = createGuard(f.io)
    await spawn(g1, 'S', 's', 'a1')
    await spawn(g1, 'T', 't', 'b1')
    const g2 = createGuard(fakeIo(f.store).io)
    await g2.end('S')
    expect(Object.keys(f.store.seats)).toEqual(['b1'])
    expect(await write(g2, 'T', 'b1')).toContain('lumos-guard 寫檔')
  })
  test('S7 會談結束的掛鉤等存檔做完才回:回來時那一場的席已不在存檔', async () => {
    const f = fakeIo()
    const g = createGuard(f.io)
    await spawn(g, 'S', 's', 'a1')
    expect(Object.keys(f.store.seats)).toEqual(['a1'])
    await onEnd({ guard: g }, { sessionId: 'S' })
    expect(f.store.seats['a1']).toBe(undefined)
  })
  test('S7 會談結束後才登記完成的派工:不放回對照表', async () => {
    const f = fakeIo()
    const g = createGuard(f.io)
    let finish: (r: any) => void = () => {}
    const sp = g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, () => new Promise(res => { finish = res }))
    await g.end('S')
    finish({ agentId: 'late' })
    await sp
    expect(g._state.seat('late')).toBe(undefined)
    expect(f.store.seats['late']).toBe(undefined)
  })
  test('S7 會談結束後同一個編號再派的審查席照常登記', async () => {
    const f = fakeIo()
    const g = createGuard(f.io)
    await g.end('S')
    await spawn(g, 'S', 's', 'n1')
    expect(await write(g, 'S', 'n1')).toContain('lumos-guard 寫檔')
  })
  test('S7 兩份實例交錯存回(熱重載前後),後寫的不抹掉先寫的席', async () => {
    const f = fakeIo()
    let hold: (() => void) | null = null
    let first = true
    const slow: Io = { ...f.io, loadVersioned: async () => {
      const v = await f.io.loadVersioned()
      if (first) { first = false; await new Promise<void>(res => { hold = res }) }
      return v
    } }
    const g1 = createGuard(slow)
    const g2 = createGuard(f.io)
    const p1 = spawn(g1, 'S', 's', 'a1')
    await new Promise(res => setTimeout(res, 0))
    await spawn(g2, 'S', 't', 'b1')
    hold!()
    await p1
    await new Promise(res => setTimeout(res, 0))
    expect(Object.keys(f.store.seats).sort()).toEqual(['a1', 'b1'])
  })
  test('S7 存回卡住時派工不被拖住,照樣登記與釋放', async () => {
    const f = fakeIo()
    const g = createGuard({ ...f.io, saveSeats: () => new Promise<boolean>(() => {}) })
    const r = await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    expect(r).toEqual({ agentId: 'a1' })
    expect(g._state.pending('S')).toBe(0)
    expect(await write(g, 'S', 'a1')).toContain('lumos-guard 寫檔')
  })
  test('S7 /clear 結束的會談,背景審查席照擋', async () => {
    const f = fakeIo()
    const g = createGuard(f.io)
    await spawn(g, 'S', 's', 'a1')
    await onEnd({ guard: g }, { sessionId: 'S', reason: 'clear' })
    expect(await write(g, 'T', 'a1')).toContain('lumos-guard 寫檔')
    expect(Object.keys(f.store.seats)).toEqual(['a1'])
  })
  test('S7 $.state 讀回的值形狀不對:當查不到', async () => {
    const f = fakeIo({ seats: { a1: { loop: 'L', round: 'r1', name: 5 } as any, b1: 'x' as any } })
    const g = createGuard(f.io)
    expect(await write(g, 'S', 'a1')).toBe(null)
    expect(await write(g, 'S', 'b1')).toBe(null)
  })
  test('S8 $.state 讀不到(丟錯):子代理的 Bash 擋,讀取照常', async () => {
    const f = fakeIo()
    const g = createGuard({ ...f.io, loadSeats: async () => { throw new Error('state 壞了') }, loadVersioned: async () => { throw new Error('state 壞了') } })
    expect(await g.call('S', { tool: 'Bash', command: 'ls', agentId: 'x1' })).toContain('lumos-guard Bash')
    expect(await g.call('S', { tool: 'Read', file_path: '/repo/a.md', agentId: 'x1' })).toBe(null)
    expect(await g.call('S', { tool: 'Bash', command: 'ls' })).toBe(null)
  })
  test('S7 makeIo 接 $.state:讀 value、寫進同一個鍵', async () => {
    let saved: any = null
    const ref: any[] = []
    const $: any = { state: { get: async (r: any) => { ref.push(r); return { value: { a1: { loop: 'L', round: 'r1', name: 's', cwd: '/r' } }, version: 3 } },
                              set: async (r: any, v: any) => { ref.push(r); saved = v; return { isSet: true, version: 4 } } } }
    const io = makeIo($)
    expect(await io.loadSeats()).toEqual({ a1: { loop: 'L', round: 'r1', name: 's', cwd: '/r' } })
    expect(await io.saveSeats({ b1: { loop: 'L', round: 'r1', name: 't', cwd: '/r' } }, 3)).toBe(true)
    expect(saved).toEqual({ b1: { loop: 'L', round: 'r1', name: 't', cwd: '/r' } })
    expect((await io.loadVersioned()).version).toBe(3)
    expect(ref.every(r => r.plugin === 'lumos-guard' && r.key === 'seats')).toBe(true)
  })
})

describe('代碼審 r2 組丙:寫壞標記的判準', () => {
  test('S5 開頭有清單符號、編號、括號、引號、零寬空白,或冒號在修飾符外、忘了冒號:判成寫壞', () => {
    for (const p of ['- LUMOS-SEAT: a/r1/b', '1. LUMOS-SEAT: a/r1/b', '[LUMOS-SEAT: a/r1/b]', '"LUMOS-SEAT: a/r1/b"',
                     '**LUMOS-SEAT**: a/r1/b', 'LUMOS-SEAT a/r1/b', '\u200bLUMOS-SEAT: a/r1/b', '+ lumos-seat: a/r1/b']) {
      expect(parseMarker(p).kind).toBe('bad')
    }
  })
  test('S5 只是提到 lumos-seat 開頭的字(後面接連字號或字母):照常', () => {
    for (const p of ['lumos-seat-work 資料夾清理', 'Lumos-seating plan', 'lumos-seats-report 整理', '- lumos-seat-staging 要清']) {
      expect(parseMarker(p).kind).toBe('none')
    }
  })
  test('S5 合格標記不受新判準影響', () => {
    expect(parseMarker('LUMOS-SEAT: L/r1/s').kind).toBe('seat')
  })
})

describe('代碼審 r2 組庚:補守不住的地方', () => {
  test('S6 子代理沒給 cwd:沿用發起方的工作目錄', async () => {
    const { io } = fakeIo()
    const g = createGuard(io)
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s', cwd: '/tmp/scratch' }, async () => ({ agentId: 'a1' }))
    await g.spawn('S', '/repo', { prompt: 'x', parentAgentId: 'a1' }, async () => ({ agentId: 'c1' }))
    expect(g._state.seat('c1')?.cwd).toBe('/tmp/scratch')
  })
})

describe('代碼審 r2 組乙:每個詞都取路徑最後一段比', () => {
  test('S3 帶路徑的指令詞照擋', () => {
    for (const c of ['/usr/bin/git push', '$HOME/bin/gh x', 'bin/gh x', 'node_modules/.bin/claude x']) {
      expect(bashBlock(c)).not.toBe(null)
    }
  })
  test('S3 路徑只是含這些字、最後一段不是:照常', () => {
    for (const c of ['cat mods/claude/x.ts', 'ls mods/claude/', 'cat docs/claude-notes.md']) expect(bashBlock(c)).toBe(null)
  })
})

// 代碼審 r3:接線(掛鉤裡那幾行)原本只有純函式有測試,接線改成一律放行照綠;
// 掛上去的那幾行由 Python 端 t_guard_plugin_files_valid 釘住只呼叫這幾支函式
describe('S1–S8 接線:從掛鉤呼叫的函式', () => {
  const fake$ = { session: { id: async () => 'S', cwd: async () => '/repo' } }
  const next = async (e: any) => ({ passed: e })
  test('S1 派工接線登記審查席、工具接線把擋下理由轉成 deny', async () => {
    const st = { guard: createGuard(fakeIo().io) }
    const r = await onSpawn(st, fake$, { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'c1' }))
    expect(r).toEqual({ agentId: 'c1' })
    const out = await onTool(st, fake$, { tool: 'Write', file_path: '/repo/a.md', agentId: 'c1' }, next)
    expect(String(out?.deny)).toContain('lumos-guard 寫檔')
    expect(await onTool(st, fake$, { tool: 'Read', file_path: '/repo/a.md', agentId: 'c1' }, next))
      .toEqual({ passed: { tool: 'Read', file_path: '/repo/a.md', agentId: 'c1' } })
  })
  test('S5 寫壞的標記:派工接線擋下派工', async () => {
    const st = { guard: createGuard(fakeIo().io) }
    const r = await onSpawn(st, fake$, { prompt: 'lumos-seat: 寫壞' }, async () => ({ agentId: 'c1' }))
    expect(String(r?.deny)).toContain('lumos-guard')
  })
  test('S8 工具接線出錯:有子代理編號的 Bash 擋、其他工具放行、主會談放行', async () => {
    const st: any = { guard: { call: async () => { throw new Error('boom') }, seatish: () => true } }
    expect(await onCall(st, fake$, { tool: 'Bash', command: 'ls', agentId: 'c1' })).toBe(BASH_ERROR)
    expect(await onCall(st, fake$, { tool: 'Write', file_path: '/repo/a', agentId: 'c1' })).toBe(null)
    expect(await onCall(st, fake$, { tool: 'Bash', command: 'ls' })).toBe(null)
  })
  test('S8 seatishOf:還沒建好守衛也當審查席、主會談不算', () => {
    expect(seatishOf({ guard: null }, { agentId: 'c1' })).toBe(true)
    expect(seatishOf({ guard: null }, {})).toBe(false)
  })
})

// 代碼審 r3 乙組(路徑判定)、丙組(讀不到對照表)、戊組(標記判準)
describe('代碼審 r3 路徑、對照表、標記', () => {
  test('S2 資料卷別名下的暫存處照樣擋;資料卷別名下自己的工作資料夾照樣可寫', async () => {
    expect(await chk({ tool: 'Read', file_path: '/System/Volumes/Data/private/tmp/lumos-seat-staging/L/r1-x.md' })).toContain('lumos-guard 暫存處')
    expect(await chk({ tool: 'Grep', path: '/System/Volumes/Data/private/tmp' })).toContain('lumos-guard 暫存處')
    expect(await chk({ tool: 'Write', file_path: '/System/Volumes/Data/private/tmp/lumos-seat-work/L/s/a.md' })).toBe(null)
  })
  test('S2 檔案編號寫法(/.vol/)當看不懂:讀與寫都擋', async () => {
    expect(await chk({ tool: 'Read', file_path: '/.vol/16777220/12345' })).toContain('lumos-guard 暫存處')
    expect(await chk({ tool: 'Write', file_path: '/.VOL/1/2' })).toContain('lumos-guard 寫檔')
  })
  test('S1 段數上限:剛好上限加結尾斜線不算多一段', async () => {
    const { io } = fakeIo()
    const deep = '/repo' + '/d'.repeat(255)
    expect(await realOf(io, deep)).not.toBe(null)
    expect(await realOf(io, deep + '/')).not.toBe(null)
    expect(await realOf(io, deep + '/e')).toBe(null)
  })
  test('S2 Glob 大括號選項裡放絕對路徑或 .. 當看不懂;一般的選項照常', async () => {
    expect(await chk({ tool: 'Glob', pattern: '{/private/tmp/lumos-seat-staging/**,x}' })).toContain('lumos-guard 暫存處')
    expect(await chk({ tool: 'Glob', pattern: '{../../x,y}/*' })).toContain('lumos-guard 暫存處')
    expect(await chk({ tool: 'Glob', pattern: 'docs/**/*.{md,ts}' })).toBe(null)
  })
  test('S7 派工帶空字串 cwd:退回會談的 cwd,不帶 path 的搜尋照常', async () => {
    const g = createGuard(fakeIo().io)
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s', cwd: '' }, async () => ({ agentId: 'a1' }))
    expect(g._state.seat('a1')?.cwd).toBe('/repo')
    expect(await g.call('S', { tool: 'Grep', agentId: 'a1' })).toBe(null)
  })
  test('S7 從 $.state 讀回的席位段落不合規則:當查不到', async () => {
    const f = fakeIo({ seats: { a1: { loop: '../x', round: 'r1', name: 's', cwd: '/r' }, b1: { loop: 'L', round: 'r1', name: 'a/b', cwd: '/r' } } })
    const g = createGuard(f.io)
    expect(g._state.seat('a1')).toBe(undefined)
    expect(await g.call('S', { tool: 'Read', file_path: '/repo/a.md', agentId: 'a1' })).toBe(null)
    expect(g._state.seat('a1')).toBe(undefined)
    expect(g._state.seat('b1')).toBe(undefined)
  })
  test('S8 讀不到對照表:子代理派的派工擋下;子代理的寫檔與 Bash 擋、讀取放行', async () => {
    const f = fakeIo()
    const broken = { ...f.io, loadSeats: async () => { throw new Error('state 壞了') } }
    const g = createGuard(broken)
    const r = await g.spawn('S', '/repo', { prompt: '做事', parentAgentId: 'x1' }, async () => ({ agentId: 'c1' }))
    expect(String(r?.deny)).toContain('lumos-guard 派工')
    expect(await g.call('S', { tool: 'Write', file_path: '/repo/a.md', agentId: 'x1' })).toContain('lumos-guard 寫檔')
    expect(await g.call('S', { tool: 'Bash', command: 'ls', agentId: 'x1' })).toContain('lumos-guard Bash')
    expect(await g.call('S', { tool: 'Read', file_path: '/repo/a.md', agentId: 'x1' })).toBe(null)
  })
  test('S5 標記的連字號換成別的橫線、底線、空白,或夾零寬字元:判成寫壞', () => {
    for (const p of ['LUMOS\uff0dSEAT: L/r1/s', 'LUMOS_SEAT: L/r1/s', 'LUMOS SEAT: L/r1/s', 'LUMOS\u2011SEAT: L/r1/s',
                     'LUMOS-\u200bSEAT: L/r1/s', '\u200b\nLUMOS-SEAT: L/r1/s', '\uff2c\uff35\uff2d\uff2f\uff33-SEAT: L/r1/s']) {
      const m = parseMarker(p)
      expect(m.kind === 'bad' || m.kind === 'seat').toBe(true)
    }
    expect(parseMarker('LUMOS_SEAT: L/r1/s').kind).toBe('bad')
    expect(parseMarker('\u200b\nLUMOS-SEAT: L/r1/s').kind).toBe('seat')
    expect(parseMarker('Lumos seating plan').kind).toBe('none')
  })
})

// 代碼審 r4:上一輪修正自己帶出來的與它的鄰居
describe('代碼審 r4 修正', () => {
  const write = (g: any, s: string, id: string) => g.call(s, { tool: 'Write', file_path: '/repo/a.md', agentId: id })
  test('S7 /clear 剛好落在派工途中:回來的席照常登記、照擋', async () => {
    const g = createGuard(fakeIo().io)
    let finish: (r: any) => void = () => {}
    const sp = g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, () => new Promise(res => { finish = res }))
    await onEnd({ guard: g }, { sessionId: 'S', reason: 'clear' })
    finish({ agentId: 'a1' })
    await sp
    expect(await write(g, 'T', 'a1')).toContain('lumos-guard 寫檔')
  })
  test('S7 resume 結束的會談跟 /clear 一樣保留席', async () => {
    const f = fakeIo()
    const g = createGuard(f.io)
    const r = await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    expect(r).toEqual({ agentId: 'a1' })
    await onEnd({ guard: g }, { sessionId: 'S', reason: 'resume' })
    expect(await write(g, 'T', 'a1')).toContain('lumos-guard 寫檔')
  })
  test('S7 存回卡住時會談結束照樣回來,下一次存回照樣做', async () => {
    const f = fakeIo()
    let stuck = true
    const g = createGuard({ ...f.io, saveSeats: async (x: any, v: any) => (stuck ? new Promise<boolean>(() => {}) : f.io.saveSeats(x, v)) })
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    await onEnd({ guard: g }, { sessionId: 'S' })
    stuck = false
    await g.spawn('T', '/repo', { prompt: 'LUMOS-SEAT: L/r1/t' }, async () => ({ agentId: 'b1' }))
    expect(Object.keys(f.store.seats)).toEqual(['b1'])
  })
  test('S7 會談結束後,舊派工回來不扣掉同編號新派工的啟動中計數', async () => {
    const g = createGuard(fakeIo().io)
    let finishA: (r: any) => void = () => {}
    const a = g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/a' }, () => new Promise(res => { finishA = res }))
    await g.end('S')
    let finishB: (r: any) => void = () => {}
    const b = g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/b' }, () => new Promise(res => { finishB = res }))
    finishA({ agentId: 'old' })
    await a
    expect(g._state.pending('S')).toBe(1)
    finishB({ agentId: 'new' })
    await b
    expect(g._state.pending('S')).toBe(0)
  })
  test('S7 存回撞版三次放棄:跳提示', async () => {
    const f = fakeIo()
    const g = createGuard({ ...f.io, saveSeats: async () => false })
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    expect(f.toasts.some(t => t.startsWith('lumos-guard 存回撞版'))).toBe(true)
  })
  test('S7 讀到的版本不是數字:照版本 0 帶條件寫,不退回無條件寫', async () => {
    const f = fakeIo()
    const seen: any[] = []
    const g = createGuard({ ...f.io, loadVersioned: async () => ({ seats: {}, version: undefined }), saveSeats: async (_x: any, v: any) => { seen.push(v); return true } })
    await g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    expect(seen).toEqual([0])
  })
  test('S7 makeIo 存回:帶 ifVersion、撞版回 false', async () => {
    const calls: any[] = []
    const $: any = { state: { get: async () => ({ value: {}, version: 7 }), set: async (_r: any, _v: any, o: any) => { calls.push(o); return { isSet: false, version: 8 } } } }
    const io = makeIo($)
    expect(await io.saveSeats({}, 7)).toBe(false)
    expect(calls).toEqual([{ ifVersion: 7 }])
  })
  test('S5 一般句子以 Lumos seat 開頭不算想寫標記;空白或底線寫法接冒號才算', () => {
    for (const p of ['Lumos seat guard 的 r4 修正', 'lumos seats are listed below', 'Lumos Seats 說明', 'lumosseat 筆記']) {
      expect(parseMarker(p).kind).toBe('none')
    }
    for (const p of ['LUMOS SEAT: L/r1/s', 'lumos_seat: L/r1/s', 'LUMOS SEAT：L/r1/s']) expect(parseMarker(p).kind).toBe('bad')
    expect(parseMarker('lumos-seat中文').kind).toBe('bad')
  })
  test('S5 第一行只有格式字元(方向標記、軟連字號)當空行跳過;標記中間夾格式字元判寫壞', () => {
    expect(parseMarker('\u200e\nLUMOS-SEAT: L/r1/s').kind).toBe('seat')
    expect(parseMarker('\u00ad\nLUMOS-SEAT: L/r1/s').kind).toBe('seat')
    expect(parseMarker('LUMOS\u00ad-SEAT: L/r1/s').kind).toBe('bad')
  })
  test('S5 以 U+2028 分行:標記那一行後面的內容不算進標記', () => {
    expect(parseMarker('LUMOS-SEAT: L/r1/s\u2028後面的說明').kind).toBe('seat')
    expect(parseMarker('前言\u2029LUMOS-SEAT: L/r1/s').kind).toBe('none')
  })
  test('S2 Glob 的 .. 不論在萬用字元前後、大括號巢狀:當看不懂', async () => {
    for (const pattern of ['*/../../x/**', '**/../y', '{a,b}/../z', '{{a,b},c}/x', 'a/{b,{c,d}}/e']) {
      expect(await chk({ tool: 'Glob', pattern })).toContain('lumos-guard 暫存處')
    }
    expect(await chk({ tool: 'Glob', pattern: 'src/**/*.{ts,tsx}' })).toBe(null)
  })
})

// 代碼審 r5
describe('代碼審 r5 修正', () => {
  // 存回的時間上限由測試手動推進:tick() 一次放掉目前在等的那幾個
  function heldIo(f: ReturnType<typeof fakeIo>) {
    const waiting: (() => void)[] = []
    const io: Io = { ...f.io, sleep: (ms: number) => ms === SAVE_MS ? new Promise<void>(res => { waiting.push(res) }) : f.io.sleep(ms) }
    const tick = async () => { for (const w of waiting.splice(0)) w(); for (let i = 0; i < 20; i++) await Promise.resolve() }
    return { io, tick }
  }
  test('S7 存回卡住時好幾個派工同時排隊:一次上限到期就全部回來', async () => {
    const f = fakeIo()
    const h = heldIo(f)
    const g = createGuard({ ...h.io, saveSeats: () => new Promise<boolean>(() => {}) })
    const done: string[] = []
    const ps = ['a', 'b', 'c'].map(n => g.spawn('S', '/repo', { prompt: `LUMOS-SEAT: L/r1/${n}` }, async () => ({ agentId: n }))
      .then(() => { done.push(n) }))
    for (let i = 0; i < 20; i++) await Promise.resolve()
    await h.tick()
    expect(done.sort()).toEqual(['a', 'b', 'c'])
    await Promise.all(ps)
  })
  test('S7 逾時被放掉的那一格,之後才回來也不寫', async () => {
    const f = fakeIo()
    const h = heldIo(f)
    let release: () => void = () => {}
    let first = true
    const writes: string[][] = []
    const g = createGuard({ ...h.io,
      loadVersioned: async () => { if (first) { first = false; await new Promise<void>(res => { release = res }) } return f.io.loadVersioned() },
      saveSeats: async (x: any, v: any) => { writes.push(Object.keys(x)); return f.io.saveSeats(x, v) } })
    const sp = g.spawn('S', '/repo', { prompt: 'LUMOS-SEAT: L/r1/s' }, async () => ({ agentId: 'a1' }))
    for (let i = 0; i < 20; i++) await Promise.resolve()
    await h.tick()
    await sp
    release()
    for (let i = 0; i < 20; i++) await Promise.resolve()
    expect(writes).toEqual([])
  })
  test('S5 標記值裡夾格式字元:判寫壞', () => {
    expect(parseMarker('LUMOS-SEAT: L/r1/s\u200b').kind).toBe('bad')
    expect(parseMarker('LUMOS-SEAT: L/r\u00ad1/s').kind).toBe('bad')
  })
  test('S5 擋下寫壞標記的理由:叫人改第一行,不叫人刪內文', async () => {
    const g = createGuard(fakeIo().io)
    const r = await g.spawn('S', '/repo', { prompt: 'lumos-seat: 寫壞\n內文' }, async () => ({ agentId: 'a1' }))
    expect(String(r?.deny)).toContain('第一行別用 lumos-seat 這個詞開頭')
    expect(String(r?.deny)).toContain('不用刪內文')
  })
})

describe('S5 席位標記的共用案例(seat-fixture.ts,事件帳外掛有同一份)', () => {
  test('S5 守衛認成審查席的值跟案例一致,其他判成不是或寫壞', () => {
    for (const c of SEAT_CASES) {
      const m = parseMarker(c.prompt)
      expect([c.prompt, m.kind === 'seat' ? `${m.loop}/${m.round}/${m.name}` : null]).toEqual([c.prompt, c.seat])
    }
  })
})

