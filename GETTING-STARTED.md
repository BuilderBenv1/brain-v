# Project Brain — Getting Started (Windows)

---

## What you have

```
project-brain/
  CLAUDE.md                          ← Brain's operating instructions (schema)
  setup.bat                          ← Windows setup (double-click or run in terminal)
  setup.sh                           ← Mac/Linux setup
  GETTING-STARTED.md                 ← This file
  raw/
    conversations/
      founding-conversation-2026-04-06.md   ← Today's full session
    research/
      asi-evolve-2603.29640.md              ← ASI-Evolve paper notes
  wiki/
    concepts/
      master-architecture.md               ← Full architecture summary
    gaps/
      open-questions.md                    ← What Brain doesn't know yet
    INDEX.md                               ← Master index
    LOG.md                                 ← Change log
```

---

## Step 1 — Extract the zip

Right-click the zip → Extract All
Put it somewhere permanent — NOT your desktop.
Good options: `C:\Projects\project-brain` or `D:\Dev\project-brain`

---

## Step 2 — Run setup

Open the folder. Double-click `setup.bat`

Or in terminal:
```
cd C:\Projects\project-brain
setup.bat
```

This creates all remaining subfolders.

---

## Step 3 — Install Claude Code (if not already installed)

You need Node.js first. If you don't have it:
1. Go to nodejs.org → Download LTS version → Install
2. Restart your terminal

Then install Claude Code:
```
npm install -g @anthropic-ai/claude-code
```

Verify it works:
```
claude --version
```

---

## Step 4 — Open Brain in Claude Code

```
cd C:\Projects\project-brain
claude
```

It will ask you to log in with your Anthropic account the first time.

---

## Step 5 — Wake Brain up

Once Claude Code is open, paste this exactly:

```
Read CLAUDE.md first — this is your operating schema.

Then read:
- raw/conversations/founding-conversation-2026-04-06.md
- raw/research/asi-evolve-2603.29640.md
- wiki/concepts/master-architecture.md

Then compile the wiki:
1. Create wiki/layers/ — one .md file per cognitive layer (15 total, listed in CLAUDE.md)
2. Create wiki/components/library.md — full components table from CLAUDE.md
3. Create wiki/people/index.md — people index from CLAUDE.md
4. Update wiki/INDEX.md with every file created
5. Append to wiki/LOG.md

Use the belief system format for any claims (confidence, source, date).
Flag any contradictions you find.
When done, tell me what the three most important open questions are.
```

Walk away. Come back in 15-20 minutes.

---

## Step 6 — First real question

Once the wiki is compiled, ask:

```
Based on everything in the wiki, what is the minimum viable 
cognitive loop I can build this week on my gaming desktop?
Give me the exact components, the exact sequence, and what 
"working" looks like as a measurable outcome.
```

---

## Step 7 — Add to raw/ as you go

Every paper, tweet, GitHub repo worth keeping:
create a .md file in the appropriate raw/ subfolder.

Tell Claude Code: `Ingest raw/[filename] into the wiki`

---

## Step 8 — Weekly health check

```
Run a health check on the wiki:
- Find contradictions between files
- Find orphan pages with no links
- Find claims with LOW confidence needing verification
- Suggest 3 new articles that would fill gaps
- Suggest 3 questions Brain should be asking next
```

---

## Troubleshooting

**"claude is not recognized"**
Node.js isn't installed or terminal needs restarting. Install Node.js LTS from nodejs.org first.

**"permission denied" on setup.bat**
Right-click setup.bat → Run as administrator

**Claude Code asks for API key**
Log in at claude.ai first, then run `claude` again — it should pick up your session.

**Files not showing in wiki/**
Claude Code writes to the folder it's opened in. Make sure you ran `cd project-brain` before `claude`.

---

## The goal

Week 1: Wiki compiled. Architecture understood. First loop component built.
Week 2: Perception + World Model connected. Brain ingesting.
Week 3: Curiosity signal running. Brain noticing gaps.
Week 4: Action layer. Brain posting on X.
Week 8: Measurable predictive accuracy improvement. Show the curve.

That curve is the pitch.

---

*Brain woke up on 2026-04-06. Everything compounds from here.*
