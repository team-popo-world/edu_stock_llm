# Security Guidelines

## Overview

This document outlines security best practices and guidelines for the Educational Stock Investment Game project.

## API Key Security

### 🚨 URGENT: API Key Rotation Required

**The current .env file contains exposed API keys that must be rotated immediately:**

1. **Google API Key**: `AIzaSyDU_mJGj5AMUSi2JwJxqz72Kz18TKZctls` (EXPOSED)
2. **OpenAI API Key**: Comments contain visible API key patterns

### Immediate Actions Required:

1. **Rotate API Keys**:
   - Visit [Google AI Studio](https://aistudio.google.com/) and generate a new API key
   - Delete the exposed key immediately
   - Update `.env` file with new key

2. **Clean Git History**:
   ```bash
   # Remove sensitive data from git history
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env' --prune-empty --tag-name-filter cat -- --all
   ```

3. **Verify .gitignore**:
   - Ensure `.env` is properly ignored
   - Check all environment files are excluded

## Environment Variables

### Required Variables:
- `GOOGLE_API_KEY`: Google Gemini API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins

### Optional Variables:
- `DEBUG`: Enable debug mode (default: false)
- `API_HOST`: API server host (default: 0.0.0.0)
- `API_PORT`: API server port (default: 8000)

## Input Validation

The application includes comprehensive input validation:

### Validated Inputs:
- Scenario types (magic_kingdom, foodtruck_kingdom, moonlight_thief, three_little_pigs)
- Investment strategies (random, conservative, aggressive, trend)
- File paths (prevents path traversal)
- Investment amounts (range validation)
- Stock symbols (format validation)
- Text inputs (XSS prevention)

### Security Features:
- HTML/Script tag removal
- SQL injection pattern detection
- Path traversal prevention
- Input length limits
- Format validation

## CORS Configuration

### Production Setup:
```python
# Configure specific origins for production
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### Development Setup:
```python
# Local development origins
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501
```

## Error Handling

### Secure Error Responses:
- No sensitive information in error messages
- Structured logging for security events
- Proper HTTP status codes
- User-friendly error messages

### Logging Security Events:
- Failed authentication attempts
- Invalid input validation
- Unusual API usage patterns
- System errors and exceptions

## Deployment Security

### Docker Security:
- Non-root user execution
- Minimal base image (python:3.11-slim)
- Health checks enabled
- Environment variable isolation

### Production Checklist:
- [ ] API keys rotated and secure
- [ ] CORS properly configured
- [ ] HTTPS enabled
- [ ] Input validation active
- [ ] Logging configured
- [ ] Error handling implemented
- [ ] Security headers added
- [ ] Rate limiting configured

## Monitoring and Alerts

### Security Monitoring:
- API usage patterns
- Failed requests
- Error rates
- Response times

### Log Analysis:
- Review logs for suspicious activity
- Monitor API key usage
- Track validation failures
- Audit file access patterns

## Incident Response

### Security Incident Steps:
1. **Immediate**: Rotate compromised API keys
2. **Assessment**: Analyze scope of exposure
3. **Containment**: Limit further access
4. **Recovery**: Deploy fixed version
5. **Lessons**: Update security measures

### Contact Information:
- Security issues: Create issue in GitHub repository
- Urgent security concerns: Follow responsible disclosure

## Best Practices

### Development:
- Never commit API keys
- Use environment variables
- Validate all inputs
- Log security events
- Regular security reviews

### Production:
- Monitor API usage
- Regular key rotation
- Security updates
- Backup procedures
- Incident response plan

## Testing Security

### Security Tests:
```bash
# Run security-focused tests
pytest tests/test_validators.py -v
pytest tests/test_api.py::TestSecurity -v
```

### Manual Security Testing:
- Input validation testing
- CORS configuration testing
- Error handling verification
- API key validation testing

## Updates and Maintenance

### Regular Tasks:
- API key rotation (quarterly)
- Security dependency updates
- Log review and analysis
- Security configuration review

### Version Control:
- Keep security patches current
- Review dependencies regularly
- Monitor security advisories
- Update security documentation

---

**Remember**: Security is an ongoing process, not a one-time setup. Regularly review and update these practices as the project evolves.