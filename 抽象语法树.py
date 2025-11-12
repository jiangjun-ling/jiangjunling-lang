# -*- coding: utf-8 -*-
"""
将军令语言 - 抽象语法树节点定义
"""

class 抽象语法树节点:
    def __init__(self, 节点类型, 行号=0, 列号=0):
        self.类型 = 节点类型
        self.行号 = 行号
        self.列号 = 列号
    
    def __repr__(self):
        return f"{self.类型}节点(行{self.行号})"


class 程序节点(抽象语法树节点):
    def __init__(self, 语句列表):
        super().__init__("PROGRAM")
        self.语句列表 = 语句列表


class 函数定义节点(抽象语法树节点):
    def __init__(self, 函数名, 参数列表, 函数体):
        super().__init__("FUNCTION_DEF")
        self.函数名 = 函数名
        self.参数列表 = 参数列表
        self.函数体 = 函数体


class 变量声明节点(抽象语法树节点):
    def __init__(self, 声明列表):
        super().__init__("VARIABLE_DECLARATION")
        self.声明列表 = 声明列表


class 赋值节点(抽象语法树节点):
    def __init__(self, 变量名, 值表达式):
        super().__init__("ASSIGNMENT")
        self.变量名 = 变量名
        self.值表达式 = 值表达式


class 函数调用节点(抽象语法树节点):
    def __init__(self, 函数名, 参数列表):
        super().__init__("FUNCTION_CALL")
        self.函数名 = 函数名
        self.参数列表 = 参数列表


class 输出节点(抽象语法树节点):
    def __init__(self, 输出内容):
        super().__init__("REPORT")
        self.输出内容 = 输出内容


class 返回节点(抽象语法树节点):
    def __init__(self, 返回值):
        super().__init__("RETURN")
        self.返回值 = 返回值


class 访问循环节点(抽象语法树节点):
    def __init__(self, 元素变量, 集合表达式, 循环体):
        super().__init__("VISIT_LOOP")
        self.元素变量 = 元素变量
        self.集合表达式 = 集合表达式
        self.循环体 = 循环体


class 条件节点(抽象语法树节点):
    def __init__(self, 条件表达式, 则分支, 否则分支=None):
        super().__init__("CONDITIONAL")
        self.条件表达式 = 条件表达式
        self.则分支 = 则分支
        self.否则分支 = 否则分支


class 表达式节点(抽象语法树节点):
    def __init__(self, 表达式类型, 值=None, 左表达式=None, 右表达式=None, 运算符=None, 元素列表=None):
        super().__init__(表达式类型)
        self.值 = 值
        self.左表达式 = 左表达式
        self.右表达式 = 右表达式
        self.运算符 = 运算符
        self.元素列表 = 元素列表
    
    def __repr__(self):
        if self.类型 == "IDENTIFIER":
            return f"标识符表达式('{self.值}')"
        elif self.类型 == "NUMBER":
            return f"数字表达式({self.值})"
        elif self.类型 == "STRING":
            return f"字符串表达式('{self.值}')"
        elif self.类型 == "BINARY_OP":
            return f"二元运算({self.左表达式} {self.运算符} {self.右表达式})"
        elif self.类型 == "LIST":
            return f"列表表达式({len(self.元素列表)}个元素)"
        else:
            return f"表达式节点({self.类型})"