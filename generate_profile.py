#!/usr/bin/env python3
import json
import sys
from collections import defaultdict

def load_bookmarks(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_category_map(categories):
    category_map = {}
    
    def process_category(cat, parent_name=""):
        if 'id' in cat and 'name' in cat:
            full_name = f"{parent_name} > {cat['name']}" if parent_name else cat['name']
            category_map[cat['id']] = {
                'name': cat['name'],
                'full_path': full_name,
                'parent_name': parent_name
            }
            
            # Process children recursively
            for child in cat.get('children', []):
                process_category(child, full_name)
    
    for category in categories:
        process_category(category)
    
    return category_map

def organize_bookmarks_by_category(data):
    categories = data.get('categories', [])
    bookmarks = data.get('bookmarks', [])
    
    category_map = build_category_map(categories)
    organized = defaultdict(list)
    
    for bookmark in bookmarks:
        if not isinstance(bookmark, dict):
            continue
        category_id = bookmark.get('categoryId')
        if category_id and category_id in category_map:
            category_path = category_map[category_id]['full_path']
        else:
            category_path = 'Uncategorized'
        
        organized[category_path].append({
            'title': bookmark.get('title', 'Untitled'),
            'url': bookmark.get('url', ''),
            'summary': bookmark.get('summary', '')
        })
    
    return dict(organized)

def generate_markdown(organized_bookmarks):
    md_content = []
    md_content.append("# 📚 My Development Resources")
    md_content.append("")
    md_content.append("A curated collection of useful development resources, tools, and references organized by category.")
    md_content.append("")
    md_content.append("---")
    md_content.append("")
    
    # Sort categories alphabetically
    sorted_categories = sorted(organized_bookmarks.keys())
    
    for category in sorted_categories:
        bookmarks = organized_bookmarks[category]
        if not bookmarks:
            continue
            
        # Create heading from category path
        heading_level = "##"  # Start with level 2
        if " > " in category:
            depth = category.count(" > ")
            heading_level = "#" * min(depth + 2, 6)  # Max heading level is 6
        
        # Clean up category name for display
        display_category = category.replace(" > ", " → ")
        
        md_content.append(f"{heading_level} {display_category}")
        md_content.append("")
        
        # Sort bookmarks by title
        sorted_bookmarks = sorted(bookmarks, key=lambda x: x['title'].lower())
        
        for bookmark in sorted_bookmarks:
            if bookmark['url']:
                md_content.append(f"- **[{bookmark['title']}]({bookmark['url']})**")
                if bookmark['summary'] and 'Heuristic categorization:' not in bookmark['summary']:
                    md_content.append(f"  <br>*{bookmark['summary']}*")
                md_content.append("")
            else:
                md_content.append(f"- **{bookmark['title']}**")
                md_content.append("")
    
    md_content.append("---")
    md_content.append("")
    md_content.append("*Generated from bookmarks collection*")
    md_content.append("")
    
    return "\n".join(md_content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 generate_profile.py <bookmarks.json>")
        sys.exit(1)
    
    try:
        data = load_bookmarks(sys.argv[1])
        organized = organize_bookmarks_by_category(data)
        markdown = generate_markdown(organized)
        
        output_file = 'README.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"✅ Generated {output_file} successfully!")
        print(f"📁 Total categories: {len(organized)}")
        total_bookmarks = sum(len(bookmarks) for bookmarks in organized.values())
        print(f"🔗 Total bookmarks: {total_bookmarks}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()