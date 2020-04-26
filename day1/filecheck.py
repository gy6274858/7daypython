# 导入OS模块
import os

# 待搜索的目录路径
path = "Day1-homework"
# 待搜索的名称
filename = "2020"
# 定义保存结果的数组
result = []


def findfiles():
    # 在这里写下您的查找文件代码吧！
    for file in os.listdir(path):
        if '2020' in os.path.splitext(file)[1]:
            result.append(file)

    for t in result:
        print(t)


if __name__ == '__main__':
    findfiles()