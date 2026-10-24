import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Vite blocks requests whose Host header isn't localhost/127.0.0.1 by
    // default (DNS-rebinding protection) — allow ngrok tunnels through too.
    allowedHosts: ['.ngrok-free.dev', '.ngrok-free.app', '.ngrok.io', '.ngrok.app'],
  },
})
