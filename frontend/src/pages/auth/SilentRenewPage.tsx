import { useEffect } from 'react'
import { getUserManager } from '@/contexts/AuthContext'

export default function SilentRenewPage() {
  useEffect(() => {
    const handleSilentRenew = async () => {
      try {
        const manager = getUserManager()
        await manager.signinSilentCallback()
      } catch (error) {
        console.error('Silent renew failed:', error)
      }
    }

    handleSilentRenew()
  }, [])

  return <div>Silent renew in progress...</div>
}
