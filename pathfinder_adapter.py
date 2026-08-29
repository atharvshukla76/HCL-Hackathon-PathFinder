import os
import contextlib
import io
from pathlib import Path
from dotenv import load_dotenv

from pathfinder_engine import (
    PathForgeKnowledgeBase,
    SkillGapEngine,
    SkillGraph,
    RecommendationEngine,
    OpenDomainLLMCallback,
    ConversationalAIAssistant,
    AdaptiveProgressEngine,
    resolve_career_requirements,
    LearnerProfile
)

# Load environment variables
load_dotenv()

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
JSON_DIR = PROJECT_ROOT / "PathFinder" / "data"

class PathFinderAdapter:
    def __init__(self):
        # We redirect stdout so the initializations don't print anything to streamlit UI
        with contextlib.redirect_stdout(io.StringIO()):
            self.api_key = os.getenv("GROQ_API_KEY")
            
            # Initialize core components
            self.kb = PathForgeKnowledgeBase(data_dir=str(DATA_DIR), json_dir=str(JSON_DIR))
            self.skill_graph = SkillGraph(self.kb.prerequisites)
            self.gap_engine = SkillGapEngine(self.kb)
            self.llm_assistant = ConversationalAIAssistant(api_key=self.api_key)
            self.recommender = RecommendationEngine(knowledge_base=self.kb, llm_assistant=self.llm_assistant)
            self.llm_callback = OpenDomainLLMCallback(knowledge_base=self.kb, api_key=self.api_key)
            
            # --- RESILIENT PRESENTATION PATCH ---
            # Try the original model first. If it fails (due to rate limits, permissions, or being offline),
            # gracefully fall back to a reliable model available on your custom endpoint so the presentation never crashes.
            def _patch_client(client_instance):
                if not client_instance: return
                original_create = client_instance.chat.completions.create
                def patched_create(*args, **kwargs):
                    kwargs["timeout"] = 120.0
                    try:
                        return original_create(*args, **kwargs)
                    except Exception as primary_error:
                        print(f"Primary model {kwargs.get('model')} failed: {primary_error}. Retrying with fallback.")
                        import time
                        time.sleep(2.0) # Small backoff to bypass instant rate-limits
                        kwargs["model"] = "qwen/qwen3.8-27b"
                        return original_create(*args, **kwargs)
                client_instance.chat.completions.create = patched_create

            if hasattr(self.llm_assistant, "client"): _patch_client(self.llm_assistant.client)
            if hasattr(self.llm_callback, "client"): _patch_client(self.llm_callback.client)

    def _clean_llm_output(self, text):
        """Removes unclosed <think> tags and intercepts notebook fallback strings."""
        if not isinstance(text, str):
            return text
            
        # STRICT PROMPT COMPLIANCE: Do not expose notebook fallback strings to the UI.
        # If the API timed out and the notebook returned its hardcoded fallbacks, throw an error
        # so the UI can display the clean "Something went wrong..." message.
        if "I've updated your roadmap! Check out the visualization panel." in text:
            raise ValueError("API Timeout in generate_reply")
        if text.startswith("Question for ") and "What is the primary function?" in text:
            raise ValueError("API Timeout in generate_assessment")
            
        import re
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        text = re.sub(r'<think>.*', '', text, flags=re.DOTALL)
        # Strip out ALL markdown code blocks (JSON, HTML, Python, etc) if they accidentally leak
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        return text.strip()
        
    def _clean_roadmap(self, roadmap):
        """Cleans up any leaked think tags in roadmap reasons."""
        for milestone in roadmap:
            if "reason" in milestone:
                milestone["reason"] = self._clean_llm_output(milestone["reason"])
        return roadmap

    def process_message(self, user_input, profile: LearnerProfile):
        """
        Main hook for Streamlit to pass user input.
        Returns (parsed_data, reply_text, new_roadmap, new_career_data)
        """
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                # Process user input
                parsed_data = self.llm_assistant.process_user_input(user_input, profile)
                
                # Check if we have enough info to generate/update roadmap
                new_roadmap = []
                career_data = None
                if profile.onboarding_complete and profile.target_career:
                    career_data = resolve_career_requirements(profile.target_career, self.gap_engine, self.llm_callback)
                    if career_data:
                        progress_engine = AdaptiveProgressEngine(profile, self.gap_engine, self.recommender, self.skill_graph)
                        new_roadmap = progress_engine.regenerate_roadmap(career_data)
                
                # Generate natural reply
                reply_text = self.llm_assistant.generate_reply(user_input, profile, new_roadmap)
                
                # Cleanup LLM output leaks
                reply_text = self._clean_llm_output(reply_text)
                new_roadmap = self._clean_roadmap(new_roadmap)
                
                return parsed_data, reply_text, new_roadmap, career_data
            except Exception as e:
                import traceback
                with open("debug_log.txt", "w") as f:
                    f.write(traceback.format_exc())
                # Catch exceptions and return a safe message
                return None, "Something went wrong while preparing your learning path. Please try again.", [], None

    def run_assessment(self, skill):
        """Generates an assessment for a skill."""
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                question = self.llm_assistant.generate_assessment(skill)
                return self._clean_llm_output(question)
            except Exception:
                return "Something went wrong generating the assessment. Please try again."

    def grade_answer(self, question, answer):
        """Grades an answer and returns the score (0-100)."""
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                return self.llm_assistant.grade_assessment(question, answer)
            except Exception:
                return 0

    def get_roadmap(self, career_data, profile: LearnerProfile):
        """Regenerates roadmap based on current profile and career data."""
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                if not career_data:
                    return []
                progress_engine = AdaptiveProgressEngine(profile, self.gap_engine, self.recommender, self.skill_graph)
                roadmap = progress_engine.regenerate_roadmap(career_data)
                return self._clean_roadmap(roadmap)
            except Exception:
                return []
                
    def record_assessment(self, profile: LearnerProfile, career_data, skill, score):
        """Records the assessment score and regenerates the roadmap."""
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                progress_engine = AdaptiveProgressEngine(profile, self.gap_engine, self.recommender, self.skill_graph)
                progress_engine.record_assessment_result(skill, score)
                if career_data:
                    roadmap = progress_engine.regenerate_roadmap(career_data)
                    return self._clean_roadmap(roadmap)
                return []
            except Exception:
                return []
