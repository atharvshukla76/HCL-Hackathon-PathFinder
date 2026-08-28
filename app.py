import streamlit as st
import time

from pathfinder_adapter import PathFinderAdapter
from pathfinder_engine import LearnerProfile
from ui.styles import apply_custom_styles
from ui.components import render_thinking_indicator, render_roadmap, render_readiness_result, render_progress_sidebar, render_dashboard

# Page configuration
st.set_page_config(
    page_title="PathFinder AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_styles()

# Initialize session state
if "adapter" not in st.session_state:
    st.session_state.adapter = PathFinderAdapter()
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm PathFinder AI. What career are you interested in pursuing, or what skills do you want to learn?"}
    ]
if "learner_profile" not in st.session_state:
    st.session_state.learner_profile = LearnerProfile()
if "career_data" not in st.session_state:
    st.session_state.career_data = None
if "roadmap" not in st.session_state:
    st.session_state.roadmap = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "assessment_state" not in st.session_state:
    st.session_state.assessment_state = None

def restart_journey():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm PathFinder AI. What career are you interested in pursuing, or what skills do you want to learn?"}
    ]
    st.session_state.learner_profile = LearnerProfile()
    st.session_state.career_data = None
    st.session_state.roadmap = []
    st.session_state.processing = False
    st.session_state.assessment_state = None

# Sidebar
render_progress_sidebar(st.session_state.learner_profile, st.session_state.roadmap)
with st.sidebar:
    st.button("Restart Journey", on_click=restart_journey, use_container_width=True)

# Main chat container
chat_container = st.container()

# Render chat history
with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("roadmap"):
                render_dashboard(st.session_state.learner_profile, msg["roadmap"])
                render_roadmap(msg["roadmap"])
            if msg.get("assessment_result"):
                render_readiness_result(msg["assessment_result"]["skill"], msg["assessment_result"]["score"])

# Handle Assessment state logic
if st.session_state.assessment_state and st.session_state.assessment_state.get("phase") == "asking":
    skill = st.session_state.assessment_state["skill"]
    question = st.session_state.assessment_state["question"]
    
    with st.chat_message("assistant"):
        st.markdown(f"**Readiness Check: {skill}**")
        st.markdown(question)
        
        with st.form(key="assessment_form"):
            answer = st.text_input("Your answer (e.g. A, B, C, D or text)")
            submit = st.form_submit_button("Submit")
            
            if submit:
                st.session_state.processing = True
                
                # Append user answer to messages
                st.session_state.messages.append({"role": "user", "content": answer})
                
                # Grade it
                score = st.session_state.adapter.grade_answer(question, answer)
                
                # Record it and regenerate roadmap
                new_roadmap = st.session_state.adapter.record_assessment(
                    st.session_state.learner_profile,
                    st.session_state.career_data,
                    skill,
                    score
                )
                if new_roadmap:
                    st.session_state.roadmap = new_roadmap
                
                # Update UI
                response_msg = {
                    "role": "assistant", 
                    "content": f"Thanks for completing the assessment for {skill}.",
                    "assessment_result": {"skill": skill, "score": score}
                }
                
                if new_roadmap:
                    response_msg["roadmap"] = new_roadmap
                    
                st.session_state.messages.append(response_msg)
                
                # Clear assessment state
                st.session_state.assessment_state = None
                st.session_state.processing = False
                st.rerun()

# User input area
user_input = st.chat_input("Type your message here...", disabled=st.session_state.processing or (st.session_state.assessment_state is not None))

if user_input:
    # 1. Show user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.processing = True
    st.rerun()

# Background Processing Block
if st.session_state.processing and not (st.session_state.assessment_state and st.session_state.assessment_state.get("phase") == "asking"):
    with chat_container:
        with st.chat_message("assistant"):
            
            # Determine loading text based on context
            if st.session_state.assessment_state and st.session_state.assessment_state.get("phase") == "generating":
                st.markdown("Preparing your readiness check...")
            elif st.session_state.roadmap == [] and getattr(st.session_state.learner_profile, "onboarding_complete", False):
                st.markdown("Building your learning path...")
            else:
                st.markdown("Thinking...")
                
            render_thinking_indicator()
            
            stop_container = st.empty()
            with stop_container.container():
                if st.button("⏹ Stop", key=f"stop_btn_{len(st.session_state.messages)}"):
                    st.session_state.processing = False
                    st.session_state.messages.append({"role": "assistant", "content": "Processing stopped by user."})
                    st.rerun()

    # Retrieve last user message
    last_user_msg = [m for m in st.session_state.messages if m["role"] == "user"]
    if last_user_msg and st.session_state.processing:
        text = last_user_msg[-1]["content"]
        
        parsed_data, reply_text, new_roadmap, new_career_data = st.session_state.adapter.process_message(
            text, st.session_state.learner_profile
        )
        
        if not st.session_state.processing:
            st.stop() # Abort if stopped during processing
            
        if new_career_data:
            st.session_state.career_data = new_career_data
        if new_roadmap:
            st.session_state.roadmap = new_roadmap

        # Check for assessment trigger
        if parsed_data and parsed_data.get("completed_skill"):
            completed_skill = parsed_data["completed_skill"]
            
            # Generate assessment
            question = st.session_state.adapter.run_assessment(completed_skill)
            
            if st.session_state.processing: # Still not cancelled
                intro_msg = f"Great! You finished {completed_skill}. Before we move forward, let's quickly check your readiness."
                st.session_state.messages.append({"role": "assistant", "content": intro_msg})
                
                st.session_state.assessment_state = {
                    "skill": completed_skill,
                    "question": question,
                    "phase": "asking"
                }
        else:
            if st.session_state.processing:
                response_msg = {"role": "assistant", "content": reply_text}
                if new_roadmap and len(st.session_state.messages) > 1 and "roadmap" not in st.session_state.messages[-2]:
                    # To avoid repeating the roadmap excessively, we attach it to the message.
                    # Or we just always attach if new_roadmap generated.
                    response_msg["roadmap"] = new_roadmap
                st.session_state.messages.append(response_msg)
                
        st.session_state.processing = False
        st.rerun()
