'use client'

import { IconButton, useColorMode, useColorModeValue } from '@chakra-ui/react'
import * as React from 'react'
import { LuMoon, LuSun } from 'react-icons/lu'

export function ColorModeProvider(props) {
  return <>{props.children}</>
}

export function ColorModeIcon() {
  const { colorMode } = useColorMode()
  return colorMode === 'dark' ? <LuMoon /> : <LuSun />
}

export const ColorModeButton = React.forwardRef(
  function ColorModeButton(props, ref) {
    const { toggleColorMode } = useColorMode()
    return (
      <IconButton
        onClick={toggleColorMode}
        variant='ghost'
        aria-label='Toggle color mode'
        size='sm'
        ref={ref}
        {...props}
        icon={<ColorModeIcon />}
      />
    )
  },
)

export const LightMode = React.forwardRef(function LightMode(props, ref) {
  return (
    <span
      className='chakra-theme light'
      ref={ref}
      {...props}
    />
  )
})

export const DarkMode = React.forwardRef(function DarkMode(props, ref) {
  return (
    <span
      className='chakra-theme dark'
      ref={ref}
      {...props}
    />
  )
})
