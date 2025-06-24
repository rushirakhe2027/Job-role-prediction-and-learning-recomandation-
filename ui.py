import streamlit as st
import pickle
import pandas as pd
import numpy as np
import joblib
import sqlite3
import hashlib
import datetime
import os
from pathlib import Path
try:
    from openai import OpenAI
    OPENAI_LIBRARY_AVAILABLE = True
except ImportError:
    OPENAI_LIBRARY_AVAILABLE = False

# Set OpenAI API Key (can be overridden by environment variable)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="CareerPath AI - Smart Job Role Predictor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Database setup
def init_database():
    """Initialize SQLite database for user authentication"""
    conn = sqlite3.connect('career_predictor.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        full_name TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        prediction_result TEXT,
        input_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """Verify password against hash"""
    return hash_password(password) == hashed_password

def register_user(username, email, password, full_name):
    """Register a new user"""
    conn = sqlite3.connect('career_predictor.db')
    cursor = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_password, full_name))
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username or email already exists!"
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate user login"""
    conn = sqlite3.connect('career_predictor.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, username, email, password_hash, full_name
    FROM users WHERE username = ?
    ''', (username,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user[3]):
        return True, {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[4]
        }
    return False, None

def save_prediction(user_id, prediction_result, input_data):
    """Save user prediction to database"""
    conn = sqlite3.connect('career_predictor.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_predictions (user_id, prediction_result, input_data)
        VALUES (?, ?, ?)
    ''', (user_id, prediction_result, str(input_data)))
    
    conn.commit()
    conn.close()

def get_user_predictions(user_id):
    """Get user's prediction history"""
    conn = sqlite3.connect('career_predictor.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT prediction_result, created_at
        FROM user_predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (user_id,))
    
    predictions = cursor.fetchall()
    conn.close()
    return predictions

# Initialize database
init_database()

# OpenAI Configuration with enhanced error handling
@st.cache_resource
def init_openai():
    """Initialize OpenAI client with robust error handling"""
    try:
        if not OPENAI_LIBRARY_AVAILABLE:
            return None
            
        # Get API key from environment variable or use default (for demo purposes)
        api_key = OPENAI_API_KEY
        
        if not api_key or api_key == 'your-api-key-here':
            return None
            
        # Initialize client with just the API key (avoiding potential parameter issues)
        client = OpenAI(api_key=api_key)
        
        # Test the client with a simple API call (optional - comment out to avoid API calls during init)
        # try:
        #     test_response = client.chat.completions.create(
        #         model="gpt-4o-mini",
        #         messages=[{"role": "user", "content": "Hello"}],
        #         max_tokens=5
        #     )
        # except Exception as api_error:
        #     return None
            
        return client
            
    except Exception as e:
        error_msg = str(e)
        if "proxies" in error_msg:
            # Silently handle version compatibility issues
            pass
        # Don't show other errors during initialization
        return None

# Initialize OpenAI client with better error handling
try:
    client = init_openai()
    OPENAI_AVAILABLE = client is not None
except Exception as e:
    client = None
    OPENAI_AVAILABLE = False

# Show a single info message about OpenAI status at startup
if not OPENAI_AVAILABLE and OPENAI_LIBRARY_AVAILABLE:
    st.info("💡 **Note**: Using built-in career roadmaps. To enable AI-generated roadmaps, configure your OpenAI API key.")

# Related Career Fields Mapping
RELATED_CAREERS = {
    'Applications Developer': [
        'Full Stack Developer',
        'Frontend Developer', 
        'Backend Developer'
    ],
    'CRM Technical Developer': [
        'Salesforce Developer',
        'Business Analyst',
        'ERP Developer'
    ],
    'Database Developer': [
        'Data Engineer',
        'Database Administrator',
        'Data Analyst'
    ],
    'Mobile Applications Developer': [
        'iOS Developer',
        'Android Developer',
        'React Native Developer'
    ],
    'Network Security Engineer': [
        'Cybersecurity Analyst',
        'Information Security Manager',
        'Penetration Tester'
    ],
    'Software Developer': [
        'DevOps Engineer',
        'Software Architect',
        'Technical Lead'
    ],
    'Software Engineer': [
        'Site Reliability Engineer',
        'Machine Learning Engineer',
        'Platform Engineer'
    ],
    'Software Quality Assurance (QA) / Testing': [
        'Test Automation Engineer',
        'Quality Analyst',
        'Performance Test Engineer'
    ],
    'Systems Security Administrator': [
        'Cloud Security Engineer',
        'IT Security Consultant',
        'Compliance Officer'
    ],
    'Technical Support': [
        'System Administrator',
        'Help Desk Manager',
        'IT Support Specialist'
    ],
    'UX Designer': [
        'UI Designer',
        'Product Designer',
        'Interaction Designer'
    ],
    'Web Developer': [
        'Frontend Developer',
        'Full Stack Developer',
        'Web Designer'
    ]
}

# Roadmap generation functions
def generate_roadmap_prompt(job_role):
    """Generate a comprehensive prompt for detailed career roadmap"""
    return f"""
You are an expert career mentor and industry professional with 15+ years of experience. Create a comprehensive, detailed learning roadmap for someone who wants to become a {job_role}.

REQUIREMENTS:
1. **Structure**: Organize into clear phases with specific timelines
2. **Specificity**: Include exact technologies, tools, and versions where relevant
3. **Resources**: Provide specific course names, book titles, and platform recommendations
4. **Projects**: Detail 5-7 hands-on projects with specific requirements
5. **Certifications**: List industry-recognized certifications with exam codes
6. **Skills Assessment**: Include measurable milestones for each phase
7. **Industry Context**: Explain current market trends and salary expectations
8. **Career Path**: Show progression from junior to senior levels

ROADMAP STRUCTURE:
## 🎯 {job_role} Complete Learning Roadmap

### 📊 **Career Overview**
- Current market demand and salary range
- Key responsibilities and daily tasks
- Career progression path (Junior → Mid → Senior → Lead)
- Industry trends and future outlook

### 🏗️ **Phase 1: Foundation (Months 1-3)**
- **Core Technologies**: List 5-7 fundamental technologies
- **Learning Resources**: 
  - Specific online courses (Udemy, Coursera, Pluralsight)
  - Essential books (with authors)
  - YouTube channels and tutorials
  - Free resources and documentation
- **Hands-on Practice**: 2-3 beginner projects
- **Milestone**: What you should be able to build/do after 3 months

### 🚀 **Phase 2: Intermediate (Months 4-8)**
- **Advanced Technologies**: Framework/tools for real-world development
- **Learning Resources**: 
  - Advanced courses and specializations
  - Technical blogs and publications
  - Community resources (Reddit, Discord, Stack Overflow)
- **Projects**: 2-3 intermediate projects with specific features
- **Networking**: Communities to join, conferences to attend
- **Milestone**: Portfolio-worthy projects and skills

### 🎓 **Phase 3: Advanced (Months 9-12)**
- **Expert-Level Skills**: Architecture, optimization, best practices
- **Specialization Areas**: Choose focus areas within the role
- **Learning Resources**: 
  - Professional courses and bootcamps
  - Industry publications and research papers
  - Open source contribution opportunities
- **Capstone Projects**: 1-2 complex, production-ready projects
- **Milestone**: Job-ready skills and professional portfolio

### 💼 **Phase 4: Professional Development (Months 12+)**
- **Industry Certifications**: Specific exam names and preparation resources
- **Soft Skills**: Communication, leadership, project management
- **Job Preparation**: 
  - Resume building tips
  - Interview preparation resources
  - Portfolio presentation strategies
- **Continuous Learning**: Staying updated with industry trends

### 🛠️ **Detailed Project Portfolio**
For each project, include:
- Project description and objectives
- Technologies and tools used
- Key features to implement
- Estimated time to complete
- Learning outcomes
- GitHub repository structure

### 📚 **Comprehensive Resource Library**
- **Free Resources**: (10+ specific links)
- **Paid Courses**: (5+ course recommendations with platforms)
- **Books**: (5+ essential books with authors)
- **Tools & Software**: (Complete development environment setup)
- **Communities**: (Discord servers, Reddit communities, professional groups)

### 📜 **Certification Roadmap**
- **Entry Level**: Beginner certifications (with exam codes)
- **Professional**: Industry-standard certifications
- **Expert**: Advanced/specialized certifications
- **Preparation**: Study materials and practice exams

### 💰 **Career Progression & Salary**
- **Junior Level**: Expected salary range and responsibilities
- **Mid Level**: Growth expectations and skills required
- **Senior Level**: Leadership responsibilities and compensation
- **Specialization**: High-demand niches and their requirements

### 🎯 **Monthly Milestones Checklist**
Create a month-by-month checklist of specific achievements and skills to master.

Make this roadmap actionable, specific, and comprehensive. Include real course names, specific technologies with versions, actual book titles, and measurable milestones. The goal is to create a roadmap so detailed that someone could follow it step-by-step to become job-ready in 12 months.
"""

def generate_project_prompt(job_role, project_type="portfolio"):
    """Generate specific project ideas for the job role"""
    return f"""
As a senior {job_role} and technical mentor, suggest 3 specific, detailed project ideas for someone learning to become a {job_role}.

For each project, provide:
1. **Project Name & Description**: Clear, engaging title and 2-3 sentence description
2. **Technical Requirements**: Specific technologies, frameworks, and tools to use
3. **Core Features**: 5-7 essential features to implement
4. **Advanced Features**: 3-4 optional features for extra challenge
5. **Learning Objectives**: What skills this project will teach
6. **Time Estimate**: Realistic timeline for completion
7. **Deployment Strategy**: How and where to host/deploy the project
8. **Portfolio Value**: Why this project will impress employers

Make these projects:
- **Industry-relevant**: Based on real-world applications
- **Scalable**: Can be enhanced over time
- **Portfolio-worthy**: Impressive to potential employers
- **Skill-building**: Cover different aspects of the {job_role} role
- **Current**: Use modern, in-demand technologies

Focus on projects that demonstrate both technical skills and business understanding.
"""

def generate_resources_prompt(job_role):
    """Generate specific learning resources for the job role"""
    return f"""
As an expert {job_role} and career coach, provide a comprehensive list of specific learning resources for someone pursuing a {job_role} career.

Organize resources into these categories:

### 📚 **Books** (5-7 essential books)
- Title, Author, Year
- Brief description of what makes it valuable
- Skill level (Beginner/Intermediate/Advanced)

### 🎓 **Online Courses** (8-10 courses)
- Course name, Platform (Udemy, Coursera, Pluralsight, etc.)
- Instructor name if notable
- Duration and cost
- What specific skills it covers

### 🆓 **Free Resources** (10+ resources)
- YouTube channels with subscriber count
- Documentation and official guides
- Free coding platforms and tutorials
- Open source projects to study

### 🏆 **Certifications** (5-7 certifications)
- Certification name and issuing organization
- Exam code and cost
- Prerequisites and preparation time
- Industry recognition and value

### 🛠️ **Tools & Software**
- Development environment setup
- Essential tools and their purposes
- Browser extensions and productivity tools
- Version control and collaboration tools

### 👥 **Communities & Networking**
- Reddit communities with member count
- Discord servers and Slack groups
- Professional associations and meetups
- Twitter accounts and LinkedIn groups to follow

### 📰 **Industry Publications**
- Blogs, newsletters, and magazines
- Technical publications and research sources
- Podcasts and video channels
- Conference talks and presentations

### 💻 **Practice Platforms**
- Coding challenge websites
- Project-based learning platforms
- Hackathon platforms
- Open source contribution opportunities

Make sure all resources are:
- **Current**: Updated within the last 2 years
- **Specific**: Include exact names, URLs where helpful
- **Varied**: Different learning styles and budgets
- **Actionable**: Clear next steps for each resource
"""

@st.cache_data
def get_career_roadmap(job_role):
    """Generate comprehensive career roadmap using OpenAI or provide fallback"""
    if not OPENAI_AVAILABLE or client is None:
        return get_fallback_roadmap(job_role)
    
    try:
        prompt = generate_roadmap_prompt(job_role)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior industry professional and expert career mentor with deep knowledge of current technology trends, hiring practices, and career development. You provide detailed, actionable, and industry-relevant guidance."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000  # Increased for more detailed response
        )
        return response.choices[0].message.content
    except Exception as e:
        # Enhanced error handling with specific messages
        error_msg = str(e).lower()
        if "rate limit" in error_msg:
            st.warning("⏳ OpenAI rate limit reached. Using comprehensive built-in roadmap.")
        elif "api key" in error_msg or "authentication" in error_msg:
            st.info("🔑 OpenAI API key not configured. Using detailed built-in roadmap.")
        elif "quota" in error_msg:
            st.warning("💳 OpenAI quota exceeded. Using built-in roadmap.")
        else:
            st.info("🤖 Using built-in roadmap. For AI-generated personalized roadmaps, configure OpenAI API key.")
        return get_fallback_roadmap(job_role)

@st.cache_data
def get_project_ideas(job_role):
    """Generate specific project ideas for the job role"""
    if not OPENAI_AVAILABLE or client is None:
        return get_fallback_projects(job_role)
    
    try:
        prompt = generate_project_prompt(job_role)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior software architect and project manager who designs real-world, industry-relevant projects for skill development."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=3000
        )
        return response.choices[0].message.content
    except Exception:
        return get_fallback_projects(job_role)

@st.cache_data
def get_learning_resources(job_role):
    """Generate comprehensive learning resources for the job role"""
    if not OPENAI_AVAILABLE or client is None:
        return get_fallback_resources(job_role)
    
    try:
        prompt = generate_resources_prompt(job_role)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert career coach and technical educator with comprehensive knowledge of learning resources across all technology domains."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=3500
        )
        return response.choices[0].message.content
    except Exception:
        return get_fallback_resources(job_role)

def get_fallback_projects(job_role):
    """Provide fallback project ideas when OpenAI is not available"""
    return f"""
## 🛠️ Project Ideas for {job_role}

### Project 1: Industry-Standard Application
Build a production-ready application that demonstrates core {job_role} skills with proper architecture, testing, and deployment.

### Project 2: API Integration Project
Create a project that integrates with multiple external APIs, handles data processing, and provides a user-friendly interface.

### Project 3: Full-Stack Solution
Develop a complete solution that showcases both frontend and backend skills relevant to {job_role} responsibilities.

*For detailed, personalized project ideas with specific requirements and technologies, configure OpenAI API key.*
"""

def get_fallback_resources(job_role):
    """Provide fallback learning resources when OpenAI is not available"""
    return f"""
## 📚 Learning Resources for {job_role}

### Essential Learning Paths
- Industry-standard documentation and official guides
- Reputable online learning platforms (Coursera, Udemy, Pluralsight)
- Open source projects and GitHub repositories
- Professional community forums and discussion groups

### Skill Development
- Hands-on practice through coding challenges
- Real-world project development
- Industry certification preparation
- Continuous learning through tech blogs and publications

*For comprehensive, specific resource recommendations with exact course names, books, and links, configure OpenAI API key.*
"""

# Load the model
@st.cache_resource
def load_model():
    return joblib.load('job_role_model.pkl')

model = load_model()

# Page configuration already set at the top

# Custom CSS for bright, modern UI with excellent visibility
st.markdown("""
<style>
    /* Import Google Fonts for better typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling for bright, clean interface */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main content area */
    .main .block-container {
        padding: 2rem 1rem;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin: 1rem;
    }
    
    /* Text selection with vibrant colors */
    ::selection {
        background-color: #667eea;
        color: white;
    }
    
    ::-moz-selection {
        background-color: #667eea;
        color: white;
    }
    
    /* Headers with bright, modern styling */
    h1, h2, h3, h4, h5, h6 {
        color: #2d3748 !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    /* Paragraph text with excellent readability */
    p, .stMarkdown p {
        color: #4a5568 !important;
        font-family: 'Inter', sans-serif;
        line-height: 1.7;
    }
    
    /* Form elements with bright, clean styling */
    .stSelectbox > div > div > div {
        background: linear-gradient(145deg, #ffffff, #f7fafc) !important;
        color: #2d3748 !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    .stSelectbox > div > div > div:hover {
        border-color: #667eea !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15) !important;
    }
    
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        background: linear-gradient(145deg, #ffffff, #f7fafc) !important;
        color: #2d3748 !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 16px !important;
    }
    
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 12px rgba(102, 126, 234, 0.15) !important;
    }
    
    /* Form labels with bright, readable text */
    .stSelectbox label, 
    .stNumberInput label, 
    .stTextInput label, 
    .stSlider label,
    .stCheckbox label,
    .stRadio label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        font-family: 'Inter', sans-serif;
        margin-bottom: 8px !important;
    }
    
    /* Checkboxes with modern styling */
    .stCheckbox > label {
        background: rgba(255, 255, 255, 0.8);
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin: 4px 0;
        transition: all 0.2s ease;
    }
    
    .stCheckbox > label:hover {
        background: rgba(102, 126, 234, 0.05);
        border-color: #667eea;
    }
    
    /* Slider with vibrant theme */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    
    /* Buttons with bright, modern gradient */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    }
    
    /* Main header with stunning gradient */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        padding: 1rem 0;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Hero section with bright, attractive design */
    .landing-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 4rem 2rem;
        border-radius: 24px;
        text-align: center;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .landing-hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.3;
    }
    
    /* Feature cards with bright, clean design */
    .feature-card {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .feature-card h3 {
        color: #2d3748 !important;
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1.4rem;
    }
    
    .feature-card p {
        color: #4a5568 !important;
        line-height: 1.7;
        font-size: 1rem;
    }
    
    /* Login form with bright, welcoming design */
    .login-form {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        padding: 3rem;
        border-radius: 24px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        max-width: 420px;
        margin: 2rem auto;
        border: 1px solid rgba(102, 126, 234, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Metric cards with bright, informative design */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff, #f8fafc) !important;
        border: 1px solid rgba(102, 126, 234, 0.1) !important;
        padding: 1.5rem !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.15) !important;
    }
    
    div[data-testid="metric-container"] > div {
        color: #2d3748 !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    /* Tab styling with bright, modern appearance */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255, 255, 255, 0.5);
        padding: 8px;
        border-radius: 16px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.7);
        color: #4a5568;
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transform: translateY(-2px);
    }
    
    /* Dashboard with bright, professional design */
    .user-dashboard {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 3rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(79, 172, 254, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    /* Info, success, and warning boxes with bright themes */
    .stInfo {
        background: linear-gradient(145deg, #ebf8ff, #bee3f8) !important;
        border-left: 4px solid #3182ce !important;
        color: #2a4365 !important;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stSuccess {
        background: linear-gradient(145deg, #f0fff4, #c6f6d5) !important;
        border-left: 4px solid #38a169 !important;
        color: #22543d !important;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stWarning {
        background: linear-gradient(145deg, #fffbeb, #fed7aa) !important;
        border-left: 4px solid #d69e2e !important;
        color: #744210 !important;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Additional bright styling for better visibility */
    .stMarkdown {
        color: #2d3748;
    }
    
    /* Spinner with bright theme */
    .stSpinner {
        color: #667eea !important;
    }
    
    /* Progress bar with gradient */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
</style>""", unsafe_allow_html=True)

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

# Navigation functions
def show_landing_page():
    """Display the enhanced landing page"""
    st.markdown('<h1 class="main-header">🎯 CareerPath AI</h1>', unsafe_allow_html=True)
    
    # Enhanced hero section
    st.markdown("""
    <div class="landing-hero">
        <h2>🚀 Smart Job Role Prediction & Career Guidance</h2>
        <p style="font-size: 1.3rem; margin: 2rem 0; font-weight: 300; line-height: 1.6;">
            Unlock your career potential with our cutting-edge AI technology. 
            Get personalized job role predictions and career roadmaps tailored to your unique profile.
        </p>
        <div style="display: flex; justify-content: center; gap: 3rem; margin: 3rem 0; flex-wrap: wrap;">
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: bold;">95%</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Prediction Accuracy</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: bold;">12</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Career Roles</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: bold;">20+</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Skill Parameters</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; font-weight: bold;">36</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Related Careers</div>
            </div>
        </div>
        <p style="font-size: 1.1rem; margin-top: 2rem;">
            ✨ Advanced Machine Learning • 📊 Personalized Analysis • 🎯 Career Roadmaps • 🚀 Growth Tracking
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced features section
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <h2 style="font-size: 2.5rem; color: #667eea; margin-bottom: 1rem;">Why Choose CareerPath AI?</h2>
        <p style="font-size: 1.1rem; color: #666; max-width: 600px; margin: 0 auto;">
            Experience the future of career guidance with our comprehensive platform designed for modern professionals.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">🤖</div>
            </div>
            <h3 style="color: #667eea; text-align: center;">AI-Powered Predictions</h3>
            <p style="text-align: center; line-height: 1.6;">
                Our state-of-the-art machine learning model analyzes <strong>20+ unique parameters</strong> 
                including skills, interests, and capabilities to predict your ideal career path with 
                <strong>95% accuracy</strong>.
            </p>
            <div style="text-align: center; margin-top: 1rem;">
                <span style="background: #f0f4ff; color: #667eea; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                    Machine Learning
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">📈</div>
            </div>
            <h3 style="color: #667eea; text-align: center;">Smart Career Roadmaps</h3>
            <p style="text-align: center; line-height: 1.6;">
                Get personalized learning paths for <strong>36 related career fields</strong>. 
                Our AI generates detailed roadmaps with actionable steps, skill requirements, 
                and timeline recommendations.
            </p>
            <div style="text-align: center; margin-top: 1rem;">
                <span style="background: #f0f4ff; color: #667eea; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                    AI Roadmaps
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">📊</div>
            </div>
            <h3 style="color: #667eea; text-align: center;">Career Analytics</h3>
            <p style="text-align: center; line-height: 1.6;">
                Track your career growth with comprehensive analytics. View prediction history, 
                monitor skill development, and make <strong>data-driven career decisions</strong> 
                with confidence.
            </p>
            <div style="text-align: center; margin-top: 1rem;">
                <span style="background: #f0f4ff; color: #667eea; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                    Analytics Dashboard
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f6f9fc 0%, #eef2f7 100%); padding: 3rem 2rem; border-radius: 20px; margin: 3rem 0;">
        <h2 style="text-align: center; color: #667eea; margin-bottom: 2rem; font-size: 2.2rem;">How It Works</h2>
        <div style="display: flex; justify-content: space-between; gap: 2rem; flex-wrap: wrap;">
            <div style="flex: 1; text-align: center; min-width: 200px;">
                <div style="background: #667eea; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">1</div>
                <h4 style="color: #333; margin-bottom: 0.5rem;">Complete Assessment</h4>
                <p style="color: #666; font-size: 0.9rem;">Fill out our comprehensive 20-parameter assessment covering your skills, interests, and capabilities.</p>
            </div>
            <div style="flex: 1; text-align: center; min-width: 200px;">
                <div style="background: #667eea; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">2</div>
                <h4 style="color: #333; margin-bottom: 0.5rem;">AI Analysis</h4>
                <p style="color: #666; font-size: 0.9rem;">Our advanced ML model processes your data and identifies your ideal career match from 12 job roles.</p>
            </div>
            <div style="flex: 1; text-align: center; min-width: 200px;">
                <div style="background: #667eea; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">3</div>
                <h4 style="color: #333; margin-bottom: 0.5rem;">Get Roadmaps</h4>
                <p style="color: #666; font-size: 0.9rem;">Receive personalized career roadmaps for 3 related fields with detailed learning paths and next steps.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Call to action section
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0;">
        <h2 style="color: #333; margin-bottom: 1rem;">Ready to Discover Your Career Path?</h2>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">Join thousands of professionals who have transformed their careers with CareerPath AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔑 Login", use_container_width=True, help="Sign in to your account"):
            st.session_state.page = 'login'
            st.rerun()
    
    with col2:
        if st.button("📝 Register", use_container_width=True, help="Create a new account"):
            st.session_state.page = 'register'
            st.rerun()
    
    with col3:
        if st.button("👁️ Try Demo", use_container_width=True, help="Experience the platform without signing up"):
            st.session_state.page = 'demo'
            st.rerun()
    
    # Footer section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem; padding: 2rem 0;">
        <p>🎯 CareerPath AI - Empowering careers through intelligent predictions</p>
        <p>Built with ❤️ using Machine Learning and AI technology</p>
    </div>
    """, unsafe_allow_html=True)

def show_login_page():
    """Display the login page"""
    st.markdown('<h1 class="main-header">🔑 Login to CareerPath AI</h1>', unsafe_allow_html=True)
    
    # Navigation
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
    with col_nav1:
        if st.button("🏠 Home", key="login_home"):
            st.session_state.page = 'landing'
            st.rerun()
    with col_nav2:
        if st.button("📝 Register", key="login_register"):
            st.session_state.page = 'register'
            st.rerun()
    with col_nav3:
        if st.button("👁️ Demo", key="login_demo"):
            st.session_state.page = 'demo'
            st.rerun()
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Welcome Back! 👋")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_login, col_back = st.columns(2)
            
            with col_login:
                login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            
            with col_back:
                if st.form_submit_button("← Back", use_container_width=True):
                    st.session_state.page = 'landing'
                    st.rerun()
            
            if login_button:
                if username and password:
                    success, user_info = authenticate_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_info = user_info
                        st.session_state.page = 'dashboard'
                        st.success("Login successful! 🎉")
                        st.rerun()
                    else:
                        st.error("Invalid username or password! ❌")
                else:
                    st.warning("Please fill in all fields! ⚠️")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Don't have an account?")
        if st.button("📝 Create New Account", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()

def show_register_page():
    """Display the registration page"""
    st.markdown('<h1 class="main-header">📝 Join CareerPath AI</h1>', unsafe_allow_html=True)
    
    # Navigation
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
    with col_nav1:
        if st.button("🏠 Home", key="register_home"):
            st.session_state.page = 'landing'
            st.rerun()
    with col_nav2:
        if st.button("🔑 Login", key="register_login"):
            st.session_state.page = 'login'
            st.rerun()
    with col_nav3:
        if st.button("👁️ Demo", key="register_demo"):
            st.session_state.page = 'demo'
            st.rerun()
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        with st.form("register_form"):
            st.markdown("### Create Your Account 🌟")
            full_name = st.text_input("Full Name", placeholder="Enter your full name")
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            col_register, col_back = st.columns(2)
            
            with col_register:
                register_button = st.form_submit_button("🎉 Create Account", use_container_width=True)
            
            with col_back:
                if st.form_submit_button("← Back", use_container_width=True):
                    st.session_state.page = 'landing'
                    st.rerun()
            
            if register_button:
                if all([full_name, username, email, password, confirm_password]):
                    if password != confirm_password:
                        st.error("Passwords don't match! ❌")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long! ❌")
                    else:
                        success, message = register_user(username, email, password, full_name)
                        if success:
                            st.success(message + " 🎉")
                            st.info("Please login with your new account!")
                            st.session_state.show_login_button = True
                        else:
                            st.error(message + " ❌")
                else:
                    st.warning("Please fill in all fields! ⚠️")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Show login button after successful registration
        if 'show_login_button' in st.session_state and st.session_state.show_login_button:
            if st.button("🔑 Go to Login", use_container_width=True):
                st.session_state.page = 'login'
                st.session_state.show_login_button = False
                st.rerun()
        
        st.markdown("---")
        st.markdown("### Already have an account?")
        if st.button("🔑 Login Instead", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()

def show_prediction_interface(show_nav=True):
    """Display the career prediction interface"""
    
    if show_nav:
        user = st.session_state.user_info
        
        # User navigation
        col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
        with col_nav1:
            if st.button("🏠 Home", key="predict_home"):
                st.session_state.page = 'landing'
                st.rerun()
        with col_nav2:
            if st.session_state.authenticated:
                st.write(f"**Logged in as: {user['username']}**")
            else:
                st.write("**Demo Mode**")
        with col_nav3:
            if st.session_state.authenticated:
                if st.button("🚪 Logout", key="predict_logout"):
                    st.session_state.authenticated = False
                    st.session_state.user_info = None
                    st.session_state.page = 'landing'
                    st.rerun()
        
        st.markdown("---")
    
    st.markdown("""
    <div class="prediction-section">
        <h2>🎯 Career Path Prediction</h2>
        <p>Fill in your details to get personalized job role recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Model loading
    model = load_model()
    
    # Create two columns for the form
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Skills & Capabilities")
        
        # Numeric input fields
        Logical_quotient_rating = st.slider("Logical Quotient Rating:", min_value=1, max_value=10, value=5)
        coding_skills_rating = st.slider("Coding Skills Rating:", min_value=1, max_value=10, value=5)
        hackathons = st.number_input("Number of Hackathons Participated:", min_value=0, max_value=50, value=0)
        public_speaking_points = st.slider("Public Speaking Points:", min_value=1, max_value=10, value=5)
        
        # Memory capability mapping
        memory_mapping = {"poor": 0, "medium": 1, "excellent": 2}
        selected_memory = st.selectbox("Memory Capability Score:", list(memory_mapping.keys()))
        memory_score = memory_mapping[selected_memory]

        # Yes/No encoded fields
        self_learning_capability = 1 if st.selectbox("Self-Learning Capability?", ["No", "Yes"]) == "Yes" else 0
        extra_courses = 1 if st.selectbox("Did Extra Courses?", ["No", "Yes"]) == "Yes" else 0
        senior_input = 1 if st.selectbox("Taken Inputs from Seniors?", ["No", "Yes"]) == "Yes" else 0
        team_work = 1 if st.selectbox("Worked in Teams?", ["No", "Yes"]) == "Yes" else 0
        introvert = 1 if st.selectbox("Are you Introvert?", ["No", "Yes"]) == "Yes" else 0

        skill_mapping = {"poor": 0, "medium": 1, "excellent": 2}
        selected_skill = st.selectbox("Reading/Writing Skills Level:", list(skill_mapping.keys()))
        skill_value = skill_mapping[selected_skill]
        rw_skills = skill_value

    with col2:
        st.markdown("### 🎯 Preferences & Interests")

        # Binary checkboxes
        b_hard_worker = 1 if st.checkbox("Are you a Hard Worker?") else 0
        b_smart_worker = 1 if st.checkbox("Are you a Smart Worker?") else 0
        a_management = 1 if st.checkbox("Aspired Management Role?") else 0
        a_technical = 1 if st.checkbox("Aspired Technical Role?") else 0

        # Certification mapping
        certification_mapping = {
            'information security': 4, 'shell programming': 8, 'r programming': 7,
            'distro making': 1, 'machine learning': 5, 'full stack': 2,
            'hadoop': 3, 'app development': 0, 'python': 6
        }
        selected_cert = st.selectbox("Select a Certification:", list(certification_mapping.keys()))
        cert_value = certification_mapping[selected_cert]

        # Book type mapping
        book_type_mapping = {
            'Series': 28, 'Autobiographies': 3, 'Travel': 29, 'Guide': 13,
            'Health': 14, 'Journals': 17, 'Anthology': 1, 'Dictionaries': 9
        }
        selected_book_type = st.selectbox("Select Interested Type of Books:", list(book_type_mapping.keys()))
        book_type_value = book_type_mapping[selected_book_type]

        # Workshop mapping
        workshop_mapping = {
            'testing': 6, 'database security': 2, 'game development': 3,
            'data science': 1, 'system designing': 5, 'hacking': 4,
            'cloud computing': 0, 'web technologies': 7
        }
        selected_workshop = st.selectbox("Select a Workshop Attended:", list(workshop_mapping.keys()))
        workshop_value = workshop_mapping[selected_workshop]

        # Additional fields in full width
        st.markdown("### 🏢 Career Preferences")

        col3, col4 = st.columns(2)

        with col3:
            # Interested subjects mapping
            subject_mapping = {
                'programming': 9, 'Management': 2, 'data engineering': 5,
                'networks': 7, 'Software Engineering': 3, 'cloud computing': 4,
                'parallel computing': 8, 'IOT': 1, 'Computer Architecture': 0, 'hacking': 6
            }
            selected_subject = st.selectbox("Select an Interested Subject:", list(subject_mapping.keys()))
            subject_value = subject_mapping[selected_subject]

            # Interested career area mapping
            career_area_mapping = {
                'testing': 5, 'system developer': 4, 'Business process analyst': 0,
                'security': 3, 'developer': 2, 'cloud computing': 1
            }
            selected_career_area = st.selectbox("Select Your Interested Career Area:", list(career_area_mapping.keys()))
            career_area_value = career_area_mapping[selected_career_area]

        with col4:
            # Company type mapping
            company_type_mapping = {
                'BPA': 0, 'Cloud Services': 1, 'product development': 9,
                'Testing and Maintainance Services': 7, 'SAaS services': 4,
                'Web Services': 8, 'Finance': 2, 'Sales and Marketing': 5,
                'Product based': 3, 'Service Based': 6
            }
            selected_company_type = st.selectbox("Type of company you want to settle in?", list(company_type_mapping.keys()))
            company_type_value = company_type_mapping[selected_company_type]

        # Create input DataFrame (preserved original logic)
        input_data = pd.DataFrame([[Logical_quotient_rating, coding_skills_rating, hackathons, public_speaking_points, self_learning_capability,
                                    extra_courses, senior_input, team_work, introvert, rw_skills,
                                    memory_score, b_hard_worker, b_smart_worker, a_management, a_technical, subject_value,
                                    book_type_value, cert_value, workshop_value, company_type_value, career_area_value]], columns=[
            'Logical quotient rating', 'coding skills rating', 'hackathons', 'public speaking points', 'self-learning capability?',
            'Extra-courses did', 'Taken inputs from seniors or elders', 'worked in teams ever?', 'Introvert', 'reading and writing skills',
            'memory capability score', 'B_hard worker', 'B_smart worker', 'A_Management', 'A_Technical', 'Interested subjects_code',
            'Interested Type of Books_code', 'certifications_code', 'workshops_code', 'Type of company want to settle in?_code',
            'interested career area _code'
        ])

        # Predict button
        st.markdown("---")
        col_predict, col_reset = st.columns([3, 1])
        
        with col_predict:
            if st.button("🔍 Predict My Career Path", use_container_width=True):
                with st.spinner("🤖 Analyzing your profile..."):
                    prediction = model.predict(input_data)[0]
                    
                    # Save prediction if user is logged in
                    if st.session_state.authenticated:
                        save_prediction(st.session_state.user_info['id'], prediction, input_data.to_dict())
                    
                    st.balloons()
                    st.success(f"✅ **Recommended Job Role: {prediction}**")
                    
                    # Show additional insights
                    st.markdown("### 📊 Your Profile Summary")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.metric("Logic Rating", f"{Logical_quotient_rating}/10")
                    with col_b:
                        st.metric("Coding Skills", f"{coding_skills_rating}/10")
                    with col_c:
                        st.metric("Hackathons", hackathons)
                    with col_d:
                        st.metric("Public Speaking", f"{public_speaking_points}/10")
                    
                    # Show Related Career Fields
                    st.markdown("---")
                    st.markdown("### 🎯 Related Career Fields You Can Explore")
                    
                    if prediction in RELATED_CAREERS:
                        related_careers = RELATED_CAREERS[prediction]
                        
                        st.info(f"💡 Based on your predicted role **{prediction}**, here are 3 related career paths you can also consider:")
                        
                        # Display related careers in columns
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                        padding: 1rem; border-radius: 10px; text-align: center; color: white; margin: 0.5rem 0;">
                                <h4>🚀 {related_careers[0]}</h4>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                        padding: 1rem; border-radius: 10px; text-align: center; color: white; margin: 0.5rem 0;">
                                <h4>💻 {related_careers[1]}</h4>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                                        padding: 1rem; border-radius: 10px; text-align: center; color: white; margin: 0.5rem 0;">
                                <h4>⚡ {related_careers[2]}</h4>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Career Roadmaps Section
                        st.markdown("---")
                        st.markdown("### 🗺️ Comprehensive Career Development Guide")
                        
                        if not OPENAI_AVAILABLE:
                            st.info("💡 **Note**: Using built-in roadmaps. For AI-generated personalized roadmaps, configure your OpenAI API key for detailed, industry-specific guidance.")
                        else:
                            st.success("🤖 **AI-Powered**: Generating personalized, detailed roadmaps with current industry insights and specific resources.")
                        
                        # Create tabs for each career with comprehensive content
                        tab1, tab2, tab3 = st.tabs([
                            f"🎯 {related_careers[0]}", 
                            f"💻 {related_careers[1]}", 
                            f"⚡ {related_careers[2]}"
                        ])
                        
                        with tab1:
                            st.markdown(f"# 🎯 Complete Guide: {related_careers[0]}")
                            
                            # Create sub-tabs for different aspects
                            subtab1, subtab2, subtab3 = st.tabs(["📚 Learning Roadmap", "🛠️ Project Ideas", "📖 Resources"])
                            
                            with subtab1:
                                if OPENAI_AVAILABLE:
                                    with st.spinner(f"🤖 Generating comprehensive roadmap for {related_careers[0]}..."):
                                        roadmap1 = get_career_roadmap(related_careers[0])
                                        st.markdown(roadmap1)
                                else:
                                    roadmap1 = get_career_roadmap(related_careers[0])
                                    st.markdown(roadmap1)
                            
                            with subtab2:
                                if OPENAI_AVAILABLE:
                                    with st.spinner(f"🛠️ Generating project ideas for {related_careers[0]}..."):
                                        projects1 = get_project_ideas(related_careers[0])
                                        st.markdown(projects1)
                                else:
                                    projects1 = get_project_ideas(related_careers[0])
                                    st.markdown(projects1)
                            
                            with subtab3:
                                if OPENAI_AVAILABLE:
                                    with st.spinner(f"📖 Generating learning resources for {related_careers[0]}..."):
                                        resources1 = get_learning_resources(related_careers[0])
                                        st.markdown(resources1)
                                else:
                                    resources1 = get_learning_resources(related_careers[0])
                                    st.markdown(resources1)
                        
                        with tab2:
                            st.markdown(f"# 💻 Complete Guide: {related_careers[1]}")
                            
                            # Create sub-tabs for different aspects
                            subtab1, subtab2, subtab3 = st.tabs(["📚 Learning Roadmap", "🛠️ Project Ideas", "📖 Resources"])
                            
                            with subtab1:
                                if OPENAI_AVAILABLE:
                                    with st.spinner(f"🤖 Generating comprehensive roadmap for {related_careers[1]}..."):
                                        roadmap2 = get_career_roadmap(related_careers[1])
                                        st.markdown(roadmap2)
                                else:
                                    roadmap2 = get_career_roadmap(related_careers[1])
                                    st.markdown(roadmap2)
                            
                            with subtab2:
                                if OPENAI_AVAILABLE:
                                    with st.spinner(f"🛠️ Generating project ideas for {related_careers[1]}..."):
                                        projects2 = get_project_ideas(related_careers[1])
                                        st.markdown(projects2)
                                else:
                                    projects2 = get_project_ideas(related_careers[1])
                                    st.markdown(projects2)
                            
                            with subtab3:
                                if OPENAI_AVAILABLE:
                                    with st.spinner(f"📖 Generating learning resources for {related_careers[1]}..."):
                                        resources2 = get_learning_resources(related_careers[1])
                                        st.markdown(resources2)
                                else:
                                    resources2 = get_learning_resources(related_careers[1])
                                    st.markdown(resources2)
                        
                        with tab3:
                            st.markdown(f"# ⚡ Complete Guide: {related_careers[2]}")
                            
                            # Create sub-tabs for different aspects
                            subtab1, subtab2, subtab3 = st.tabs(["📚 Learning Roadmap", "🛠️ Project Ideas", "📖 Resources"])
                            
                            with subtab1:
                                if OPENAI_AVAILABLE:
                                    with st.spinner(f"🤖 Generating comprehensive roadmap for {related_careers[2]}..."):
                                        roadmap3 = get_career_roadmap(related_careers[2])
                                        st.markdown(roadmap3)
                                else:
                                    roadmap3 = get_career_roadmap(related_careers[2])
                                    st.markdown(roadmap3)
                            
                            with subtab2:
                                if OPENAI_AVAILABLE:
                                    with st.spinner(f"🛠️ Generating project ideas for {related_careers[2]}..."):
                                        projects3 = get_project_ideas(related_careers[2])
                                        st.markdown(projects3)
                                else:
                                    projects3 = get_project_ideas(related_careers[2])
                                    st.markdown(projects3)
                            
                            with subtab3:
                                if OPENAI_AVAILABLE:
                                    with st.spinner(f"📖 Generating learning resources for {related_careers[2]}..."):
                                        resources3 = get_learning_resources(related_careers[2])
                                        st.markdown(resources3)
                                else:
                                    resources3 = get_learning_resources(related_careers[2])
                                    st.markdown(resources3)
                        
                        # Additional Career Guidance
                        st.markdown("---")
                        st.markdown("### 💡 Next Steps")
                        st.info("""
                        **🎯 How to Use This Information:**
                        1. **Primary Path**: Focus on your predicted role - **{}**
                        2. **Explore Options**: Consider the 3 related career fields based on your interests
                        3. **Follow Roadmaps**: Use the detailed learning paths above to build required skills
                        4. **Start Learning**: Begin with Foundation level skills and progress step by step
                        5. **Build Projects**: Apply your learning through hands-on projects
                        """.format(prediction))
                        
                    else:
                        st.warning("Related career recommendations not available for this role.")
                        
                    # Final motivation message
                    st.markdown("---")
                    st.success("🌟 **Remember**: Your career journey is unique. Use this as a guide, but don't limit yourself to these suggestions. Keep learning and exploring! 🚀")
        
        with col_reset:
            if st.button("🔄 Reset", use_container_width=True):
                st.rerun()

def show_dashboard():
    """Display user dashboard"""
    user = st.session_state.user_info
    
    # User navigation
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
    with col_nav1:
        if st.button("🏠 Home", key="dashboard_home"):
            st.session_state.page = 'landing'
            st.rerun()
    with col_nav2:
        st.write(f"**Logged in as: {user['username']}**")
    with col_nav3:
        if st.button("🚪 Logout", key="dashboard_logout"):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.page = 'landing'
            st.rerun()
    
    st.markdown("---")
    
    st.markdown(f"""
    <div class="user-dashboard">
        <h2>👋 Welcome back, {user['full_name']}!</h2>
        <p>Ready to explore your career path? Let's make some predictions!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboard metrics
    predictions = get_user_predictions(user['id'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯</h3>
            <h2>{}</h2>
            <p>Total Predictions</p>
        </div>
        """.format(len(predictions)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>👤</h3>
            <h2>{}</h2>
            <p>Profile Score</p>
        </div>
        """.format("95%"), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📈</h3>
            <h2>{}</h2>
            <p>Growth Rate</p>
        </div>
        """.format("+12%"), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🏆</h3>
            <h2>{}</h2>
            <p>Accuracy</p>
        </div>
        """.format("98%"), unsafe_allow_html=True)
    
    # Recent predictions
    if predictions:
        st.markdown("### 📊 Recent Predictions")
        for i, (prediction, date) in enumerate(predictions[:5]):
            with st.expander(f"Prediction #{i+1} - {prediction} ({date[:10]})"):
                st.write(f"**Result:** {prediction}")
                st.write(f"**Date:** {date}")
    
    # Main prediction interface
    show_prediction_interface(show_nav=False)

def show_demo_mode():
    """Display demo mode"""
    st.markdown('<h1 class="main-header">👁️ Demo Mode</h1>', unsafe_allow_html=True)
    
    # Navigation
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
    with col_nav1:
        if st.button("🏠 Home", key="demo_home"):
            st.session_state.page = 'landing'
            st.rerun()
    with col_nav2:
        if st.button("🔑 Login", key="demo_login"):
            st.session_state.page = 'login'
            st.rerun()
    with col_nav3:
        if st.button("📝 Register", key="demo_register"):
            st.session_state.page = 'register'
            st.rerun()
    
    st.markdown("---")
    
    st.info("🔍 **Demo Mode**: Explore the prediction system without creating an account. Your predictions won't be saved.")
    
    show_prediction_interface()

# Navigation buttons moved to main content area

# Main content routing
if st.session_state.page == 'landing':
    show_landing_page()
elif st.session_state.page == 'login':
    show_login_page()
elif st.session_state.page == 'register':
    show_register_page()
elif st.session_state.page == 'dashboard' and st.session_state.authenticated:
    show_dashboard()
elif st.session_state.page == 'demo':
    show_demo_mode()
else:
    # Default to landing if something goes wrong
    st.session_state.page = 'landing'
    show_landing_page()



