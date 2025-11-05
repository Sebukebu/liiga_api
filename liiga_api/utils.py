


def flatten_dict(d, parent_key="", skip_keys=None): # Recusive flattening for endpoint json responses!!
            skip_keys = skip_keys or []
            out = {}
            for k, v in d.items():
                if k in skip_keys:
                    out[k] = v
                elif isinstance(v, dict):
                    out.update(flatten_dict(v, parent_key=f"{parent_key}{k}_", skip_keys=skip_keys))
                else:
                    out[k] = v
            return out


def player_stat_parse(endpoint) -> list[dict]:
    players = []

    if endpoint.summed:
        players.extend(endpoint.response)

    else:
        for player_data in endpoint.response:
            previous_teams = player_data.get("previousTeamsForTournament")
            if previous_teams:
                players.extend(previous_teams)
            else:
                players.append(player_data)
    return players


def search_playerid_by_name(name: str):
    pass

def search_name_by_playerid(id: str):
    pass