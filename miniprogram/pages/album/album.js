const app = getApp()

Page({
  data: {
    album: {},
    photos: [],
    loading: true
  },

  onLoad: function(options) {
    if (options.id) {
      this.setData({ albumId: options.id })
      this.loadAlbum(options.id)
    }
  },

  onShow: function() {
    if (this.data.albumId) {
      this.loadAlbum(this.data.albumId)
    }
  },

  loadAlbum: function(albumId) {
    const that = this
    const apiBase = app.globalData.apiBase

    wx.showLoading({ title: '加载中...' })

    wx.request({
      url: apiBase + '/api/albums/?album_id=' + albumId,
      success: function(res) {
        if (res.data && res.data.length > 0) {
          that.setData({ album: res.data[0] })
          wx.setNavigationBarTitle({ title: res.data[0].name })
        }
      },
      fail: function(err) {
        console.error('加载相册失败', err)
        wx.showToast({ title: '加载失败', icon: 'none' })
      }
    })

    wx.request({
      url: apiBase + '/api/photos/?album_id=' + albumId,
      success: function(res) {
        if (res.data && Array.isArray(res.data)) {
          that.setData({
            photos: res.data,
            loading: false
          })
        }
      },
      fail: function(err) {
        console.error('加载照片失败', err)
      },
      complete: function() {
        wx.hideLoading()
      }
    })
  },

  previewPhoto: function(e) {
    const index = e.currentTarget.dataset.index
    const urls = this.data.photos.map(p => p.src)
    wx.previewImage({
      current: urls[index],
      urls: urls
    })
  },

  viewPhoto: function(e) {
    const photoId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: '/pages/photo/photo?id=' + photoId
    })
  }
})
