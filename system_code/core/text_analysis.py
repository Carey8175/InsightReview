import os
import joblib
from system_code.core.config import Config
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


class SentimentClassifier:
    def __init__(self):
        self.model = joblib.load(os.path.join(Config.STATICS_PATH, 'models', 'logistic_regression_sentiment_model.pkl'))
        self.vectorizer = joblib.load(os.path.join(Config.STATICS_PATH, 'models', 'tfidf_sentiment_vectorizer.pkl'))

    def predict(self, text: str) -> str:
        """
        Input:Str
        Otuput:positive neutral negative

        """

        text_tfidf = self.vectorizer.transform([text])

        prediction = self.model.predict(text_tfidf)

        return prediction[0]


class BotClassifier:
    def __init__(self):
        # 加载保存的模型
        self.model = joblib.load(
            os.path.join(Config.STATICS_PATH, 'models', 'logistic_regression_model.pkl'))  # 替换为您的模型路径
        # 加载保存的TF-IDF向量化器
        self.vectorizer = joblib.load(
            os.path.join(Config.STATICS_PATH, 'models', 'tfidf_vectorizer.pkl'))  # 替换为您的TF-IDF路径

    def predict(self, text: str) -> int:
        """
        预测输入的文本是否为虚假信息。

        参数:
        text (str): 输入的文本

        返回:
        str: "0" 表示虚假信息，"1" 表示真实信息
        """
        # 将输入文本转换为TF-IDF特征
        text_tfidf = self.vectorizer.transform([text])

        # 使用模型进行预测
        prediction = self.model.predict(text_tfidf)

        return int(prediction)


class TitleClassifier:
    def __init__(self):
        # Load model and tokenizer from Hugging Face
        model_name = 'Carey8175/InsightView-Title'
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        # Use GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval() # Set model to evaluation mode

        self.eos_token = self.tokenizer.convert_tokens_to_ids('<|im_end|>')

    def predict(self, text: str) -> str:
        """
        Predicts the title category for the input text.

        Args:
            text (str): The input text (e.g., review title).

        Returns:
            str: The predicted title category.
        """
        test = '<|im_start|>' + text + '<|im_end|>\n<|im_start|>'

        inputs = self.tokenizer([text], return_tensors="pt", truncation=True, padding=True, max_length=512).to(self.device)

        generated_ids = self.model.generate(
            **inputs,
            temperature=0.01,
            max_new_tokens=50,
            eos_token_id=self.eos_token,
            do_sample=True)

        # Decode the generated tokens to get the predicted class
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        output_text = self.tokenizer .batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        return output_text

class TextAnalysis:
    def __init__(self):
        self.bot_classifier = BotClassifier()
        self.sentiment_classifier = SentimentClassifier()
        self.title_classifier = TitleClassifier() # Add title classifier instance

    def single_process(self, text: str):
        """执行各项文本分析任务， 返回3种分析结果"""
        sentiment = self.sentiment_classifier.predict(text)
        is_real = self.bot_classifier.predict(text)
        title = self.title_classifier.predict(text) # Get title prediction


        return sentiment, is_real, title # Update return value

    def text_analyse(self, df):
        """df is a pandas dataframe, include: id, text"""
        df['sentiment'], df['real_review'], df['summary'] = zip(*df['text'].map(self.single_process))
        return df


if __name__ == "__main__":
    titles = TitleClassifier()
    print(titles.predict("I love this product!"))

    print(TextAnalysis().single_process("I hate this"))
