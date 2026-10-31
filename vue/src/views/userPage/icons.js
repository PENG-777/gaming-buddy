/**
 * 用户端公共 SVG 图标集(统一 stroke 线性风格, 无 emoji)
 * 用法: <span class="u-icon w-5 h-5 text-warm-primary" v-html="ICONS.crown"></span>
 * 颜色: svg 使用 currentColor, 由外层 text-* 控制
 */
const s = (d, extra = '') =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${d}${extra}</svg>`

export const ICONS = {
  /* ---- 游戏图标(游戏分类已改用图片, 现 gamepad 仍作卡片封面兜底) ---- */
  crown: s('<path d="M3 17l2-10 5 4 2-7 2 7 5-4 2 10H3z"/><line x1="4" y1="20" x2="20" y2="20"/>'),
  sword: s('<path d="M4 20l10-10"/><path d="M14 10l5-6 1 3-4 5-2-2z"/><path d="M6 14l4 4"/><path d="M3 21l3-1-2-2-1 3z"/>'),
  swords: s('<path d="M4 4l7 7"/><path d="M20 4l-7 7"/><path d="M14 14l6 6"/><path d="M10 14l-6 6"/><path d="M4 4h3v3"/><path d="M20 4h-3v3"/><path d="M14.5 19.5L17 17"/><path d="M9.5 19.5L7 17"/>'),
  target: s('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1" fill="currentColor"/>'),
  shield: s('<path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3z"/><polyline points="9 12 11 14 15 10"/>'),
  gem: s('<path d="M7 3h10l4 6-9 12L3 9l4-6z"/><path d="M3 9h18"/><path d="M9 3l-2 6 5 12 5-12-2-6"/>'),
  plane: s('<path d="M21 3L3 10.5l6 2.5"/><path d="M21 3l-6.5 18-3-8-8.5-2L21 3z"/>'),
  puzzle: s('<path d="M10 3h4v3a2 2 0 1 0 4 0V3h3v5a2 2 0 1 1 0 4h0v9h-5v-2a2 2 0 1 0-4 0v2H3v-6h2a2 2 0 1 0 0-4H3V3h7z"/>'),
  ghost: s('<path d="M12 3a7 7 0 0 0-7 7v10l2.5-2 2.3 2 2.2-2 2.2 2 2.3-2L19 20V10a7 7 0 0 0-7-7z"/><circle cx="9.5" cy="11" r="0.6" fill="currentColor"/><circle cx="14.5" cy="11" r="0.6" fill="currentColor"/>'),
  shovel: s('<path d="M13 5l6 6"/><path d="M16 2l6 6-3 1-4-4 1-3z"/><path d="M12 7L4 15v5h5l8-8"/>'),
  cloud: s('<path d="M6 18a4 4 0 1 1 .9-7.9A6 6 0 0 1 18.6 9.5 3.5 3.5 0 0 1 18 18H6z"/>'),
  gamepad: s('<rect x="2.5" y="7" width="19" height="11" rx="5.5"/><path d="M8 11v3M6.5 12.5h3"/><circle cx="16" cy="11.5" r="0.8" fill="currentColor"/><circle cx="18" cy="14" r="0.8" fill="currentColor"/>'),
  monitor: s('<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M9 20h6"/><path d="M12 16v4"/>'),
  mic: s('<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0"/><path d="M12 18v3"/>'),

  /* ---- 服务玩法 ---- */
  rocket: s('<path d="M12 15c-2 0-5-1-5-1s1.5-7 8-11c1 3 1 6 0 8l-3 4z"/><path d="M9 14l-4 7 4-1 2-3"/><path d="M12 15s3-1 5-1 4 2 4 2-2 1-4 3-5 0-5 0"/><circle cx="14.5" cy="9.5" r="1.2"/>'),
  users: s('<circle cx="9" cy="8" r="3.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7"/><path d="M18 14.5c2 .8 3 2.9 3 5.5"/>'),
  book: s('<path d="M12 6s-2-1.5-9-1.5V19c7 0 9 1.5 9 1.5s2-1.5 9-1.5V4.5C14 4.5 12 6 12 6z"/><path d="M12 6v14.5"/>'),
  moon: s('<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/>'),

  /* ---- 通用功能 ---- */
  star: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9 2.9-6z"/></svg>`,
  fire: s('<path d="M12 22c4.4 0 8-3.1 8-7.5 0-3-1.7-5-3-6.5.3 2-.6 3.4-1.7 4-0.3-2.7-1.6-6-4.3-8 .5 3-1 4.6-2.5 6.3C7 12 6 13.7 6 15.5 6 19.4 8.6 22 12 22z"/><path d="M12 22c-1.9 0-3.5-1.6-3.5-3.8 0-1.6 1-2.7 1.9-3.7.8.9 2 1.3 3.1 1 .6.8 1 1.7 1 2.7 0 2.2-1.2 3.8-2.5 3.8z"/>'),
  location: s('<path d="M12 21s7-6.1 7-11a7 7 0 1 0-14 0c0 4.9 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>'),
  verified: s('<circle cx="12" cy="12" r="9"/><polyline points="8 12.5 10.8 15.2 16 9.5"/>'),
  calendar: s('<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/>'),
  clock: s('<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15.5 14"/>'),
  bell: s('<path d="M6 9a6 6 0 1 1 12 0c0 5 2 6 2 6H4s2-1 2-6z"/><path d="M10 19a2 2 0 0 0 4 0"/>'),
  wallet: s('<path d="M3 7a2 2 0 0 1 2-2h13a2 2 0 0 1 2 2v1"/><path d="M3 7v10a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1H3z"/><circle cx="16.5" cy="14" r="1" fill="currentColor"/>'),
  coupon: s('<path d="M3 6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v3a2.5 2.5 0 0 0 0 6v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3a2.5 2.5 0 0 0 0-6V6z"/><path d="M14 5v2M14 11v2M14 17v2"/>'),
  gift: s('<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M5 12v8a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-8"/><path d="M12 8v13"/><path d="M12 8s-1-4-4-4a2 2 0 0 0 0 4h4z"/><path d="M12 8s1-4 4-4a2 2 0 0 1 0 4h-4z"/>'),
  search: s('<circle cx="11" cy="11" r="7"/><line x1="16.5" y1="16.5" x2="21" y2="21"/>'),
  chat: s('<path d="M21 12a8 8 0 0 1-8 8H4l2-3.2A8 8 0 1 1 21 12z"/><path d="M8.5 11h7M8.5 14h4"/>'),
  headset: s('<path d="M4 13a8 8 0 0 1 16 0"/><rect x="3" y="13" width="4" height="6" rx="2"/><rect x="17" y="13" width="4" height="6" rx="2"/><path d="M19 19a4 4 0 0 1-4 3"/>'),
  trophy: s('<path d="M8 4h8v6a4 4 0 0 1-8 0V4z"/><path d="M8 5H4.5c0 3 1.5 5 3.5 5"/><path d="M16 5h3.5c0 3-1.5 5-3.5 5"/><path d="M12 14v3"/><path d="M8 20h8"/><path d="M10 17h4l1 3H9l1-3z"/>'),
  medal: s('<circle cx="12" cy="15" r="5.5"/><path d="M8.5 10.5L6 3h4l2 5 2-5h4l-2.5 7.5"/>'),
  home: s('<path d="M4 11l8-7 8 7"/><path d="M6 9.5V20a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V9.5"/><path d="M10 21v-6h4v6"/>'),
  list: s('<path d="M8 6h13M8 12h13M8 18h13"/><circle cx="4" cy="6" r="1" fill="currentColor"/><circle cx="4" cy="12" r="1" fill="currentColor"/><circle cx="4" cy="18" r="1" fill="currentColor"/>'),
  user: s('<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>'),
  logout: s('<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/>'),
  order: s('<path d="M5 3h14a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M9 3v3h6V3"/><path d="M8 10h8M8 14h8M8 18h5"/>'),
  send: s('<path d="M21 3L10.5 13.5"/><path d="M21 3l-7 18-3.5-7.5L3 10l18-7z"/>'),
  trash: s('<path d="M4 7h16"/><path d="M9 7V4h6v3"/><path d="M6.5 7l1 13a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1l1-13"/><path d="M10 11v6M14 11v6"/>'),
  edit: s('<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>'),
  eye: s('<path d="M2 12s3.5-6.5 10-6.5S22 12 22 12s-3.5 6.5-10 6.5S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>'),
  lock: s('<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>'),
  phone: s('<path d="M6.5 3h3l1.5 4-2 1.5a12 12 0 0 0 6.5 6.5L17 13l4 1.5v3a2 2 0 0 1-2.2 2A17 17 0 0 1 3.5 5.2 2 2 0 0 1 5.5 3z"/>'),
  play: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13l11-6.5-11-6.5z"/></svg>`,
  pause: `<svg viewBox="0 0 24 24" fill="currentColor"><rect x="7" y="5" width="3.5" height="14" rx="1"/><rect x="13.5" y="5" width="3.5" height="14" rx="1"/></svg>`,
  plus: s('<path d="M12 5v14M5 12h14"/>'),
  check: s('<polyline points="4.5 12.5 9.5 17.5 19.5 6.5"/>'),
  close: s('<path d="M6 6l12 12M18 6L6 18"/>'),
  arrowLeft: s('<path d="M15 5l-7 7 7 7"/>'),
  arrowRight: s('<path d="M9 5l7 7-7 7"/>'),
  arrowDown: s('<path d="M5 9l7 7 7-7"/>'),
  sparkle: s('<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z"/><path d="M19 16l.9 2.1L22 19l-2.1.9L19 22l-.9-2.1L16 19l2.1-.9L19 16z"/>'),
  music: s('<path d="M9 18V6l11-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>'),
  refund: s('<path d="M3.5 12a8.5 8.5 0 1 0 2.6-6.1"/><path d="M3 4v5h5"/><path d="M12 8v8"/><path d="M9.5 10.5L12 8l2.5 2.5"/><path d="M9.5 13.5L12 16l2.5-2.5"/>'),
  fish: s('<path d="M3 12c3-5 8-6 12-4l5-3-1.5 5.5L20 16l-5-3c-4 2-9 1-12-4z"/><circle cx="8" cy="12" r="0.6" fill="currentColor"/><path d="M3 12c2 1.5 4 2 6 2"/>'),
  cup: s('<path d="M6 9h11l-1 11a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L6 9z"/><path d="M6 9c-2 0-3 1.5-3 3s1 2.5 2.5 2.5"/><path d="M9 6c0-1.5 1-2 1-3.5M13 6c0-1.5 1-2 1-3.5"/>'),
  box: s('<path d="M3.5 7.5L12 3l8.5 4.5v9L12 21l-8.5-4.5v-9z"/><path d="M3.5 7.5L12 12l8.5-4.5"/><path d="M12 12v9"/>'),
  setting: s('<circle cx="12" cy="12" r="3"/><path d="M12 2.5l1.2 2.8 3-.6.4 3 2.9 1-1.4 2.7 2 2.3-2.4 1.9.6 3-3 .4-1 2.9-2.7-1.3-2.7 1.3-1-2.9-3-.4.6-3L2.5 17l2-2.3L3.1 12l2.9-1 .4-3 3 .6L9.6 2.7 12 2.5z" stroke-width="1.2"/>'),
  customer: s('<circle cx="12" cy="7" r="3.5"/><path d="M5 21c0-3.5 3-6 7-6s7 2.5 7 6"/><path d="M9.5 12.5c.8.8 1.6 1.2 2.5 1.2s1.7-.4 2.5-1.2"/>'),
  rank: s('<rect x="3" y="12" width="5" height="9" rx="1"/><rect x="9.5" y="6" width="5" height="15" rx="1"/><rect x="16" y="9" width="5" height="12" rx="1"/>'),
  /* 性别符号(实心风格, 白色使用) */
  genderFemale: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><circle cx="12" cy="9.5" r="5.5"/><path d="M12 15v6.5M8.8 18.5h6.4"/></svg>`,
  genderMale: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><circle cx="10" cy="14" r="5.5"/><path d="M14.2 9.8L20.5 3.5M15.5 3.5h5v5"/></svg>`,
}

/** 取图标(不存在的 key 兜底为 box) */
export const iconOf = (key) => ICONS[key] || ICONS.box