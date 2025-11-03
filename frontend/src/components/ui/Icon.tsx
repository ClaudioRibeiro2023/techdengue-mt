import * as LucideIcons from 'lucide-react'
import { type LucideIcon } from 'lucide-react'

type IconProps = {
  name?: string
  className?: string
  size?: number
}

export default function Icon({ name, className = '', size = 16 }: IconProps) {
  if (!name) return null

  const IconComponent = LucideIcons[name as keyof typeof LucideIcons] as LucideIcon

  if (!IconComponent) {
    console.warn(`Icon "${name}" not found in lucide-react`)
    return null
  }

  return <IconComponent className={className} size={size} />
}
