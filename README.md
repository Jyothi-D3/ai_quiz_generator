# 🧠 AI Quiz Generator

An intelligent quiz generation application that extracts text from PowerPoint presentations and creates interactive MCQ quizzes using OpenAI's GPT API.

## ✨ Features

- 📂 **Upload PPT/PPTX** files and extract text automatically
- 📊 **File Preview** - View slide count, file size, and extracted text preview
- ⚙️ **Customizable Quiz Settings** - Choose number of questions (5-30) and difficulty level (Simple/Medium/Complex)
- 🤖 **AI-Powered Question Generation** - Uses OpenAI GPT to create high-quality MCQs
- ⏱️ **Timed Quiz** - Auto-submit when time runs out
- 📝 **Interactive Quiz Interface** - One question at a time with Previous/Next navigation
- 📊 **Detailed Results** - Score, grade, performance message, and question-by-question review
- 🔄 **Re-take Quiz** or **Upload New PPT**
- 🌙 **Modern Dark UI** - Beautiful gradient-based design

## 🛠️ Tech Stack

- **Frontend/Backend**: [Streamlit](https://streamlit.io/)
- **PPT Parsing**: [python-pptx](https://python-pptx.readthedocs.io/)
- **AI**: [OpenAI API](https://openai.com/api/) (GPT-4o-mini)

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key

## 🚀 Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd ai-quiz-generator
```

2. **Create a virtual environment** (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up your OpenAI API key**

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-api-key-here
```

Or export it directly:

```bash
export OPENAI_API_KEY=your-api-key-here  # macOS/Linux
set OPENAI_API_KEY=your-api-key-here     # Windows
```

## 🎮 Usage

1. **Start the application**

```bash
streamlit run app.py
```

2. **Open your browser** - Streamlit will open automatically at `http://localhost:8501`

3. **Upload a PPT/PPTX file** - Drag and drop or browse for a file

4. **Configure quiz settings** - Select number of questions and difficulty

5. **Generate quiz** - Click "Generate Quiz" and wait for AI to create questions

6. **Take the quiz** - Answer questions one at a time, navigate with Previous/Next

7. **Review results** - See your score, correct/incorrect answers, and explanations

## 📁 Project Structure

```
ai-quiz-generator/
├── app.py                  # Main Streamlit application
├── utils/
│   ├── __init__.py         # Package initializer
│   ├── ppt_parser.py       # PPT/PPTX text extraction
│   ├── quiz_generator.py   # OpenAI API quiz generation
│   └── scoring.py          # Score calculation and grading
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .env                    # Environment variables (not tracked)
```

## 🔧 Configuration

- **Number of Questions**: 5 to 30
- **Difficulty Levels**: Simple, Medium, Complex
- **Timer**: Auto-calculated (30 seconds per question, min 5 min, max 30 min)
- **API Model**: gpt-4o-mini (configurable in `utils/quiz_generator.py`)

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License.