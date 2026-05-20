import { useEffect } from 'react'
import { useBlocker } from 'react-router-dom'

export function useUnsavedChangesWarning(hasUnsavedChanges: boolean) {
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      hasUnsavedChanges && currentLocation.pathname !== nextLocation.pathname,
  )

  useEffect(() => {
    if (!hasUnsavedChanges) return

    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault()
      e.returnValue = ''
    }
    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [hasUnsavedChanges])

  useEffect(() => {
    if (blocker.state === 'blocked') {
      const confirmou = window.confirm(
        'Há alterações não salvas. Deseja sair mesmo assim?',
      )
      if (confirmou) blocker.proceed()
      else blocker.reset()
    }
  }, [blocker])
}
