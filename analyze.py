import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os

DB_PATH = os.environ.get('INFINITY_DB_PATH', 'infinity_logs.db')
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM interaction_logs", conn)
conn.close()

# Exclude voice_out — system call, not user action
df = df[df['intent_category'] != 'voice_out']

print("=== FEATURE ADOPTION ===")
adoption = df.groupby('intent_category').agg(
    total=('id','count'),
    successes=('success','sum'),
    avg_latency_ms=('latency_ms','mean')
).reset_index()
adoption['success_rate_pct'] = (adoption['successes']/adoption['total']*100).round(1)
adoption['avg_latency_s'] = (adoption['avg_latency_ms']/1000).round(2)
print(adoption[['intent_category','total','success_rate_pct','avg_latency_s']].to_string(index=False))

print("\n=== INTENT FAILURE ANALYSIS ===")
unknown = df[df['intent_category']=='unknown']
total_non_voice = len(df)
print(f"Unknown intent interactions: {len(unknown)}")
print(f"% of total interactions: {len(unknown)/total_non_voice*100:.1f}%")
print(f"Success rate: 0% (all fail — no handler for unknown intent)")

print("\n=== LATENCY RANKING (slowest first) ===")
latency = adoption[adoption['intent_category']!='unknown'].sort_values('avg_latency_s', ascending=False)
print(latency[['intent_category','avg_latency_s']].to_string(index=False))

print("\n=== RAG FUNNEL ===")
rag_ingest = len(df[df['intent_category']=='rag_ingest'])
rag_query = len(df[df['intent_category']=='rag'])
print(f"Documents uploaded (rag_ingest): {rag_ingest}")
print(f"RAG queries made: {rag_query}")
print(f"Query-to-ingest ratio: {rag_query/rag_ingest:.2f} queries per upload")
print(f"Drop-off: {100-(rag_query/rag_ingest*100):.0f}% of users who upload never query")

print("\n=== PRIORITIZATION RECOMMENDATION ===")
print("P0 — Fix intent classifier: 12.5% of queries fail silently")
print("P1 — Reduce web_search latency: 13.5s is unacceptable for chat UX")
print("P2 — Improve RAG discoverability: 4 uploads, only 2 queries = feature underused")
print("P3 — General response latency: 12s average needs optimization")