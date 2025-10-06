import os
import shutil
import datetime
import subprocess

# Configuration
BACKUP_ROOT = 'backups'
DATABASE_NAME = 'flowstate_ai_db'
DATABASE_USER = 'flowstate_user'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'
FILES_DIR = 'data'


def create_backup_dir():
    today = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_dir = os.path.join(BACKUP_ROOT, today)
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def backup_database(backup_dir):
    db_backup_path = os.path.join(backup_dir, f'{DATABASE_NAME}.sql')
    try:
        # Dump PostgreSQL database
        subprocess.run([
            'pg_dump',
            '-h', DATABASE_HOST,
            '-p', DATABASE_PORT,
            '-U', DATABASE_USER,
            '-F', 'c',  # custom format
            '-f', db_backup_path,
            DATABASE_NAME
        ], check=True, env={**os.environ, 'PGPASSWORD': os.getenv('DB_PASSWORD', '')})
        print(f'Database backup saved to {db_backup_path}')
    except subprocess.CalledProcessError as e:
        print(f'Error during database backup: {e}')


def backup_files(backup_dir):
    files_backup_path = os.path.join(backup_dir, 'files_backup')
    try:
        shutil.copytree(FILES_DIR, files_backup_path)
        print(f'Files backup saved to {files_backup_path}')
    except Exception as e:
        print(f'Error during files backup: {e}')


def main():
    backup_dir = create_backup_dir()
    backup_database(backup_dir)
    backup_files(backup_dir)


if __name__ == '__main__':
    main()
