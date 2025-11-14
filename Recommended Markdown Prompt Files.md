<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Do deep research on the internet about what are the recommended prompt files that I should have in order to develop my application. because i saw people having like ARCHITECTURE.md, SKILLS.md, or something like that so I think that I want to have those in my repository. I heard that they usually have those to use for Claude Code also but I think they can be used as general instructions since I am using Cursor also instead of just Claude Code. Give the short explanations of what the markdown files for and the example of them.

Perfect! Now I'll provide a comprehensive summary of the research:

## Recommended Prompt Files for AI-Assisted Development

Based on comprehensive research into Claude Code, Cursor, and AI-assisted development best practices, here's what you need to know about essential documentation files for your repository:

### Core Files You Should Have

**CLAUDE.md** is the most important file and should be your first priority. This is Claude Code's automatic context loader—it appears whenever you start a conversation. Include your project structure, common commands, code style guidelines, testing instructions, and any project quirks. This file becomes part of Claude's prompts, so it improves over time as you refine it.[^1_1][^1_2][^1_3][^1_4]

**ARCHITECTURE.md** is crucial for larger projects and helps AI quickly understand your entire system. It should contain your project structure (directory tree), high-level system diagrams, core components and their responsibilities, databases, external integrations, deployment infrastructure, security considerations, and future roadmap. Research shows this file significantly improves AI's ability to navigate and contribute to complex codebases.[^1_5][^1_6][^1_1]

**.cursor/index.mdc** (or legacy `.cursorrules`) is specifically for Cursor IDE users. This stores project-specific rules and conventions that Cursor should follow. Create this in `.cursor/` directory and set it as "Always" apply type to ensure consistent AI behavior throughout your project.[^1_7][^1_8]

**SKILLS.md** defines specialized Claude Skills—reusable workflows for complex tasks. Each skill folder contains a SKILL.md file with YAML frontmatter (name and description) plus optional resources subdirectory containing supporting files, templates, or reference documentation. Skills use "progressive disclosure" where Claude only loads detailed resources when needed, preserving context window.[^1_9][^1_10]

### Supporting Documentation Files

**PROTOCOL.md** establishes your workflow rules and collaboration protocol. Define your role versus the AI's role, your workflow phases, coding standards, git protocols (branch naming, commit messages), review processes, and when to ask for help from Claude.[^1_11]

**ACTION_PLAN.md** tracks current tasks and progress with status indicators (⚪ not started, 🟡 in progress, 🟢 completed). Include priority ordering, subtasks, dependencies, and relevant file locations. This helps Claude understand what needs to be done next.[^1_12]

**MANIFEST.md** provides a complete project state snapshot for context persistence across sessions. Include project overview, technology stack, current status/milestones, component descriptions, architectural decisions, environment configuration, known issues, and next steps.[^1_13]

**REQUIREMENTS.md** formally specifies features using user stories with acceptance criteria and technical requirements. This prevents misunderstandings about what should be implemented.[^1_14]

### Why These Files Matter

Research on 253 Claude.md files from 242 repositories revealed that these files follow shallow hierarchical structures with most containing: Build and Run instructions (42%), Implementation Details (35%), Architecture descriptions (31%), and AI role definitions (15%). The most successful projects prioritize action-oriented, context-rich documentation.[^1_15][^1_16]

For Cursor specifically, developers use `.mdc` files (instead of `.cursorrules`) to define project structure, code style, architecture patterns, testing conventions, documentation standards, and git workflows. Each `.mdc` file should focus on one specific concern and be under 100 lines for optimal token usage.[^1_8][^1_7]

### Quick Implementation Strategy

**Start with minimum setup:**

1. Create **CLAUDE.md** immediately - this gives Claude instant context
2. Add **ARCHITECTURE.md** if your project exceeds 10k lines
3. Add **.cursor/index.mdc** if using Cursor IDE

**Expand to medium setup:**

- Add **REQUIREMENTS.md** for formal feature specifications
- Add **ACTION_PLAN.md** if tracking complex features

**Complete setup for teams:**

- Add **PROTOCOL.md** for collaboration guidelines
- Add **MANIFEST.md** for multi-session context
- Add **SKILLS.md** for reusable workflows


### Key Takeaways

These files work with both Claude Code and Cursor because they're language-agnostic markdown documentation. The difference is that Claude automatically loads CLAUDE.md files, while Cursor uses `.cursor/` rules. Both systems benefit from comprehensive ARCHITECTURE.md files that explain your system design.[^1_6][^1_1][^1_5][^1_7]

The most impactful strategy is creating these files iteratively—start with CLAUDE.md, add ARCHITECTURE.md when needed, then expand based on your project complexity. These become your project's "knowledge base" that helps AI make better decisions throughout development.[^1_1][^1_15]

[^1_2][^1_10][^1_3][^1_16][^1_11][^1_14][^1_5][^1_9][^1_12][^1_6][^1_7][^1_8][^1_13][^1_15][^1_1]

I've also created a comprehensive downloadable guide with detailed examples for all 8 recommended files:
<span style="display:none">[^1_17][^1_18][^1_19][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_30][^1_31][^1_32][^1_33][^1_34][^1_35][^1_36][^1_37][^1_38][^1_39][^1_40][^1_41][^1_42][^1_43]</span>

<div align="center">⁂</div>

[^1_1]: https://danielmeppiel.github.io/awesome-ai-native/docs/concepts/

[^1_2]: https://www.builder.io/blog/claude-code

[^1_3]: https://www.anthropic.com/engineering/claude-code-best-practices

[^1_4]: https://www.eesel.ai/blog/git-workflows-claude-code

[^1_5]: https://architecture.md

[^1_6]: https://github.com/noahbald/awesome-architecture-md

[^1_7]: https://kirill-markin.com/articles/cursor-ide-rules-for-ai/

[^1_8]: https://dotcursorrules.com

[^1_9]: https://skywork.ai/blog/ai-agent/claude-skills-skill-md-resources-runtime-loading/

[^1_10]: https://www.eesel.ai/blog/skills-md-vs-agents-md

[^1_11]: https://www.reddit.com/r/ClaudeAI/comments/1j5t1nh/my_cursor_claude_37t_method_the_opposite_of_vibe/

[^1_12]: https://www.reddit.com/r/cursor/comments/1k76kvd/always_make_a_markdown_file_before_tackling_a_new/

[^1_13]: https://github.com/sethshoultes/Manual-for-AI-Development-Collaboration

[^1_14]: https://www.linkedin.com/posts/george-sadathian-280914102_softwaredevelopment-aiassistedcoding-cursoride-activity-7366044314855956480-IOF5

[^1_15]: https://arxiv.org/html/2509.14744v1

[^1_16]: https://arxiv.org/html/2509.14744

[^1_17]: https://support.claude.com/en/articles/12512198-how-to-create-custom-skills

[^1_18]: https://claude-plugins.dev/skills/@romiluz13/cc10x/cursor-rules-generation

[^1_19]: https://github.com/Alexanderdunlop/ai-architecture-prompts

[^1_20]: https://blog.fsck.com/2025/10/16/skills-for-claude/

[^1_21]: https://github.blog/ai-and-ml/generative-ai/spec-driven-development-using-markdown-as-a-programming-language-when-building-with-ai/

[^1_22]: https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/

[^1_23]: https://danielraffel.me/til/2024/09/23/how-i-optimized-my-development-workflow-with-cursor-pro-chatgpt-and-github-desktop/

[^1_24]: https://shekhargulati.com/2024/07/31/generating-architecture-md-with-code2prompt-and-openai-gpt-4o-mini-model/

[^1_25]: https://www.freecodecamp.org/news/how-to-structure-your-readme-file/

[^1_26]: https://github.com/digitalchild/cursor-best-practices

[^1_27]: https://www.datacamp.com/tutorial/claude-code

[^1_28]: https://forum.cursor.com/t/good-examples-of-cursorrules-file/4346

[^1_29]: https://arxiv.org/html/2508.08804v1

[^1_30]: https://www.siddharthbharath.com/claude-code-the-complete-guide/

[^1_31]: https://dev.to/simbo1905/augmented-intelligence-ai-coding-using-markdown-driven-development-pg5

[^1_32]: https://github.com/zebbern/claude-code-guide

[^1_33]: https://www.makeareadme.com

[^1_34]: https://www.codecademy.com/article/markdown-and-readmemd-files

[^1_35]: https://manifest.build/docs

[^1_36]: https://www.ionos.com/digitalguide/websites/web-development/readme-file/

[^1_37]: https://www.drupal.org/docs/develop/managing-a-drupalorg-theme-module-or-distribution-project/documenting-your-project/readmemd-template

[^1_38]: https://github.com/ruvnet/claude-flow/wiki/CLAUDE-MD-Templates

[^1_39]: https://github.com/jcmellado/markdown-template/blob/master/examples/schema.md

[^1_40]: https://kce.fgov.be/sites/default/files/2023-05/KCE_Trials_IMP_MD_Protocol%20template_V3.0_20230413.docx

[^1_41]: https://www.bumc.bu.edu/irb/files/2016/10/Protocol-Template.docx

[^1_42]: https://dev.to/merlos/how-to-write-a-good-readme-bog

[^1_43]: https://github.com/ietf-satp/draft-avrilionis-satp-asset-profiles/blob/main/draft-todo-yourname-protocol.md

