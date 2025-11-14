"""
Meeting Minutes Generator - Uses local LLM to create formatted meeting minutes
"""
from local_llm_service import LocalLLMService
from datetime import datetime
from pathlib import Path
import json


class MeetingMinutesGenerator:
    """Generate structured meeting minutes from transcripts"""

    def __init__(self, llm_provider: str = "ollama", model_name: str = "llama3"):
        """
        Initialize minutes generator

        Args:
            llm_provider: "ollama", "llamacpp", or "azure"
            model_name: Model to use
        """
        self.llm_service = LocalLLMService(provider=llm_provider, model_name=model_name)

    def generate_minutes(self, transcript: str, meeting_title: str = "Meeting",
                        meeting_date: str = None) -> dict:
        """
        Generate meeting minutes from transcript

        Args:
            transcript: Full meeting transcript
            meeting_title: Title of the meeting
            meeting_date: Date of meeting (ISO format or datetime)

        Returns:
            Dictionary with summary, key_points, and action_items
        """
        if not meeting_date:
            meeting_date = datetime.now().isoformat()

        print("📝 Generating meeting minutes...")

        # Create prompt for LLM
        prompt = f"""You are an expert meeting assistant. Analyze the following meeting transcript and create structured meeting minutes.

Meeting Title: {meeting_title}
Date: {meeting_date}

Transcript:
{transcript}

Please provide:
1. **Summary**: A concise 2-3 sentence overview of the meeting
2. **Key Points & Decisions**: Bullet points of important topics discussed and decisions made
3. **Action Items**: Tasks identified with owner (if mentioned) in format "- [Task] (Owner: [Name])"

Format your response as:

SUMMARY:
[2-3 sentence summary]

KEY POINTS & DECISIONS:
- [Point 1]
- [Point 2]
- [...]

ACTION ITEMS:
- [Action 1] (Owner: [Name])
- [Action 2] (Owner: [Name])
- [...]

If no action items are identified, write "No action items identified."
"""

        # Generate with LLM
        response = self.llm_service.generate(prompt)

        # Parse response
        minutes = self._parse_minutes(response, meeting_title, meeting_date)

        print("✅ Minutes generated successfully!")
        return minutes

    def _parse_minutes(self, response: str, meeting_title: str, meeting_date: str) -> dict:
        """Parse LLM response into structured format"""

        minutes = {
            "meeting_title": meeting_title,
            "date": meeting_date,
            "summary": "",
            "key_points": [],
            "action_items": []
        }

        try:
            # Split response into sections
            lines = response.strip().split('\n')
            current_section = None

            for line in lines:
                line = line.strip()

                if not line:
                    continue

                # Detect sections
                if "SUMMARY:" in line.upper():
                    current_section = "summary"
                    continue
                elif "KEY POINTS" in line.upper():
                    current_section = "key_points"
                    continue
                elif "ACTION ITEMS" in line.upper():
                    current_section = "action_items"
                    continue

                # Add content to appropriate section
                if current_section == "summary":
                    minutes["summary"] += line + " "
                elif current_section == "key_points" and line.startswith('-'):
                    minutes["key_points"].append(line[1:].strip())
                elif current_section == "action_items" and line.startswith('-'):
                    minutes["action_items"].append(line[1:].strip())

            # Clean up summary
            minutes["summary"] = minutes["summary"].strip()

        except Exception as e:
            print(f"⚠️  Parsing error: {e}")
            # Fallback: use raw response as summary
            minutes["summary"] = response[:500]

        return minutes

    def save_minutes_to_file(self, minutes: dict, output_path: str = None) -> str:
        """
        Save minutes to markdown file

        Args:
            minutes: Minutes dictionary
            output_path: Optional custom path

        Returns:
            Path to saved file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./storage/minutes/meeting_minutes_{timestamp}.md"

        # Create directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Format as markdown
        markdown = self._format_as_markdown(minutes)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"💾 Minutes saved to: {output_path}")
        return output_path

    def save_minutes_to_json(self, minutes: dict, output_path: str = None) -> str:
        """Save minutes as JSON"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"./storage/minutes/meeting_minutes_{timestamp}.json"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(minutes, f, indent=2, ensure_ascii=False)

        print(f"💾 Minutes (JSON) saved to: {output_path}")
        return output_path

    def _format_as_markdown(self, minutes: dict) -> str:
        """Format minutes as markdown"""

        md = f"""# {minutes['meeting_title']}

**Date:** {minutes['date']}

---

## Summary

{minutes['summary']}

---

## Key Points & Decisions

"""

        if minutes['key_points']:
            for point in minutes['key_points']:
                md += f"- {point}\n"
        else:
            md += "_No key points identified._\n"

        md += "\n---\n\n## Action Items\n\n"

        if minutes['action_items']:
            for item in minutes['action_items']:
                md += f"- [ ] {item}\n"
        else:
            md += "_No action items identified._\n"

        md += f"\n---\n\n_Generated by Lumina on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n"

        return md


# Test function
if __name__ == "__main__":
    print("Testing Meeting Minutes Generator...")

    # Sample transcript
    test_transcript = """
    John: Hey team, thanks for joining. Today we need to discuss the Q4 roadmap.
    Sarah: Sure, I think we should prioritize the mobile app launch.
    John: Agreed. Let's target November 15th for the beta release.
    Mike: I can handle the backend API updates. Should be done by Nov 1st.
    Sarah: I'll coordinate with design team for the UI.
    John: Great. Let's also discuss the budget for marketing.
    Sarah: We need about $50k for the initial campaign.
    John: Approved. Mike, can you prepare a technical spec by next week?
    Mike: Yes, I'll have it ready by Friday.
    """

    # Generate minutes
    generator = MeetingMinutesGenerator(llm_provider="ollama", model_name="llama3")
    minutes = generator.generate_minutes(
        transcript=test_transcript,
        meeting_title="Q4 Planning Meeting",
        meeting_date="2025-11-14"
    )

    # Print results
    print("\n" + "="*60)
    print("GENERATED MINUTES:")
    print("="*60)
    print(generator._format_as_markdown(minutes))

    # Save to files
    md_path = generator.save_minutes_to_file(minutes)
    json_path = generator.save_minutes_to_json(minutes)

    print("\nTest complete!")
