#!/usr/bin/env bash
# Usage: ./scripts/encode_resume.sh resume.pdf
# Encodes your resume to base64 and copies it to clipboard.
# Paste the result into GitHub Settings -> Secrets -> RESUME_B64

FILE="$1"
if [ -z "$FILE" ]; then 
    echo "Usage: $0 <resume.pdf>"
    exit 1 
fi

if [ ! -f "$FILE" ]; then
    echo "Error: File '$FILE' not found."
    exit 1
fi

B64=$(base64 -w0 "$FILE" 2>/dev/null || base64 "$FILE")

if [ -z "$B64" ]; then
    echo "Error: Encoding failed."
    exit 1
fi

# Try to copy to clipboard
if command -v xclip >/dev/null 2>&1; then
    echo "$B64" | xclip -sel clip
    echo "Success! Base64 encoded string copied to clipboard (xclip)."
elif command -v pbcopy >/dev/null 2>&1; then
    echo "$B64" | pbcopy
    echo "Success! Base64 encoded string copied to clipboard (pbcopy)."
else
    echo "$B64" > resume_b64.txt
    echo "Success! Base64 encoded string saved to resume_b64.txt (clipboard utility not found)."
fi

echo "Done. Paste the base64 string into GitHub Secrets as RESUME_B64."
