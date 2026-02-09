import json
import yaml
import logging
from .llm_client import OllamaClient
from .prompt_loader import PromptLoader

logger = logging.getLogger(__name__)

def summarize_tenants(root_group, config):
    """
    Traverse each direct child of root_group, summarize bottom-up using JSON-based prompts.
    Returns dict {group_id: summary_text}.
    """
    client = OllamaClient(config['ollama_host'], config['model'])
    prompt_dir = config.get('prompt_dir', 'prompts')
    loader = PromptLoader(prompt_dir)
    summaries = {}
    include_sub = config['summarization'].get('include_subgroups', True)

    def recurse(group):
        # Summarize sub-groups first
        child_summaries = []
        if include_sub:
            for child in group.children:
                recurse(child)
                child_summaries.append({
                    'id': child.id,
                    'name': child.name,
                    'summary': summaries.get(child.id, '')
                })

        # Prepare JSON strings
        try:
            nodes_yaml = yaml.safe_dump(group.nodes, sort_keys=False)
            edges_yaml = yaml.safe_dump(group.edges, sort_keys=False)
        except Exception as e:
            logger.exception(f"Failed to serialize process group {group.id} nodes and edges to YAML: {e}")
            nodes_yaml=''
            edges_yaml=''

        prompt = f"Could not determine the summary of process group with id {group.id}"
        # Choose appropriate template
        if child_summaries:
            try:
                tone=config['summarization'].get('persona', 'executive')
                template = loader.load(tone+'_aggregation_summary_template.txt')
                child_yaml = yaml.safe_dump(child_summaries, sort_keys=False)
                #child_json = json.dumps(child_summaries, indent=2)
                prompt = template.format(
                    child_summaries_yaml=child_yaml,
                    nodes_yaml=nodes_yaml,
                    edges_yaml=edges_yaml,
                )
            except Exception as e:
                logger.exception(f"Error loading aggregation template: {e}")
        else:
            try:
                tone=config['summarization'].get('persona', 'executive')
                template = loader.load(tone+'_group_summary_template.txt')
                prompt = template.format(
                    nodes_yaml=nodes_yaml,
                    edges_yaml=edges_yaml,
                )
            except Exception as e:
                logger.exception(f"Error loading group template: {e}")

        # Generate summary via LLM
        try:
            logger.info(f"LLM generate API called with prompt of length: {len(prompt)} bytes" )
            logger.debug(f"{prompt}" )
            summary = client.generate(prompt)
            logger.info(f"LLM generate API call completed with summary:\n {summary}" )
            logger.info(f"-----------------------------------------------------------------")
        except Exception as e:
            logger.exception(f"LLM generation error for group {group.id}: {e}")
            summary = ''

        summaries[group.id] = summary

    # Kick off summarization for each tenant
    for tenant in root_group.children:
        recurse(tenant)

    return summaries
