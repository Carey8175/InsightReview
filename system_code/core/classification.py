import os
import joblib
from system_code.core.config import Config


class Classifier:
    def __init__(self):
        # 加载保存的模型
        self.model = joblib.load(os.path.join(Config.STATICS_PATH, 'models', 'logistic_regression_model.pkl'))  # 替换为您的模型路径
        # 加载保存的TF-IDF向量化器
        self.vectorizer = joblib.load(os.path.join(Config.STATICS_PATH, 'models', 'tfidf_vectorizer.pkl'))   # 替换为您的TF-IDF路径

    def predict(self, text: str) -> str:
        """
        预测输入的文本是否为虚假信息。
        
        参数:
        text (str): 输入的文本

        返回:
        str: "FR" 表示虚假信息，"RR" 表示真实信息
        """
        # 将输入文本转换为TF-IDF特征
        text_tfidf = self.vectorizer.transform([text])
        
        # 使用模型进行预测
        prediction = self.model.predict(text_tfidf)
        
        # 根据预测结果返回 "FR" 或 "RR"
        if prediction == 0:
            return "FR"  # 0 表示虚假信息
        else:
            return "RR"  # 1 表示真实信息

