import streamlit as st
from openai import OpenAI

# Set your OpenAI API key here (consider storing it in environment variable or Streamlit secrets for production)
client = OpenAI(api_key="your-openai-api-key-here")

# Prompt generation function
def generate_prompt(job_role):
    return f"""
You are a career mentor AI. Your task is to provide a comprehensive, step-by-step learning roadmap for someone who wants to become a {job_role}.

Instructions:
1. Break down the roadmap into stages (e.g., Foundation, Intermediate, Advanced, Projects, and Resources).
2. For each stage, include what skills, tools, and concepts should be learned.
3. Suggest relevant certifications, online courses, GitHub projects, and practical tasks.
4. Keep the tone professional, beginner-friendly, and structured.

Provide the roadmap in a bullet or numbered list format.
"""

# Function to call OpenAI API
def get_roadmap(job_role):
    prompt = generate_prompt(job_role)
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o" if using a better version
        messages=[
            {"role": "system", "content": "You are a helpful and expert AI career advisor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# Streamlit UI
st.set_page_config(page_title="Job Role to Roadmap Generator", layout="centered")
st.title("🧭 GenAI: Job Role to Learning Roadmap")

job_role = st.text_input("Enter a job role (e.g., Data Scientist, Frontend Developer, DevOps Engineer)")

if st.button("Generate Roadmap") and job_role:
    with st.spinner("Generating roadmap..."):
        try:
            roadmap = get_roadmap(job_role)
            st.subheader(f"Learning Roadmap for: {job_role}")
            st.markdown(roadmap)
        except Exception as e:
            st.error(f"Failed to generate roadmap: {e}")
