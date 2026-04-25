import React, { useState } from 'react';

function App() {
  // Состояние для переключения вкладок
  const [currentTab, setCurrentTab] = useState('storage');
  const [aiText, setAiText] = useState('');

  return (
    <div className="max-w-xl mx-auto mt-10 p-4 border border-slate-200 rounded-xl shadow-md">
      
      {/* Кнопки переключения сверху */}
      <div className="flex gap-2 mb-6 border-b pb-4">
        <button 
          onClick={() => setCurrentTab('storage')}
          className={`px-4 py-2 rounded ${currentTab === 'storage' ? 'bg-blue-600 text-white' : 'bg-slate-100 hover:bg-slate-200'}`}
        >
          Storage
        </button>
        <button 
          onClick={() => setCurrentTab('ai')}
          className={`px-4 py-2 rounded ${currentTab === 'ai' ? 'bg-blue-600 text-white' : 'bg-slate-100 hover:bg-slate-200'}`}
        >
          AI
        </button>
      </div>

      {/* Контент вкладок */}
      <div className="tab-content">
        
        {/* Вкладка Storage */}
        {currentTab === 'storage' && (
          <div id="storage-tab" className="flex flex-col gap-4">
            <h2 className="text-lg font-bold">Хранилище</h2>
            <button 
              onClick={() => console.log('Read file clicked')}
              className="bg-emerald-500 hover:bg-emerald-600 text-white py-2 px-4 rounded transition-colors"
            >
              Read file
            </button>
          </div>
        )}

        {/* Вкладка AI */}
        {currentTab === 'ai' && (
          <div id="ai-tab" className="flex flex-col gap-4">
            
            <h2 className="text-lg font-bold">ИИ Ассистент</h2>

            <textarea 
              value={aiText}
              onChange={(e) => setAiText(e.target.value)}
              placeholder="Введите текст для анализа..."
              className="w-full h-32 p-2 border border-slate-300 rounded focus:outline-blue-500"
            />

            <p className="text-xs text-slate-400">Символов: {aiText.length}</p>

            <button 
              onClick={() => console.log('request send to ai')}
              className="bg-emerald-500 hover:bg-emerald-600 text-white py-2 px-4 rounded transition-colors"
            >
              Отправить
            </button>
            
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
