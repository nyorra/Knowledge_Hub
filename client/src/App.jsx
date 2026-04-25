import React, { useState, useEffect, useRef } from 'react';

function App() {
  // --- СОСТОЯНИЕ ИНТЕРФЕЙСА ---
  const [currentTab, setCurrentTab] = useState('storage');
  const [aiText, setAiText] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(''); 
  const [files, setFiles] = useState([]);
  
  // Реф для доступа к скрытому инпуту выбора файла без перезагрузки DOM
  const fileInputRef = useRef(null);

  // Автоматическая синхронизация списка файлов при монтировании компонента
  useEffect(() => {
    fetchFiles();
  }, []);

  // --- БИЗНЕС-ЛОГИКА (API CALLS) ---

  /**
   * Запрашивает актуальный список имен файлов из локального хранилища.
   * Вызывается при загрузке и после любого CRUD действия.
   */
  const fetchFiles = async () => {
    try {
      const response = await fetch('http://localhost:8000/storage/files');
      const data = await response.json();
      setFiles(data.files || []);
    } catch (error) {
      console.error('Ошибка синхронизации с базой данных:', error);
    }
  };

  /**
   * Отправка запроса к ИИ. 
   * В будущем здесь будет собираться контекст из всех файлов на бэкенде.
   */
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
      setAiResponse('Ошибка связи с AI-модулем');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Обработка загрузки физического файла через FormData.
   * FormData необходим для корректной передачи multipart/form-data потока.
   */
  const handleUploadFile = async (event) => {
    const file = event.target.files[0]; // Берем первый выбранный файл
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file); // Ключ 'file' должен совпадать с сигнатурой FastAPI (UploadFile)

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/storage/upload', {
        method: 'POST',
        body: formData, // Браузер сам выставит нужный Boundary заголовок
      });
      
      if (response.ok) await fetchFiles();
    } catch (error) {
      console.error('Критическая ошибка загрузки:', error);
    } finally {
      setLoading(false);
      event.target.value = null; // Сброс инпута для возможности повторной загрузки
    }
  };

  /**
   * Создание текстовой заметки (файла) вручную через prompt.
   * Содержимое кодируется через encodeURIComponent для безопасной передачи в URL.
   */
  const handleCreateFile = async () => {
    const filename = prompt("Введите имя нового файла (напр. notes.txt):");
    if (!filename) return;
    const content = prompt("Введите текст для сохранения:");
    
    try {
      // Используем метод GET/POST (в зависимости от бека) с Query-параметрами
      await fetch(`http://localhost:8000/storage/create?filename=${filename}&content=${encodeURIComponent(content)}`, {
        method: 'POST'
      });
      await fetchFiles(); 
    } catch (error) { console.error(error); }
  };

  /**
   * Редактирование: полная перезапись существующего файла.
   */
  const handleEditFile = async () => {
    const filename = prompt("Какой файл нужно изменить?");
    if (!filename || !files.includes(filename)) return alert("Файл не найден в текущем списке");
    const newContent = prompt("Введите новое содержимое (старое будет удалено):");
    
    try {
      await fetch(`http://localhost:8000/storage/edit?filename=${filename}&content=${encodeURIComponent(newContent)}`, {
        method: 'PUT' 
      });
      await fetchFiles();
    } catch (error) { console.error(error); }
  };

  /**
   * Удаление файла с подтверждением действия.
   */
  const handleDeleteFile = async () => {
    const filename = prompt("Имя файла для безвозвратного удаления:");
    if (!filename || !confirm(`Вы уверены, что хотите удалить ${filename}?`)) return;
    
    try {
      await fetch(`http://localhost:8000/storage/delete?filename=${filename}`, {
        method: 'DELETE'
      });
      await fetchFiles();
    } catch (error) { console.error(error); }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-4 border border-slate-200 rounded-xl shadow-md bg-white">
      
      {/* Скрытый системный элемент для выбора файлов */}
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleUploadFile} 
        className="hidden" 
        accept=".txt" // Ограничиваем расширение для чистоты Knowledge Hub
      />

      {/* ПЕРЕКЛЮЧАТЕЛЬ ВКЛАДОК */}
      <div className="flex gap-2 mb-6 border-b pb-4 w-full">
        <button 
          onClick={() => setCurrentTab('storage')} 
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${currentTab === 'storage' ? 'bg-blue-600 text-white shadow-lg' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
        >
          📁 Хранилище
        </button>
        <button 
          onClick={() => setCurrentTab('ai')} 
          className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${currentTab === 'ai' ? 'bg-blue-600 text-white shadow-lg' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
        >
          🤖 Ассистент
        </button>
      </div>

      <div className="min-h-75">
        {/* ВКЛАДКА: УПРАВЛЕНИЕ ФАЙЛАМИ */}
        {currentTab === 'storage' && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
              <h3 className="text-sm font-bold text-slate-700 mb-3 uppercase tracking-wider">База знаний (TXT)</h3>
              <ul className="space-y-2">
                {files.length > 0 ? files.map(file => (
                  <li key={file} className="bg-white p-3 rounded border border-slate-200 text-sm flex justify-between items-center shadow-sm hover:border-blue-300 transition-colors">
                    <span className="font-mono text-blue-600">{file}</span>
                    <span className="text-[10px] font-bold text-slate-400 border px-2 py-0.5 rounded">UTF-8</span>
                  </li>
                )) : (
                  <div className="text-center py-10 text-slate-400 italic font-light">Документы не загружены</div>
                )}
              </ul>
              <button onClick={fetchFiles} className="mt-3 text-xs text-blue-500 hover:text-blue-700 font-bold transition-colors">🔄 ОБНОВИТЬ СПИСОК</button>
            </div>

            {/* СЕТКА УПРАВЛЕНИЯ (CRUD) */}
            <div className="grid grid-cols-2 gap-2">
              <button 
                onClick={() => fileInputRef.current.click()} 
                className="bg-violet-600 hover:bg-violet-700 text-white py-3 rounded-lg text-xs font-bold uppercase transition-transform active:scale-95 shadow-sm"
              >
                Загрузить с ПК
              </button>
              <button 
                onClick={handleCreateFile} 
                className="bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-lg text-xs font-bold uppercase transition-transform active:scale-95 shadow-sm"
              >
                Создать текст
              </button>
              <button 
                onClick={handleEditFile} 
                className="bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg text-xs font-bold uppercase transition-transform active:scale-95 shadow-sm"
              >
                Правка
              </button>
              <button 
                onClick={handleDeleteFile} 
                className="bg-rose-600 hover:bg-rose-700 text-white py-3 rounded-lg text-xs font-bold uppercase transition-transform active:scale-95 shadow-sm"
              >
                Удалить
              </button>
            </div>
          </div>
        )}

        {/* ВКЛАДКА: ИНТЕРФЕЙС ИИ */}
        {currentTab === 'ai' && (
          <div className="flex flex-col gap-4 animate-in slide-in-from-right-4 duration-300">
            <textarea 
              value={aiText} 
              onChange={(e) => setAiText(e.target.value)} 
              placeholder="О чем рассказать, опираясь на ваши документы?" 
              className="w-full h-40 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 shadow-inner resize-none transition-all" 
              disabled={loading} 
            />
            
            <div className="flex justify-between items-center px-1">
              <span className={`text-[10px] font-bold ${aiText.length > 500 ? 'text-rose-500' : 'text-slate-400'}`}>
                ДЛИНА ЗАПРОСА: {aiText.length}
              </span>
              {loading && <div className="text-blue-600 text-[10px] font-black animate-pulse">⚙️ ИИ АНАЛИЗИРУЕТ...</div>}
            </div>

            <button 
              onClick={handleSendToAi} 
              disabled={loading || !aiText.trim()} 
              className="bg-slate-900 hover:bg-black disabled:bg-slate-300 text-white py-3 rounded-lg font-black uppercase tracking-widest transition-all shadow-md active:translate-y-1"
            >
              {loading ? 'Поиск в базе...' : 'Запустить анализ'}
            </button>

            {/* ПАНЕЛЬ ОТВЕТА */}
            {aiResponse && (
              <div className="mt-2 p-4 bg-blue-50 border-l-4 border-blue-600 rounded-r-lg shadow-inner">
                <p className="text-[10px] font-black text-blue-700 mb-2 uppercase tracking-tighter">Сгенерированный ответ:</p>
                <p className="text-sm text-slate-900 leading-relaxed font-medium">"{aiResponse}"</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
