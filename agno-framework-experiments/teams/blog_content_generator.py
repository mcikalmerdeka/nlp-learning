import os
from pathlib import Path
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.tools.exa import ExaTools

# Load the environment variables and configure the OpenAI API key
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")    
EXA_API_KEY = os.getenv("EXA_API_KEY")

if not OPENAI_API_KEY or not EXA_API_KEY:
    raise ValueError("OPENAI_API_KEY and EXA_API_KEY must be set")

# Create individual specialized agents
researcher = Agent(
    name="Researcher",
    role="Expert at finding information",
    tools=[ExaTools(api_key=EXA_API_KEY)],
    model=OpenAIChat(id="gpt-5-mini", api_key=OPENAI_API_KEY)
)

writer = Agent(
    name="Writer",
    role="Expert at writing clear, engaging medium blog post content",
    model=OpenAIChat(id="gpt-5-mini", api_key=OPENAI_API_KEY)
)

# Create a team with agents to create medium blog post content
content_team = Team(
    name="Content Team",
    members=[researcher, writer],
    instructions="You are a team of researchers and writers that work together to create high-quality medium blog post content.",
    model=OpenAIChat(id="gpt-5-mini", api_key=OPENAI_API_KEY),
    show_members_responses=True,
    markdown=True
)

# Run the team with a task
content_team.print_response("Create a short article about quantum computing", stream=True)

# Output:

# (.venv) PS E:\NLP Learning\NLP-Learning\agno-framework-experiments> uv run .\teams\linkedin_content.py
# ┏━ Message ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                                                                                                                     ┃
# ┃ Create a short article about quantum computing                                                                                                                                      ┃
# ┃                                                                                                                                                                                     ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Researcher Tool Calls ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                                                                                                                     ┃
# ┃ • search_exa(query=quantum computing 2025 state of the field quantum advantage 2024 2025 milestones Google IBM                                                                      ┃
# ┃   IonQ Quantinuum 2025 breakthroughs, num_results=5)                                                                                                                                ┃
# ┃                                                                                                                                                                                     ┃
# ┃ • search_exa(query=quantum advantage 2023 2024 2025 demonstration IonQ 2024 2025 quantum advantage experiments                                                                      ┃
# ┃   'quantum advantage' paper 2024 'quantum supremacy' update 2024, num_results=10)                                                                                                   ┃
# ┃                                                                                                                                                                                     ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Researcher Response ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                                                                                                                     ┃
# ┃ Fact sheet — Quantum computing (for a short article)                                                                                                                                ┃
# ┃                                                                                                                                                                                     ┃
# ┃  1 Brief up-to-date summary (4–6 sentences) Quantum computing is a form of information processing that uses quantum-mechanical effects — chiefly superposition and entanglement —   ┃
# ┃    to represent and transform information. Instead of classical bits that are either 0 or 1, quantum bits (qubits) can exist in combinations of 0 and 1 simultaneously and be       ┃
# ┃    correlated in ways impossible for classical systems, enabling new algorithmic approaches. Today’s field is in the noisy-intermediate-scale-quantum (NISQ) era: hardware qubit    ┃
# ┃    counts and gate fidelities have steadily improved across platforms (superconducting circuits, trapped ions, neutral atoms, photonics), but error rates remain high enough that   ┃
# ┃    large-scale fault-tolerant machines do not yet exist. Researchers and companies are pursuing hybrid quantum–classical algorithms and domain-specific demonstrations that may     ┃
# ┃    show practical advantage for narrowly defined problems before universal fault-tolerant quantum computers become available. Broad, general-purpose quantum computing with         ┃
# ┃    reliable error correction is widely expected to require substantial further advances and likely years (often estimated as a decade or more), but near-term application-specific  ┃
# ┃    gains are plausible.                                                                                                                                                             ┃
# ┃  2 Short explanations of key concepts (1–2 sentences each)                                                                                                                          ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • Qubit: A qubit is the quantum analogue of a bit — a two-level quantum system (e.g., an ion, superconducting circuit, photon polarization) that can encode 0, 1, or any quantum   ┃
# ┃    superposition of both.                                                                                                                                                           ┃
# ┃  • Superposition: Superposition means a qubit can be in a combination of basis states at once (roughly “partly 0 and partly 1”), which lets quantum processors explore multiple     ┃
# ┃    possibilities simultaneously in certain computations.                                                                                                                            ┃
# ┃  • Entanglement: Entanglement is a strong quantum correlation between qubits where the state of one immediately constrains the state of another, enabling nonclassical coordination ┃
# ┃    essential to many quantum algorithms.                                                                                                                                            ┃
# ┃  • Quantum gates: Quantum gates are controlled, reversible operations that change qubit states (like logic gates for classical computers) — sequences of gates form quantum         ┃
# ┃    circuits that implement algorithms.                                                                                                                                              ┃
# ┃  • Quantum supremacy / quantum advantage: “Quantum supremacy” originally meant a quantum device performing a computation infeasible for any classical computer; “quantum advantage” ┃
# ┃    is a more practical term referring to a quantum system delivering a meaningful, demonstrable benefit (speed, quality, or cost) over the best classical methods for a useful      ┃
# ┃    task.                                                                                                                                                                            ┃
# ┃                                                                                                                                                                                     ┃
# ┃  3 Current state of the field and near-term expectations (2–3 sentences) Hardware progress over recent years has increased qubit counts, gate fidelities, and system                ┃
# ┃    programmability, and firms and labs now offer cloud access and domain-specific pilot projects. Near-term realistic expectations are targeted, problem-specific demonstrations of ┃
# ┃    advantage (e.g., in optimization, chemistry simulations, or sampling tasks) using hybrid algorithms on NISQ devices, plus commercial pilot use-cases; however, broad             ┃
# ┃    fault-tolerant quantum computing that outperforms classical systems across many applications remains a longer-term goal. Investors and governments are accelerating funding and  ┃
# ┃    partnerships, so commercialization of narrow, high-value applications could accelerate in the next few years while fundamental engineering challenges are addressed.             ┃
# ┃  4 Top 5 potential applications (one line each, with reason)                                                                                                                        ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • Quantum chemistry and drug discovery — more accurate simulation of molecular electronic structure could speed design of drugs, catalysts, and batteries.                         ┃
# ┃  • Optimization (logistics, supply chains, finance) — quantum algorithms (or hybrid approaches) may find higher-quality solutions faster for large combinatorial problems.          ┃
# ┃  • Materials design and discovery — simulate materials and condensed-matter systems that are intractable classically to enable new superconductors, photovoltaics, or catalysts.    ┃
# ┃  • Cryptography and cybersecurity — large, fault-tolerant quantum computers could break widely used public-key schemes (e.g., RSA), motivating both risk assessments and deployment ┃
# ┃    of quantum-resistant cryptography.                                                                                                                                               ┃
# ┃  • Quantum sensing and metrology — quantum devices can improve precision in timing, magnetic/acceleration sensing, and imaging beyond classical limits for navigation and           ┃
# ┃    scientific measurements.                                                                                                                                                         ┃
# ┃                                                                                                                                                                                     ┃
# ┃  5 Major challenges and limitations (3–5 bullets)                                                                                                                                   ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • Decoherence and error rates: qubits are fragile and lose quantum information quickly; current gate fidelities require extensive error mitigation or correction.                  ┃
# ┃  • Scalability and engineering complexity: connecting, controlling, and cooling millions of high-quality qubits (or otherwise scaling architectures) remains a major                ┃
# ┃    systems-engineering challenge.                                                                                                                                                   ┃
# ┃  • Error correction overhead: known fault-tolerant schemes require large numbers of physical qubits per logical qubit, raising resource demands by orders of magnitude.             ┃
# ┃  • Limited algorithms and problem fit: only a subset of problems are known to benefit from quantum speedups, and identifying practical, near-term use-cases remains nontrivial.     ┃
# ┃  • Competition from classical improvements: advances in classical algorithms, HPC, and specialized hardware may push out or reduce windows of quantum advantage.                    ┃
# ┃                                                                                                                                                                                     ┃
# ┃  6 Simple analogies/metaphors for a general reader                                                                                                                                  ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • Qubit as a spinning coin: a classical bit is like a coin lying heads or tails; a qubit in superposition is like a coin spinning in the air — it’s not just heads or tails until  ┃
# ┃    you “look” (measure).                                                                                                                                                            ┃
# ┃  • Entanglement like matched gloves in sealed boxes: two entangled boxes always yield results that match in a correlated way even when separated, unlike two independent dice.      ┃
# ┃  • Quantum computation as a choir vs. solo singer: classical computing is one singer singing a single melody (one path at a time); quantum computing is like a choir harmonizing    ┃
# ┃    many notes at once, letting the combination produce effects you can’t get from any single voice.                                                                                 ┃
# ┃                                                                                                                                                                                     ┃
# ┃  7 Suggested reputable sources to cite                                                                                                                                              ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • “Quantum supremacy using a programmable superconducting processor,” Google AI Quantum and collaborators (Nature, 2019). https://www.nature.com/articles/s41586-019-1666-5        ┃
# ┃  • “The Year of Quantum: From concept to reality in 2025,” Henning Soller et al., McKinsey & Company (2025 report).                                                                 ┃
# ┃    https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/the-year-of-quantum-from-concept-to-reality-in-2025                                                               ┃
# ┃  • “Progress in Trapped-Ion Quantum Simulation,” Michael Foss-Feig et al., arXiv:2409.02990 (2024). https://arxiv.org/abs/2409.02990                                                ┃
# ┃                                                                                                                                                                                     ┃
# ┃ If you’d like, I can (a) shorten this further to a single-page handout, (b) produce a one-paragraph “lede” for the article using these facts, or (c) provide a few quick quotes you ┃
# ┃ can attribute to public organizations. Which would help next?                                                                                                                       ┃
# ┃                                                                                                                                                                                     ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Writer Response ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                                                                                                                     ┃
# ┃ Quantum computing matters because it promises to tackle problems that are effectively out of reach for today’s computers — from designing new medicines to optimizing complex       ┃
# ┃ logistics — by using the strange rules of quantum physics to explore many possibilities at once.                                                                                    ┃
# ┃                                                                                                                                                                                     ┃
# ┃ What is quantum computing? Think of a quantum computer as a different kind of engine: instead of classical bits (0 or 1), it uses quantum bits that follow quantum mechanics.       ┃
# ┃ Rather than replacing classical machines overnight, quantum computers are specialized tools best suited for particular hard tasks where their physics-based approach gives an edge. ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Key concepts, simply                                                                                                                                                                ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • Qubit: a quantum bit that can be 0, 1, or both at once — like a spinning coin that hasn’t landed yet.                                                                            ┃
# ┃  • Superposition: the ability of a qubit to hold multiple possibilities simultaneously, enabling a quantum computer to explore many options in parallel.                            ┃
# ┃  • Entanglement: a quantum link between qubits so that measuring one instantly affects the other, even when apart — like a pair of perfectly synchronized dice that always show     ┃
# ┃    matching patterns. These properties let quantum programs combine and amplify good answers while cancelling bad ones.                                                             ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Current state and realistic near-term expectations Quantum hardware has moved from lab curiosities to noisy, intermediate devices with tens to a few hundred qubits. We’re not at   ┃
# ┃ universal, error-free quantum computers yet. In the next 3–10 years expect steady improvements: better qubit quality, hybrid algorithms that pair classical and quantum processing, ┃
# ┃ and niche “quantum advantage” demonstrations for specific tasks rather than sweeping breakthroughs.                                                                                 ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Top applications and challenges Promising areas include materials and drug discovery, optimization for logistics and finance, and simulating chemistry and physics. Major           ┃
# ┃ challenges are error rates, scaling up qubit counts, and developing algorithms that deliver real-world benefits. Progress will be incremental and often collaborative across        ┃
# ┃ hardware, software, and theory — like building an orchestra where each instrument must be finely tuned to play together.                                                            ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Takeaway Quantum computing is a powerful, emerging tool that won’t replace classical computers but could transform select industries by solving problems they cannot. Expect        ┃
# ┃ steady, practical advances rather than overnight miracles.                                                                                                                          ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Sources                                                                                                                                                                             ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • "What is quantum computing?" — IBM (IBM Research). https://www.ibm.com/topics/quantum-computing                                                                                  ┃
# ┃  • "Quantum information science" — NIST (National Institute of Standards and Technology). https://www.nist.gov/quantum-information-science                                          ┃
# ┃  • "What is quantum computing?" — Microsoft Azure Quantum (Microsoft). https://learn.microsoft.com/azure/quantum/overview-what-is-quantum-computing                                 ┃
# ┃                                                                                                                                                                                     ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Team Tool Calls ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                                                                                                                     ┃
# ┃ • delegate_task_to_member(member_id=researcher, task=Research and produce a concise fact-sheet to support a                                                                         ┃
# ┃   short article about quantum computing. Include: 1) A 4–6 sentence up-to-date summary of what quantum                                                                              ┃
# ┃   computing is, 2) Brief explanations (1–2 sentences each) of the key concepts: qubit, superposition,                                                                               ┃
# ┃   entanglement, quantum gates, and quantum supremacy/advantage, 3) Current state-of-the-field (2–3 sentences)                                                                       ┃
# ┃   with realistic near-term expectations, 4) Top 5 potential applications (one line each) with brief reasons,                                                                        ┃
# ┃   5) Major challenges and limitations (3–5 bullet points), 6) 2–3 simple analogies or metaphors that help a                                                                         ┃
# ┃   general reader understand quantum concepts, and 7) 3 suggested reputable sources or references to cite                                                                            ┃
# ┃   (title, author/organization, and URL if available). Output should be clear, factual, and suitable for a                                                                           ┃
# ┃   general audience. Do not write the final article—just the research content to be used by the writer.)                                                                             ┃
# ┃                                                                                                                                                                                     ┃
# ┃ • delegate_task_to_member(member_id=writer, task=Using the research fact-sheet provided by the Researcher,                                                                          ┃
# ┃   write a short, engaging article about quantum computing for a general audience (suitable for Medium).                                                                             ┃
# ┃   Requirements: keep it concise (about 300–450 words), clear and friendly tone, include a strong lede (1–2                                                                          ┃
# ┃   sentences) that explains why quantum computing matters, 3–5 short body paragraphs covering: what quantum                                                                          ┃
# ┃   computing is, key concepts (qubit, superposition, entanglement) explained simply, current state and                                                                               ┃
# ┃   realistic near-term expectations, and top applications and challenges. Add 2 simple analogies/metaphors                                                                           ┃
# ┃   within the article to help understanding. End with a short 2–3 line takeaway and include 3 suggested                                                                              ┃
# ┃   reputable sources as citations (use titles and organizations/author and URLs). Format the output in                                                                               ┃
# ┃   Markdown. Do not include the research fact-sheet itself in the article; synthesize it into the article                                                                            ┃
# ┃   content.)                                                                                                                                                                         ┃
# ┃                                                                                                                                                                                     ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Response (110.9s) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                                                                                                                     ┃
# ┃ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┃
# ┃ ┃                                                                Quantum Computing: What It Is and Why It Matters                                                                 ┃ ┃
# ┃ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Quantum computing matters because it promises to tackle problems that are effectively out of reach for today’s computers — from designing new medicines to optimizing complex       ┃
# ┃ logistics — by using the strange rules of quantum physics to explore many possibilities at once.                                                                                    ┃
# ┃                                                                                                                                                                                     ┃
# ┃ What is quantum computing? Think of a quantum computer as a different kind of engine: instead of classical bits (0 or 1), it uses quantum bits that follow quantum mechanics.       ┃
# ┃ Rather than replacing classical machines overnight, quantum computers are specialized tools best suited for particular hard tasks where their physics-based approach gives an edge. ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Key concepts, simply                                                                                                                                                                ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • Qubit: a quantum bit that can be 0, 1, or both at once — like a spinning coin that hasn’t landed yet.                                                                            ┃
# ┃  • Superposition: the ability of a qubit to hold multiple possibilities simultaneously, enabling a quantum computer to explore many options in parallel.                            ┃
# ┃  • Entanglement: a quantum link between qubits so that measuring one instantly affects the other, even when apart — like a pair of perfectly synchronized dice that always show     ┃
# ┃    matching patterns. These properties let quantum programs combine and amplify good answers while cancelling bad ones.                                                             ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Current state and realistic near-term expectations Quantum hardware has moved from lab curiosities to noisy, intermediate devices with tens to a few hundred qubits. We’re not at   ┃
# ┃ universal, error-free quantum computers yet. In the next several years expect steady improvements: better qubit quality, hybrid algorithms that pair classical and quantum          ┃
# ┃ processing, and niche “quantum advantage” demonstrations for specific tasks rather than sweeping breakthroughs. Progress will be iterative, driven by improvements in hardware,     ┃
# ┃ software, and co-design with real-world problems.                                                                                                                                   ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Top applications and challenges Promising areas include materials and drug discovery, optimization for logistics and finance, and simulating chemistry and physics — tasks where    ┃
# ┃ simulating quantum systems or exploring huge option spaces gives a natural fit. Major challenges are error rates and decoherence, the difficulty of scaling up qubit counts, and    ┃
# ┃ the algorithmic work needed to find practical, real-world uses. Building useful quantum systems will be like assembling an orchestra where each instrument must be finely tuned to  ┃
# ┃ play together.                                                                                                                                                                      ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Takeaway Quantum computing is a powerful, emerging tool that won’t replace classical computers but could transform select industries by solving problems they cannot. Expect        ┃
# ┃ steady, practical advances rather than overnight miracles.                                                                                                                          ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Sources                                                                                                                                                                             ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • "What is quantum computing?" — IBM (IBM Research). https://www.ibm.com/topics/quantum-computing                                                                                  ┃
# ┃  • "Quantum information science" — NIST (National Institute of Standards and Technology). https://www.nist.gov/quantum-information-science                                          ┃
# ┃  • "What is quantum computing?" — Microsoft Azure Quantum (Microsoft). https://learn.microsoft.com/azure/quantum/overview-what-is-quantum-computing                                 ┃
# ┃                                                                                                                                                                                     ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
