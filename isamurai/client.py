import requests
import time
import os
import base64
import json

class Isamurai:
    """
    Official Client for the iSamurai Face Swap API.
    """
    BASE_URL = "https://isamur.ai/api"

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Api-Key {self.api_key}"
        })

    def _to_base64(self, file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def _check_error(self, response):
        if not response.ok:
            try:
                error_data = response.json()
                msg = error_data.get('error', response.text)
            except:
                msg = response.text
            raise Exception(f"API Error ({response.status_code}): {msg}")

    # --- User ---
    def get_credits(self):
        """Get current subscription plan and credit balance."""
        response = self.session.get(f"{self.BASE_URL}/user-credits/")
        self._check_error(response)
        return response.json()

    # --- Face Swap (Single) ---
    def create_preview(self, source_path, target_path, enhance=False):
        """
        Generate a single-frame preview (Quick Face Swap).
        """
        data = {
            "source_image_base64": self._to_base64(source_path),
            "target_image_base64": self._to_base64(target_path),
            "enhance": enhance
        }
        response = self.session.post(f"{self.BASE_URL}/preview-swap-api/", json=data)
        self._check_error(response)
        return response.json()

    def process_face_swap(self, source_path, target_path, quality="720p", name="SDK Job", enhance=False):
        """
        Submit a Full Face Swap job (Video or Image).
        """
        files = {
            'source_image': open(source_path, 'rb'),
            'target_media': open(target_path, 'rb'),
        }
        data = {
            'gquality': quality,
            'name': name,
            'enhance': str(enhance).lower()
        }
        try:
            response = self.session.post(f"{self.BASE_URL}/full-process-swap/", files=files, data=data)
            self._check_error(response)
            return response.json()['faceswap']['id']
        finally:
            for f in files.values(): f.close()

    # --- Multi-Face Swap ---
    def analyze_frame(self, target_frame_path):
        """
        Detect all faces in a video frame for Multi-Swap.
        """
        data = {"target_image_base64": self._to_base64(target_frame_path)}
        response = self.session.post(f"{self.BASE_URL}/analyse-frame/", json=data)
        self._check_error(response)
        return response.json()['analysis']

    def process_multi_face_swap(self, target_path, analysis_results, quality="720p"):
        """
        Process a Multi-Face Swap video.
        :param analysis_results: List of dicts with 'person_id', 'source_image' (base64), etc.
        """
        files = {'target_media': open(target_path, 'rb')}
        data = {
            'gquality': quality,
            'analysis_results': json.dumps(analysis_results)
        }
        try:
            response = self.session.post(f"{self.BASE_URL}/multiple-face-swap/", files=files, data=data)
            self._check_error(response)
            return response.json()['faceswap']['id']
        finally:
            files['target_media'].close()

    # --- Slow Motion ---
    def create_slow_motion(self, video_path, slowdown_factor=4, quality="720p", mode="slowmo"):
        """
        Upload video and create Slow Motion project.
        :param mode: 'slowmo' (slower speed) or 'fps' (smoother motion, same speed)
        """
        files = {'source_video': open(video_path, 'rb')}
        data = {
            'slowdown_factor': slowdown_factor,
            'quality': quality,
            'mode': mode
        }
        try:
            response = self.session.post(f"{self.BASE_URL}/slowmotion/", files=files, data=data)
            self._check_error(response)
            return response.json()['slowmotion']['id']
        finally:
            files['source_video'].close()

    def process_slow_motion(self, project_id):
        """Start processing a Slow Motion project."""
        data = {"project_id": project_id}
        response = self.session.post(f"{self.BASE_URL}/faceswap/slowmotion/process/", json=data)
        self._check_error(response)
        return True

    # --- Image Restore ---
    def restore_image(self, image_path, mode="restore"):
        """
        Restore or enhance an image.
        :param mode: 'restore' (old photos) or 'face_enhance' (upscale faces)
        """
        files = {'image': open(image_path, 'rb')}
        data = {'mode': mode}
        try:
            response = self.session.post(f"{self.BASE_URL}/restore-image/", files=files, data=data)
            self._check_error(response)
            return response.json()
        finally:
            files['image'].close()

    # --- Gallery ---
    def upload_to_gallery(self, image_paths):
        """Upload source images to the Gallery."""
        files = [('images', open(p, 'rb')) for p in image_paths]
        try:
            response = self.session.post(f"{self.BASE_URL}/gallery/sources/", files=files)
            self._check_error(response)
            return response.json()
        finally:
            for _, f in files: f.close()

    # --- Utilities ---
    def get_job_status(self, job_id, multi=False):
        """Check status of FaceSwap or MultiSwap job."""
        params = {"id": job_id}
        if multi: params['multi'] = "True"
        response = self.session.get(f"{self.BASE_URL}/swap-progress/", params=params)
        self._check_error(response)
        return response.json()

    def wait_for_job(self, job_id, multi=False, interval=5, timeout=600):
        """BLOCKING: Wait for job to complete."""
        start = time.time()
        print(f"Polling job {job_id}...")
        while (time.time() - start) < timeout:
            status = self.get_job_status(job_id, multi)
            state = status.get('status')
            if state == 'Done': return status
            if state in ['Failed', 'Cancelled']: 
                raise Exception(f"Job Failed: {status.get('error')}")
            time.sleep(interval)
        raise TimeoutError("Job timed out")
