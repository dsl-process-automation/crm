import { ref, Ref } from 'vue'
import { useTheme } from 'frappe-ui'

export type DSLTheme = 'light' | 'dark' | 'system' | 'dsl'

const DSL_THEME_KEY = 'dsl_theme'

export function useDSLTheme() {
  const { setTheme } = useTheme()
  const currentDSLTheme: Ref<DSLTheme> = ref('system')

  function applyDSLTheme(theme: DSLTheme) {
    currentDSLTheme.value = theme
    localStorage.setItem(DSL_THEME_KEY, theme)

    if (theme === 'dsl') {
      setTheme('dark')
      document.documentElement.setAttribute('data-dsl-theme', 'true')
    } else {
      document.documentElement.removeAttribute('data-dsl-theme')
      setTheme(theme)
    }
  }

  function initializeDSLTheme() {
    const stored = localStorage.getItem(DSL_THEME_KEY) as DSLTheme | null
    if (stored && ['light', 'dark', 'system', 'dsl'].includes(stored)) {
      applyDSLTheme(stored)
    } else {
      applyDSLTheme('system')
    }
  }

  return {
    currentDSLTheme,
    applyDSLTheme,
    initializeDSLTheme,
  }
}
