# Prediction interface for Cog ⚙️
# https://cog.run/python

from cog import BasePredictor, Input, Path
import torch
# import nemo.collections.asr as nemo_asr
# import torch.nn as nn
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook


# class Output(BaseModel):
#     path: Path

class Predictor(BasePredictor):
    def setup(self) -> None:
        #load pipeline
        self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token="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")

        #activate CUDA
        if torch.cuda.is_available():
            torch.set_default_tensor_type(torch.cuda.FloatTensor)
            self.pipeline.to(torch.device("cuda"))
            print("Using CUDA:", torch.cuda.get_device_name(0))
        else:
            print("CUDA is not available. Using CPU instead.")

    def predict(
        self,
        path_to_upload: Path = Input(
            description="Input audio file path for diarization"
        ),
    ) -> Path:
        """Run a single prediction on the model"""
        with ProgressHook() as hook:
            diarization = self.pipeline(path_to_upload, min_speakers=1, max_speakers=3, hook=hook)

        print("PRE")
        print(path_to_upload)
        # Dump the diarization output to disk using RTTM format
        # with output_rttm_path.open("w") as rttm:
        #     diarization.write_rttm(rttm)

        with open("/tmp/audio.txt", "w") as rttm:
            diarization.write_rttm(rttm)
        
        with open("/tmp/audio.txt", 'r') as f:
            print(f.read())

        # Prepare the output path for the RTTM file using Cog's Path
        # output_rttm_path = Output(file="/tmp/audio.rttm")

        print("POST")
        # print(output_rttm_path)
        # print(type(output_rttm_path))
        return Path("/tmp/audio.txt")
