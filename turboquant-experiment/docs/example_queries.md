# Example Queries and Questions

This file contains example prompts you can try in the Gradio app after loading
the documents from `data/` into the TurboQuant index.

Use the **Search** tab for similarity-search queries and the **Agent (RAG)**
tab for questions that require the `gpt-5.4-nano` model to synthesize an
answer from the retrieved context.

---

## `nebula_station_incident.txt`

A fictional incident report from an orbital research platform.

### Search queries
- "anomalous energy signature near Nebula Station"
- "Dr. Elara Voss incident report"
- "voltage oscillation reactor outage sectors C through F"
- "shimmering distortion spherical object 200 meters"

### Agent questions
- What happened on Nebula Station on 14 March 2147?
- Who witnessed the anomalous object, and what did it look like?
- Why was communication with Kepler-442b lost during the incident?
- What did the survey drone find at the object's last known coordinates?
- What follow-up actions did Commander Voss request?

---

## `evergreen_corp_q3_review.txt`

A confidential internal strategic review for a fictional corporation.

### Search queries
- "Project Thrift cost reduction savings"
- "Solara product line launch delay"
- "Riverstone Analytics acquisition integration"
- "AuroraTech European market discount"

### Agent questions
- How did Evergreen perform in Q3 2026 compared to its growth target?
- What is Project Thrift, and how much money is it expected to save?
- Why was the Solara launch delayed, and what is the new launch window?
- What risks are mentioned regarding product quality?
- What competitive pressure did Evergreen face in Europe?
- When is the executive committee meeting to finalize the Q4 budget?

---

## `asteria_colony_charter.txt`

A fictional governance charter for a space colony.

### Search queries
- "General Assembly two-thirds vote amendment"
- "resource stewardship water quota Council"
- "Council member term limits Asteria"
- "exile colony two-thirds vote crime"

### Agent questions
- What is the purpose of the Asteria Colony Charter?
- How is the colony governed, and who can serve on the Council?
- Can the Charter be amended, and what are the requirements?
- What resources are considered the common heritage of the colony?
- Under what conditions can a resident be exiled?
- What does the Charter say about education for children?

---

## `lumina_tech_product_spec.txt`

An internal hardware specification for a fictional edge inference accelerator.

### Search queries
- "Project Firewheel edge inference accelerator"
- "Ignite TPU tera-operations INT8 FP16"
- "Firewheel power consumption 45 watts"
- "Firewheel Bridge adapter PCIe"

### Agent questions
- What is Project Firewheel, and what environments is it designed for?
- What are the performance specifications of the Ignite TPU?
- How much memory and bandwidth does the Firewheel module have?
- What is the target price and gross margin for Firewheel?
- What are the open issues blocking the project?
- Does Firewheel support PCIe natively? If not, how can a customer use it with PCIe?

---

## Cross-document prompts

Try these after loading all four documents to see how retrieval selects the
right context.

### Search queries
- "incident report 2147"
- "colony governance water quota"
- "product launch delay"
- "space station anomaly"

### Agent questions
- Compare the leadership decisions made by Commander Voss and the Evergreen
  executive committee.
- Which document discusses a delay that affected a product or project timeline?
- What are the rules for removing someone from a group in the Asteria Colony
  Charter, and how does that contrast with the Nebula Station incident response?
