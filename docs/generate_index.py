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


def load_approaches(approaches_file):
    """Load approach/paper mapping data from CSV."""
    approaches = {}
    with open(approaches_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            approaches[row['model_name']] = {
                'paper_url': row['paper_url'],
                'org_key': row['org_key'],
                'trajectory_link': row['trajectory_link']
            }
    return approaches


def load_models(models_file):
    """Load model data from CSV."""
    models = []
    with open(models_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            models.append(row)
    return models


def create_model_row(model, providers, approaches, rank):
    """Create an HTML table row for a model."""
    # Get approach info first, fall back to model data
    approach_info = None
    model_name = model['model_name']
    
    # Look for exact match first, then partial matches
    if model_name in approaches:
        approach_info = approaches[model_name]
    else:
        # Check for partial matches
        for approach_name in approaches:
            if approach_name in model_name:
                approach_info = approaches[approach_name]
                break
    
    # Use org_key and trajectory_link from approach if available, otherwise from model
    org_key = approach_info['org_key'] if approach_info else model['org_key']
    trajectory_link = approach_info['trajectory_link'] if approach_info else model['trajectory_link']
    
    # Get provider info
    provider = providers.get(org_key, {})
    org_name = provider.get('org_name', 'Unknown')
    org_url = provider.get('org_url', '#')
    logo_path = provider.get('logo_path', '')
    
    # Build model name cell
    model_cell = ""
    if rank == 0:
        model_cell += '🥇'
    elif rank == 1:
        model_cell += '🥈'
    elif rank == 2:
        model_cell += '🥉'
    if "new" in model["ranking"]:
        model_cell += '🆕'
    if model['ranking']:
        model_cell += '&nbsp;'
    
    # Add model name with link from approaches mapping
    if approach_info and approach_info['paper_url']:
        model_cell += f'<a href="{approach_info["paper_url"]}">{model_name}</a>'
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
    traj_cell = f'<a href="{trajectory_link}">🔗</a>'
    
    # Build the complete row
    data_mode_attr = f' data-mode="{model["data_mode"]}"' if model['data_mode'] else ''
    
    row = f'''                <tr{data_mode_attr}>
                  <td>{model_cell}</td>
                  <td class="has-text-centered">{org_cell}</td>
                  <td>{model["success_rate"]}%</td>
                  <td>{model["coverage_increase"]}%</td>
                  <td><time>{model["date"]}</time></td>
                  <td class="has-text-centered">{traj_cell}</td>
                </tr>'''
    
    return row


def generate_html(template_file, models_file, providers_file, approaches_file, output_file):
    """Generate the final HTML file."""
    # Load data
    providers = load_providers(providers_file)
    approaches = load_approaches(approaches_file)
    models = load_models(models_file)
    
    lite_rows = []
    verified_rows = []
    for data_mode in ["reproduction", "unittest"]:
        # Separate models by table type
        lite_models = [m for m in models if m['table_type'] == 'lite' and m['data_mode'] == data_mode]
        verified_models = [m for m in models if m['table_type'] == 'verified' and m['data_mode'] == data_mode]

        # determine top 3 for success rate across
        lite_models = sorted(lite_models, key=lambda x: float(x['success_rate']), reverse=True)
        verified_models = sorted(verified_models, key=lambda x: float(x['success_rate']), reverse=True)

        # Generate table rows
        for i, model in enumerate(lite_models):
            lite_rows.append(create_model_row(model, providers, approaches, i))
        
        for i, model in enumerate(verified_models):
            verified_rows.append(create_model_row(model, providers, approaches, i))
    
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
    approaches_file = script_dir / 'approaches.csv'
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
    
    if not approaches_file.exists():
        print(f"Error: Approaches file {approaches_file} not found!")
        sys.exit(1)
    
    # Generate HTML
    generate_html(template_file, models_file, providers_file, approaches_file, output_file)


if __name__ == '__main__':
    main()