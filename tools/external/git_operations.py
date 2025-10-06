import subprocess

class GitOperations:
    def __init__(self, repo_path='.'):
        self.repo_path = repo_path

    def _run_git_command(self, *args):
        result = subprocess.run(
            ['git', *args],
            cwd=self.repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git command failed: git {' '.join(args)}\n{result.stderr.strip()}")
        return result.stdout.strip()

    def status(self):
        return self._run_git_command('status', '--short')

    def auto_commit(self, message='Auto commit'):
        # Add all changes
        self._run_git_command('add', '--all')

        # Check if there is anything to commit
        status = self.status()
        if not status:
            # Nothing to commit
            return 'No changes to commit.'

        # Commit changes
        self._run_git_command('commit', '-m', message)
        return 'Committed changes.'

    def push(self, remote='origin', branch=None):
        if branch is None:
            branch = self.current_branch()
        self._run_git_command('push', remote, branch)
        return f'Pushed to {remote}/{branch}.'

    def pull(self, remote='origin', branch=None):
        if branch is None:
            branch = self.current_branch()
        self._run_git_command('pull', remote, branch)
        return f'Pulled from {remote}/{branch}.'

    def current_branch(self):
        branch = self._run_git_command('rev-parse', '--abbrev-ref', 'HEAD')
        return branch

    def list_branches(self):
        branches_raw = self._run_git_command('branch')
        branches = []
        for line in branches_raw.splitlines():
            # Current branch marked with *
            branches.append(line.strip().lstrip('* ').strip())
        return branches

    def create_branch(self, branch_name, checkout=False):
        self._run_git_command('branch', branch_name)
        if checkout:
            self.checkout_branch(branch_name)
        return f'Branch {branch_name} created.'

    def delete_branch(self, branch_name, force=False):
        if force:
            self._run_git_command('branch', '-D', branch_name)
        else:
            self._run_git_command('branch', '-d', branch_name)
        return f'Branch {branch_name} deleted.'

    def checkout_branch(self, branch_name):
        self._run_git_command('checkout', branch_name)
        return f'Checked out to {branch_name}.'
