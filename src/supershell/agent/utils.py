import os
import requests

from typing import Dict, Any

def call_openai_style_api(prompt: str,api_url:str = None,model: str = None, api_key: str = None) -> Dict[Any, Any]:
    """调用DeepSeek API接口获取响应
    
    Args:
        prompt: 输入的prompt文本
        api_key: DeepSeek API密钥,默认从环境变量获取
        
    Returns:
        Dict: API返回的响应结果
    """
    # 获取API密钥
    if not api_key or not api_url:
        raise ValueError("需要提供DeepSeek API密钥")
            
    # API请求地址    
    # 构造请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 构造请求体
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        # 发送POST请求
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        # print(response.json())
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"调用DeepSeek API失败: {str(e)}")
def get_llm_output(prompt,model = "deepseek-chat",api_key = None):
    # 调用DeepSeek API接口获取响应    
    return call_openai_style_api(prompt,"https://api.deepseek.com/v1/chat/completions", model,api_key)
def get_llm_output_with_api_address(prompt,api = "deepseek",model = "deepseek-chat",api_key = None):
    # 调用DeepSeek API接口获取响应
    if api=="deepseek":
        api = "https://api.deepseek.com/v1/chat/completions"
    elif api=="openai":
        api = "https://api.openai.com/v1/chat/completions"
    return call_openai_style_api(prompt,api, model,api_key)