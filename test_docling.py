from pathlib import Path

from app.ingestion.parser import parse_pdf


input_file = "/home/hp/Desktop/paperpilot/data/uploads/WorkHub - Training Project.pdf"
output_file = Path("data/processed/paper.md")

document = parse_pdf(input_file)

markdown = document.export_to_markdown()

output_file.write_text(markdown, encoding="utf-8")

print(f"PDF parsed successfully.")
print(f"Output saved to: {output_file}")