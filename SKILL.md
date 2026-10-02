---
name: apple-hig
description: Apple Human Interface Guidelines (HIG) — full offline copy of developer.apple.com/design/human-interface-guidelines covering iOS, iPadOS, macOS, watchOS, tvOS, visionOS, iPhone Duo and games. Use whenever designing, building, or reviewing UI for any Apple platform — SwiftUI/UIKit/AppKit screens, layout, navigation, tab bars, sheets, alerts, buttons, typography, color, Dark Mode, Liquid Glass, materials, SF Symbols, app icons, accessibility, onboarding, widgets, Live Activities, notifications, App Store-ready UX — or when the user asks "what does Apple recommend", "is this HIG-compliant", or mentions HIG, even if they don't name it.
---

# Apple Human Interface Guidelines

Local mirror of Apple's HIG: 173 pages as markdown in `references/`, one file per HIG page (filename = URL slug, e.g. `buttons.md` ↔ `/design/human-interface-guidelines/buttons`). Snapshot taken 2026-10-02.

## How to use

1. Find the relevant page(s) in the index below. Grep `references/` when the topic isn't obvious from titles (e.g. `grep -ril "44x44" references/`, `grep -l "Liquid Glass" references/*.md`).
2. Read the page rather than answering from memory. The HIG changes every WWDC (Liquid Glass and iPhone Duo are recent), and exact numbers such as hit targets, margins and type sizes matter. Most pages are around 1,000 words, so read them in full. A few are long (`typography.md` is about 10k words, and `widgets.md`, `wallet.md` and `machine-learning.md` are 6–7k), so run `grep -n '^#' <page>` first and read only the sections you need.
3. Most component pages follow the same order: intro → **Best practices** → topic sections → **Platform considerations** (per-OS differences, as `#### iOS, iPadOS`, `#### visionOS` and so on) → **Resources** / **Change log**. Check Platform considerations for the user's target OS, because guidance often differs. For example, visionOS hit targets are 60 pt and other platforms use 44 pt.
4. Cite the page and section for every recommendation or flagged issue, and link the live page: `https://developer.apple.com/design/human-interface-guidelines/<slug>`. Citations are what let the user check the advice, and they separate HIG guidance from your own opinion. If you add advice the HIG doesn't cover (App Store rules, engineering practice), label it as your own.
5. When a rule seems to cut against the user's case, quote it and explain your call instead of dropping it silently. For example, the alert guidance says not to use the destructive style for an action the person chose deliberately, yet deleting an account may still warrant red.
6. Pages link to each other with relative `.md` links, so follow them for related guidance. Images appear only as text descriptions (`[Image: …]`). If the user asks about something newer than the snapshot date above and you can't find it in `references/`, say the local copy may be out of date.

When reviewing a UI (code or screenshot), check at least these, each against its page:
- layout and safe areas (`layout.md`)
- typography and Dynamic Type (`typography.md`)
- color, contrast and Dark Mode (`color.md`, `dark-mode.md`, `accessibility.md`)
- hit targets (`accessibility.md`, `buttons.md`)
- whether the navigation pattern fits (`tab-bars.md`, `sidebars.md`)
- VoiceOver labels (`voiceover.md`)
- the component page for each control used

## Refreshing

Run `python3 scripts/crawl.py`. It uses `curl`, so it works behind TLS-intercepting proxies, and takes about a minute. It re-downloads every page into `references/` and regenerates the index, page count and snapshot date below. If fewer than 150 pages come back, it aborts and leaves the current copy untouched.

## Index

_Not generated yet. Run `python3 scripts/crawl.py` to download the HIG pages into `references/` and fill in this index._
