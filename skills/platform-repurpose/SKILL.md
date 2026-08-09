---
name: platform-repurpose
description: Cut one long asset into platform-specific posts that fit on the first try. Use when a video, article or build needs versions for YouTube, Instagram, TikTok, X or LinkedIn.
---

# Platform repurpose

One asset in, platform cuts out. Load `bareloop-voice` first.

The point of this file is not tone. It is the numbers below. Copy written
without them comes back in the right voice and the wrong length, and gets
trimmed by hand every time — which is the work you were trying to avoid.

## Hard limits

Counts are characters unless noted. Write to the target, not the ceiling: copy
that lands at 98% of a limit breaks the moment anyone edits a word.

| Surface | Limit | Target | Notes |
|---|---|---|---|
| Instagram bio | 150 | ≤ 135 | Line breaks allowed. |
| Instagram Name field | 30 | ≤ 27 | Searchable. Put keywords here, not in the bio. |
| Instagram caption | 2 200 | ≤ 300 | Only ~125 show before "more". Front-load. |
| TikTok bio | 80 | ≤ 74 | The tightest surface. Cut first, tone second. |
| X post | 280 | ≤ 240 | Leave room for a quote-post. |
| X bio | 160 | ≤ 145 | |
| YouTube title | 100 | ≤ 60 | Only ~60 survive in feed and search. |
| YouTube description | 5 000 | — | First 2 lines show above the fold. |

Volatile — **verify before relying on them**, platforms move these: TikTok
caption length, LinkedIn truncation point, and whether a TikTok bio link is
available on the account (it is gated by account type and follower count).

## Rules

1. **Count, then report.** Every returned string carries its own count as
   `n/limit`. If a count is not shown, it was not checked.
2. **Never pad to fill.** Under target is fine. Padding is how hype gets in.
3. **One asset, one claim per platform.** Not the same sentence reformatted
   five ways — the same claim, argued in the shape each surface rewards.
4. **The hook is rewritten per platform, never reused.** A YouTube title and an
   X first line optimise for different things: search intent versus scroll-stop.
5. **No cross-posted watermarks or platform-native artifacts.** Reposting a
   watermarked TikTok to Reels is downranked.

## Output

Group by platform. For each: the copy, the count, and the asset spec (aspect
ratio, duration) where one applies. Flag anything that had to be cut so hard
the claim changed — that is a signal the claim was too long for the surface,
not that the copy is bad.

## AI disclosure

Any cut containing synthesized narration or generated visuals carries the
platform's native AI-content label. The label is what satisfies policy, not a
line of text in the caption. Never spend bio characters on a disclosure.
