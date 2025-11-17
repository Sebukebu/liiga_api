
class ResponseParser:
    """Helper class to build custom parsers for endpoints."""

    @staticmethod
    def _parse_record(data: dict, columns: dict) -> dict:
        """Extract fields according to COLUMNS spec."""
        return {
            col: ResponseParser._get_nested(data, path) for path, col in columns.items()
            }

    
    @staticmethod
    def _get_nested(data: dict, path: str):
        """Navigate nested dict using dot notation."""
        current = data
        for key in path.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(key)
            if current is None:
                return None
        return current

        


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


def search_playerid_by_name(name: str):
    pass

def search_name_by_playerid(id: str):
    pass