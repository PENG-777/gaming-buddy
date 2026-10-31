import request from '@/utils/request'

//查询轮播图列表
export function selectBannerList(query) {
  return request({
    url: '/biz/banner/selectBannerList',
    method: 'get',
    params: query
  })
}

//根据轮播图ID查询轮播图信息
export function selectBannerByBannerId(bannerId) {
  return request({
    url: '/biz/banner/selectBannerByBannerId/' + bannerId,
    method: 'get'
  })
}

//新增轮播图
export function insertBanner(data) {
  return request({
    url: '/biz/banner/insertBanner',
    method: 'post',
    data: data
  })
}

//修改轮播图
export function updateBanner(data) {
  return request({
    url: '/biz/banner/updateBanner',
    method: 'put',
    data: data
  })
}

//删除轮播图
export function deleteBannerByBannerIds(bannerIds) {
  return request({
    url: '/biz/banner/deleteBannerByBannerIds/' + bannerIds,
    method: 'delete'
  })
}

//查询启用中的轮播图列表(用户端首页)
export function selectPublishedBannerList() {
  return request({
    url: '/biz/banner/selectPublishedBannerList',
    method: 'get'
  })
}