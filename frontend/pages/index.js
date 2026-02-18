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
      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prefix: prefix,
          max_length: 50 
        }),
      })

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`)
      }

      const data = await response.json()
      
      if (data.story) {
        // Extra safety: aggressive cleaning of any remaining special tokens
        let cleanedStory = data.story
        
        // Remove common special tokens
        const specialTokens = [
          '<EOT>', '<EOS>', '<EOP>', '<PAD>', '<UNK>', '<START>', '<END>',
          'undefined', 'None', 'null', 'NaN', 'false', 'true'
        ]
        
        specialTokens.forEach(token => {
          cleanedStory = cleanedStory.split(token).join('')
        })
        
        // Remove any remaining angle bracket tokens using regex
        cleanedStory = cleanedStory.replace(/<[^>]+>/g, '')
        
        // Remove 'undefined' that might appear at word boundaries
        cleanedStory = cleanedStory.replace(/\bundefined\b/gi, '')
        
        // Clean multiple spaces and trim
        cleanedStory = cleanedStory.replace(/\s+/g, ' ').trim()
        
        console.log('Final cleaned story:', cleanedStory)
        
        setStory(cleanedStory)
      } else {
        setError('No story was generated. Please try again.')
      }
    } catch (error) {
      console.error('Error:', error)
      setError('Connection error. Make sure backend is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0F0F0F] text-white">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <header className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-cyan-500 rounded-lg flex items-center justify-center shadow-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
              اردو کہانی جنریٹر
            </h1>
          </div>
          <p className="text-gray-400 text-sm">AI-Powered Urdu Story Generator</p>
        </header>

        <div className="space-y-6">
          <StoryInput onGenerate={handleGenerateStory} loading={loading} />
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-center">
              {error}
            </div>
          )}
          <StoryOutput story={story} loading={loading} />
        </div>
      </div>
    </div>
  )
}

// Test snippet - Example of how the integration works
/*
Test flow:
1. User types prefix in StoryInput: "ایک دفعہ"
2. User clicks submit button
3. handleGenerateStory() is called with prefix
4. POST request sent to http://localhost:8000/generate
   Body: { "prefix": "ایک دفعہ", "max_length": 50 }
5. Backend responds with: { "story": "ایک دفعہ کا ذکر ہے..." }
6. StoryOutput displays the generated story
7. Loading state handled during API call

Manual test:
- Start backend: cd backend && python api.py
- Start frontend: cd frontend && npm run dev
- Visit http://localhost:3000
- Enter Urdu text and click submit
- Watch loading indicator then see result
*/
