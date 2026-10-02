# apple-hig skill

A [Claude Code](https://claude.com/claude-code) skill that gives Claude an offline copy of Apple's [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines). Claude uses it when designing or reviewing UI for iOS, iPadOS, macOS, watchOS, tvOS or visionOS, and it cites the HIG page and section behind each recommendation.

This repo doesn't include the guideline text, which is Apple's copyright. After you clone it, the crawler downloads the pages straight from Apple.

## Install

```sh
git clone https://github.com/b1tweiser/apple-hig ~/.claude/skills/apple-hig
python3 ~/.claude/skills/apple-hig/scripts/crawl.py
```

The crawler takes about a minute and needs `python3` and `curl`. It saves about 170 pages as markdown in `references/` and writes the page index into `SKILL.md`.

## Update

Apple revises the HIG every WWDC. Run the crawler again to refresh your copy:

```sh
python3 ~/.claude/skills/apple-hig/scripts/crawl.py
```

If fewer than 150 pages download (for example because the network failed), the crawler stops and leaves your current copy unchanged.

Updating the index rewrites `SKILL.md`, so `git status` will show it as modified. Run `git checkout SKILL.md` before `git pull`, then run the crawler again.
