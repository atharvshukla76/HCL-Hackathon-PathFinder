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
if "assessment_queue" not in st.session_state:
    st.session_state.assessment_queue = []

def restart_journey():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm PathFinder AI. What career are you interested in pursuing, or what skills do you want to learn?"}
    ]
    st.session_state.learner_profile = LearnerProfile()
    st.session_state.career_data = None
    st.session_state.roadmap = []
    st.session_state.processing = False
    st.session_state.assessment_state = None
    st.session_state.assessment_queue = []

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
    q_index = st.session_state.assessment_state["current_q_index"]
    question = st.session_state.assessment_state["questions"][q_index]
    
    with st.chat_message("assistant"):
        st.markdown(f"**Readiness Check: {skill} (Question {q_index+1}/5)**")
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
                points = 20 if score >= 80 else 0
                st.session_state.assessment_state["score_total"] += points
                st.session_state.assessment_state["current_q_index"] += 1
                
                # Check if there are more questions for THIS skill
                if st.session_state.assessment_state["current_q_index"] < len(st.session_state.assessment_state["questions"]):
                    feedback = "✅ Correct!" if points > 0 else "❌ Incorrect."
                    st.session_state.messages.append({"role": "assistant", "content": feedback})
                else:
                    # Finished all 5 questions for this skill
                    final_score = st.session_state.assessment_state["score_total"]
                    
                    # Record it and regenerate roadmap
                    new_roadmap = st.session_state.adapter.record_assessment(
                        st.session_state.learner_profile,
                        st.session_state.career_data,
                        skill,
                        final_score
                    )
                    if new_roadmap:
                        st.session_state.roadmap = new_roadmap
                    
                    more_in_queue = len(st.session_state.assessment_queue) > 0
                    
                    msg = f"Thanks for completing the assessment for {skill}. You scored {final_score}%."
                    if final_score < 100:
                        msg += f"\n\nTo achieve true mastery, you'll need to review the missing concepts in the roadmap."
                    
                    # Update UI
                    response_msg = {
                        "role": "assistant", 
                        "content": msg,
                        "assessment_result": {"skill": skill, "score": final_score}
                    }
                    
                    if new_roadmap and not more_in_queue:
                        response_msg["roadmap"] = new_roadmap
                        
                    st.session_state.messages.append(response_msg)
                    
                    # Check if there are more skills in the queue to assess
                    if more_in_queue:
                        next_skill = st.session_state.assessment_queue.pop(0)
                        next_qs = st.session_state.adapter.run_assessment(next_skill)
                        
                        st.session_state.assessment_state = {
                            "skill": next_skill,
                            "questions": next_qs,
                            "current_q_index": 0,
                            "score_total": 0,
                            "phase": "asking"
                        }
                        st.session_state.messages.append({"role": "assistant", "content": f"Next, let's check your readiness for {next_skill}."})
                    else:
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

        # Check for assessment triggers
        if parsed_data:
            if parsed_data.get("completed_skill"):
                st.session_state.assessment_queue.append(parsed_data["completed_skill"])
            if parsed_data.get("known_skills"):
                for skill in parsed_data["known_skills"].keys():
                    if skill not in st.session_state.assessment_queue:
                        st.session_state.assessment_queue.append(skill)
                        
        if st.session_state.assessment_queue:
            next_skill = st.session_state.assessment_queue.pop(0)
            
            # Generate assessment
            questions = st.session_state.adapter.run_assessment(next_skill)
            
            if st.session_state.processing: # Still not cancelled
                intro_msg = f"Before we finalize your roadmap, let's quickly check your readiness for {next_skill}."
                st.session_state.messages.append({"role": "assistant", "content": intro_msg})
                
                st.session_state.assessment_state = {
                    "skill": next_skill,
                    "questions": questions,
                    "current_q_index": 0,
                    "score_total": 0,
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
