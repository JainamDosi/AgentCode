'use client'

import { ChakraProvider, extendTheme } from '@chakra-ui/react'
import { ColorModeProvider } from './color-mode'

const theme = extendTheme({
  config: {
    initialColorMode: 'system',
    useSystemColorMode: true,
  },
})

export function Provider(props) {
  return (
    <ChakraProvider theme={theme}>
      <ColorModeProvider {...props} />
    </ChakraProvider>
  )
}
