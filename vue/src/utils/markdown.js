/**
 * AI 回复 Markdown 渲染工具(markdown-it, 管理端数据分析/用户端助手共用)
 *
 * 使用: renderMarkdown(text) 返回 HTML 字符串, 配合 v-html 使用;
 * 输出为 markdown-it 默认安全规则(默认转义 HTML 标签, 无需额外插件)。
 */
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  breaks: true, // 单换行转 <br>(聊天场景更自然)
  linkify: true, // 自动识别链接
})

export function renderMarkdown(text) {
  if (!text) return ''
  return md.render(String(text))
}