# Leaderboard System Guide

## Overview
The leaderboard system tracks and displays global rankings for all skills across all players.

## Skills Tracked
1. **Mining** - Mining ore from rocks
2. **Woodcutting** - Chopping trees for logs
3. **Fishing** - Catching fish
4. **Cooking** - Cooking raw fish into food
5. **Merchant** - Buying and selling at shops
6. **Athletics** - Swimming and movement

## How to Access
- Press **L** to open/close the leaderboard
- Or navigate with **TAB** to cycle through skill tabs

## Navigation
- **←/→ or TAB**: Switch between skill tabs
- **↑/↓**: Scroll through rankings
- **L or ESC**: Close leaderboard

## Features

### Individual Skill Rankings
- Shows top 50 players for each skill
- Displays:
  - Rank (with gold/silver/bronze medals for top 3)
  - Player name
  - Skill level
  - Total experience
  - Last updated timestamp
- Your current rank is highlighted in gold
- If you're not visible in current scroll, your rank is shown at the bottom

### Overall Rankings
- The "Overall" tab shows total level rankings
- Sum of all 6 skill levels combined
- Great way to see who the most well-rounded players are

### Data Persistence
- Leaderboards are saved to `leaderboards.json`
- Updated when you open the leaderboard
- Automatically saved when you close it
- Also saved when you quit the game

## How Rankings Work

### Ranking Criteria
Rankings are sorted by:
1. **Primary**: Total Experience (higher is better)
2. **Tiebreaker**: Level (higher is better)

### Entry Requirements
- Simply train any skill to appear on the leaderboard
- Your best performance in each skill is tracked
- Rankings update in real-time as you gain experience

### Top 100
- Only the top 100 players per skill are retained
- If you fall out of top 100, your entry is removed
- Keeps leaderboard file size manageable

## Tips
- Train multiple skills to climb the overall rankings
- Check leaderboards regularly to see your progress
- Gold medal (🥇) = Rank 1, Silver (🥈) = Rank 2, Bronze (🥉) = Rank 3
- Your entry is highlighted in yellow/gold for easy spotting

## Technical Details

### Data Storage
- File: `leaderboards.json`
- Format: JSON with skill categories
- Each entry contains:
  - player_name
  - level
  - xp
  - last_updated

### Update Frequency
- On leaderboard open (press L)
- On game exit
- When leaderboard closes

### Privacy
- Only player names are visible (no other personal data)
- Leaderboards are local to your game instance
- To share rankings, share the `leaderboards.json` file

## Troubleshooting

### "No rankings yet!"
- This means no players have trained that skill yet
- Be the first! Train the skill and check back

### Not seeing your rank
- Make sure you've actually gained XP in that skill
- Press L to open leaderboard (this updates your entry)
- Check if you're in the top 100 for that skill

### Leaderboards reset
- If `leaderboards.json` is deleted, all rankings are lost
- Back up this file to preserve rankings
- Leaderboards don't reset on game restart (they persist)

## Future Enhancements
Potential features for future updates:
- Online leaderboards (requires server)
- Leaderboard rewards for top players
- Historical rankings (track changes over time)
- Clan/guild leaderboards
- Fastest time to level 99 leaderboards
- Most total XP gained in 24 hours

## Questions?
The leaderboard system is fully automated - just play the game normally and your progress will be tracked!
