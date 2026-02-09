import argparse
import yaml
import logging
import sys
from .flow_parser import parse_flow_definition
from .summarizer import summarize_tenants
from .report_generator import build_report


def main():
    parser = argparse.ArgumentParser(
        description='Generate NiFi flow summary report'
    )
    parser.add_argument('--input', '-i', required=True,
                        help='Path to flow.json.gz')
    parser.add_argument('--config', '-c', default='config.yaml',
                        help='Path to YAML config file')
    parser.add_argument('--output', '-o', default=None,
                        help='Output Markdown file path')
    args = parser.parse_args()

    # Load config
    try:
        with open(args.config) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error(f"Error parsing config file: {e}")
        sys.exit(1)

    # Set logging
    level = config.get('logging_level', 'INFO').upper()
    logging.basicConfig(level=getattr(logging, level, logging.INFO),
                        format='%(asctime)s %(levelname)s %(message)s')
    logging.info("NiFi Flow Summary tool started.")

    # Parse flow
    try:
        root_group = parse_flow_definition(args.input)
    except Exception as e:
        logging.exception(f"Failed to parse flow definition: {e}")
        sys.exit(1)

    # Summarize
    try:
        summaries = summarize_tenants(root_group, config)
    except Exception as e:
        logging.exception(f"Summarization failed: {e}")
        sys.exit(1)

    # Build report
    try:
        report = build_report(root_group, summaries, config)
    except Exception as e:
        logging.exception(f"Report generation failed: {e}")
        sys.exit(1)

    # Write output
    output_path = args.output or config.get('output_file')
    try:
        with open(output_path, 'w', encoding='utf-8') as outf:
            outf.write(report)
        logging.info(f"Report written to {output_path}")
    except Exception as e:
        logging.exception(f"Failed to write report: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
