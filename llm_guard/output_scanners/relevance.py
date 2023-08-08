import logging

from sentence_transformers import SentenceTransformer, util

from .base import Scanner

log = logging.getLogger(__name__)
_transformer_name = "sentence-transformers/all-MiniLM-L6-v2"


class Relevance(Scanner):
    """
    A class used to scan the relevance of the output of a language model to the input prompt.

    This class uses SentenceTransformers to encode the prompt and output into vector embeddings, then computes
    the cosine similarity between them. If the similarity is below a given threshold, the output is considered
    not relevant to the prompt.
    """

    def __init__(self, threshold: float = 0):
        """
        Initializes an instance of the Relevance class.

        Parameters:
            threshold (float): The minimum cosine similarity (-1 to 1) between the prompt and output for the output to
                              be considered relevant.
        """

        self._threshold = threshold
        self._transformer_model = SentenceTransformer(_transformer_name)

    def scan(self, prompt: str, output: str) -> (str, bool):
        if output.strip() == "":
            return output, True

        similarity = 1
        try:
            embedding_1 = self._transformer_model.encode(prompt, convert_to_tensor=True)
            embedding_2 = self._transformer_model.encode(output, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(embedding_1, embedding_2)
        except Exception as e:
            log.warning(f"pandas {output} caused similarity_MiniLM_L6_v2 to encounter error: {e}")

        if similarity.item() < self._threshold:
            log.warning(
                f"Result is not similar to the prompt. Score {similarity.item}, threshold {self._threshold}"
            )

            return output, False

        log.debug(
            f"Result is similar to the prompt. Score {similarity.item}, threshold {self._threshold}"
        )

        return output, True
