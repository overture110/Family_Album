<template>
  <view class="photo-waterfall-container">
    <view class="waterfall-wrapper">
      <view
        v-for="(column, columnIndex) in columns"
        :key="columnIndex"
        class="waterfall-column"
      >
        <view
          v-for="(photo, photoIndex) in column"
          :key="photo.id"
          class="waterfall-item"
          @tap="previewImage(photo, columnIndex, photoIndex)"
        >
          <image
            :src="photo.thumbnail || photo.url"
            :style="{
              height: photo.containerHeight + 'px',
              opacity: loadedImages.has(photo.id) ? 1 : 0
            }"
            :lazy-load="true"
            mode="widthFix"
            class="waterfall-image"
            @load="onImageLoad(photo.id)"
            @error="onImageError(photo.id)"
          />
          <view
            v-if="photo.title || photo.description"
            class="photo-overlay"
          >
            <text class="photo-title" v-if="photo.title">{{ photo.title }}</text>
            <text class="photo-date" v-if="photo.taken_date">{{ photo.taken_date }}</text>
          </view>
        </view>
      </view>
    </view>

    <view v-if="loading" class="loading-indicator">
      <text>加载中...</text>
    </view>

    <view v-if="!hasMore && photos.length > 0" class="no-more-data">
      <text>没有更多照片了</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  photos: {
    type: Array,
    required: true,
    default: () => []
  },
  columnCount: {
    type: Number,
    default: 2
  },
  gap: {
    type: Number,
    default: 8
  },
  loading: {
    type: Boolean,
    default: false
  },
  hasMore: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['photo-click', 'load-more', 'image-load', 'image-error']);

const loadedImages = ref(new Set());
const columnHeights = ref([]);
const containerWidth = ref(0);

const columns = computed(() => {
  const cols = Array.from({ length: props.columnCount }, () => []);
  const heights = Array(props.columnCount).fill(0);

  props.photos.forEach(photo => {
    const shortestColumn = heights.indexOf(Math.min(...heights));
    cols[shortestColumn].push(photo);
    const imageHeight = photo.aspectRatio
      ? (containerWidth.value / props.columnCount - props.gap) / photo.aspectRatio
      : 200;
    heights[shortestColumn] += imageHeight + props.gap;
  });

  return cols;
});

const onImageLoad = (photoId) => {
  loadedImages.value.add(photoId);
  emit('image-load', photoId);
};

const onImageError = (photoId) => {
  emit('image-error', photoId);
};

const previewImage = (photo, columnIndex, photoIndex) => {
  emit('photo-click', { photo, columnIndex, photoIndex });

  const urls = props.photos.map(p => p.url || p.thumbnail);
  const currentIndex = props.photos.findIndex(p => p.id === photo.id);

  // #ifdef H5
  if (currentIndex !== -1) {
    openH5Preview(urls, currentIndex);
  }
  // #endif

  // #ifdef MP-WEIXIN
  uni.previewImage({
    current: currentIndex,
    urls: urls,
    fail: () => {
      if (currentIndex !== -1) {
        openH5Preview(urls, currentIndex);
      }
    }
  });
  // #endif
};

const openH5Preview = (urls, currentIndex) => {
  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    cursor: pointer;
  `;

  const img = document.createElement('img');
  img.src = urls[currentIndex];
  img.style.cssText = `
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
  `;

  const closeBtn = document.createElement('span');
  closeBtn.textContent = '×';
  closeBtn.style.cssText = `
    position: absolute;
    top: 20px;
    right: 30px;
    font-size: 40px;
    color: white;
    cursor: pointer;
  `;

  overlay.appendChild(img);
  overlay.appendChild(closeBtn);

  const closePreview = (e) => {
    if (e.target === overlay || e.target === closeBtn) {
      document.body.removeChild(overlay);
      document.removeEventListener('keydown', handleKeyDown);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      document.body.removeChild(overlay);
      document.removeEventListener('keydown', handleKeyDown);
    }
  };

  overlay.addEventListener('click', closePreview);
  document.body.appendChild(overlay);
  document.addEventListener('keydown', handleKeyDown);
};

const handleScroll = () => {
  if (props.loading || !props.hasMore) return;

  const scrollTop = window.scrollY || document.documentElement.scrollTop;
  const windowHeight = window.innerHeight;
  const documentHeight = document.documentElement.scrollHeight;

  if (scrollTop + windowHeight >= documentHeight - 200) {
    emit('load-more');
  }
};

const updateContainerWidth = () => {
  const container = document.querySelector('.photo-waterfall-container');
  if (container) {
    containerWidth.value = container.offsetWidth;
  }
};

onMounted(() => {
  updateContainerWidth();
  window.addEventListener('scroll', handleScroll);
  window.addEventListener('resize', updateContainerWidth);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('resize', updateContainerWidth);
});
</script>

<style scoped>
.photo-waterfall-container {
  width: 100%;
  padding: 0;
  box-sizing: border-box;
}

.waterfall-wrapper {
  display: flex;
  width: 100%;
}

.waterfall-column {
  flex: 1;
  padding: 0 4px;
  box-sizing: border-box;
}

.waterfall-item {
  position: relative;
  margin-bottom: 8px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f5f5f5;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.waterfall-item:active {
  transform: scale(0.98);
}

.waterfall-image {
  width: 100%;
  display: block;
  transition: opacity 0.3s ease;
}

.photo-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24rpx 16rpx 16rpx;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
  color: white;
}

.photo-title {
  display: block;
  font-size: 28rpx;
  font-weight: 500;
  margin-bottom: 4rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.photo-date {
  display: block;
  font-size: 24rpx;
  opacity: 0.8;
}

.loading-indicator {
  text-align: center;
  padding: 32rpx;
  color: #999;
  font-size: 28rpx;
}

.no-more-data {
  text-align: center;
  padding: 32rpx;
  color: #ccc;
  font-size: 26rpx;
}
</style>
