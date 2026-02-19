import { useState, useEffect } from 'react'

export default function StoryOutput({ story, loading }) {
  const [displayedText, setDisplayedText] = useState('')

  useEffect(() => {
    if (!story) {
      setDisplayedText('')
      return
    }

    // Minimal cleaning - backend decode already handles special tokens
    let cleanStory = story.trim()
    
    // Only remove these if they somehow made it through
    const removePatterns = ['undefined', 'None', 'null', 'NaN']
    removePatterns.forEach(pattern => {
      const regex = new RegExp(`\\b${pattern}\\b`, 'gi')
      cleanStory = cleanStory.replace(regex, '')
    })
    
    // Clean up excessive spaces but preserve newlines
    cleanStory = cleanStory.replace(/ {2,}/g, ' ')
    
    // Split into segments (by newlines to preserve paragraphs)
    const paragraphs = cleanStory.split('\n')
    const segments = []
    
    paragraphs.forEach((para, pIndex) => {
      const words = para.split(/\s+/).filter(w => w.trim())
      words.forEach(word => segments.push(word))
      // Add paragraph marker if not last paragraph
      if (pIndex < paragraphs.length - 1 && para.trim()) {
        segments.push('\n\n')
      }
    })
    
    console.log('Total segments to display:', segments.length)
    
    let currentIndex = 0
    setDisplayedText('')

    const interval = setInterval(() => {
      if (currentIndex < segments.length) {
        const segment = segments[currentIndex]
        
        // Check if it's a newline marker or a word
        if (segment === '\n\n') {
          setDisplayedText(prev => prev + '\n\n')
        } else if (segment && segment.trim()) {
          setDisplayedText(prev => 
            prev ? (prev.endsWith('\n\n') ? prev + segment : prev + ' ' + segment) : segment
          )
        }
        currentIndex++
      } else {
        clearInterval(interval)
      }
    }, 80) // Slightly faster for better UX

    return () => clearInterval(interval)
  }, [story])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="relative mb-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-t-2 border-emerald-500"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="h-8 w-8 bg-gradient-to-br from-emerald-400 to-cyan-500 rounded-full opacity-20 animate-pulse"></div>
          </div>
        </div>
        <p className="text-gray-400 animate-pulse">کہانی بن رہی ہے...</p>
      </div>
    )
  }

  if (!displayedText && !story) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-emerald-400/10 to-cyan-500/10 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <h2 className="text-xl text-gray-500 mb-2">کہانی شروع کریں</h2>
        <p className="text-gray-600 text-sm">اپنی کہانی کا آغاز نیچے لکھیں</p>
        <p className="text-gray-700 text-xs mt-1">Start your story below</p>
      </div>
    )
  }

  return (
    <div className="py-6">
      {/* Story Content Card */}
      <div className="bg-[#1A1A1A] rounded-2xl border border-gray-800 p-8 shadow-lg">
        <div className="flex items-center gap-2 mb-4 text-emerald-400">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span className="text-sm font-medium">تیار شدہ کہانی</span>
        </div>
        <div className="prose prose-invert max-w-none">
          <p className="text-lg text-gray-200 leading-relaxed text-right whitespace-pre-wrap" dir="rtl">
            {displayedText}
          </p>
        </div>
      </div>
    </div>
  )
}
