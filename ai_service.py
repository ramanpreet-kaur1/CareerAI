import os
from typing import Dict
import json
from dotenv import load_dotenv

# FORCE reload environment variables every time
load_dotenv(override=True)

# Debug environment
print("\n" + "="*60)
print("🔧 AI SERVICE ENVIRONMENT CHECK")
print("="*60)
print(f"Current directory: {os.getcwd()}")
print(f"AI_PROVIDER env var: {os.getenv('AI_PROVIDER')}")
print(f"OPENAI_API_KEY present: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
print("="*60 + "\n")

# Get AI provider setting
AI_PROVIDER = os.getenv('AI_PROVIDER', 'fallback')
print(f"✅ Using AI Provider: {AI_PROVIDER}\n")

# Only import if needed
client = None

if AI_PROVIDER == 'openai':
    try:
        from openai import OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("⚠️  No OpenAI API key found, using fallback\n")
            AI_PROVIDER = 'fallback'
        else:
            # Simple initialization without extra parameters
            try:
                client = OpenAI(api_key=api_key)
                print("✅ OpenAI client initialized\n")
            except TypeError as e:
                # If there's a version mismatch, try old style
                print(f"⚠️  Version compatibility issue, trying alternative...\n")
                import openai
                openai.api_key = api_key
                client = openai
                print("✅ OpenAI client initialized (legacy mode)\n")
                
    except Exception as e:
        print(f"❌ OpenAI initialization error: {e}\n")
        AI_PROVIDER = 'fallback'


elif AI_PROVIDER == 'gemini':
    try:
        from google import genai
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            print("⚠️  No Gemini API key found, using fallback\n")
            AI_PROVIDER = 'fallback'
        else:
            client = genai.Client(api_key=api_key)
            print("✅ Gemini client initialized (NEW SDK)\n")
            
    except Exception as e:
        print(f"❌ Gemini initialization error: {e}\n")
        AI_PROVIDER = 'fallback'



def analyze_career_assessment(assessment_data: Dict) -> Dict:
    """Analyze assessment and generate recommendations"""
    
    print("\n" + "="*60)
    print(f"🤖 AI PROVIDER: {AI_PROVIDER}")
    print("="*60)
    
    # Use fallback if no API configured
    if AI_PROVIDER == 'fallback':
        print("⚠️  Using fallback response (demo mode)")
        return generate_fallback_response()
    
    # Build prompt
    print("📝 Building prompt from assessment data...")
    prompt = build_assessment_prompt(assessment_data)
    print(f"Prompt length: {len(prompt)} characters")
    
    # Get response based on provider
    if AI_PROVIDER == 'openai':
        print("🔵 Calling OpenAI...")
        response = get_openai_response(prompt)
    elif AI_PROVIDER == 'gemini':
        print("🟢 Calling Gemini...")
        response = get_gemini_response(prompt)
    else:
        print("⚠️  Unknown provider, using fallback")
        return generate_fallback_response()
    
    # Parse and return
    print("🔄 Parsing AI response...")
    result = parse_ai_response(response)
    print("✅ Analysis complete!")
    print("="*60 + "\n")
    
    return result




def build_assessment_prompt(data: Dict) -> str:
    """Build prompt for AI analysis"""
    
    interests = data.get('q1_interests', 'Not specified')
    environment = data.get('q2_environment', 'Not specified')
    tech = data.get('q3_technical_skill', '5')
    comm = data.get('q3_communication_skill', '5')
    creative = data.get('q3_creative_skill', '5')
    subjects = data.get('q4_academic_subjects', 'Not specified')
    aspirations = data.get('q14_career_aspirations', 'Not specified')
    
    prompt = "You are an expert career counselor. Analyze this assessment:\n\n"
    prompt += f"Interests: {interests}\n"
    prompt += f"Environment: {environment}\n"
    prompt += f"Technical Skill: {tech}/10\n"
    prompt += f"Communication: {comm}/10\n"
    prompt += f"Creative: {creative}/10\n"
    prompt += f"Subjects: {subjects}\n"
    prompt += f"Aspirations: {aspirations}\n\n"
    prompt += "Return JSON with: career_matches, top_strengths, skill_gaps, learning_roadmap, next_steps, personalized_advice\n"
    prompt += "Include 3 careers with title, match_percentage, description, why_good_fit, salary_range, growth_outlook, skills_needed"
    
    return prompt


def get_openai_response(prompt: str) -> str:
    """Get response from OpenAI"""
    try:
        print("="*60)
        print("📤 CALLING OPENAI API...")
        print("="*60)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a career counselor. Respond with JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        result = response.choices[0].message.content
        print("="*60)
        print("✅ GOT RESPONSE FROM OPENAI")
        print(f"Response length: {len(result)} characters")
        print(f"First 200 chars: {result[:200]}")
        print("="*60)
        
        return result
        
    except Exception as e:
        print("="*60)
        print(f"❌ OPENAI API ERROR: {e}")
        print("Falling back to sample response...")
        print("="*60)
        return json.dumps(generate_fallback_response())


def get_gemini_response(prompt: str) -> str:
    """Get response from Gemini using NEW SDK"""
    try:
        print("="*60)
        print("📤 CALLING GEMINI API (NEW SDK)...")
        print("="*60)
        
        # Use the new SDK method
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        result = response.text
        
        print("="*60)
        print("✅ GOT RESPONSE FROM GEMINI")
        print(f"Response length: {len(result)} characters")
        print(f"First 200 chars: {result[:200]}")
        print("="*60)
        
        return result
        
    except Exception as e:
        print("="*60)
        print(f"❌ GEMINI API ERROR: {e}")
        print("Falling back to sample response...")
        print("="*60)
        return json.dumps(generate_fallback_response())





def parse_ai_response(response: str) -> Dict:
    """Parse AI response and extract JSON"""
    try:
        text = response.strip()
        
        # Check for code blocks with backticks
        code_json = '`' + '`' + '`' + 'json'
        code_generic = '`' + '`' + '`'
        
        if code_json in text:
            # Find content between ```json and ```
            start_idx = text.find(code_json) + len(code_json)
            end_idx = text.find(code_generic, start_idx)
            if end_idx != -1:
                text = text[start_idx:end_idx].strip()
        elif code_generic in text:
            # Find content between first ``` and second ```
            parts = text.split(code_generic)
            if len(parts) >= 3:
                text = parts.strip()[1]
        
        # Parse JSON
        data = json.loads(text)
        
        # Validate required fields
        required = ['career_matches', 'top_strengths', 'skill_gaps', 'learning_roadmap', 'next_steps']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing field: {field}")
        
        return data
        
    except Exception as e:
        print(f"Parse Error: {e}")
        print(f"Response: {response[:300]}")
        return generate_fallback_response()


def generate_fallback_response() -> Dict:
    """Fallback response if AI fails"""
    return {
        "career_matches": [
            {
                "title": "Technology Specialist",
                "match_percentage": 85,
                "description": "Work with modern technologies to solve business problems and create innovative solutions.",
                "why_good_fit": "Your skills and interests align well with technology roles that offer growth and variety.",
                "salary_range": "$60,000 - $120,000",
                "growth_outlook": "High - Technology sector continues to expand with strong job growth",
                "skills_needed": ["Technical Skills", "Problem Solving", "Continuous Learning"]
            },
            {
                "title": "Business Analyst",
                "match_percentage": 78,
                "description": "Bridge the gap between business needs and technical solutions through data analysis and communication.",
                "why_good_fit": "Your analytical thinking and communication skills make you well-suited for this collaborative role.",
                "salary_range": "$55,000 - $95,000",
                "growth_outlook": "Medium-High - Consistent demand across all industries",
                "skills_needed": ["Data Analysis", "Communication", "Business Knowledge"]
            },
            {
                "title": "Project Coordinator",
                "match_percentage": 72,
                "description": "Organize and manage projects, ensuring smooth team collaboration and timely delivery of goals.",
                "why_good_fit": "Your organizational abilities and attention to detail are valuable assets in project management.",
                "salary_range": "$45,000 - $75,000",
                "growth_outlook": "Medium - Steady opportunities across various sectors",
                "skills_needed": ["Organization", "Communication", "Time Management"]
            }
        ],
        "top_strengths": [
            "Strong problem-solving abilities that can be applied across various professional roles",
            "Good balance of technical and interpersonal skills that enable effective collaboration",
            "Demonstrated willingness to learn and adapt to new challenges and environments"
        ],
        "skill_gaps": [
            {
                "skill": "Industry-Specific Knowledge",
                "priority": "High",
                "how_to_develop": "Complete online courses in your target field, attend industry workshops, and gain hands-on experience through projects or internships"
            },
            {
                "skill": "Advanced Technical Skills",
                "priority": "Medium",
                "how_to_develop": "Practice with real-world projects, contribute to open source initiatives, and earn relevant professional certifications"
            }
        ],
        "learning_roadmap": [
            {
                "phase": "Foundation Phase (0-3 months)",
                "focus": "Build core foundational skills and knowledge",
                "actions": [
                    "Complete 2-3 introductory courses in your field of interest",
                    "Start building a portfolio with small personal projects",
                    "Join online communities and professional forums"
                ],
                "resources": ["Coursera", "edX", "LinkedIn Learning", "YouTube"]
            },
            {
                "phase": "Development Phase (3-9 months)",
                "focus": "Gain practical experience and deepen your expertise",
                "actions": [
                    "Work on increasingly complex projects",
                    "Seek mentorship or networking opportunities in your field",
                    "Consider freelance work or part-time internships"
                ],
                "resources": ["Udemy", "Professional certifications", "GitHub", "Industry meetups"]
            },
            {
                "phase": "Transition Phase (9-18 months)",
                "focus": "Position yourself for your career transition",
                "actions": [
                    "Build a strong professional network in your target industry",
                    "Update your resume, portfolio, and LinkedIn profile",
                    "Begin actively applying for positions in your target field"
                ],
                "resources": ["LinkedIn", "Industry conferences", "Career coaches", "Job boards"]
            }
        ],
        "next_steps": [
            "Research the recommended careers in depth to understand the daily responsibilities and requirements",
            "Identify 2-3 online courses or certifications to start building relevant skills this month",
            "Connect with professionals currently working in your target field for informational interviews"
        ],
        "personalized_advice": "Based on your assessment results, you have a solid foundation for transitioning into several rewarding career paths. Your unique combination of skills and interests positions you well for roles that require both technical capability and strong interpersonal skills. Focus on building deep expertise in your chosen direction while maintaining flexibility to explore related opportunities. Remember that career transitions take time and persistence, so be patient with yourself and celebrate the small wins along the way. Your demonstrated willingness to learn and adapt will be your greatest asset throughout this journey. Consider starting with smaller steps - perhaps a side project or volunteer work in your target field - to gain experience while reducing risk. Most importantly, stay committed to continuous learning and don't be afraid to seek guidance from mentors who have walked this path before you."
    }


if __name__ == "__main__":
    test_data = {
        'q1_interests': 'investigative,artistic',
        'q3_technical_skill': '7',
        'q3_communication_skill': '8',
        'q14_career_aspirations': 'UX designer at tech company'
    }
    
    result = analyze_career_assessment(test_data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING AI SERVICE")
    print("="*60)
    
    test_data = {
        'q1_interests': 'investigative,artistic',
        'q3_technical_skill': '8',
        'q3_communication_skill': '7',
        'q14_career_aspirations': 'I want to become a data scientist at a tech company'
    }
    
    print("Test data:", test_data)
    print("\nCalling analyze_career_assessment...")
    
    result = analyze_career_assessment(test_data)
    
    print("\n" + "="*60)
    print("📊 RESULT:")
    print("="*60)
    print(f"Career matches: {len(result.get('career_matches', []))}")
    if result.get('career_matches'):
        print(f"First career: {result['career_matches'][0]['title']}")
    print("="*60)
