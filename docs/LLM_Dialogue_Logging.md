# LLM Dialogue Logging

This feature allows you to log and analyze all dialogue between your application and the LLM (Ollama) for debugging and analysis purposes.

## Features

1. **Complete Dialogue Logging**: Record all prompts sent to the LLM and all responses received.
2. **JSON and HTML Output**: Logs are saved in both JSON format (for programmatic analysis) and HTML format (for human reading).
3. **Metadata Tracking**: Additional information like model name, temperature settings, and timestamps are recorded.
4. **Visual Display**: HTML output gives a clean, easy-to-read view of the conversations.

## Usage

### Using the Logging Versions of Test Scripts

1. Run the feedback loop test with logging:
   ```
   python test_feedback_loop_with_logging.py
   ```

2. Process feedback with logging:
   ```
   python process_feedback_with_logging.py --job-id JOB_ID --feedback "Your feedback text here"
   ```

### Viewing the Logs

1. **JSON Logs**: Located in the `logs/llm_dialogue/` directory with filenames like `llm_dialogue_YYYYMMDD_HHMMSS.json`.
2. **HTML Logs**: Located in the same directory with `.html` extension. Open these in any web browser for a formatted view.

### Integration with Ollama WebUI

The JSON log files are compatible with Ollama WebUI for analysis. You can:

1. Open the `.json` files to inspect the raw prompts and responses
2. Import conversations into the WebUI for analysis (if supported by your WebUI version)

## Implementation Details

The logging functionality is implemented in `run_pipeline/utils/logging_llm_client.py`, which extends the standard LLM client with logging capabilities.

- `LoggingOllamaClient`: Records dialogue while maintaining all original functionality
- `call_logging_ollama_api`: Drop-in replacement for the standard `call_ollama_api` function
- `DialogueLogger`: Generic class for logging and displaying dialogues

## Troubleshooting

If you don't see any logs being generated:

1. Check that the `logs/llm_dialogue/` directory exists and is writable
2. Verify that the LLM client is actually being called during your tests
3. Try running with debug logging enabled: `export LOG_LEVEL=DEBUG`
