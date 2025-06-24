# 🎯 CareerPath AI - Job Role Prediction & Learning Recommendation System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)](https://openai.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)](https://sqlite.org/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-orange.svg)](https://scikit-learn.org/)

> An intelligent career guidance platform that combines machine learning with AI-powered recommendations to predict job roles and provide comprehensive learning roadmaps for career development.

## 📋 Project Overview

CareerPath AI is a comprehensive career guidance system that helps individuals discover their ideal career paths through data-driven predictions and provides personalized learning roadmaps to achieve their career goals. The system combines traditional machine learning with modern AI technologies to deliver accurate predictions and actionable career advice.

## 🚀 How to Run the Project

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package installer)

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/rushirakhe2027/Job-role-prediction-and-learning-recomandation-.git
cd Job-role-prediction-and-learning-recomandation-
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: Run the Application**
```bash
streamlit run ui.py
```

### **Step 4: Access the Application**
Open your web browser and navigate to:
```
http://localhost:8501
```

### **Optional: Enable AI-Generated Roadmaps**
For enhanced AI-powered roadmaps, configure your OpenAI API key:

**Method 1: Environment Variable (Recommended)**
```bash
# Windows
set OPENAI_API_KEY=your-api-key-here

# macOS/Linux
export OPENAI_API_KEY=your-api-key-here
```

**Method 2: Configuration File**
1. Copy `config_template.py` to `config.py`
2. Edit `config.py` and add your OpenAI API key
3. The system will automatically detect and use it

**Note**: The application works perfectly with built-in roadmaps if no API key is provided.

### **Troubleshooting**
**If you encounter import errors:**
```bash
pip install --upgrade streamlit pandas scikit-learn joblib openai numpy
```

**If port 8501 is already in use:**
```bash
streamlit run ui.py --server.port 8502
```

**For Windows permission issues:**
Run Command Prompt or PowerShell as Administrator

### 🎯 What This Project Does

1. **Career Prediction**: Analyzes 20+ personal and professional parameters to predict the most suitable job role from 12 different career paths
2. **Learning Roadmaps**: Generates detailed, phase-wise learning paths for each predicted career
3. **Resource Recommendations**: Provides specific courses, books, certifications, and project ideas
4. **Progress Tracking**: Maintains user profiles and prediction history for career development monitoring
5. **Career Exploration**: Suggests 3 related career fields for each prediction to expand opportunities

## 🛠️ Technologies Used & Why

### **Frontend & UI Framework**
- **Streamlit** - Chosen for rapid prototyping and beautiful data applications
  - Why: Easy to create interactive web apps with Python
  - Benefits: No HTML/CSS/JS knowledge required, built-in widgets
  - Usage: Complete UI including forms, dashboards, and data visualization

### **Machine Learning**
- **Scikit-learn** - Primary ML library for model development
  - Algorithm: Decision Tree Classifier
  - Why: Interpretable results, handles categorical data well
  - Performance: 95%+ accuracy on career prediction
- **Pandas** - Data manipulation and analysis
  - Usage: Data preprocessing, feature engineering, CSV handling
- **NumPy** - Numerical computing foundation
- **Joblib** - Model serialization and loading

### **AI Integration**
- **OpenAI GPT-4o-mini** - Advanced language model for content generation
  - Why: Generates human-like, contextual career advice
  - Usage: Creating personalized roadmaps, project ideas, resource recommendations
  - Benefits: Up-to-date industry insights, specific and actionable content

### **Database & Authentication**
- **SQLite** - Lightweight, serverless database
  - Why: No setup required, perfect for local applications
  - Usage: User authentication, prediction history, profile management
- **Hashlib** - Password security
  - Implementation: SHA-256 hashing for secure password storage

### **Security & Configuration**
- **Environment Variables** - Secure API key management
- **Input Validation** - Prevents SQL injection and data corruption
- **Session Management** - Secure user sessions with Streamlit

## 🏗️ System Architecture

### **Data Flow Pipeline**
```
User Input (20 parameters) → Feature Processing → ML Model → Job Prediction
                                                      ↓
User Profile ← Database Storage ← Prediction Results ← Related Careers
                                                      ↓
AI Prompts ← Career Selection ← Learning Roadmaps ← OpenAI API
```

### **Component Architecture**
```
├── Frontend (Streamlit)
│   ├── Landing Page
│   ├── Authentication System
│   ├── Prediction Interface
│   ├── Dashboard
│   └── Results Display
├── Backend Logic
│   ├── ML Prediction Engine
│   ├── AI Content Generation
│   ├── Database Operations
│   └── Session Management
├── Data Layer
│   ├── SQLite Database
│   ├── ML Models (pkl files)
│   └── Training Dataset
└── External APIs
    └── OpenAI GPT-4o-mini
```

## 🔬 How We Built This Project

### **Phase 1: Data Analysis & Model Development**
1. **Dataset Preparation**: Collected 6,903 career profiles with 20 features
2. **Feature Engineering**: 
   - Categorical encoding for skills and preferences
   - Numerical scaling for ratings and scores
   - Binary encoding for yes/no questions
3. **Model Selection**: Tested multiple algorithms, chose Decision Tree for interpretability
4. **Model Training**: Achieved 95%+ accuracy with cross-validation
5. **Model Serialization**: Saved using Joblib for production use

### **Phase 2: Web Application Development**
1. **UI Framework**: Selected Streamlit for rapid development
2. **Page Structure**: Designed multi-page application with navigation
3. **Form Design**: Created intuitive input forms for 20 parameters
4. **Database Design**: Implemented user management and prediction storage
5. **Authentication**: Added secure login/register functionality

### **Phase 3: AI Integration**
1. **Prompt Engineering**: Designed comprehensive prompts for roadmap generation
2. **API Integration**: Connected OpenAI GPT-4o-mini for content generation
3. **Content Structure**: Created templates for roadmaps, projects, and resources
4. **Fallback System**: Built built-in roadmaps for offline functionality
5. **Error Handling**: Implemented graceful degradation for API failures

### **Phase 4: Enhancement & Security**
1. **UI/UX Improvements**: Bright design with excellent text visibility
2. **Security Implementation**: API key protection, input validation
3. **Performance Optimization**: Caching, efficient database queries
4. **Testing**: Comprehensive testing of all features and edge cases

## 📊 Machine Learning Model Details

### **Input Features (20 Parameters)**
- **Skills**: Logical quotient, coding skills, public speaking, memory capability
- **Experience**: Hackathons, certifications, workshops, extra courses
- **Preferences**: Career interests, company type, subject interests
- **Capabilities**: Self-learning, teamwork, leadership aspirations
- **Background**: Reading/writing skills, introversion, work experience

### **Output Predictions (12 Job Roles)**
1. Software Engineer
2. Data Scientist  
3. Product Manager
4. DevOps Engineer
5. Mobile Developer
6. Security Analyst
7. Database Administrator
8. Network Engineer
9. Quality Assurance
10. Technical Writer
11. System Administrator
12. Business Analyst

### **Model Performance Metrics**
- **Training Data**: 6,903 career profiles
- **Accuracy**: 95%+ on test dataset
- **Algorithm**: Decision Tree Classifier
- **Cross-validation**: 5-fold CV for robust evaluation
- **Feature Importance**: Analyzed to understand prediction factors

## 🤖 AI-Powered Features

### **Intelligent Roadmap Generation**
- **Comprehensive Prompts**: 4000+ token detailed prompts for each career
- **Structured Output**: Phase-wise learning paths (Foundation → Advanced)
- **Specific Resources**: Real course names, book titles, certification codes
- **Industry Context**: Current market trends, salary expectations
- **Project Ideas**: Portfolio-worthy projects with technical specifications

### **Content Categories Generated**
1. **Learning Roadmaps**: 12-month structured career development plans
2. **Project Portfolio**: Industry-relevant projects with detailed requirements
3. **Resource Library**: Courses, books, certifications, tools, communities
4. **Career Progression**: Junior → Mid → Senior level pathways
5. **Market Analysis**: Salary ranges, demand trends, skill requirements

## 🎨 User Interface Design

### **Design Philosophy**
- **Bright Theme**: Excellent text visibility and contrast ratios
- **Modern Aesthetics**: Gradient backgrounds, smooth animations
- **Responsive Design**: Works across different screen sizes
- **Intuitive Navigation**: Clear user flow and logical organization

### **Key UI Components**
- **Landing Page**: Hero section with feature highlights
- **Authentication**: Secure login/register with form validation
- **Prediction Interface**: Step-by-step career assessment
- **Dashboard**: Personal metrics and prediction history
- **Results Display**: Multi-tab interface with comprehensive guidance

## 🔒 Security & Best Practices

### **Security Measures Implemented**
- **Password Hashing**: SHA-256 encryption for user passwords
- **SQL Injection Prevention**: Parameterized queries throughout
- **API Key Protection**: Environment variables and gitignore configuration
- **Input Validation**: Comprehensive data sanitization
- **Session Security**: Secure session management with Streamlit

### **Code Quality Standards**
- **Modular Architecture**: Separate functions for different features
- **Error Handling**: Comprehensive exception handling and graceful degradation
- **Documentation**: Detailed comments and docstrings
- **Performance**: Caching strategies and optimized database queries

## 📈 Project Impact & Results

### **Technical Achievements**
- ✅ 95%+ prediction accuracy on career recommendations
- ✅ Real-time AI content generation with fallback systems
- ✅ Comprehensive user management with secure authentication
- ✅ Scalable architecture supporting multiple concurrent users
- ✅ Production-ready code with proper error handling

### **User Experience**
- ✅ Intuitive interface requiring no technical knowledge
- ✅ Comprehensive career guidance beyond just prediction
- ✅ Personalized learning paths for skill development
- ✅ Progress tracking and history management
- ✅ Multiple career options for exploration

## 🔧 Technical Implementation Details

### **Database Schema**
```sql
-- Users table for authentication
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table for history tracking
CREATE TABLE user_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prediction_result TEXT NOT NULL,
    input_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### **AI Prompt Structure**
```python
def generate_roadmap_prompt(job_role):
    return f"""
    You are an expert career mentor with 15+ years of experience.
    Create a comprehensive learning roadmap for {job_role} including:
    
    1. Career Overview (market demand, salary ranges)
    2. Phase-wise Learning (Foundation → Advanced)
    3. Specific Resources (courses, books, certifications)
    4. Project Portfolio (5-7 industry-relevant projects)
    5. Career Progression (Junior → Senior pathways)
    
    Make it actionable with specific technologies, timelines, and milestones.
    """
```

## 🎓 Learning Outcomes

### **Skills Demonstrated**
- **Machine Learning**: End-to-end ML pipeline from data to production
- **Web Development**: Full-stack application with modern UI/UX
- **AI Integration**: Practical implementation of LLM APIs
- **Database Design**: Relational database with proper normalization
- **Security**: Authentication, encryption, and data protection
- **Software Architecture**: Modular, scalable, and maintainable code

### **Technologies Mastered**
- Python ecosystem (Pandas, NumPy, Scikit-learn, Streamlit)
- Machine Learning (Classification, Model Selection, Evaluation)
- AI/LLM Integration (OpenAI API, Prompt Engineering)
- Database Management (SQLite, SQL queries, Schema design)
- Web Development (Frontend/Backend integration)
- Security (Hashing, Authentication, Input validation)

## 🤝 Contributing

This project demonstrates modern software development practices and is open for educational use and contributions. Key areas for enhancement:

- **Model Improvements**: Additional algorithms, feature engineering
- **UI Enhancements**: Mobile responsiveness, accessibility features
- **AI Features**: More sophisticated prompt engineering, fine-tuning
- **Scalability**: Performance optimization, database enhancement
- **Analytics**: User behavior tracking, prediction accuracy monitoring

## 👨‍💻 Developer

**Rushikesh Rakhe**
- Email: rushirakhe2027@gmail.com
- GitHub: [@rushirakhe2027](https://github.com/rushirakhe2027)
- Focus: Machine Learning, AI Integration, Full-Stack Development

## 🙏 Acknowledgments

- **OpenAI** for providing advanced language models
- **Streamlit** for the excellent web application framework
- **Scikit-learn** for comprehensive machine learning tools
- **Python Community** for the rich ecosystem of libraries
- **Career Guidance Research** for insights into effective career counseling

---

⭐ **Star this repository if you found it helpful for learning ML, AI integration, or web development!**

*This project showcases the integration of traditional machine learning with modern AI technologies to solve real-world career guidance challenges.* 