import os
import hashlib
import shutil

AI_GODS_DIR = 'ai_gods'


def file_hash(filepath):
    """Generate SHA256 hash of file contents."""
    hash_sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def find_duplicates(dir_path):
    """Find duplicate files by content hash."""
    hash_map = {}
    duplicates = []

    for root, _, files in os.walk(dir_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            h = file_hash(filepath)
            if h in hash_map:
                duplicates.append((filepath, hash_map[h]))
            else:
                hash_map[h] = filepath
    return duplicates


def merge_files(original, duplicate):
    """
    Merge duplicate file into original.
    Since files are identical by hash, merge functionality is trivial (keep original).
    If future enhancements require merging different but similar files, this function can be extended.
    """
    # For now, just remove the duplicate file
    os.remove(duplicate)
    print(f'Removed duplicate file: {duplicate}')


def main():
    duplicates = find_duplicates(AI_GODS_DIR)
    if not duplicates:
        print('No duplicate AI God files found.')
        return

    print(f'Found {len(duplicates)} duplicate file(s). Merging...')

    for dup, orig in duplicates:
        merge_files(orig, dup)

    print('Duplicate AI God files merged successfully.')


if __name__ == '__main__':
    main()
