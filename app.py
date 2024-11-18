import streamlit as st
import boto3
import json
import os
from typing import Dict, List, Optional

# Initialize Bedrock client
def init_bedrock_client():
    try:
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'  # Update with your region
        )
        return bedrock_runtime
    except Exception as e:
        st.error(f"Error initializing Bedrock client: {e}")
        return None

# Invoke Claude model through Bedrock
def invoke_claude(
    prompt: str,
    client,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens: int = 4096,
    temperature: float = 0.7
) -> Optional[str]:
    try:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature
        })
        
        response = client.invoke_model(
            modelId=model_id,
            body=body
        )
        
        response_body = json.loads(response.get('body').read())
        return response_body.get('content')[0].get('text')
    
    except Exception as e:
        st.error(f"Error invoking Claude: {e}")
        return None

# Define the system prompt
SYSTEM_PROMPT = """You are a specialized music marketing AI assistant for African artists. Your role is to:
1. Help artists create customized marketing plans
2. Analyze target audiences and market trends
3. Provide actionable recommendations for:
   - Social media campaigns (TikTok, Instagram, YouTube)
   - Live events and performances
   - Streaming promotions (Boomplay, Audiomack, Spotify)
   - Storytelling and brand building
4. Track campaign performance and provide optimization insights

Focus on African music genres like Afrobeats and Amapiano, and consider local cultural contexts.
"""

# Streamlit UI
def main():
    st.title("African Music Marketing Assistant")
    st.sidebar.header("Configuration")
    
    # Initialize Bedrock client
    client = init_bedrock_client()
    
    if not client:
        st.error("Failed to initialize Bedrock client. Please check your AWS credentials.")
        return
    
    # Sidebar options
    temperature = st.sidebar.slider("Creativity Level", 0.0, 1.0, 0.7)
    max_tokens = st.sidebar.slider("Max Response Length", 1000, 4096, 2048)
    
    # Main interface
    st.markdown("### Artist Information")
    
    # Collect artist information
    artist_name = st.text_input("Artist Name")
    genre = st.selectbox("Primary Genre", 
                        ["Afrobeats", "Amapiano", "Highlife", "Bongo Flava", 
                         "Gqom", "Gengetone", "Other"])
    
    target_market = st.multiselect("Target Markets",
                                  ["Nigeria", "South Africa", "Kenya", "Ghana", 
                                   "Tanzania", "International"])
    
    marketing_goal = st.selectbox("Primary Marketing Goal",
                                ["Build Local Fanbase", 
                                 "International Expansion",
                                 "Increase Streaming Numbers",
                                 "Promote Upcoming Release",
                                 "Build Social Media Presence",
                                 "Event/Tour Promotion"])
    
    # Generate marketing plan button
    if st.button("Generate Marketing Plan"):
        if not artist_name:
            st.warning("Please enter an artist name")
            return
            
        prompt = f"""Based on the following artist information, create a detailed marketing plan:
        Artist: {artist_name}
        Genre: {genre}
        Target Markets: {', '.join(target_market)}
        Marketing Goal: {marketing_goal}
        
        Please provide:
        1. A comprehensive marketing strategy
        2. Specific platform recommendations (social media, streaming)
        3. Content ideas and storytelling approaches
        4. Timeline and key performance indicators
        5. Budget considerations and resource allocation
        """
        
        with st.spinner("Generating marketing plan..."):
            response = invoke_claude(prompt, client, temperature=temperature, 
                                  max_tokens=max_tokens)
            
            if response:
                st.markdown("### Your Marketing Plan")
                st.markdown(response)
                
                # Add download button for the marketing plan
                st.download_button(
                    label="Download Marketing Plan",
                    data=response,
                    file_name=f"{artist_name}_marketing_plan.txt",
                    mime="text/plain"
                )
    
    # Additional features
    st.markdown("### Additional Tools")
    tool_choice = st.selectbox("Select Tool",
                             ["Content Calendar Generator",
                              "Hashtag Recommendations",
                              "Platform-Specific Strategy",
                              "Performance Analytics"])
    
    if st.button("Generate Insights"):
        tool_prompt = f"""For {artist_name} ({genre}), provide specific insights for: {tool_choice}
        Consider the target markets: {', '.join(target_market)}
        Focus on practical, actionable recommendations."""
        
        with st.spinner("Generating insights..."):
            tool_response = invoke_claude(tool_prompt, client, temperature=temperature)
            if tool_response:
                st.markdown(f"### {tool_choice} Insights")
                st.markdown(tool_response)

if __name__ == "__main__":
    main()