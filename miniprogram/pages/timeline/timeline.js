const app = getApp()

Page({
  data: {
    albums: [],
    years: [],
    albumsByYear: {},
    loading: true
  },

  onLoad: function() {
    this.loadAlbums()
  },

  onShow: function() {
    this.loadAlbums()
  },

  loadAlbums: function() {
    const that = this
    const apiBase = app.globalData.apiBase

    wx.showLoading({ title: '加载中...' })

    wx.request({
      url: apiBase + '/api/albums/',
      success: function(res) {
        if (res.data && Array.isArray(res.data)) {
          const albums = res.data
          const years = [...new Set(albums.map(a => a.year))].sort((a, b) => b - a)

          const albumsByYear = {}
          years.forEach(year => {
            albumsByYear[year] = albums.filter(a => a.year === year)
          })

          that.setData({
            albums: albums,
            years: years,
            albumsByYear: albumsByYear,
            loading: false
          })
        }
      },
      fail: function(err) {
        console.error('加载相册失败', err)
        wx.showToast({ title: '加载失败', icon: 'none' })
      },
      complete: function() {
        wx.hideLoading()
      }
    })
  },

  viewAlbum: function(e) {
    const albumId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: '/pages/album/album?id=' + albumId
    })
  }
})
