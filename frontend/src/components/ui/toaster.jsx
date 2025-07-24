'use client'

import {
  createStandaloneToast,
  Portal,
  Spinner,
  Stack,
  useToast,
} from '@chakra-ui/react'

const { ToastContainer, toast } = createStandaloneToast()

export const toaster = toast

export const Toaster = () => {
  return (
    <Portal>
      <ToastContainer />
    </Portal>
  )
}

// Helper function to show a loading toast
export const showLoadingToast = (title, description) => {
  return toast({
    title,
    description,
    status: 'loading',
    duration: null,
    isClosable: true,
  })
}

// Helper function to show a success toast
export const showSuccessToast = (title, description) => {
  return toast({
    title,
    description,
    status: 'success',
    duration: 5000,
    isClosable: true,
  })
}

// Helper function to show an error toast
export const showErrorToast = (title, description) => {
  return toast({
    title,
    description,
    status: 'error',
    duration: 5000,
    isClosable: true,
  })
}
