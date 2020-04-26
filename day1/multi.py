def table():
    #在这里写下您的乘法口诀表代码吧！
    for i in range(1, 10):
        for j in range(1, i+1):
            print("%d * %d = %d" % (j, i, j*i), end='\t')
        print()




if __name__ == '__main__':
    table()
