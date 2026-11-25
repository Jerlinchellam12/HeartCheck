
import sys

# Force UTF-8 console output on Windows — otherwise printing some
# characters the model generates (curly quotes, em-dashes) can crash
# this script with a UnicodeEncodeError, even though the app itself
# (served through a browser) is unaffected.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from utils.llm import generate_response

print("Testing HeartCheck AI connection...")

try:
    messages = [
        {
            "role": "user",
            "content": (
                "This is a fictional research test. "
                "Reply with: HeartCheck AI connection successful."
            )
        }
    ]

    result = generate_response(messages)

    print(f"\nSOURCE: {result['source']}")
    if result["source"] == "SIMULATED":
        print(f"REASON: {result['reason']}")

    print("\nAI RESPONSE:")
    print(result["text"])

    print("\nConnection test completed.")

except Exception as error:
    print("\nConnection test failed.")
    print("Error:", error)
