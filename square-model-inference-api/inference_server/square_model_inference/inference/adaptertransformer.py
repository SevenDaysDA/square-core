import json

from loguru import logger

from transformers import AutoModelWithHeads, list_adapters

from square_model_inference.inference.transformer import Transformer
from square_model_inference.models.request import PredictionRequest, Task

from square_model_inference.models.prediction import PredictionOutput


class AdapterTransformer(Transformer):
    """
    The class for all adapter-based models using the adapter-transformers package
    """
    def __init__(self, model_name, batch_size, disable_gpu, transformers_cache, max_input_size, **kwargs):
        """
        Initialize the Adapter with its underlying Transformer and pre-load all available adapters from adapterhub.ml
        :param model_name: the Huggingface model name
        :param batch_size: batch size used for inference
        :param disable_gpu: do not move model to GPU even if CUDA is available
        :param transformers_cache: Should be same as TRANSFORMERS_CACHE env variable.
        This folder will be used to store the adapters
        :param max_input_size: requests with a larger input are rejected
        :param kwargs: Not used
        """
        self._load_model(AutoModelWithHeads, model_name, disable_gpu)
        self._load_adapter(model_name, transformers_cache)
        self.batch_size = batch_size
        self.max_input_size = max_input_size

    def _load_adapter(self, model_name, transformers_cache):
        """
        Pre-load all available adapters for MODEL_NAME from adapterhub.ml.
        We parse the hub index to extract all names and then load each model.
        """
        logger.info("Loading all available adapters")
        adapter_infos = [info for info in list_adapters(source="ah") if info.model_name==model_name]
        adapters = set(f"{adapter_info.task}/{adapter_info.subtask}@{adapter_info.username}" for adapter_info in adapter_infos)
        for adapter in adapters:
            logger.debug(f"Loading adapter {adapter}")
            try:
                self.model.load_adapter(adapter, load_as=adapter, with_head=True, cache_dir=transformers_cache)
            except RuntimeError as e:
                if "Error(s) in loading state_dict" in e.args[0]:
                    logger.debug(f"Could not load {adapter} due to missing label_ids in config resulting in exception:\n{e.args[0]}")
                else:
                    raise e

# def _load_single_adapter(self, adapter_name: str):
    #     if adapter_name not in self.model.config.adapters.adapters:
    #         logger.info(f"Loading new adapter {adapter_name}")
    #         self.model.load_adapter(adapter_name, with_head=True, load_as=adapter_name)
    #     else:
    #         logger.debug(f"Adapter {adapter_name} is already loaded. Not loading again")

    def _token_classification(self, request: PredictionRequest) -> PredictionOutput:
        # We only have to change the label2id mapping from config.label2id (what super() uses) to the mapping
        # of the chosen head
        prediction = super()._token_classification(request)

        label2id = self.model.config.prediction_heads[request.adapter_name]["label2id"]
        id2label = {v:k for k,v in label2id.items()}
        prediction.id2label = id2label

        return prediction

    def _sequence_classification(self, request: PredictionRequest) -> PredictionOutput:
        # We only have to change the label2id mapping from config.label2id (what super() uses) to the mapping
        # of the chosen head
        prediction = super()._sequence_classification(request)

        label2id = self.model.config.prediction_heads[request.adapter_name]["label2id"]
        id2label = {v:k for k,v in label2id.items()}
        prediction.id2label = id2label

        return prediction

    async def predict(self, request: PredictionRequest, task: Task) -> PredictionOutput:
        if request.is_preprocessed:
            raise ValueError("is_preprocessed=True is not supported for this model. Please use text as input.")
        if len(request.input) > self.max_input_size:
            raise ValueError(f"Input is too large. Max input size is {self.max_input_size}")
        if not request.adapter_name or request.adapter_name not in self.model.config.adapters.adapters:
            raise ValueError(f"Unknown or missing adapter {request.adapter_name}. "
                       f"Please provider a fully specified adapter name from adapterhub.ml")
        self.model.set_active_adapters(request.adapter_name)

        if task == Task.sequence_classification:
            return self._sequence_classification(request)
        elif task == Task.token_classification:
            return self._token_classification(request)
        elif task == Task.question_answering:
            return self._question_answering(request)
        elif task == Task.embedding:
            return self._embedding(request)
        elif task == Task.generation:
            return self._generation(request)

