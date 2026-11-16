# Ghost-Crafters

We make behavior packs, add-ons, large builds and server tools for Minecraft, for people who keep a world or a server going for the long haul. Bedrock is our main focus. Java versions follow at a later time, and a few builds already work on both editions from one download.

Most of these projects were built and tested locally before we decided to bring them to GitHub. They're now arriving here as fresh builds, one project at a time, each in its own public repo. The org is mostly empty for now; the list below shows what's on the way.

## Contents

- [What we're building](#what-were-building)
- [Releases and pre-releases](#releases-and-pre-releases)
- [Terms](#terms)
- [Bugs and security](#bugs-and-security)

## What we're building

Packs and add-ons for players:

### Item Magnet

![coming](https://img.shields.io/badge/coming-blue?style=plastic)

[Item Magnet](https://github.com/Ghost-Crafters/item-magnet) pulls dropped items inside your range to you, where they're picked up the normal way, so you stop chasing loot around. Every player sets their own range. Items you throw yourself stay put unless you switch on "Pull items I throw", so dropping things on purpose still works. It's script-only, with no client mod to install, and it runs on a dedicated server or in a local world. XP orbs are pulled the same way. Planned are items that follow you when your inventory is full, item clumping and XP sharing between players.

### Server Teleport

![coming](https://img.shields.io/badge/coming-blue?style=plastic)

[Server Teleport](https://github.com/Ghost-Crafters/server-teleport) gives every player a home button and everyone a hub button. Press yours and you go, along with anyone and any mob within 6 blocks of you, except creepers. Titles, chat messages and sounds play on the way. It's for survival servers where players share a hub and each keep a home. Adding players and changing teleports is done in the Teleport Pack Editor, a Windows app that checks every command before it saves, so a typo can't break a button.

### Blueprint

![in development](https://img.shields.io/badge/in%20development-orange?style=plastic)

[Blueprint](https://github.com/Ghost-Crafters/blueprint) shows a schematic as see-through ghost blocks in your world, one layer at a time. It lists the materials you still need and marks blocks that are missing or wrong. A converter reads Bedrock structure files, Java litematic files and Storage Campus builds. Because Bedrock has no client-only mods, Blueprint is a world add-on: you add it to a world you host, or the server admin installs it and players get the resource pack when they join.

### Hopper Tick

![research](https://img.shields.io/badge/research-lightgrey?style=plastic)

[Hopper Tick](https://github.com/Ghost-Crafters/hopper-tick) is meant to let idle hoppers sleep until something changes next to them, so big storage builds stop costing tick time. Everything else about hoppers has to behave exactly as in vanilla. We're aiming it at Storage Campus first, where one finished world holds 362,533 hoppers in 532 chunks.

Builds for world builders:

### Storage Campus

![coming](https://img.shields.io/badge/coming-blue?style=plastic)

[Storage Campus](https://github.com/Ghost-Crafters/storage-campus) places a mega-storage campus in your world: a hub, storage halls, a port, grounds, the sorting machinery, a dome and a lagoon. It's for players who want a very large storage system without laying out every hall by hand.

### Mega Furnace

![coming](https://img.shields.io/badge/coming-blue?style=plastic)

[Mega Furnace](https://github.com/Ghost-Crafters/mega-furnace) is an automated smelter built inside a furnace block, 48 x 48 x 48 blocks at the scale of the real texture, with the front lit like a burning furnace. It holds 192 smelters in four tiers around a hollow tower: 96 furnaces, 48 smokers and 48 blast furnaces. You drop items into three roof chests and collect the results from 32 barrel stacks in the firebox. Its fuel comes from a kelp farm and a bamboo farm built against its walls, and a master autocrafter room with 56 recipes sits against the west wall.

### Sakura Fishbowl

![coming](https://img.shields.io/badge/coming-blue?style=plastic)

[Sakura Fishbowl](https://github.com/Ghost-Crafters/sakura-fishbowl) is a glass goldfish bowl aquarium 129 blocks across, standing in a cherry grove, with a long glass lab tank beside it for axolotls. The whole build is 227 x 128 x 172 blocks with 226,994 blocks to place and 24,156 water buckets to pour, so it's a project for survival players with time to spare. It comes with a step-by-step guide, and the same build works on Bedrock and Java.

Tools for server owners:

### Bedrock Server Launcher

![coming](https://img.shields.io/badge/coming-blue?style=plastic) ![free for now](https://img.shields.io/badge/free%20for%20now-brightgreen?style=plastic)

[Bedrock Server Launcher](https://github.com/Ghost-Crafters/bedrock-server-launcher) runs Mojang's Bedrock Dedicated Server for you. It restarts the server after a crash, by default after 60 seconds, and refuses a second launcher on the same server. A stop waits for the server to finish saving and never kills one that is still writing. Your terminal stays the server console, and lines starting with `!` go to the launcher. Backups, restore, a nightly restart, installing packs into a world and plugins written in Python come in later releases. The server itself stays Mojang's and stays free.

### Op Commands

![coming](https://img.shields.io/badge/coming-blue?style=plastic)

[Op Commands](https://github.com/Ghost-Crafters/op-commands) is a launcher plugin for worlds that keep their achievements. With cheats off the game disables `/tp`, `/gamemode` and `/give` even for operators, and turning cheats on costs the world its achievements. Op Commands adds operator-only versions that work with cheats off, such as `/opc:tp` and `/opc:gamemode`, plus clear, time, weather, effect, kill and summon. The plugin logs every command an operator runs.

### Server Scripts

![planned](https://img.shields.io/badge/planned-lightgrey?style=plastic)

[Server Scripts](https://github.com/Ghost-Crafters/server-scripts) is a launcher plugin that lets an operator run a script on the server machine from chat. `/scripts:run restart-lobby fast` runs the script `restart-lobby` from the server's `scripts` folder, and its output comes back to that player. Scripts can be shell, PowerShell, batch or Python, and the plugin runs them with a time limit and an output cap. It works with cheats off, on a vanilla Bedrock server.

### Achievement Keeper

![planned](https://img.shields.io/badge/planned-lightgrey?style=plastic)

[Achievement Keeper](https://github.com/Ghost-Crafters/achievement-keeper) is a launcher plugin that keeps a world able to earn the normal Bedrock achievements. On every server start it reads the world's `level.dat`, `server.properties` and pack list, and tells you what would keep achievements off. When something can be cleared, one command stops the server, takes a backup, makes the edit and starts the server again. A world that has already lost achievements may not get them back.

## Releases and pre-releases

Each project's downloads are on its repo's Releases page, next to its guide and changelog.

Pre-releases (alpha, beta and rc) are published there too, for anyone who wants to try what's next and tell us what breaks. If you'd rather wait for the finished release, skip them.

Back up your world before you install anything, and a pre-release especially.

## Terms

Everything here is free to play and to run on your server. The Bedrock Server Launcher is free for now and may become a paid program later.

You're welcome to download any project from its Releases page and use it in your worlds and on servers you run. We keep the rights to the projects and their files, so please don't reupload or mirror them anywhere else. If you want to share a project, share the link to its Releases page. Each repo's LICENSE has the exact terms.

Everything is made within Mojang's EULA and usage guidelines. You need your own copy of Minecraft, and anything that belongs to Mojang or Microsoft stays theirs.

## Bugs and security

Found a bug? Open an issue in that project's repo. Say what you did, what you expected and which version you have.

Security problems go through the repo's Security tab instead, so they stay private until they are fixed. The [security policy](https://github.com/Ghost-Crafters/.github/blob/master/SECURITY.md) says how.

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

[![Back to top](https://img.shields.io/badge/Back%20to%20top-222?style=plastic&logo=github)](#ghost-crafters)
