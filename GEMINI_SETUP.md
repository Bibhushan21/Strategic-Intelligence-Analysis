# Google Gemini API Setup

## Overview
The Strategic Intelligence App has been updated to use Google Gemini API instead of Mistral AI for better performance and reliability.

## Required Changes

### 1. Environment Variables
Add your Google API key to your `.env` file:

```bash
# Add this to your .env file
GOOGLE_API_KEY=your_google_api_key_here

# Old Mistral AI key can be commented out or removed
# MISTRAL_API_KEY=your_mistral_key
```

### 2. Get Google API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Add it to your `.env` file

### 3. Install Google Gemini API (Choose One Method)

#### Method A: Simple Gemini-Only Installation (RECOMMENDED)
```bash
python install_gemini_only.py
```

#### Method B: Full Dependency Resolution
```bash
python fix_dependencies.py
```

#### Method C: Manual Installation (if scripts fail)
```bash
# Uninstall conflicting Google packages only
pip uninstall google-generativeai langchain-google-genai -y

# Install compatible versions
pip install "google-generativeai>=0.8.0,<0.9.0"
pip install "langchain-google-genai>=1.0.0,<2.1.0"

# Test installation
python -c "import google.generativeai as genai; from langchain_google_genai import ChatGoogleGenerativeAI; print('✅ Success!')"
```

### 4. Dependencies Added (Compatible Versions)
- `langchain-google-genai==2.0.6` - LangChain integration for Google Gemini
- `google-generativeai==0.7.2` - Google Generative AI SDK (compatible version)
- Updated FastAPI to `0.115.9` and other packages for compatibility

### 5. Dependencies Commented Out
- `langchain-mistralai==0.2.11` - Mistral AI integration (commented out)
- `mistralai==0.4.2` - Mistral AI SDK (commented out)

## Features Enhanced

### Best Practices Agent
- Now includes **real reference links** and sources
- References are displayed in a separate "References & Sources" section
- References include clickable URLs when available
- References are included in PDF and Word exports

### Model Configuration
- **Model**: `gemini-1.5-pro-latest`
- **Temperature**: 0.7 (consistent with previous setup)
- **Max Output Tokens**: 8192
- **Timeout**: 120 seconds
- **Max Retries**: 5

## Verification
After setup, test the system by:
1. Starting the application: `python run.py`
2. Running a strategic analysis
3. Checking that the "References & Sources" section appears after the Implementation Roadmap
4. Verifying that Best Practices include real reference links

## Troubleshooting

### Dependency Conflicts (Most Common Issue)
If you see errors like:
```
langchain-google-genai 2.0.6 depends on google-generativeai<0.9.0 and >=0.8.0
open-webui 0.5.20 requires google-generativeai==0.7.2
```

**Quick Solutions:**

**Option 1 - Use Simple Installer (Recommended):**
```bash
python install_gemini_only.py
```

**Option 2 - Force Install Specific Versions:**
```bash
pip install google-generativeai==0.8.3 --force-reinstall
pip install langchain-google-genai==2.0.6 --force-reinstall
```

**Option 3 - Accept Conflicts with open-webui:**
- Your Strategic Intelligence App will work perfectly
- open-webui may show warnings but usually still functions
- This is the fastest solution for getting Gemini working

### Error: "GOOGLE_API_KEY not found"
- Ensure you've added the API key to your `.env` file
- Restart the application after adding the key

### Import Errors
- Run the dependency fix script: `python fix_dependencies.py`
- Ensure you're using Python 3.8+
- Check that all packages installed successfully

### API Rate Limits
- Google Gemini has generous free tier limits
- Monitor usage at [Google AI Studio](https://aistudio.google.com/)
- Consider upgrading if you hit limits

### FastAPI Version Issues
- The app now requires FastAPI 0.115.9+ for compatibility
- Old FastAPI versions (0.110.0) will cause conflicts
- Run the fix script to update to compatible versions

## Migration Notes
- The output structure remains the same - no changes to frontend needed
- All existing functionality is preserved
- Google Gemini typically provides faster and more reliable responses
- References will automatically appear in new analyses 