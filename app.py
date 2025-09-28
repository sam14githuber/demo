# app.py

import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# --- API Key Configuration ---
# For local development, create a .env file and add your GOOGLE_API_KEY
load_dotenv()

# For Streamlit Community Cloud, set the GOOGLE_API_KEY in st.secrets
# The key is fetched from environment variables or Streamlit secrets
try:
    api_key = "AIzaSyDcJXTc_FM2sNqfWrvCrYYsAPKssCPl1AQ"
    #os.getenv("GOOGLE_API_KEY") or st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except (TypeError, KeyError):
    st.error("🔑 Google API Key not found! Please set it in your .env file or Streamlit secrets.")
    st.stop()


# =======================================================================================
# AGENT DEFINITIONS
#
# In this section, we define the functions that act as our specialized AI agents.
# Each function has a specific role and uses the Gemini model to perform its task.
# =======================================================================================

def get_planner_agent():
    """Returns a configured GenerativeModel instance for the Planner Agent."""
    return genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        )
    )

def get_researcher_agent():
    """Returns a configured GenerativeModel instance for the Researcher Agent."""
    return genai.GenerativeModel("gemini-2.0-flash")

def get_writer_agent():
    """Returns a configured GenerativeModel instance for the Writer Agent."""
    return genai.GenerativeModel("gemini-2.0-flash")


# ---------------------------------------------------------------------------------------
# Agent 1: The Planner Agent
# ---------------------------------------------------------------------------------------
def create_research_plan(topic: str) -> list[str]:
    """
    Takes a research topic and generates a step-by-step research plan.
    
    This function acts as the "Planner Agent". Its sole responsibility is to
    deconstruct the user's topic into a series of actionable research questions.
    It is configured to expect a JSON response from the AI.
    
    Args:
        topic: The main topic of research.
        
    Returns:
        A list of questions that form the research plan.
    """
    planner_agent = get_planner_agent()
    
    prompt = f"""
    You are a world-class research assistant. Your task is to create a concise, step-by-step research plan 
    for the given topic. The plan should consist of 3 to 5 essential questions that, when answered, will provide 
    a comprehensive overview of the topic.

    Topic: "{topic}"

    Respond with ONLY a valid JSON array of strings, where each string is a question.
    Example: ["What is the history of X?", "What are the main components of X?", "What is the future of X?"]
    """
    
    try:
        response = planner_agent.generate_content(prompt)
        # The response.text will be a JSON string, so we parse it.
        plan = json.loads(response.text)
        return plan
    except (ValueError, json.JSONDecodeError) as e:
        st.error(f"Planner Agent Error: Could not parse the plan. Details: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred with the Planner Agent: {e}")
        return []

# ---------------------------------------------------------------------------------------
# Agent 2: The Researcher Agent
# ---------------------------------------------------------------------------------------
def conduct_research(topic: str, question: str) -> str:
    """
    Takes a topic and a specific question, and researches the answer.
    
    This function acts as the "Researcher Agent". It takes a single question from
    the plan and the overall topic for context, then generates a detailed answer.
    
    Args:
        topic: The main topic of research, for context.
        question: The specific question to be answered.
        
    Returns:
        A string containing the answer to the question.
    """
    researcher_agent = get_researcher_agent()

    prompt = f"""
    You are a highly skilled researcher. Your goal is to provide a detailed and accurate answer 
    to the question provided below. Your answer should be concise and directly address the question, 
    while keeping the main research topic in mind for context.

    Main Topic: "{topic}"
    Question to Answer: "{question}"

    Provide a clear, well-written answer.
    """
    
    try:
        response = researcher_agent.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"An unexpected error occurred with the Researcher Agent: {e}")
        return f"Error: Could not retrieve research for '{question}'."


# ---------------------------------------------------------------------------------------
# Agent 3: The Writer Agent
# ---------------------------------------------------------------------------------------
def write_summary_report(topic: str, research_findings: list[dict]) -> str:
    """
    Takes all research findings and synthesizes them into a final report.
    
    This function acts as the "Writer Agent". Its job is to take the raw
    question-and-answer pairs from the research phase and weave them into a
    coherent, well-formatted summary.
    
    Args:
        topic: The main topic of research.
        research_findings: A list of dictionaries, each with a 'question' and 'answer'.
        
    Returns:
        A final, formatted summary report as a string.
    """
    writer_agent = get_writer_agent()

    findings_text = ""
    for find in research_findings:
        findings_text += f"Question: {find['question']}\nAnswer: {find['answer']}\n\n---\n\n"

    prompt = f"""
    You are an expert report writer. Your task is to synthesize the following research findings 
    into a single, cohesive, and well-structured summary report. Do not simply list the answers; 
    weave them together into a coherent narrative that is easy to read and understand.

    The original research topic was: "{topic}"

    Use markdown for formatting (e.g., headings, bold text, bullet points) to improve readability.
    Ensure the final report flows logically from one point to the next.

    Here are the research findings you must use:
    {findings_text}
    """
    
    try:
        response = writer_agent.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An unexpected error occurred with the Writer Agent: {e}")
        return "Error: Could not generate the final report."


# =======================================================================================
# STREAMLIT UI
#
# This section defines the user interface of the application.
# =======================================================================================

st.set_page_config(page_title="Multi-Agent Researcher", page_icon="🤖", layout="wide")

st.title("🤖 Multi-Agent Research Assistant")
st.write(
    "Enter a topic, and a team of AI agents will collaborate to create a comprehensive research report for you."
)

topic = st.text_input(
    "Enter a research topic:", 
    placeholder="e.g., The future of renewable energy sources"
)

if st.button("Start Research", type="primary"):
    if not topic:
        st.error("Please enter a topic to research.")
    else:
        # --- Main Agentic Workflow Execution ---
        st.session_state.clear() # Clear previous results on a new run
        
        # 1. PLANNER AGENT EXECUTION
        with st.status("🤖 **Phase 1: Planning** - The Planner Agent is creating a research plan...", expanded=True) as status:
            plan = create_research_plan(topic)
            if not plan:
                status.update(label="Planner Agent failed. Please try a different topic.", state="error", expanded=False)
                st.stop()
            st.session_state.plan = plan
            status.update(label="✅ Plan created successfully!", state="complete", expanded=False)
        
        with st.expander("📚 View Research Plan"):
            for i, question in enumerate(st.session_state.plan, 1):
                st.write(f"{i}. {question}")

        # 2. RESEARCHER AGENT EXECUTION
        research_findings = []
        st.write("---")
        
        with st.status("🔬 **Phase 2: Researching** - The Researcher Agent is answering questions...", expanded=True) as status:
            progress_bar = st.progress(0)
            total_steps = len(st.session_state.plan)

            for i, question in enumerate(st.session_state.plan):
                status.update(label=f"🔬 Researching question {i+1}/{total_steps}: '{question}'")
                answer = conduct_research(topic, question)
                research_findings.append({'question': question, 'answer': answer})
                progress_bar.progress((i + 1) / total_steps)
            
            st.session_state.findings = research_findings
            status.update(label="✅ Research phase complete!", state="complete", expanded=False)

        with st.expander("🔍 View Research Findings"):
            for find in st.session_state.findings:
                 st.info(f"**Question:** {find['question']}\n\n**Answer:** {find['answer']}")

        # 3. WRITER AGENT EXECUTION
        st.write("---")
        with st.status("✍️ **Phase 3: Writing** - The Writer Agent is synthesizing the final report...", expanded=True) as status:
            final_report = write_summary_report(topic, st.session_state.findings)
            st.session_state.report = final_report
            status.update(label="✅ Report generated!", state="complete", expanded=False)
        
        # --- Display Final Report ---
        st.write("---")
        st.subheader("📄 Final Summary Report")
        st.markdown(st.session_state.report)
