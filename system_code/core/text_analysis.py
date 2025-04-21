import os
import joblib
from system_code.core.config import Config


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


class TextAnalysis:
    def __init__(self):
        self.bot_classifier = BotClassifier()
        self.sentiment_classifier = SentimentClassifier()

    def single_process(self, text: str):
        """执行各项文本分析任务， 返回3种分析结果"""
        sentiment = self.sentiment_classifier.predict(text)
        is_real = self.bot_classifier.predict(text)



        return sentiment, is_real, ''

    def text_analyse(self, df):
        """df is a pandas dataframe, include: id, text"""
        df['sentiment'], df['real_review'], df['summary'] = zip(*df['text'].map(self.single_process))
        return df


if __name__ == "__main__":
    print(TextAnalysis().single_process("I hate this"))
