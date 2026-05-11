const app = getApp()

Page({
  data: {
    photo: {},
    album: {},
    loading: true
  },

  onLoad: function(options) {
    if (options.id) {
      this.loadPhoto(options.id)
    }
  },

  loadPhoto: function(photoId) {
    const that = this
    const apiBase = app.globalData.apiBase

    wx.showLoading({ title: '加载中...' })

    wx.request({
      url: apiBase + '/api/photos/',
      success: function(res) {
        if (res.data && Array.isArray(res.data)) {
          const photo = res.data.find(p => p.id == photoId)
          if (photo) {
            that.setData({ photo: photo })
            wx.setNavigationBarTitle({ title: photo.title })
          }
        }
      },
      fail: function(err) {
        console.error('加载照片失败', err)
        wx.showToast({ title: '加载失败', icon: 'none' })
      },
      complete: function() {
        wx.hideLoading()
        that.setData({ loading: false })
      }
    })
  },

  previewImage: function() {
    if (this.data.photo && this.data.photo.src) {
      wx.previewImage({
        current: this.data.photo.src,
        urls: [this.data.photo.src]
      })
    }
  },

  saveImage: function() {
    if (!this.data.photo || !this.data.photo.src) return

    wx.showLoading({ title: '保存中...' })

    wx.downloadFile({
      url: this.data.photo.src,
      success: function(res) {
        wx.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: function() {
            wx.showToast({ title: '保存成功', icon: 'success' })
          },
          fail: function(err) {
            console.error('保存失败', err)
            wx.showToast({ title: '保存失败', icon: 'none' })
          }
        })
      },
      fail: function(err) {
        console.error('下载失败', err)
        wx.showToast({ title: '下载失败', icon: 'none' })
      },
      complete: function() {
        wx.hideLoading()
      }
    })
  }
})
