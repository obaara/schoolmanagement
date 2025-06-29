import { toast } from "sonner"

const useToast = () => {
  return {
    toast: (props) => {
      if (typeof props === 'string') {
        return toast(props)
      }
      
      const { title, description, variant = 'default', ...rest } = props
      
      if (variant === 'destructive') {
        return toast.error(title, {
          description,
          ...rest
        })
      }
      
      return toast(title, {
        description,
        ...rest
      })
    }
  }
}

export { useToast }

