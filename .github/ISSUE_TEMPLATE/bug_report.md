---
name: Bug report
about: Create a report to help us improve FastProxy
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Start FastProxy with '...'
2. Configure route '...'
3. Send request '...'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Actual behavior**
What actually happened.

**Logs**
If applicable, add logs to help explain your problem.
```
Paste logs here
```

**Environment (please complete the following information):**
 - OS: [e.g. Ubuntu 22.04, macOS 13.0]
 - FastProxy Version: [e.g. 2.0.0]
 - Python Version: [e.g. 3.11]
 - Deployment: [e.g. Docker, Native, Kubernetes]

**Configuration**
```yaml
# Paste relevant parts of your config.yaml here
routes:
  - path: /api
    target: http://backend:8001
```

**Additional context**
Add any other context about the problem here.

