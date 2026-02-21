"""
Parse intent.txt and create structured CSV file for intent indexing.
Similar to product_data.csv structure.
"""
import csv
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')


def parse_intent_file(filepath):
    """Parse intent.txt and extract intent data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract intent descriptions
    intent_descriptions = {}
    description_pattern = r'\*\* ([a-z_]+): (.+?)(?=\*\*|Customer Message:|Product category names:|If customer message only contains|$)'

    for match in re.finditer(description_pattern, content, re.DOTALL):
        intent_name = match.group(1).strip()
        description = match.group(2).strip().replace('\n', ' ')
        intent_descriptions[intent_name] = description

    # Extract query variation examples
    intent_examples = {}
    example_pattern = r"Customer Message: '([^']+)', intent:\s*'([a-z_]+)'"

    for match in re.finditer(example_pattern, content):
        query = match.group(1).strip()
        intent_name = match.group(2).strip()

        if intent_name not in intent_examples:
            intent_examples[intent_name] = []
        intent_examples[intent_name].append(query)

    # Extract product categories (special case)
    category_pattern = r"'([^']+)'(?=\s*'|\s*Examples)"
    categories = re.findall(category_pattern, content[content.find("Product category names:"):content.find("Examples :")])

    # Add categories to favorite_product_stock_check_by_category
    category_intent = 'favorite_product_stock_check_by_category'
    if category_intent not in intent_examples:
        intent_examples[category_intent] = []
    intent_examples[category_intent].extend(categories)

    # Combine data
    intent_data = []

    # Get all unique intent names from both descriptions and examples
    all_intents = set(intent_descriptions.keys()) | set(intent_examples.keys())

    for intent_name in sorted(all_intents):
        description = intent_descriptions.get(intent_name, "Intent description not provided.")
        examples = intent_examples.get(intent_name, [])

        # Create embedding text: combine intent name, description, and examples
        embedding_parts = [
            intent_name.replace('_', ' '),
            description
        ]
        if examples:
            embedding_parts.append("Examples: " + " | ".join(examples[:5]))  # Limit to first 5 examples

        embedding_text = ". ".join(embedding_parts)

        intent_data.append({
            'intent_name': intent_name,
            'description': description,
            'query_variations': ';'.join(examples) if examples else '',
            'embedding_text': embedding_text,
            'example_count': len(examples)
        })

    return intent_data


def save_to_csv(intent_data, output_path):
    """Save parsed intent data to CSV."""
    fieldnames = ['intent_name', 'description', 'query_variations', 'embedding_text', 'example_count']

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(intent_data)

    print(f"✓ Successfully created {output_path}")
    print(f"  Total intents: {len(intent_data)}")
    print(f"  Total examples: {sum(item['example_count'] for item in intent_data)}")


if __name__ == "__main__":
    input_file = "data/intent.txt"
    output_file = "data/intent_data.csv"

    print(f"Parsing {input_file}...")
    intent_data = parse_intent_file(input_file)

    print(f"\nSample parsed intents:")
    for item in intent_data[:3]:
        print(f"\n  Intent: {item['intent_name']}")
        print(f"  Description: {item['description'][:80]}...")
        print(f"  Examples: {item['example_count']}")
        if item['query_variations']:
            variations = item['query_variations'].split(';')
            print(f"    First variation: {variations[0]}")

    save_to_csv(intent_data, output_file)
    print(f"\n✓ Intent data ready for indexing!")
