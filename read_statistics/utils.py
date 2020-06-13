import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail



def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)

    if not request.COOKIES.get(key):
        # 总阅读数 +1
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        # 计数加一
        readnum.read_num += 1
        # 可做优化 具体参考https://docs.djangoproject.com/en/2.0/ref/models/expressions/
        # 实际开发应用时多加考虑（数据库调优）
        readnum.save() 

        # 获取当天时间（注意时区）
        date = timezone.now().date()
        # 当天阅读数 +1
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)

        readDetail.read_num += 1
        readDetail.save()
        # get_or_create 函数可以官网了解


    return key


def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = [] 
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        # strftime 将时间转换成字符串
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))
        # django.db中的models求和方法
        read_nums.append(result['read_num_sum'] or 0)
        # or 判断布尔值
    return dates, read_nums
    

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')[:7]
    # 指明排序方式
    return read_details

def get_yesterday_hot_day(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
    # 切片取热门博客阅读数前五显示，可以对照具体页面调试. 注意下SQL调优
    return read_details[:7]


# 具体请看views中get_7_days_hot_blogs()和
# 模版类中的read_details = GenericRelation(ReadDetail)
# 
# 
# def get_7_day_hot_day(content_type):
#     today = timezone.now().date()
#     date = today - datetime.timedelta(days=7)
#     read_details = ReadDetail.objects \
#                     .filter(content_type=content_type, date__lt=today, date__gte=date) \
#                     .values('content_type', 'object_id') \
#                     .annotate(read_num_sum=Sum('read_num')) \
#                     .order_by('-read_num')
#     # 空格 加反斜杠换行 .values.annotate.order_by可上django官网查看其用法
#     # https://docs.djangoproject.com/en/2.0/ref/models/querysets/
#     return read_details[:5]


