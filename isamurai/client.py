import requests
import time
import os

class Isamurai:
    """
    Client for the iSamurai Face Swap API.
    """
    BASE_URL = "https://isamur.ai/api"

    def __init__(self, api_key):
        """
        Initialize the iSamurai client.
        
        :param api_key: Your API Key (starts with 'isk_')
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Api-Key {self.api_key}"
        })

    def get_credits(self):
        """
        Get current subscription plan and credit balance.
        
        :return: Dict containing 'credits' and 'plan'.
        """
        response = self.session.get(f"{self.BASE_URL}/user-credits/")
        self._check_error(response)
        return response.json()

    def process_face_swap(self, source_path, target_path, quality="720p", name="SDK Job"):
        """
        Submit a Face Swap job.
        
        :param source_path: Path to the source face image.
        :param target_path: Path to the target video or image.
        :param quality: Output quality ('480p', '720p', '1080p'). Default '720p'.
        :param name: Optional name for the job.
        :return: The Job ID (str).
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Target file not found: {target_path}")

        files = {
            'source_image': open(source_path, 'rb'),
            'target_media': open(target_path, 'rb'),
        }
        data = {
            'gquality': quality,
            'name': name
        }

        try:
            response = self.session.post(f"{self.BASE_URL}/full-process-swap/", files=files, data=data)
            self._check_error(response)
            result = response.json()
            if 'faceswap' in result:
                return result['faceswap']['id']
            raise Exception(f"Unexpected response format: {result}")
        finally:
            for f in files.values():
                f.close()

    def get_job_status(self, job_id):
        """
        Check the status of a specific job.
        
        :param job_id: The ID of the job to check.
        :return: Dict containing 'status', 'progress_percentage', 'output_media_url', etc.
        """
        response = self.session.get(f"{self.BASE_URL}/swap-progress/?id={job_id}")
        self._check_error(response)
        return response.json()

    def wait_for_job(self, job_id, interval=5, timeout=600):
        """
        Poll the job status until it completes or fails.
        
        :param job_id: Job ID to monitor.
        :param interval: Seconds between checks.
        :param timeout: Maximum seconds to wait.
        :return: Final status dict with 'output_media_url'.
        :raises TimeoutError: If timeout is reached.
        :raises Exception: If job fails.
        """
        start_time = time.time()
        print(f"Waiting for job {job_id}...")
        
        while (time.time() - start_time) < timeout:
            status = self.get_job_status(job_id)
            state = status.get('status')
            
            if state in ['Done', 'complete']:
                return status
            
            if state in ['Failed', 'failed']:
                error = status.get('error', 'Unknown error')
                raise Exception(f"Job failed: {error}")
            
            time.sleep(interval)
            
        raise TimeoutError(f"Job timed out after {timeout} seconds")

    def _check_error(self, response):
        if not response.ok:
            try:
                error_data = response.json()
                msg = error_data.get('error', response.text)
            except:
                msg = response.text
            raise Exception(f"API Error ({response.status_code}): {msg}")
