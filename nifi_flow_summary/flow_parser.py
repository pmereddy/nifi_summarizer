import gzip
import json
import ijson
from .models import ProcessGroup



def parse_flow_definition(path: str) -> ProcessGroup:
    """
    Load flow.json.gz and build the process group hierarchy.
    """
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    # TODO: detect schema differences and extract rootGroup
    root = data.get('rootGroup') or data.get('flowController', {}).get('rootGroup')
    return ProcessGroup.from_dict(root)
