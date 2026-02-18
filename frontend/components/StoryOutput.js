import { useState, useEffect } from 'react'

export default function StoryOutput({ story, loading }) {
  const [displayedText, setDisplayedText] = useState('')

  useEffect(() => {
    if (!story) {
      setDisplayedText('')
      return
    }

    // Aggressive cleaning of all special tokens
    let cleanStory = story
    
    // Remove all special tokens
    const specialTokens = [
      '<EOT>', '<EOS>', '<EOP>', '<PAD>', '<UNK>', '<START>', '<END>',
      'undefined', 'None', 'null', 'NaN', 'false', 'true'
    ]
    
    specialTokens.forEach(token => {
      // Case-insensitive replacement
      const regex = new RegExp(token, 'gi')
      cleanStory = cleanStory.replace(regex, '')
    })
    
    // Remove any remaining angle bracket tokens
    cleanStory = cleanStory.replace(/<[^>]+>/g, '')
    
    // Split by spaces and filter out empty/invalid words
    const allWords = cleanStory.split(/\s+/)
    const words = allWords.filter(word => {
      if (!word || word.trim() === '') return false
      // Ensure word is defined and is a string
      if (typeof word === 'undefined' || word === 'undefined') return false
      // Filter out words that are just punctuation or look like tokens
      const cleanWord = word.trim().toLowerCase()
      if (cleanWord === 'undefined' || cleanWord === 'none' || cleanWord === 'null') return false
      if (cleanWord.startsWith('<') || cleanWord.endsWith('>')) return false
      return true
    })
    
    console.log('Words to display:', words)
    
    let currentIndex = 0
    setDisplayedText('')

    const interval = setInterval(() => {
      if (currentIndex < words.length) {
        const word = words[currentIndex]
        // Extra safety check - only add defined words
        if (word && typeof word === 'string' && word !== 'undefined') {
          setDisplayedText(prev => 
            prev + (prev ? ' ' : '') + word
          )
        }
        currentIndex++
      } else {
        clearInterval(interval)
      }
    }, 100) // 100ms delay between words

    return () => clearInterval(interval)
  }, [story])

  if (loading) {
    return (
      <div className="bg-[#1A1A1A] rounded-2xl shadow-2xl p-8 border border-gray-800">
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-t-2 border-emerald-500"></div>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div className="h-10 w-10 bg-gradient-to-br from-emerald-400 to-cyan-500 rounded-full opacity-20 animate-pulse"></div>
            </div>
          </div>
          <p className="text-gray-400 animate-pulse">کہانی بن رہی ہے...</p>
        </div>
      </div>
    )
  }

  if (!displayedText && !story) {
    return (
      <div className="bg-[#1A1A1A] rounded-2xl shadow-2xl p-8 border border-gray-800 border-dashed">
        <div className="flex flex-col items-center justify-center py-12 text-center space-y-3">
          <div className="w-16 h-16 bg-gradient-to-br from-emerald-400/10 to-cyan-500/10 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-gray-500">آپ کی کہانی یہاں ظاہر ہوگی</p>
          <p className="text-gray-600 text-sm">Your generated story will appear here</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-[#1A1A1A] rounded-2xl shadow-2xl p-6 border border-gray-800 hover:border-gray-700 transition-all duration-300">
      <h2 className="text-xl font-semibold text-gray-200 mb-4 text-right flex items-center justify-end gap-2">
        <span>تیار شدہ کہانی</span>
        <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </h2>
      <div className="max-h-96 overflow-y-auto bg-[#0F0F0F] border border-gray-800 rounded-xl p-5 custom-scrollbar">
        <p className="text-lg text-gray-200 leading-relaxed text-right whitespace-pre-wrap" dir="rtl">
          {(displayedText || '').replace(/\bundefined\b/gi, '').replace(/\s+/g, ' ').trim()}
        </p>
      </div>
    </div>
  )
}

// Example usage test block with streaming demonstration
/*
import { useState } from 'react'
import StoryOutput from './components/StoryOutput'

function StreamingExample() {
  const [story, setStory] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const sampleStory = 'ایک دفعہ کا ذکر ہے کہ ایک گاؤں میں ایک بہادر لڑکا رہتا تھا جس کا نام احمد تھا وہ بہت ہی نیک دل اور مہربان تھا ایک دن وہ جنگل میں گیا <EOT>'

  const simulateGeneration = () => {
    setIsLoading(true)
    setStory('')
    
    // Simulate API delay
    setTimeout(() => {
      setStory(sampleStory)
      setIsLoading(false)
    }, 1500)
  }

  return (
    <div className="p-8">
      <button 
        onClick={simulateGeneration}
        className="bg-purple-600 text-white px-6 py-2 rounded-lg mb-4"
      >
        Generate Story (Watch Streaming Effect)
      </button>
      <StoryOutput story={story} loading={isLoading} />
    </div>
  )
}

// Test behavior:
// 1. Click button
// 2. Loading spinner appears
// 3. After 1.5s, story appears word by word
// 4. Each word shows with 100ms delay
// 5. Stops at <EOT> token (token not displayed)
*/
