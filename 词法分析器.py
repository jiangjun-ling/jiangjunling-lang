# -*- coding: utf-8 -*-
"""
将军令语言 - 词法分析器
将源代码分解为令牌序列
"""

class 令牌:
    """表示源代码中的一个令牌"""
    def __init__(self, 类型, 值, 行号, 列号):
        self.类型 = 类型
        self.值 = 值
        self.行号 = 行号
        self.列号 = 列号
    
    def __repr__(self):
        return f"令牌({self.类型}, '{self.值}', {self.行号}:{self.列号})"


class 词法错误(Exception):
    """词法分析错误"""
    def __init__(self, 消息, 行号, 列号):
        super().__init__(f"词法错误（第{行号}行，第{列号}列）: {消息}")
        self.行号 = 行号
        self.列号 = 列号


class 将军令词法分析器:
    """将军令编程语言的词法分析器"""
    
    def __init__(self):
        self.关键词表 = {
            "征": "IMPORT_BLOCK",
            "策": "DEF", 
            "令": "LET_BLOCK",
            "策行": "FUNCTION_CALL",
            "令行": "ASSIGNMENT_EXEC", 
            "报": "REPORT",
            "访": "VISIT_LOOP",
            "若": "IF",
            "则": "THEN",
            "否则": "ELSE", 
            "否则若": "ELIF",
            "于": "IN",
            "返": "RETURN",
            "为": "AS",
        }
        
        self.多字符关键词 = sorted(self.关键词表.keys(), key=len, reverse=True)
        
        self.运算符表 = {
            '+': 'PLUS', '-': 'MINUS', '*': 'MULTIPLY', '/': 'DIVIDE',
            '=': 'ASSIGN', '==': 'EQ', '!=': 'NEQ', '>': 'GT', '<': 'LT', 
            '>=': 'GTE', '<=': 'LTE', '(': 'LPAREN', ')': 'RPAREN',
            '[': 'LBRACKET', ']': 'RBRACKET', ',': 'COMMA', ':': 'COLON',
            '：': 'COLON', '，': 'COMMA',
        }
        
        self.多字符运算符 = ['==', '!=', '>=', '<=']

    def 分析(self, 源代码):
        """分析源代码，返回令牌列表"""
        self.源代码 = 源代码
        self.行号 = 1
        self.列号 = 0
        self.令牌列表 = []
        self.缩进栈 = [0]
        
        行列表 = 源代码.split('\n')
        
        for 行号, 行内容 in enumerate(行列表, 1):
            self.行号 = 行号
            self.列号 = 0
            
            缩进级别 = self.计算缩进(行内容)
            self.处理缩进(缩进级别)
            
            处理内容 = 行内容.strip()
            if 处理内容:
                self.处理行(处理内容)
            
            if 处理内容:
                self.令牌列表.append(令牌("NEWLINE", "", self.行号, len(行内容)))
        
        while len(self.缩进栈) > 1:
            self.令牌列表.append(令牌("DEDENT", "", self.行号, self.列号))
            self.缩进栈.pop()
        
        self.令牌列表.append(令牌("EOF", "", self.行号, self.列号))
        return self.令牌列表

    def 计算缩进(self, 行内容):
        缩进 = 0
        for 字符 in 行内容:
            if 字符 == ' ':
                缩进 += 1
            elif 字符 == '\t':
                缩进 += 4
            else:
                break
        return 缩进

    def 处理缩进(self, 缩进级别):
        当前缩进 = self.缩进栈[-1]
        if 缩进级别 > 当前缩进:
            self.缩进栈.append(缩进级别)
            self.令牌列表.append(令牌("INDENT", "", self.行号, 0))
        elif 缩进级别 < 当前缩进:
            while self.缩进栈[-1] > 缩进级别:
                self.缩进栈.pop()
                self.令牌列表.append(令牌("DEDENT", "", self.行号, 0))

    def 处理行(self, 行内容):
        位置 = 0
        行长度 = len(行内容)
        
        while 位置 < 行长度:
            字符 = 行内容[位置]
            self.列号 = 位置
            
            if 字符.isspace():
                位置 += 1
            elif 字符 == '#':
                break
            elif 字符.isdigit():
                位置 = self.处理数字(行内容, 位置)
            elif 字符 == '"' or 字符 == "'":
                位置 = self.处理字符串(行内容, 位置, 字符)
            elif 字符.isalpha() or 字符 == '_' or self.是中文字符(字符):
                位置 = self.处理标识符(行内容, 位置)
            else:
                位置 = self.处理运算符(行内容, 位置)

    def 是中文字符(self, 字符):
        return '\u4e00' <= 字符 <= '\u9fff'

    def 处理数字(self, 行内容, 开始位置):
        位置 = 开始位置
        行长度 = len(行内容)
        
        while 位置 < 行长度 and 行内容[位置].isdigit():
            位置 += 1
        
        if 位置 < 行长度 and 行内容[位置] == '.':
            位置 += 1
            while 位置 < 行长度 and 行内容[位置].isdigit():
                位置 += 1
        
        数字值 = 行内容[开始位置:位置]
        self.令牌列表.append(令牌("NUMBER", 数字值, self.行号, 开始位置))
        return 位置

    def 处理字符串(self, 行内容, 开始位置, 引号类型):
        位置 = 开始位置 + 1
        行长度 = len(行内容)
        字符串值 = ""
        转义 = False
        
        while 位置 < 行长度:
            字符 = 行内容[位置]
            
            if 转义:
                if 字符 == 'n': 字符串值 += '\n'
                elif 字符 == 't': 字符串值 += '\t'
                elif 字符 == 'r': 字符串值 += '\r'
                elif 字符 == '\\': 字符串值 += '\\'
                elif 字符 == 引号类型: 字符串值 += 引号类型
                else: 字符串值 += 字符
                转义 = False
            elif 字符 == '\\':
                转义 = True
            elif 字符 == 引号类型:
                位置 += 1
                break
            else:
                字符串值 += 字符
            
            位置 += 1
        
        self.令牌列表.append(令牌("STRING", 字符串值, self.行号, 开始位置))
        return 位置

    def 处理标识符(self, 行内容, 开始位置):
        位置 = 开始位置
        行长度 = len(行内容)
        
        for 关键词 in self.多字符关键词:
            关键词长度 = len(关键词)
            if (位置 + 关键词长度 <= 行长度 and 
                行内容[位置:位置+关键词长度] == 关键词):
                if (位置 + 关键词长度 == 行长度 or 
                    not (行内容[位置 + 关键词长度].isalnum() or 
                        行内容[位置 + 关键词长度] == '_' or
                        self.是中文字符(行内容[位置 + 关键词长度]))):
                    self.令牌列表.append(
                        令牌(self.关键词表[关键词], 关键词, self.行号, 开始位置)
                    )
                    return 位置 + 关键词长度
        
        while (位置 < 行长度 and 
               (行内容[位置].isalnum() or 
                行内容[位置] == '_' or
                self.是中文字符(行内容[位置]))):
            位置 += 1
        
        标识符 = 行内容[开始位置:位置]
        令牌类型 = self.关键词表.get(标识符, "IDENTIFIER")
        self.令牌列表.append(令牌(令牌类型, 标识符, self.行号, 开始位置))
        return 位置

    def 处理运算符(self, 行内容, 开始位置):
        位置 = 开始位置
        行长度 = len(行内容)
        
        for 运算符 in self.多字符运算符:
            运算符长度 = len(运算符)
            if (位置 + 运算符长度 <= 行长度 and 
                行内容[位置:位置+运算符长度] == 运算符):
                self.令牌列表.append(
                    令牌(self.运算符表[运算符], 运算符, self.行号, 开始位置)
                )
                return 位置 + 运算符长度
        
        字符 = 行内容[位置]
        if 字符 in self.运算符表:
            self.令牌列表.append(
                令牌(self.运算符表[字符], 字符, self.行号, 开始位置)
            )
            位置 += 1
        else:
            print(f"警告：第{self.行号}行第{开始位置}列：未知字符 '{字符}'")
            位置 += 1
        
        return 位置