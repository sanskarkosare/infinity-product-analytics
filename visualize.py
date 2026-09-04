import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

conn = sqlite3.connect(r'D:\Sk Work\Placement-Things\Machine Learning\ML projects\infinity-agent\infinity_logs.db')
df = pd.read_sql("SELECT * FROM interaction_logs", conn)
conn.close()

df = df[df['intent_category'] != 'voice_out']

adoption = df.groupby('intent_category').agg(
    total=('id','count'),
    successes=('success','sum'),
    avg_latency_ms=('latency_ms','mean')
).reset_index()
adoption['success_rate_pct'] = (adoption['successes']/adoption['total']*100).round(1)
adoption['avg_latency_s'] = (adoption['avg_latency_ms']/1000).round(2)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Infinity AI Agent — Product Analytics Dashboard", 
             fontsize=15, fontweight='bold')

colors = ['#4F8EF7','#22C55E','#F97316','#EF4444','#A78BFA','#EC4899','#14B8A6']

# 1. Feature adoption (excluding unknown)
ax1 = axes[0, 0]
known = adoption[adoption['intent_category'] != 'unknown'].sort_values('total', ascending=True)
bars = ax1.barh(known['intent_category'], known['total'], color=colors[:len(known)])
ax1.set_title("Feature Adoption (Interaction Count)")
ax1.set_xlabel("Number of Interactions")
for bar, val in zip(bars, known['total']):
    ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
             str(int(val)), va='center', fontweight='bold')

# 2. Latency by feature
ax2 = axes[0, 1]
latency = adoption[adoption['intent_category'] != 'unknown'].sort_values('avg_latency_s', ascending=False)
bar_colors = ['#EF4444' if x > 10 else '#F97316' if x > 5 else '#22C55E' 
              for x in latency['avg_latency_s']]
bars = ax2.bar(latency['intent_category'], latency['avg_latency_s'], color=bar_colors)
ax2.axhline(5, color='orange', linestyle='--', linewidth=1.5, label='5s warning threshold')
ax2.axhline(10, color='red', linestyle='--', linewidth=1.5, label='10s critical threshold')
ax2.set_title("Average Latency by Feature (seconds)")
ax2.set_ylabel("Latency (s)")
ax2.set_xticklabels(latency['intent_category'], rotation=15, ha='right')
ax2.legend(fontsize=8)
for bar, val in zip(bars, latency['avg_latency_s']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f"{val:.1f}s", ha='center', fontweight='bold', fontsize=9)

# 3. Success rate including unknown
ax3 = axes[1, 0]
success_data = adoption.sort_values('success_rate_pct')
bar_colors2 = ['#EF4444' if x < 100 else '#22C55E' for x in success_data['success_rate_pct']]
bars = ax3.bar(success_data['intent_category'], success_data['success_rate_pct'], color=bar_colors2)
ax3.set_title("Success Rate by Intent Category")
ax3.set_ylabel("Success Rate (%)")
ax3.set_ylim(0, 110)
ax3.set_xticklabels(success_data['intent_category'], rotation=15, ha='right')
for bar, val in zip(bars, success_data['success_rate_pct']):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f"{val:.0f}%", ha='center', fontweight='bold', fontsize=9)

# 4. RAG funnel
ax4 = axes[1, 1]
stages = ['Documents\nUploaded', 'RAG Queries\nMade']
values = [4, 2]
bar_colors3 = ['#4F8EF7', '#F97316']
bars = ax4.bar(stages, values, color=bar_colors3, width=0.4)
ax4.set_title("RAG Feature Funnel\n(50% Drop-off After Upload)")
ax4.set_ylabel("Count")
for bar, val in zip(bars, values):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
             str(val), ha='center', fontweight='bold', fontsize=12)
ax4.annotate('50% drop-off', xy=(0.5, 3), fontsize=11, 
             color='red', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('infinity_analytics.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved as infinity_analytics.png")