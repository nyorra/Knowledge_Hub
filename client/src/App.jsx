import React, { useState, useEffect, useRef } from "react";

function App() {
  // --- STATE MANAGEMENT ---
  const [selectedFile, setSelectedFile] = useState(null);
  const [files, setFiles] = useState([]);
  const [currentTab, setCurrentTab] = useState("storage");
  const [aiText, setAiText] = useState("");
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState("");
  const [conversationHistory, setConversationHistory] = useState([]);

  // Modal states
  const [modal, setModal] = useState(null); // { type: 'create' | 'edit' | 'preview', data: {...} }
  const [toast, setToast] = useState(null); // { message: string, type: 'success' | 'error' | 'info' }

  // File preview
  const [fileContent, setFileContent] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  const fileInputRef = useRef(null);

  // Fetch files on mount
  useEffect(() => {
    fetchFiles();
  }, []);

  // --- HELPER FUNCTIONS ---

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const closeModal = () => {
    setModal(null);
    setFileContent("");
  };

  // --- API ACTIONS ---

  const fetchFiles = async () => {
    try {
      const response = await fetch("http://localhost:8000/storage/files");
      const data = await response.json();
      setFiles(data.files || []);
    } catch (error) {
      console.error("Storage Sync Error:", error);
      showToast("Failed to load files", "error");
    }
  };

  const fetchFileContent = async (filename) => {
    try {
      const response = await fetch(
        `http://localhost:8000/storage/content?filename=${encodeURIComponent(filename)}`,
      );
      const data = await response.json();
      return data.content || "";
    } catch (error) {
      console.error("Error fetching file content:", error);
      showToast("Failed to read file", "error");
      return "";
    }
  };

  const handlePreviewFile = async (filename) => {
    const content = await fetchFileContent(filename);
    setFileContent(content);
    setModal({ type: "preview", filename });
  };

  const handleCreateFile = () => {
    setModal({ type: "create", filename: "", content: "" });
  };

  const handleEditFile = async () => {
    if (!selectedFile) {
      showToast("Select a file to edit", "info");
      return;
    }
    const content = await fetchFileContent(selectedFile);
    setFileContent(content);
    setModal({ type: "edit", filename: selectedFile, content });
  };

  const submitCreateFile = async (filename, content) => {
    if (!filename.trim()) {
      showToast("Enter filename", "error");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/storage/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename, content }),
      });

      if (response.ok) {
        await fetchFiles();
        closeModal();
        showToast(`✓ File "${filename}" created`);
      } else {
        showToast("Failed to create file", "error");
      }
    } catch (error) {
      console.error("Create error:", error);
      showToast("Failed to update file", "error");
    }
  };

  const submitEditFile = async (filename, content) => {
    try {
      const response = await fetch("http://localhost:8000/storage/edit", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename, content }),
      });

      if (response.ok) {
        await fetchFiles();
        closeModal();
        showToast(`✓ File "${filename}" updated`);
      } else {
        showToast("Failed to update file", "error");
      }
    } catch (error) {
      console.error("Edit error:", error);
      showToast("Failed to update file", "error");
    }
  };

  const handleDeleteFile = async () => {
    if (!selectedFile) {
      showToast("Select a file to delete", "info");
      return;
    }

    if (!confirm(`Удалить файл "${selectedFile}"?`)) return;

    try {
      const response = await fetch(
        `http://localhost:8000/storage/delete?filename=${encodeURIComponent(selectedFile)}`,
        { method: "DELETE" },
      );

      if (response.ok) {
        setSelectedFile(null);
        await fetchFiles();
        showToast(`✓ File "${selectedFile}" deleted`);
      } else {
        showToast("Failed to delete file", "error");
      }
    } catch (error) {
      console.error("Delete error:", error);
      showToast("Failed to upload file", "error");
    }
  };

  const handleUploadFile = async (file) => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/storage/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        await fetchFiles();
        showToast(`✓ File "${file.name}" uploaded`);
      } else {
        showToast("Failed to upload file", "error");
      }
    } catch (error) {
      console.error("Upload error:", error);
      showToast("Failed to upload file", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleFileInputChange = (event) => {
    const file = event.target.files[0];
    handleUploadFile(file);
    event.target.value = null;
  };

  // Drag & Drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUploadFile(file);
  };

  // AI Assistant
  const handleSendToAi = async () => {
    if (!aiText.trim()) return;

    setLoading(true);
    const question = aiText;

    try {
      const response = await fetch("http://localhost:8000/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      const answer = data.answer || "Ответ не получен";

      setAiResponse(answer);
      setConversationHistory((prev) => [
        ...prev,
        { question, answer, timestamp: new Date().toISOString() },
      ]);
      setAiText("");
    } catch (error) {
      console.error("AI Error:", error);
      const errorMsg = "AI Service Unavailable";
      setAiResponse(errorMsg);
      showToast("AI service error", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading && aiText.trim()) {
        handleSendToAi();
      }
    }
  };

  const clearHistory = () => {
    setConversationHistory([]);
    setAiResponse("");
    showToast("History cleared", "info");
  };

  // --- RENDER ---

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-50 via-blue-50 to-indigo-50 py-3 px-4 pb-2">
      <div className="max-w-5xl mx-auto">
        {/* HEADER */}
        <div className="mb-4 text-center">
          <h1 className="text-3xl font-black text-slate-900 mb-1 tracking-tight">
            Knowledge Hub
          </h1>
          <p className="text-slate-600 text-xs mb-2">
            AI-powered document management & intelligent assistant
          </p>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white rounded-full shadow-sm border border-slate-200">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-xs font-medium text-slate-600">
              {files.length} документов в базе
            </span>
          </div>
        </div>

        {/* MAIN CARD */}
        <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden">
          {/* TAB SWITCHER */}
          <div className="flex border-b border-slate-200 bg-slate-50/50">
            {[
              { id: "storage", label: "Storage", icon: "📁" },
              { id: "ai", label: "AI Assistant", icon: "✨" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setCurrentTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-2 py-3 text-xs font-bold uppercase tracking-wider transition-all relative                ${
                  currentTab === tab.id
                    ? "text-indigo-600"
                    : "text-slate-500 hover:text-slate-700"
                }`}
              >
                <span className="text-xl">{tab.icon}</span>
                {tab.label}
                {currentTab === tab.id && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-indigo-600 rounded-t-full" />
                )}
              </button>
            ))}
          </div>

          {/* TAB CONTENT */}
          <div className="p-6">
            {/* STORAGE TAB */}
            {currentTab === "storage" && (
              <div className="space-y-6">
                {/* ACTION BUTTONS */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <button
                    onClick={handleCreateFile}
                    className="px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-semibold text-sm transition-all shadow-lg shadow-indigo-200 hover:shadow-xl active:scale-95"
                  >
                    Create
                  </button>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold text-sm transition-all shadow-lg shadow-blue-200 hover:shadow-xl active:scale-95"
                  >
                    Upload
                  </button>
                  <button
                    onClick={handleEditFile}
                    disabled={!selectedFile}
                    className="px-4 py-3 bg-amber-600 hover:bg-amber-700 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl font-semibold text-sm transition-all shadow-lg
  shadow-amber-200 hover:shadow-xl active:scale-95 disabled:shadow-none disabled:cursor-not-allowed"
                  >
                    Edit
                  </button>
                  <button
                    onClick={handleDeleteFile}
                    disabled={!selectedFile}
                    className="px-4 py-3 bg-rose-600 hover:bg-rose-700 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl font-semibold text-sm transition-all shadow-lg
  shadow-rose-200 hover:shadow-xl active:scale-95 disabled:shadow-none disabled:cursor-not-allowed"
                  >
                    Delete
                  </button>
                </div>

                {/* DRAG & DROP ZONE */}
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-2xl p-4 text-center transition-all ${
                    isDragging
                      ? "border-indigo-500 bg-indigo-50"
                      : "border-slate-300 bg-slate-50/50"
                  }`}
                >
                  <div className="text-3xl mb-2">📂</div>
                  <p className="text-sm font-semibold text-slate-700 mb-1">
                    Drop file here
                  </p>
                  <p className="text-xs text-slate-500">or use Upload</p>
                </div>

                {/* FILE LIST */}
                <div className="bg-slate-50/50 rounded-2xl border border-slate-200 p-5">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xs font-black text-slate-500 uppercase tracking-wider">
                      Documents ({files.length})
                    </h3>
                    <button
                      onClick={fetchFiles}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-semibold hover:underline"
                    >
                      🔄 Refresh
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-2 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
                    {files.length > 0 ? (
                      files.map((file) => (
                        <div
                          key={file}
                          onClick={() => setSelectedFile(file)}
                          onDoubleClick={() => handlePreviewFile(file)}
                          className={`group p-3 rounded-xl border transition-all cursor-pointer ${
                            selectedFile === file
                              ? "border-indigo-500 bg-indigo-50 shadow-md"
                              : "border-slate-200 bg-white hover:border-indigo-300 hover:shadow-sm"
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            <div className="text-xl shrink-0">
                              {(() => {
                                const ext = file.toLowerCase().split(".").pop();
                                if (ext === "txt") return "📄";
                                if (ext === "md" || ext === "markdown")
                                  return "📝";
                                if (ext === "pdf") return "📕";
                                if (ext === "doc" || ext === "docx")
                                  return "📘";
                                return "📎";
                              })()}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p
                                className={`font-mono text-xs truncate ${
                                  selectedFile === file
                                    ? "text-indigo-700 font-bold"
                                    : "text-slate-700"
                                }`}
                              >
                                {file}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="col-span-2 text-center py-12">
                        <div className="text-5xl mb-3">📭</div>
                        <p className="text-slate-500 font-medium mb-1 text-sm">
                          No documents
                        </p>
                        <p className="text-xs text-slate-400">
                          Create or upload your first file
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* AI ASSISTANT TAB */}
            {currentTab === "ai" && (
              <div className="space-y-6">
                {/* CONVERSATION HISTORY */}
                {conversationHistory.length > 0 && (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-xs font-black text-slate-500 uppercase tracking-wider">
                        Conversation History
                      </h3>
                      <button
                        onClick={clearHistory}
                        className="text-xs text-rose-600 hover:text-rose-700 font-semibold hover:underline"
                      >
                        Clear
                      </button>
                    </div>
                    <div className="space-y-2 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
                      {conversationHistory.map((item, idx) => (
                        <div
                          key={idx}
                          className="bg-slate-50 rounded-xl p-4 border border-slate-200"
                        >
                          <div className="flex items-start gap-2 mb-2">
                            <span className="text-lg">❓</span>
                            <p className="text-sm font-semibold text-slate-700 flex-1">
                              {item.question}
                            </p>
                          </div>
                          <div className="flex items-start gap-2 ml-7">
                            <span className="text-lg">💬</span>
                            <p className="text-sm text-slate-600 flex-1">
                              {item.answer}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* QUESTION INPUT */}
                <div className="relative">
                  <textarea
                    value={aiText}
                    onKeyDown={handleKeyDown}
                    onChange={(e) => setAiText(e.target.value)}
                    placeholder="Ask a question about your documents..."
                    className="w-full h-40 p-5 pr-16 bg-slate-50 border-2 border-slate-200 rounded-2xl focus:ring-4
  focus:ring-indigo-500/20 focus:border-indigo-400 outline-none resize-none transition-all text-sm leading-relaxed"
                    disabled={loading}
                  />
                  <div className="absolute bottom-4 right-4 flex items-center gap-3">
                    <VoiceRecorder
                      onTranscript={(text) =>
                        setAiText((prev) => prev + " " + text)
                      }
                    />
                    <span
                      className="text-xs font-semibold text-slate-400 bg-white px-3 py-1 rounded-full border
  border-slate-200"
                    >
                      {aiText.length} characters
                    </span>
                  </div>
                </div>

                {/* SEND BUTTON */}
                <button
                  onClick={handleSendToAi}
                  disabled={loading || !aiText.trim()}
                  className="w-full bg-linear-to-br from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700
  disabled:from-slate-200 disabled:to-slate-200 disabled:text-slate-400 text-white py-4 rounded-2xl font-bold text-sm
  uppercase tracking-wider transition-all shadow-xl shadow-indigo-200 hover:shadow-2xl flex items-center justify-center
  gap-3 disabled:shadow-none disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <span className="flex gap-1">
                        <span className="w-2 h-2 bg-white rounded-full animate-bounce" />
                        <span className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:-0.15s]" />
                        <span className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:-0.3s]" />
                      </span>
                      <span>Processing...</span>
                    </>
                  ) : (
                    <span>Send Query</span>
                  )}
                </button>

                {/* AI RESPONSE */}
                {aiResponse && (
                  <div
                    className="bg-linear-to-br from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-2xl p-6
  shadow-lg"
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-3 h-3 bg-indigo-500 rounded-full animate-pulse" />
                      <span className="text-xs font-black text-indigo-600 uppercase tracking-widest">
                        Ответ AI
                      </span>
                    </div>
                    <div className="prose prose-sm max-w-none">
                      <p className="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
                        {aiResponse}
                      </p>
                    </div>
                  </div>
                )}

                {/* HINT */}
                {!aiResponse && conversationHistory.length === 0 && (
                  <div className="text-center py-12">
                    <div className="text-5xl mb-4">
                      <img
                        src="Public/peter.png"
                        alt="AI"
                        className="w-40 h-40 mx-auto mb-4 object-contain"
                      />
                    </div>
                    <p className="text-slate-600 font-medium mb-2">
                      Ready to answer your questions
                    </p>
                    <p className="text-xs text-slate-400">
                      Press Enter to send, Shift+Enter for new line
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* HIDDEN FILE INPUT */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInputChange}
        className="hidden"
        accept="*"
      />

      {/* MODALS */}
      {modal && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={closeModal}
        >
          <div
            className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* CREATE MODAL */}
            {modal.type === "create" && (
              <CreateModal onSubmit={submitCreateFile} onClose={closeModal} />
            )}

            {/* EDIT MODAL */}
            {modal.type === "edit" && (
              <EditModal
                filename={modal.filename}
                initialContent={fileContent}
                onSubmit={submitEditFile}
                onClose={closeModal}
              />
            )}

            {/* PREVIEW MODAL */}
            {modal.type === "preview" && (
              <PreviewModal
                filename={modal.filename}
                content={fileContent}
                onClose={closeModal}
              />
            )}
          </div>
        </div>
      )}

      {/* TOAST NOTIFICATIONS */}
      {toast && (
        <div
          className={`fixed top-6 right-6 px-6 py-4 rounded-2xl shadow-2xl animate-in slide-in-from-top-4 duration-300 z-50 flex items-center gap-3 ${
            toast.type === "error"
              ? "bg-rose-500 text-white"
              : toast.type === "info"
                ? "bg-blue-500 text-white"
                : "bg-emerald-500 text-white"
          }`}
        >
          <span className="text-xl">
            {toast.type === "error"
              ? "❌"
              : toast.type === "info"
                ? "ℹ️"
                : "✅"}
          </span>
          <span className="font-semibold">{toast.message}</span>
        </div>
      )}
    </div>
  );
}

// --- MODAL COMPONENTS ---

function CreateModal({ onSubmit, onClose }) {
  const [filename, setFilename] = useState("");
  const [content, setContent] = useState("");

  const handleSubmit = () => {
    onSubmit(filename, content);
  };

  return (
    <>
      <div className="p-6 border-b border-slate-200">
        <h2 className="text-2xl font-bold text-slate-900">Создать файл</h2>
      </div>
      <div className="p-6 space-y-4">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Filename
          </label>
          <input
            type="text"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            placeholder="example.txt"
            className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none transition-all"
            autoFocus
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Content
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Введите текст..."
            className="w-full h-64 px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none resize-none
transition-all font-mono text-sm"
          />
        </div>
      </div>
      <div className="p-6 border-t border-slate-200 flex gap-3">
        <button
          onClick={handleSubmit}
          className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-bold transition-all shadow-lg hover:shadow-xl active:scale-95"
        >
          Create
        </button>
        <button
          onClick={onClose}
          className="flex-1 border-2 border-slate-200 hover:bg-slate-50 py-3 rounded-xl font-bold transition-all active:scale-95"
        >
          Cancel
        </button>
      </div>
    </>
  );
}

function EditModal({ filename, initialContent, onSubmit, onClose }) {
  const [content, setContent] = useState(initialContent);

  const handleSubmit = () => {
    onSubmit(filename, content);
  };

  return (
    <>
      <div className="p-6 border-b border-slate-200">
        <h2 className="text-2xl font-bold text-slate-900">Edit</h2>
        <p className="text-sm text-slate-500 mt-1 font-mono">{filename}</p>
      </div>
      <div className="p-6">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full h-96 px-4 py-3 border-2 border-slate-200 rounded-xl focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none resize-none
transition-all font-mono text-sm"
          autoFocus
        />
      </div>
      <div className="p-6 border-t border-slate-200 flex gap-3">
        <button
          onClick={handleSubmit}
          className="flex-1 bg-amber-600 hover:bg-amber-700 text-white py-3 rounded-xl font-bold transition-all shadow-lg hover:shadow-xl active:scale-95"
        >
          Save
        </button>
        <button
          onClick={onClose}
          className="flex-1 border-2 border-slate-200 hover:bg-slate-50 py-3 rounded-xl font-bold transition-all active:scale-95"
        >
          Cancel
        </button>
      </div>
    </>
  );
}

function PreviewModal({ filename, content, onClose }) {
  return (
    <>
      <div className="p-6 border-b border-slate-200">
        <h2 className="text-2xl font-bold text-slate-900">Просмотр файла</h2>
        <p className="text-sm text-slate-500 mt-1 font-mono">{filename}</p>
      </div>
      <div className="p-6 max-h-[60vh] overflow-y-auto custom-scrollbar">
        <pre className="whitespace-pre-wrap font-mono text-sm text-slate-700 bg-slate-50 p-4 rounded-xl border border-slate-200">
          {content || "(Файл пуст)"}
        </pre>
      </div>
      <div className="p-6 border-t border-slate-200 flex justify-end">
        <button
          onClick={onClose}
          className="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors"
        >
          Close
        </button>
      </div>
    </>
  );
}
export default App;

// --- VOICE RECORDER COMPONENT ---

function VoiceRecorder({ onTranscript }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((track) => track.stop());
        await transcribeAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Microphone access error:", error);
      alert("Failed to access microphone");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob) => {
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append("file", audioBlob, "recording.webm");

      const response = await fetch("http://localhost:8000/ai/transcribe", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.status === "success") {
        onTranscript(data.text);
      } else {
        alert("Transcription failed: " + data.message);
      }
    } catch (error) {
      console.error("Transcription error:", error);
      alert("Failed to transcribe audio");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <button
      onClick={isRecording ? stopRecording : startRecording}
      disabled={isProcessing}
      className={`p-2 rounded-full transition-all ${
        isRecording
          ? "bg-rose-500 hover:bg-rose-600 animate-pulse"
          : isProcessing
            ? "bg-slate-300 cursor-wait"
            : "bg-indigo-500 hover:bg-indigo-600"
      } text-white shadow-lg hover:shadow-xl active:scale-95 disabled:cursor-not-allowed`}
      title={isRecording ? "Stop recording" : "Start voice recording"}
    >
      {isProcessing ? (
        <span className="text-lg">⏳</span>
      ) : isRecording ? (
        <span className="text-lg">⏹️</span>
      ) : (
        <span className="text-lg">🎤</span>
      )}
    </button>
  );
}
