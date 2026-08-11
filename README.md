# UTOPIA BombSquad Dashboard

Web dashboard for your BombSquad server stats. Lightweight Flask app — runs on the same VPS.

## Quick Start (VPS)

```sh
git clone https://github.com/Yuma-desu/UTOPIA-BOMBSQUAD-DASHBOARD
cd UTOPIA-BOMBSQUAD-DASHBOARD
pip install -r requirements.txt
```

Set the path to your server if it's not `~/UTOPIA-BOMBSQUAD-SERVER`:

```sh
export BS_SERVER_DIR=~/UTOPIA-BOMBSQUAD-SERVER
export DISCORD_INVITE=https://discord.gg/yourcode
```

Run:

```sh
python app.py
```

Dashboard at `http://your-vps-ip:5050`

## 24/7 with tmux

```sh
tmux new -s dashboard
cd ~/UTOPIA-BOMBSQUAD-DASHBOARD
python app.py
# Ctrl+B D to detach
```

## Auto-start on reboot

Add to `crontab -e`:

```
@reboot sleep 35 && cd ~/UTOPIA-BOMBSQUAD-DASHBOARD && tmux new-session -d -s dashboard 'python app.py'
```

## Config

| Env var | Default | Description |
|---|---|---|
| `BS_SERVER_DIR` | `~/UTOPIA-BOMBSQUAD-SERVER` | Path to server files |
| `DISCORD_INVITE` | `discord.gg/jBj8tFuu2ah` | Discord invite link |
| `SERVER_NAME` | `SONder` | Dashboard title |
| `PORT` | `5050` | Web server port |
