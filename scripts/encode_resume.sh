#!/usr/bin/env bash
#
# Job Hunter - Resume Encoder
# Usage: ./scripts/encode_resume.sh resume.pdf
#
# Encodes your resume to base64 and copies it to clipboard
# Paste the result into GitHub Settings → Secrets → RESUME_B64
#

set -e

FILE="${1:-.}"

# Check if file provided
if [ -z "$FILE" ] || [ "$FILE" = "-h" ] || [ "$FILE" = "--help" ]; then
    echo "Usage: $0 <resume.pdf>"
    echo ""
    echo "Encodes your resume to base64 and copies it to clipboard."
    echo "Paste the result into GitHub Settings → Secrets → RESUME_B64"
    echo ""
    echo "Examples:"
    echo "  $0 resume.pdf"
    echo "  $0 ~/Desktop/my_resume.docx"
    exit 1
fi

# Check if file exists
if [ ! -f "$FILE" ]; then
    echo "❌ Error: File not found: $FILE"
    exit 1
fi

# Check file extension
if [[ ! "$FILE" =~ \.(pdf|docx|doc)$ ]]; then
    echo "⚠️  Warning: File extension is not .pdf, .docx, or .doc"
    echo "⚠️  Job Hunter expects PDF or DOCX files"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Encode to base64
echo "🔄 Encoding $FILE to base64..."

# Use base64 with appropriate flags for the platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    B64=$(base64 < "$FILE")
else
    # Linux / other Unix
    B64=$(base64 -w0 "$FILE" 2>/dev/null || base64 "$FILE")
fi

# Copy to clipboard
if command -v xclip &> /dev/null; then
    # Linux with xclip
    echo "$B64" | xclip -selection clipboard
    echo "✅ Copied to clipboard (xclip)"
elif command -v xsel &> /dev/null; then
    # Linux with xsel
    echo "$B64" | xsel --clipboard --input
    echo "✅ Copied to clipboard (xsel)"
elif command -v pbcopy &> /dev/null; then
    # macOS
    echo "$B64" | pbcopy
    echo "✅ Copied to clipboard (pbcopy)"
else
    # Fallback: save to file
    OUTPUT_FILE="resume_b64.txt"
    echo "$B64" > "$OUTPUT_FILE"
    echo "⚠️  Clipboard not available"
    echo "✅ Saved to $OUTPUT_FILE"
    echo ""
    echo "Next steps:"
    echo "1. Open the file: cat $OUTPUT_FILE"
    echo "2. Copy the contents"
fi

# Print summary
FILE_SIZE=$(du -h "$FILE" | cut -f1)
B64_SIZE=$(echo -n "$B64" | wc -c)
echo ""
echo "📊 Summary:"
echo "   File: $FILE"
echo "   Size: $FILE_SIZE (encoded: $B64_SIZE bytes)"
echo ""
echo "📋 Next steps:"
echo "1. Go to your GitHub repository"
echo "2. Settings → Secrets and variables → Actions"
echo "3. Click 'New repository secret'"
echo "4. Name: RESUME_B64"
echo "5. Paste the base64 string"
echo "6. Click 'Add secret'"
echo ""
echo "✨ Done! Your resume is encoded and ready to use in GitHub Actions."
