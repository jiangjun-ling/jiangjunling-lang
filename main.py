
### 2. main.py
#```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将军令语言 - 主入口文件
"""

import sys
import os
from pathlib import Path

# 添加核心模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '核心'))

from 词法分析器 import 将军令词法分析器
from 语法分析器 import 将军令语法分析器
from 解释器 import 将军令解释器


def 运行文件(文件路径):
    """运行指定的将军令文件"""
    try:
        with open(文件路径, 'r', encoding='utf-8') as f:
            源代码 = f.read()
        
        print(f"运行文件: {文件路径}")
        print("=" * 50)
        
        # 执行代码
        词法分析器 = 将军令词法分析器()
        语法分析器 = 将军令语法分析器()
        解释器 = 将军令解释器()
        
        令牌列表 = 词法分析器.分析(源代码)
        抽象语法树 = 语法分析器.解析程序(令牌列表)
        结果 = 解释器.解释(抽象语法树)
        
        print("=" * 50)
        print("执行完成!")
        return 结果
        
    except FileNotFoundError:
        print(f"错误: 文件不存在 {文件路径}")
    except Exception as e:
        print(f"执行错误: {e}")


def 交互模式():
    """启动交互式解释器"""
    print("将军令语言交互模式")
    print("输入 '退出' 或 'exit' 退出")
    
    词法分析器 = 将军令词法分析器()
    语法分析器 = 将军令语法分析器()
    解释器 = 将军令解释器()
    
    while True:
        try:
            输入 = input("将军令> ").strip()
            
            if 输入 in ['退出', 'exit', 'quit']:
                break
            if not 输入:
                continue
            
            # 执行单行代码
            令牌列表 = 词法分析器.分析(输入)
            抽象语法树 = 语法分析器.解析程序(令牌列表)
            结果 = 解释器.解释(抽象语法树)
            
            if 结果 is not None:
                print(结果)
                
        except KeyboardInterrupt:
            print("\n再见!")
            break
        except Exception as e:
            print(f"错误: {e}")


def 显示帮助():
    """显示使用帮助"""
    print("""
将军令语言使用说明:

用法:
    python main.py [文件路径]    # 运行将军令文件
    python main.py -i           # 启动交互模式
    python main.py -t           # 运行测试套件
    python main.py -h           # 显示帮助

示例:
    python main.py 示例/基础语法.jl
    python main.py -i
    """)


def 运行测试():
    """运行测试套件"""
    from 测试.测试套件 import 运行功能测试, 运行错误恢复测试, 运行性能测试
    
    print("开始运行将军令语言测试套件...")
    
    功能测试通过 = 运行功能测试()
    错误恢复测试通过 = 运行错误恢复测试() 
    性能测试通过 = 运行性能测试()
    
    if 功能测试通过 and 错误恢复测试通过 and 性能测试通过:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    if len(sys.argv) == 1:
        显示帮助()
    elif len(sys.argv) == 2:
        参数 = sys.argv[1]
        
        if 参数 == "-i" or 参数 == "--interactive":
            交互模式()
        elif 参数 == "-t" or 参数 == "--test":
            exit(运行测试())
        elif 参数 == "-h" or 参数 == "--help":
            显示帮助()
        else:
            # 当作文件路径处理
            if os.path.exists(参数):
                运行文件(参数)
            else:
                print(f"错误: 文件不存在 {参数}")
    else:
        显示帮助()