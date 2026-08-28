import streamlit as st
import textwrap

def render_thinking_indicator():
    html = """
<div class="thinking-dots">
<span></span>
<span></span>
<span></span>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

def render_roadmap(roadmap):
    if not roadmap:
        return
    
    st.markdown("### Your PathFinder Roadmap")
    
    # 1. Generate Visual Flowchart
    flowchart_nodes = []
    for milestone in roadmap:
        skill = milestone["target_skill"]
        diff = milestone.get("difficulty", "Beginner")
        flowchart_nodes.append(f'<div class="flowchart-node">{skill}<br><span style="font-size:0.75rem; color:#888;">{diff}</span></div>')
    
    flowchart_html = f"""
<div class="flowchart-container">
    {'<div class="flowchart-arrow">→</div>'.join(flowchart_nodes)}
</div>
"""
    st.markdown("##### Visual Journey Chart")
    st.markdown(flowchart_html, unsafe_allow_html=True)
    
    st.markdown("##### Detailed Steps")
    # 2. Render Detailed Roadmap Cards
    for milestone in roadmap:
        step = milestone["step"]
        skill = milestone["target_skill"]
        resource = milestone["recommended_resource"]
        url = milestone["url"]
        duration = milestone["duration"]
        difficulty = milestone["difficulty"]
        reason = milestone["reason"]
        
        is_revision = "REVISION" in reason.upper()
        reason_class = "roadmap-reason revision" if is_revision else "roadmap-reason"
        
        # Parse Target Segment if exists
        formatted_reason = reason
        if "Target Segment:" in reason:
            parts = reason.split("Target Segment:")
            base_reason = parts[0].strip()
            segment = parts[1].strip()
            if segment:
                formatted_reason = f"""
{base_reason}<br>
<div class="roadmap-segment-tag">⏱️ Target Video Segment: {segment}</div>
"""
            else:
                formatted_reason = base_reason
            
        card_html = f"""
<div class="roadmap-card">
<div class="roadmap-step">Step {step:02d}</div>
<div class="roadmap-skill">{skill}</div>
<div class="roadmap-details">
<span>⏱️ {duration} hrs</span>
<span>📊 {difficulty}</span>
</div>
<div class="{reason_class}">
{formatted_reason}
</div>
<div class="roadmap-resource">
📚 <a href="{url}" target="_blank" class="roadmap-link">{resource}</a>
</div>
</div>
"""
        st.markdown(card_html, unsafe_allow_html=True)

    # 3. Render Written Explanation & Instructions
    st.markdown("##### Roadmap Summary")
    summary_html = """
<div style="background-color: #1a1a1f; padding: 16px; border-radius: 8px; border-left: 4px solid #4CAF50; margin-top: 20px; color: #ddd; font-size: 0.95rem; line-height: 1.6; border: 1px solid #333;">
<p style="margin-top:0;"><strong>What to do next:</strong> Follow the steps outlined in the visual chart above. Click on the recommended resource links to begin your learning. If a specific <em>Target Video Segment</em> is provided, focus primarily on that timeframe to master the main content quickly and efficiently.</p>
<p style="margin-bottom:0; color: #FF9800; font-weight: 600;">
(If you have finished a skill, such as Python or Statistics, please tell me! For example: "I have finished Python". I will then assess your readiness and update your roadmap automatically.)
</p>
</div>
"""
    st.markdown(summary_html, unsafe_allow_html=True)

def render_dashboard(profile, roadmap):
    if not profile or not profile.target_career:
        return
        
    # Calculate Metrics
    assessed_count = len(profile.skill_readiness)
    avg_readiness = sum(profile.skill_readiness.values()) / assessed_count if assessed_count > 0 else 0
    
    total_steps = len(roadmap) if roadmap else 0
    total_hours = sum([ms.get("duration", 0) for ms in roadmap]) if roadmap else 0
    
    current_focus = roadmap[0]["target_skill"] if roadmap else "Completed!"
    
    html = f"""
<div class="ai-core-container" style="margin-bottom: 10px;">
<div class="ai-core-dot"></div>
<div class="ai-core-text">AI PathFinder Engine Active</div>
</div>
<div class="metric-dashboard">
<div class="metric-card">
<div class="metric-title">Career Readiness</div>
<div class="metric-value">{avg_readiness:.0f}%</div>
<div class="metric-bar-bg">
<div class="metric-bar-fill" style="width: {avg_readiness}%;"></div>
</div>
</div>
<div class="metric-card">
<div class="metric-title">Scale Target</div>
<div class="metric-value">{assessed_count} Skills</div>
<div class="metric-title" style="margin-top: 8px;">Mastered</div>
</div>
<div class="metric-card">
<div class="metric-title">Current Focus</div>
<div class="metric-value" style="font-size: 1.4rem;">{current_focus}</div>
<div class="metric-bar-bg">
<div class="metric-bar-fill metric-focus" style="width: 100%;"></div>
</div>
</div>
<div class="metric-card">
<div class="metric-title">Statistics</div>
<div class="metric-value">{total_hours:.0f} hrs</div>
<div class="metric-title" style="margin-top: 8px;">Across {total_steps} Steps</div>
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

def render_readiness_result(skill, score):
    status = "Ready" if score >= 80 else "Needs Revision"
    color = "#4CAF50" if score >= 80 else "#FF9800"
    
    html = f"""
<div style="background-color: #1E1E24; border: 1px solid #333; border-radius: 8px; padding: 16px; margin: 10px 0;">
<h3 style="margin-top: 0; margin-bottom: 8px;">{skill} Readiness: {score}%</h3>
<div style="display: inline-block; padding: 4px 12px; border-radius: 16px; background-color: {color}22; color: {color}; font-weight: bold; border: 1px solid {color}55;">
Status: {status}
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

def render_progress_sidebar(profile, roadmap):
    st.sidebar.title("PathFinder AI")
    
    # Animated AI Status
    ai_status_html = """
<div class="ai-core-container">
<div class="ai-core-dot"></div>
<div class="ai-core-text">System Active & Monitoring</div>
</div>
"""
    st.sidebar.markdown(ai_status_html, unsafe_allow_html=True)
    
    target_career = profile.target_career if profile.target_career else "Not set"
    
    # Calculate readiness summary
    assessed_count = len(profile.skill_readiness)
    if assessed_count > 0:
        avg_readiness = f"{sum(profile.skill_readiness.values()) / assessed_count:.0f}%"
    else:
        avg_readiness = "Not assessed yet"
        
    current_focus = roadmap[0]["target_skill"] if roadmap and len(roadmap) > 0 else "Not determined yet"
    next_step = roadmap[1]["target_skill"] if roadmap and len(roadmap) > 1 else ("Goal Reached!" if roadmap else "Not determined yet")
    
    sidebar_html = f"""
<div class="sidebar-card">
<div class="sidebar-title">Target Career</div>
<div class="sidebar-value">{target_career}</div>
</div>
<div class="sidebar-card">
<div class="sidebar-title">Overall Readiness</div>
<div class="sidebar-value">{avg_readiness}</div>
</div>
<div class="sidebar-card" style="border-left: 3px solid #FF9800;">
<div class="sidebar-title">Current Focus</div>
<div class="sidebar-value highlight">{current_focus}</div>
</div>
<div class="sidebar-card">
<div class="sidebar-title">Next Step</div>
<div class="sidebar-value">{next_step}</div>
</div>
"""
    st.sidebar.markdown(sidebar_html, unsafe_allow_html=True)
