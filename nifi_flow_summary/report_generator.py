
def build_report(root_group, summaries, config) -> str:
    """
    Assemble the final Markdown report from summaries and group details.
    """
    lines = []
    lines.append(f"# NiFi Flow Summary Report\n")

    for tenant in root_group.children:
        summary = summaries.get(tenant.id, '')
        lines.append(f"## Tenant: {tenant.name}\n")
        lines.append(summary + "\n")
        # Detailed notes
        #lines.extend(tenant.format_details())
        lines.append("\n---\n")

    return '\n'.join(lines)
