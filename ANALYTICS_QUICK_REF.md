# Analytics Quick Reference

## Key Metrics at a Glance

### Token Usage
| Metric | Description | Typical Range |
|--------|-------------|---------------|
| Total Tokens | Prompt + Completion | 2,000 - 15,000 |
| Prompt Tokens | Input to LLM | 1,500 - 10,000 |
| Completion Tokens | LLM output | 500 - 5,000 |
| API Calls | Number of requests | 4 (one per agent) |

### Cost Estimates (Gemini 2.0 Flash)
| Document Size | Estimated Tokens | Estimated Cost |
|---------------|------------------|----------------|
| Small (1-5 pages) | 2,000 - 5,000 | $0.00005 - $0.00015 |
| Medium (5-20 pages) | 5,000 - 12,000 | $0.00015 - $0.00036 |
| Large (20+ pages) | 10,000 - 15,000 | $0.00030 - $0.00045 |

*Note: Costs are approximate and depend on content complexity*

### Performance Benchmarks
| Agent | Typical Duration | Token Usage |
|-------|------------------|-------------|
| Classifier | 1-2s | 500-800 |
| Extractor | 2-4s | 2,000-4,000 |
| Summarizer | 2-3s | 3,000-5,000 |
| Insight Generator | 1-2s | 1,000-2,000 |

## Agent Flow

```
PDF Upload
    ↓
Classifier Agent (3K chars)
    ↓
Extractor Agent (10K chars)
    ↓
Summarizer Agent (15K chars)
    ↓
Insight Generator (summary + sections)
    ↓
Results + Analytics
```

## Common Patterns

### High Token Usage
**Symptoms**: >15,000 tokens per analysis
**Causes**:
- Large document with dense text
- Complex technical content
- Multiple detailed sections

**Solutions**:
- Reduce truncation limits in `agents.py`
- Use more aggressive chunking
- Implement map-reduce for large docs

### Slow Performance
**Symptoms**: >15s total duration
**Causes**:
- Network latency
- API rate limiting
- Complex prompts

**Solutions**:
- Check network connection
- Verify API key limits
- Optimize prompt templates

### Failed Agents
**Symptoms**: failed_agents > 0
**Causes**:
- Malformed JSON response
- API timeout
- Invalid prompt

**Solutions**:
- Check agent logs
- Verify prompt format
- Add error handling

## Quick Commands

### View Recent Analytics
```bash
curl http://localhost:8000/analytics/sessions?limit=5
```

### Get Summary Stats
```bash
curl http://localhost:8000/analytics/summary
```

### Query Database Directly
```bash
sqlite3 backend/agentic_pdf.db "SELECT * FROM analytics_sessions ORDER BY start_timestamp DESC LIMIT 5;"
```

## Cost Optimization Tips

1. **Reduce Text Samples**
   - Classifier: 3K → 2K chars
   - Extractor: 10K → 7K chars
   - Summarizer: 15K → 10K chars

2. **Use Cheaper Models**
   - Switch to `google/gemini-flash-1.5`
   - Use `openai/gpt-3.5-turbo` for classification

3. **Batch Processing**
   - Process multiple PDFs in sequence
   - Reuse extracted sections

4. **Smart Caching**
   - Cache document classifications
   - Store extracted sections
   - Reuse summaries for similar docs

## Monitoring Checklist

- [ ] Check total cost weekly
- [ ] Monitor average tokens per session
- [ ] Review failed agent rates
- [ ] Verify performance benchmarks
- [ ] Archive old sessions monthly
- [ ] Update cost rates quarterly

## Emergency Actions

### Cost Spike
1. Check recent sessions for anomalies
2. Verify token usage patterns
3. Temporarily reduce truncation limits
4. Switch to cheaper model

### Performance Degradation
1. Check API status
2. Review network latency
3. Analyze slow agents
4. Optimize prompts

### High Failure Rate
1. Review error logs
2. Check API key validity
3. Verify prompt formats
4. Test with simple document

## Contact & Support

For issues with the analytics system:
1. Check `ANALYTICS_GUIDE.md` for detailed docs
2. Review error logs in terminal
3. Inspect browser console for frontend issues
4. Check database integrity

---

**Last Updated**: 2026-01-17
**Version**: 1.0
