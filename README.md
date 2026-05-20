ALGaE 🧠✨

Artificial Language Generator and Expression

ALGaE is a fully local, multi-modal AI appliance designed to bring a large language model to life through a dynamic, physical-feeling interface. It bridges the gap between a text-based AI and an interactive entity by giving the AI a responsive 3D visual representation, persistent memory, and environmental awareness.

Built around the Gemma 4 model, ALGaE is engineered to run entirely locally. This ensures complete privacy and low latency while maintaining high-end visual and conversational capabilities.

📖 Table of Contents

The Vision

Core Components

1. The Expression (Visualizer)

2. The Generator (AI Brain)

3. Persistent Memory

Hardware & Architecture

🔭 The Vision

The goal of ALGaE is to create an AI that feels present in the room. Instead of typing into a chatbox, users interact with a visual entity that clearly communicates its internal state.

When it listens, the visualizer reacts. When it thinks, it visually processes. When it uses its camera tools, it actively "looks" at the user.

⚙️ Core Components

1. The Expression (Visualizer)

The visual front-end is a custom-built WebGL 3D point cloud running on Three.js. It acts as the "face" of ALGaE, running in a full-screen kiosk mode.

Dynamic States: The point cloud fluidly morphs between different mathematical shapes and color gradients based on what the AI is doing (Idle, Listening, Thinking, Speaking, Updating).

Spatial Awareness: In the "Watching" state, the cloud flattens into a lens with a roaming "pupil" that actively tracks. It comes complete with a Picture-in-Picture (PiP) feed of what the AI is currently seeing through its camera.

Immersive Design: The visualizer uses a deep cosmic color palette inspired by modern AI aesthetics, floating in a dark 3D environment.

2. The Generator (AI Brain)

The intelligence of ALGaE is powered by a local LLM stack, designed for maximum efficiency.

Gemma 4: Utilizes quantized Gemma 4 models (including vision variants) via Ollama, which is optimized for hardware-accelerated CPU inference.

Multi-Modal Inputs: Capable of processing voice commands (wake words and speech-to-text) and analyzing live camera feeds.

Tool Calling: The AI can actively trigger system tools. This includes controlling its own visual interface, checking system temperatures, or fetching live data.

3. Persistent Memory

ALGaE is designed to remember past interactions. It uses an SQLite database stored securely on the host machine.

Conversations and context are saved across reboots and system updates.

The memory system allows the AI to recall past interactions, making it feel like a consistent companion rather than a stateless chatbot.

Memory can be managed and cleared by the user via direct voice commands.

🖥️ Hardware & Architecture

ALGaE is built to be a standalone appliance. The primary development and deployment target is an Ubuntu Server running on a highly efficient micro-PC (like the Lenovo M70q Gen 2).

The architecture is split into two main parts. First, a robust Python back-end manages the AI, memory, and hardware interfaces (camera, microphones). Second, a lightweight web server drives the 3D visualizer on a connected large-format display.