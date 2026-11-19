# backend/config.py
import os
import sys
from dotenv import load_dotenv
from groq import AsyncGroq
import networkx as nx

load_dotenv()

# ── Env vars ──────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

# ── Groq model ────────────────────────────────────────────────────
# openai/gpt-oss-120b (replaces the retired llama-3.3-70b-versatile):
# - 131k context window (handles large graph data dumps)
# - Reasoning model: its hidden reasoning tokens count toward max_tokens,
#   so the token budget is higher than for a non-reasoning model.
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_MAX_TOKENS = 4096
# "low" keeps answers fast; raise to "medium"/"high" for harder questions.
# Sent via extra_body because the pinned groq SDK has no reasoning_effort argument.
GROQ_EXTRA_BODY = {"reasoning_effort": "low"}

groq_client = AsyncGroq(api_key=GROQ_API_KEY)

# ── Graph (loaded once at startup) ────────────────────────────────
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from graph.cache import load_graph, load_graph_json
from graph.analyzer import OTCGraphAnalyzer

G: nx.DiGraph = None
graph_json: dict = None
analyzer: OTCGraphAnalyzer = None


def load_all():
    """Called once at FastAPI startup."""
    global G, graph_json, analyzer
    G = load_graph()
    graph_json = load_graph_json()
    analyzer = OTCGraphAnalyzer(G)
    print(f"  ✓ Graph ready: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")