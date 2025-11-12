# -*- coding: utf-8 -*-
"""
将军令语言 - 解释器
执行抽象语法树
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from 抽象语法树 import *


class 解释错误(Exception):
    def __init__(self, 消息, 行号=0, 列号=0):
        super().__init__(f"解释错误（第{行号}行，第{列号}列）: {消息}")
        self.行号 = 行号
        self.列号 = 列号


class 执行环境:
    def __init__(self, 父环境=None):
        self.变量表 = {}
        self.函数表 = {}
        self.父环境 = 父环境
        self.内置函数 = self.初始化内置函数()
    
    def 初始化内置函数(self):
        return {
            "报": self.内置_报,
            "长度": self.内置_长度,
            "类型": self.内置_类型,
            "范围": self.内置_范围,
        }
    
    def 设置变量(self, 名称, 值):
        self.变量表[名称] = 值
    
    def 获取变量(self, 名称):
        if 名称 in self.变量表:
            return self.变量表[名称]
        
        if 名称 in self.内置函数:
            return self.内置函数[名称]
        
        if self.父环境:
            return self.父环境.获取变量(名称)
        
        raise NameError(f"未定义变量或函数: {名称}")
    
    def 设置函数(self, 名称, 函数节点):
        self.函数表[名称] = 函数节点
    
    def 获取函数(self, 名称):
        if 名称 in self.函数表:
            return self.函数表[名称]
        elif self.父环境:
            return self.父环境.获取函数(名称)
        else:
            raise NameError(f"未定义函数: {名称}")
    
    def 内置_报(self, *参数列表):
        结果 = " ".join(str(参数) for 参数 in 参数列表)
        print(结果)
        return 结果
    
    def 内置_长度(self, 集合):
        if isinstance(集合, (list, str)):
            return len(集合)
        else:
            raise TypeError(f"无法获取类型 {type(集合)} 的长度")
    
    def 内置_类型(self, 值):
        类型映射 = {
            int: "整数", 
            float: "小数", 
            str: "字符串",
            list: "列表", 
            bool: "布尔", 
            type(None): "空"
        }
        return 类型映射.get(type(值), "未知")
    
    def 内置_范围(self, 开始, 结束=None, 步长=1):
        if 结束 is None:
            return list(range(开始))
        else:
            return list(range(开始, 结束, 步长))


class 将军令解释器:
    def __init__(self):
        self.全局环境 = 执行环境()
    
    def 解释(self, 抽象语法树):
        return self.解释_程序(抽象语法树, self.全局环境)
    
    def 解释_程序(self, 节点, 环境):
        结果 = None
        for 语句 in 节点.语句列表:
            结果 = self.解释_语句(语句, 环境)
        return 结果
    
    def 解释_语句(self, 节点, 环境):
        if 节点 is None:
            return None
            
        节点类型 = 节点.类型
        
        if 节点类型 == "FUNCTION_DEF":
            return self.解释_函数定义(节点, 环境)
        elif 节点类型 == "VARIABLE_DECLARATION":
            return self.解释_变量声明(节点, 环境)
        elif 节点类型 == "ASSIGNMENT":
            return self.解释_赋值(节点, 环境)
        elif 节点类型 == "FUNCTION_CALL":
            return self.解释_函数调用(节点, 环境)
        elif 节点类型 == "REPORT":
            return self.解释_输出(节点, 环境)
        elif 节点类型 == "VISIT_LOOP":
            return self.解释_访问循环(节点, 环境)
        elif 节点类型 == "CONDITIONAL":
            return self.解释_条件语句(节点, 环境)
        elif 节点类型 == "RETURN":
            return self.解释_返回语句(节点, 环境)
        else:
            if hasattr(节点, '类型') and 节点.类型 in ["IDENTIFIER", "NUMBER", "STRING", "BINARY_OP", "LIST", "FUNCTION_CALL"]:
                return self.解释_表达式(节点, 环境)
            raise 解释错误(f"未知语句类型: {节点类型}", 节点.行号, 节点.列号)
    
    def 解释_函数定义(self, 节点, 环境):
        环境.设置函数(节点.函数名, 节点)
        环境.设置变量(节点.函数名, 节点)
        return f"<函数: {节点.函数名}>"
    
    def 解释_变量声明(self, 节点, 环境):
        结果 = None
        for 变量名, 值表达式 in 节点.声明列表:
            if 值表达式 is not None:
                值 = self.解释_表达式(值表达式, 环境)
                环境.设置变量(变量名, 值)
                结果 = 值
            else:
                环境.设置变量(变量名, None)
        return 结果
    
    def 解释_赋值(self, 节点, 环境):
        值 = self.解释_表达式(节点.值表达式, 环境)
        环境.设置变量(节点.变量名, 值)
        return 值
    
    def 解释_函数调用(self, 节点, 环境):
        函数值 = None
        try:
            函数值 = 环境.获取变量(节点.函数名)
        except NameError:
            try:
                函数值 = 环境.获取函数(节点.函数名)
            except NameError:
                raise 解释错误(f"未定义函数: {节点.函数名}", 节点.行号, 节点.列号)
        
        参数值列表 = [self.解释_表达式(参数, 环境) for 参数 in 节点.参数列表]
        
        if callable(函数值):
            try:
                return 函数值(*参数值列表)
            except Exception as e:
                raise 解释错误(f"内置函数调用错误: {str(e)}", 节点.行号, 节点.列号)
        
        if hasattr(函数值, '类型') and 函数值.类型 == "FUNCTION_DEF":
            return self.解释_用户函数(函数值, 参数值列表, 环境, 节点)
        
        raise 解释错误(f"{节点.函数名} 不是可调用函数", 节点.行号, 节点.列号)
    
    def 解释_用户函数(self, 函数节点, 参数值列表, 调用环境, 调用节点):
        函数环境 = 执行环境(调用环境)
        
        if len(参数值列表) != len(函数节点.参数列表):
            raise 解释错误(
                f"函数 {函数节点.函数名} 期望 {len(函数节点.参数列表)} 个参数，但得到 {len(参数值列表)} 个",
                调用节点.行号, 调用节点.列号
            )
        
        for 参数名, 参数值 in zip(函数节点.参数列表, 参数值列表):
            函数环境.设置变量(参数名, 参数值)
        
        结果 = None
        for 语句 in 函数节点.函数体:
            结果 = self.解释_语句(语句, 函数环境)
            
            if hasattr(语句, '类型') and 语句.类型 == "RETURN":
                break
        
        return 结果
    
    def 解释_输出(self, 节点, 环境):
        输出内容 = self.解释_表达式(节点.输出内容, 环境)
        return 环境.内置函数["报"](输出内容)
    
    def 解释_返回语句(self, 节点, 环境):
        if 节点.返回值:
            return self.解释_表达式(节点.返回值, 环境)
        return None
    
    def 解释_访问循环(self, 节点, 环境):
        集合值 = self.解释_表达式(节点.集合表达式, 环境)
        结果 = None
        
        if not isinstance(集合值, (list, str, range)):
            raise 解释错误("访问循环只能用于列表、字符串或范围", 节点.行号, 节点.列号)
        
        for 元素 in 集合值:
            循环环境 = 执行环境(环境)
            循环环境.设置变量(节点.元素变量, 元素)
            
            for 语句 in 节点.循环体:
                结果 = self.解释_语句(语句, 循环环境)
        
        return 结果
    
    def 解释_条件语句(self, 节点, 环境):
        条件值 = self.解释_表达式(节点.条件表达式, 环境)
        
        if 条件值:
            for 语句 in 节点.则分支:
                self.解释_语句(语句, 环境)
        elif 节点.否则分支:
            for 语句 in 节点.否则分支:
                self.解释_语句(语句, 环境)
        
        return None
    
    def 解释_表达式(self, 节点, 环境):
        if hasattr(节点, '类型'):
            节点类型 = 节点.类型
        else:
            return 节点
        
        if 节点类型 == "IDENTIFIER":
            return self.解释_标识符(节点, 环境)
        elif 节点类型 == "NUMBER":
            return self.解释_数字(节点, 环境)
        elif 节点类型 == "STRING":
            return self.解释_字符串(节点, 环境)
        elif 节点类型 == "BINARY_OP":
            return self.解释_二元运算(节点, 环境)
        elif 节点类型 == "LIST":
            return self.解释_列表(节点, 环境)
        elif 节点类型 == "FUNCTION_CALL":
            return self.解释_函数调用(节点, 环境)
        else:
            raise 解释错误(f"未知表达式类型: {节点类型}", 节点.行号, 节点.列号)
    
    def 解释_标识符(self, 节点, 环境):
        try:
            return 环境.获取变量(节点.值)
        except NameError as e:
            raise 解释错误(str(e), 节点.行号, 节点.列号)
    
    def 解释_数字(self, 节点, 环境):
        值 = 节点.值
        if '.' in 值:
            return float(值)
        else:
            return int(值)
    
    def 解释_字符串(self, 节点, 环境):
        return 节点.值
    
    def 解释_列表(self, 节点, 环境):
        元素列表 = []
        for 元素表达式 in 节点.元素列表:
            元素值 = self.解释_表达式(元素表达式, 环境)
            元素列表.append(元素值)
        return 元素列表
    
    def 解释_二元运算(self, 节点, 环境):
        左值 = self.解释_表达式(节点.左表达式, 环境)
        右值 = self.解释_表达式(节点.右表达式, 环境)
        运算符 = 节点.运算符
        
        if 运算符 == '+':
            if isinstance(左值, list) and isinstance(右值, list):
                return 左值 + 右值
            elif isinstance(左值, str) and isinstance(右值, str):
                return 左值 + 右值
            elif isinstance(左值, str) or isinstance(右值, str):
                return str(左值) + str(右值)
            return 左值 + 右值
        elif 运算符 == '-':
            return 左值 - 右值
        elif 运算符 == '*':
            if isinstance(左值, list) and isinstance(右值, int):
                return 左值 * 右值
            elif isinstance(左值, int) and isinstance(右值, list):
                return 右值 * 左值
            return 左值 * 右值
        elif 运算符 == '/':
            if 右值 == 0:
                raise 解释错误("除零错误", 节点.行号, 节点.列号)
            return 左值 / 右值
        elif 运算符 == '==':
            return 左值 == 右值
        elif 运算符 == '!=':
            return 左值 != 右值
        elif 运算符 == '>':
            return 左值 > 右值
        elif 运算符 == '<':
            return 左值 < 右值
        elif 运算符 == '>=':
            return 左值 >= 右值
        elif 运算符 == '<=':
            return 左值 <= 右值
        else:
            raise 解释错误(f"未知运算符: {运算符}", 节点.行号, 节点.列号)