class DiGua:
    def __init__(self):
        self.cook_time=0
        self.state='生的'
        self.tiaoliao=[]
    def cook(self,time):
        self.cook_time+=time
        if self.cook_time<3:
            self.state='生的'
        elif self.cook_time<6:
            self.state = '半生的'
        elif self.cook_time<9:
            self.state = '熟了'
        else:
            self.state = '糊了'
        print( f'该地瓜已经烤制了{self.cook_time}分钟了，已经{self.state}')
    def app_tiaoliao(self, tl):
        if self.tiaoliao in self.tiaoliao:
            return f'该调料已经加过了，请勿重复添加'
        else:
            self.tiaoliao.append(tl)
        return f'{self.tiaoliao}'


s=DiGua()
s2 = s.cook(6)
s.app_tiaoliao("yan")
print(s2)
