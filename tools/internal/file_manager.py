#!/usr/bin/env python3
"""
📁 FILE MANAGER TOOL
⚡ Handles file operations, merging, cleanup, and organization
🎯 Mission: Keep the codebase clean and organized
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FileManager')

class FileManager:
    """Manages file operations and organization"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ignore_patterns = [
            '__pycache__',
            '.git',
            'node_modules',
            '.venv',
            'venv',
            '.env',
            '*.pyc',
            '.DS_Store'
        ]
    
    def find_duplicate_files(self) -> List[Tuple[str, List[Path]]]:
        """Find duplicate files based on content hash"""
        logger.info("🔍 Scanning for duplicate files...")
        
        file_hashes = {}
        
        for file_path in self.project_root.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Skip ignored patterns
            if any(pattern in str(file_path) for pattern in self.ignore_patterns):
                continue
            
            # Calculate file hash
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                if file_hash not in file_hashes:
                    file_hashes[file_hash] = []
                file_hashes[file_hash].append(file_path)
            except Exception as e:
                logger.warning(f"⚠️  Could not hash {file_path}: {e}")
        
        # Find duplicates
        duplicates = [(h, paths) for h, paths in file_hashes.items() if len(paths) > 1]
        
        logger.info(f"✅ Found {len(duplicates)} sets of duplicate files")
        return duplicates
    
    def merge_files(self, files: List[Path], target: Path) -> bool:
        """Merge multiple files into one target file"""
        logger.info(f"🔀 Merging {len(files)} files into {target}")
        
        try:
            # Read all file contents
            contents = []
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    contents.append(f.read())
            
            # Write merged content
            with open(target, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(contents))
            
            # Delete source files (except target)
            for file_path in files:
                if file_path != target:
                    file_path.unlink()
                    logger.info(f"🗑️  Deleted {file_path}")
            
            logger.info(f"✅ Successfully merged files into {target}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to merge files: {e}")
            return False
    
    def organize_files(self) -> Dict[str, int]:
        """Organize files into proper directory structure"""
        logger.info("📂 Organizing files...")
        
        stats = {
            'moved': 0,
            'created_dirs': 0
        }
        
        # Define organization rules
        rules = {
            'brain': ['*intelligence*', '*decision*', '*memory*', '*orchestrat*'],
            'tools/internal': ['*generator*', '*manager*', '*refactor*'],
            'tools/external': ['*git*', '*api*', '*deploy*'],
            'docs': ['*.md', '*.txt'],
            'tests': ['*test*.py', 'test_*.py']
        }
        
        for target_dir, patterns in rules.items():
            target_path = self.project_root / target_dir
            target_path.mkdir(parents=True, exist_ok=True)
            stats['created_dirs'] += 1
            
            for pattern in patterns:
                for file_path in self.project_root.rglob(pattern):
                    if file_path.is_file() and target_dir not in str(file_path):
                        try:
                            new_path = target_path / file_path.name
                            if not new_path.exists():
                                shutil.move(str(file_path), str(new_path))
                                logger.info(f"📦 Moved {file_path.name} to {target_dir}/")
                                stats['moved'] += 1
                        except Exception as e:
                            logger.warning(f"⚠️  Could not move {file_path}: {e}")
        
        logger.info(f"✅ Organization complete: {stats}")
        return stats
    
    def cleanup_empty_dirs(self) -> int:
        """Remove empty directories"""
        logger.info("🧹 Cleaning up empty directories...")
        
        removed = 0
        for dir_path in sorted(self.project_root.rglob('*'), reverse=True):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                    logger.info(f"🗑️  Removed empty directory: {dir_path}")
                    removed += 1
                except Exception as e:
                    logger.warning(f"⚠️  Could not remove {dir_path}: {e}")
        
        logger.info(f"✅ Removed {removed} empty directories")
        return removed
    
    def consolidate_documentation(self) -> bool:
        """Consolidate scattered documentation files"""
        logger.info("📚 Consolidating documentation...")
        
        docs_dir = self.project_root / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        # Find all markdown files
        md_files = list(self.project_root.rglob('*.md'))
        
        # Organize by category
        categories = {
            'api': [],
            'guides': [],
            'architecture': [],
            'other': []
        }
        
        for md_file in md_files:
            if 'docs' in str(md_file):
                continue
            
            content = md_file.read_text().lower()
            
            if 'api' in content or 'endpoint' in content:
                categories['api'].append(md_file)
            elif 'guide' in content or 'tutorial' in content or 'how to' in content:
                categories['guides'].append(md_file)
            elif 'architecture' in content or 'design' in content or 'system' in content:
                categories['architecture'].append(md_file)
            else:
                categories['other'].append(md_file)
        
        # Move files to appropriate subdirectories
        for category, files in categories.items():
            if not files:
                continue
            
            category_dir = docs_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for file_path in files:
                try:
                    new_path = category_dir / file_path.name
                    if not new_path.exists():
                        shutil.move(str(file_path), str(new_path))
                        logger.info(f"📄 Moved {file_path.name} to docs/{category}/")
                except Exception as e:
                    logger.warning(f"⚠️  Could not move {file_path}: {e}")
        
        logger.info("✅ Documentation consolidated")
        return True
    
    def create_index_files(self) -> int:
        """Create README.md index files in directories"""
        logger.info("📑 Creating index files...")
        
        created = 0
        for dir_path in self.project_root.rglob('*'):
            if not dir_path.is_dir():
                continue
            
            # Skip ignored directories
            if any(pattern in str(dir_path) for pattern in self.ignore_patterns):
                continue
            
            readme_path = dir_path / 'README.md'
            if not readme_path.exists():
                # List files in directory
                files = [f.name for f in dir_path.iterdir() if f.is_file()]
                
                if files:
                    content = f"""# {dir_path.name}

## Contents

"""
                    for file_name in sorted(files):
                        content += f"- `{file_name}`\n"
                    
                    readme_path.write_text(content)
                    logger.info(f"📑 Created index: {readme_path}")
                    created += 1
        
        logger.info(f"✅ Created {created} index files")
        return created

if __name__ == "__main__":
    print("📁 File Manager Tool")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent.parent
    manager = FileManager(project_root)
    
    print("\n🔍 Finding duplicate files...")
    duplicates = manager.find_duplicate_files()
    for file_hash, paths in duplicates[:5]:  # Show first 5
        print(f"  Duplicate set: {len(paths)} files")
        for path in paths:
            print(f"    - {path.relative_to(project_root)}")
    
    print("\n📂 Organizing files...")
    stats = manager.organize_files()
    print(f"  Moved: {stats['moved']} files")
    print(f"  Created: {stats['created_dirs']} directories")
    
    print("\n🧹 Cleaning up...")
    removed = manager.cleanup_empty_dirs()
    print(f"  Removed: {removed} empty directories")
    
    print("\n📚 Consolidating documentation...")
    manager.consolidate_documentation()
    
    print("\n📑 Creating index files...")
    created = manager.create_index_files()
    print(f"  Created: {created} index files")
    
    print("\n✅ File management complete!")
