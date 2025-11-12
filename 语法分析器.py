# -*- coding: utf-8 -*-
"""
将军令语言 - 语法分析器
将令牌序列转换为抽象语法树
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from 抽象语法树 import *


class 语法错误(Exception):
    def __init__(self, 消息, 行号, 列号):
        super().__init__(f"语法错误（第{行号}行，第{列号}列）: {消息}")
        self.行号 = 行号
        self.列号 = 列号


class 将军令语法分析器:
    def __init__(self):
        self.令牌列表 = []
        self.当前位置 = 0
        self.当前令牌 = None
        self.二元运算符 = ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE']
    
    def 解析程序(self, 令牌列表):
        self.令牌列表 = 令牌列表
        self.当前位置 = 0
        self.前进()
        
        语句列表 = []
        
        while self.当前令牌.类型 != "EOF":
            if self.当前令牌.类型 in ["NEWLINE"]:
                self.前进()
                continue
            
            语句 = self.解析语句()
            if 语句:
                语句列表.append(语句)
        
        return 程序节点(语句列表)
    
    def 前进(self):
        if self.当前位置 < len(self.令牌列表):
            self.当前令牌 = self.令牌列表[self.当前位置]
            self.当前位置 += 1
        else:
            self.当前令牌 = 令牌("EOF", "", 0, 0)
    
    def 期待(self, 期望类型, 期望值=None):
        if self.当前令牌.类型 == 期望类型:
            if 期望值 is None or self.当前令牌.值 == 期望值:
                令牌副本 = self.当前令牌
                self.前进()
                return 令牌副本
            else:
                raise 语法错误(f"期望 '{期望值}'，但找到 '{self.当前令牌.值}'", 
                              self.当前令牌.行号, self.当前令牌.列号)
        else:
            raise 语法错误(f"期望 {期望类型}，但找到 {self.当前令牌.类型}", 
                          self.当前令牌.行号, self.当前令牌.列号)
    
    def 解析语句(self):
        令牌类型 = self.当前令牌.类型
        
        if 令牌类型 == "DEF":
            return self.解析函数定义()
        elif 令牌类型 == "LET_BLOCK":
            return self.解析变量声明块()
        elif 令牌类型 == "ASSIGNMENT_EXEC":
            return self.解析赋值语句()
        elif 令牌类型 == "FUNCTION_CALL":
            return self.解析函数调用语句()
        elif 令牌类型 == "REPORT":
            return self.解析输出语句()
        elif 令牌类型 == "VISIT_LOOP":
            return self.解析访问循环()
        elif 令牌类型 == "IF":
            return self.解析条件语句()
        elif 令牌类型 == "RETURN":
            return self.解析返回语句()
        elif 令牌类型 == "INDENT":
            self.前进()
            return None
        elif 令牌类型 == "DEDENT":
            self.前进()
            return None
        else:
            # 尝试解析为表达式语句
            try:
                表达式 = self.解析表达式()
                return 表达式
            except 语法错误 as e:
                print(f"警告：无法解析语句，跳过令牌 {self.当前令牌}: {e}")
                self.前进()
                return None
    
    def 解析块语句(self):
        语句列表 = []
        
        if self.当前令牌.类型 == "INDENT":
            self.前进()
        
        while self.当前令牌.类型 not in ["DEDENT", "EOF"]:
            if self.当前令牌.类型 in ["NEWLINE"]:
                self.前进()
                continue
            
            语句 = self.解析语句()
            if 语句:
                语句列表.append(语句)
        
        if self.当前令牌.类型 == "DEDENT":
            self.前进()
        
        return 语句列表
    
    def 解析函数定义(self):
        开始令牌 = self.期待("DEF")
        函数名 = self.期待("IDENTIFIER").值
        self.期待("LPAREN")
        
        参数列表 = []
        while self.当前令牌.类型 != "RPAREN":
            if self.当前令牌.类型 == "IDENTIFIER":
                参数列表.append(self.当前令牌.值)
                self.前进()
                if self.当前令牌.类型 == "COMMA":
                    self.前进()
            else:
                break
        
        self.期待("RPAREN")
        self.期待("COLON")
        
        if self.当前令牌.类型 == "NEWLINE":
            self.前进()
        
        函数体 = self.解析块语句()
        
        return 函数定义节点(函数名, 参数列表, 函数体)
    
    def 解析变量声明块(self):
        开始令牌 = self.期待("LET_BLOCK")
        self.期待("COLON")
        
        if self.当前令牌.类型 == "NEWLINE":
            self.前进()
        
        if self.当前令牌.类型 == "INDENT":
            self.前进()
        
        声明列表 = []
        while self.当前令牌.类型 not in ["DEDENT", "EOF"]:
            if self.当前令牌.类型 == "IDENTIFIER":
                变量名 = self.当前令牌.值
                self.前进()
                
                if self.当前令牌.类型 == "ASSIGN":
                    self.前进()
                    值表达式 = self.解析表达式()
                    声明列表.append((变量名, 值表达式))
                    
                    if self.当前令牌.类型 == "NEWLINE":
                        self.前进()
                else:
                    声明列表.append((变量名, None))
                    
                    if self.当前令牌.类型 == "NEWLINE":
                        self.前进()
            else:
                self.前进()
        
        if self.当前令牌.类型 == "DEDENT":
            self.前进()
        
        return 变量声明节点(声明列表)
    
    def 解析赋值语句(self):
        开始令牌 = self.期待("ASSIGNMENT_EXEC")
        变量名 = self.期待("IDENTIFIER").值
        self.期待("ASSIGN")
        值表达式 = self.解析表达式()
        return 赋值节点(变量名, 值表达式)
    
    def 解析输出语句(self):
        开始令牌 = self.期待("REPORT")
        输出内容 = self.解析表达式()
        return 输出节点(输出内容)
    
    def 解析返回语句(self):
        开始令牌 = self.期待("RETURN")
        返回值 = self.解析表达式()
        return 返回节点(返回值)
    
    def 解析访问循环(self):
        开始令牌 = self.期待("VISIT_LOOP")
        元素变量 = self.期待("IDENTIFIER").值
        self.期待("IN")
        集合表达式 = self.解析表达式()
        self.期待("COLON")
        
        if self.当前令牌.类型 == "NEWLINE":
            self.前进()
        
        循环体 = self.解析块语句()
        
        return 访问循环节点(元素变量, 集合表达式, 循环体)
    
    def 解析条件语句(self):
        开始令牌 = self.期待("IF")
        条件表达式 = self.解析表达式()
        
        if self.当前令牌.类型 == "THEN":
            self.前进()
        
        self.期待("COLON")
        
        if self.当前令牌.类型 == "NEWLINE":
            self.前进()
        
        则分支 = self.解析块语句()
        
        否则分支 = None
        
        if self.当前令牌.类型 in ["ELSE", "ELIF"]:
            if self.当前令牌.类型 == "ELSE":
                self.前进()
                self.期待("COLON")
                
                if self.当前令牌.类型 == "NEWLINE":
                    self.前进()
                
                否则分支 = self.解析块语句()
            
            elif self.当前令牌.类型 == "ELIF":
                否则分支 = [self.解析条件语句()]
        
        return 条件节点(条件表达式, 则分支, 否则分支)
    
    def 解析表达式(self):
        return self.解析二元运算()
    
    def 解析二元运算(self):
        左表达式 = self.解析项()
        
        while self.当前令牌.类型 in self.二元运算符:
            运算符 = self.当前令牌.值
            self.前进()
            右表达式 = self.解析项()
            左表达式 = 表达式节点("BINARY_OP", 左表达式=左表达式, 右表达式=右表达式, 运算符=运算符)
        
        return 左表达式
    
    def 解析项(self):
        if self.当前令牌.类型 == "IDENTIFIER":
            # 检查是否是函数调用
            当前位置 = self.当前位置
            if 当前位置 < len(self.令牌列表) and self.令牌列表[当前位置].类型 == "LPAREN":
                return self.解析函数调用()
            else:
                节点 = 表达式节点("IDENTIFIER", self.当前令牌.值)
                self.前进()
                return 节点
        elif self.当前令牌.类型 == "NUMBER":
            节点 = 表达式节点("NUMBER", self.当前令牌.值)
            self.前进()
            return 节点
        elif self.当前令牌.类型 == "STRING":
            节点 = 表达式节点("STRING", self.当前令牌.值)
            self.前进()
            return 节点
        elif self.当前令牌.类型 == "LPAREN":
            self.前进()
            表达式 = self.解析表达式()
            self.期待("RPAREN")
            return 表达式
        elif self.当前令牌.类型 == "LBRACKET":
            return self.解析列表字面量()
        else:
            raise 语法错误(f"意外的表达式开始: {self.当前令牌.类型}", 
                          self.当前令牌.行号, self.当前令牌.列号)
    
    def 解析列表字面量(self):
        try:
            开始令牌 = self.期待("LBRACKET")
            元素列表 = []
            
            if self.当前令牌.类型 == "RBRACKET":
                self.期待("RBRACKET")
                return 表达式节点("LIST", 元素列表=[])
            
            while self.当前令牌.类型 != "RBRACKET":
                元素 = self.解析表达式()
                元素列表.append(元素)
                
                if self.当前令牌.类型 == "COMMA":
                    self.前进()
                elif self.当前令牌.类型 != "RBRACKET":
                    raise 语法错误("列表元素后应有逗号或右括号", 
                                  self.当前令牌.行号, self.当前令牌.列号)
            
            self.期待("RBRACKET")
            return 表达式节点("LIST", 元素列表=元素列表)
        
        except 语法错误:
            raise
        except Exception as e:
            raise 语法错误(f"解析列表时出错: {str(e)}", 
                          self.当前令牌.行号, self.当前令牌.列号)
    
    def 解析函数调用(self):
        """解析函数调用"""
        函数名 = self.当前令牌.值
        self.前进()
        self.期待("LPAREN")
        
        参数列表 = []
        while self.当前令牌.类型 != "RPAREN" and self.当前令牌.类型 != "EOF":
            参数 = self.解析表达式()
            参数列表.append(参数)
            
            if self.当前令牌.类型 == "COMMA":
                self.前进()
            elif self.当前令牌.类型 != "RPAREN":
                raise 语法错误(f"参数列表中出现意外的令牌: {self.当前令牌.类型}", 
                              self.当前令牌.行号, self.当前令牌.列号)
        
        self.期待("RPAREN")
        return 函数调用节点(函数名, 参数列表)

    def 解析函数调用语句(self):
        """解析策行：函数调用语句"""
        开始令牌 = self.期待("FUNCTION_CALL")
        
        if self.当前令牌.类型 != "IDENTIFIER":
            raise 语法错误(f"期望函数名，但找到 {self.当前令牌.类型}", 
                          self.当前令牌.行号, self.当前令牌.列号)
        
        函数名 = self.当前令牌.值
        self.前进()
        self.期待("LPAREN")
        
        参数列表 = []
        while self.当前令牌.类型 != "RPAREN" and self.当前令牌.类型 != "EOF":
            参数 = self.解析表达式()
            参数列表.append(参数)
            
            if self.当前令牌.类型 == "COMMA":
                self.前进()
            elif self.当前令牌.类型 != "RPAREN":
                raise 语法错误(f"参数列表中出现意外的令牌: {self.当前令牌.类型}", 
                              self.当前令牌.行号, self.当前令牌.列号)
        
        self.期待("RPAREN")
        return 函数调用节点(函数名, 参数列表)