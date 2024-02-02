import torch, gc
import numpy as np

from transformers import AutoTokenizer, AutoModel
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Set
torch.manual_seed(2)


class MatchingAlgo:
    
    def __init__(self, model_path_or_name: str, max_length : int):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path_or_name, use_safetensors=True)
        self.model = AutoModel.from_pretrained(model_path_or_name, use_safetensors=True)
        self.max_length = max_length

    def _tokenization(self, sent:List[str])-> Dict[str, torch.Tensor]:
        """The function tokenize and create a pooled dictionary of all
        the individual sentences given in list of sentences.

        Args:
            sent (List[str]): List of sentences to be tokenized.

        Returns:
            Dict[List]: Dictionary of input ids and attetion mask.
        """        
        token = {'input_ids': [], 'attention_mask': []}
        for sentence in sent:
        # encode each sentence, append to dictionary
            new_token = self.tokenizer.encode_plus(sentence, max_length=self.max_length,
                                       truncation=True, padding='max_length',
                                       return_tensors='pt')
            token['input_ids'].append(new_token['input_ids'][0])
            token['attention_mask'].append(new_token['attention_mask'][0])
        # reformat list of tensors to single tensor
        token['input_ids'] = torch.stack(token['input_ids'])
        token['attention_mask'] = torch.stack(token['attention_mask'])
        return token
    
    def _model_pass(self, token: Dict[str, torch.Tensor])-> np.ndarray:

        """Generate embeddings of all the sentences and pool the given output.

        Returns:
            np.array: Numpy array of individual sentence embeddings.
        """
        output = self.model(**token)
        embeddings = output.last_hidden_state
        att_mask = token['attention_mask']
        mask = att_mask.unsqueeze(-1).expand(embeddings.size()).float()
        mask_embeddings = embeddings * mask # nullify non required signal
        summed = torch.sum(mask_embeddings, 1)
        summed_mask = torch.clamp(mask.sum(1), min=1e-9)
        mean_pooled = summed / summed_mask
        mean_pooled = mean_pooled.detach().numpy()
        return mean_pooled
        
        
    def _find_similar_sentences(self, mean_pooled : np.ndarray) -> np.ndarray :
        """Compute similarity between pair on embeddings.

        Args:
            mean_pooled (np.ndarray): Mean pooler output of couple of strings for which similarity is required.

        Returns:
            nd.ndarray: similarity array
        """        
        similarity_array = cosine_similarity(
                [mean_pooled[0]],
                [mean_pooled[1]]
                )
        return similarity_array
    

    def section_score(self, string1: str, string2: str) -> float:
        """Take two sentences tokenize them and generate emebddings by transformer and denoise with mask and 
        compute cosine similarity and return score.

        Args:
            string1 (str): First string to be matched
            string2 (str):  Second string to be matched

        Returns:
            float: cosine similarity between strings
        """        
        sentences = [string1, string2]
        # initialize dictionary: stores tokenized sentences
        tokens = self._tokenization(sentences)
        mean_pooled = self._model_pass(tokens)
        similarity = self._find_similar_sentences(mean_pooled)
        gc.collect()
        return float(similarity[0][0])