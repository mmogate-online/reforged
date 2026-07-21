## Test log
1. Got first quest from Axelle - Dawn`s Twilight;
2. Delivered it to Lam right before the bridge;
3. Got 10 copper and 100xp reward;
4. Then got 2 quests, Making the Rounds (Story Quest) and Another Fine Mess (Zone Quest);
5. Delivered Anothe Fine Mess quest to Barsabba, got reward 10 copper and 150 xp;
6. Got another quest from Barsabba, "A Bridge Pretty Near";
7. Delivered "A Bridge Pretty Near" quest to Kishale, got 30 copper and 300xp;
8. Still on Kishale the follow-up quest Making the Rounds is telling me to kill 5 Ghilliedhu Claws;
9. Kishale give us another Zone quest Unrest in the Forest, which also ask to kill 5 Ghilliedhu;
10. During the initial hunt on Ghilliedhu the first thing I notice is the balancing, it is not tuned for the weapons revamp the server had, that means we should restore the ATK/DEF/HP balancing these mobs had in this region;
11. Delivered the Unrest in the Forest to Kishale, got 500xp as reward;
12. Kishale follow-up quest appeared, Getting Some Answers, it ask me to kill more 5 Ghilliedhu;
13. Anothe quest appeared from Neely, Hunting the Beasts, asking me to kill Noruks;
14. Delivered, both Making the Rounds (500xp reward) and Getting Some Answers (80 copper and 1x Lucky Egg I) quest to Dulari;
15. Got from Dulari 2 follow-up quests, Essence and Sensibility and Slayer Training zone quests;
16. Talked to Junia to continue the Slayer Training quest;
17. I have noticed Junia quest dialog talk about leaning Whirlwind, but in v92 slayer learns Heart Thrust first, which was an issue we had previously fixed on quests, since other classes had the same issue; Also worth considering if this skill training quest is also accounting for other newer classes like Gunner, Ninja, Brawler and Valkryie;
18. Besides the incorrect dialog the Slayer Training quest seems to be progressing, I talk again with Dulari which asks me to get 5 Nuruk Hide by killing Noruks;
19. I deliver Essence and Sensibility quest to Dulari after killing the requested Ghilliedhu variants, got another Lucky Egg I, 90 copper and 900xp;
20. Another quest appears from Dulari, Garrison in Distress, I take the quest and then a popori called Ramun appears walking towards the camp with an yellow question mark;
21. I'm unable to interact with Ramun, the popori NPC, its displayed position is: 80667 -81177 -4409, continent id 13, reported by the GM tool; My suspicion is a possible desync from client and server data or the correct npc spawning in a different region which is not the one I'm currently at;

22. After fixing Ramun animation, I was able to talk to him which was just a follow-up step in its quest;
23. I delivered the Slayer Training quest to Nivek,  it rewarded me with 05 copper and 50 xp;
24. I delivered the Hunting the Beasts quest to Neziir, it gave me another Lucky Egg I, 90 copper and 900xp;
25. Got another the follow-up step in Neziir quest, Garrison in Distress, which now ask me to collect samples from Sickly Noruks;
26. I have noticed the Story Quest did not get unlocked, I have reached level 5 by now and the Story Quest after Making the Rounds is not unlocked; If I check the quest journal it say i have not received this quest yet; We need to check which NPC give me this quest since I might have missed it.

27. Now the Nivek issue is fixed, the story quest "The Secret Life of Trees" is obtainable from the NPC;
28. I have killed Verkas and delivered the quest to Nivek, which is only a follow-up step in the quest which now ask me to talk to Neziir;
29. Talking to Neziir the quest now point me at Adria to deliver the quest;
30. Along the way I take the quest "The Perfect Cut" from Leolin, which ask me to kill some piglings;
31. I have noticed the quest Garisson in Distress which ask me to Collect serum samples from Sickly Noruks it not working; After killing a few Sickly Noruks the quest is not progressing and I have also noticed that unlike other quests the mob is nor marked with the yellow exclamation mark, which is a hit that the mob might not be correctly tagged in the quest configuration;

32. The Garisson in Distress have been fixed and now I'm able to collect the Serum Samples, it is important to check if we should add this to the datasheet-domain knowledgebase or just consider a DSL bug-fix and move on;
33. I have delivered the Garrison in Distress quest to Ashak and got as reward another Lucky Egg I, 80 copper and 800xp;
34. I have also delivered the quest The Perfect Cut to Leolin, got as reward 500xp;
35. Moving on to Tower Base I got the follow-up task in the story quest a Clue in the Dark from Leander;
36. Also got the zone quest Going Above and Beyond from Adria;
37. I have noticed that when entering the Tower Base section of the map the minimap doesn't show the map anymore and it display as "North Dock"; This might be related to the Area Data changes we conducted from v17 which might be conflicting with v92 assets, if necessary we can check the game assets using the tera-editor project (rfe), see: "D:\dev\mmogate\github\reforged-editor"; Bellow I'll share 2 screenshots, the first one is outside the Tower Base area, which shows the entire IoD minimap, the second screenshot is inside the Tower Base area which the minimap gets blank:
- Z:\Windows Folders\Desktop\img_dump\minimap_iod.png
- Z:\Windows Folders\Desktop\img_dump\minimap_iod_towerbase.png
You might wanna scan our datasheet-domain for more information, if nothing relevant is found you may also search on TERA Ragezone through playwright MCP;

38. I talk to Taras which has the follow-up task for the quest "A Clue in the Dark";
39. I also grab a zone quest from Taras, Horned Horrors;
40. I also grab a zone quest from Jirash, Mana out of Mudmen;
41. I deliver the Mana out of Mudman quest, get 02 silver, 2000xp, bandage, panacea and divine infusion as rewards; It is important to note the bandage and panacea provided as reward in this quest are no longer working on v92, so we need to reenable or repurpose these items; The stamina system was remover from newer versions of the game, that being said we may need to repurpose the panacea potions, maybe allowing them to work as a cleanse consumable to remove debuffs instead; The bandage I think can be fully reinstated since the healing mechanics still functions in the game; For this live testing, repurposing items right now is out of scope, we're going to decide this once we fully validate IoD but this is worth keeping in our backlog;
42. I have also delivered the quest to Taras;
43. Next I'm getting the quest from Milene, Getting to Know the Garrison;
44. Then I talk to Rutgar, which then ask me to talk back to Milene;
45. I use the charm and the quest completes;
Charms are also another thing we should keep our eyes on in the backlog, since only a few charms were manually restored just as a spike test to ensure the system was still functioning in the v92 client, but we actually need a proper research on how the charms worked and fully restore all of them, which may require a research over skill data files and abnormalities relationships;
46. I deliever Getting to Know the Garrison quest back to Milene, which then follow up with another quest, Always After Me Lucky Charms;
47. Then I hit a wall with this quest because it requires me to use Onslaught Charm, which was not one of the charms we restored in our spike and also this quest is now looking duplicated since we already had a step that teaches the player on how to use the charm, this step that used one of the charms we restored was previously introduced in early patches since we didn't provide the full restoration of the charms; 
In a recent change we already fully restored the charms, what we need now is to fix this quest step by adding the Onslaught Charm IV instead of Onslaught Charm I, since the IV can replace a stronger buff just in case the player gets buffer by other charm along the way; Since the new step is already adapted for the new standard we should just remove the Onslaught Charm I step, and replace the Greater Power Charm with the Onslaught Charm IV, since the newer step doesn't require or have any stamina requirement as part of the quest, which is a system already removed from the game.

48. The charm issue was settled on both the core charm mechanics and the quest sequencing as well;
49. I delivered the "Going Above and Beyond" to Kiriya, got Shiny New Greatsword, 10 copper, 100xp;
50. Got 2 zone quests from Jorhon, "Bombs Away" and "Supply and Demand";
51. Bombs Away quest seems to repeat the same quest from "Going Above and Beyond" which requires using bombs on training dummies;
52. Delivering the Bombs Away to Jorhon I get Bomb I, 30 copper and 300xp;
53. Jorhon gives another quest called Climbing through the Ranks;
54. Adria gives now another quest called Academic Theft;
55. Follow-up quest Supply and Demand from Rutgar, which ask us to talk to Gurney;
56. Gurney send us to Lilni which delivers the quest, 10 copper and 100xp as rewards;
57. Academic Theft and Climbing Through the Ranks quests both ask us to kill stonebeak mobs, but currently the map ping/location seems to be lacking when clicking over the mob link, not showing on mini map;
58. After getting the "Traces of Darkness" quest from Leander it asks us to give Magical Power Gauge to Eria, but when clicking over the Eria link in the quest journal no pings or map markers;
Eria was suposed to be at Leander's Outpost but I can't find her anywhere, it could be a regression during spec reapply, client sync issue, maybe another issue related to section/regions;
