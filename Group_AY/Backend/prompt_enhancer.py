"""
Prompt Enhancer Module
Enhances user prompts to be more clear, structured, and detailed for better video generation
"""

import os
from openai import OpenAI
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


class PromptEnhancer:
    """
    Enhances educational video prompts using GPT-4 to add clarity,
    structure, and educational best practices
    """

    def __init__(self, openai_api_key: str = None):
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    def enhance_prompt(self, user_prompt: str) -> Dict[str, str]:
        """
        Enhance a user's educational video prompt to be more detailed and structured

        Args:
            user_prompt: The original user prompt

        Returns:
            Dictionary with:
            - original: Original user prompt
            - enhanced: Enhanced, detailed prompt
            - title: Suggested video title
        """
        enhancement_prompt = f"""You are an educational content expert. A user wants to create an educational video with this description:

"{user_prompt}"

Your task is to enhance this prompt to make it more clear, structured, and effective for video generation. Follow these guidelines:

1. **Clarify the concept**: If vague, specify exactly what should be taught
2. **Add structure**: Break down into clear steps or sections (intro, main concept, examples, conclusion)
3. **Specify visuals**: Describe what animations, diagrams, or visualizations should appear
4. **Educational best practices**:
   - Start with a hook or question
   - Use simple, clear language
   - Include concrete examples
   - Add a summary or key takeaway
5. **Timing**: Suggest appropriate pacing (60-90 seconds total)
6. **Learning objectives**: What should viewers understand by the end?

Return your response in this EXACT format:

TITLE: [A catchy, clear title for the video]

ENHANCED_PROMPT:
[The enhanced, detailed prompt with all improvements. Be specific about visuals, timing, and flow.]

LEARNING_OBJECTIVES:
- [Objective 1]
- [Objective 2]
- [Objective 3]
"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content creator who helps design clear, engaging educational videos.",
                },
                {"role": "user", "content": enhancement_prompt},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content.strip()

        # Parse the response
        title = ""
        enhanced = ""
        objectives = []

        try:
            # Extract title
            if "TITLE:" in content:
                title_section = content.split("TITLE:")[1].split("\n")[0].strip()
                title = title_section

            # Extract enhanced prompt
            if "ENHANCED_PROMPT:" in content:
                enhanced_section = content.split("ENHANCED_PROMPT:")[1]
                if "LEARNING_OBJECTIVES:" in enhanced_section:
                    enhanced = enhanced_section.split("LEARNING_OBJECTIVES:")[0].strip()
                else:
                    enhanced = enhanced_section.strip()

            # Extract learning objectives
            if "LEARNING_OBJECTIVES:" in content:
                objectives_section = content.split("LEARNING_OBJECTIVES:")[1].strip()
                objectives = [
                    line.strip("- ").strip()
                    for line in objectives_section.split("\n")
                    if line.strip().startswith("-")
                ]

        except Exception as e:
            print(f"Warning: Error parsing enhanced prompt: {e}")
            # Fallback: use the whole response as enhanced prompt
            enhanced = content
            title = "Educational Video"

        return {
            "original": user_prompt,
            "enhanced": enhanced or user_prompt,  # Fallback to original if parsing fails
            "title": title or "Educational Video",
            "learning_objectives": objectives,
        }

    def quick_enhance(self, user_prompt: str) -> str:
        """
        Quick enhancement - just returns the enhanced prompt text

        Args:
            user_prompt: The original user prompt

        Returns:
            Enhanced prompt string
        """
        result = self.enhance_prompt(user_prompt)
        return result["enhanced"]


def main():
    """
    Example usage
    """
    enhancer = PromptEnhancer()

    # Example 1: Vague prompt
    vague_prompt = "Explain gravity"

    print("=" * 60)
    print("ORIGINAL PROMPT:")
    print(vague_prompt)
    print("\n" + "=" * 60)

    enhanced = enhancer.enhance_prompt(vague_prompt)

    print("ENHANCED TITLE:")
    print(enhanced["title"])
    print("\n" + "=" * 60)

    print("ENHANCED PROMPT:")
    print(enhanced["enhanced"])
    print("\n" + "=" * 60)

    print("LEARNING OBJECTIVES:")
    for obj in enhanced["learning_objectives"]:
        print(f"  - {obj}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
