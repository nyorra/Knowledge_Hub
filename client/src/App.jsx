import React, { useState, useEffect } from 'react'; // Добавил useEffect

function App() {
  const [currentTab, setCurrentTab] = useState('storage');
  const [aiText, setAiText] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(''); 
  const [files, setFiles] = useState([]);

  // --- ЭФФЕКТЫ ---
  // Автоматически подгружаем файлы при открытии приложения
  useEffect(() => {
    fetchFiles();
  }, []);

  // --- ЛОГИКА ---

  const fetchFiles = async () => {
    try {
      const response = await fetch('http://localhost:8000/storage/files');
      const data = await response.json();
      setFiles(data.files || []);
    } catch (error) {
      console.error('Ошибка загрузки файлов:', error);
    }
  };

  const handleSendToAi = async () => {
    if (!aiText.trim()) return;
    setLoading(true); 
    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: aiText }),
      });
      const data = await response.json();
      setAiResponse(data.answer || data.received);
    } catch (error) {
      setAiResponse('Ошибка сети');
    } finally {
      setLoading(false);
    }
  };


  const handleCreateFile = async () => {
    const filename = prompt("Имя файла (test.txt):");
    if (!filename) return;
    const content = prompt("Содержимое:");

    try {
      await fetch(`http://localhost:8000/storage/upload?filename=${filename}&content=${encodeURIComponent(content)}`, {
        method: 'POST'
      });
      fetchFiles(); 
    } catch (error) {
      console.error('Ошибка создания:', error);
    }
  };

  const handleEditFile = async () => {
    const filename = prompt("Какой файл изменить?");
    if (!filename || !files.includes(filename)) return alert("Файл не найден");
    const newContent = prompt("Новое содержимое:");

    try {
      await fetch(`http://localhost:8000/storage/edit?filename=${filename}&content=${encodeURIComponent(newContent)}`, {
        method: 'PUT' 
      });
      fetchFiles();
    } catch (error) {
      console.error('Ошибка изменения:', error);
    }
  };

  const handleDeleteFile = async () => {
    const filename = prompt("Имя файла для удаления:");
    if (!filename || !confirm(`Удалить ${filename}?`)) return;

    try {
      await fetch(`http://localhost:8000/storage/delete?filename=${filename}`, {
        method: 'DELETE'
      });
      fetchFiles();
    } catch (error) {
      console.error('Ошибка удаления:', error);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-4 border border-slate-200 rounded-xl shadow-md bg-white">
      {/* Tab Switcher: Исправлено w-pull на w-full */}
      <div className="flex gap-2 mb-6 border-b pb-4 w-full">
        <button 
          onClick={() => setCurrentTab('storage')}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${currentTab === 'storage' ? 'bg-blue-600 text-white shadow-lg' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
        >
          Хранилище
        </button>
        <button 
          onClick={() => setCurrentTab('ai')}
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${currentTab === 'ai' ? 'bg-blue-600 text-white shadow-lg' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
        >
          Ассистент
        </button>
      </div>

      <div className="min-h-75">
        {currentTab === 'storage' && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
              <h3 className="text-sm font-bold text-slate-700 mb-3 uppercase tracking-wider">Файлы базы знаний</h3>
              <ul className="space-y-2">
                {files.length > 0 ? files.map(file => (
                  <li key={file} className="bg-white p-3 rounded border border-slate-200 text-sm flex justify-between items-center shadow-sm">
                    <span className="font-mono text-blue-600">{file}</span>
                    <span className="text-[10px] font-bold text-slate-400 border px-2 py-0.5 rounded">TXT</span>
                  </li>
                )) : (
                  <div className="text-center py-10 text-slate-400 italic">Тут пока пусто</div>
                )}
              </ul>
              <button onClick={fetchFiles} className="mt-3 text-xs text-blue-500 hover:text-blue-700 font-medium">Sync</button>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <button onClick={handleCreateFile} className="bg-emerald-500 hover:bg-emerald-600 text-white py-2.5 rounded-lg text-sm font-semibold transition-transform active:scale-95">Создать</button>
              <button onClick={handleEditFile} className="bg-blue-500 hover:bg-blue-600 text-white py-2.5 rounded-lg text-sm font-semibold transition-transform active:scale-95">Изменить</button>
              <button onClick={handleDeleteFile} className="bg-rose-500 hover:bg-rose-600 text-white py-2.5 rounded-lg text-sm font-semibold transition-transform active:scale-95">Удалить</button>
            </div>
          </div>
        )}

        {currentTab === 'ai' && (
          <div className="flex flex-col gap-4 animate-in slide-in-from-right-4 duration-300">
            <textarea 
              value={aiText}
              onChange={(e) => setAiText(e.target.value)}
              placeholder="Спроси что-нибудь о своих документах..."
              className="w-full h-40 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none shadow-inner"
              disabled={loading}
            />
            
            <div className="flex justify-between items-center px-1">
              <span className={`text-xs ${aiText.length > 500 ? 'text-rose-500' : 'text-slate-400'}`}>Символов: {aiText.length}</span>
              {loading && <div className="flex items-center gap-2 text-blue-600 text-xs font-bold animate-pulse">⚙️ Обработка...</div>}
            </div>

            <button 
              onClick={handleSendToAi}
              disabled={loading || !aiText.trim()}
              className="bg-slate-900 hover:bg-black disabled:bg-slate-300 text-white py-3 rounded-lg font-bold transition-all shadow-md active:translate-y-0.5"
            >
              {loading ? 'Ищу в документах...' : 'Спросить ИИ'}
            </button>

            {aiResponse && (
              <div className="mt-2 p-4 bg-blue-50 border-l-4 border-blue-500 rounded-r-lg shadow-sm">
                <p className="text-xs font-bold text-blue-800 mb-2 underline">ОТВЕТ СИСТЕМЫ:</p>
                <p className="text-sm text-slate-800 leading-relaxed italic">"{aiResponse}"</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
