# 🎯 CareerPath AI - Job Role Prediction & Learning Recommendation System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)](https://openai.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)](https://sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An intelligent career guidance platform that predicts job roles using machine learning and provides comprehensive, AI-generated learning roadmaps with personalized career recommendations.

## 🌟 Features

### 🤖 **AI-Powered Career Prediction**
- **Machine Learning Model**: Predicts from 12 job roles using 20+ parameters
- **95%+ Accuracy**: Trained on 6,900+ career profiles
- **Real-time Analysis**: Instant predictions with detailed insights

### 🎓 **Comprehensive Learning Roadmaps**
- **AI-Generated Content**: Powered by OpenAI GPT-4o-mini
- **Detailed Roadmaps**: 12-month structured learning paths
- **Specific Resources**: Real course names, books, certifications
- **Project Ideas**: Industry-relevant portfolio projects
- **Career Progression**: Junior → Mid → Senior pathways

### 👥 **User Management System**
- **Secure Authentication**: SHA-256 password hashing
- **SQLite Database**: User profiles and prediction history
- **Personal Dashboard**: Track progress and past predictions
- **Demo Mode**: Try without registration

### 🎨 **Modern UI/UX**
- **Bright Design**: Excellent text visibility and contrast
- **Responsive Layout**: Works on all device sizes
- **Interactive Elements**: Smooth animations and transitions
- **Multi-tab Interface**: Organized content presentation

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip (Python package installer)
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/rushirakhe2027/Job-role-prediction-and-learning-recomandation-.git
cd Job-role-prediction-and-learning-recomandation-
```

2. **Install dependencies**
```bash
pip install streamlit pandas scikit-learn joblib openai sqlite3 hashlib
```

3. **Run the application**
```bash
streamlit run ui.py
```

4. **Access the application**
```
Local URL: http://localhost:8501
Network URL: http://[your-ip]:8501
```

## 📊 Supported Job Roles

The ML model predicts from these 12 career paths:
- **Software Engineer** → Full Stack Developer, Frontend Developer, Backend Developer
- **Data Scientist** → Data Analyst, Machine Learning Engineer, Data Engineer
- **Product Manager** → Business Analyst, Project Manager, Scrum Master
- **DevOps Engineer** → Cloud Engineer, Site Reliability Engineer, Infrastructure Engineer
- **Mobile Developer** → iOS Developer, Android Developer, React Native Developer
- **Security Analyst** → Cybersecurity Specialist, Penetration Tester, Security Architect
- **Database Administrator** → Data Engineer, Database Developer, Data Architect
- **Network Engineer** → Cloud Network Engineer, Network Security Engineer, Systems Engineer
- **Quality Assurance** → Test Automation Engineer, QA Lead, Performance Tester
- **Technical Writer** → Documentation Specialist, Content Strategist, UX Writer
- **System Administrator** → Cloud Administrator, Linux Administrator, Windows Administrator
- **Business Analyst** → Product Owner, Requirements Analyst, Process Analyst

## 🛠️ Technical Architecture

### Machine Learning Pipeline
```
Input (20 parameters) → Feature Processing → Decision Tree Model → Job Role Prediction
```

### AI Roadmap Generation
```
Career Role → Enhanced Prompts → OpenAI API → Comprehensive Roadmaps
```

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT,
    full_name TEXT,
    created_at TIMESTAMP
);

-- Predictions table
CREATE TABLE user_predictions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    prediction_result TEXT,
    input_data TEXT,
    created_at TIMESTAMP
);
```

## 🎯 Usage Guide

### 1. **Landing Page**
- View system overview and features
- Access login/register or try demo mode

### 2. **Career Assessment**
Fill in 20 parameters including:
- **Skills**: Logical quotient, coding skills, public speaking
- **Experience**: Hackathons, certifications, workshops
- **Preferences**: Career interests, company type, subjects
- **Capabilities**: Self-learning, teamwork, leadership

### 3. **Get Predictions**
- **Primary Role**: ML-predicted job role
- **Related Careers**: 3 additional career paths
- **Confidence Score**: Prediction accuracy

### 4. **Explore Roadmaps**
For each career path, get:
- **📚 Learning Roadmap**: 12-month structured plan
- **🛠️ Project Ideas**: Portfolio-worthy projects
- **📖 Resources**: Courses, books, certifications

### 5. **Track Progress**
- Save predictions to personal dashboard
- View prediction history
- Monitor career development

## 🔧 Configuration

### OpenAI API Setup (Optional)
For AI-generated roadmaps, configure your OpenAI API key:

```python
# In ui.py, line 17
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
```

Or set environment variable:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

**Note**: The system works with built-in roadmaps if OpenAI is not configured.

## 📈 Model Performance

- **Training Data**: 6,903 career profiles
- **Features**: 20 carefully selected parameters
- **Algorithm**: Decision Tree Classifier
- **Accuracy**: 95%+ on test data
- **Predictions**: 12 distinct job roles
- **Related Careers**: 36 total career recommendations

## 🎨 UI Screenshots

### Landing Page
- Modern gradient design
- Feature highlights
- Call-to-action buttons

### Dashboard
- Personal metrics
- Prediction history
- Quick access to tools

### Prediction Interface
- Intuitive form design
- Real-time validation
- Progress indicators

### Roadmap Display
- Multi-tab interface
- AI-generated content
- Detailed learning paths

## 🔒 Security Features

- **Password Hashing**: SHA-256 encryption
- **SQL Injection Prevention**: Parameterized queries
- **Input Validation**: Comprehensive data sanitization
- **Session Management**: Secure user sessions

## 🌐 Deployment Options

### Local Development
```bash
streamlit run ui.py
```

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy with one click

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "ui.py"]
```

## 📚 Dependencies

```txt
streamlit>=1.28.0
pandas>=1.5.0
scikit-learn>=1.3.0
joblib>=1.3.0
openai>=1.0.0
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Rushikesh Rakhe**
- GitHub: [@rushirakhe2027](https://github.com/rushirakhe2027)
- LinkedIn: [Connect with me](https://linkedin.com/in/rushikesh-rakhe)

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o-mini API
- **Streamlit** for the amazing web framework
- **Scikit-learn** for machine learning capabilities
- **Career guidance community** for insights and feedback

## 📞 Support

For support, email rushikeshrakhe2027@gmail.com or create an issue on GitHub.

---

⭐ **Star this repository if it helped you in your career journey!**

## 🔗 Live Demo

Try the live application: [CareerPath AI](https://your-streamlit-app-url.streamlit.app)

---

*Built with ❤️ by Rushikesh Rakhe* 