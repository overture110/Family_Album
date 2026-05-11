const app = getApp()

Page({
  data: {
    carouselPhotos: [],
    recentPhotos: [],
    mottoList: [],
    loading: true
  },

  onLoad: function() {
    this.loadData()
  },

  onShow: function() {
    this.loadData()
  },

  loadData: function() {
    const that = this
    const apiBase = app.globalData.apiBase

    wx.showLoading({ title: '加载中...' })

    wx.request({
      url: apiBase + '/api/photos/',
      success: function(res) {
        if (res.data && Array.isArray(res.data)) {
          that.setData({
            carouselPhotos: res.data.slice(0, 10),
            recentPhotos: res.data.slice(0, 20),
            loading: false
          })
        }
      },
      fail: function(err) {
        console.error('加载照片失败', err)
        wx.showToast({ title: '加载失败', icon: 'none' })
      },
      complete: function() {
        wx.hideLoading()
      }
    })

    that.setData({
      mottoList: [
        { title: '敬爱', subtitle: '敬', content: '成员互敬，长幼互爱。' },
        { title: '关怀', subtitle: '关', content: '远婚姻干涉，近生活冷暖。' },
        { title: '通达', subtitle: '通', content: '凡事有交代，沟通不隔夜。' },
        { title: '包容', subtitle: '包', content: '礼待传统，亦守自由。' },
        { title: '共生', subtitle: '共', content: '爱己为本，舍己为家。' }
      ]
    })
  },

  viewPhoto: function(e) {
    const photoId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: '/pages/photo/photo?id=' + photoId
    })
  },

  goTimeline: function() {
    wx.switchTab({ url: '/pages/timeline/timeline' })
  }
})
