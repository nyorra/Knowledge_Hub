# AI_Knowledge_Hub 🧠

Web-приложение для создания персональной базы знаний. Позволяет загружать файлы и получать информацию по их контексту с помощью ИИ.

## 🚀 Стек

- **AI Engine:** Python, FastAPI, LangChain
- **Frontend:** React, Tailwind CSS
- **Database:** Vector DB (ChromaDB), PostgreSQL
- **Environment:** Docker & Docker Compose

---

## 🛠 Установка и запуск

### 1. Backend (Python)

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com
   cd AI_Knowledge_Hub/src/back
   ```

2. Создайте и активируйте виртуальное окружение:

   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Запуск приложения:

   ```bash
   uvicorn main:app --reload
   ```

---

### 2. Frontend (React)

1. Перейдите в папку frontend:

   ```bash
   cd src/front
   ```

2. Установите зависимости:

   ```bash
   npm install
   ```

3. Запуск React приложения:

   ```bash
   npm start
   ```

---

## 🔒 Лицензия и авторство

**© 2025 Пышкин Влад (nyorraa). Все права защищены.**

Данный проект является интеллектуальной собственностью автора. Копирование кода, модификация или использование в коммерческих целях без письменного согласия автора **запрещены**.

По всем вопросам: [nyorraa](https://github.com)
