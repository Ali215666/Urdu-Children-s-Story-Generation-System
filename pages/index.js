import { useState } from 'react'
import StoryInput from '../components/StoryInput'
import StoryOutput from '../components/StoryOutput'

export default function Home() {
  const [story, setStory] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerateStory = async (prefix) => {
    setLoading(true)
    setStory('')
    setError('')

    try {
      // Call Vercel serverless function at /api/generate
      // This works both in development (localhost:3000) and production (vercel.app)
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prefix: prefix,
          max_length: 500 
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `Backend error: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.story) {
        // Backend already handles special tokens and formatting
        const cleanedStory = data.story.trim()
        
        console.log('Story from backend:', cleanedStory)
        console.log('Tokens generated:', data.tokens_generated)
        
        setStory(cleanedStory)
      } else {
        setError('No story was generated. Please try again.')
      }
    } catch (error) {
      console.error('Error:', error)
      setError(error.message || 'Failed to generate story. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-screen bg-[#0F0F0F] text-white flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-gray-800 px-6 py-5">
        <div className="max-w-4xl mx-auto flex items-center justify-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-cyan-500 rounded-lg flex items-center justify-center shadow-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
              اردو کہانی جنریٹر
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="max-w-4xl mx-auto px-6 py-8">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-center mb-6">
              {error}
            </div>
          )}
          <StoryOutput story={story} loading={loading} />
        </div>
      </div>

      {/* Input Area - Fixed at Bottom */}
      <div className="flex-shrink-0 border-t border-gray-800 bg-[#0F0F0F]">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <StoryInput onGenerate={handleGenerateStory} loading={loading} />
        </div>
      </div>

      {/* Custom Scrollbar Styles */}
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #1A1A1A;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #2D2D2D;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #404040;
        }
      `}</style>
    </div>
  )
}
