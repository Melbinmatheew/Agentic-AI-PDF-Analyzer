# Token Usage and Thinking Process Analytics

## Overview

This analytics system provides comprehensive tracking and visualization of token usage, API costs, and agent execution flow for the Agentic AI PDF Analyzer. It helps you understand:

- **Token consumption** across different agents
- **Cost estimation** for API usage
- **Performance metrics** (execution time, success rates)
- **Thinking process flow** showing how agents collaborate
- **Historical data** for trend analysis

## Features

### 1. Real-Time Analytics Dashboard

After each PDF analysis, you'll see a detailed analytics dashboard showing:

#### Key Metrics
- **Total Tokens**: Combined prompt and completion tokens
- **API Calls**: Number of LLM API requests made
- **Estimated Cost**: Calculated based on model pricing
- **Processing Time**: Total duration of analysis

#### Agent Execution Summary
- Success/failure rates for each agent
- Individual agent execution times
- Execution timeline with visual indicators

#### Thinking Process Flow
- Visual representation of agent collaboration
- Step-by-step breakdown of the analysis pipeline
- Sequential flow diagram

#### Detailed Token Breakdown
- Per-call token usage
- Prompt vs completion token distribution
- Individual API call metrics

### 2. Analytics History Page

Access historical analytics data:
- View past analysis sessions
- Track cumulative token usage and costs
- Monitor performance trends
- Compare session metrics

## Architecture

### Backend Components

#### 1. `core/analytics.py`

**TokenUsageTracker**
- LangChain callback handler for tracking token usage
- Captures prompt tokens, completion tokens, and total tokens
- Records individual API call details

**AgentExecutionTracker**
- Monitors agent execution timing
- Tracks success/failure status
- Records input/output sizes

**AnalyticsSession**
- Combines token and execution tracking
- Generates comprehensive reports
- Calculates cost estimates

#### 2. `core/db.py`

**AnalyticsSession Table**
```python
- session_id: Unique identifier
- filename: Analyzed document name
- start_timestamp, end_timestamp: Session timing
- total_tokens, prompt_tokens, completion_tokens: Token metrics
- api_calls: Number of API requests
- estimated_cost_usd: Cost calculation
- total_agents, successful_agents, failed_agents: Agent metrics
- token_details, execution_details, thinking_process: JSON data
```

#### 3. API Endpoints

**POST /analyze-pdf**
- Returns analytics data along with analysis results
- Automatically tracks and saves session metrics

**GET /analytics/sessions?limit=N**
- Retrieves recent analytics sessions
- Default limit: 10 sessions

**GET /analytics/summary**
- Returns aggregate statistics
- Total sessions, tokens, costs, average duration

### Frontend Components

#### 1. `AnalyticsDashboard.jsx`

Real-time analytics visualization displayed after each analysis:
- Gradient metric cards with hover animations
- Agent execution timeline
- Thinking process flow diagram
- Expandable detailed token breakdown

#### 2. `AnalyticsHistory.jsx`

Historical analytics page:
- Summary statistics across all sessions
- Session list with detailed metrics
- Success/failure indicators
- Sortable and filterable views

## Usage

### Viewing Analytics After Analysis

1. Upload and analyze a PDF
2. Scroll down to see the **Analytics Dashboard**
3. Review token usage, costs, and agent performance
4. Expand "Detailed Token Breakdown" for per-call metrics

### Accessing Analytics History

1. Click the **Analytics** button in the header
2. View summary statistics (total sessions, tokens, costs)
3. Browse recent sessions
4. Click "Back to Analyzer" to return

### Understanding the Metrics

#### Token Usage
- **Prompt Tokens**: Input text sent to the LLM
- **Completion Tokens**: Generated response from the LLM
- **Total Tokens**: Sum of prompt and completion tokens

#### Cost Calculation
Based on model pricing (configurable):
```python
cost = (prompt_tokens / 1000) * prompt_rate + 
       (completion_tokens / 1000) * completion_rate
```

Current default rates (for gemini-2.0-flash):
- Prompt: $0.01 per 1M tokens
- Completion: $0.03 per 1M tokens

#### Agent Metrics
- **Successful Agents**: Completed without errors
- **Failed Agents**: Encountered exceptions
- **Duration**: Time taken for execution

## Configuration

### Adjusting Cost Rates

Edit `backend/core/analytics.py`:

```python
# In AnalyticsSession.get_full_report()
cost_per_1k_prompt = 0.00001  # Adjust based on your model
cost_per_1k_completion = 0.00003
```

### Changing Model

Edit `backend/.env`:

```env
LLM_MODEL=google/gemini-2.0-flash-001
OPENROUTER_API_KEY=your_key_here
```

### Session Limit

Modify the history page limit in `AnalyticsHistory.jsx`:

```javascript
fetch('/analytics/sessions?limit=50')  // Default: 20
```

## Database Schema

Analytics data is stored in SQLite (`agentic_pdf.db`):

```sql
CREATE TABLE analytics_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,
    filename TEXT,
    start_timestamp DATETIME,
    end_timestamp DATETIME,
    total_duration_seconds REAL,
    total_tokens INTEGER,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    api_calls INTEGER,
    estimated_cost_usd REAL,
    total_agents INTEGER,
    successful_agents INTEGER,
    failed_agents INTEGER,
    token_details JSON,
    execution_details JSON,
    thinking_process JSON,
    metadata JSON
);
```

## Performance Considerations

### Token Optimization

The system uses text truncation to minimize token usage:
- **Classifier**: First 3,000 characters
- **Extractor**: First 10,000 characters
- **Summarizer**: First 15,000 characters
- **Insight Generator**: Uses summary + sections (compact)

### Callback Overhead

Token tracking adds minimal overhead:
- Callbacks are lightweight
- No blocking operations
- Async-compatible

### Database Performance

- Indexed on `session_id` and `start_timestamp`
- JSON columns for flexible data storage
- Efficient querying for recent sessions

## Troubleshooting

### Analytics Not Showing

**Issue**: Analytics dashboard is empty after analysis

**Solutions**:
1. Check that `analytics` is in the response:
   ```javascript
   console.log(result.analytics)
   ```
2. Verify trackers are in state:
   ```python
   print(state.get('_token_tracker'))
   ```

### Cost Estimates Seem Wrong

**Issue**: Estimated costs don't match actual billing

**Solutions**:
1. Verify model pricing in `analytics.py`
2. Check OpenRouter pricing page for current rates
3. Update cost calculation formulas

### Missing Token Data

**Issue**: Token counts show as 0

**Solutions**:
1. Ensure LangChain callbacks are working
2. Check OpenRouter response format
3. Verify `on_llm_end` is being called

### Database Errors

**Issue**: Failed to save analytics session

**Solutions**:
1. Check database file permissions
2. Verify SQLite installation
3. Review error logs for schema issues

## Best Practices

### 1. Regular Monitoring
- Check analytics history weekly
- Monitor cost trends
- Identify optimization opportunities

### 2. Cost Management
- Set budget alerts based on token usage
- Optimize text truncation limits
- Use cheaper models for classification

### 3. Performance Tuning
- Monitor agent execution times
- Identify slow agents
- Optimize prompts for efficiency

### 4. Data Retention
- Periodically archive old sessions
- Export analytics data for reporting
- Clean up test sessions

## Future Enhancements

Potential improvements to the analytics system:

1. **Advanced Visualizations**
   - Charts and graphs for trend analysis
   - Token usage over time
   - Cost breakdown by agent

2. **Export Capabilities**
   - CSV export for sessions
   - PDF reports
   - API for external tools

3. **Alerts and Notifications**
   - Cost threshold warnings
   - Performance degradation alerts
   - Failure notifications

4. **Comparative Analysis**
   - Compare sessions side-by-side
   - Benchmark against averages
   - Model performance comparison

5. **Real-time Streaming**
   - Live token counting during analysis
   - Progress indicators
   - Streaming analytics updates

## API Reference

### Analytics Endpoints

#### GET /analytics/sessions

Retrieve recent analytics sessions.

**Query Parameters**:
- `limit` (optional): Number of sessions to return (default: 10)

**Response**:
```json
{
  "sessions": [
    {
      "session_id": "uuid",
      "filename": "document.pdf",
      "start_timestamp": "2026-01-17T12:00:00",
      "total_tokens": 5000,
      "estimated_cost_usd": 0.00015,
      "total_duration_seconds": 12.5,
      "successful_agents": 4,
      "failed_agents": 0
    }
  ]
}
```

#### GET /analytics/summary

Get aggregate statistics.

**Response**:
```json
{
  "total_sessions": 25,
  "total_tokens": 125000,
  "total_cost": 0.00375,
  "average_duration": 10.2,
  "total_api_calls": 100
}
```

## Contributing

To extend the analytics system:

1. Add new metrics in `AnalyticsSession`
2. Update database schema in `db.py`
3. Create visualizations in dashboard components
4. Update this documentation

## License

Part of the Agentic AI PDF Analyzer project.
