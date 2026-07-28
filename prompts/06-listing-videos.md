# Listing Videos

*photos in, branded property tour out*

**Replaces:** listing video services ($150-400/video)
**Runs at:** `localhost:7306`

Paste this into [Claude Code](https://claude.com/claude-code). It installs what it needs.

```
Make a listing tour video from the photos in [FOLDER]. Address [X], price [Y],
agent [NAME / PHONE / BROKERAGE]. Vertical 1080x1920.

1. LOOK at the photos and identify what room each one shows first.
2. Order them as a WALK, not as the MLS exported them: exterior, entry, main
   living, kitchen (two shots if you have two good angles), dining, primary bed,
   primary bath, secondary rooms, backyard. Never cut back to an exterior
   mid-tour. Never put a bathroom right after a kitchen. Cut anything past 12
   shots, starting with laundry, garage, hallways, closets. Show me the order.
3. Slow move on each - push in on hero rooms, pull out on reveals. Never the same
   motion three times running. 3.2s per shot, 0.6s crossfade.
4. Open on a card with address + price, end on the agent's details.
5. HARD RULE: describe the property ONLY. Never "perfect for families", "safe
   neighborhood", "great schools" - that's Fair Housing language and it is the
   agent's legal liability. Never state a fact I didn't give you: no square
   footage, no year built, no "recently renovated".
6. Read the phone number back to me digit by digit before exporting.

Then wrap it in a local web app on localhost:7306.
```

---

[← all seven prompts](../README.md)
