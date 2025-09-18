from graph import graph
from state import BlogStateInput
from datetime import datetime
import os

input_data = BlogStateInput(
    transcribed_notes_file="workflows.txt",
    urls=[])

print("🐉 Starting D&D Campaign Story Generator...")
print(f"📜 Reading campaign workflow from: notes/workflows.txt")
print(f"🎲 Creating epic adventure for 3 heroes...")

response = graph.invoke(input=input_data)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"results/dnd_campaign_{timestamp}.md"

os.makedirs("results", exist_ok=True)

with open(output_filename, "w") as f:
    f.write(response["final_blog"])

print(f"\n⚔️  D&D Campaign Story generated successfully!")
print(f"📖 Adventure saved to: {output_filename}")
print(f"🏰 Your epic tale awaits!")
