from volcengine.viking_knowledgebase import VikingKnowledgeBaseService
from system_code.core.config import Config
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from loguru import logger


class RagSdk:
    def __init__(self):
        self.config = Config()
        self.ak = self.config.volcengine['ak']
        self.sk = self.config.volcengine['sk']
        self.collection = self.config.volcengine['collection_name']
        self.viking_knowledgebase_service = VikingKnowledgeBaseService(host="api-knowledgebase.mlp.cn-beijing.volces.com",
                                                                  scheme="https", connection_timeout=30,
                                                                  socket_timeout=30)
        self.viking_knowledgebase_service.set_ak(self.ak)
        self.viking_knowledgebase_service.set_sk(self.sk)

        self.deep_search_model = AutoModelForCausalLM.from_pretrained("Carey8175/InsightView-DeepSearch")
        self.deep_search_model.to('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained("Carey8175/InsightView-DeepSearch")
        self.eos_token = '<|deep_search_end|>'

    def init_deep_search_model(self):
        """
        Initialize the deep search model and tokenizer.
        """
        try:
            # add new tokens
            new_tokens = ['<|deep_search_start|>', '<|deep_search_end|>',
                          '<|sub0_start|>', '<|sub0_end|>',
                          '<|sub1_start|>', '<|sub1_end|>',
                          '<|sub2_start|>', '<|sub2_end|>',
                          '<|sub3_start|>', '<|sub3_end|>',
                          '<|sub4_start|>', '<|sub4_end|>']
            self.tokenizer.add_tokens(new_tokens)
            self.deep_search_model.resize_token_embeddings(len(self.tokenizer))

        except Exception as e:
            print(f"Error initializing deep search model: {e}")

    def apply_deep_search_template(self, query):
        """
        Apply the deep search template to the query.
        :param query:
        :return:
        """
        return f"<|deep_search_start|>{query}\n"

    def extract_sub_queries(self, response: str):
        """
        Extract sub-queries from the generated response.
        :param response:
        :return:
        """
        sub_queries = []

        for i in range(5):
            if f"<|sub{i}_start|>" in response and f"<|sub{i}_end|>" in response:
                start = response.index(f"<|sub{i}_start|>") + len(f"<|sub{i}_start|>")
                end = response.index(f"<|sub{i}_end|>")
                sub_query = response[start:end].strip()
                sub_queries.append(sub_query)

        return sub_queries


    def generate_sub_queries(self, query):
        """
        Perform a deep search using the initialized model and tokenizer.

        Args:
            query (str): The search query.

        Returns:
            str: The generated response from the deep search model.
        """
        if self.deep_search_model is None or self.tokenizer is None:
            logger.error("Deep search model and tokenizer must be initialized first.")
            return

        model_inputs = self.tokenizer([self.apply_deep_search_template(query)], return_tensors="pt").to(self.deep_search_model.device)
        outputs = self.deep_search_model.generate(
            **model_inputs,
            max_new_tokens=512,
            temperature=0.1,
            do_sample=True,
            eos_token_id=self.tokenizer.convert_tokens_to_ids(self.eos_token))
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, outputs)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=False)[0]

        return self.extract_sub_queries(response)

    def search(self, query, top_k=10, dense_weight=0.7):
        """
        Search for the most relevant documents in the collection based on the query.

        Args:
            query (str): The search query.
            top_k (int): The number of top results to return.
            dense_weight (float): The weight for the dense vector search.

        Returns:
            list: A list of dictionaries containing the search results.
        """
        try:
            response = self.viking_knowledgebase_service.search_knowledge(
                collection_name=self.collection,
                query=query,
                limit=top_k,
                dense_weight=dense_weight,
                project="default")

            return response['result_list']
        except Exception as e:
            print(f"Error during search: {e}")
            return []

    def deep_search(self, query, top_k=10, dense_weight=0.7):
        """
        Perform a deep search using the initialized model and tokenizer.

        Args:
            query (str): The search query.
            top_k (int): The number of top results to return.
            dense_weight (float): The weight for the dense vector search.

        Returns:
            list: A list of dictionaries containing the search results.
        """
        sub_queries = self.generate_sub_queries(query)
        results = []
        for sub_query in sub_queries:
            result = self.search(sub_query, top_k, dense_weight)
            results.extend(result)

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]  # Return top_k results

if __name__ == '__main__':
    sdk = RagSdk()
    res = sdk.search('How about the smell of the perfume?')
    deep_res = sdk.deep_search('How about the smell of the perfume?')
    print()