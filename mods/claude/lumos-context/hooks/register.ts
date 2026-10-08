import type { Register } from 'claude-code'

// lumos-context:壓縮前叫摘要保住交棒狀態(Projects/Claude-mod第二批_計劃)。
// 外掛裝在使用者層、所有專案都會生效,所以附加段的用詞不帶 lumos 專用名詞。
// 不寫檔、不呼叫網路或外部程式、不設環境變數;只改摘要指示。

export const MARK_MAIN = '[lumos-context 交棒要求 v1]'
export const MARK_SUB = '[lumos-context 交棒要求 v1 精簡]'

export const HANDOFF_MAIN = [
  MARK_MAIN,
  '摘要必須逐字保留下列內容,不要改寫或省略:',
  '- 使用者在對話裡下的裁定與指示(原話)',
  '- 目前在做的任務、做到哪一步、下一步是什麼',
  '- 還在跑或剛交回的背景代理,各自負責什麼、結果放在哪',
  '- 還沒提交或還沒推的改動(哪些檔、在哪個分支或工作目錄)',
  '- 還在等使用者回覆的問題',
].join('\n')

export const HANDOFF_SUB = [
  MARK_SUB,
  '摘要必須保留:這個子代理被交代的任務原文、到目前為止得到的結論與證據位置。',
].join('\n')

// 去頭尾空白後整行相等才算已附過;句中引用標記不算
export function hasMark(text: string, mark: string): boolean {
  return text.split('\n').some(line => line.trim() === mark)
}

// 原指示不空時先接一個空行再附;空字串、純空白或沒有指示時直接附
export function withHandoff(instructions: string | undefined, isSub: boolean): string {
  const mark = isSub ? MARK_SUB : MARK_MAIN
  const block = isSub ? HANDOFF_SUB : HANDOFF_MAIN
  const orig = instructions ?? ''
  if (hasMark(orig, mark)) return orig
  return orig.trim() === '' ? block : `${orig}\n\n${block}`
}

export const register: Register = on => {
  // 自己算壞了就照原樣交下去,不影響壓縮;.catch 裡的 next 不會重跑,壓縮已做完就交回原本的結果
  on('session.compact', async ($, e, next) => next({ ...e, instructions: withHandoff(e.instructions, typeof e.agentId === 'string') }))
    .catch(($, e, next) => next(e))
}
