import { useState } from 'react'

export default function StoryInput({ onGenerate, loading }) {
  const [prefix, setPrefix] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (prefix.trim()) {
      onGenerate(prefix)
      setPrefix('')  // Clear input after submitting
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-center gap-3 bg-[#1A1A1A] rounded-2xl border border-gray-800 hover:border-gray-700 focus-within:border-emerald-500 transition-all duration-200 px-5 py-3">
        {/* Input Field */}
        <input
          type="text"
          value={prefix}
          onChange={(e) => setPrefix(e.target.value)}
          placeholder="اپنی کہانی کا آغاز یہاں لکھیں..."
          className="flex-1 bg-transparent text-gray-100 placeholder-gray-600 text-lg outline-none text-right"
          dir="rtl"
          disabled={loading}
        />
        
        {/* Send/Generate Button */}
        <button
          type="submit"
          disabled={loading || !prefix.trim()}
          className="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed rounded-xl transition-all duration-200 flex items-center justify-center shadow-lg hover:shadow-emerald-500/25 transform hover:scale-105 active:scale-95"
        >
          {loading ? (
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg className="w-5 h-5 text-white transform -rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>
    </form>
  )
}
