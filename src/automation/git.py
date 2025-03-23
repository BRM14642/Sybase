import os
import subprocess
from dotenv import load_dotenv
from src.utils.logging_config import logger

load_dotenv()

class Git:

    def __init__(self):
        self.local_repos = os.getenv("LOCAL_REPOSITORY")

    def is_git_repo(self, folder):
        return os.path.isdir(os.path.join(folder, '.git'))

    def git_pull_develop(self, folder):
        try:
            self.run_command(['git', 'checkout', 'develop'], cwd=folder)
            self.run_command(['git', '-C', folder, 'pull'],  cwd=folder)
            logger.info(f'Successfully pulled in {folder}')
        except subprocess.CalledProcessError as e:
            logger.info(f'Failed to pull in {folder}: {e}')

    def git_pull(self, folder):
        try:
            subprocess.run(['git', '-C', folder, 'pull'], check=True)
            logger.info(f'Successfully pulled in {folder}')
        except subprocess.CalledProcessError as e:
            logger.info(f'Failed to pull in {folder}: {e}')

    def iterate_and_pull(self, base_dir):
        for folder_name in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder_name)
            if os.path.isdir(folder_path) and self.is_git_repo(folder_path):
                self.git_pull(folder_path)

    def iterate_and_reset(self, base_dir, exclude_dirs=None):
        if exclude_dirs is None:
            exclude_dirs = []
        for folder_name in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder_name)
            if os.path.isdir(folder_path) and self.is_git_repo(folder_path) and folder_name not in exclude_dirs:
                self.git_reset_hard(folder_path)

    def git_reset_hard(self, folder):
        try:
            self.run_command(['git', 'reset', '--hard', 'HEAD'], cwd=folder)
            logger.info(f'Successfully reset in {folder}')
        except subprocess.CalledProcessError as e:
            logger.info(f'Failed to reset in {folder}: {e}')

    def find_local_repo(self, base_dir, repo_name):
        for folder_name in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder_name)
            if os.path.isdir(folder_path) and self.is_git_repo(folder_path):
                if folder_name == repo_name:
                    return folder_path
        return None

    def clone_repo(self, repo_url, clone_dir):
        try:
            subprocess.run(['git', 'clone', repo_url, clone_dir], check=True)
            logger.info(f'Successfully cloned {repo_url} into {clone_dir}')
        except subprocess.CalledProcessError as e:
            logger.info(f'Failed to clone {repo_url}: {e}')

    def find_or_clone_repo(self, base_dir, repo_name, repo_url):
        local_repo_path = self.find_local_repo(base_dir, repo_name)
        if local_repo_path:
            logger.info(f'Repository {repo_name} found at {local_repo_path}')
            return local_repo_path
        else:
            user_input = input(f'Repository {repo_name} not found. Do you want to clone it? (yes/no): ')
            if user_input.lower() == 'yes':
                clone_dir = os.path.join(base_dir, repo_name)
                self.clone_repo(repo_url, clone_dir)
                return clone_dir
            else:
                logger.info('Repository not cloned.')
                return None

    def generate_clone_url(self, browse_url):
        clone_url = browse_url
        if 'projects' in browse_url:
            clone_url = clone_url.replace('projects', 'scm')
        if 'repos' in browse_url:
            clone_url = clone_url.replace('repos/', '')
        if 'browse' in browse_url:
            clone_url = clone_url.replace('/browse', '.git')
            return clone_url.lower()
        else:
            raise ValueError("Invalid browse URL")

    def update_branch(self, repo_path, branch_name):
        try:
            logger.info('git checkout develop')
            self.run_command(['git', 'checkout', 'develop'], cwd=repo_path)

            logger.info('git pull')
            self.run_command(['git', 'pull'], cwd=repo_path)

            logger.info(f'git checkout {branch_name}')
            self.run_command(['git', 'checkout', branch_name], cwd=repo_path)

            logger.info('git pull')
            self.run_command(['git', 'pull'], cwd=repo_path)

            logger.info('git merge develop -m Merge develop into feature')
            self.run_command(['git', 'merge', 'develop', '-m', 'Merge develop into feature'], cwd=repo_path)

            logger.info('git push')
            self.run_command(['git', 'push'], cwd=repo_path)

        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to update branch {branch_name}: {e}')


    def branch_exists(self, repo_path, branch_name):
        result = subprocess.run(['git', 'branch', '--list', branch_name], cwd=repo_path, text=True, capture_output=True)
        return branch_name in result.stdout

    def checkout_or_create_branch(self, repo_name, branch_name):
        try:
            repo_path = f'{self.local_repos}/{repo_name}'
            if self.branch_exists(repo_path, branch_name):
                logger.info(f'Branch {branch_name} exists. Checking out...')
                self.run_command(['git', 'checkout', branch_name], cwd=repo_path)
            else:
                logger.info(f'Branch {branch_name} does not exist. Creating and checking out...')
                self.run_command(['git', 'checkout', '-b', branch_name], cwd=repo_path)
        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to checkout or create branch {branch_name}: {e}')

    def git_add_commit_push(self, repo_name, branch_name, commit_message):
        try:
            repo_path = f'{self.local_repos}/{repo_name}'
            self.run_command(['git', 'add', '.'], cwd=repo_path)
            self.run_command(['git', 'commit', '-m', commit_message], cwd=repo_path)
            self.run_command(['git', 'push', '--set-upstream', 'origin', branch_name], cwd=repo_path)
        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to add, commit and push: {e}')

    def git_clean_repo(self, repo_name):
        try:
            repo_path = f'{self.local_repos}/{repo_name}'
            self.run_command(['git', 'clean', '-fd'], cwd=repo_path)
        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to add, commit and push: {e}')

    def run_command(self, command, cwd):
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
        if result.returncode == 0:
            logger.info(result.stdout.strip())
        else:
            logger.error(f'ERROR al ejecutar: {command} ==>>    {result.stderr.strip()}')
        result.check_returncode()