import random
import math
from iNews.settings import DATA_FILE, K_NUM
from user.models import UserRating


# 将最近的1000条用户行为日志取出存放在data.txt中，进行分析
def create_data():
    user_ratings = UserRating.objects.all()[:1000]
    with open(DATA_FILE, 'w') as file_object:
        for user_rating in user_ratings:
            file_object.write(
                str(user_rating.user_id_id) + ',' + str(user_rating.news_id_id) + ',' + str(
                    user_rating.rating_num) + '\n')


# 将数据加载进内存
def load_data():
    data = []
    for line in open(DATA_FILE):
        user_id, item_id, record = line.split(',')
        data.append((user_id, item_id, int(record)))
    return data


# 更新最优K值
def jude():
    list_k = []
    list_p = []
    prec = dict()
    for k in range(1, 4):
        cf = UserCFRecJude()
        create_data()
        precision = cf.precision(k=k)
        list_k.append(k)
        list_p.append(precision)
        prec[k] = precision
    max_k = max(prec, key=lambda x: prec[x])
    with open(K_NUM, 'w') as file_object:
        file_object.write(str(max_k))

# 准确率评价
class UserCFRecJude:
    def __init__(self):
        self.data = load_data()
        self.trainData, self.testData = self.split_data(3, 47)
        self.users_sim = self.cal_user_sim()

    # 采用随机函数将数据拆分成训练集和测试集
    def split_data(self, k, seed, M=8):
        train = {}
        test = {}
        random.seed(seed)
        for user, item, record in self.data:
            if random.randint(0, M) == k:
                test.setdefault(user, {})
                test[user][item] = record
            else:
                train.setdefault(user, {})
                train[user][item] = record
        return train, test

    # 计算用户之间的相似度，采用惩罚热门商品和优化算法复杂度的算法
    def cal_user_sim(self):
        # 得到每个item被哪些user评价过
        item_users = dict()
        # 按用户遍历整个字典
        for u, items in self.trainData.items():
            # 遍历该用户有过行为的每条物品
            for i in items.keys():
                # 建立以物品为key的用户字典
                item_users.setdefault(i, set())
                if items[i] > 0:
                    item_users[i].add(u)
        # 构建倒排表
        count = dict()
        user_item_count = dict()
        # 遍历整个物品-用户字典
        for i, users in item_users.items():
            # 遍历某个物品下的所有用户
            for u in users:
                # 建立该用户有过行为的的物品总数的统计
                user_item_count.setdefault(u, 0)
                user_item_count[u] += 1
                # 建立该用户和其他用户的所有正反馈的交集以及交集数目
                # 冗余存储
                count.setdefault(u, {})
                for v in users:
                    count[u].setdefault(v, 0)
                    if u == v:
                        continue
                    count[u][v] += 1 / math.log(1 + len(users))
        # 用户相似度表
        userSim = dict()
        # 遍历所有的用户
        for u, related_users in count.items():
            userSim.setdefault(u, {})
            # 对于该用户所有有过正反馈交集的用户
            for v, cuv in related_users.items():
                if u == v:
                    continue
                userSim[u].setdefault(v, 0.0)
                # 计算他们的相似度（交集数目/各自行为总数）
                userSim[u][v] = cuv / math.sqrt(user_item_count[u] * user_item_count[v])
        # 返回用户相似度
        return userSim

    # 推荐算法
    def recommend(self, user, k=2, n=20):
        result = dict()
        have_score_items = self.trainData.get(user, {})
        # 按相关度进行倒序排序，选取前k位相似度最高的用户
        for v, wuv in sorted(self.users_sim[user].items(), key=lambda x: x[1], reverse=True)[0:k]:
            # 遍历其他用户的历史数据
            for i, rvi in self.trainData[v].items():
                # 如果该用户对某物品没有过评分（其他用户有过正反馈而自己没有的）
                if i in have_score_items:
                    continue
                # 就加入推荐列表，并累加推荐值
                result.setdefault(i, 0)
                # 推荐值等所有相关用户的相似度*相关用户对该物品的评分
                result[i] += wuv * rvi
        # 然后逆序排序选取前n项推送给用户
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True)[0:n])

    # 计算推荐结果准确率
    def precision(self, k=2, n=20):
        hit = 0
        precision = 0
        # 遍历训练集中所有用户的数据
        for user in self.trainData.keys():
            # 取出测试集该用户的所有评分数据
            tu = self.testData.get(user, {})
            # 通过推荐算法得出推荐结果
            rank = self.recommend(user, k=k, n=n)
            # 遍历推荐结果
            for item, rate in rank.items():
                # 如果在测试集中
                if item in tu:
                    # 准确推荐数加1
                    hit += 1
            # 推荐结果数为n
            precision += n
        # 推荐准确率为hit/n
        return hit / (precision * 1.0)
