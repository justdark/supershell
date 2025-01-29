from .utils import get_llm_output_with_api_address
from pathlib import Path
import json
import subprocess
import sys
class ReActAgent:
    """ReAct范式的Agent类，实现思考-行动-观察的循环"""
    
    def __init__(self,config_path):
        self.thought_history = []
        self.action_history = []
        # 存储prompt模板的字典
        self.prompts = {}
        self.config = json.loads(open(config_path,"r").read())
        # 读取prompts文件夹下的所有md文件
        # 获取当前脚本所在目录
        current_dir = Path(__file__).parent
        prompt_dir = current_dir / "prompts"
        for file_path in prompt_dir.glob("*.md"):
            # 获取文件名(不含后缀)作为key
            prompt_name = file_path.stem
            # 读取文件内容作为value
            with open(file_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()
                
            self.prompts[prompt_name] = prompt_content
    def llm_for_output(self,prompt):
        response = get_llm_output_with_api_address(prompt,self.config["api_address"],self.config["model_name"],self.config["access_key"])
        output = json.loads(response.split("【最终输出json】")[1].replace("```json","").replace("```",""))
        return output
    def process(self, nlp_command,history = [],current_step = 0, max_step = 10):
        prompt = self.prompts["rethink"]
        historyInfo = self.historyFormat(history)
        prompt = self.promptFormat(prompt,{"target":nlp_command,"history_command_rst":historyInfo})
        result = self.llm_for_output(prompt)
        if "reason" in result:
            return "无法完成目标："+result["reason"]
        elif "enquiry" in result:
            query_result = self.query(result["enquiry"])
            history.append({"query":result["enquiry"],"query_rst":query_result})            
            return self.process(nlp_command,history,current_step+1,max_step)            
        elif "context_commands" in result:
            commands = result["context_commands"]
            targets = result["commands_target"]
            if "warnning" in result and len(result["warnning"])>0:
                print("警告：",result["warnning"])
                confirm = input("是否继续执行？(y/n)")
                if confirm != "y" and confirm!="Y":
                    return "用户拒绝执行"
            print("-"*20)
            print("正在执行：",targets)
            executeRst = self.execute(commands)
            history.append({"commands":commands,"execute_rst":executeRst,"targets":targets})            
            result = self.process(nlp_command,history,current_step+1,max_step)
            print(result)
            return result
        elif "commands" in result:
            commands = result["commands"]
            targets = result["commands_target"]
            if "warnning" in result and len(result["warnning"])>0:
                print("警告：",result["warnning"])
                confirm = input("是否继续执行？(y/n)")
                if confirm != "y" and confirm!="Y":
                    return "用户拒绝执行"
            print("-"*20)
            print("正在执行：",targets)
            executeRst = self.execute(commands)
            print(executeRst)
            return executeRst    
        else:
            print(result)
            print("无法解析LLM输出")
            assert 1==2
        return result
        
    def historyFormat(self,historys):
        if len(historys)==0:
            return "无历史执行记录"
        output_historys = []
        for h in historys:
            if "commands" in h:
                output_historys.append("- 执行命令`{}`".format(h["commands"])+"\n  - 执行目的：{}\n  - 执行结果：\n```\n{}\n```".format(h["targets"],h["execute_rst"]))
            elif "query" in h:
                output_historys.append("- 询问用户 `{}`".format(h["query"])+"\n  - 用户回应：\n```\n{}\n```".format(h["query_rst"]))
        return "\n".join(output_historys)
            
    def query(self,query):
        # print(query)
        rst = input(query)
        return rst
    def promptFormat(self,prompt,params):
        # 遍历params字典，将键值对替换到prompt中
        for key, value in params.items():
            prompt = prompt.replace("{{" + key + "}}", value)
        return prompt

    def rethink(self):
        pass
        
    def execute(self, commands,indent = 0):
        # 如果commands是字符串，转换为列表
        if isinstance(commands, str):
            commands = [commands]            
        # 存储所有命令执行结果
        results = []
        
        
        # 逐个执行命令
        for cmd in commands:
            try:
                print("尝试执行命令：",cmd)
                # 执行shell命令并获取输出
                # 使用shlex.split对命令进行安全分割，防止命令注入
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()                
                # 如果有错误输出，添加到结果中
                if stderr:
                    results.append(f"{stderr}")
                # 添加标准输出到结果中
                if stdout:
                    results.append(stdout)
                
            except Exception as e:
                results.append(f"执行出错: {str(e)}")
        # print("执行结果：","\n".join(results))
        # 返回所有结果拼接的字符串
        return "\n".join(results)

if __name__ == "__main__":
    agent = ReActAgent()
    # agent.process("如果当前目录下有txt文件，把所有文件内容都拼接到一起；没有的话，结果文件内容是“没有文件”")
    # agent.process("系统设置为暗色模式")
    # agent.process("系统设置为暗色模式")
    # agent.process("当前目录下的txt文件打包成tar.gz文件")
    # agent.process("解压 ./x.tar.gz")
    if len(sys.argv) > 1:
        # 将所有参数组合成一个命令字符串
        command = " ".join(sys.argv[1:])
        print(f"正在执行您的指令: {command}")
        result = agent.process(command)
        print(f"执行结果: \n{result}")
    else:
        print("请提供要执行的命令")
    