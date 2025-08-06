import { ref, onMounted, onUnmounted, nextTick } from 'vue'

export interface LazyLoadOptions {
  rootMargin?: string
  threshold?: number
}

export function useImageLazyLoad(options: LazyLoadOptions = {}) {
  const intersectionObserver = ref<IntersectionObserver | null>(null)
  const visibleImages = ref<Set<string>>(new Set())
  const imageRefs = ref<Map<string, HTMLElement>>(new Map())
  const pendingUpdates = ref<Set<string>>(new Set())

  const defaultOptions = {
    rootMargin: '50px',
    threshold: 0.1,
    ...options
  }

  // 初始化交集观察器
  const initObserver = () => {
    if (intersectionObserver.value) return

    intersectionObserver.value = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const imageId = entry.target.getAttribute('data-image-id')
          if (imageId) {
            // 防止重复处理
            if (pendingUpdates.value.has(imageId)) return
            
            pendingUpdates.value.add(imageId)
            
            // 使用 nextTick 确保状态更新的一致性
            nextTick(() => {
              if (entry.isIntersecting) {
                visibleImages.value.add(imageId)
              } else {
                visibleImages.value.delete(imageId)
              }
              pendingUpdates.value.delete(imageId)
            })
          }
        })
      },
      {
        root: null,
        ...defaultOptions
      }
    )
  }

  // 观察图片元素
  const observeImage = (element: HTMLElement, imageId: string) => {
    if (!element || !intersectionObserver.value) return
    
    // 检查是否已经在观察中
    if (imageRefs.value.has(imageId)) {
      return
    }

    element.dataset.imageId = imageId
    imageRefs.value.set(imageId, element)
    intersectionObserver.value.observe(element)
  }

  // 取消观察图片元素
  const unobserveImage = (imageId: string) => {
    const element = imageRefs.value.get(imageId)
    if (element && intersectionObserver.value) {
      intersectionObserver.value.unobserve(element)
      imageRefs.value.delete(imageId)
      visibleImages.value.delete(imageId)
    }
  }

  // 设置图片引用
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const setImageRef = (el: any, imageId: string) => {
    if (!el) return

    nextTick(() => {
      const imageElement = el.$el || el
      if (imageElement) {
        observeImage(imageElement, imageId)
      }
    })
  }

  // 检查图片是否可见
  const isImageVisible = (imageId: string): boolean => {
    return visibleImages.value.has(imageId)
  }

  // 清理观察器
  const cleanup = () => {
    if (intersectionObserver.value) {
      intersectionObserver.value.disconnect()
      intersectionObserver.value = null
    }
    visibleImages.value.clear()
    imageRefs.value.clear()
  }

  // 清空可见图片集合（用于重新加载场景）
  const clearVisible = () => {
    visibleImages.value.clear()
  }

  onMounted(() => {
    initObserver()
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    visibleImages: visibleImages.value,
    setImageRef,
    isImageVisible,
    observeImage,
    unobserveImage,
    clearVisible,
    cleanup
  }
}