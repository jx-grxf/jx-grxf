<div align="center">

# Johannes Grof

**I build native macOS and iOS apps, developer tools, and the backends behind them.**

Austria · HTBLA Kaindorf an der Sulm · Swift · TypeScript · Rust

[![Website](https://img.shields.io/badge/johannesgrof.me-000000?style=for-the-badge&logo=astro&logoColor=white)](https://johannesgrof.me)
[![X](https://img.shields.io/badge/@jx__grxf-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/johannesgrofdev)
[![LinkedIn](https://img.shields.io/badge/Johannes_Grof-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/johannes-grof)
[![Email](https://img.shields.io/badge/contact@johannesgrof.me-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:contact@johannesgrof.me)

</div>

---

## Currently building — ÖffiGo

> **A truly native public transport app for all of Austria.** Real-time departures, journey
> planning, live vehicle positions and disruptions — on iOS (SwiftUI), Android (Jetpack Compose)
> and Apple Watch, backed by my own TypeScript BFF.
>
> Primary data source: **Verkehrsauskunft Österreich (VAO)** - the national mobility data
> platform behind Austria's official transit apps.
>
> **[oeffigo.app](https://oeffigo.app)** · closed TestFlight beta · Android in development

<div align="center">

`SwiftUI` · `Jetpack Compose` · `TypeScript` · `Supabase` · `Redis` · `Cloudflare` · `Railway` · `Live Activities` · `Apple Intelligence`

</div>

---

## What I build

```mermaid
graph TD
    ME(("Johannes Grof"))

    ME --> MAC["🖥️ Native macOS &amp; iOS<br/>Swift · SwiftUI · AppKit"]
    ME --> AGT["🤖 Agent &amp; Dev Tooling<br/>Rust · TypeScript"]
    ME --> NET["🌐 Backend, Networking &amp; CLI<br/>TypeScript · Python · Rust"]

    MAC --> OG["ÖffiGo"]
    MAC --> BE["BriskEdit"]
    MAC --> PO["poise"]
    MAC --> NT["NotchTray"]
    MAC --> BL["BottleLite"]
    MAC --> MP["MacPhone"]
    MAC --> CC["CCrab"]

    AGT --> PP["PatchPilot"]
    AGT --> AP["agent-presence"]
    AGT --> CSB["claude-swap-bar"]
    AGT --> HK["HealthKit-MCP"]

    NET --> TO["Tools"]
    NET --> IP["ip-multitool"]
    NET --> CR["Caruso-Reborn"]
    NET --> STD["scooter-tuning-db"]
```

---

## macOS apps

| Project | Tech | What it does |
|:---|:---|:---|
| ✏️ **[BriskEdit](https://github.com/jx-grxf/BriskEdit)** | ![Swift](https://img.shields.io/badge/Swift-FA7343?logo=swift&logoColor=white) ![SwiftUI](https://img.shields.io/badge/SwiftUI-0A84FF?logo=swift&logoColor=white) | Native developer text editor. SwiftUI + AppKit, TextKit 2, Swift 6 — built against the Electron VS Code experience. |
| 🧍 **[poise](https://github.com/jx-grxf/poise)** | ![Swift](https://img.shields.io/badge/Swift-FA7343?logo=swift&logoColor=white) ![CoreMotion](https://img.shields.io/badge/CoreMotion-333333?logo=apple&logoColor=white) | Turns your AirPods into a posture coach using their motion sensors. No camera, no cloud, fully on-device. |
| 📲 **[NotchTray](https://github.com/jx-grxf/NotchTray)** | ![Swift](https://img.shields.io/badge/Swift-FA7343?logo=swift&logoColor=white) ![AppKit](https://img.shields.io/badge/AppKit-333333?logo=apple&logoColor=white) | Finds menu bar items hidden behind the MacBook notch and surfaces them in a Dynamic Island-style panel. |
| 🍾 **[BottleLite](https://github.com/jx-grxf/BottleLite)** | ![Swift](https://img.shields.io/badge/Swift-FA7343?logo=swift&logoColor=white) ![Wine](https://img.shields.io/badge/Wine-722F37?logo=wine&logoColor=white) | Lightweight open-source macOS runner for Windows apps. |
| 🔀 **[claude-swap-bar](https://github.com/jx-grxf/claude-swap-bar)** | ![Swift](https://img.shields.io/badge/Swift-FA7343?logo=swift&logoColor=white) ![Sparkle](https://img.shields.io/badge/Sparkle-5E5CE6?logo=apple&logoColor=white) | Switch between Claude Code accounts from the menu bar, with live per-window usage meters. |
| 🦀 **[CCrab](https://github.com/jx-grxf/CCrab)** | ![Swift](https://img.shields.io/badge/Swift-FA7343?logo=swift&logoColor=white) ![AppKit](https://img.shields.io/badge/AppKit-333333?logo=apple&logoColor=white) | Desktop companion for Claude Code. Live session state on a floating panel and usage limits in the menu bar, at **0.0% idle CPU** — Core Animation owns the timeline, so there is no draw loop. |
| 📱 **[MacPhone](https://github.com/jx-grxf/MacPhone)** | ![Swift](https://img.shields.io/badge/Swift-FA7343?logo=swift&logoColor=white) ![CoreBluetooth](https://img.shields.io/badge/CoreBluetooth-0082FC?logo=bluetooth&logoColor=white) | macOS device lab that bridges a *real* BLE device into an Android emulator's virtual controller. |

---

## Developer &amp; agent tooling

| Project | Tech | What it does |
|:---|:---|:---|
| 🦀 **[agent-presence](https://github.com/jx-grxf/agent-presence)** | ![Rust](https://img.shields.io/badge/Rust-000000?logo=rust&logoColor=white) ![macOS](https://img.shields.io/badge/-000000?logo=apple&logoColor=white) ![Windows](https://img.shields.io/badge/-0078D6?logo=windows&logoColor=white) ![Linux](https://img.shields.io/badge/-FCC624?logo=linux&logoColor=black) | Discord Rich Presence for Claude Code and Codex. One ~1.5 MB static binary, no bot token, privacy-safe defaults. |
| 🛠️ **[PatchPilot](https://github.com/jx-grxf/PatchPilot)** | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white) ![Ollama](https://img.shields.io/badge/Ollama-000000?logo=ollama&logoColor=white) | Local-first terminal coding agent. Inspect, plan and apply changes with explicit permissions for every file write and shell command. |
| ❤️ **[HealthKit-MCP](https://github.com/jx-grxf/HealthKit-MCP)** | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white) ![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?logo=supabase&logoColor=white) | Read-only MCP bridge for Apple Health — sleep, workouts and training load for any MCP-capable agent. |
| 🧰 **[ip-multitool](https://github.com/jx-grxf/ip-multitool)** | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) | Terminal toolkit for IP intelligence, DNS/RDAP, HTTP checks, subnet math and authorized network diagnostics. |

---

## Web, hardware &amp; open data

| Project | Tech | What it does |
|:---|:---|:---|
| 🌐 **[johannesgrof.me](https://github.com/jx-grxf/johannesgrof.me)** | ![Astro](https://img.shields.io/badge/Astro-BC52EE?logo=astro&logoColor=white) ![Vercel](https://img.shields.io/badge/Vercel-000000?logo=vercel&logoColor=white) | My portfolio and project site. Bilingual (EN/DE), static, fast. |
| 🧾 **[Tools](https://github.com/jx-grxf/tools)** | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white) | Merge, split, rotate and convert PDFs and images entirely in the browser — no upload, no account. Live at **[tools.johannesgrof.me](https://tools.johannesgrof.me)**. |
| 📻 **[Caruso-Reborn](https://github.com/jx-grxf/Caruso-Reborn)** | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white) ![Electron](https://img.shields.io/badge/Electron-47848F?logo=electron&logoColor=white) | Brings internet radio and modern sources back to first-generation T+A Caruso hi-fi systems over UPnP. |
| 🛴 **[scooter-tuning-db](https://github.com/jx-grxf/scooter-tuning-db)** | ![Markdown](https://img.shields.io/badge/Docs-000000?logo=markdown&logoColor=white) ![BLE](https://img.shields.io/badge/BLE-0082FC?logo=bluetooth&logoColor=white) | Open, community-reverse-engineered BLE register and tuning map database for e-scooters. |

---

## Coming soon

| Project | Tech | Status |
|:---|:---|:---|
| 🧰 **PortPirate** | ![Swift](https://img.shields.io/badge/Swift-FA7343?logo=swift&logoColor=white) | macOS menu bar control center for local dev ports — maps every listener to its process and repo. |
| ⌨️ **TypeBot** | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white) ![Playwright](https://img.shields.io/badge/Playwright-2EAD33) | Stay tuned 👀 |

---

<details>
<summary><b>📦 Archive</b> — unmaintained projects &amp; forks</summary>

<br>

> [!NOTE]
> These repositories are no longer maintained. They stay public for reference,
> but expect no fixes, releases, or support.

| Project | Tech | Description |
|:---|:---|:---|
| 🔊 [SlamX](https://github.com/jx-grxf/SlamX) | ![Swift](https://img.shields.io/badge/Swift-FA7343?logo=swift&logoColor=white) | Want to make your MacBook scream? Fan and thermal control experiment. |
| 📄 [DocxToPDF](https://github.com/jx-grxf/DocxToPDF) | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white) | Batch convert DOCX to PDF on macOS via Word and AppleScript. |
| 🎧 [Hermes-Discord-Voice](https://github.com/jx-grxf/Hermes-Discord-Voice) | ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white) | Discord voice bridge for Hermes Agent. |
| 📡 [arduino-distance-alarm](https://github.com/jx-grxf/arduino-distance-alarm) | ![Arduino](https://img.shields.io/badge/Arduino-00979D?logo=arduino&logoColor=white) | Distance measurement with a local web dashboard. |
| 📚 [EBookToPDF](https://github.com/jx-grxf/EBookToPDF) *(fork)* | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) | Ebook to PDF conversion utility. |

</details>

---

## Stack

**Languages**

[![Languages](https://skillicons.dev/icons?i=swift,ts,js,rust,py,kotlin,c,java&theme=dark)](https://skillicons.dev)

**Platforms &amp; frameworks**

[![Platforms](https://skillicons.dev/icons?i=apple,nodejs,astro,tailwind,electron&theme=dark)](https://skillicons.dev)

![SwiftUI](https://img.shields.io/badge/SwiftUI-0A84FF?style=flat-square&logo=swift&logoColor=white)
![Jetpack Compose](https://img.shields.io/badge/Jetpack_Compose-4285F4?style=flat-square&logo=jetpackcompose&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-111827?style=flat-square)

**Infrastructure &amp; services**

[![Infra](https://skillicons.dev/icons?i=supabase,postgres,redis,cloudflare,vercel,aws,docker,linux&theme=dark)](https://skillicons.dev)

![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white)
![App Store Connect](https://img.shields.io/badge/App_Store_Connect-0D96F6?style=flat-square&logo=appstore&logoColor=white)
![TestFlight](https://img.shields.io/badge/TestFlight-0D96F6?style=flat-square&logo=apple&logoColor=white)
![Sparkle](https://img.shields.io/badge/Sparkle-5E5CE6?style=flat-square)

**Tooling**

[![Tooling](https://skillicons.dev/icons?i=git,github,bash,vscode&theme=dark)](https://skillicons.dev)

![Xcode](https://img.shields.io/badge/Xcode-147EFB?style=flat-square&logo=xcode&logoColor=white)
![Tuist](https://img.shields.io/badge/Tuist-6236FF?style=flat-square)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat-square)

---

<div align="center">

![Stats](https://github-stats-extended.vercel.app/api?username=jx-grxf&show_icons=true&hide_border=true&theme=dark&card_width=450)

</div>

---

<div align="center">

**Available for freelance work** — websites, small tools and automation, IT support.
On-site in south-east Styria, remote across Austria.

[johannesgrof.me](https://johannesgrof.me) · [contact@johannesgrof.me](mailto:contact@johannesgrof.me)

</div>
