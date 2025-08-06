import { ElMessageBox } from 'element-plus'

/**
 * 通用确认弹窗
 */
export function showConfirm(message: string, title = '提示', options: Partial<{ confirmButtonText: string; cancelButtonText: string; type: 'warning' | 'info' | 'success' | 'error'; }> = {}) {
  return ElMessageBox.confirm(message, title, {
    confirmButtonText: options.confirmButtonText || '确定',
    cancelButtonText: options.cancelButtonText || '取消',
    type: options.type || 'warning',
    ...options,
  })
}

/**
 * 通用信息弹窗
 */
export function showAlert(message: string, title = '提示', options: Partial<{ confirmButtonText: string; type: 'info' | 'success' | 'warning' | 'error'; }> = {}) {
  return ElMessageBox.alert(message, title, {
    confirmButtonText: options.confirmButtonText || '确定',
    type: options.type || 'info',
    ...options,
  })
}

/**
 * 通用输入弹窗
 */
export function showPrompt(message: string, title = '输入', options: Partial<{ confirmButtonText: string; cancelButtonText: string; inputPlaceholder: string; type: 'info' | 'success' | 'warning' | 'error'; }> = {}) {
  return ElMessageBox.prompt(message, title, {
    confirmButtonText: options.confirmButtonText || '确定',
    cancelButtonText: options.cancelButtonText || '取消',
    inputPlaceholder: options.inputPlaceholder || '',
    type: options.type || 'info',
    ...options,
  })
}
