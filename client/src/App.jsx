import React, { useState, useEffect, useRef } from "react";

function App() {
  // --- STATE MANAGEMENT ---
  const [selectedFile, setSelectedFile] = useState(null);
  const [files, setFiles] = useState([]);
  const [currentTab, setCurrentTab] = useState("storage");
  const [aiText, setAiText] = useState("");
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState("");

  const fileInputRef = useRef(null);

  // Синхронизируем состояние фронта с хранилищем при инициализации
  useEffect(() => {
    fetchFiles();
  }, []);

  // --- API ACTIONS ---

  /**
   * Синхронизация списка имен файлов.
   */
  const fetchFiles = async () => {
    try {
      const response = await fetch("http://localhost:8000/storage/files");
      const data = await response.json();
      setFiles(data.files || []);
    } catch (error) {
      console.error("Storage Sync Error:", error);
    }
  };

  /**
   * Отправка запроса через Enter
   */
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();

      if (loading || !aiText.trim()) return;

      handleSendToAi();
    }
  };

  /**
   * RAG-интерфейс: отправка промпта.
   */
  const handleSendToAi = async () => {
    if (!aiText.trim()) return;
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: aiText }),
      });

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      const data = await response.json();

      setAiResponse(data.answer || "Ответ не получен");
    } catch (error) {
      console.error("AI Error:", error);
      setAiResponse("AI Service Unavailable");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Multipart Upload.
   * Используем FormData: браузер автоматически установит boundary для multipart/form-data.
   */
  const handleUploadFile = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/storage/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) await fetchFiles();
    } catch (error) {
      console.error("Upload Failure:", error);
    } finally {
      setLoading(false);
      event.target.value = null;
    }
  };

  /**
   * Создание "виртуальной" заметки.
   * Отправляем JSON Body (FileData), чтобы избежать проблем с кодировкой спецсимволов в URL.
   */
  const handleCreateFile = async () => {
    const filename = prompt("Enter filename (e.g. notes.txt):", "note.txt");
    if (!filename) return;

    try {
      const response = await fetch("http://localhost:8000/storage/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename, content: "Initial content" }),
      });

      if (response.ok) await fetchFiles();
    } catch (err) {
      console.error("Create Operation Error:", err);
    }
  };

  /**
   * Обновление контента существующего файла.
   * Использует PUT семантику — полная перезапись ресурса.
   */
  const handleEditFile = async () => {
    if (!selectedFile) return alert("No file selected for editing");

    const newContent = prompt(`Update content for ${selectedFile}:`);
    if (newContent === null) return; // Обработка отмены в prompt

    try {
      const response = await fetch("http://localhost:8000/storage/edit", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: selectedFile, content: newContent }),
      });

      if (response.ok) await fetchFiles();
    } catch (error) {
      console.error("Edit Operation Error:", error);
    }
  };

  /**
   * Удаление ресурса.
   * ВАЖНО: FastAPI ожидает filename как Query параметр (?filename=...)
   */
  const handleDeleteFile = async () => {
    if (!selectedFile) return alert("Select a file to delete");
    if (!confirm(`Are you sure you want to delete ${selectedFile}?`)) return;

    try {
      const response = await fetch(
        `http://localhost:8000/storage/delete?filename=${encodeURIComponent(selectedFile)}`,
        { method: "DELETE" },
      );

      if (response.ok) {
        setSelectedFile(null);
        await fetchFiles();
      }
    } catch (error) {
      console.error("Delete Operation Error:", error);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-6 border border-slate-200 rounded-2xl shadow-xl bg-white text-slate-900 font-sans">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleUploadFile}
        className="hidden"
        accept="*"
      />

      {/* ПЕРЕКЛЮЧАТЕЛЬ ВКЛАДОК */}
      <div className="flex p-1 bg-slate-100 rounded-xl mb-8">
        {[
          { id: "storage", label: "Хранилище", icon: "📁" },
          { id: "ai", label: "Ассистент", icon: "🧠" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setCurrentTab(tab.id)}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all
            ${
              currentTab === tab.id
                ? "bg-white text-slate-900 shadow-sm ring-1 ring-slate-200"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      <div className="min-h-100]">
        {/* ПАНЕЛЬ ХРАНИЛИЩЕ */}
        {currentTab === "storage" && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-400">
            <div className="bg-slate-50/50 p-5 rounded-2xl border border-slate-100 shadow-inner">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">
                  База знаний
                </h3>
                <button
                  onClick={fetchFiles}
                  className="text-[10px] text-indigo-600 hover:underline font-bold"
                >
                  ОБНОВИТЬ
                </button>
              </div>

              <div className="space-y-2 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                {files.length > 0 ? (
                  files.map((file) => (
                    <div
                      key={file}
                      onClick={() => setSelectedFile(file)}
                      className={`group p-3 rounded-xl border text-sm flex justify-between items-center transition-all cursor-pointer
                    ${
                      selectedFile === file
                        ? "border-indigo-500 bg-white shadow-md ring-1 ring-indigo-50"
                        : "border-slate-200 bg-white/50 hover:border-slate-300"
                    }`}
                    >
                      <span
                        className={`font-mono truncate ${selectedFile === file ? "text-indigo-600 font-bold" : "text-slate-600"}`}
                      >
                        {file}
                      </span>
                      {selectedFile === file && (
                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 text-slate-400 italic text-xs font-light">
                    Документы не найдены
                  </div>
                )}
              </div>
            </div>

            {/* КНОПКИ УПРАВЛЕНИЯ */}
            <div className="grid grid-cols-4 gap-2">
              {[
                {
                  label: "Создать",
                  onClick: handleCreateFile,
                  theme: "hover:bg-slate-900 hover:text-white",
                },
                {
                  label: "Загрузить",
                  onClick: () => fileInputRef.current.click(),
                  theme: "hover:bg-slate-900 hover:text-white",
                },
                {
                  label: "Правка",
                  onClick: handleEditFile,
                  theme: "hover:bg-slate-900 hover:text-white",
                },
                {
                  label: "Удалить",
                  onClick: handleDeleteFile,
                  theme:
                    "hover:bg-rose-600 hover:text-white hover:border-rose-600",
                },
              ].map((btn) => (
                <button
                  key={btn.label}
                  onClick={btn.onClick}
                  className={`border border-slate-200 bg-white py-3 rounded-xl text-[10px] font-bold text-slate-600 uppercase transition-all active:scale-95 shadow-sm ${btn.theme}`}
                >
                  {btn.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ВКЛАДКА AI */}
        {currentTab === "ai" && (
          <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-400">
            <div className="relative">
              <textarea
                value={aiText}
                onKeyDown={handleKeyDown}
                onChange={(e) => setAiText(e.target.value)}
                placeholder="Задайте вопрос по вашим данным..."
                className="w-full h-44 p-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-indigo-500/5 focus:border-indigo-400 outline-none shadow-inner resize-none transition-all text-sm leading-relaxed"
                disabled={loading}
              />
              <div className="absolute bottom-4 right-4 text-[10px] font-bold text-slate-400 bg-white px-2 py-1 rounded-md border border-slate-100">
                {aiText.length} Символов
              </div>
            </div>

            <button
              onClick={handleSendToAi}
              disabled={loading || !aiText.trim()}
              className="w-full bg-slate-900 hover:bg-black disabled:bg-slate-100 disabled:text-slate-400 text-white py-4 rounded-2xl font-bold text-xs uppercase tracking-[0.2em] transition-all shadow-xl shadow-slate-200 flex items-center justify-center gap-3"
            >
              {loading ? (
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" />
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                </span>
              ) : (
                "Запустить анализ"
              )}
            </button>

            {aiResponse && (
              <div className="p-6 bg-indigo-50/30 border border-indigo-100 rounded-2xl shadow-sm animate-in zoom-in-95 duration-300">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
                  <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">
                    AI Response
                  </span>
                </div>
                <p className="text-sm text-slate-800 leading-relaxed font-medium">
                  {aiResponse}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
