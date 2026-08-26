"""Check .env file contents and dotenv loading."""
import os
from dotenv import load_dotenv

# Show raw .env contents (key names + value status only)
print("=== .env file contents ===")
try:
    with open(".env", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                val = val.strip().strip('"').strip("'")
                status = "EMPTY" if not val else f"{len(val)} chars, starts: {val[:8]}..."
                print(f"  {key.strip()} = [{status}]")
            else:
                print(f"  (no = sign): {line}")
except FileNotFoundError:
    print("  .env file NOT FOUND")

print()
print("=== After load_dotenv() ===")
load_dotenv(override=True)
groq = os.environ.get("GROQ_API_KEY", "")
gemini = os.environ.get("GEMINI_API_KEY", "")
print(f"  GROQ_API_KEY   : {'SET (' + str(len(groq)) + ' chars)' if groq else 'NOT SET'}")
print(f"  GEMINI_API_KEY : {'SET (' + str(len(gemini)) + ' chars)' if gemini else 'NOT SET'}")
