/**
 * 用户端业务数据 Store(真实后端)
 * 数据源: /biz/game/selectAllGame + /biz/serviceItem/selectAllServiceItem + /biz/companion/selectAllCompanion
 * 三类基础数据一次拉全量后本地转换/筛选(数据量小, 免分页请求);
 * 评分/接单量/评价数/粉丝数由后端按订单/关注表聚合返回(rating/orderCount/reviewCount/fans);
 * 游戏热度/陪玩师数/最低价由真实陪玩师数据聚合计算。
 */
import { defineStore } from 'pinia'
import { selectAllGame } from '@/api/biz/game.js'
import { selectAllServiceItem } from '@/api/biz/serviceItem.js'
import { selectAllCompanion } from '@/api/biz/companion.js'
import { serviceIconOf } from '@/views/userPage/utils'

/* ---------------- 服务配色(4 组暖色循环) ---------------- */
const SERVICE_PALETTE = [
  { color: '#fff3e8', ink: '#f07c2a' },
  { color: '#e4f4f2', ink: '#26a69a' },
  { color: '#fdf3e3', ink: '#e6b422' },
  { color: '#eef3f8', ink: '#5b7a99' },
]

/** 图片地址: 相对路径(/profile/..)拼代理前缀, 完整 URL 原样使用(与 GameImage 一致) */
const imgSrc = (image) => (!image ? '' : /^https?:/.test(image) ? image : import.meta.env.VITE_APP_BASE_API + image)

/** 后端陪玩师行 -> 用户端展示结构(字段名对齐原 mock, 页面零成本切换) */
const mapCompanion = (row) => ({
  id: row.companionId,
  name: row.nickName,
  gender: row.gender === 1 ? 'female' : 'male',
  age: row.age,
  city: row.city || '',
  avatar: row.avatar || '',
  voice: row.voice || '',
  price: row.price ?? 0,
  intro: row.intro || '',
  tags: (row.tags || '').split(',').filter(Boolean),
  certified: row.certified === 1,
  mainGame: row.mainGameId,                 // 主游戏ID(数字, 供 gameById 查询)
  mainGameName: row.mainGameName || '',     // 后端 join 直接带回的主游戏名
  rank: row.mainRank || '',
  joinedAt: (row.createTime || '').slice(0, 10),
  createTime: row.createTime,
  games: (row.games || []).map(g => ({ key: g.gameId, name: g.gameName, rank: g.gameRank || '' })),
  services: (row.services || []).map(s => ({
    id: s.serviceId, name: s.serviceName, icon: serviceIconOf(s.serviceName),
    desc: s.description || '', price: s.price ?? 0,
  })),
  rating: row.rating ?? 5,                         // 后端聚合: 已评价订单平均星级(无评价默认 5.0)
  orders: row.orderCount ?? 0,                     // 后端聚合: 累计接单(非取消订单数)
  fans: row.fans ?? 0,                             // 后端聚合: 粉丝数(follow 表)
  reviewCount: row.reviewCount ?? 0,               // 后端聚合: 评价数
})

/** 聚合每个游戏的陪玩师数/最低价/热度(基于真实陪玩师数据计算) */
const buildGameStats = (games, companions) => {
  const stats = {}  // gameId -> { count, minPrice }
  for (const c of companions) {
    const ids = new Set([c.mainGame, ...c.games.map(g => g.key)].filter(Boolean))
    for (const gid of ids) {
      const s = stats[gid] || (stats[gid] = { count: 0, minPrice: Infinity })
      s.count += 1
      if (c.price > 0) s.minPrice = Math.min(s.minPrice, c.price)
    }
  }
  const maxCount = Math.max(1, ...Object.values(stats).map(s => s.count))
  return games.map(g => {
    const s = stats[g.id] || { count: 0, minPrice: Infinity }
    return {
      ...g,
      count: s.count,
      minPrice: s.minPrice === Infinity ? 0 : s.minPrice,
      hot: Math.round(60 + (s.count / maxCount) * 38),  // 热度按陪玩师数映射到 60-98
    }
  })
}

const useCompanionStore = defineStore('companion', {
  state: () => ({
    loaded: false,
    loading: null,    // 进行中的加载 promise(并发去重)
    games: [],        // [{ id, name, image, tags, desc, count, minPrice, hot }]
    serviceItems: [], // [{ id, name, image, desc, icon, color, ink }]
    companions: [],   // 用户端陪玩师结构(见 mapCompanion)
  }),

  getters: {
    /** 按 ID 查游戏(参数为后端 gameId) */
    gameById: (state) => (id) => state.games.find(g => g.id === Number(id)) || null,
    /** 按 ID 查服务项目 */
    serviceById: (state) => (id) => state.serviceItems.find(s => s.id === Number(id)) || null,
    /** 按 ID 查陪玩师 */
    companionById: (state) => (id) => state.companions.find(c => c.id === Number(id)) || null,
    /** 热门游戏(陪玩师数降序取前 8) */
    hotGames: (state) => [...state.games].sort((a, b) => b.count - a.count).slice(0, 8),
    /** 精选陪玩(评分降序 + 接单量, 前 10) */
    featuredCompanions: (state) =>
      [...state.companions].sort((a, b) => b.rating - a.rating || b.orders - a.orders).slice(0, 10),
    /** 首页服务玩法(前 8 个启用服务) */
    serviceTypes: (state) => state.serviceItems.slice(0, 8),
    /** 相似推荐(同主游戏或同性别, 排除自己, 评分降序) */
    similarCompanions: (state) => (c, count = 4) =>
      state.companions
        .filter(x => x.id !== c.id && (x.mainGame === c.mainGame || x.gender === c.gender))
        .sort((a, b) => b.rating - a.rating).slice(0, count),
  },

  actions: {
    /** 拉取全量基础数据(幂等, 各用户端页面 onMounted 调用即可; 失败可重试) */
    loadAll() {
      if (this.loaded) return Promise.resolve()
      if (this.loading) return this.loading
      this.loading = Promise.all([
        selectAllGame(), selectAllServiceItem(), selectAllCompanion(),
      ]).then(([gamesRes, servicesRes, companionsRes]) => {
        const companions = (companionsRes.data || []).map(mapCompanion)
        this.games = buildGameStats(
          (gamesRes.data || []).filter(g => g.status === 0).map(g => ({
            id: g.gameId, name: g.gameName, image: g.image || '',
            tags: (g.tags || '').split(',').filter(Boolean), desc: g.description || '',
          })),
          companions,
        )
        this.serviceItems = (servicesRes.data || []).filter(s => s.status === 0).map((s, i) => ({
          id: s.serviceId, name: s.serviceName, image: s.image || '', img: imgSrc(s.image),
          desc: s.description || '',
          icon: serviceIconOf(s.serviceName), ...SERVICE_PALETTE[i % SERVICE_PALETTE.length],
        }))
        this.companions = companions
        this.loaded = true
      }).finally(() => { this.loading = null })
      return this.loading
    },
  },
})

export default useCompanionStore