#!/usr/bin/env python3
from __future__ import print_function
import re
import argparse
import sys
import xml.etree.ElementTree as EL

#######################################   C L A S S   S T R U C T U R E   P R O G R A M   #######################################

# Class representing a variable

class Variable:

    # Creates variable
    # args: name - variable name
    # args: frame - in which frame variable was created
    def __init__(self, name, frame):
        self.name = name
        self.frame = frame
        self.value = None
        self.type = None

    # set to variable an value
    # args: value - value of variable
    def setValue(self, value):
        self.value = value

    # set variable type
    # args: type - type of variable
    def setType(self, type):
        self.type = type
        return True

    # changes variable name to LF when PUSHFRAME
    def nameToLF(self):
        self.name = re.sub('^TF', 'LF', self.name)

    # changes variable name to TF when POPFRAME
    def nameToTF(self):
        self.name = re.sub('^LF', 'TF', self.name)

    # get variable parameters
    def getName(self):
        return self.name
    def getType(self):
        return self.type
    def getValue(self):
        return self.value

# Class representing frame in IPPcode21
class Frame:
    # frame contans name and variable list
    #args: name - frame name
    def __init__(self, name):
        self.variable_list = []
        self.name = name

    # Check if variable with same name doesn't exists and create it
    # args: name - variable name
    def addVariable(self, name):
        for var in self.variable_list:
            if var.name == name:
                sys.exit(52)
        var = Variable(name, self)  
        self.variable_list.append(var)

    # Find an variable and set type to it
    # args: name - variable name
    # args: value - variable value
    # args: type - variable type
    def setVariableValue(self, name, value, type):
        for var in self.variable_list:
            if name == var.getName():
                # if var.getType() == type or var.getType() == None:
                var.setType(type)
                var.setValue(value)
                return
        sys.exit(54)

    # Transform frame to LF after PUSHFRAME
    def toLF(self):
        self.name = "LF"
        for var in self.variable_list:
            var.nameToLF()
    
    # Tramsform frame to TF after POPFRAME
    def toTF(self):
        self.name = "TF"
        for var in self.variable_list:
            var.nameToTF()

    # returns name of frame
    def getName(self):
        return self.name
    
    # returns type of variable
    # args: name - name of variable
    def getVariableType(self, name):
        for var in self.variable_list:
            if var.getName() == name:
                return var.getType()
        sys.exit(54)

    # returns name of frame
    # args: name - name of variable
    def getVariableValue(self, name):
        for var in self.variable_list:
            if var.getName() == name:
                return var.getValue()
        sys.exit(54)

    # prints all variables from frame
    def printVariables(self):
        for var in self.variable_list:
            print(var.getName())
            print(var.getValue())
            print(var.getType())
        

# Class representing work of program IPPcode21
class Program:

    # Creates empty GF, none TF and empty list of LF 
    def __init__(self):
        self.GF = Frame("GF")
        self.CurrentFrame = None
        self.LF_list = []
        self.TF = None

    # Creates empty TF
    def addTF(self):
        self.TF = Frame("TF")

    # Adds one LF on the end of the LF list and cleans TF
    def addLF(self):
        if self.TF == None:
            sys.exit(55)
        self.TF.toLF()
        self.CurrentFrame = self.TF
        self.LF_list.append(self.CurrentFrame)
        self.TF = None
    
    # Pops the top of LF list to TF
    def popLF(self):
        if len(self.LF_list) == 0:
            sys.exit(55)
        self.TF = self.CurrentFrame
        self.LF_list.pop()
        if len(self.LF_list) != 0:
            self.CurrentFrame = self.getCurrent()
        self.TF.toTF()

    # returns the top of LF list
    def getCurrent(self):
        return self.LF_list[-1] # get the last element from list (current FRAME)

    # Prints LF list
    def printFrames(self):
        for frame in self.LF_list:
            print(frame.getName())
        
    # Adds variable to nedeed frame
    # args: name - variable name
    def addVariable(self, name):
        if re.search('^GF@', name):
            self.GF.addVariable(name)
        elif re.search('^TF@', name) and self.TF != None:
            self.TF.addVariable(name)
        elif re.search('^LF@', name) and self.CurrentFrame != None:
            self.CurrentFrame.addVariable(name)
        else:
            sys.exit(55)

    # Adds value to needed frame
    # args: name - variable name
    # args: value - variable value
    # args: type - variable type
    def setVarValue(self, name, value, vtype):
        if re.search('^GF@', name):
            self.GF.setVariableValue(name, value, vtype)
        elif re.search('^TF@', name) and self.TF != None:
            self.TF.setVariableValue(name, value, vtype)
        elif re.search('^LF@', name) and self.CurrentFrame != None:
            self.CurrentFrame.setVariableValue(name, value, vtype)
        else:
            sys.exit(55)

    # returns type of variable from needed frame
    # args: name - variable name
    def getVarType(self, name):
        if re.search('^GF@', name):
            return self.GF.getVariableType(name)
        elif re.search('^TF@', name) and self.TF != None:
            return self.TF.getVariableType(name)
        elif re.search('^LF@', name) and self.CurrentFrame != None:
            return self.CurrentFrame.getVariableType(name)
        else:
            sys.exit(55)

    # returns value of variable from needed frame
    # args: name - variable name
    def getVarValue(self, name):
        if re.search('^GF@', name):
            return self.GF.getVariableValue(name)
        elif re.search('^TF@', name) and self.TF != None:
            return self.TF.getVariableValue(name)
        elif re.search('^LF@', name) and self.CurrentFrame != None:
            return self.CurrentFrame.getVariableValue(name)
        else:
            sys.exit(55)

    # prints all variables from all frames
    def printVariables(self, frame):
        if frame == "GF":
            print("----- IN GF -----")
            self.GF.printVariables()
            print("-----------------")
        elif frame == "TF":
            print("----- IN TF -----")
            self.TF.printVariables()
            print("-----------------")
        elif frame == "LF":
            print("----- IN LF -----")
            self.CurrentFrame.printVariables()
            


# --------------------------- CLASS STRUCTURE   I N S T R U C T I O N

# Class representing argument from XML file
class Argument:
    def __init__(self, argtype, argvalue):
        self.argtype = argtype
        self.argvalue = argvalue

# Class representing instruction from XML file
class Instruction:
    def __init__(self, name, id):
        self.id = id
        self.name = name
        self.args = []
    
    # Adds one argument on top of list
    # args: argtype - type of argument
    # args: argvalue - value of argument
    def addAgrument(self, argtype, argvalue, argNumber):
        arg = Argument(argtype, argvalue)
        self.args.insert(argNumber, arg)


# Class representing work of whole interpret
class Interpret:
    # creates empty list of instructions, empty CALL list, empty list of literals
    def __init__(self, prog):
        self.instructionList = []
        self.operation = 0
        self.prog = prog
        self.currentInstr = None
        self.callStack = []
        self.callStackOp = []
        self.pushStack = []

    # adds instruction to list
    def addInstruction(self, instruction):
        self.instructionList.append(instruction)

    # checks if names of labels and jumps are correct
    def checkLabelsAndJumps(self):
        # dublicated labels
        for i in range(len(self.instructionList)-1):
            for j in range(i+1, len(self.instructionList)):
                if self.instructionList[i].name == "LABEL" and self.instructionList[j].name == "LABEL":
                    if self.instructionList[i].args[0].argvalue == self.instructionList[j].args[0].argvalue:
                        sys.exit(52)

        # every jump has only one label
        for jump in self.instructionList:
            if jump.name == "CALL" or jump.name == "JUMP" or \
                jump.name == "JUMPIFEQ" or jump.name == "JUMPIFNEQ":
                counter = 0
                for label in self.instructionList:
                    if label.name == "LABEL" and jump.args[0].argvalue == label.args[0].argvalue:
                        counter += 1
                if counter != 1:
                    sys.exit(52)


    # function defines next instruction
    # args: number - number of current instruction
    def getNextOperation(self, number):
        if self.operation == 0 and len(self.instructionList) != 0 and number == 0:
            self.operation = self.instructionList[0].id
        elif len(self.instructionList) != 0 and number == 0:
            for i in range (len(self.instructionList)):
                if self.operation == self.instructionList[i].id:
                    if i < len(self.instructionList) - 1:
                        self.operation = self.instructionList[i+1].id
                        self.currentInstr = self.instructionList[i+1]
                        break
                    else:
                        self.operation = -1

            
        elif number != 0:
            for i in range (len(self.instructionList)):
                if number == self.instructionList[i].id:
                    self.operation = self.instructionList[i+1].id
                    self.currentInstr = self.instructionList[i+1]
                    break
    
    # controls if argument[1] is var or literal and returns its type and value
    def control1Symb(self):
        if self.currentInstr.args[1].argtype == "var":
            type = self.prog.getVarType(self.currentInstr.args[1].argvalue)
            value = self.prog.getVarValue(self.currentInstr.args[1].argvalue)
            if value == None:
                exit(56)
        else:
            type = self.currentInstr.args[1].argtype
            value = self.currentInstr.args[1].argvalue
        return type, value

    # controls if argument[1] is var or literal and returns its type and value
    # controls if argument[2] is var or literal and returns its type and value
    def control2Symb(self):
        if self.currentInstr.args[1].argtype == "var":
            type1 = self.prog.getVarType(self.currentInstr.args[1].argvalue)
            value1 = self.prog.getVarValue(self.currentInstr.args[1].argvalue)
            if value1 == None:
                exit(56)
        else:
            type1 = self.currentInstr.args[1].argtype
            value1 = self.currentInstr.args[1].argvalue

        if self.currentInstr.args[2].argtype == "var":
            type2 = self.prog.getVarType(self.currentInstr.args[2].argvalue)
            value2 = self.prog.getVarValue(self.currentInstr.args[2].argvalue)
            if value2 == None:
                exit(56)
        else:
            type2 = self.currentInstr.args[2].argtype
            value2 = self.currentInstr.args[2].argvalue
        return type1, type2, value1, value2

    # creates TF 
    def createFrame(self):
        self.prog.addTF()

    # transform TF to LF
    def pushFrame(self):
        self.prog.addLF()
    
    # pop LF and transform to TF
    def popFrame(self):
        self.prog.popLF()

    # implementing instruction DEFVAR, creates a new varianble in needed frame
    def defVar(self):
        self.prog.addVariable(self.currentInstr.args[0].argvalue)

    # adds value to variable
    def move(self):
        type, value = self.control1Symb()
        self.prog.setVarValue(self.currentInstr.args[0].argvalue, value, type)
            
    # adds two int values and saves it to variable
    def add(self):
        type1, type2, value1, value2 = self.control2Symb()

        if type1 == type2:
            if type1 == "int":
                value = int(value1) + int(value2)
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, value, type1)
            else:
                sys.exit(53)
        else: 
            sys.exit(53)

    # substitutes two int values and saves it to variable
    def sub(self):
        type1, type2, value1, value2 = self.control2Symb()

        if type1 == type2:
            if type1 == "int":
                value = int(value1) - int(value2)
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, value, type1)
            else:
                sys.exit(53)
        else: 
            sys.exit(53)

    # representing MUL instruction (only ints)
    def mul(self):
        type1, type2, value1, value2 = self.control2Symb()

        if type1 == type2:
            if type1 == "int":
                value = int(value1) * int(value2)
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, value, type1)
            else:
                sys.exit(53)
        else: 
            sys.exit(53)

    # representing DIV instruction (only ints)
    def div(self):
        type1, type2, value1, value2 = self.control2Symb()

        if type1 == type2:
            if type1 == "int":
                if int(value2) == 0:
                    sys.exit(57)
                value = int(value1) // int(value2)
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, value, type1)
            else:
                sys.exit(53)
        else: 
            sys.exit(53)

    # representing WRITE instruction
    def write(self):
        if self.currentInstr.args[0].argtype == "var":
            value = self.prog.getVarValue(self.currentInstr.args[0].argvalue)
            if value == None:
                sys.exit(56)
        elif self.currentInstr.args[0].argvalue != None:
            value = self.currentInstr.args[0].argvalue
        else:
            sys.exit(56)
        if(value == 'nil'):
            print('', end = '')
        else:
            print(value, end = '') # print from write
    

    # representing EXIT instruction 
    def exit(self):
        if self.currentInstr.args[0].argtype == "var":
            value = self.prog.getVarValue(self.currentInstr.args[0].argvalue)
            type = self.prog.getVarType(self.currentInstr.args[0].argvalue)
        elif self.currentInstr.args[0].argvalue != None:
            type = self.currentInstr.args[0].argtype
            value = self.currentInstr.args[0].argvalue
        else:
            sys.exit(56)
        if type == "int" and int(value) >= 0 and int(value) <= 49:
            sys.exit(int(value))
        if type != "int" or value == None:
            sys.exit(53)
        else:
            sys.exit(57)
    
    # representing JUMP instruction 
    def jump(self):
        name = self.currentInstr.args[0].argvalue
        label = "label"
        for element in self.instructionList:
            if element.name == "LABEL" and element.args[0].argvalue == name \
                and element.args[0].argtype == "label":
                self.operation = element.id
                self.currentInstr = element

    # representing CALL instruction, adds frame to stack and makes jump
    def call(self):
        self.callStack.append(self.currentInstr)
        self.callStackOp.append(self.operation)
        self.jump()

    # representing RETURN instruction and check correct return values
    def returned(self):
        if len(self.callStack) != 0 and len(self.callStackOp) != 0:
            self.currentInstr = self.callStack.pop()
            self.operation = self.callStackOp.pop()
        else: 
            sys.exit(56)  

    # representing JUMPEQ instruction, jumps on needed label if values are equal
    def jumpEQ(self):
        type1, type2, value1, value2 = self.control2Symb()
        
        if type1 == type2:
            if str(value1) == str(value2):
                self.jump()
        elif type1 == "nil" or type2 == "nil":
            if value1 == value2:
                self.jump()
        else: 
            sys.exit(53)

    # representing JUMPNOTEQ instruction, jumps on needed label if values are equal
    def jumpNOTEQ(self):
        type1, type2, value1, value2 = self.control2Symb()

        if type1 == type2:
            if str(value1) != str(value2):
                self.jump()
        elif type1 == "nil" or type2 == "nil":
            self.jump()
        else: 
            sys.exit(53)

    # representing PUSHS instruction, adds value to stack
    def pushs(self):
        if self.currentInstr.args[0].argtype == "var":
            value = self.prog.getVarValue(self.currentInstr.args[0].argvalue)
            type = self.prog.getVarType(self.currentInstr.args[0].argvalue)
        elif self.currentInstr.args[0].argvalue != None:
            type = self.currentInstr.args[0].argtype
            value = self.currentInstr.args[0].argvalue
        else:
            sys.exit(56)
        a = Argument(type, value)
        self.pushStack.append(a)

    # representing POPS instruction, pops value from stack
    def pops(self):
        if len(self.pushStack) == 0:
            sys.exit(56)
        symb = self.pushStack.pop()
        self.prog.setVarValue(self.currentInstr.args[0].argvalue, symb.argvalue, symb.argtype)

    # representing LT instruction, compare two variables
    def lt(self):
        type1, type2, value1, value2 = self.control2Symb()
        if type1 == "nil" or type2 == nil:
            sys.exit(53)
        if type1 == type2:
            if type1 == "bool":
                if value1 == "false" and value2 == "true":
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
                else: 
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
            elif type1 == "string":
                if str(value1) < str(value2):
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
                else:
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
            elif type1 == "int":
                if int(value1) < int(value2):
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
                else:
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
        else:
            sys.exit(53)

    # representing GT instruction, compare two variables
    def gt(self):
        type1, type2, value1, value2 = self.control2Symb()
        if type1 == "nil" or type2 == "nil":
            sys.exit(53)
        
        if type1 == type2:
            if type1 == "bool":
                if value1 == "true" and value2 == "false":
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
                else: 
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
            elif type1 == "string":
                if len(value1) > len(value2):
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
                else:
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
            elif type1 == "int":
                if int(value1) > int(value2):
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
                else:
                    self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
        else:
            sys.exit(53)

    # representing EQ instruction, compare two variables
    def eq(self):
        type1, type2, value1, value2 = self.control2Symb()
        if type1 == "nil" or type2 == "nil":
            if value1 == value2:
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
            else:
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
        elif type1 == type2:
            if str(value1) == str(value2):
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
            else:
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
        else:
            sys.exit(53)

    # representing logical AND
    def andOp(self):
        type1, type2, value1, value2 = self.control2Symb()
        if type1 == type2 and type1 == "bool":
            if str(value1) == "true" and str(value2) == "true":
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
            else:
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
        else:
            sys.exit(53)

    # representing logical OR
    def orOp(self):
        type1, type2, value1, value2 = self.control2Symb()
        if type1 == type2 and type1 == "bool":
            if str(value1) == "true" or str(value2) == "true":
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
            else:
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
        else:
            sys.exit(53)

    # representing logical NOT
    def notOp(self):
        type, value = self.control1Symb()
        if type == "bool":
            if value == "true":
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, "false", "bool")
            else:
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, "true", "bool")
        else:
            sys.exit(53)

    # representing INT2CHAR, create char from int
    def int2char(self):
        type, value = self.control1Symb()
        if type != 'int':
            sys.exit(53)
        type = 'string'
        try:
            value = chr(int(value))   
        except:
            sys.exit(58)
        self.prog.setVarValue(self.currentInstr.args[0].argvalue, value, type)

    # representing STR2INT, create int from str and position number
    def stri2int(self):
        type1, type2, value1, value2 = self.control2Symb()
        if type2 != 'int' or type1 != 'string':
            sys.exit(53)
        if int(value2) < 0 or int(value2) >= len(value1): 
            sys.exit(58) 
        type = 'int'
        symb = value1[int(value2)]
        value = ord(symb)   
        self.prog.setVarValue(self.currentInstr.args[0].argvalue, value, type)

    # representing reading from file or stdin
    def read(self): 
        read = readFile.readline()
        read = re.sub("\n$", '', read)
        type, value = self.control1Symb()

        if value == 'string':
            self.prog.setVarValue(self.currentInstr.args[0].argvalue, read, value)
        elif value == 'nil':
            sys.exit(53)
        elif value == 'int':
            if re.search('^[+-]?[1-9][0-9]*$', read):
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, read, value)
            else:
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, 'nil', 'nil')
        elif value == 'bool':
            if re.search('^true$', read.lower()):
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, 'true', value)
            else:
                self.prog.setVarValue(self.currentInstr.args[0].argvalue, 'false', value)
        
    # concatenate two strings
    def concat(self):
        type1, type2, value1, value2 = self.control2Symb()
        if type1 == 'string' and type2 == 'string':
            value = value1 + value2
            self.prog.setVarValue(self.currentInstr.args[0].argvalue, value, type1)
        else:
            sys.exit(53)

    # calculate len of string
    def strlen(self):
        type, value = self.control1Symb()
        if type == 'string':
            strlen = len(value)
            self.prog.setVarValue(self.currentInstr.args[0].argvalue, strlen, 'int')
        else:
            sys.exit(53)

    # get the char from int (ascii value)
    def getchar(self):
        type1, type2, value1, value2 = self.control2Symb()
        if type1 == 'string' and type2 == 'int':
            if int(value2) < 0 or int(value2) >= len(value1):
                sys.exit(58)
            char = value1[int(value2)]
            self.prog.setVarValue(self.currentInstr.args[0].argvalue, char, type1)
        else:
            sys.exit(53)

    # transform int to char (ascii)
    def setchar(self):
        type1, type2, value1, value2 = self.control2Symb()
        varType = self.prog.getVarType(self.currentInstr.args[0].argvalue)
        varValue = self.prog.getVarValue(self.currentInstr.args[0].argvalue)
        if varType == 'string' and type1 == 'int' and type2 == 'string':
            if type2 == 'string' and (value2 == None or value2 == ""):
                sys.exit(58)
            if int(value1) >= 0 and int(value1) < len(varValue) and \
                len(value2) > 0:
                newStr = varValue
                newStr = newStr[:int(value1)] + value2[0] + newStr[int(value1)+1:]

                self.prog.setVarValue(self.currentInstr.args[0].argvalue, newStr, varType)
            else:
                sys.exit(58)
        else: 
            sys.exit(53)

    # get type of the value and write that to variable
    def types(self):
        if self.currentInstr.args[1].argtype == "var":
            type = self.prog.getVarType(self.currentInstr.args[1].argvalue)
            value = self.prog.getVarValue(self.currentInstr.args[1].argvalue)
        else:
            type = self.currentInstr.args[1].argtype
            value = self.currentInstr.args[1].argvalue
            
        varType = 'string'
        if type == None:
            varValue = ''
        else:
            varValue = type
        self.prog.setVarValue(self.currentInstr.args[0].argvalue, varValue, varType)

    # function representing running of the program
    def run(self):
        self.operation = self.instructionList[0].id
        self.currentInstr = self.instructionList[0]
        
        while 1:
            if self.currentInstr.name == "CREATEFRAME":
                self.createFrame()
            elif self.currentInstr.name == "PUSHFRAME":
                self.pushFrame()
            elif self.currentInstr.name == "POPFRAME":
                self.popFrame()
            elif self.currentInstr.name == "DEFVAR":
                self.defVar()
            elif self.currentInstr.name == "MOVE":
                self.move()
            elif self.currentInstr.name == "ADD":
                self.add()
            elif self.currentInstr.name == "SUB":
                self.sub()
            elif self.currentInstr.name == "MUL":
                self.mul()
            elif self.currentInstr.name == "IDIV":
                self.div()
            elif self.currentInstr.name == "WRITE":
                self.write()
            elif self.currentInstr.name == "EXIT":
                self.exit()
            elif self.currentInstr.name == "JUMP":
                self.jump()
                continue
            elif self.currentInstr.name == "CALL":
                self.call()
                continue
            elif self.currentInstr.name == "RETURN":
                self.returned()
            elif self.currentInstr.name == "JUMPIFEQ":
                self.jumpEQ()
                if self.currentInstr.name != "JUMPIFEQ":
                    continue
            elif self.currentInstr.name == "JUMPIFNEQ":
                self.jumpNOTEQ()
                if self.currentInstr.name != "JUMPIFNEQ":
                    continue

            elif self.currentInstr.name == "PUSHS": 
                self.pushs()
            elif self.currentInstr.name == "POPS": 
                self.pops()
            elif self.currentInstr.name == "LT": 
                self.lt()
            elif self.currentInstr.name == "GT": 
                self.gt()
            elif self.currentInstr.name == "EQ": 
                self.eq()
            elif self.currentInstr.name == "AND": 
                self.andOp()
            elif self.currentInstr.name == "NOT": 
                self.notOp()
            elif self.currentInstr.name == "OR": 
                self.orOp()
            elif self.currentInstr.name == "INT2CHAR": 
                self.int2char()
            elif self.currentInstr.name == "STRI2INT": 
                self.stri2int()
            elif self.currentInstr.name == "READ":  
                self.read()
            elif self.currentInstr.name == "CONCAT": 
                self.concat()
            elif self.currentInstr.name == "STRLEN":  
                self.strlen()
            elif self.currentInstr.name == "GETCHAR":  
                self.getchar()
            elif self.currentInstr.name == "SETCHAR": 
                self.setchar()
            elif self.currentInstr.name == "TYPE":  # <-
                self.types()
            
            # if it was last instruction from the list, stop running program
            self.getNextOperation(0)
            if self.operation == -1:
                break

# --------------------------------------------------------------------------------------------


# replace all valid escape sequences with their symvols
# args: string - string from source code or from variable
# return: string - deleted escape sequences and replaced by their symbols
def remove_escape_sequences(string):
    if(string == None):
        return ''
    esc_seq = re.findall(r"\\\d{3}", string)
    words = re.split(r"\\\d{3}", string)

    new_string = words[0]

    for i in range(len(esc_seq)):
        esc_seq[i] = chr(int(esc_seq[i][1:]))

        new_string = new_string + esc_seq[i] + words[i+1]
    return new_string


# check if VAR is valid
# args: text - value of possible variable
# returns if it was okay
def varCheck(value, text):
    if value == "var" and re.search('^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][0-9a-zA-Z_\-$&%*!?]*$', text):
        return True
    else:
        return False 

# check if SYMB is valid
# args: text - value of possible variable, or literal or nil
# returns if it was okay
def symbCheck(value, text):
    if value == "var" and re.search('^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][0-9a-zA-Z_\-$&%*!?]*$', text):
        return True
    elif value == "int" and re.search('^[-+]?[0-9]+$', text):
        return True
    elif value == "string" and (text == None or re.search('^([^\\\]|[\\\][0-9][0-9][0-9])*$', text)):
        return True
    elif value == "bool" and re.search('^(true|false)$', text):
        return True
    elif value == "nil" and re.search('^nil$', text):
        return True
    else:
        return False

# check if TYPE is valid
# args: text - int, bool or string
# returns if it was okay
def typeCheck(value, text):
    if value == "type" and re.search('^(int|bool|string)$', text):
        return True
    else:
        return False

# check if LABEL is valid
# args: text - label name
# returns if it was okay
def labelCheck(value, text):
    if value == "label" and re.search('^[a-zA-Z][a-zA-Z0-9_\-$&%*!?]*$', text):
        return True
    else:
        return False
        

# function check every instruction, counts instuction arguments and check if syntax tests were complited
# args: child - children of the XML structure tree (representation of instruction)
# args: typeList - list of arguments of current instruction
def checkChild(child, typeList):
    value_list = []

    for i in range (len(typeList)):
        value_list.append(i+1)
    
    for elem in child:
            if re.search(rf'^arg[1-3]$', elem.tag):
                argNumber = re.search(rf'^arg[1-3]$', elem.tag).group(0)
            else:
                exit(32)
            try:
                argNumber = int(argNumber[3])
                value_list.remove(argNumber)
            except: 
                exit(32)

            argStr = str(argNumber)
            if not re.search(rf'^arg{argStr}$', elem.tag):
                sys.exit(32)

            key, value = list(elem.attrib.items())[0] # type : var  1) always type, 2) different variations

            if not re.search('^type$', key):
                sys.exit(32)

            try:
                t = typeList[argNumber-1]
            except:
                sys.exit(32)

            if t == "var":
                if not varCheck(value, elem.text):
                    sys.exit(32)
            elif t == "symb":
                if not symbCheck(value, elem.text):
                    sys.exit(32)
                else: 
                    if value == 'string':
                        elem.text = remove_escape_sequences(elem.text)
            elif t == "label":
                if not labelCheck(value, elem.text):
                    sys.exit(32)
            elif t == "type":
                if not typeCheck(value, elem.text):
                    sys.exit(32)
            else:
                sys.exit(32)

    if len(value_list) > 0:
        exit(32)

############################## MAIN ##########################

# function sorts children of the tree by ORDER
def sortchildrenby(parent, attr):
    try:
        parent[:] = sorted(parent, key=lambda child: int(child.get(attr)))
    except:
        sys.exit(32)

# program arguments parse
parser = argparse.ArgumentParser(description='Program ma dvz argumenty')
parser.add_argument('--source', help='Soubor s XML reprezentaci', required=False)
parser.add_argument('--input', help='Soubor pro READ', required=False)
args = vars(parser.parse_args())

sourceF = args['source']
inputF = args['input']

# check if both of files are in stock
if sourceF == None and inputF == None:
    sys.exit(10)
elif sourceF == None:
    sourceF = sys.stdin
elif inputF == None:
    inputF = sys.stdin

# check if files are ok
try:
    if inputF != sys.stdin:
        readFile = open(inputF)
    if sourceF != sys.stdin:
        o = open(sourceF)
        o.close()
except:
    sys.exit(11)


# check if XML structure was correct
try:
    tree = EL.parse(sourceF)
except:
  sys.exit(31)

# parsing XML format by xml.etree
root = tree.getroot()
sortchildrenby(root, 'order')

# check atrivutes of root instruction (IPPcode21)
prev_order = 0
if root.attrib['language'] != 'IPPcode21' or root.tag != 'program':
    sys.exit(32)
for child in root:
    if child.tag != "instruction":
        sys.exit(32)

    ca = list(child.attrib.keys())

    if (not 'order' in ca) or (not 'opcode' in ca):
            sys.exit(32)
    
    if int(child.attrib["order"]) > prev_order:
        prev_order = int(child.attrib["order"])
    else:
        sys.exit(32)

    op = child.attrib["opcode"].upper()
    
    # check syntax of every single instruction
    if op == "CREATEFRAME" or op == "PUSHFRAME" or op == "POPFRAME" \
        or op == "RETURN" or op == "BREAK":
        opList = []

    elif op == "DEFVAR" or op == "POPS":
        opList = ["var"]

    elif op == "WRITE" or op == "PUSHS" or op == "WRITE" or op == "DPRINT"\
        or op == "EXIT":
        opList = ["symb"]

    elif op == "MOVE" or op == "NOT" or op == "INT2CHAR" or \
        op == "STRLEN" or op == "TYPE":
        opList = ["var", "symb"]

    elif op == "READ":
        opList = ["var", "type"]

    elif op == "ADD" or op == "SUB" or op == "MUL" or op == "IDIV" or \
        op == "AND" or op == "LT" or op == "GT" or op == "EQ" or op == "OR" \
            or op == "STRI2INT" or op == "CONCAT" or op == "GETCHAR" or op == "SETCHAR":
        # create list with 
        opList = ["var", "symb", "symb"]

    elif op == "JUMPIFEQ" or op == "JUMPIFNEQ":
        opList = ["label", "symb", "symb"]

    elif op == "CALL" or op == "LABEL" or op == "JUMP":
        opList = ["label"]

    else:
        sys.exit(32)

    checkChild(child, opList)

prog = Program()
inter = Interpret(prog)

# write every single instruction to class instruction and to instruction list of interpret
for child in root:
    op = child.attrib["opcode"].upper()
    id = child.attrib["order"]

    instr = Instruction(op, id)
    for elem in child:
        key, argtype = list(elem.attrib.items())[0]
        argvalue = elem.text        

        argNumber = re.search(rf'^arg[1-3]$', elem.tag).group(0)
        argNumber = int(argNumber[3])-1
        arg = instr.addAgrument(argtype, argvalue, argNumber)
    inter.addInstruction(instr)

inter.checkLabelsAndJumps()
inter.run()
if inputF != sys.stdin:
    readFile.close()