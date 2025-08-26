#!/usr/bin/env python3
"""
Script to generate index.html from template and CSV data files.
Combines index.template.html with models.csv and providers.csv.
"""

import csv
import sys
from pathlib import Path


def load_providers(providers_file):
    """Load provider/organization data from CSV."""
    providers = {}
    with open(providers_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            providers[row['org_key']] = row
    return providers


def load_models(models_file):
    """Load model data from CSV."""
    models = []
    with open(models_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            models.append(row)
    return models


def create_model_row(model, providers):
    """Create an HTML table row for a model."""
    # Get provider info
    provider = providers.get(model['org_key'], {})
    org_name = provider.get('org_name', 'Unknown')
    org_url = provider.get('org_url', '#')
    logo_path = provider.get('logo_path', '')
    
    # Build model name cell
    model_cell = model['ranking']
    if model['ranking']:
        model_cell += '&nbsp;'
    
    # Add model name with link if it contains URL patterns
    model_name = model['model_name']
    if 'arxiv.org' in model_name or 'github.com' in model_name or 'docs.all-hands.dev' in model_name:
        # Extract URL from model name - this is a simplified approach
        if 'AEGIS' in model_name:
            model_cell += f'<a href="https://arxiv.org/pdf/2411.18015">{model_name}</a>'
        elif 'e-Otter++' in model_name:
            model_cell += f'<a href="https://arxiv.org/abs/2508.06365">{model_name}</a>'
        elif 'Amazon Q Developer Agent' in model_name:
            model_cell += f'<a href="https://aws.amazon.com/q/">{model_name}</a>'
        elif 'AssertFlip' in model_name:
            model_cell += f'<a href="https://arxiv.org/abs/2507.17542">{model_name}</a>'
        elif 'OpenHands' in model_name:
            model_cell += f'<a href="https://docs.all-hands.dev/">{model_name}</a>'
        elif 'SWE-Agent+' in model_name:
            model_cell += f'<a href="https://arxiv.org/abs/2406.12952">{model_name}</a>'
        elif 'SWE-Agent' in model_name:
            model_cell += f'<a href="https://swe-agent.com/latest/">{model_name}</a>'
        elif 'Aider' in model_name:
            model_cell += f'<a href="https://aider.chat">{model_name}</a>'
        elif 'AutoCodeRover' in model_name:
            model_cell += f'<a href="https://autocoderover.dev">{model_name}</a>'
        elif 'LIBRO' in model_name:
            model_cell += f'<a href="https://arxiv.org/abs/2209.11515">{model_name}</a>'
        elif 'Otter++' in model_name:
            model_cell += f'<a href="https://arxiv.org/abs/2502.05368v1">{model_name}</a>'
        elif 'Otter' in model_name and 'Otter++' not in model_name:
            model_cell += f'<a href="https://arxiv.org/abs/2502.05368v1">{model_name}</a>'
        else:
            model_cell += model_name
    else:
        model_cell += model_name
    
    # Add model details if present
    if model['model_details']:
        model_cell += f' <small>{model["model_details"]}</small>'
    
    # Add special markers
    if model['data_mode'] == 'reproduction':
        model_cell += '<sup>&Dagger;</sup>'
    
    # Build organization cell
    org_cell = f'<a href="{org_url}"><img alt="{org_name}" title="{org_name}" src="{logo_path}" class="org-icon"></a>'
    
    # Build trajectory cell
    traj_cell = f'<a href="{model["trajectory_link"]}">🔗</a>'
    
    # Build the complete row
    data_mode_attr = f' data-mode="{model["data_mode"]}"' if model['data_mode'] else ''
    
    row = f'''                <tr{data_mode_attr}>
                  <td>{model_cell}</td>
                  <td class="has-text-centered">{org_cell}</td>
                  <td>{model["success_rate"]}</td>
                  <td>{model["coverage_increase"]}</td>
                  <td><time>{model["date"]}</time></td>
                  <td class="has-text-centered">{traj_cell}</td>
                </tr>'''
    
    return row


def generate_html(template_file, models_file, providers_file, output_file):
    """Generate the final HTML file."""
    # Load data
    providers = load_providers(providers_file)
    models = load_models(models_file)
    
    # Separate models by table type
    lite_models = [m for m in models if m['table_type'] == 'lite']
    verified_models = [m for m in models if m['table_type'] == 'verified']
    
    # Generate table rows
    lite_rows = []
    for model in lite_models:
        lite_rows.append(create_model_row(model, providers))
    
    verified_rows = []
    for model in verified_models:
        verified_rows.append(create_model_row(model, providers))
    
    # Read template
    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Replace placeholders
    html = template.replace('{LITE_TABLE_ROWS}', '\n'.join(lite_rows))
    html = html.replace('{VERIFIED_TABLE_ROWS}', '\n'.join(verified_rows))
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated {output_file} successfully!")


def main():
    """Main function."""
    # Set file paths
    script_dir = Path(__file__).parent
    template_file = script_dir / 'index.template.html'
    models_file = script_dir / 'models.csv'
    providers_file = script_dir / 'providers.csv'
    output_file = script_dir / 'index.html'
    
    # Check if files exist
    if not template_file.exists():
        print(f"Error: Template file {template_file} not found!")
        sys.exit(1)
    
    if not models_file.exists():
        print(f"Error: Models file {models_file} not found!")
        sys.exit(1)
    
    if not providers_file.exists():
        print(f"Error: Providers file {providers_file} not found!")
        sys.exit(1)
    
    # Generate HTML
    generate_html(template_file, models_file, providers_file, output_file)


if __name__ == '__main__':
    main()