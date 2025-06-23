# 🚀 Quick Setup Guide - CareerPath AI

## 📋 Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## ⚡ Quick Start (5 minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/rushirakhe2027/Job-role-prediction-and-learning-recomandation-.git
cd Job-role-prediction-and-learning-recomandation-
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run ui.py
```

### 4. Access the Application
Open your browser and go to: `http://localhost:8501`

## 🔧 Optional: Enable AI-Generated Roadmaps

### Method 1: Environment Variable (Recommended)
```bash
# Windows
set OPENAI_API_KEY=your-api-key-here

# macOS/Linux
export OPENAI_API_KEY=your-api-key-here
```

### Method 2: Configuration File
1. Copy `config_template.py` to `config.py`
2. Edit `config.py` and add your OpenAI API key
3. The file is already in `.gitignore` for security

### Method 3: Direct Edit (Not Recommended)
Edit `ui.py` line 17 and replace `"your-openai-api-key-here"` with your actual key.

## 🎯 What You Get

### Without OpenAI API Key:
- ✅ Complete ML-powered job role prediction
- ✅ User authentication and dashboard
- ✅ Built-in career roadmaps
- ✅ All core features working

### With OpenAI API Key:
- ✅ Everything above PLUS
- 🤖 AI-generated personalized roadmaps
- 📚 Detailed learning resources
- 🛠️ Custom project ideas
- 📊 Industry-specific guidance

## 🆘 Troubleshooting

### Common Issues:

**Import Error**: 
```bash
pip install --upgrade streamlit pandas scikit-learn joblib openai
```

**Port Already in Use**:
```bash
streamlit run ui.py --server.port 8502
```

**Permission Issues (Windows)**:
Run PowerShell as Administrator

## 📞 Support
- 📧 Email: rushikeshrakhe2027@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/rushirakhe2027/Job-role-prediction-and-learning-recomandation-/issues)
- ⭐ Star the repo if it helps you!

---
*Ready to discover your career path? Let's go! 🚀* 