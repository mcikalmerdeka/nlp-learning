import os
from dotenv import load_dotenv

from agno.agent import Agent
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.openai import OpenAIChat
from agno.vectordb.pgvector import PgVector, SearchType

# Load the environment variables and configure the OpenAI API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the chat model and embedding model
chat_model = OpenAIChat(id="gpt-5-mini", api_key=openai_api_key)
embedding_model = OpenAIEmbedder(id="text-embedding-3-small", api_key=openai_api_key)

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
knowledge = Knowledge(
    # Use PgVector as the vector database and store embeddings in the `ai.recipes` table
    vector_db=PgVector(
        table_name="recipes",
        db_url=db_url,
        search_type=SearchType.hybrid,
        embedder=embedding_model,
    ),
)

knowledge.add_content(
    url="https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"
)

agent = Agent(
    model=chat_model,
    knowledge=knowledge,
    search_knowledge=True,
    markdown=True,
)

if __name__ == "__main__":
    agent.print_response(
        "How do I make chicken and galangal in coconut milk soup", stream=True
    )

# # Pull and start the docker container for pgvector first
# docker run -d `
#   -e POSTGRES_DB=ai `
#   -e POSTGRES_USER=ai `
#   -e POSTGRES_PASSWORD=ai `
#   -e PGDATA=/var/lib/postgresql/data/pgdata `
#   -v pgvolume:/var/lib/postgresql/data `
#   -p 5532:5432 `
#   --name pgvector `
#   agnohq/pgvector:16

# One liner: 
# docker run -d -e POSTGRES_DB=ai -e POSTGRES_USER=ai -e POSTGRES_PASSWORD=ai -e PGDATA=/var/lib/postgresql/data/pgdata -v pgvolume:/var/lib/postgresql/data -p 5532:5432 --name pgvector agnohq/pgvector:16

# # Output:
# (.venv) PS E:\NLP Learning\NLP-Learning\agno-rag-agent> uv run .\rag_pgvector.py
# INFO skip_if_exists is disabled, disabling upsert
# INFO Loading content: b9d61209-73e8-5072-8d39-84263a15b9d6
# INFO Adding content from URL https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf
# INFO Reading: https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf
# INFO Inserted batch of 14 documents.
# WARNING  Contents DB not found for knowledge base: None
#                                                                                                                                                                                   ┃
# ▰▰▰▱▱▱▱ Thinking...
# ┏━ Message ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                                                                                                                     ┃
# ┃ How do I make chicken and galangal in coconut milk soup                                                                                                                             ┃
# ┃                                                                                                                                                                                     ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Response (28.5s) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                                                                                                                     ┃
# ┃ You’re describing Tom Kha Gai — a classic Thai chicken soup with galangal and coconut milk. Below is an easy, authentic-style recipe (serves 4) plus tips and substitutions.        ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Ingredients                                                                                                                                                                         ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • 4 cups (1 L) chicken stock (or water + bouillon)                                                                                                                                 ┃
# ┃  • 1 (14 oz / 400 ml) can full-fat coconut milk (add 1/2 cup coconut cream for extra richness, optional)                                                                            ┃
# ┃  • 12 oz (350 g) chicken (breast or thigh), thinly sliced across the grain                                                                                                          ┃
# ┃  • 1–2 stalks lemongrass, tough outer layers removed, smash and cut into 2–3 inch pieces                                                                                            ┃
# ┃  • 6–8 thin slices fresh galangal (about 1–1.5 oz / 30–45 g). If using frozen, use same amount; if using dried or powdered, reduce (it’s stronger)                                  ┃
# ┃  • 3–4 kaffir lime leaves, torn (remove the central stem)                                                                                                                           ┃
# ┃  • 2–3 shallots, thinly sliced                                                                                                                                                      ┃
# ┃  • 8 oz (225 g) mushrooms (straw, button or cremini), halved                                                                                                                        ┃
# ┃  • 2–3 Thai bird chilies (or 1 serrano), smashed or sliced — adjust to taste                                                                                                        ┃
# ┃  • 2–3 tbsp fish sauce (to taste)                                                                                                                                                   ┃
# ┃  • 2–3 tbsp fresh lime juice (to taste)                                                                                                                                             ┃
# ┃  • 1 tsp sugar or palm sugar (optional)                                                                                                                                             ┃
# ┃  • Fresh cilantro (coriander) for garnish                                                                                                                                           ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Method                                                                                                                                                                              ┃
# ┃                                                                                                                                                                                     ┃
# ┃  1 Prep: slice galangal thinly, bruise lemongrass with the back of a knife and cut, tear kaffir leaves, thinly slice chicken.                                                       ┃
# ┃  2 In a pot, bring the chicken stock to a gentle simmer. Add lemongrass, galangal, kaffir lime leaves, shallots and chilies. Simmer gently 5–10 minutes to infuse flavors.          ┃
# ┃  3 Add mushrooms and the coconut milk. Warm gently until steaming but avoid a rolling boil (boiling can separate/curdle the coconut milk). Simmer 3–5 minutes.                      ┃
# ┃  4 Add the sliced chicken and simmer just until cooked through (about 3–5 minutes depending on thickness).                                                                          ┃
# ┃  5 Remove from heat. Season with fish sauce, lime juice and sugar, tasting and adjusting so the soup is balanced salty-sour-slightly sweet.                                         ┃
# ┃  6 Serve hot garnished with cilantro and extra sliced chili or lime wedges.                                                                                                         ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Timing                                                                                                                                                                              ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • Active prep: 10–15 min                                                                                                                                                           ┃
# ┃  • Cook: 15–20 min                                                                                                                                                                  ┃
# ┃  • Total: ~30–35 min                                                                                                                                                                ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Tips & substitutions                                                                                                                                                                ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • No galangal? Use ginger as a last resort — flavor is different (ginger is spicier, less citrusy/woodsy).                                                                         ┃
# ┃  • If fresh galangal is hard to find, frozen slices are common in Asian markets. Dried/powdered galangal is more concentrated; use sparingly.                                       ┃
# ┃  • Don’t boil vigorously after adding coconut milk — gentle simmer keeps the texture smooth.                                                                                        ┃
# ┃  • Vegetarian version: use vegetable stock, replace fish sauce with soy sauce or tamari and add extra lime for brightness; swap chicken for firm tofu.                              ┃
# ┃  • For richer soup, stir in a bit of coconut cream before serving.                                                                                                                  ┃
# ┃  • Adjust heat with more/less chilies or use jalapeño/serrano if bird chilies aren’t available.                                                                                     ┃
# ┃                                                                                                                                                                                     ┃
# ┃ Storage                                                                                                                                                                             ┃
# ┃                                                                                                                                                                                     ┃
# ┃  • Refrigerate up to 2–3 days. Reheat gently (don’t boil) to avoid breaking the coconut milk.                                                                                       ┃
# ┃                                                                                                                                                                                     ┃
# ┃ If you’d like, I can give a scaled version for a different number of servings, a printable shopping list, or a vegetarian variant.                                                  ┃
# ┃                                                                                                                                                                                     ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
