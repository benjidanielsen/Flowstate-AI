import subprocess
import os
import logging
import requests

class DevOpsAgent:
    def __init__(self, ci_cd_config_path='ci_cd_config.yaml', monitoring_url=None, infra_repo_path='infra'):
        self.ci_cd_config_path = ci_cd_config_path
        self.monitoring_url = monitoring_url
        self.infra_repo_path = infra_repo_path
        logging.basicConfig(level=logging.INFO)

    def deploy(self, environment='staging'):
        logging.info(f'Starting deployment to {environment}')
        try:
            # Example: running deployment script
            result = subprocess.run(['./deploy.sh', environment], cwd=os.getcwd(), capture_output=True, text=True)
            if result.returncode != 0:
                logging.error(f'Deployment failed: {result.stderr}')
                return False
            logging.info(f'Deployment succeeded: {result.stdout}')
            return True
        except Exception as e:
            logging.error(f'Exception during deployment: {e}')
            return False

    def run_ci_cd_pipeline(self):
        logging.info('Running CI/CD pipeline')
        try:
            # Example: run CI/CD command or script defined in config
            result = subprocess.run(['./ci_cd_pipeline.sh'], cwd=os.getcwd(), capture_output=True, text=True)
            if result.returncode != 0:
                logging.error(f'CI/CD pipeline failed: {result.stderr}')
                return False
            logging.info(f'CI/CD pipeline succeeded: {result.stdout}')
            return True
        except Exception as e:
            logging.error(f'Exception during CI/CD pipeline: {e}')
            return False

    def monitor(self):
        if not self.monitoring_url:
            logging.warning('No monitoring URL configured')
            return None
        logging.info(f'Fetching monitoring data from {self.monitoring_url}')
        try:
            response = requests.get(self.monitoring_url)
            response.raise_for_status()
            data = response.json()
            logging.info(f'Monitoring data received: {data}')
            return data
        except Exception as e:
            logging.error(f'Error fetching monitoring data: {e}')
            return None

    def update_infrastructure(self, commit_message='Update infrastructure'):
        logging.info('Updating infrastructure repository')
        try:
            # Pull latest changes
            subprocess.run(['git', 'pull'], cwd=self.infra_repo_path, check=True)
            # Add changes
            subprocess.run(['git', 'add', '.'], cwd=self.infra_repo_path, check=True)
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_message], cwd=self.infra_repo_path, check=True)
            # Push changes
            subprocess.run(['git', 'push'], cwd=self.infra_repo_path, check=True)
            logging.info('Infrastructure updated and pushed successfully')
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f'Git command failed: {e}')
            return False
        except Exception as e:
            logging.error(f'Exception during infrastructure update: {e}')
            return False

    def full_pipeline(self):
        logging.info('Starting full DevOps pipeline')
        if not self.run_ci_cd_pipeline():
            logging.error('CI/CD pipeline failed, aborting deployment')
            return False
        if not self.deploy():
            logging.error('Deployment failed')
            return False
        monitoring_data = self.monitor()
        if monitoring_data is None:
            logging.warning('Monitoring data unavailable')
        if not self.update_infrastructure():
            logging.warning('Failed to update infrastructure repository')
        logging.info('Full DevOps pipeline completed')
        return True


if __name__ == '__main__':
    agent = DevOpsAgent(monitoring_url='http://localhost:9000/api/metrics')
    agent.full_pipeline()
