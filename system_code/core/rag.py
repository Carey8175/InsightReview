import json
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials
import re


class RAG:
    def __init__(self, ak, sk, domain, account_id):
        self.ak = ak
        self.sk = sk
        self.domain = domain
        self.account_id = account_id

    def prepare_request(self, method, path, params=None, data=None, doseq=0):
        # 创建请求
        if params:
            for key in params:
                if isinstance(params[key], (int, float, bool)):
                    params[key] = str(params[key])
                elif isinstance(params[key], list) and not doseq:
                    params[key] = ",".join(params[key])
        
        r = Request()
        r.set_shema("https")
        r.set_method(method)
        r.set_connection_timeout(10)
        r.set_socket_timeout(10)
        mheaders = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Host": self.domain,
            "V-Account-Id": self.account_id,
        }
        r.set_headers(mheaders)
        if params:
            r.set_query(params)
        r.set_host(self.domain)
        r.set_path(path)
        if data is not None:
            r.set_body(json.dumps(data))
        
        # 生成签名
        credentials = Credentials(self.ak, self.sk, "air", "cn-north-1")
        SignerV4.sign(r, credentials)
        return r

    def search(self, query, name, limit=5, rerank_switch=False, dense_weight=0.5):
        # 创建搜索请求的请求体
        path = "/api/knowledge/collection/search"
        request_params = {
            "name": name,
            "query": query,
            "limit": limit,
            "rerank_switch": rerank_switch,

            "dense_weight": dense_weight
        }
        info_req = self.prepare_request(method="POST", path=path, data=request_params)
        
        # 发送请求
        rsp = requests.request(
            method=info_req.method,
            url=f"https://{self.domain}{info_req.path}",
            headers=info_req.headers,
            data=info_req.body
        )
        return rsp.json()



    def retrieval(self, texts: list, topk=5):
        """
        检索相似的文本
        输入: ['hello', 'world']
        输出: [["t1", ... "t_topk"], ["s1", ... "s_topk"]]
        """
        results = []
        for text in texts:
            # 调用 search 函数进行检索
            search_results = self.search(query=text, name="RAG", limit=topk)
            
            result_list = []
            for item in search_results.get("data", {}).get("result_list", []):
                original_content = item["content"]
                # 正则替换：去除开头的 'text:' 和结尾的 '\nasin:' 及其后内容
                # 在此正则中，我们用 re.DOTALL 来匹配换行符
                cleaned_content = re.sub(r'^text:', '', re.sub(r'(\n?)(asin:.*)$', '', original_content, flags=re.DOTALL))

                result_list.append(cleaned_content)
            
            results.append(result_list)
        return results

    def rerank(self, query, results: list) -> list:
        """
        对检索结果进行重排。
        
        参数:
        - query: 输入的查询文本
        - results: 检索到的文本列表，每个元素是一个字符串
        
        返回:
        - list: 包含每个文本的重排分数
        """
        # 构造请求数据
        datas = []
        for result in results:
            datas.append({
                "query": query,
                "content": result,  # 使用文本内容
                "title": "无"  # 假设没有标题的情况下填充为"无"
            })
        
        request_data = {
            "datas": datas
        }

        # 将请求数据转换为 JSON 字符串
        request_json = json.dumps(request_data)
        
        # 使用 prepare_request 来生成签名并发起请求
        path = "/api/knowledge/service/rerank"
        info_req = self.prepare_request(method="POST", path=path, data=request_data)
        
        # 发送请求
        response = requests.request(
            method=info_req.method,
            url=f"https://{self.domain}{info_req.path}",
            headers=info_req.headers,
            data=info_req.body
        )
        
        # 打印调试信息，查看返回的数据结构
        # print("Response JSON:", response.json())  # 打印完整的响应
        
        # 处理响应
        if response.status_code == 200:
            response_data = response.json()
            
            # 检查是否有返回数据
            if response_data.get("code") == 0:
                # 获取返回的分数列表
                scores = response_data.get("data", {}).get("scores", [])
                
                # 判断是否有正确的分数数据
                if isinstance(scores, list) and len(scores) == len(results):
                    reranked_results = [{"text": result, "score": float(score)} 
                                        for result, score in zip(results, scores)]
                    
                    reranked_results = sorted(reranked_results, key=lambda x: x['score'], reverse=True)

                    return reranked_results
                else:
                    raise Exception("错误：返回的分数数量与结果数量不匹配。")
            else:
                raise Exception(f"重排请求失败：{response_data.get('message')}")
        else:
            raise Exception(f"请求失败，HTTP 状态码: {response.status_code}, {response.text}")
