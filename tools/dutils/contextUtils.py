# coding=gbk
import time


class OutTime(object):
    """
    打印上下文管理器内代码运行花费的时间，若出现报错则直接停止
    使用时在with contextUtils.OutTime() as f:下书写业务代码，业务代码运行完后自动打印耗时
    """
    def __enter__(self):
        self.stater = time.time()

    def __exit__(self, typ, val, tb):
        print(time.time() - self.stater)
        return False  # 这里返回True意味着with as语句块后面的代码会继续执行,但是with as语句块内部，产生异常之后的代码不会执行
        #为false则with as内部与外部的代码都不会执行


def get_time_consumption(return_fun=False):
    """
    该参数用于向装饰器传参，如果不需要向装饰器传参，可以不使用这一层函数
    :param return_fun:返回对象是否指定为传入函数的返回
    :return:
    """
    def actual_decorator(func):
        """
        通过装饰器的方法计算函数消耗的时间
        :param func: 需要运行的函数，格式为在函数上写：@contextUtils.get_time_consumption()
        :return: 消耗的时间，单位秒(s)
        """
        def wrapper(*args, **kwargs):
            stared = time.time()
            resuat = func(*args, **kwargs)
            tim = time.time() - stared
            print(u'函数{}运行耗时{}秒'.format(func.__name__,tim))
            if return_fun:
                return resuat
            else:
                return tim
        return wrapper
    return actual_decorator

