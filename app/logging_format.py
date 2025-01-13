class log_:
    def __init__(self,type_="Common Error",ID_=None,msg_=""):
        self.type_=type_
        self.ID=ID_
        self.msg_=msg_
    def get(self):
        return {"type":self.type_,"id":self.ID,"error":self.msg_}



class log_container:
    def __init__(self):
        self.count=0
        self.items=[]
    def add(self,item=log_()):
        self.items.append(item.get())
        self.count+=1
    def get(self):
        return self.items
    def get_counter(self):
        return self.count
    def extend(self,other):
        if type(other)!=type(self):
            return
        else:
            self.count+=other.count
            self.items.extend(other.get())



