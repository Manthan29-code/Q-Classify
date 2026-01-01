# 🎓 Q-Classify - AI-Powered PDF Analyzer

Analyze your exam papers with AI-powered insights! Upload your syllabus and question papers, and let AI map each question to its corresponding chapter and concepts.

## ✨ Features

- 🔍 **AI-driven Question Categorization** - Maps questions to syllabus chapters and concepts
- 📂 **Multiple Question Papers Support** - Upload and analyze papers from different years
- 📑 **Structured PDF Reports** - Download categorized reports with insights
- 📊 **Trend Analysis** - Identify recurring concepts across years
- 🎯 **Difficulty Estimation** - AI estimates question difficulty levels
- 🗺️ **Concept Mapping** - Visual representation of concepts and relationships
- 📝 **Summary Generator** - Quick syllabus summary for revision

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone/Navigate to the project directory**
   ```bash
   cd c:\MyProject\Q-Classify
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   **Windows (Command Prompt):**
   ```bash
   venv\Scripts\activate
   ```
   
   **Windows (PowerShell):**
   ```bash
   .\venv\Scripts\Activate.ps1
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure your API key**
   
   Open the `.env` file and replace `your_gemini_api_key_here` with your actual Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key
   ```

### Running the Application

1. **Make sure virtual environment is activated** (you should see `(venv)` in your terminal)

2. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** at `http://localhost:8501`

## 📖 How to Use

1. **📤 Upload Syllabus** - Upload your course syllabus PDF
2. **📄 Upload Question Papers** - Upload one or more question paper PDFs
3. **🔍 Analyze** - Click analyze and let AI process the files
4. **📊 Explore Results** - View categorized questions, trends, and concept maps
5. **💾 Download Report** - Download the structured PDF report

## 📁 Project Structure

```
Q-Classify/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env                      # API keys (not in git)
├── .gitignore               # Git ignore rules
├── README.md                # This file
│
├── pages/                   # Streamlit multi-page app
│   ├── 1_📤_Upload_Files.py
│   ├── 2_🔍_Analysis.py
│   ├── 3_📊_Trend_Analysis.py
│   ├── 4_🔎_Custom_Search.py
│   ├── 5_📝_Summary.py
│   └── 6_🗺️_Concept_Map.py
│
├── services/                # Business logic
│   ├── pdf_extractor.py     # PDF text extraction
│   ├── pdf_generator.py     # Report generation
│   └── ai_analyzer.py       # LangChain + Gemini
│
├── components/              # UI components
│   ├── header.py
│   └── footer.py
│
├── utils/                   # Utilities
│   ├── config.py
│   └── helpers.py
│
├── assets/                  # Static files
│   └── styles.css
│
└── data/                    # Temporary storage
    ├── uploads/
    └── outputs/
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/LLM**: LangChain + Google Gemini 1.5 Pro
- **PDF Processing**: pdfplumber, PyPDF2
- **PDF Generation**: ReportLab
- **Visualization**: Plotly, streamlit-agraph, NetworkX
- **Data Processing**: Pandas

## ⚙️ Configuration

The app uses these environment variables (set in `.env`):

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Your Google Gemini API key |

## 🤝 Troubleshooting

### "ModuleNotFoundError" when running the app
Make sure you activated the virtual environment:
```bash
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

### API errors
- Verify your `GOOGLE_API_KEY` is correct in `.env`
- Check your API quota at [Google AI Studio](https://makersuite.google.com/)

### PDF extraction issues
- Ensure PDFs are text-based (not scanned images)
- Try re-uploading the file

## 📄 License

This project is for educational purposes.

---

**Empowering students with AI-driven learning insights.** 🎓
