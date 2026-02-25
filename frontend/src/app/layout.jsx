
import '../styles/globals.css'
import { AuthProvider } from '../lib/auth-context'
import { Nav } from '../components/Nav'
import { Toaster } from '../components/Toaster'
export const metadata = {
  title: 'LuminaLib',
  description: 'Library system',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className="flex min-h-screen flex-col"
        suppressHydrationWarning
      >
        <AuthProvider>
          <Nav />
          <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-8 sm:px-6 sm:py-10">
            {children}
          </main>
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  )
}