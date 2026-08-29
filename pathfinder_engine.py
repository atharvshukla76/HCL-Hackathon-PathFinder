import json
import pandas as pd
import networkx as nx
import re
import os
import threading
from groq import Groq
import warnings
warnings.filterwarnings('ignore')

class PathForgeKnowledgeBase:
    def __init__(self, data_dir="../data", json_dir="../PathFinder/data"):
        self.data_dir = data_dir
        self.json_dir = json_dir
        self.load_data()
    def load_data(self):
        try:
            self.occupation_skills = pd.read_parquet(f"{self.data_dir}/processed/occupation_skills.parquet")
            self.occupations = pd.read_parquet(f"{self.data_dir}/processed/occupations.parquet")
            self.alt_titles = pd.read_parquet(f"{self.data_dir}/processed/alternate_titles.parquet")
            self.tech_skills = pd.read_parquet(f"{self.data_dir}/processed/technology_skills.parquet")
        except (FileNotFoundError, Exception) as e:
            print(f"[Init] ⚠️ Parquet datasets not found in {self.data_dir}. Running purely on curated JSON/LLM fallbacks.")
            self.occupation_skills = pd.DataFrame()
            self.occupations = pd.DataFrame()
            self.alt_titles = pd.DataFrame()
            self.tech_skills = pd.DataFrame()
        
        with open(f"{self.json_dir}/careers.json", 'r') as f:
            self.seed_careers = json.load(f)
        with open(f"{self.json_dir}/prerequisites.json", 'r') as f:
            self.prerequisites = json.load(f)
        with open(f"{self.json_dir}/dynamic_careers.json", 'r') as f:
            self.dynamic_careers = json.load(f)
            
        self.resources = pd.read_csv(f"{self.json_dir}/resources.csv")

class SkillNormalizer:
    ALIASES = {
        "programming": "Python",
        "python programming": "Python",
        "statistical analysis": "Statistics",
        "data analysis": "Data Analysis",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning"
    }
    @classmethod
    def canonicalize(cls, skill):
        key = skill.strip().lower()
        return cls.ALIASES.get(key, skill.strip().title())
        
    @classmethod
    def get_search_aliases(cls, skill):
        canonical = cls.canonicalize(skill)
        aliases = [canonical]
        for k, v in cls.ALIASES.items():
            if v == canonical: aliases.append(k.title())
        return list(set(aliases))

class SkillGraph:
    def __init__(self, prerequisites_dict):
        self.graph = nx.DiGraph()
        self.build_graph(prerequisites_dict)
        
    def build_graph(self, prerequisites_dict):
        temp_graph = self.graph.copy()
        for target_skill, prereqs in prerequisites_dict.items():
            target_norm = SkillNormalizer.canonicalize(target_skill)
            temp_graph.add_node(target_norm)
            for prereq in prereqs:
                prereq_norm = SkillNormalizer.canonicalize(prereq)
                temp_graph.add_edge(prereq_norm, target_norm)
                
        if nx.is_directed_acyclic_graph(temp_graph):
            self.graph = temp_graph
        else:
            print("⚠️ [SkillGraph] Detected a logical cycle in LLM prerequisites! Ignoring invalid dependencies.")
                
    def get_learning_order(self, skills_needed):
        relevant_nodes = set()
        missing_from_graph = []
        for skill in skills_needed:
            if skill in self.graph:
                relevant_nodes.add(skill)
                relevant_nodes.update(nx.ancestors(self.graph, skill))
            else:
                missing_from_graph.append(skill)
        subgraph = self.graph.subgraph(relevant_nodes)
        try:
            ordered = list(nx.topological_sort(subgraph))
            return ordered + missing_from_graph 
        except nx.NetworkXUnfeasible:
            return skills_needed

class LearnerProfile:
    def __init__(self, target_career=None, experience_level="Beginner", current_skills=None, interests=None, weekly_hours=10):
        self.target_career = target_career
        self.experience_level = experience_level
        self.current_skills = current_skills or {}
        self.interests = interests or []
        self.weekly_hours = weekly_hours
        
        self.skills_assessed = False
        self.onboarding_complete = False
        
        self.skill_readiness = {} 
        self.assessment_history = {} 
        self.active_assessment = None 

class SkillGapEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base

    def get_career_profile(self, career_name):
        print(f"\n[Career Knowledge] Resolving: {career_name}")
        career_name_lower = career_name.lower().strip()
        matched_career = None

        
        for key in self.kb.seed_careers:
            if key.lower() == career_name_lower:
                matched_career = key
                break

        
        if not matched_career:
            for key, data in self.kb.seed_careers.items():
                aliases = data.get("aliases", [])
                if any(a.lower() == career_name_lower for a in aliases):
                    matched_career = key
                    print(f"[Career Knowledge] Matched via alias → '{matched_career}'")
                    break

        
        if not matched_career:
            for key in self.kb.seed_careers:
                if career_name_lower in key.lower() or key.lower() in career_name_lower:
                    matched_career = key
                    print(f"[Career Knowledge] Matched via partial → '{matched_career}'")
                    break

        if not matched_career:
            print(f"[Career Knowledge] ❌ No profile found for '{career_name}'.")
            return {}

        career_data = self.kb.seed_careers[matched_career]

        
        direct_skills = {
            k: v for k, v in career_data.items()
            if isinstance(v, (int, float)) and k not in ("onet_codes", "aliases")
        }
        if direct_skills:
            print(f"[Career Knowledge] ✅ Layer 1: Found {len(direct_skills)} skills from careers.json!")
            return direct_skills

        
        onet_codes = career_data.get("onet_codes", [])
        if onet_codes:
            print(f"[Career Knowledge] Layer 1 empty. Trying O*NET dataset with codes: {onet_codes}")
            for code in onet_codes:
                try:
                    row = self.kb.occupation_skills[
                        self.kb.occupation_skills["O*NET-SOC Code"].astype(str).str.strip() == str(code).strip()
                    ]
                    if not row.empty:
                        skills = {}
                        for column in row.columns:
                            if column == "O*NET-SOC Code":
                                continue
                            try:
                                value = float(row.iloc[0][column])
                                if value > 0.4:
                                    skills[column] = round(value, 3)
                            except:
                                continue
                        if skills:
                            print(f"[O*NET] ✅ Layer 2: Found {len(skills)} skills for code {code}!")
                            return skills
                except Exception as e:
                    print(f"[O*NET] ❌ Error querying parquet: {e}")

        print(f"[Career Knowledge] ❌ All local layers failed for '{career_name}'. LLM fallback needed.")
        return {}

    def calculate_gaps(self, career_skills, user_profile):
        gaps = {}
        for skill, required_weight in career_skills.items():
            norm_skill = SkillNormalizer.canonicalize(skill)
            current_proficiency = user_profile.current_skills.get(norm_skill, 0.0)
            gap = required_weight - current_proficiency
            readiness = user_profile.skill_readiness.get(norm_skill, 100)

            if gap > 0:
                gaps[norm_skill] = gap
            elif readiness < 80:
                gaps[norm_skill] = 1.0 - (readiness / 100.0)

        return dict(sorted(gaps.items(), key=lambda item: item[1], reverse=True))
    
def resolve_learning_path(skill_gaps, skill_graph):
    target_skills = list(skill_gaps.keys())
    return skill_graph.get_learning_order(target_skills)

class RecommendationEngine:
    def __init__(self, knowledge_base, llm_assistant):
        self.kb = knowledge_base
        self.llm_assistant = llm_assistant
    def get_resource_candidates(self, skill):
        aliases = SkillNormalizer.get_search_aliases(skill)
        return self.kb.resources[self.kb.resources["skill"].isin(aliases)]
        
    def generate_milestones(self, learning_path, user_profile):
        roadmap = []
        for i, skill in enumerate(learning_path):
            candidates = self.get_resource_candidates(skill)
            
            if not candidates.empty:
                candidates = candidates.copy()
                
                
                def calculate_quality(row):
                    base_quality = float(row.get('quality_score', 0.85)) 
                    diff_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
                    user_diff = diff_map.get(user_profile.experience_level, 1)
                    res_diff = diff_map.get(row.get('difficulty', 'Beginner'), 1)
                    return base_quality - (abs(user_diff - res_diff) * 0.15)
                    
                candidates['calculated_quality'] = candidates.apply(calculate_quality, axis=1)
                candidates = candidates.sort_values(by='calculated_quality', ascending=False)
                best_resource = candidates.iloc[0]
                
                try: duration = float(best_resource.get('duration_hours', 5.0))
                except: duration = 5.0
                    
                reason = "Your next prerequisite."
                readiness = user_profile.skill_readiness.get(skill, 100)
                
                if readiness < 100 and skill in user_profile.current_skills:
                    reason = f"⚠️ REVISION REQUIRED (Readiness: {readiness}%). You must learn the missing portions of this skill to achieve full 5/5 mastery."
                elif duration > 3.0:
                    
                    mock_chapter = self.llm_assistant.extract_video_chapters(best_resource['title'], skill, duration)
                    reason = f"CRASH COURSE. Target Segment: {mock_chapter}"


                
                milestone = {
                    "step": i + 1,
                    "target_skill": skill,
                    "recommended_resource": best_resource['title'],
                    "url": best_resource['url'],
                    "duration": duration, 
                    "difficulty": best_resource.get('difficulty', 'Beginner'),
                    "reason": reason
                }
                roadmap.append(milestone)
            else:
                clean_search = skill.replace(' ', '+')
                roadmap.append({
                    "step": i + 1,
                    "target_skill": skill,
                    "recommended_resource": f"Custom Search: '{skill} tutorial'",
                    "url": f"https://www.youtube.com/results?search_query={clean_search}+crash+course",
                    "duration": 5.0,
                    "difficulty": user_profile.experience_level,
                    "reason": f"Specialized open-domain skill."
                })
        return roadmap

class OpenDomainLLMCallback:
    def __init__(self, knowledge_base, api_key):
        self.kb = knowledge_base
        try: self.client = Groq(api_key=api_key)
        except: self.client = None
            
    def fetch_career_skills(self, career_name):
        print(f"\n[Open Domain LLM] Generating requirements & prerequisites for: {career_name}")
        if career_name in self.kb.dynamic_careers:
            return self.kb.dynamic_careers[career_name]
        if self.client is None: return {}
        prompt = f"""
        TARGET CAREER: {career_name}
        Identify 5-8 critical skills and the PREREQUISITE order between them.
        Return ONLY valid JSON in this exact structure:
        {{
            "skills": {{"Physics": 0.9, "Mathematics": 0.95}},
            "prerequisites": {{"Physics": ["Mathematics"]}}
        }}
        """
        try:
            response = self.client.chat.completions.create(model="qwen/qwen3.6-27b", messages=[{"role": "user", "content": prompt}], temperature=0.1)
            raw_text = re.sub(r"<think>.*?</think>", "", response.choices[0].message.content or "", flags=re.DOTALL).strip()
            match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
            if not match: return {}
            llm_response = json.loads(match.group(0))
            if not llm_response.get("skills"): return {}
            self.kb.dynamic_careers[career_name] = llm_response
            return llm_response
        except Exception: return {}

def resolve_career_requirements(career_name, engine, llm_callback):
    reqs = engine.get_career_profile(career_name)
    if reqs:
        print("[Career Resolver] ✅ Requirements obtained from knowledge base.")
        return {"skills": reqs, "prerequisites": {}}
    reqs = llm_callback.fetch_career_skills(career_name)
    if reqs and "skills" in reqs:
        print("[Career Resolver] ✅ Requirements and dynamic prerequisites obtained from LLM.")
        return reqs
    print(f"[Career Resolver] ❌ Unable to resolve requirements for {career_name}")
    return None

class ConversationalAIAssistant:
    _cache_lock = threading.Lock()

    def __init__(self, api_key):
        try:
            self.client = Groq(api_key=api_key)
        except:
            self.client = None
            
    def process_user_input(self, user_input, current_profile):
        if self.client is None: return False
        try:
            prompt = f"""
            Extract user intent into JSON.
            USER MESSAGE: "{user_input}"
            
            STRUCTURE:
            {{
                "target_career": null,
                "known_skills": {{"SkillName": 0.8}}, // MUST BE FLOATS BETWEEN 0.0 AND 1.0!
                "completed_skill": null,
                "skills_assessed": false
            }}
            
            RULES:
            1. If they say "I have no skills", "start from basics", or "zero experience", set "skills_assessed" to true and "known_skills" to {{}}.
            2. If they explicitly state they JUST FINISHED a course or skill right now, set "completed_skill" to that skill name.
            3. OUTPUT ONLY RAW JSON. Do NOT output any conversational text, self-corrections, or markdown outside of the JSON object.
            """
            response = self.client.chat.completions.create(model="qwen/qwen3.6-27b", messages=[{"role": "user", "content": prompt}], temperature=0.1, timeout=15.0)
            raw_text = re.sub(r'<think>.*?</think>', '', response.choices[0].message.content, flags=re.DOTALL).strip()
            
            
            json_match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if not match: 
                    print(f"\n⚠️ [Debug] Could not find JSON format. AI responded with:\n{raw_text}")
                    return None
                json_str = match.group(0).strip()
            
            try:
                data = json.loads(json_str)
            except Exception as json_error:
                
                try:
                    idx = json_str.rfind('}') 
                    while idx > 0:
                        try:
                            data = json.loads(json_str[:idx+1])
                            break
                        except:
                            idx = json_str.rfind('}', 0, idx)
                    else:
                        raise json_error
                except Exception as e:
                    print(f"\n⚠️ [Debug] JSON Parsing failed: {e}\nInvalid JSON string was:\n{json_str}")
                    return None

            if data.get("target_career"): current_profile.target_career = data["target_career"]
            
            known_skills = data.get("known_skills", {})
            if isinstance(known_skills, dict):
                for skill, proficiency in known_skills.items():
                    norm = SkillNormalizer.canonicalize(skill)
                    try:
                        current_profile.current_skills[norm] = float(proficiency)
                    except ValueError:
                        current_profile.current_skills[norm] = 0.5 
            
            if data.get("skills_assessed") is True or len(known_skills) > 0:
                current_profile.skills_assessed = True
                
            has_career = (current_profile.target_career is not None and str(current_profile.target_career).strip() != "")
            current_profile.onboarding_complete = (has_career and current_profile.skills_assessed)
            
            return data
            
        except Exception as e: 
            print(f"\n⚠️ [Debug] Fatal API Error: {e}")
            return None

    def extract_video_chapters(self, video_title, skill, duration):
        cache_file = "video_chapters_cache.json"
        cache = {}
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f: cache = json.load(f)
            except: pass
                
        cache_key = f"{video_title}_{skill}"
        if cache_key in cache: return cache[cache_key]

        if self.client is None: return "Check the video description for chapters."
        try:
            prompt = f"The user is watching a {duration}-hour crash course titled '{video_title}'. They only need to learn '{skill}'. Generate a highly realistic, brief timeline showing the start and end time (e.g. 01:15:00 - 02:30:00) where this topic is most likely covered. Return ONLY the timestamp string."
            response = self.client.chat.completions.create(model="qwen/qwen3.6-27b", messages=[{"role": "user", "content": prompt}], temperature=0.5, timeout=5.0)
            result = re.sub(r'<think>.*?</think>', '', response.choices[0].message.content, flags=re.DOTALL).strip()
            
            with self._cache_lock:
                cache[cache_key] = result
                with open(cache_file, 'w') as f: json.dump(cache, f, indent=4)
            return result
        except: return "Check video timeline."
            
    def generate_assessment(self, skill):
        try:
            prompt = f"Generate 5 distinct, moderately difficult assessment questions to thoroughly test conceptual knowledge of '{skill}'. Include a mix of multiple-choice (with options A, B, C, D) and open-ended short-answer questions. Return ONLY a valid JSON array of 5 strings. Each string must contain the question text (and options only if it is multiple-choice). Example: [\"Q1 text... A) B) C) D)\", \"Q2 short-answer text...\"]"
            response = self.client.chat.completions.create(model="qwen/qwen3.6-27b", messages=[{"role": "user", "content": prompt}], temperature=0.5, timeout=15.0)
            raw_text = re.sub(r'<think>.*?</think>', '', response.choices[0].message.content, flags=re.DOTALL).strip()
            
            # Extract JSON array
            json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
            if json_match:
                return json_match.group(0).strip()
            return raw_text
        except: return f"[\"Question 1 for {skill}: What is the primary function? A, B, C, D.\", \"Question 2...\", \"Question 3...\", \"Question 4...\", \"Question 5...\"]"
        
    def grade_assessment(self, question, user_answer):
        try:
            prompt = f"Question: {question}\nUser Answer: {user_answer}\nGrade this answer. Return ONLY a JSON object: {{\"score\": 100}} if correct, {{\"score\": 0}} if totally wrong, or in between for partial credit."
            response = self.client.chat.completions.create(model="qwen/qwen3.6-27b", messages=[{"role": "user", "content": prompt}], temperature=0.1, timeout=10.0)
            raw_text = re.sub(r'<think>.*?</think>', '', response.choices[0].message.content, flags=re.DOTALL)
            return json.loads(re.search(r'\{.*\}', raw_text, re.DOTALL).group(0)).get("score", 0)
        except: return 0
            
    def generate_reply(self, user_input, current_profile, new_roadmap):
        try:
            roadmap_summary = [m['target_skill'] for m in new_roadmap] if new_roadmap else "No roadmap yet."
            prompt = f"""You are an AI Career Mentor. The user just said: "{user_input}"
            RULES: If Target Career is None, ask what they want to become. If Skills Assessed is False, ask what they currently know. If Onboarding Complete is True, enthusiastically explain how their existing knowledge shaped this roadmap: {roadmap_summary}."""
            response = self.client.chat.completions.create(model="qwen/qwen3.6-27b", messages=[{"role": "user", "content": prompt}], temperature=0.7, timeout=10.0)
            return re.sub(r'<think>.*?</think>', '', response.choices[0].message.content, flags=re.DOTALL).strip()
        except: return "I've updated your roadmap! Check out the visualization panel."

class AdaptiveProgressEngine:
    def __init__(self, user_profile, gap_engine, recommender, skill_graph):
        self.user_profile = user_profile
        self.gap_engine = gap_engine
        self.recommender = recommender
        self.skill_graph = skill_graph
        
    def record_assessment_result(self, skill, score=100):
        norm = SkillNormalizer.canonicalize(skill)
        
        
        if norm not in self.user_profile.assessment_history:
            self.user_profile.assessment_history[norm] = []
        self.user_profile.assessment_history[norm].append(score)
        
        # Update readiness
        self.user_profile.skill_readiness[norm] = score
        
        # Mark as strictly mastered only if 100%
        if score == 100:
            current_prof = self.user_profile.current_skills.get(norm, 0.0)
            self.user_profile.current_skills[norm] = min(1.0, current_prof + 0.2)
        
    def regenerate_roadmap(self, career_data):
        career_skills = career_data.get("skills", {})
        dynamic_prereqs = career_data.get("prerequisites", {})
        if dynamic_prereqs: self.skill_graph.build_graph(dynamic_prereqs)
        new_gaps = self.gap_engine.calculate_gaps(career_skills, self.user_profile)
        new_learning_path = resolve_learning_path(new_gaps, self.skill_graph)
        return self.recommender.generate_milestones(new_learning_path, self.user_profile)
