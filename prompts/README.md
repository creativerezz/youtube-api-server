# Prompts Directory

This directory contains LLM/AI system prompts for Claude and other AI tools used in the YouTube API Server project.

## Purpose

This collection stores reusable prompts that guide AI behavior for project-specific tasks such as:
- YouTube data extraction workflows
- API endpoint design and testing
- Code review and refactoring
- Documentation generation
- Deployment automation

These prompts help maintain consistency in AI-assisted development and serve as a knowledge base for common project patterns.

## Organization

### File Naming Convention
- Use descriptive, kebab-case names: `task-name.md` or `task-name.txt`
- Group related prompts with common prefixes: `youtube-*.md`, `api-*.md`
- Use `.md` for markdown-formatted prompts with examples and context
- Use `.txt` for simple, plain-text prompts

### Prompt Structure
Each prompt file should include:

```markdown
# [Task Name]

## Context
Brief description of when and why to use this prompt.

## Instructions
Clear, specific instructions for the AI tool.

## Examples
Input/output examples demonstrating expected behavior.

## Notes
Additional context, edge cases, or considerations.
```

### Directory Organization (Future)
As the collection grows, consider organizing into subdirectories:
- `/api/` - API design, endpoint creation, validation
- `/youtube/` - YouTube-specific data extraction and processing
- `/testing/` - Test generation, debugging, quality assurance
- `/deployment/` - CI/CD, Docker, Railway deployment tasks
- `/docs/` - Documentation generation and updates

## Usage

### With Claude Code
Reference prompts in your CLAUDE.md file or load them during interactive sessions:
```markdown
See prompts/youtube-extraction.md for guidance on extracting video data.
```

### With Claude API
Load prompt content programmatically:
```python
with open('prompts/task-name.md', 'r') as f:
    system_prompt = f.read()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    system=system_prompt,
    messages=[...]
)
```

### Best Practices
- **Version Control**: Keep prompts in git to share knowledge across the team
- **Iterate**: Refine prompts based on AI responses and project evolution
- **Document Context**: Include enough background so prompts work standalone
- **Test Regularly**: Verify prompts produce expected results as AI models update
- **Use Variables**: Mark placeholder values clearly (e.g., `{VIDEO_URL}`, `{ENDPOINT_NAME}`)

## Security Considerations

- **No Secrets**: Never include API keys, tokens, or credentials in prompts
- **Sensitive Patterns**: If a prompt references sensitive implementation details, add it to `.gitignore`:
  ```gitignore
  prompts/*.secret.md
  prompts/internal-*
  ```

## Contributing

When adding new prompts:
1. Use the structure template above
2. Test the prompt to ensure it produces desired results
3. Include clear examples and context
4. Update this README if introducing new categories

## Examples

### Example Prompt File: `youtube-metadata-extraction.md`

```markdown
# YouTube Metadata Extraction

## Context
Extract video metadata using the YouTube oEmbed API for the /youtube/video-data endpoint.

## Instructions
Given a YouTube video URL, extract the following metadata:
- Title
- Author name and channel URL
- Thumbnail URL
- Video dimensions (height, width)

Use the oEmbed API endpoint: https://www.youtube.com/oembed?url={VIDEO_URL}&format=json

## Examples
Input: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Output: VideoData model with title, author_name, thumbnail_url, etc.

## Notes
- Handle invalid URLs gracefully
- Support multiple URL formats (youtube.com, youtu.be, embed)
- Cache responses when possible
```

## Maintenance

Review and update prompts periodically to:
- Align with project architecture changes
- Incorporate new best practices
- Remove deprecated patterns
- Improve clarity based on usage feedback

---

For questions or suggestions about prompt organization, see the main [CLAUDE.md](../CLAUDE.md) or contact the project maintainers.
