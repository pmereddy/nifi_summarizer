from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import logging


@dataclass
class ProcessGroup:
    id: str
    name: str
    comments: Optional[str] = None
    children: List['ProcessGroup'] = field(default_factory=list)
    processors: List[Dict[str, Any]] = field(default_factory=list)
    input_ports: List[Dict[str, Any]] = field(default_factory=list)
    output_ports: List[Dict[str, Any]] = field(default_factory=list)
    controller_services: List[Dict[str, Any]] = field(default_factory=list)
    connections: List[Dict[str, Any]] = field(default_factory=list)

    # Extracted design info
    sources: List[str] = field(default_factory=list)
    destinations: List[str] = field(default_factory=list)
    schedules: List[str] = field(default_factory=list)
    transforms: List[str] = field(default_factory=list)
    css: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessGroup':
        logger = logging.getLogger(__name__)
        if not isinstance(data, dict):
            logger.warning(f"data in from_dict is not a dict. {data}")
            return None
        
        try:
            comp = data.get('component', data)
            group = cls(
                id=comp.get('id'),
                name=comp.get('name'),
                comments=comp.get('comment')
            )
            logger.debug(f"Creating ProcessGroup {group.id} ('{group.name}')")

            # Parse child process groups
            pg = data.get('processGroup') or data.get('processGroups', [])
            pgs = pg if isinstance(pg, list) \
                    else ([pg ] if isinstance(pg, dict) else [])
            for child in pgs:
                group.children.append(cls.from_dict(child))

            # Parse processors
            group.processors = (data.get('processor') or comp.get('processors', []))
            # Parse input ports
            group.input_ports = (data.get('inputPort') or data.get('inputPorts', []))
            # Parse output ports
            group.output_ports = (data.get('outputPort') or data.get('outputPorts', []))
            # Parse controller services
            group.controller_services = (data.get('controllerService') or data.get('controllerServices', []))
            # Parse connections
            group.connections = (data.get('connection') or data.get('connections', []))

            # Extract design info
            group.extract_design_info()
            return group
        except Exception as e:
            logger.exception(f"Error parsing ProcessGroup from dict: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'comments': self.comments,
            'sources': self.sources,
            'destinations': self.destinations,
            'schedules': self.schedules,
            'transforms': self.transforms,
            'children': [child.to_dict() for child in self.children]
        }


    def extract_design_info(self):
        """
        Populates:
          - self.nodes: list of dicts, each with:
              - type, id, name
              - artifact         # from bundle.artifact
              - schedulingStrategy, schedulingPeriod (processors)
              - comments, scheduledState (ports)
              - properties       # flattened key/value map
          - self.edges: list of dicts { from_id, to_id, relationship, … }
        """
        logger = logging.getLogger(__name__)

        # initialize
        self.nodes = []
        self.edges = []

        try:
            # ─── 1) NODES ────────────────────────────────────────────────────────────
            # ——— Processors —————————————————————————————————————————————
            procs = (self.processors if isinstance(self.processors, list)
                     else [self.processors] if isinstance(self.processors, dict)
                     else [])
            for entry in procs:
                if not isinstance(entry, dict):
                    logger.warning(f"processor entry not a dict: {entry}")
                    continue
                comp = entry.get('component', entry)
                node = {
                    'type': 'processor',
                    'id':   comp.get('id'),
                    'name': comp.get('name'),
                    'artifact': comp.get('bundle', {}).get('artifact'),
                    # scheduling fields
                    'schedulingStrategy': comp.get('schedulingStrategy'),
                    'schedulingPeriod':   comp.get('schedulingPeriod'),
                    'executionNode':   comp.get('executionNode'),
                }
                # flatten property list into a dict
                props = {}
                for p in comp.get('property', []):
                    props[p['name']] = p.get('value')
                node['properties'] = props

                self.nodes.append(node)

            # ——— Controller Services —————————————————————————————————————
            css = (self.controller_services if isinstance(self.controller_services, list)
                   else [self.controller_services] if isinstance(self.controller_services, dict)
                   else [])
            for entry in css:
                if not isinstance(entry, dict):
                    logger.warning(f"controller_service entry not a dict: {entry}")
                    continue
                comp = entry.get('component', entry)
                node = {
                    'type': 'controller_service',
                    'id':   comp.get('id'),
                    'name': comp.get('name'),
                    # extract artifact from bundle too
                    'artifact': comp.get('bundle', {}).get('artifact'),
                }
                # flatten property list
                props = {}
                for p in comp.get('property', []):
                    props[p['name']] = p.get('value')
                node['properties'] = props

                self.nodes.append(node)

            # ——— Input Ports ————————————————————————————————————————————
            in_ports = (self.input_ports if isinstance(self.input_ports, list)
                        else [self.input_ports] if isinstance(self.input_ports, dict)
                        else [])
            for entry in in_ports:
                if not isinstance(entry, dict):
                    logger.warning(f"input_port entry not a dict: {entry}")
                    continue
                comp = entry.get('component', entry)
                node = {
                    'type': 'input_port',
                    'id':   comp.get('id'),
                    'name': comp.get('name'),
                    'comments':       comp.get('comments'),
                    'scheduledState': comp.get('scheduledState'),
                }
                self.nodes.append(node)

            # ——— Output Ports ———————————————————————————————————————————
            out_ports = (self.output_ports if isinstance(self.output_ports, list)
                         else [self.output_ports] if isinstance(self.output_ports, dict)
                         else [])
            for entry in out_ports:
                if not isinstance(entry, dict):
                    logger.warning(f"output_port entry not a dict: {entry}")
                    continue
                comp = entry.get('component', entry)
                node = {
                    'type': 'output_port',
                    'id':   comp.get('id'),
                    'name': comp.get('name'),
                    'comments':       comp.get('comments'),
                    'scheduledState': comp.get('scheduledState'),
                }
                self.nodes.append(node)

            # ─── 2) EDGES ────────────────────────────────────────────────────────────
            conns = (self.connections if isinstance(self.connections, list)
                     else [self.connections] if isinstance(self.connections, dict)
                     else [])
            for c in conns:
                if not isinstance(c, dict):
                    logger.warning(f"connection is not a dict: {c}")
                    continue
                edge = {
                    'from_id':             c.get('sourceId'),
                    'to_id':               c.get('destinationId'),
                    'relationship':        c.get('relationship'),
                    'maxWorkQueueSize':    c.get('maxWorkQueueSize'),
                    'loadBalanceStrategy': c.get('loadBalanceStrategy'),
                    # add others as desired…
                }
                self.edges.append(edge)

        except Exception as e:
            logger.exception(f"Error extracting design info for ProcessGroup {self.id}: {e}")


    def _extract_design_info(self):
        """
        Populates:
          - self.nodes:  list of dicts { type, id, name, comments?, scheduledState?, schedulingStrategy?, schedulingPeriod? }
          - self.edges:  list of dicts { from_id, to_id, relationship, maxWorkQueueSize?, loadBalanceStrategy?, … }
        """
        logger = logging.getLogger(__name__)

        # initialize
        self.nodes = []
        self.edges = []

        try:
            # 1) NODES: iterate each component type
            def harvest(attr, node_type, extra_fields):
                """
                attr:       self.<attr> (e.g. 'processors', 'input_ports')
                node_type:  a string, e.g. 'processor', 'input_port'
                extra_fields: list of keys (or nested tuples) to pull off comp
                """
                raw = getattr(self, attr, None)
                entries = raw if isinstance(raw, list) \
                          else ([raw] if isinstance(raw, dict) else [])
                for entry in entries:
                    if not isinstance(entry, dict):
                        logger.warning(f"{attr} entry not a dict: {entry}")
                        continue
                    comp = entry.get('component', entry)
                    node = {
                        'type': node_type,
                        'id':   comp.get('id'),
                        'name': comp.get('name')
                    }
                    # pull any extra fields
                    for fld in extra_fields:
                        if isinstance(fld, str):
                            node[fld] = comp.get(fld)
                        else:
                            # nested key, e.g. ('config','schedulingStrategy')
                            val = comp
                            for sub in fld:
                                val = val.get(sub, {}) if isinstance(val, dict) else {}
                            node["_".join(fld)] = val or None
                    self.nodes.append(node)

            # define what to extract from each type
            harvest('processors', 'processor', extra_fields=['artifact', 'class', 'artifact', 'schedulingStrategy', 'schedulingPeriod', 'executionNode','properties'])
            harvest('input_ports', 'input_port', extra_fields=['comments', 'scheduledState'])
            harvest('output_ports', 'output_port', extra_fields=['comments', 'scheduledState'])
            harvest('controller_services','controller_service', extra_fields=['comment', 'class', 'artifact', 'properties'])

            # 2) EDGES: flatten your connections list
            conns = self.connections if isinstance(self.connections, list) \
                    else ([self.connections] if isinstance(self.connections, dict) else [])
            for c in conns:
                if not isinstance(c, dict):
                    logger.warning(f"connection is not a dict: {c}")
                    continue
                edge = {
                    'from_id':            c.get('sourceId'),
                    'to_id':              c.get('destinationId'),
                    'relationship':       c.get('relationship'),
                    'maxWorkQueueSize':   c.get('maxWorkQueueSize'),
                    'loadBalanceStrategy':c.get('loadBalanceStrategy'),
                    # add any other connection‐level props you care about…
                }
                self.edges.append(edge)

        except Exception as e:
            logger.exception(f"Error extracting design info for ProcessGroup {self.id}: {e}")
