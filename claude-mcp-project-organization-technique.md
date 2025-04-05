# How I Organized 75+ Coding Projects in Minutes: The Claude MCP Technique Every Developer Needs

*By Jannis Douloumis*

*4 min read · Mar 18, 2025*

---

I believe you are familiar with this scenario: You've accumulated dozens of coding projects over months — some maintained on GitHub, others lurking only on your local machine. Keeping track of what exists where became increasingly difficult as your collection grows. This disorganization makes it challenging to prioritize which projects to continue developing and which to archive.

## Happy Times ahead, thanks to MCP

I recently used anthropic's model context protocol to analyze my development folder and create a comprehensive overview of my projects. This automation saved me hours of manual work while providing valuable insights into my development history.

## The Challenge: Project Overload

My development folder had ballooned to over 75 projects spanning multiple technologies and purposes. I needed to understand:

- Which projects were Git-enabled vs. standalone local experiments
- Which projects existed on GitHub vs. only on my machine
- The purpose and technology stack of each project
- How to categorize projects to better understand my past coding interests

Manually auditing each project would have taken an entire day — checking for .git folders, opening READMEs, inspecting code to determine technologies used, and organizing everything into categories.

> **Before we start**: If you are new to the MCP topic there are plenty of beginner friendly tutorials here on Medium. Just search for MCP.

## Claude MCP to the Rescue

I asked Claude Desktop (with MCP servers for local file access, github connection and tavily websearch enabled) to analyze my development folder, check which projects had Git repositories, determine which were connected to GitHub, categorize them, and create an HTML report summarizing everything.

The prompt was straightforward:

```
"Check my code projects in my development folder. Analyze what they do and create an HTML file with paths to the project folders. Create categories. Check if they are git enabled and a GitHub repository exists and highlight this information in the HTML file so I can see which projects exist on my GitHub and which are only existing in my development folder. Save the created HTML file with a proper name to my downloads folder."
```

Claude immediately went to work, accessing my development directory with my permission, then:

1. Listed all the project directories
2. Identified which had .git folders (indicating Git-enabled projects)
3. Examined Git config files to determine which had GitHub remotes
4. Analyzed directory contents to determine project types/technologies
5. Generated a categorized HTML report with filtering capabilities
6. Saved the file to my downloads folder

The entire process took just a few minutes — automation at its finest.

## The Results: Clarity and Insights

### My Coding Projects Ready For Evaluation

The generated HTML report provided:

- **Project Statistics**: 77 total projects with 39 Git repositories and 38 non-Git projects
- **Filtering Options**: Toggle between All/Git/GitHub/Non-Git projects
- **Categorized Sections**: Python, Web/JavaScript, WordPress Integration, AI/ML, Image Processing, Tools/Utilities, etc.
- **Visual Indicators**: Color-coded tags showing Git status and project categories
- **Project Details**: Descriptions, file paths, and GitHub status for each project

This report gave me immediate clarity about my development landscape. I could see:

- Several projects were Git-enabled but never pushed to GitHub
- I had multiple projects with similar functionality (duplicate efforts!)
- My strongest technology focus areas based on project counts
- Projects I had completely forgotten about but contained valuable code
- Which projects were worth continuing vs. archiving

## Making Better Decisions

With this comprehensive overview, I could make informed decisions about:

- **Project Consolidation**: Merging similar projects or extracting useful code
- **GitHub Management**: Identifying which local projects deserve to be published
- **Technology Focus**: Understanding where I've spent most of my coding time
- **Effort Prioritization**: Deciding which projects to continue developing
- **Code Reuse**: Finding existing solutions in my own codebase rather than rewriting

## The Power of AI-Assisted Organization

This experience demonstrated how Claude's MCP capabilities can transform what would have been a tedious manual task into an efficient automated process. The ability to interact with my filesystem, analyze project structures, and generate an organized report saved me significant time while providing valuable insights.

For developers managing numerous projects, this kind of AI-assisted organization can be transformative. It helps turn project chaos into structured understanding, enabling better decision-making about where to invest development time.

The next time you're overwhelmed by your collection of coding projects, consider asking an AI assistant with filesystem access to help you make sense of it all. The clarity might just help you rediscover valuable work and make better decisions about your coding future.

---

👍 *If you found this article helpful, please show support by clapping.*

💡 *You can give up to 50 claps on Medium with one long press? Try it!*

*Thank you for reading!*

---

**Tags:** Development, Productivity, Software Development, MCPs, Git

---

### Comments

**Micha(el) Bladowski** · *1 day ago*

> github connection and tavily websearch enabled

Glad you didn't show which MCPs you are using here + your config 👍

---

### More from Jannis Douloumis

- [Anthropic's New Coding Tool "Claude Code" Beta, Key Features explained (Is It Any Good?)](https://medium.com/@jannisdouloumis/anthropics-new-coding-tool-claude-code-beta-key-features-explained-is-it-any-good)
  *I've been eagerly waiting to get my hands on Claude Code ever since I first heard about Anthropic's new AI coding assistant.*
  Feb 28

- [Bolt.diy Is The Open Source Coding Tool We've Been Asking for](https://medium.com/@jannisdouloumis/bolt-diy-is-the-open-source-coding-tool-weve-been-asking-for)
  *You're probably thinking, "Great, another browser-based development environment."*
  Jan 12

- [The Free Tool That's Making Mac Users Question Their Paid Clipboard Managers](https://medium.com/@jannisdouloumis/the-free-tool-thats-making-mac-users-question-their-paid-clipboard-managers)
  *Sometimes the best discoveries come from unexpected setbacks. After years, my trusty clipboard manager had completely stopped working (I am…*
  Dec 28, 2024

- [Your Mac Ran Out of Storage 😳? This Is Why I Never Have To Worry Again](https://medium.com/@jannisdouloumis/your-mac-ran-out-of-storage-this-is-why-i-never-have-to-worry-again)
  *Managing storage on a Mac can be a challenge, especially when dealing with large applications and data. I've explored a couple of effective…*
  Jan 13

CONVERSION COMPLETE