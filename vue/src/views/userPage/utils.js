/**
 * 用户端公共工具: 时间格式化 / 可约日期时段 / 订单状态字典 / 杂项
 */

/** Date -> 'yyyy-MM-dd HH:mm:ss' */
export const fmtDateTime = (d = new Date()) => {
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}

/** Date -> 'yyyy-MM-dd HH:mm' */
export const fmtMinute = (d = new Date()) => fmtDateTime(d).slice(0, 16)

/** Date -> 'yyyy-MM-dd' */
export const fmtDate = (d = new Date()) => fmtDateTime(d).slice(0, 10)

/** Date -> 'HH:mm' */
export const fmtClock = (d = new Date()) => fmtDateTime(d).slice(11, 16)

const WEEKS = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

/**
 * 未来 n 天日期列表(含今天), 供预约/时间表使用
 * 返回 [{ dateStr, label(今天/明天/周X), monthDay('10/17'), week }]
 */
export const nextDays = (n = 7) => {
  const today = new Date()
  return Array.from({ length: n }, (_, i) => {
    const d = new Date(today.getFullYear(), today.getMonth(), today.getDate() + i)
    const dateStr = fmtDate(d)
    return {
      dateStr,
      label: i === 0 ? '今天' : i === 1 ? '明天' : WEEKS[d.getDay()],
      monthDay: `${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`,
      week: WEEKS[d.getDay()],
    }
  })
}

/** 可约小时档(10 点至 22 点整点) */
export const SLOT_HOURS = [10, 12, 14, 16, 18, 19, 20, 21, 22]

/* 服务名称 -> 图标 key 规则(未命中回退 gamepad, 供 companionStore/bizStore 共用) */
const SERVICE_ICON_RULES = [
  [/上分|冲分|陪练|代肝/, 'rocket'],
  [/娱乐|开黑|双人|联机/, 'users'],
  [/教学|指导|引导/, 'book'],
  [/语音|倾听|哄睡|陪聊|陪伴/, 'moon'],
]

/** 服务名称 -> 图标 key(未命中回退 gamepad) */
export const serviceIconOf = (name) => (SERVICE_ICON_RULES.find(([re]) => re.test(name || ''))?.[1]) || 'gamepad'

/** 订单状态字典 */
export const ORDER_STATUS = {
  pending: { label: '待支付', cls: 'text-warm-warning', bg: 'bg-[#fdf6e3]', dot: 'bg-warm-warning' },
  booked: { label: '待开始', cls: 'text-warm-primary', bg: 'bg-warm-bg', dot: 'bg-warm-primary' },
  ongoing: { label: '进行中', cls: 'text-warm-success', bg: 'bg-[#e4f4f2]', dot: 'bg-warm-success' },
  completed: { label: '已完成', cls: 'text-warm-sub', bg: 'bg-[#f3f4f6]', dot: 'bg-warm-sub' },
  refunding: { label: '退款中', cls: 'text-warm-danger', bg: 'bg-[#fdeeee]', dot: 'bg-warm-danger' },
  cancelled: { label: '已取消', cls: 'text-warm-sub', bg: 'bg-[#f3f4f6]', dot: 'bg-warm-sub' },
}

/** 我的订单 Tab 配置 */
export const ORDER_TABS = [
  { key: 'all', label: '全部' },
  { key: 'pending', label: '待支付' },
  { key: 'booked', label: '待开始' },
  { key: 'ongoing', label: '进行中' },
  { key: 'completed', label: '已完成' },
  { key: 'cancelled', label: '已取消' },
]

/** 生成订单号 */
export const genOrderNo = () => {
  const d = fmtDateTime(new Date()).replace(/[-: ]/g, '')
  const r = String(Math.floor(Math.random() * 900) + 100)
  return `GB${d}${r}`
}

/** 金额格式化: 默认整数, decimals 指定小数位 */
export const fmtMoney = (n, decimals = 0) => `¥${Number(n || 0).toFixed(decimals)}`

/** 订单服务时间描述: '2026-10-18 20:00 ~ 22:00' */
export const orderTimeText = (o) => {
  const p = (n) => String(n).padStart(2, '0')
  return `${o.date} ${p(o.startHour)}:00 ~ ${p(o.startHour + o.hours)}:00`
}

/** 段位档位(筛选项, 由高到低) */
export const RANK_TIERS = ['巅峰王者', '最强王者', '大师宗师', '钻石铂金', '黄金以下']

/** 段位在档位中的归组(供筛选比较) */
export const tierIndexOf = (rank) => {
  if (/巅峰|荣耀王者|50星|1800/.test(rank)) return 0
  if (/最强王者|王者/.test(rank)) return 1
  if (/大师|宗师|超凡|不朽/.test(rank)) return 2
  if (/钻石|铂金|翡翠/.test(rank)) return 3
  return 4
}

/** 简单 id */
let idSeed = 1000
export const nextId = () => ++idSeed