"""UTOPIA BombSquad Dashboard — Flask web server."""

import json
import os
import time
from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# ── config ──────────────────────────────────────────────────────────
SERVER_DIR = os.environ.get("BS_SERVER_DIR", os.path.expanduser("~/UTOPIA-BOMBSQUAD-SERVER"))
STATS_FILE = os.path.join(SERVER_DIR, "dist", "ba_root", "mods", "stats", "stats.json")
PROFILES_FILE = os.path.join(SERVER_DIR, "dist", "ba_root", "mods", "playersdata", "profiles.json")
ROLES_FILE = os.path.join(SERVER_DIR, "dist", "ba_root", "mods", "playersdata", "roles.json")
SETTINGS_FILE = os.path.join(SERVER_DIR, "dist", "ba_root", "mods", "setting.json")

# Show these on the dashboard
DISCORD_INVITE = os.environ.get("DISCORD_INVITE", "https://discord.gg/jBj8tFuu2ah")
SERVER_NAME = os.environ.get("SERVER_NAME", "SONder")
REFRESH_SECONDS = 30

# ── helpers ──────────────────────────────────────────────────────────
def safe_read_json(path, default=None):
    """Read a JSON file, returning default on any error."""
    if default is None:
        default = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return default


def get_stats():
    """Return sorted player stats from stats.json."""
    raw = safe_read_json(STATS_FILE, {"stats": {}})
    stats = raw.get("stats", {})

    players = []
    for aid, data in stats.items():
        players.append({
            "aid": aid,
            "name": data.get("name", "???"),
            "rank": data.get("rank", 0),
            "scores": data.get("scores", 0),
            "kills": data.get("kills", 0),
            "deaths": data.get("deaths", 0),
            "kd": round(data.get("kd", 0), 2),
            "games": data.get("games", 0),
            "avg_score": round(data.get("avg_score", 0), 2),
            "last_seen": data.get("last_seen", ""),
        })

    players.sort(key=lambda p: p["rank"])
    return players


def get_server_info():
    """Return basic server metadata."""
    settings = safe_read_json(SETTINGS_FILE, {})
    roles = safe_read_json(ROLES_FILE, {})

    owner_ids = roles.get("owner", {}).get("ids", [])
    return {
        "name": settings.get("HostName", SERVER_NAME),
        "device_name": settings.get("HostDeviceName", "unknown"),
        "discord": DISCORD_INVITE,
        "max_players": settings.get("maxPartySize", 8),
        "owner_count": len(owner_ids),
        "stats_reset_days": settings.get("statsResetAfterDays", 31),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# ── routes ───────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE,
                                  server=get_server_info(),
                                  refresh=REFRESH_SECONDS)


@app.route("/api/stats")
def api_stats():
    return jsonify({"players": get_stats(), "server": get_server_info()})


@app.route("/api/server")
def api_server():
    return jsonify(get_server_info())


# ── HTML template ────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ server.name }} — Dashboard</title>
<meta http-equiv="refresh" content="{{ refresh }}">
<style>
  :root {
    --bg: #0d0d12;
    --card: #16161f;
    --text: #e0e0e0;
    --muted: #888;
    --accent: #c0392b;
    --gold: #f0a030;
    --silver: #a0a8b8;
    --bronze: #c08050;
    --green: #27ae60;
    --border: #222;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, sans-serif;
    min-height: 100vh;
  }
  header {
    background: var(--card);
    border-bottom: 2px solid var(--accent);
    padding: 20px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
  }
  header h1 { font-size: 1.8rem; font-weight: 700; }
  header h1 span { color: var(--accent); }
  .header-links { display:flex; gap:12px; align-items:center; }
  .btn {
    padding: 8px 18px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    transition: 0.2s;
  }
  .btn-discord { background:#5865F2; color:#fff; }
  .btn-discord:hover { background:#4752c4; }
  .btn-refresh { background:var(--border); color:var(--text); }
  main { max-width:1100px; margin:30px auto; padding:0 20px; }
  .meta-bar {
    display: flex; gap: 20px; flex-wrap: wrap;
    margin-bottom: 30px;
  }
  .meta-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px 24px; min-width: 140px;
    text-align: center;
  }
  .meta-card .val { font-size: 1.5rem; font-weight:700; }
  .meta-card .lbl { font-size: 0.75rem; color: var(--muted); margin-top:4px; }
  table {
    width:100%; border-collapse: collapse;
    background: var(--card); border-radius: 8px;
    overflow: hidden; border: 1px solid var(--border);
  }
  th, td { padding: 12px 16px; text-align: left; }
  th { background: #1a1a26; color: var(--muted); font-size: 0.75rem;
       text-transform: uppercase; letter-spacing: 0.5px; }
  tr { border-bottom: 1px solid var(--border); }
  tr:hover { background: #1c1c28; }
  .rank-1 { color: var(--gold); font-weight:800; }
  .rank-2 { color: var(--silver); font-weight:700; }
  .rank-3 { color: var(--bronze); font-weight:700; }
  .name-cell { font-weight:600; }
  .kd-good { color: var(--green); }
  .empty-state { text-align:center; padding:60px 20px; color:var(--muted); }
  .empty-state h2 { font-size:1.2rem; margin-bottom:8px; }
  footer { text-align:center; padding:30px; color: var(--muted);
           font-size:0.8rem; }
  @media (max-width:600px) {
    header { padding:15px 20px; }
    th, td { padding:8px 10px; font-size:0.85rem; }
    .meta-card { min-width:100px; padding:10px; }
  }
</style>
</head>
<body>

<header>
  <h1>&#x1f4ca; <span>{{ server.name }}</span> Dashboard</h1>
  <div class="header-links">
    <span style="color:var(--muted);font-size:0.8rem">Auto-refresh {{ refresh }}s</span>
    <a class="btn btn-refresh" href="/">Refresh</a>
    <a class="btn btn-discord" href="{{ server.discord }}" target="_blank">
      &#x1f4ac; Discord
    </a>
  </div>
</header>

<main>
  <div class="meta-bar" id="meta"></div>
  <div id="table-container">
    <div class="empty-state"><h2>Loading stats...</h2></div>
  </div>
</main>

<footer>
  {{ server.name }} &copy; {{ server.last_updated[:4] }} &mdash;
  Last updated: <span id="updated">{{ server.last_updated }}</span>
</footer>

<script>
  async function load() {
    try {
      const res = await fetch('/api/stats');
      const data = await res.json();

      // meta bar
      document.getElementById('meta').innerHTML = `
        <div class="meta-card"><div class="val">${data.players.length}</div><div class="lbl">Players Tracked</div></div>
        <div class="meta-card"><div class="val">${data.server.max_players}</div><div class="lbl">Max Party Size</div></div>
        <div class="meta-card"><div class="val">${data.server.stats_reset_days}d</div><div class="lbl">Season Reset</div></div>
        <div class="meta-card"><div class="val">${data.server.owner_count}</div><div class="lbl">Owners</div></div>
      `;

      // table
      const container = document.getElementById('table-container');
      if (!data.players.length) {
        container.innerHTML = `<div class="empty-state">
          <h2>No stats yet</h2><p>Play a few games and stats will appear here.</p>
        </div>`;
        return;
      }

      let rows = data.players.map((p, i) => {
        const rankClass = p.rank === 1 ? 'rank-1' : p.rank === 2 ? 'rank-2' : p.rank === 3 ? 'rank-3' : '';
        const kdClass = p.kd >= 1.5 ? 'kd-good' : '';
        return `<tr>
          <td class="${rankClass}">#${p.rank || '?'}</td>
          <td class="name-cell">${p.name}</td>
          <td>${p.scores.toLocaleString()}</td>
          <td>${p.kills}</td>
          <td>${p.deaths}</td>
          <td class="${kdClass}">${p.kd}</td>
          <td>${p.games}</td>
          <td>${p.avg_score}</td>
        </tr>`;
      }).join('');

      container.innerHTML = `<table>
        <thead><tr>
          <th>Rank</th><th>Name</th><th>Score</th><th>Kills</th>
          <th>Deaths</th><th>K/D</th><th>Games</th><th>Avg Score</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>`;

      document.getElementById('updated').textContent = data.server.last_updated;
    } catch(e) {
      document.getElementById('table-container').innerHTML =
        `<div class="empty-state"><h2>Server offline?</h2><p>Could not reach stats.</p></div>`;
    }
  }

  load();
  setInterval(load, {{ refresh }} * 1000);
</script>

</body>
</html>"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Dashboard starting on http://0.0.0.0:{port}")
    print(f"Stats path: {STATS_FILE}")
    app.run(host="0.0.0.0", port=port, debug=False)
