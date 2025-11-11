# worded_domain_lookup
Script for checking availability of domains from a provided dictionary

# Domain Availability Checker

A Python script that checks domain availability for dictionary words using the GoDaddy API. Quickly find available domains by filtering words based on length and checking multiple TLDs simultaneously.

## Features

- ✅ Batch domain availability checking via GoDaddy API
- 🔤 Filter words by exact length or length range
- 🌐 Support for multiple TLDs (e.g., .com, .io, .net)
- 📝 Custom word list support
- 💾 Export results to JSON
- ⚡ Rate-limited API calls to comply with GoDaddy limits
- 📊 Progress tracking and detailed logging

## Prerequisites

- Python 3.7 or higher
- GoDaddy API key and secret
- A word list file (default: `words.txt`)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/domain-checker.git
   cd domain-checker
   ```

2. **Install required packages**
   ```bash
   pip install requests python-dotenv
   ```

3. **Set up your GoDaddy API credentials**
   
   Create a `.env` file in the project root:
   ```bash
   touch .env
   ```
   
   Add your credentials to the `.env` file:
   ```
   GODADDY_API_KEY=your_api_key_here
   GODADDY_API_SECRET=your_api_secret_here
   ```

   > **How to get GoDaddy API credentials:**
   > 1. Go to [GoDaddy Developer Portal](https://developer.godaddy.com/)
   > 2. Sign in or create an account
   > 3. Navigate to "API Keys"
   > 4. Create a new API key (Production or OTE environment)
   > 5. Copy the key and secret to your `.env` file

## Usage

### Basic Command Structure

```bash
python domain_checker.py [OPTIONS]
```

### Required Arguments

You **must** specify either:
- `--length N` - Check words with exactly N letters
- `--min-length N` - Check words with at least N letters

### Optional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--max-length N` | Maximum word length (requires `--min-length`) | None |
| `--tlds` | Comma-separated list of TLDs | `.com` |
| `--dict` | Path to custom word list file | `words.txt` |

### Examples

**Check 3-letter .com domains:**
```bash
python domain_checker.py --length 3
```

**Check 4-letter domains for multiple TLDs:**
```bash
python domain_checker.py --length 4 --tlds .com,.io,.net
```

**Check domains with 3-5 letters:**
```bash
python domain_checker.py --min-length 3 --max-length 5
```

**Use a custom word list:**
```bash
python domain_checker.py --dict /path/to/mywords.txt --length 4
```

**Check 5-7 letter domains for .io and .dev:**
```bash
python domain_checker.py --min-length 5 --max-length 7 --tlds .io,.dev
```

## Using Your Own Word List

### Word List Format

The script expects a plain text file with one word per line:

```
apple
banana
cherry
domain
example
```

### Word List Requirements

- **One word per line**
- **Only alphabetic characters** - Words with numbers or special characters are filtered out
- **Case insensitive** - Words are automatically converted to lowercase
- **UTF-8 encoding** - Save your file in UTF-8 format

### Creating a Custom Word List

1. **Create a new text file:**
   ```bash
   nano mywords.txt
   ```

2. **Add your words (one per line):**
   ```
   tech
   app
   web
   cloud
   data
   ```

3. **Save the file** (in nano: `Ctrl+O`, then `Ctrl+X`)

4. **Run the script with your custom list:**
   ```bash
   python domain_checker.py --dict mywords.txt --length 4
   ```

### Where to Find Word Lists

- **Built-in system dictionaries:**
  - Linux/Mac: `/usr/share/dict/words`
  - Windows: Download from [GitHub word lists](https://github.com/dwyl/english-words)

- **Custom lists:**
  - Create your own based on keywords in your niche
  - Use industry-specific terminology
  - Combine common prefixes/suffixes with root words

### Example: Using System Dictionary (Linux/Mac)

```bash
python domain_checker.py --dict /usr/share/dict/words --length 5 --tlds .com
```

### Example: Filtering Words from Large Dictionary

If you have a large dictionary and want to pre-filter it:

```bash
# Extract 4-letter words only
grep -E '^[a-z]{4}$' /usr/share/dict/words > 4letter_words.txt

# Use the filtered list
python domain_checker.py --dict 4letter_words.txt --length 4
```

## Output

Results are saved to `available.json` in the following format:

```json
{
  ".com": [
    "example.com",
    "domain.com"
  ],
  ".io": [
    "tech.io",
    "app.io"
  ]
}
```

## Configuration

### Default Settings

You can modify these constants in the script:

```python
BATCH_SIZE = 70          # Number of domains per API call
DELAY_SECONDS = 4        # Delay between batches (rate limiting)
DEFAULT_TLD = ".com"     # Default TLD if none specified
OUTPUT_FILE = "available.json"  # Output file name
DEFAULT_DICTIONARY = "words.txt"  # Default word list path
```

### API Environment

The script uses GoDaddy's **OTE (Test) environment** by default:
```python
GODADDY_API_URL = "https://api.ote-godaddy.com/v1/domains/available"
```

For **production** use, change to:
```python
GODADDY_API_URL = "https://api.godaddy.com/v1/domains/available"
```

## Logging

The script provides detailed logging output:

- ✓ Available domains (green check)
- ✗ Taken domains (red X, debug level)
- Progress indicators
- API errors and warnings

To enable debug logging (show all checked domains):
```python
logging.basicConfig(level=logging.DEBUG)
```

## Rate Limiting

The script implements rate limiting to comply with GoDaddy API limits:
- Processes **70 domains per batch**
- **4-second delay** between batches
- Prevents API throttling errors

## Troubleshooting

### "Missing GoDaddy API credentials"
- Ensure `.env` file exists in the project root
- Verify `GODADDY_API_KEY` and `GODADDY_API_SECRET` are set correctly
- Check for typos in variable names

### "Dictionary file not found"
- Verify the file path is correct
- Use absolute paths for files outside the project directory
- Check file permissions

### "No words found matching the criteria"
- Verify your word list contains words matching the length criteria
- Check that words contain only alphabetic characters
- Ensure the file is not empty

### API Request Failed
- Check your internet connection
- Verify API credentials are valid
- Ensure you haven't exceeded rate limits
- Confirm the API endpoint is accessible

## Performance Tips

1. **Start with smaller batches** - Test with a small word list first
2. **Use exact length** - `--length 4` is faster than `--min-length 3 --max-length 5`
3. **Filter your word list** - Pre-filter words before running the script
4. **Check one TLD at a time** - More accurate for high-demand TLDs

## License

MIT License - Feel free to use and modify for your needs.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note:** This script uses GoDaddy's domain availability API. Make sure you comply with their [API Terms of Service](https://developer.godaddy.com/terms).
