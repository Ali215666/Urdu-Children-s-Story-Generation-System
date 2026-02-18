import { useState } from 'react'

export default function StoryInput({ onGenerate, loading }) {
  const [prefix, setPrefix] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (prefix.trim()) {
      onGenerate(prefix)
    }
  }

  return (
    <div className="bg-[#1A1A1A] rounded-2xl shadow-2xl p-6 border border-gray-800 hover:border-gray-700 transition-all duration-300">
      <h2 className="text-xl font-semibold text-gray-200 mb-4 text-right flex items-center justify-end gap-2">
        <span>کہانی کا آغاز لکھیں</span>
        <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
        </svg>
      </h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={prefix}
          onChange={(e) => setPrefix(e.target.value)}
          placeholder="شروع کریں اپنی کہانی..."
          className="w-full p-4 bg-[#0F0F0F] border border-gray-700 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-right text-gray-100 placeholder-gray-600 transition-all duration-200 hover:border-gray-600"
          dir="rtl"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !prefix.trim()}
          className="mt-4 w-full bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-600 hover:to-cyan-600 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-emerald-500/25 transform hover:scale-[1.02] active:scale-[0.98]"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>کہانی بن رہی ہے...</span>
            </span>
          ) : (
            'کہانی بنائیں'
          )}
        </button>
      </form>
    </div>
  )
}

// Example usage test block
/*
import StoryInput from './components/StoryInput'

function ExampleUsage() {
  const handleGenerate = (prefix) => {
    console.log('Generating story with prefix:', prefix)
    // Make API call or process the prefix
  }

  return (
    <div>
      <StoryInput onGenerate={handleGenerate} loading={false} />
    </div>
  )
}
*/
